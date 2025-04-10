import os
from pymongo import MongoClient
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self):
        # Cấu hình MongoDB
        self.MONGODB_HOST = os.getenv('MONGODB_HOST', 'localhost')
        self.MONGODB_PORT = int(os.getenv('MONGODB_PORT', 27017))
        self.MONGODB_DATABASE = os.getenv('MONGODB_DATABASE', 'sdn')
        self.MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'traffic')
        self.mongo_uri = f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}"
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.MONGODB_DATABASE]
        self.collection = self.db[self.MONGODB_COLLECTION]
        
    def save_traffic_data(self, data):
        try:
            label = os.getenv('LABEL', 'unknown')
            
            document = {
                'src_port': data['src_port'],
                'dst_port': data['dst_port'],
                'frame_len': data['frame_len'],
                'ip_proto': data['ip_proto'],
                'device_id': data['device_id'],
                'src_ip': data['src_ip'],
                'dst_ip': data['dst_ip'],
                'label': label,
                'time_epoch': data['time_epoch'],
                'created_at': datetime.now()
            }

            # Insert document into MongoDB
            result = self.collection.insert_one(document)
            logger.info(f"Data saved successfully to MongoDB with ID: {result.inserted_id}, data: {data}")
            return True
        except Exception as e:
            logger.error(f"Error saving to database: {e}, data: {data}")
            return False