import socket
import threading
import os
import sys
import time
import pickle
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd

import eel

from encryptor import Encryptor

eel.init('gui')

PORT = 5050
ENCODING = 'utf-8'

global client


class Client:
    def __init__(self, server_address) -> None:
        self._server_address = server_address
        self._encryptor = Encryptor()
        self._is_connected = False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_username(self, username) -> None:
        self._socket.send(username.encode(ENCODING))

    def send_file(self, path) -> None:
        with open(path, "rb") as f:
            while True:
                data = f.read(32000)
                packet = {
                    'type': 'file',
                    'username': self._username,
                    'file_name': os.path.basename(path),
                    'data': data
                }
                packet = pickle.dumps(packet)
                self._socket.sendall(packet)
                time.sleep(0.1)
                if data == b'':
                    break
            f.close()

    def recv_file(self, packet) -> None:
        path = os.path.join('files', packet['file_name'])
        with open(path, "wb") as f:
            while True:
                packet = self._socket.recv(32768)
                if packet:
                    packet = pickle.loads(packet)
                    if packet['data'] == b'':
                        break
                    f.write(packet['data'])
            f.close()

    def recv_file_message(self, packet) -> None:
        get_file(packet['username'], packet['file_name'])

    def send_data(self, data) -> None:
        if data['type'] != 'request' and data['type'] != 'download_request':
            enc_data = self._encryptor.encrypt(data['data'])
            data['data'] = enc_data
        data = pickle.dumps(data)
        self._socket.sendall(data)

    def check_username_validity(self, username) -> None:
        self.send_username(username)
        answer = self._socket.recv(16384).decode(ENCODING)
        if answer == 'OK':
            self._username = username
            self._is_connected = True
            run()
        else:
            eel.username_reentry()

    def connect(self, username) -> None:
        self._socket.connect(self._server_address)
        self.check_username_validity(username)

    def handle_messages(self) -> None:
        while self._is_connected:
            try:
                packet = self._socket.recv(16384)
                if packet:
                    packet = pickle.loads(packet)
                if not packet:
                    print('Disconnecting from the server')
                    self._socket.close()
                    eel.close_window()
                    break
                if packet['type'] == 'message':
                    username = packet['username']
                elif packet['type'] == 'private_message':
                    username = 'Private message from '
                    username += packet['username']
                elif packet['type'] == 'file_message':
                    self.recv_file_message(packet)
                    continue
                elif packet['type'] == 'file_request':
                    self.recv_file(packet)
                    continue
                dec_message = self._encryptor.decrypt(packet['data'])
                get_message(username, dec_message)
            except Exception as e:
                print(e)
                print('Error! Disconnecting from the server')
                self._socket.close()
                eel.close_window()
                break


@eel.expose
def resend_username(username) -> None:
    client.check_username_validity(username)


@eel.expose
def send_message(msg) -> None:
    if msg[0] == '@':
        packet = {
            'type': 'private_message',
            'username': client._username,
            'destination': msg.split()[0][1:],
            'data': " ".join(msg.split()[1:])
        }
    else:
        packet = {
            'type': 'message',
            'username': client._username,
            'data': msg
        }
    client.send_data(packet)


@eel.expose
def send_file(file_path) -> None:
    file_size = os.path.getsize(file_path)
    packet = {
        'type': 'request',
        'username': client._username,
        'file_name': os.path.basename(file_path),
        'file_size': file_size
    }
    client.send_data(packet)
    client.send_file(file_path)


@eel.expose
def open_file() -> None:
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    filepath = fd.askopenfilename()
    eel.show_filename(filepath)


@eel.expose
def download_file(file_name):
    packet = {
        'type': 'download_request',
        'username': client._username,
        'file_name': file_name,
    }
    client.send_data(packet)


@eel.expose
def get_message(usrname, msg) -> None:
    eel.get_recv_msg(usrname, msg)


@eel.expose
def get_file(usrname, filename) -> None:
    eel.get_recv_file(usrname, filename)


@eel.expose
def connect(username) -> None:
    try:
        client.connect(username)
    except Exception:
        print('Server is offline. Try again later')
        eel.get_exception('Server is offline. Try again later')


@eel.expose
def run() -> None:
    thread = threading.Thread(target=client.handle_messages)  # daemon
    thread.start()
    eel.open_chat()


# def close_callback(route, websockets):
#     if not websockets:
#         client._is_connected = False
#         client._socket.close()
#         exit()


if __name__ == '__main__':
    server_ip = socket.gethostbyname(sys.argv[1])
    server_address = (server_ip, PORT)
    client = Client(server_address)
    eel.start('index.html', port=0, size=(800, 500))
#   close_callback=close_callback)
