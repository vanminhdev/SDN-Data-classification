import socket
import ssl
import pyaudio
import wave

CHUNK = 1024

def voip_server(host='0.0.0.0', port=12345):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile='server.crt', keyfile='server.key')

    wf = wave.open('speaker2.wav', 'rb')  # File âm thanh của người thứ 2
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, port))
        sock.listen(5)
        print(f"VoIP Server running on {host}:{port} with SSL/TLS")
        
        with context.wrap_socket(sock, server_side=True) as ssock:
            conn, addr = ssock.accept()
            print(f"Connection from {addr}")

            # Nhận âm thanh từ client và phát lại
            while True:
                data = conn.recv(CHUNK)
                if not data:
                    break
                stream.write(data)  # Phát lại âm thanh
                # Gửi phản hồi âm thanh
                conn.sendall(wf.readframes(CHUNK))
            
            conn.close()
    
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    voip_server()
