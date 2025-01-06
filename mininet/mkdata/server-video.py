import socket
import ssl
import struct
import cv2
import numpy as np

def video_stream_server(host='0.0.0.0', port=12345):
    # Tạo context SSL và cấu hình server SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='server.crt', keyfile='server.key')

    # Tạo socket và chấp nhận kết nối
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Video Stream Server running on {host}:{port}")
    
    # Chấp nhận kết nối từ client
    client_socket, addr = server_socket.accept()
    print(f"Connection from {addr}")
    
    # Wrap socket để sử dụng SSL/TLS
    secure_socket = context.wrap_socket(client_socket, server_side=True)
    
    # Đọc video từ file hoặc webcam
    video_capture = cv2.VideoCapture('video.mp4')  # Hoặc dùng 0 để dùng webcam
    
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        # Mã hóa frame thành JPEG
        data = cv2.imencode('.jpg', frame)[1].tobytes()
        
        # Gửi kích thước dữ liệu trước, sau đó gửi dữ liệu frame
        message_size = struct.pack("L", len(data))
        secure_socket.sendall(message_size)
        secure_socket.sendall(data)

    secure_socket.close()
    server_socket.close()
    video_capture.release()

if __name__ == "__main__":
    video_stream_server()
