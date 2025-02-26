import logging
import pickle
import numpy as np
import pandas as pd
import threading
import time
from collections import defaultdict
from datetime import datetime

# Cấu hình logger
logger = logging.getLogger(__name__)

class ClassificationHandler:
    def __init__(self, model_path='models/traffic_classifier.pkl', time_window_ms=1000):
        """Khởi tạo Classification Handler
        
        Args:
            model_path: Đường dẫn đến file mô hình đã huấn luyện
            time_window_ms: Kích thước cửa sổ thời gian (ms)
        """
        self.MODEL_PATH = model_path
        self.TIME_WINDOW_MS = time_window_ms
        
        # Dictionary lưu trữ gói tin theo cặp IP và thời gian
        self.traffic_buffer = defaultdict(list)
        # Dictionary lưu kết quả phân loại
        self.classification_results = {}
        # Khóa để đồng bộ hóa truy cập vào buffer
        self.buffer_lock = threading.Lock()
        
        # Tải mô hình phân loại
        self.model = None
        try:
            with open(self.MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("Đã tải mô hình phân loại thành công")
        except Exception as e:
            logger.error(f"Không thể tải mô hình phân loại: {e}")

        # Khởi động thread dọn dẹp
        self.cleanup_thread = threading.Thread(target=self.clean_old_data, daemon=True)
        self.cleanup_thread.start()
    
    def clean_old_data(self):
        """Hàm dọn dẹp dữ liệu cũ trong buffer"""
        while True:
            time.sleep(60)  # Kiểm tra mỗi phút
            current_time = int(time.time() * 1000)  # ms
            with self.buffer_lock:
                for key in list(self.traffic_buffer.keys()):
                    # Giữ lại các gói tin trong khoảng 5 phút gần nhất
                    self.traffic_buffer[key] = [
                        packet for packet in self.traffic_buffer[key] 
                        if (current_time - packet['time_epoch']) < 5*60*1000
                    ]
                    # Xóa cặp IP không còn gói tin nào
                    if not self.traffic_buffer[key]:
                        del self.traffic_buffer[key]
            logger.info(f"Đã dọn dẹp buffer, hiện đang theo dõi {len(self.traffic_buffer)} luồng dữ liệu")
    
    def extract_features(self, packets):
        """Trích xuất đặc trưng từ danh sách gói tin trong một time window
        
        Args:
            packets: Danh sách các gói tin trong time window
            
        Returns:
            Dictionary chứa các đặc trưng đã trích xuất hoặc None nếu không đủ dữ liệu
        """
        if len(packets) < 2:
            return None
            
        # Chuyển thành DataFrame để dễ xử lý
        df = pd.DataFrame(packets)
        # Chuyển đổi time_epoch nếu cần
        if 'time_epoch' in df.columns:
            df['timestamp'] = df['time_epoch']
        
        # Sắp xếp theo thời gian
        df = df.sort_values('timestamp')
        
        # Trích xuất đặc trưng
        packet_count = len(df)
        average_packet_length = df['frame_len'].mean()
        
        # Tính thời gian giữa các gói tin
        inter_packet_times = np.diff(df['timestamp']) / 1_000_000  # convert ns to ms
        
        # Tính các đặc trưng thời gian
        if len(inter_packet_times) > 0:
            average_inter_packet_time = inter_packet_times.mean()
            inter_packet_time_variance = inter_packet_times.var() if len(inter_packet_times) > 1 else 0
        else:
            average_inter_packet_time = 0
            inter_packet_time_variance = 0
        
        # Tính phương sai kích thước gói tin
        packet_size_variance = df['frame_len'].var() if len(df) > 1 else 0
        
        # Tạo và trả về vector đặc trưng
        features = {
            'packet_count': packet_count,
            'average_packet_length': average_packet_length,
            'average_inter_packet_time': average_inter_packet_time,
            'packet_size_variance': packet_size_variance,
            'inter_packet_time_variance': inter_packet_time_variance
        }
        
        return features
    
    def classify_flow(self, ip_pair, packets):
        """Phân loại luồng dữ liệu dựa trên mô hình đã huấn luyện
        
        Args:
            ip_pair: Cặp IP nguồn-đích
            packets: Danh sách các gói tin trong luồng
            
        Returns:
            Dictionary chứa kết quả phân loại hoặc None nếu không thể phân loại
        """
        if self.model is None:
            logger.error("Không thể phân loại do không có mô hình")
            return None

        # Nhóm gói tin theo time window
        min_time = min(packet['time_epoch'] for packet in packets)
        
        # Gán window_id cho từng gói tin
        for packet in packets:
            packet['window_id'] = (packet['time_epoch'] - min_time) // self.TIME_WINDOW_MS
        
        # Nhóm theo window_id
        window_groups = defaultdict(list)
        for packet in packets:
            window_groups[packet['window_id']].append(packet)
        
        # Trích xuất đặc trưng và phân loại từng cửa sổ thời gian
        window_results = []
        
        for window_id, window_packets in window_groups.items():
            features = self.extract_features(window_packets)
            if features is None:
                continue
                
            # Chuyển đặc trưng thành mảng để dự đoán
            feature_vector = np.array([[
                features['packet_count'],
                features['average_packet_length'],
                features['average_inter_packet_time'],
                features['packet_size_variance'],
                features['inter_packet_time_variance']
            ]])
            
            # Dự đoán
            try:
                prediction = self.model.predict(feature_vector)[0]
                probability = np.max(self.model.predict_proba(feature_vector))
                
                window_results.append({
                    'window_id': window_id,
                    'start_time': min_time + window_id * self.TIME_WINDOW_MS,
                    'end_time': min_time + (window_id + 1) * self.TIME_WINDOW_MS,
                    'prediction': prediction,
                    'confidence': float(probability),
                    'packet_count': features['packet_count']
                })
            except Exception as e:
                logger.error(f"Lỗi khi dự đoán: {e}")
        
        # Nếu không có kết quả, trả về None
        if not window_results:
            return None
        
        # Lấy kết quả dự đoán từ cửa sổ có nhiều gói tin nhất
        best_window = max(window_results, key=lambda x: x['packet_count'])
        
        return {
            'ip_pair': ip_pair,
            'classification': best_window['prediction'],
            'confidence': best_window['confidence'],
            'timestamp': datetime.now().isoformat(),
            'packet_count': sum(len(packets) for packets in window_groups.values())
        }
    
    def process_packet(self, packet_data):
        """Xử lý gói tin mới, thêm vào buffer và phân loại nếu đủ điều kiện
        
        Args:
            packet_data: Dictionary chứa thông tin của gói tin
            
        Returns:
            Dictionary chứa kết quả phân loại hoặc None nếu chưa đủ dữ liệu để phân loại
        """
        # Tạo khóa duy nhất cho cặp IP
        src_ip = packet_data.get('src_ip')
        dst_ip = packet_data.get('dst_ip')
        ip_pair = f"{src_ip}-{dst_ip}"
        
        # Thêm gói tin vào buffer
        with self.buffer_lock:
            self.traffic_buffer[ip_pair].append(packet_data)
            
            # Nếu có đủ số lượng gói tin trong một cặp IP, thực hiện phân loại
            if len(self.traffic_buffer[ip_pair]) >= 10:
                packets = self.traffic_buffer[ip_pair]
                result = self.classify_flow(ip_pair, packets)
                
                if result:
                    self.classification_results[ip_pair] = result
                    
                    logger.info(f"Đã phân loại luồng {ip_pair}: {result['classification']} "
                               f"(độ tin cậy: {result['confidence']:.2f})")
                    
                    # Trả về kết quả
                    return result
        
        return None
    
    def get_classification_results(self, src_ip=None, dst_ip=None):
        """Lấy kết quả phân loại theo địa chỉ IP
        
        Args:
            src_ip: IP nguồn (tùy chọn)
            dst_ip: IP đích (tùy chọn)
            
        Returns:
            Danh sách các kết quả phân loại thỏa mãn điều kiện lọc
        """
        results = []
        with self.buffer_lock:
            for ip_pair, result in self.classification_results.items():
                if src_ip and dst_ip:
                    if f"{src_ip}-{dst_ip}" == ip_pair:
                        results.append(result)
                elif src_ip:
                    if ip_pair.startswith(f"{src_ip}-"):
                        results.append(result)
                elif dst_ip:
                    if ip_pair.endswith(f"-{dst_ip}"):
                        results.append(result)
                else:
                    results.append(result)
        
        return results