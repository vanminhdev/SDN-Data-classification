from flask import Flask, request, jsonify
import logging
import time

from db.db_handler_mongo import DatabaseHandler
from classification_handler import ClassificationHandler
from flow_rule_handler import FlowRuleHandler
import os

app = Flask(__name__)

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo handlers
db = DatabaseHandler()
flow_handler = FlowRuleHandler()
classifier = ClassificationHandler(flow_handler=flow_handler)

@app.route('/api/push-data', methods=['POST'])
def receive_data():
    # Lấy dữ liệu JSON gửi từ Java
    data = request.get_json()

    # Kiểm tra dữ liệu có hợp lệ không
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Lấy từng giá trị từ dữ liệu gửi đến
    try:
        time_epoch = data.get('time_epoch')
        src_port = data.get('src_port')
        dst_port = data.get('dst_port')
        frame_len = data.get('frame_len')
        ip_proto = data.get('ip_proto')
        device_id = data.get('device_id')
        src_ip = data.get('src_ip')
        dst_ip = data.get('dst_ip')

        # Xử lý dữ liệu
        packet_data = {
            "time_epoch": time_epoch,
            "src_port": src_port,
            "dst_port": dst_port,
            "frame_len": frame_len,
            "ip_proto": ip_proto,
            "device_id": device_id,
            "src_ip": src_ip,
            "dst_ip": dst_ip
        }

        # Log dữ liệu nhận được
        logger.info(f"Received data: {packet_data}")
          # Kiểm tra chế độ thu thập dữ liệu
        is_collect_mode = os.environ.get('IS_COLLECT', 'false').lower() == 'true'
        
        # Lưu dữ liệu không phân loại nếu đang ở chế độ thu thập
        if is_collect_mode:
            # Lưu dữ liệu vào cơ sở dữ liệu
            db.save_traffic_data(packet_data)
            logger.info("Đã thu thập dữ liệu")
            return jsonify({"status": "collected"}), 200

        # Thêm gói tin vào buffer cho phân loại định kỳ và kiểm tra kết quả phân loại mới nhất
        classification_result = classifier.simplified_process_packet(packet_data)
        
        # Nếu có kết quả phân loại cho flow này
        if classification_result:
            # Phân loại đã được tự động cập nhật trong thread phân loại
            service_type = classification_result.get('service_type')
            logger.info(f"Flow thuộc phân loại {service_type}")
            
            return jsonify({
                "status": "classified",
                "result": classification_result
            }), 200
        else:
            # Gói tin đã được đưa vào buffer, đang đợi phân loại
            logger.info("Đã thêm gói tin vào buffer, đang đợi phân loại")
            return jsonify({"status": "buffered"}), 200

    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
