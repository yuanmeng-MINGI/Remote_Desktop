import cv2
import pyautogui
import numpy as np
import socket
import struct
import pickle
import time

def connect_to_server():
    """尝试连接到服务器"""
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('127.0.0.1', 9999))
            print("成功连接到服务器")
            return client_socket
        except socket.error:
            print("连接失败，5秒后重试...")
            time.sleep(5)

screen_width, screen_height = pyautogui.size()

client_socket = connect_to_server()

try:
    while True:
        command = client_socket.recv(1024).decode()

        if command == 'capture':
            screenshot = pyautogui.screenshot(region=(0, 0, screen_width, screen_height))
            screenshot_np = np.array(screenshot)
            screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            _, frame = cv2.imencode('.jpg', screenshot_np, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            data = pickle.dumps(frame)
            size = len(data)
            client_socket.sendall(struct.pack(">L", size) + data)
        elif command == 'exit':
            break

except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
    print(f"与服务器连接丢失: {e}")
    client_socket.close()
    client_socket = connect_to_server()
except Exception as e:
    print(f"发生错误: {e}")
finally:
    client_socket.close()
