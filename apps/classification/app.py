from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

# Cấu hình logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        tcp_src_port = data.get('tcp_src_port')
        tcp_dst_port = data.get('tcp_dst_port')
        udp_src_port = data.get('udp_src_port')
        udp_dst_port = data.get('udp_dst_port')
        frame_len = data.get('frame_len')
        ip_proto = data.get('ip_proto')

        # Xử lý dữ liệu
        input = {
            "time_epoch": time_epoch,
            "tcp_src_port": tcp_src_port,
            "tcp_dst_port": tcp_dst_port,
            "udp_src_port": udp_src_port,
            "udp_dst_port": udp_dst_port,
            "frame_len": frame_len,
            "ip_proto": ip_proto
        }

        # Log dữ liệu nhận được
        logger.info(f"Received data: {input}")

        return "Ok", 200

    except KeyError as e:
        return jsonify({"error": f"Missing field: {e}"}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
