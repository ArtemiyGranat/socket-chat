import socket
import threading
import eel 

eel.init('web')

PORT = 5050
SERVER_IP = "192.168.1.11"
SERVER_ADDRESS = (SERVER_IP, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = ".d"


def handle_messages(connection):
    while True:
        try:
            msg = connection.recv(1024)
            if not msg:
                connection.close()
                break
            print('\r' + msg.decode(FORMAT))
            print("[YOU] ", end="", flush=True)
        except Exception as e:
            print("ERROR!")
            connection.close()
            break


def send(client, msg):
    message = msg.encode(FORMAT)
    client.send(message)

@eel.expose
def start():
    eel.start('chat.html', port=PORT)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(SERVER_ADDRESS)
    thread = threading.Thread(target=handle_messages, args=[client_socket])
    thread.start()
    connected = True
    while connected:
        print("[YOU] ", end="")
        msg = input()
        if (msg == DISCONNECT_MESSAGE):
            connected = False
        send(client_socket, msg)
    send(client_socket, DISCONNECT_MESSAGE)


# username = input("Enter your username: ")
if __name__ == "__main__":
    eel.start('index.html', mode='chrome', size=(1000, 600))
    start()