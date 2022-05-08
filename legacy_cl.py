import socket
import threading
import os
import sys
import pickle

import eel

from encryptor import Encryptor

eel.init('gui')

PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_ADDRESS = (SERVER_IP, PORT)
ENCODING = 'utf-8'
DISCONNECT_MESSAGE = ".d"


class Client:
    def __init__(self) -> None:
        self._encryptor = Encryptor()
        self._is_connected = False
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_username(self, username) -> None:
        self._username = username.encode(ENCODING)
        # self._socket.send(self._username)

    def send_data(self, data) -> None:
        enc_data = self._encryptor.encrypt(data["data"])
        data["data"] = enc_data
        data = pickle.dumps(data)
        self._socket.send(data)

    def connect(self, username) -> None:
        self._socket.connect(SERVER_ADDRESS)
        self.send_username(username)

    def handle_messages(self) -> None:
        while True:
            try:
                packet = self._socket.recv(8192)
                # packet = packet.decode(ENCODING)
                if packet:
                    packet = pickle.loads(packet)
                    print(packet)
                if not packet:
                    print('\r' + "Disconnecting from the server")
                    self._socket.close()
                    try:
                        sys.exit(0)
                    except SystemExit:
                        os._exit(0)
                username = packet['username'].decode(ENCODING)
                # TODO: Фикс бага с тремя+ клиентами
                message = packet['data']
                dec_message = self._encryptor.decrypt(message)
                print(f"\r[{username}] {dec_message}")
                print("[YOU] ", end="", flush=True)
            except Exception as e:
                print("")
                print(e)
                print("Error! Disconnecting from the server")
                self._socket.close()
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)


def run():
    client = Client()
    # username = input("Enter your username: ")
    try:
        client.connect("artemiy")
        client._is_connected = True
        thread = threading.Thread(target=client.handle_messages)
        thread.start()
        while client._is_connected:
            print("[YOU] ", end="")
            msg = input()
            if not msg:
                continue
            if (msg == "q"):
                try:
                    sys.exit(0)
                except SystemExit:
                    os._exit(0)
            if (msg == DISCONNECT_MESSAGE):
                client._is_connected = False
            packet = {
                "type": "file",
                "filename": "file.txt",
                "username": client._username,
                "data": msg
                }
            client.send_data(packet)
    except Exception as e:
        print("Server is offline. Try again later")
        print(e)


if __name__ == "__main__":
    # eel.start('index.html', mode='chrome', size=(1000, 600))
    run()
