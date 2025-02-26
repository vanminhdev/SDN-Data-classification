import os
import argparse
import pandas as pd
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InfluxDBExporter:
    def __init__(self):
        """Khởi tạo Exporter dữ liệu từ InfluxDB"""
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
        self.query_api = self.client.query_api()

    def query_data(self, hours=1):
        """Truy vấn dữ liệu từ InfluxDB trong khoảng thời gian xác định
        
        Args:
            hours: Số giờ dữ liệu cần truy vấn tính từ hiện tại
            
        Returns:
            DataFrame chứa dữ liệu được truy vấn
        """
        logger.info(f"Đang truy vấn dữ liệu từ {hours} giờ trước...")
        
        # Xây dựng truy vấn Flux
        query = f'''
        from(bucket: "{self.INFLUXDB_BUCKET}")
          |> range(start: -{hours}h)
          |> filter(fn: (r) => r._measurement == "network_traffic")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
        '''
        
        # Thực hiện truy vấn
        try:
            result = self.query_api.query_data_frame(query)
            
            if result.empty:
                logger.warning("Không có dữ liệu được tìm thấy trong khoảng thời gian được chỉ định.")
                return None
            
            # Nếu kết quả là một danh sách các DataFrame, hợp nhất chúng
            if isinstance(result, list):
                result = pd.concat(result)
            
            # Xử lý dữ liệu
            # Chọn và đổi tên các cột cần thiết
            columns_to_keep = {
                'src_ip': 'src_ip',
                'dst_ip': 'dst_ip',
                'src_port': 'src_port',
                'dst_port': 'dst_port', 
                'ip_proto': 'ip_proto',
                'device_id': 'device_id',
                'frame_len': 'frame_len',
                'lable': 'label',
                '_time': 'timestamp'
            }
            
            # Lọc và đổi tên cột
            result = result[list(columns_to_keep.keys())].rename(columns=columns_to_keep)
            
            # Chuyển đổi các cột thành kiểu dữ liệu phù hợp
            result['src_port'] = result['src_port'].astype(int)
            result['dst_port'] = result['dst_port'].astype(int)
            result['ip_proto'] = result['ip_proto'].astype(int)
            result['frame_len'] = result['frame_len'].astype(int)
            
            # Chuyển đổi timestamp sang nano giấy
            result['timestamp'] = result['timestamp'].astype('int64')
            
            logger.info(f"Đã truy vấn thành công {len(result)} bản ghi.")
            return result
            
        except Exception as e:
            logger.error(f"Lỗi khi truy vấn dữ liệu: {e}")
            return None

    def export_to_csv(self, df, output_dir="data", filename=None):
        """Xuất DataFrame ra file CSV
        
        Args:
            df: DataFrame cần xuất
            output_dir: Thư mục đầu ra (mặc định: "data")
            filename: Tên file (mặc định: network_traffic_test_YYYY-MM-DD_HH-MM.csv)
            
        Returns:
            Đường dẫn đến file CSV đã xuất
        """
        if df is None or df.empty:
            logger.error("Không có dữ liệu để xuất.")
            return None
            
        try:
            # Tạo thư mục nếu chưa tồn tại
            os.makedirs(output_dir, exist_ok=True)
            
            # Tên file mặc định nếu không được cung cấp
            if filename is None:
                current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
                filename = f"network_traffic_test_{current_time}.csv"
            
            # Đường dẫn đầy đủ
            full_path = os.path.join(output_dir, filename)
            
            # Xuất ra CSV
            df.to_csv(full_path, index=False)
            logger.info(f"Đã xuất dữ liệu thành công vào file {full_path}")
            
            return full_path
            
        except Exception as e:
            logger.error(f"Lỗi khi xuất dữ liệu: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Xuất dữ liệu lưu lượng mạng từ InfluxDB ra CSV')
    parser.add_argument('--hours', type=float, default=1, 
                        help='Số giờ dữ liệu cần truy vấn tính từ hiện tại (mặc định: 1 giờ)')
    parser.add_argument('--output', type=str, default='data',
                        help='Thư mục đầu ra (mặc định: "data")')
    parser.add_argument('--filename', type=str, default=None,
                        help='Tên file (mặc định: network_traffic_test_YYYY-MM-DD_HH-MM.csv)')
    args = parser.parse_args()
    
    exporter = InfluxDBExporter()
    data = exporter.query_data(hours=args.hours)
    
    if data is not None:
        csv_path = exporter.export_to_csv(data, output_dir=args.output, filename=args.filename)
        if csv_path:
            logger.info(f"Đã xuất {len(data)} bản ghi ra file: {csv_path}")
            
            # In thống kê cơ bản
            traffic_counts = data['label'].value_counts()
            logger.info("Phân bố loại lưu lượng:")
            for label, count in traffic_counts.items():
                logger.info(f"  - {label}: {count} bản ghi ({count/len(data)*100:.1f}%)")

if __name__ == "__main__":
    main()