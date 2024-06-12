from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

# Dictionary để lưu trữ các bản ghi theo (src_ip, dest_ip, src_port, dest_port)
records = defaultdict(list)

# Hàm giả lập xử lý dữ liệu
def process_data(src_ip, dest_ip, src_port, dest_port, data):
    print(f"Processing data for {src_ip}:{src_port} -> {dest_ip}:{dest_port}: {data}")

@app.route('/api/push-data', methods=['POST'])
def add_record():
    # Lấy dữ liệu từ request
    data = request.get_json()
    src_ip = data.get('src_ip')
    dest_ip = data.get('dest_ip')
    src_port = data.get('src_port')
    dest_port = data.get('dest_port')
    hex_data = data.get('hex_data')

    if not src_ip or not dest_ip or not src_port or not dest_port or not hex_data:
        return jsonify({"error": "Missing required fields"}), 400

    # Thêm bản ghi vào danh sách tương ứng với (src_ip, dest_ip, src_port, dest_port)
    records[(src_ip, dest_ip, src_port, dest_port)].append(hex_data)

    # Kiểm tra nếu có đủ 20 bản ghi, thì gọi hàm xử lý
    if len(records[(src_ip, dest_ip, src_port, dest_port)]) == 20:
        process_data(src_ip, dest_ip, src_port, dest_port, records[(src_ip, dest_ip, src_port, dest_port)])
        # Xóa các bản ghi đã xử lý
        del records[(src_ip, dest_ip, src_port, dest_port)]

    return jsonify({"message": "Record added successfully"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
