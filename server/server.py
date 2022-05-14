import socket
import threading
import sys
import os
import pickle

PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_ADDRESS = (SERVER_IP, PORT)
ENCODING = 'utf-8'
DISCONNECT_MESSAGE = ".d"


class Server:
    def __init__(self) -> None:
        self._clients = {}

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(SERVER_ADDRESS)

    def send_all(self, conn, packet) -> None:
        packet = pickle.dumps(packet)
        for client in self._clients:
            if client != conn:
                client.send(packet)

    def send_disc_msg(self, conn) -> None:
        for client in self._clients:
            if client != conn:
                client.send(f"{self._clients[conn]} has been disconnected")

    def handle_client(self, conn, addr) -> None:
        print(f"[NEW CONNECTION] {addr} connected.")

        is_connected = False
        while (not is_connected):
            username = conn.recv(8192).decode(ENCODING)
            if (username not in self._clients.values()):
                conn.send("OK".encode(ENCODING))
                self._clients[conn] = username
                is_connected = True
            else:
                conn.send("WRONG USERNAME".encode(ENCODING))

        try:
            while is_connected:
                packet = conn.recv(8192)
                if not packet:
                    break
                else:
                    packet = pickle.loads(packet)
                    if packet['data'] == DISCONNECT_MESSAGE:
                        is_connected = False
                    print(f"[{self._clients[conn]}] {packet}")
                    if packet != DISCONNECT_MESSAGE:
                        self.send_all(conn, packet)
                    else:
                        self.send_disc_msg(conn)
        finally:
            print(f"Client {addr} has been disconnected")
            self._clients.pop(conn)
            conn.close()

    def run_server(self) -> None:
        self._socket.listen()
        print(f"[LISTENING] Server is listening on {SERVER_IP}")
        while True:
            conn, addr = self._socket.accept()
            thread = threading.Thread(target=self.handle_client,
                                      args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")

    def server_shutdown(self) -> None:
        self._socket.close()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == "__main__":
    try:
        server = Server()
        server_thread = threading.Thread(target=server.run_server)
        server_thread.start()
        cmd = input()
        while (cmd != "q"):
            print('''Unknown command, use "q" to shut down the server''')
            cmd = input()
        server.server_shutdown()
    except Exception as e:
        print(e)
        server.server_shutdown()
