# server.py
import socket
import threading
import time


class ChatServer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.clients = {}
        self.lock = threading.Lock()

    def start(self):
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        try:
            while True:
                client_socket, address = self.server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket, address)).start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, address):
        username = client_socket.recv(1024).decode('utf-8')

        with self.lock:
            self.clients[username] = client_socket
            self.broadcast(f"{username} has joined the chat!")

        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                with self.lock:
                    self.broadcast(f"{username}: {message}")
        except:
            pass
        finally:
            with self.lock:
                if username in self.clients:
                    del self.clients[username]
                    self.broadcast(f"{username} has left the chat.")
            client_socket.close()

    def broadcast(self, message):
        print(message)
        for client in self.clients.values():
            try:
                client.send(message.encode('utf-8'))
            except:
                pass


if __name__ == "__main__":
    server = ChatServer()
    server.start()
