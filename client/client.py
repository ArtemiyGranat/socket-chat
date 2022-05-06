import socket
import threading
import os
import sys

import eel

from encryptor import Encryptor

eel.init('gui')

PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_ADDRESS = (SERVER_IP, PORT)
ENCODING = "utf-8"
DISCONNECT_MESSAGE = ".d"


class Client:
    def __init__(self) -> None:
        self._encryptor = Encryptor()
        self._is_connected = False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_username(self, usrname) -> None:
        username = usrname.encode(ENCODING)
        self._socket.send(username)

    def send_data(self, msg) -> None:
        message = self._encryptor.encrypt(msg)
        message = message.encode(ENCODING)
        self._socket.send(message)

    def connect(self, username) -> None:
        self._socket.connect(SERVER_ADDRESS)
        self.send_username(username)

    def handle_messages(self) -> None:
        while True:
            try:
                msg = self._socket.recv(8192)
                if not msg:
                    print('\r' + "Disconnecting from the server")
                    self._socket.close()
                    try:
                        sys.exit(0)
                    except SystemExit:
                        os._exit(0)
                msg = self._encryptor.decrypt(msg)
                print('\r' + msg.decode(ENCODING))
                print("[YOU] ", end="", flush=True)
            # TODO: Проверить, как будет работать без этого
            except Exception:
                print("Error! Disconnecting from the server")
                self._socket.close()
                break


def run():
    client = Client()
    try:
        # TODO: "artemiy" -> username
        client.connect("artemiy")
    except Exception as e:
        print("Server is offline. Try again later")
        print(e)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    client._is_connected = True
    thread = threading.Thread(target=client.handle_messages)
    thread.start()
    while client._is_connected:
        print("[YOU] ", end="")
        msg = input()
        if (msg == DISCONNECT_MESSAGE):
            client._is_connected = False
        client.send_data(msg)


if __name__ == "__main__":
    # eel.start('index.html', mode='chrome', size=(1000, 600))
    run()
