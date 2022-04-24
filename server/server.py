import socket
import threading

PORT = 5050
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_ADDRESS = (SERVER_IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = ".d"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDRESS)

clients = set()
clients_lock = threading.Lock()


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    try:
        connected = True
        while connected:
            message = conn.recv(1024).decode(FORMAT)
            if not message:
                break
            if message == DISCONNECT_MESSAGE:
                connected = False
            print(f"[{addr}] {message}")
            with clients_lock:
                for client in clients:
                    if client != conn:
                        client.send(f"[{addr}] {message}".encode(FORMAT))
    finally:
        with clients_lock:
            clients.remove(conn)
        conn.close()


def start():
    server_socket.listen()
    print(f"[LISTENING] Server is listening on {SERVER_IP}")
    while True:
        conn, addr = server_socket.accept()
        with clients_lock:
            clients.add(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    print("[STARTING] Server is starting")
    start()