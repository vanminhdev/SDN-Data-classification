from flask import Flask, request, jsonify
import logging
import time

from db_handler import DatabaseHandler
from classification_handler import ClassificationHandler
from flow_rule_handler import FlowRuleHandler
import os

app = Flask(__name__)

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo handlers
db = DatabaseHandler()
classifier = ClassificationHandler()
flow_handler = FlowRuleHandler()

@app.route('/api/push-data', methods=['POST'])
def receive_data():
    # Lấy dữ liệu JSON gửi từ Java
    data = request.get_json()

    # Kiểm tra dữ liệu có hợp lệ không
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Lấy từng giá trị từ dữ liệu gửi đến
    try:
        # Chuyển đổi thời gian từ epoch thành ms
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

        # Xử lý phân loại
        classification_result = classifier.process_packet(packet_data)
        
        # Trả về kết quả nếu có phân loại mới
        if classification_result:
            # Xử lý sau khi phân loại: set meter cho flow rule
            service_type = classification_result.get('service_type')
            logger.info(f"Flow thuộc phân loại {service_type} -> đang update flow rule")
            
            # Gọi ONOS API để cập nhật flow rule
            update_success = flow_handler.update_flow_rule(packet_data, service_type)
            
            # Thêm thông tin cập nhật vào kết quả
            classification_result['flow_rule_updated'] = update_success
            
            return jsonify({
                "status": "classified",
                "result": classification_result
            }), 200
        else:
            logger.info("Chưa phân loại được gói tin")

        return jsonify({"status": "received"}), 200 #mới tiếp nhận gói tin chưa phân loại

    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
