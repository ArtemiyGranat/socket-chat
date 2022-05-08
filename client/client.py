import socket
import threading
# import os
# import sys
import pickle

import eel

from encryptor import Encryptor

eel.init('gui')

PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_ADDRESS = (SERVER_IP, PORT)
ENCODING = "utf-8"
DISCONNECT_MESSAGE = ".d"

global client


class Client:
    def __init__(self) -> None:
        self._encryptor = Encryptor()
        self._is_connected = False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_username(self, username) -> None:
        self._username = username.encode(ENCODING)
        self._socket.send(self._username)

    def send_data(self, data) -> None:
        # enc_data = self._encryptor.encrypt(data["data"])
        # data["data"] = enc_data
        data = pickle.dumps(data)
        self._socket.send(data)

    def check_username_validity(self, username) -> None:
        self.send_username(username)
        if (self._socket.recv(8192).decode(ENCODING) == "OK"):
            self._is_connected = True
            run()
        else:
            eel.username_reentry()

    def connect(self, username) -> None:
        self._socket.connect(SERVER_ADDRESS)
        self.check_username_validity(username)
        while (not self._is_connected):
            pass

    def handle_messages(self) -> None:
        while self._is_connected:
            try:
                packet = self._socket.recv(8192)
                if packet:
                    packet = pickle.loads(packet)
                if not packet:
                    print('\r' + "Disconnecting from the server")
                    self._socket.close()
                    eel.close_window()
                    break
                username = packet['username'].decode(ENCODING)
                # dec_message = self._encryptor.decrypt(packet['data'])
                get_message(username, packet['data'])
            except Exception:
                print("Error! Disconnecting from the server")
                self._socket.close()
                eel.close_window()
                break


@eel.expose
def resend_username(username) -> None:
    print("hello bro")
    client.check_username_validity(username)


@eel.expose
def send_message(msg) -> None:
    packet = {
        "type": "message",
        "username": client._username,
        "data": msg
    }
    client.send_data(packet)


@eel.expose
def get_message(usrname, msg) -> None:
    eel.get_recv_msg(usrname, msg)


@eel.expose
def run(username) -> None:
    try:
        client.connect(username)
        eel.close_window()
        client._is_connected = True  # remove later
        thread = threading.Thread(target=client.handle_messages)  # daemon
        thread.start()
        eel.start('chat.html', port=0, size=(1000, 600))
    except Exception:
        print("Server is offline. Try again later")
        eel.get_exception("Server is offline. Try again later")


@eel.expose
def connect(username) -> None:
    thread = threading.Thread(target=client.connect, args=username)
    thread.start()


if __name__ == "__main__":
    client = Client()
    eel.start('index.html', port=0, size=(800, 500))
