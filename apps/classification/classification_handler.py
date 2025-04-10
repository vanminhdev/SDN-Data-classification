import logging
import pickle
import numpy as np
import pandas as pd
import threading
import time
from collections import defaultdict
from datetime import datetime
import queue

# Cấu hình logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ClassificationHandler:    
    def __init__(self, model_path='models/traffic_classifier.pkl', time_window_ns=3_000_000, classification_interval=1.0, flow_handler=None):
        """Khởi tạo Classification Handler
        
        Args:
            model_path: Đường dẫn đến file mô hình đã huấn luyện
            time_window_ns: Kích thước cửa sổ thời gian (ns)
            classification_interval: Khoảng thời gian giữa các lần phân loại (giây)
            flow_handler: Đối tượng FlowRuleHandler để cập nhật flow rule
        """
        self.MODEL_PATH = model_path
        self.TIME_WINDOW_NS = time_window_ns
        self.RECENT_CLASSIFICATION_WINDOW = 5_000_000_000  # 5 giây (ns)
        self.CLASSIFICATION_INTERVAL = classification_interval  # Khoảng thời gian giữa các lần phân loại (giây)
        self.flow_handler = flow_handler  # Lưu tham chiếu đến flow_handler
        
        # Dictionary lưu tất cả gói tin theo timestamp
        self.packet_buffer = []
        # Dictionary lưu trữ gói tin theo flow 
        self.flow_buffer = defaultdict(list)
        # Dictionary lưu thời điểm phân loại cuối cùng của mỗi flow
        self.last_classification_time = {}
        # Khóa để đồng bộ hóa truy cập vào buffer
        self.buffer_lock = threading.Lock()
        # Thời điểm xử lý window cuối cùng
        self.last_window_time = 0
        
        # Hàng đợi lưu trữ kết quả phân loại mới nhất
        self.classification_queue = queue.Queue(maxsize=10000)
        
        # Cờ kiểm soát các thread
        self.running = True
        
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
        
        # Khởi động thread phân loại
        self.classification_thread = threading.Thread(target=self.run_classification, daemon=True)
        self.classification_thread.start()
    
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
            current_time = int(time.time() * 1_000_000_000)  # ns
            with self.buffer_lock:
                # Giữ lại các gói tin trong khoảng 5 phút gần nhất
                five_minutes_ago = current_time - 5 * 60 * 1_000_000_000
                self.packet_buffer = [
                    packet for packet in self.packet_buffer 
                    if packet['time_epoch'] > five_minutes_ago
                ]
                  # Cập nhật flow_buffer dựa trên packet_buffer mới
                self.flow_buffer.clear()
                for packet in self.packet_buffer:
                    flow_key = self._generate_flow_key(packet)
                    self.flow_buffer[flow_key].append(packet)
                
                # Xóa thời gian phân loại cũ (quá 10 phút)
                ten_minutes_ago = current_time - 10 * 60 * 1_000_000_000
                for flow_key in list(self.last_classification_time.keys()):
                    classification_time = self.last_classification_time[flow_key]
                    if classification_time < ten_minutes_ago:
                        del self.last_classification_time[flow_key]
            
            num_packets = len(self.packet_buffer)
            num_flows = len(self.flow_buffer)
            if num_packets > 0 or num_flows > 0:
                logger.info(f"Đã dọn dẹp buffer, hiện đang theo dõi {num_packets} gói tin, {num_flows} luồng dữ liệu")
    
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
        inter_packet_times = np.diff(df['timestamp']) #đơn vị ns
        
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
    
    def classify_single_flow(self, flow_key, packets):
        """Phân loại một luồng dữ liệu duy nhất dựa trên mô hình đã huấn luyện
        
        Args:
            flow_key: Khóa xác định flow
            packets: Danh sách các gói tin trong luồng
            
        Returns:
            Dictionary chứa kết quả phân loại hoặc None nếu không thể phân loại
        """
        if self.model is None:
            logger.error("Không thể phân loại do không có mô hình")
            return None
        
        # Kiểm tra số lượng gói tin tối thiểu
        if len(packets) < 5:
            logger.debug(f"Flow {flow_key} chưa đủ gói tin để phân loại (cần ít nhất 5)")
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
        
        # Trích xuất đặc trưng
        features = self.extract_features(sorted_packets)
        if features is None:
            logger.debug(f"Không thể trích xuất đặc trưng cho flow {flow_key}")
            return None
            
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
            
            # Tính thông tin thời gian của flow
            min_time = sorted_packets[0]['time_epoch']
            max_time = sorted_packets[-1]['time_epoch']
            time_span = max_time - min_time
            
            # Tạo kết quả chi tiết
            result = {
                'flow_key': flow_key,
                'src_ip': src_ip,
                'src_port': src_port,
                'dst_ip': dst_ip,
                'dst_port': dst_port,
                'ip_proto': ip_proto,
                'classification': prediction,
                'confidence': float(probability),
                'timestamp': datetime.now().isoformat(),
                'packet_count': len(sorted_packets),
                'time_span_ns': time_span,
                'start_time': min_time,
                'end_time': max_time
            }
            
            return result
        except Exception as e:
            logger.error(f"Lỗi khi dự đoán cho flow {flow_key}: {e}")
            return None

    def run_classification(self):
        """Hàm chạy trong một thread riêng, thực hiện phân loại định kỳ cho tất cả các flow
        """
        logger.info("Bắt đầu thread phân loại định kỳ")
        
        while self.running:
            try:
                # Đợi đến lần phân loại tiếp theo
                time.sleep(self.CLASSIFICATION_INTERVAL)
                
                current_time = int(time.time() * 1_000_000_000)  # ns
                window_start_time = current_time - self.TIME_WINDOW_NS
                
                with self.buffer_lock:
                    # Lấy các gói tin trong time window hiện tại
                    window_packets = [p for p in self.packet_buffer 
                                     if window_start_time <= p['time_epoch'] <= current_time]
                    
                    # Nhóm gói tin theo flow
                    window_flows = defaultdict(list)
                    for p in window_packets:
                        flow_k = self._generate_flow_key(p)
                        window_flows[flow_k].append(p)
                    
                    # Phân loại tất cả flow đủ điều kiện
                    classified_flows = []
                    
                    for flow_key, packets in window_flows.items():
                        # Kiểm tra điều kiện để phân loại
                        if len(packets) < 5:
                            logger.debug(f"Bỏ qua flow {flow_key} - không đủ gói tin ({len(packets)}/5)")
                            continue
                        
                        # Kiểm tra thời gian phân loại gần đây
                        last_time = self.last_classification_time.get(flow_key, 0)
                        if current_time - last_time < self.RECENT_CLASSIFICATION_WINDOW:
                            logger.debug(f"Bỏ qua flow {flow_key} - mới phân loại gần đây ({(current_time - last_time)/1_000_000_000:.2f}s)")
                            continue
                        
                        # Phân loại flow
                        result = self.classify_single_flow(flow_key, packets)
                        if result:
                            # Cập nhật thời gian phân loại cuối cùng
                            self.last_classification_time[flow_key] = current_time
                            # Thêm trường service_type
                            result['service_type'] = result['classification'].upper()
                            
                            logger.info(f"Đã phân loại flow {flow_key}: {result['classification']} "
                                        f"(độ tin cậy: {result['confidence']:.2f})")
                            
                            # Thêm vào hàng đợi kết quả (loại bỏ kết quả cũ nếu đầy)
                            try:
                                self.classification_queue.put_nowait(result)
                            except queue.Full:
                                try:
                                    # Loại bỏ kết quả cũ nhất nếu hàng đợi đầy
                                    self.classification_queue.get_nowait()
                                    self.classification_queue.put_nowait(result)
                                except:
                                    pass
                            
                            # Tự động cập nhật flow rule nếu flow_handler được cung cấp
                            if self.flow_handler:
                                service_type = result['service_type']
                                # Lấy gói tin mới nhất của flow này để gửi đến flow_handler
                                latest_packet = packets[-1] if packets else None
                                if latest_packet:
                                    logger.info(f"Tự động cập nhật flow rule cho flow {flow_key} với service_type {service_type}")
                                    update_success = self.flow_handler.update_flow_rule(latest_packet, service_type)
                                    # Thêm thông tin cập nhật vào kết quả
                                    result['flow_rule_updated'] = update_success
                                
                            classified_flows.append(result)
                    
                    if classified_flows:
                        logger.info(f"Đã phân loại {len(classified_flows)} flow trong chu kỳ phân loại này")
            
            except Exception as e:
                logger.error(f"Lỗi trong thread phân loại: {e}")
                time.sleep(5)  # Đợi một lúc trước khi thử lại nếu có lỗi
    
    def simplified_process_packet(self, packet_data):
        """Thêm gói tin vào buffer để phân loại định kỳ và trả về kết quả phân loại mới nhất nếu có
        
        Args:
            packet_data: Dictionary chứa thông tin của gói tin
            
        Returns:
            Dictionary chứa kết quả phân loại nếu có sẵn, None nếu không có
        """
        # Tạo khóa cho flow
        flow_key = self._generate_flow_key(packet_data)
        
        # Thêm gói tin vào buffer
        with self.buffer_lock:
            self.packet_buffer.append(packet_data)
            self.flow_buffer[flow_key].append(packet_data)
            logger.debug(f"Đã thêm gói tin vào flow {flow_key}: hiện có {len(self.flow_buffer[flow_key])} gói tin")
        
        # Kiểm tra xem có kết quả phân loại mới nhất cho flow này không
        try:
            # Kiểm tra tất cả kết quả trong hàng đợi
            results = list(self.classification_queue.queue)
            for result in results:
                if result['flow_key'] == flow_key:
                    # Đã tìm thấy kết quả phân loại cho flow này
                    return result
        except:
            pass
        
        # Không có kết quả phân loại cho flow hiện tại
        return None
            
    def get_latest_classification_results(self):
        """Lấy tất cả kết quả phân loại gần đây
        
        Returns:
            List chứa các kết quả phân loại gần đây nhất
        """
        try:
            return list(self.classification_queue.queue)
        except:
            return []
            
    def get_classification_results(self, src_ip=None, dst_ip=None, src_port=None, dst_port=None, ip_proto=None):
        """Lọc kết quả phân loại theo các tiêu chí
        
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
        all_results = self.get_latest_classification_results()
        
        for result in all_results:
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