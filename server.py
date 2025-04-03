# # server.py
# import socket
# import threading
# import time
#
#
# class ChatServer:
#     def __init__(self, host='127.0.0.1', port=8000):
#         self.host = host
#         self.port = port
#         self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         self.server_socket.bind((self.host, self.port))
#         self.clients = {}
#         self.lock = threading.Lock()
#
#     def start(self):
#         self.server_socket.listen(5)
#         print(f"Server started on {self.host}:{self.port}")
#
#         try:
#             while True:
#                 client_socket, address = self.server_socket.accept()
#                 threading.Thread(target=self.handle_client, args=(client_socket, address)).start()
#         except KeyboardInterrupt:
#             print("Server shutting down...")
#         finally:
#             self.server_socket.close()
#
#     def handle_client(self, client_socket, address):
#         username = client_socket.recv(1024).decode('utf-8')
#
#         with self.lock:
#             self.clients[username] = client_socket
#             self.broadcast(f"{username} has joined the chat!")
#
#         try:
#             while True:
#                 message = client_socket.recv(1024).decode('utf-8')
#                 if not message:
#                     break
#
#                 with self.lock:
#                     self.broadcast(f"{username}: {message}")
#         except:
#             pass
#         finally:
#             with self.lock:
#                 if username in self.clients:
#                     del self.clients[username]
#                     self.broadcast(f"{username} has left the chat.")
#             client_socket.close()
#
#     def broadcast(self, message):
#         print(message)
#         for client in self.clients.values():
#             try:
#                 client.send(message.encode('utf-8'))
#             except:
#                 pass
#
#
# if __name__ == "__main__":
#     server = ChatServer()
#     server.start()
import socket
import threading
import time
import argparse


class ChatServer:
    def __init__(self, host='0.0.0.0', port=8000):
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
        print(f"Local IP: {self.get_local_ip()}")

        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"New connection from {address[0]}:{address[1]}")
                threading.Thread(target=self.handle_client, args=(client_socket, address)).start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, address):
        try:
            username = client_socket.recv(1024).decode('utf-8')
            print(f"User {username} connected from {address[0]}:{address[1]}")

            with self.lock:
                self.clients[username] = client_socket
                self.broadcast(f"{username} has joined the chat!")

            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break

                with self.lock:
                    self.broadcast(f"{username}: {message}")
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            with self.lock:
                if username in self.clients:
                    del self.clients[username]
                    self.broadcast(f"{username} has left the chat.")
            client_socket.close()
            print(f"Connection closed for {address[0]}:{address[1]}")

    def broadcast(self, message):
        print(message)
        disconnected_clients = []

        for username, client in self.clients.items():
            try:
                client.send(message.encode('utf-8'))
            except:
                disconnected_clients.append(username)

        # Remove disconnected clients
        for username in disconnected_clients:
            if username in self.clients:
                del self.clients[username]
                print(f"Removed disconnected client: {username}")

    def get_local_ip(self):
        """Get the local IP address of the server"""
        try:
            # Create a socket to determine the outgoing IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Doesn't need to be reachable
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "Could not determine IP"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat Server")
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    args = parser.parse_args()

    server = ChatServer(port=args.port)
    server.start()