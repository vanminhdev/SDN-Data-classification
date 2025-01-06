import socket
import ssl
import struct
import pygame
import numpy as np
import cv2

def video_stream_client(server_ip, port=12345):
    # Tạo context SSL không xác thực chứng chỉ
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False  # Bỏ qua kiểm tra hostname
    context.verify_mode = ssl.CERT_NONE  # Bỏ qua xác thực chứng chỉ

    # Tạo kết nối SSL với server
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, port))
    
    secure_socket = context.wrap_socket(client_socket, server_hostname=server_ip)
    
    # Khởi tạo Pygame để hiển thị video
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    
    while True:
        # Nhận kích thước dữ liệu của frame
        data_size = struct.unpack("L", secure_socket.recv(struct.calcsize("L")))[0]
        
        # Nhận dữ liệu frame
        data = b""
        while len(data) < data_size:
            data += secure_socket.recv(4096)
        
        # Giải mã dữ liệu frame thành hình ảnh
        frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), 1)
        
        if frame is None:
            break
        
        # Chuyển đổi từ BGR (OpenCV) sang RGB (Pygame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Chuyển frame thành Surface của Pygame
        frame_surface = pygame.surfarray.make_surface(frame)
        
        # Hiển thị frame lên màn hình
        screen.blit(frame_surface, (0, 0))
        pygame.display.update()
        
        # Kiểm tra thoát khi nhấn phím 'q'
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
                pygame.quit()
                return

    secure_socket.close()
    pygame.quit()

if __name__ == "__main__":
    video_stream_client("127.0.0.1")  # Thay bằng IP của server
