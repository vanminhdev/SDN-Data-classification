import socket
import ssl
import pyaudio
import wave

CHUNK = 1024

def voip_client(server_ip, port=12345):
    # Tạo context SSL không xác thực chứng chỉ
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False  # Bỏ qua việc kiểm tra tên host
    context.verify_mode = ssl.CERT_NONE  # Bỏ qua xác thực chứng chỉ

    wf = wave.open('speaker1.wav', 'rb')  # File âm thanh của người thứ 1
    
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    with socket.create_connection((server_ip, port)) as sock:
        with context.wrap_socket(sock, server_hostname=server_ip) as ssock:
            print("Connected to VoIP Server")

            # Gửi âm thanh từ file
            data = wf.readframes(CHUNK)
            while data:
                ssock.sendall(data)
                # Nhận phản hồi âm thanh
                response = ssock.recv(CHUNK)
                stream.write(response)  # Phát lại âm thanh nhận được
                data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    voip_client("172.21.128.1")  # Thay bằng IP của server
