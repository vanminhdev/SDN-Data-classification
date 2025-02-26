from flask import Flask, request, jsonify
import logging

from db_handler import DatabaseHandler

app = Flask(__name__)

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Khởi tạo database handler
db = DatabaseHandler()

# Định nghĩa route POST để nhận dữ liệu từ Java
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
        src_port = data.get('tcp_src_port')
        dst_port = data.get('tcp_dst_port')
        frame_len = data.get('frame_len')
        ip_proto = data.get('ip_proto')
        device_id = data.get('device_id')
        src_ip = data.get('src_ip')
        dst_ip = data.get('dst_ip')

        # Xử lý dữ liệu
        input = {
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
        logger.info(f"Received data: {input}")
        db.save_traffic_data(input)
        return "Ok", 200

    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
