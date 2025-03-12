import os
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import logging

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self):
        # Cấu hình InfluxDB
        self.INFLUXDB_URL = "http://influxdb:8086"
        self.INFLUXDB_TOKEN = os.getenv('INFLUXDB_ADMIN_TOKEN')
        self.INFLUXDB_ORG = "huce"
        self.INFLUXDB_BUCKET = "network_traffic"
        
        # Khởi tạo client
        self.client = InfluxDBClient(
            url=self.INFLUXDB_URL, 
            token=self.INFLUXDB_TOKEN, 
            org=self.INFLUXDB_ORG
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def save_traffic_data(self, data):
        try:
            # Get label from environment variable or use a default if not set
            label = os.getenv('LABEL', 'unknown')
            
            point = Point("network_traffic") \
                .tag("src_port", data['src_port']) \
                .tag("dst_port", data['dst_port']) \
                .field("frame_len", data['frame_len']) \
                .tag("ip_proto", data['ip_proto']) \
                .tag("device_id", data['device_id']) \
                .tag("src_ip", data['src_ip']) \
                .tag("dst_ip", data['dst_ip']) \
                .tag("label", label) \
                .time(data['time_epoch'])

            self.write_api.write(bucket=self.INFLUXDB_BUCKET, record=point)
            logger.info(f"Data saved successfully to InfluxDB: {data}")
            return True
        except Exception as e:
            logger.error(f"Error saving to database: {e}, data: {data}")
            return False