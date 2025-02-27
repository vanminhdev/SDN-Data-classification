"""
Trình tạo dữ liệu lưu lượng mạng giả lập cho hệ thống phân loại
File này được tạo chỉ để mục đích giả lập (fake) dữ liệu nhằm kiểm tra hệ thống phân loại 
lưu lượng mạng. Các dữ liệu được tạo ra ở đây không phải là lưu lượng thực tế mà chỉ 
là dữ liệu có cấu trúc tương tự để thử nghiệm chức năng phân loại hoạt động chính xác.
Script này tạo hai loại lưu lượng giả lập:
1. Lưu lượng video: Đặc trưng bởi các gói tin lớn hơn, thường sử dụng TCP
2. Lưu lượng VoIP: Đặc trưng bởi các gói tin nhỏ hơn, thường sử dụng UDP
Dữ liệu được tạo ra sẽ được lưu vào cơ sở dữ liệu InfluxDB để hệ thống phân loại 
có thể đọc và xử lý. Các tham số như độ lớn gói tin, khoảng thời gian giữa các gói,
v.v. được điều chỉnh để mô phỏng tương đối chính xác đặc điểm của các loại lưu lượng.
Lưu ý: File này KHÔNG PHẢI là phần chính của hệ thống, chỉ được sử dụng trong quá trình
phát triển và kiểm thử để tạo dữ liệu thử nghiệm.
"""
import os
import time
import random
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging
import argparse
import ipaddress

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NetworkTrafficGenerator:
    def __init__(self, num_seconds=60, seed=42):
        """Khởi tạo trình tạo dữ liệu lưu lượng mạng
        
        Args:
            num_seconds: Số giây dữ liệu lưu lượng cần tạo (mặc định: 60 giây)
            seed: Giá trị khởi tạo ngẫu nhiên để tái sản xuất kết quả
        """
        # Cấu hình kết nối InfluxDB
        self.INFLUXDB_URL = "http://localhost:8086"
        self.INFLUXDB_TOKEN = "Oj5-XrZQ24Glkaz7ApaVqAXKGrX61oi3T28wcT2o5BkBWemzUyJnyUNoxYv_KghZXpcXxFmz4RZSnwjDUYQoyA=="
        self.INFLUXDB_ORG = "huce"
        self.INFLUXDB_BUCKET = "network_traffic"
        
        # Khởi tạo client
        self.client = InfluxDBClient(
            url=self.INFLUXDB_URL, 
            token=self.INFLUXDB_TOKEN, 
            org=self.INFLUXDB_ORG
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        
        # Tham số sinh dữ liệu
        self.num_seconds = num_seconds
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Hồ sơ lưu lượng
        self.traffic_profiles = {
            "video": {
                "frame_len": {
                    "mean": 1200,        # Gói tin lớn hơn cho video
                    "std": 300,
                    "min": 500
                },
                "packet_interval": {
                    "mean": 15,          # Thời gian khá đều đặn cho phát trực tuyến
                    "std": 10,
                    "min": 5
                },
                "burst_likelihood": 0.2   # Thỉnh thoảng có đợt gói tin tăng đột biến
            },
            "voip": {
                "frame_len": {
                    "mean": 200,         # Gói tin nhỏ hơn cho thoại
                    "std": 50,
                    "min": 80
                },
                "packet_interval": {
                    "mean": 20,          # Thời gian đều đặn cho thoại
                    "std": 5,
                    "min": 10
                },
                "burst_likelihood": 0.05  # Ít có đợt tăng đột biến
            }
        }
        
        # Tạo một số thành phần mạng thông dụng
        self.devices = [f"of:000000000000000{i}" for i in range(1, 4)]
        
        # Tạo một số địa chỉ IP ngẫu nhiên
        ip_network = ipaddress.IPv4Network('10.0.0.0/24')
        ip_list = list(ip_network.hosts())
        self.src_ips = [str(random.choice(ip_list)) for _ in range(2)]
        self.dst_ips = [str(random.choice(ip_list)) for _ in range(2)]
        
        # Các cổng thông dụng
        self.video_ports = [443, 8080, 1935, 554]  # HTTP, HTTPS, HTTP-alt, RTMP, RTSP
        self.voip_ports = [5060, 5061, 10000, 10001, 16384]  # SIP, SIP-TLS, và một số RTP
    
    def datetime_to_nanoseconds(self, dt):
        """Chuyển đổi đối tượng datetime thành timestamp nanoseconds"""
        # Chuyển đổi datetime thành timestamp (giây)
        epoch = datetime(1970, 1, 1)
        timestamp_seconds = (dt - epoch).total_seconds()
        # Chuyển đổi thành nanoseconds
        timestamp_nanoseconds = int(timestamp_seconds * 1_000_000_000)
        return timestamp_nanoseconds
        
    def generate_data_point(self, traffic_type, timestamp_ns):
        """Tạo một điểm dữ liệu đơn lẻ cho loại lưu lượng được chỉ định"""
        
        profile = self.traffic_profiles[traffic_type]
        
        # Tạo độ dài gói tin
        frame_len = max(
            profile["frame_len"]["min"], 
            int(np.random.normal(profile["frame_len"]["mean"], profile["frame_len"]["std"]))
        )
        
        # Chọn IP nguồn và đích
        src_ip = random.choice(self.src_ips)
        dst_ip = random.choice(self.dst_ips)
        
        # Chọn cổng dựa trên loại lưu lượng
        if traffic_type == "video":
            src_port = random.randint(1024, 65535)
            dst_port = random.choice(self.video_ports)
            ip_proto = 6  # TCP phổ biến nhất cho video
        else:  # voip
            src_port = random.randint(1024, 65535)
            dst_port = random.choice(self.voip_ports)
            ip_proto = 17  # UDP phổ biến nhất cho VoIP
        
        # Chọn một thiết bị
        device_id = random.choice(self.devices)
        
        # Tạo điểm dữ liệu
        data_point = {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "ip_proto": ip_proto,
            "device_id": device_id,
            "frame_len": frame_len,
            "lable": traffic_type,
            "time_epoch": timestamp_ns
        }
        
        return data_point

    def save_to_influxdb(self, data_point):
        """Lưu một điểm dữ liệu vào InfluxDB"""
        try:
            point = Point("network_traffic") \
                .tag("src_ip", data_point["src_ip"]) \
                .tag("dst_ip", data_point["dst_ip"]) \
                .tag("src_port", str(data_point["src_port"])) \
                .tag("dst_port", str(data_point["dst_port"])) \
                .tag("ip_proto", str(data_point["ip_proto"])) \
                .tag("device_id", data_point["device_id"]) \
                .tag("lable", data_point["lable"]) \
                .field("frame_len", data_point["frame_len"]) \
                .time(data_point["time_epoch"])  # Sử dụng timestamp dạng nanoseconds

            self.write_api.write(bucket=self.INFLUXDB_BUCKET, record=point)
            return True
        except Exception as e:
            logger.error(f"Lỗi khi lưu vào InfluxDB: {e}")
            return False

    def generate_traffic_session(self, traffic_type, start_time_ns, duration_seconds):
        """Tạo một phiên lưu lượng với các thuộc tính nhất quán"""
        
        profile = self.traffic_profiles[traffic_type]
        timestamp_ns = start_time_ns
        
        # Tính thời gian kết thúc (ns)
        end_time_ns = start_time_ns + (duration_seconds * 1_000_000_000)
        
        data_points = []
        
        # Tạo một tập hợp các tham số kết nối nhất quán cho phiên này
        session_params = {
            "src_ip": random.choice(self.src_ips),
            "dst_ip": random.choice(self.dst_ips),
            "device_id": random.choice(self.devices),
        }
        
        if traffic_type == "video":
            session_params["src_port"] = random.randint(1024, 65535)
            session_params["dst_port"] = random.choice(self.video_ports)
            session_params["ip_proto"] = 6  # TCP
        else:  # voip
            session_params["src_port"] = random.randint(1024, 65535)
            session_params["dst_port"] = random.choice(self.voip_ports)
            session_params["ip_proto"] = 17  # UDP
        
        # Xác định khoảng thời gian ban đầu và kết thúc để tạo đường cong tăng dần
        if traffic_type == "video":
            # Khoảng thời gian cho video
            initial_interval_ms = 5  # 5ms ban đầu
            final_interval_ms = 25   # 25ms cuối
        else:  # voip
            # Khoảng thời gian cho voip
            initial_interval_ms = 10  # 10ms ban đầu
            final_interval_ms = 30    # 30ms cuối
        
        # Ước tính số gói tin dựa trên khoảng thời gian trung bình
        avg_interval_ms = (initial_interval_ms + final_interval_ms) / 2
        est_packets = int(duration_seconds * 1000 / avg_interval_ms)
        
        # Theo dõi số thứ tự gói để tính khoảng thời gian tăng dần
        packet_count = 0
        
        # Tạo các gói tin cho đến khi đạt thời gian kết thúc
        while timestamp_ns < end_time_ns:
            # Kiểm tra đợt tăng gói tin
            if random.random() < profile["burst_likelihood"]:
                # Tạo một loạt gói tin với khoảng thời gian rất ngắn
                burst_size = random.randint(3, 8)
                for _ in range(burst_size):
                    frame_len = max(
                        profile["frame_len"]["min"], 
                        int(np.random.normal(profile["frame_len"]["mean"], profile["frame_len"]["std"]))
                    )
                    
                    data_point = {
                        **session_params,
                        "frame_len": frame_len,
                        "lable": traffic_type,
                        "time_epoch": timestamp_ns
                    }
                    
                    data_points.append(data_point)
                    # Khoảng thời gian rất ngắn giữa các gói tin trong đợt tăng đột biến - 1ms
                    timestamp_ns += 1_000_000  # 1ms in nanoseconds
                    packet_count += 1
            else:
                # Tạo một gói tin bình thường
                frame_len = max(
                    profile["frame_len"]["min"], 
                    int(np.random.normal(profile["frame_len"]["mean"], profile["frame_len"]["std"]))
                )
                
                data_point = {
                    **session_params,
                    "frame_len": frame_len,
                    "lable": traffic_type,
                    "time_epoch": timestamp_ns
                }
                
                data_points.append(data_point)
                packet_count += 1
            
            # Tính khoảng thời gian tăng dần dựa trên tỷ lệ tiến trình
            # Tỷ lệ tiến trình từ 0.0 (đầu) đến 1.0 (cuối)
            progress_ratio = min(1.0, packet_count / est_packets)
            
            # Tính khoảng thời gian hiện tại dựa trên tỷ lệ tiến trình
            current_interval_ms = initial_interval_ms + (final_interval_ms - initial_interval_ms) * progress_ratio
            
            # Thêm một chút nhiễu ngẫu nhiên (±10%)
            jitter_factor = 1 + random.uniform(-0.1, 0.1)
            current_interval_ms = current_interval_ms * jitter_factor
            
            # Đảm bảo khoảng thời gian không nhỏ hơn giá trị tối thiểu
            current_interval_ms = max(profile["packet_interval"]["min"], current_interval_ms)
            
            # Chuyển đổi từ ms sang ns
            timestamp_ns += int(current_interval_ms * 1_000_000)
        
        return data_points

    def generate_data(self):
        """Tạo dữ liệu lưu lượng mạng cho số giây đã chỉ định"""
        logger.info(f"Đang tạo {self.num_seconds} giây dữ liệu lưu lượng mạng...")
        
        # Bắt đầu từ thời gian hiện tại trừ đi số giây
        end_time = datetime.now() - timedelta(hours=7)
        start_time = end_time - timedelta(seconds=self.num_seconds)
        logger.info(f"Tạo dữ liệu từ {start_time} đến {end_time}")
        
        # Chuyển đổi thời gian thành nanoseconds
        end_time_ns = self.datetime_to_nanoseconds(end_time)
        start_time_ns = self.datetime_to_nanoseconds(start_time)
        
        total_points = 0
        successful_writes = 0
        
        # Tạo dữ liệu cho cả hai loại lưu lượng: video và voip
        for traffic_type in ["video", "voip"]:
            # Tạo một phiên với thời lượng bằng toàn bộ khoảng thời gian được yêu cầu
            session_duration = self.num_seconds
            
            logger.info(f"Đang tạo phiên {traffic_type} tại {start_time} trong {session_duration} giây...")
            
            # Tạo tất cả các điểm dữ liệu cho phiên này
            session_data = self.generate_traffic_session(traffic_type, start_time_ns, session_duration)
            
            # Lưu dữ liệu phiên
            batch_size = 100
            for i in range(0, len(session_data), batch_size):
                batch = session_data[i:i+batch_size]
                for point in batch:
                    total_points += 1
                    success = self.save_to_influxdb(point)
                    if success:
                        successful_writes += 1
                
                # Báo cáo tiến độ sau mỗi lô
                logger.info(f"Tiến độ {traffic_type}: {successful_writes}/{total_points} điểm đã được ghi")
            
            logger.info(f"Hoàn thành tạo dữ liệu {traffic_type}.")
        
        logger.info(f"Hoàn thành tạo dữ liệu. {successful_writes}/{total_points} điểm đã được ghi thành công.")
        
        return successful_writes

def main():
    parser = argparse.ArgumentParser(description='Tạo dữ liệu lưu lượng mạng tổng hợp cho phân loại')
    parser.add_argument('--seconds', type=int, default=2, help='Số giây lưu lượng cần tạo')
    parser.add_argument('--seed', type=int, default=42, help='Seed ngẫu nhiên để tái tạo kết quả')
    args = parser.parse_args()
    
    generator = NetworkTrafficGenerator(num_seconds=args.seconds, seed=args.seed)
    points_written = generator.generate_data()
    
    logger.info(f"Đã tạo thành công {points_written} điểm dữ liệu trong khoảng {args.seconds} giây")

if __name__ == "__main__":
    main()