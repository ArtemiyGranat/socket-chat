import socket
import threading
# import os
import sys
import pickle

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

    def send_data(self, data) -> None:
        enc_data = self._encryptor.encrypt(data['data'])
        data['data'] = enc_data
        data = pickle.dumps(data)
        self._socket.send(data)

    def check_username_validity(self, username) -> None:
        self.send_username(username)
        answer = self._socket.recv(8192).decode(ENCODING)
        if (answer == 'OK'):
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
                packet = self._socket.recv(8192)
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
                dec_message = self._encryptor.decrypt(packet['data'])
                get_message(username, dec_message)
            except Exception:
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
def get_message(usrname, msg) -> None:
    eel.get_recv_msg(usrname, msg)


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
