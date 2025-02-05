import socket
import struct
import cv2
import pickle
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('127.0.0.1', 9999))
server_socket.listen(5)
print("服务端在端口 9999 上监听...")

while True:
    try:
        client_socket, addr = server_socket.accept()
        print(f"连接来自: {addr}")
        while True:
            client_socket.sendall(b'capture')
            data = b""
            payload_size = struct.calcsize(">L")
            while len(data) < payload_size:
                packet = client_socket.recv(4096)
                if not packet:
                    raise ConnectionResetError("连接被客户端重置")
                data += packet

            if len(data) < payload_size:
                raise ConnectionResetError("数据包不完整")

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]

            while len(data) < msg_size:
                data += client_socket.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data)
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            cv2.imshow("远程屏幕", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                client_socket.sendall(b'exit')
                break

            time.sleep(0.04)

    except ConnectionResetError as e:
        print(f"客户端连接丢失: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        client_socket.close()

server_socket.close()
cv2.destroy
