import socket
import threading
import os
import sys
import time
import pickle
import tkinter as tk
from tkinter import filedialog as fd
from tkinter.filedialog import asksaveasfile

import eel

from encryptor import Encryptor

eel.init('gui')

PORT = 5050
ENCODING = 'utf-8'

global client


class Client:
    def __init__(self, server_address) -> None:
        file_dir = os.path.join('files')
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)
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
                    'file_name': self._username + '-' + os.path.basename(path),
                    'data': data
                }
                packet = pickle.dumps(packet)
                self._socket.sendall(packet)
                time.sleep(0.1)
                if data == b'':
                    break
            f.close()
        time.sleep(0.1)

    def recv_file(self, packet) -> None:
        path = os.path.join('files', packet['file_name'])
        if path:
            with open(path, "wb") as f:
                while True:
                    packet = self._socket.recv(32768)
                    if packet:
                        packet = pickle.loads(packet)
                        if packet['data'] == b'':
                            break
                        f.write(packet['data'])
                f.close()
        time.sleep(0.1)

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
                message = packet['data']
                if packet['username'] != 'server':
                    message = self._encryptor.decrypt(packet['data'])
                get_message(username, message)
            except Exception as e:
                print(e)
                print('[ERROR] Disconnecting from the server')
                self._socket.close()
                eel.close_window()
                break
        # packet = {
        #     'type': 'disconnect_msg'
        #     }
        # packet = pickle.dumps(packet)
        # self._socket.sendall(packet)
        # self._socket.close()


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
    if file_size <= 60000000:
        packet = {
            'type': 'request',
            'username': client._username,
            'file_name': client._username + '-' + os.path.basename(file_path),
            'file_size': file_size
        }
        client.send_data(packet)
        client.send_file(file_path)
    else:
        eel.get_exception('File size must be less than 60 megabytes,'
                          ' please choose another file')


@eel.expose
def open_file() -> None:
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", 1)
    filepath = fd.askopenfilename()
    if filepath:
        eel.show_filename(filepath)
    else:
        eel.show_input()


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


def run() -> None:
    thread = threading.Thread(target=client.handle_messages)
    thread.start()
    eel.open_chat()


@eel.expose
def is_connected() -> None:
    return client._is_connected


def close_callback(route, websockets):
    print('Disconnecting from the server')
    # client._is_connected = False
    # client._socket.close()
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)


if __name__ == '__main__':
    try:
        server_ip = socket.gethostbyname(sys.argv[1])
        server_address = (server_ip, PORT)
        client = Client(server_address)
        eel.start('index.html', port=0, size=(800, 500),
                close_callback=close_callback)
    except IndexError as e:
        print('[ERROR] IP address was not provided')
