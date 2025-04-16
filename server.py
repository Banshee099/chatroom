import socket
import threading
import time
import argparse
import requests
import json
import sys
import base64
import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class ChatServer:
    def __init__(self, host='0.0.0.0', port=8000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.clients = {}  # Maps usernames to (socket, encryption_info) tuples
        self.lock = threading.Lock()
        self.ngrok_url = None

        # Generate server's key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()
        self.public_key_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def start(self):
        self.server_socket.listen(5)
        print(f"Encrypted server started on {self.host}:{self.port}")
        print(f"Local IP: {self.get_local_ip()}")

        # Check for ngrok tunnel
        self.ngrok_url = self.get_ngrok_url()
        if self.ngrok_url:
            print(f"ngrok tunnel established: {self.ngrok_url}")
            print(f"For clients to connect, use: connect username {self.ngrok_url.split('//')[1]}")

        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"New connection from {address[0]}:{address[1]}")
                threading.Thread(target=self.handle_client, args=(client_socket, address)).start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server_socket.close()

    def encrypt_message(self, message, session_key, iv):
        encryptor = Cipher(
            algorithms.AES(session_key),
            modes.CFB(iv),
            backend=default_backend()
        ).encryptor()

        encrypted_data = encryptor.update(message.encode('utf-8')) + encryptor.finalize()
        return base64.b64encode(encrypted_data).decode('utf-8')

    def decrypt_message(self, encrypted_message, session_key, iv):
        encrypted_data = base64.b64decode(encrypted_message.encode('utf-8'))
        decryptor = Cipher(
            algorithms.AES(session_key),
            modes.CFB(iv),
            backend=default_backend()
        ).decryptor()

        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return decrypted_data.decode('utf-8')

    def handle_client(self, client_socket, address):
        username = None
        client_public_key = None
        session_key = None
        iv = None

        try:
            # STEP 1: Send server's public key with proper framing
            public_key_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            client_socket.send(len(public_key_pem).to_bytes(4, byteorder='big'))
            client_socket.send(public_key_pem)

            # STEP 2: Receive client's public key with proper framing
            key_size_bytes = client_socket.recv(4)
            key_size = int.from_bytes(key_size_bytes, byteorder='big')

            client_public_key_pem = b''
            remaining = key_size
            while remaining > 0:
                chunk = client_socket.recv(min(remaining, 4096))
                if not chunk:
                    raise ConnectionError("Connection closed during key exchange")
                client_public_key_pem += chunk
                remaining -= len(chunk)

            # Load the client's public key
            try:
                client_public_key = serialization.load_pem_public_key(
                    client_public_key_pem,
                    backend=default_backend()
                )
            except Exception as e:
                print(f"Failed to load client's public key: {e}")
                print(f"Received data: {client_public_key_pem[:100]}...")
                raise

            # STEP 3: Receive encrypted session key with proper framing
            key_size_bytes = client_socket.recv(4)
            key_size = int.from_bytes(key_size_bytes, byteorder='big')

            encrypted_session_key = b''
            remaining = key_size
            while remaining > 0:
                chunk = client_socket.recv(min(remaining, 4096))
                if not chunk:
                    raise ConnectionError("Connection closed during key exchange")
                encrypted_session_key += chunk
                remaining -= len(chunk)

            # Receive encrypted IV
            iv_size_bytes = client_socket.recv(4)
            iv_size = int.from_bytes(iv_size_bytes, byteorder='big')

            encrypted_iv = b''
            remaining = iv_size
            while remaining > 0:
                chunk = client_socket.recv(min(remaining, 4096))
                if not chunk:
                    raise ConnectionError("Connection closed during key exchange")
                encrypted_iv += chunk
                remaining -= len(chunk)

            # Decrypt session key and IV with server's private key
            try:
                session_key = self.private_key.decrypt(
                    encrypted_session_key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

                iv = self.private_key.decrypt(
                    encrypted_iv,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
            except Exception as e:
                print(f"Failed to decrypt session key/IV: {e}")
                raise

            # STEP 4: Receive encrypted username with proper framing
            username_size_bytes = client_socket.recv(4)
            username_size = int.from_bytes(username_size_bytes, byteorder='big')

            encrypted_username_bytes = b''
            remaining = username_size
            while remaining > 0:
                chunk = client_socket.recv(min(remaining, 4096))
                if not chunk:
                    raise ConnectionError("Connection closed during username exchange")
                encrypted_username_bytes += chunk
                remaining -= len(chunk)

            encrypted_username = encrypted_username_bytes.decode('utf-8')
            username = self.decrypt_message(encrypted_username, session_key, iv)

            print(f"User {username} connected from {address[0]}:{address[1]} (encrypted)")

            # Store client info
            encryption_info = {
                'public_key': client_public_key,
                'session_key': session_key,
                'iv': iv
            }

            with self.lock:
                self.clients[username] = (client_socket, encryption_info)
                self.broadcast(f"{username} has joined the chat!")

            # Also need to modify the message receiving loop to use proper framing
            while True:
                # Receive message size
                size_bytes = client_socket.recv(4)
                if not size_bytes:
                    break

                msg_size = int.from_bytes(size_bytes, byteorder='big')

                # Receive full message
                encrypted_message_bytes = b''
                remaining = msg_size
                while remaining > 0:
                    chunk = client_socket.recv(min(remaining, 4096))
                    if not chunk:
                        raise ConnectionError("Connection closed during message reception")
                    encrypted_message_bytes += chunk
                    remaining -= len(chunk)

                encrypted_message = encrypted_message_bytes.decode('utf-8')
                message = self.decrypt_message(encrypted_message, session_key, iv)

                with self.lock:
                    self.broadcast(f"{username}: {message}")

        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            with self.lock:
                if username and username in self.clients:
                    del self.clients[username]
                    self.broadcast(f"{username} has left the chat.")
            client_socket.close()
            print(f"Connection closed for {address[0]}:{address[1]}")
    def broadcast(self, message):
        print(message)
        disconnected_clients = []

        for uname, (client, encryption_info) in self.clients.items():
            try:
                # Encrypt message specifically for this client
                encrypted_msg = self.encrypt_message(
                    message,
                    encryption_info['session_key'],
                    encryption_info['iv']
                )
                client.send(encrypted_msg.encode('utf-8'))
            except:
                disconnected_clients.append(uname)

        # Remove disconnected clients
        for uname in disconnected_clients:
            if uname in self.clients:
                del self.clients[uname]
                print(f"Removed disconnected client: {uname}")

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

    def get_ngrok_url(self):
        """Get ngrok public URL if running"""
        try:
            # Try to get the ngrok tunnel info from the API
            response = requests.get('http://localhost:4040/api/tunnels')
            if response.status_code == 200:
                data = response.json()
                for tunnel in data['tunnels']:
                    if tunnel['proto'] == 'tcp':
                        return tunnel['public_url']
            return None
        except:
            return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat Server with ngrok support")
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    args = parser.parse_args()

    server = ChatServer(port=args.port)
    server.start()