import socket
import threading
import sys
import os
import shutil
import time
import datetime
import pickle

PORT = 5050
SERVER_IP = socket.gethostbyname('0.0.0.0')
SERVER_ADDRESS = (SERVER_IP, PORT)
ENCODING = 'utf-8'


class Server:
    def __init__(self) -> None:
        file_dir = os.path.join('files')
        if not os.path.exists(file_dir):
            os.mkdir(file_dir)

        self._clients = {}

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(SERVER_ADDRESS)

    def send_all(self, conn, packet) -> None:
        packet = pickle.dumps(packet)
        for client in self._clients:
            if client != conn:
                client.send(packet)

    def send_private_msg(self, packet) -> None:
        msg_sent = False
        for client in self._clients:
            if self._clients[client] == packet['destination']:
                msg_sent = True
                packet = pickle.dumps(packet)
                client.send(packet)
                break
        if msg_sent is False:
            sender_username = packet['username']
            for client in self._clients:
                if self._clients[client] == sender_username:
                    self.send_msg_from_server(client, '''There is no such
                                                 person on the server''')
                    break

    def send_msg_from_server(self, conn, msg) -> None:
        packet = {
            'type': 'private_message',
            'username': 'server',
            'destination': self._clients[conn],
            'data': msg
        }
        packet = pickle.dumps(packet)
        conn.send(packet)

    def send_disc_msg(self, conn) -> None:
        packet = {
            'type': 'message',
            'username': 'server',
            'data': f'''{self._clients[conn]} has been disconnected'''
        }
        packet = pickle.dumps(packet)
        for client in self._clients:
            if client != conn:
                client.send(packet)

    def send_file(self, conn, packet):
        request_packet = {
            'type': 'file_request',
            'file_name': packet['file_name']
        }
        request_packet = pickle.dumps(request_packet)
        conn.sendall(request_packet)
        path = os.path.join('files', packet['file_name'])
        with open(path, "rb") as f:
            while True:
                data = f.read(32000)
                packet = {
                    'type': 'file',
                    'username': self._clients[conn],
                    'file_name': os.path.basename(path),
                    'data': data
                }
                packet = pickle.dumps(packet)
                conn.sendall(packet)
                time.sleep(0.1)
                if data == b'':
                    break
            f.close()

    def recv_file(self, conn, packet) -> None:
        path = os.path.join('files', packet['file_name'])
        with open(path, "wb") as f:
            while True:
                packet = conn.recv(32768)
                if packet:
                    packet = pickle.loads(packet)
                    if packet['data'] == b'':
                        break
                    f.write(packet['data'])
            f.close()
        file_packet = {
            'type': 'file_message',
            'username': self._clients[conn],
            'file_name': f'''{packet['file_name']}'''
        }
        self.send_all(conn, file_packet)

    def handle_client(self, conn, addr) -> None:
        date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        print(f'[{date}] [NEW CONNECTION] {addr} connected.')

        is_connected = False
        while not is_connected:
            username = conn.recv(16384).decode(ENCODING)
            if username not in self._clients.values():
                conn.send('OK'.encode(ENCODING))
                self._clients[conn] = username
                is_connected = True
            else:
                conn.send('WRONG USERNAME'.encode(ENCODING))

        try:
            while is_connected:
                packet = conn.recv(16384)
                if not packet:
                    is_connected = False
                else:
                    packet = pickle.loads(packet)
                    date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
                    print(f'[{date}] [{self._clients[conn]}] {packet}')
                    if packet['type'] == 'message':
                        self.send_all(conn, packet)
                    elif packet['type'] == 'private_message':
                        if packet['destination'] == self._clients[conn]:
                            self.send_msg_from_server(conn, '''You can't send
                                            a private message to yourself''')
                        else:
                            self.send_private_msg(packet)
                    elif packet['type'] == 'request':
                        self.recv_file(conn, packet)
                    elif packet['type'] == 'download_request':
                        self.send_file(conn, packet)
        finally:
            date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
            print(f'[{date}] Client {addr} has been disconnected')
            self.send_disc_msg(conn)
            self._clients.pop(conn)
            conn.close()

    def run_server(self) -> None:
        date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        self._socket.listen()
        print(f'[{date}] [LISTENING] Server is listening on {SERVER_IP}')
        while True:
            conn, addr = self._socket.accept()
            thread = threading.Thread(target=self.handle_client,
                                      args=(conn, addr))
            thread.start()
            date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
            print(f'''[{date}] [ACTIVE CONNECTIONS] {threading.active_count()
                                                                    - 2}''')

    def server_shutdown(self) -> None:
        file_dir = os.path.join('files')
        if os.path.exists(file_dir):
            shutil.rmtree(file_dir, ignore_errors=True)

        self._socket.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == '__main__':
    try:
        server = Server()
        server_thread = threading.Thread(target=server.run_server)
        server_thread.start()
        cmd = input()
        while (cmd != 'q'):
            print('''Unknown command, use 'q' to shut down the server''')
            cmd = input()
        server.server_shutdown()
    except Exception as e:
        date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        print(f'[{date}] {e}')
        server.server_shutdown()
