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
        
        # Dictionary lưu trữ gói tin theo flow và thời gian
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
    
    def _generate_flow_key(self, packet_data):
        """Tạo khóa duy nhất cho mỗi flow dựa trên 5-tuple
        
        Args:
            packet_data: Dictionary chứa thông tin của gói tin
            
        Returns:
            Chuỗi đại diện cho flow
        """
        src_ip = packet_data.get('src_ip', '')
        dst_ip = packet_data.get('dst_ip', '')
        src_port = packet_data.get('src_port', 0)
        dst_port = packet_data.get('dst_port', 0)
        ip_proto = packet_data.get('ip_proto', 0)
        
        # Tạo khóa flow 5-tuple
        flow_key = f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-{ip_proto}"
        return flow_key
    
    def clean_old_data(self):
        """Hàm dọn dẹp dữ liệu cũ trong buffer"""
        while True:
            time.sleep(60)  # Kiểm tra mỗi phút
            current_time = int(time.time() * 1000)  # ms
            with self.buffer_lock:
                for flow_key in list(self.traffic_buffer.keys()):
                    # Giữ lại các gói tin trong khoảng 5 phút gần nhất
                    self.traffic_buffer[flow_key] = [
                        packet for packet in self.traffic_buffer[flow_key] 
                        if (current_time - packet['time_epoch']) < 5*60*1000
                    ]
                    # Xóa flow không còn gói tin nào
                    if not self.traffic_buffer[flow_key]:
                        del self.traffic_buffer[flow_key]
            
            num_flows = len(self.traffic_buffer)
            if num_flows > 0:
                logger.info(f"Đã dọn dẹp buffer, hiện đang theo dõi {num_flows} luồng dữ liệu")
    
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
        
        # Tính thời gian giữa các gói tin (chuyển đổi đơn vị thời gian phù hợp)
        # Đảm bảo timestamp đã ở dạng số nguyên
        df['timestamp'] = pd.to_numeric(df['timestamp'])
        inter_packet_times = np.diff(df['timestamp']) / 1_000_000  # chuyển đổi nano giây sang milli giây
        
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
    
    def classify_flow(self, flow_key, packets):
        """Phân loại luồng dữ liệu dựa trên mô hình đã huấn luyện
        
        Args:
            flow_key: Khóa xác định flow
            packets: Danh sách các gói tin trong luồng
            
        Returns:
            Dictionary chứa kết quả phân loại hoặc None nếu không thể phân loại
        """
        if self.model is None:
            logger.error("Không thể phân loại do không có mô hình")
            return None
        
        # Phân tách các thành phần của flow_key để đưa vào kết quả
        flow_parts = flow_key.split('-')
        src_info = flow_parts[0].split(':')
        dst_info = flow_parts[1].split(':')
        
        src_ip = src_info[0]
        src_port = src_info[1]
        dst_ip = dst_info[0]
        dst_port = dst_info[1]
        ip_proto = flow_parts[2] if len(flow_parts) > 2 else "unknown"

        # Sắp xếp các gói tin theo thời gian
        sorted_packets = sorted(packets, key=lambda p: p['time_epoch'])
        
        # Xác định thời điểm đầu tiên và cuối cùng trong chuỗi gói tin
        min_time = sorted_packets[0]['time_epoch']
        max_time = sorted_packets[-1]['time_epoch']
        
        # Tính số cửa sổ thời gian
        time_span = max_time - min_time
        num_windows = max(1, int(time_span / self.TIME_WINDOW_MS))
        
        # Chia các gói tin vào các cửa sổ thời gian
        window_groups = defaultdict(list)
        
        for packet in sorted_packets:
            # Xác định window_id cho gói tin
            window_id = (packet['time_epoch'] - min_time) // self.TIME_WINDOW_MS
            window_groups[window_id].append(packet)
        
        # Trích xuất đặc trưng và phân loại từng cửa sổ thời gian
        window_results = []
        
        for window_id, window_packets in window_groups.items():
            # Nếu cửa sổ không có đủ gói tin, bỏ qua
            if len(window_packets) < 2:
                continue
                
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
                    'window_id': int(window_id),
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
        
        # Tạo kết quả chi tiết
        result = {
            'flow_key': flow_key,
            'src_ip': src_ip,
            'src_port': src_port,
            'dst_ip': dst_ip,
            'dst_port': dst_port,
            'ip_proto': ip_proto,
            'classification': best_window['prediction'],
            'confidence': best_window['confidence'],
            'timestamp': datetime.now().isoformat(),
            'packet_count': sum(len(window_packets) for window_packets in window_groups.values()),
            'num_windows': len(window_groups),
            'time_span_ms': time_span,
            'window_id': best_window['window_id']
        }
        
        return result
    
    def process_packet(self, packet_data):
        """Xử lý gói tin mới, thêm vào buffer và phân loại nếu đủ điều kiện
        
        Args:
            packet_data: Dictionary chứa thông tin của gói tin
            
        Returns:
            Dictionary chứa kết quả phân loại hoặc None nếu chưa đủ dữ liệu để phân loại
        """
        # Tạo khóa cho flow
        flow_key = self._generate_flow_key(packet_data)
        
        # Thêm gói tin vào buffer
        with self.buffer_lock:
            self.traffic_buffer[flow_key].append(packet_data)
            
            packets = self.traffic_buffer[flow_key]
            
            # Chỉ phân loại khi có đủ số lượng gói tin trong một flow
            if len(packets) >= 10:
                # Kiểm tra xem các gói tin có nằm trong cùng một cửa sổ thời gian không
                timestamps = [p['time_epoch'] for p in packets]
                min_time = min(timestamps)
                max_time = max(timestamps)
                
                # Nếu khoảng thời gian lớn hơn một cửa sổ, thì thực hiện phân loại
                if (max_time - min_time) >= self.TIME_WINDOW_MS:
                    result = self.classify_flow(flow_key, packets)
                    
                    if result:
                        self.classification_results[flow_key] = result
                        
                        logger.info(f"Đã phân loại flow {flow_key}: {result['classification']} "
                                   f"(độ tin cậy: {result['confidence']:.2f})")
                        
                        # Trả về kết quả
                        return result
        
        return None
    
    def get_classification_results(self, src_ip=None, dst_ip=None, src_port=None, dst_port=None, ip_proto=None):
        """Lấy kết quả phân loại theo các tiêu chí lọc
        
        Args:
            src_ip: IP nguồn (tùy chọn)
            dst_ip: IP đích (tùy chọn)
            src_port: Cổng nguồn (tùy chọn)
            dst_port: Cổng đích (tùy chọn)
            ip_proto: Giao thức IP (tùy chọn)
            
        Returns:
            Danh sách các kết quả phân loại thỏa mãn điều kiện lọc
        """
        results = []
        with self.buffer_lock:
            for flow_key, result in self.classification_results.items():
                # Nếu kết quả không có đủ thông tin cần thiết, bỏ qua
                if not all(key in result for key in ['src_ip', 'dst_ip', 'src_port', 'dst_port', 'ip_proto']):
                    continue
                
                match = True
                if src_ip and result['src_ip'] != src_ip:
                    match = False
                if dst_ip and result['dst_ip'] != dst_ip:
                    match = False
                if src_port and result['src_port'] != src_port:
                    match = False
                if dst_port and result['dst_port'] != dst_port:
                    match = False
                if ip_proto and result['ip_proto'] != str(ip_proto):
                    match = False
                
                if match:
                    results.append(result)
        
        return results