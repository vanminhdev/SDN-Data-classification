import os
import numpy as np
import pandas as pd
import logging
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import argparse
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ignore FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)

# Constants
TIME_WINDOW_MS = 1000  # Time window in milliseconds (1 second)
MODEL_OUTPUT_PATH = 'models/traffic_classifier.pkl'

class NetworkTrafficModelTrainer:
    def __init__(self, csv_path=None):
        self.csv_path = csv_path or 'data/network_traffic.csv'
        
    def fetch_data(self):
        """Lấy dữ liệu lưu lượng mạng từ file CSV"""
        logger.info(f"Đang đọc dữ liệu lưu lượng mạng từ file {self.csv_path}...")
        
        try:
            # Đọc dữ liệu từ CSV
            df = pd.read_csv(self.csv_path)
            
            if df.empty:
                logger.error("File CSV không chứa dữ liệu")
                return None
                
            # Kiểm tra các cột bắt buộc
            required_columns = ['frame_len', 'timestamp', 'label']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"Thiếu các cột bắt buộc: {missing_columns}. Các cột hiện có: {df.columns}")
                return None
            
            # Chuyển đổi timestamp sang định dạng số
            try:
                df['timestamp'] = pd.to_numeric(df['timestamp'])
            except ValueError as e:
                logger.error(f"Lỗi khi chuyển đổi timestamp sang số: {e}")
                logger.info(f"Mẫu giá trị timestamp: {df['timestamp'].head()}")
                return None
                
            # Chuyển đổi frame_len sang số nguyên
            try:
                df['frame_len'] = pd.to_numeric(df['frame_len'])
            except ValueError as e:
                logger.error(f"Lỗi khi chuyển đổi frame_len sang số nguyên: {e}")
                logger.info(f"Mẫu giá trị frame_len: {df['frame_len'].head()}")
                return None
            
            # Log thống kê cơ bản
            logger.info(f"Đã đọc {len(df)} bản ghi từ file CSV")
            
            # Hiển thị thông tin về nhãn
            if 'label' in df.columns:
                label_counts = df['label'].value_counts()
                logger.info(f"Các nhãn trong dữ liệu: {dict(label_counts)}")
            else:
                logger.warning("Không tìm thấy cột 'label' trong dữ liệu")
            
            return df
        except Exception as e:
            logger.error(f"Lỗi khi đọc file CSV: {e}")
            return None

    def process_data(self, df):
        """Xử lý dữ liệu thô và trích xuất các đặc trưng dựa trên thời gian"""
        logger.info("Đang xử lý dữ liệu và trích xuất đặc trưng...")
        
        if df is None:
            return None
            
        # Kiểm tra các cột bắt buộc
        required_columns = ['timestamp', 'frame_len', 'label']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"Thiếu các cột bắt buộc: {missing_columns}. Các cột hiện có: {df.columns}")
            return None
        
        # Sắp xếp dữ liệu theo timestamp    
        df = df.sort_values('timestamp')
        
        # Kiểm tra và hiển thị các kiểu dữ liệu của các cột
        logger.info(f"Kiểu dữ liệu của các cột: {df.dtypes}")
        
        # Khởi tạo mảng để lưu các đặc trưng
        grouped_data = []
        
        # Nhóm theo nhãn và tạo các cửa sổ thời gian
        labels = df['label'].unique()
        for label in labels:
            logger.info(f"Đang xử lý nhãn: {label}")
            label_df = df[df['label'] == label].copy()
            
            # Tạo cửa sổ thời gian (window_id) dựa trên khoảng thời gian TIME_WINDOW_MS
            # Chuyển đổi timestamp thành milliseconds từ điểm bắt đầu
            min_timestamp = label_df['timestamp'].min()
            label_df['window_id'] = ((label_df['timestamp'] - min_timestamp) // 
                                   (TIME_WINDOW_MS * 1_000_000))  # nano to milliseconds conversion
            
            # Nhóm theo ID cửa sổ thời gian
            for window, group in label_df.groupby('window_id'):
                if len(group) < 2:  # Bỏ qua các cửa sổ chỉ có một gói tin
                    continue
                
                # Tính toán các đặc trưng
                packet_count = len(group)
                average_packet_length = group['frame_len'].mean()
                
                # Sắp xếp theo thời gian và tính thời gian giữa các gói tin
                group = group.sort_values('timestamp')
                inter_packet_times = group['timestamp'].diff() / 1_000_000  # convert nano to milliseconds
                inter_packet_times = inter_packet_times[1:]  # Loại bỏ giá trị NaN đầu tiên
                
                # Tính các đặc trưng thời gian
                if len(inter_packet_times) > 0:
                    average_inter_packet_time = inter_packet_times.mean()
                    inter_packet_time_variance = inter_packet_times.var() if len(inter_packet_times) > 1 else 0
                else:
                    average_inter_packet_time = 0
                    inter_packet_time_variance = 0
                
                # Tính phương sai kích thước gói tin
                packet_size_variance = group['frame_len'].var() if len(group) > 1 else 0
                
                # Tạo bản ghi đặc trưng
                feature_record = {
                    'packet_count': packet_count,
                    'average_packet_length': average_packet_length,
                    'average_inter_packet_time': average_inter_packet_time,
                    'packet_size_variance': packet_size_variance,
                    'inter_packet_time_variance': inter_packet_time_variance,
                    'label': label
                }
                
                grouped_data.append(feature_record)
        
        feature_df = pd.DataFrame(grouped_data)
        
        if len(feature_df) == 0:
            logger.error("Không tạo được bản ghi đặc trưng nào sau quá trình xử lý")
            return None
            
        logger.info(f"Đã tạo {len(feature_df)} bản ghi đặc trưng")
        
        # Kiểm tra và xử lý giá trị NaN hoặc vô hạn
        # Kiểm tra dữ liệu trước khi tìm vô hạn
        logger.info(f"Kiểu dữ liệu của các cột đặc trưng: {feature_df.dtypes}")
        
        # Kiểm tra NaN và thay thế
        if feature_df.isnull().any().any():
            logger.warning("Phát hiện giá trị NaN trong đặc trưng, đang thay thế...")
            feature_df = feature_df.fillna(0)
        
        # Kiểm tra các giá trị vô hạn cho từng cột số
        numeric_columns = feature_df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            inf_mask = np.isinf(feature_df[col])
            if inf_mask.any():
                logger.warning(f"Phát hiện giá trị vô hạn trong cột {col}, đang thay thế...")
                feature_df.loc[inf_mask, col] = 0
        
        return feature_df

    def train_model(self, feature_df):
        """Huấn luyện mô hình RandomForestClassifier"""
        logger.info("Đang huấn luyện mô hình RandomForestClassifier...")
        
        if feature_df is None or len(feature_df) == 0:
            logger.error("Không có dữ liệu để huấn luyện")
            return None
            
        # Chuẩn bị dữ liệu
        X = feature_df.drop('label', axis=1)
        y = feature_df['label']
        
        # Kiểm tra số lượng lớp
        unique_classes = y.nunique()
        if unique_classes < 2:
            logger.error(f"Không đủ lớp để huấn luyện. Chỉ có {unique_classes} lớp.")
            return None
        
        # Chia dữ liệu
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        # Huấn luyện mô hình
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Đánh giá mô hình
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Độ chính xác mô hình: {accuracy:.4f}")
        
        logger.info("Báo cáo phân loại:")
        class_report = classification_report(y_test, y_pred)
        logger.info("\n" + class_report)
        
        # Tạo ma trận nhầm lẫn
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=model.classes_, yticklabels=model.classes_)
        plt.xlabel('Dự đoán')
        plt.ylabel('Thực tế')
        plt.title('Ma trận nhầm lẫn')
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
        plt.savefig(os.path.join(os.path.dirname(MODEL_OUTPUT_PATH), 'confusion_matrix.png'))
        
        # Độ quan trọng của đặc trưng
        feature_importance = pd.DataFrame({
            'Đặc trưng': X.columns,
            'Độ quan trọng': model.feature_importances_
        }).sort_values('Độ quan trọng', ascending=False)
        
        logger.info("Độ quan trọng của đặc trưng:")
        logger.info(feature_importance)
        
        return model

    def save_model(self, model):
        """Lưu mô hình đã huấn luyện vào tập tin"""
        if model is None:
            logger.error("Không có mô hình để lưu")
            return
            
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
        
        with open(MODEL_OUTPUT_PATH, 'wb') as f:
            pickle.dump(model, f)
            
        logger.info(f"Đã lưu mô hình vào {MODEL_OUTPUT_PATH}")

    def run(self):
        """Thực thi toàn bộ quy trình huấn luyện"""
        raw_data = self.fetch_data()
        if raw_data is not None:
            logger.info("Dữ liệu đã được đọc thành công, tiếp tục xử lý...")
            feature_data = self.process_data(raw_data)
            if feature_data is not None:
                model = self.train_model(feature_data)
                self.save_model(model)
                logger.info("Huấn luyện hoàn thành thành công!")
            else:
                logger.error("Không thể tiếp tục do lỗi trong quá trình xử lý dữ liệu")
        else:
            logger.error("Không thể tiếp tục do lỗi khi đọc dữ liệu")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Huấn luyện mô hình phân loại lưu lượng mạng')
    parser.add_argument('--input', type=str, default=None,
                        help='Đường dẫn đến file CSV chứa dữ liệu huấn luyện')
    args = parser.parse_args()
    
    trainer = NetworkTrafficModelTrainer(csv_path=args.input)
    trainer.run()