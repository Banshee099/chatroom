import socket
import threading
import cmd
import sys
import os
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


class ChatClient(cmd.Cmd):
    prompt = '> '
    intro = "Welcome to the Encrypted Python Chat Room! Type 'help' for a list of commands."

    def __init__(self):
        super().__init__()
        self.host = None
        self.port = 8000
        self.socket = None
        self.connected = False
        self.username = None

        # Generate client's key pair
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

        # Server's public key (will be obtained during connection)
        self.server_public_key = None

        # Session key for AES encryption (will be generated during connection)
        self.session_key = None
        self.iv = None

    def encrypt_message(self, message):
        # Use AES for message encryption
        encryptor = Cipher(
            algorithms.AES(self.session_key),
            modes.CFB(self.iv),
            backend=default_backend()
        ).encryptor()

        encrypted_data = encryptor.update(message.encode('utf-8')) + encryptor.finalize()
        return base64.b64encode(encrypted_data).decode('utf-8')

    def decrypt_message(self, encrypted_message):
        # Decrypt using AES
        encrypted_data = base64.b64decode(encrypted_message.encode('utf-8'))
        decryptor = Cipher(
            algorithms.AES(self.session_key),
            modes.CFB(self.iv),
            backend=default_backend()
        ).decryptor()

        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        return decrypted_data.decode('utf-8')

    def default(self, line):
        """Handle direct messages without requiring the 'say' command"""
        if self.connected and line:
            try:
                # Encrypt the message before sending
                encrypted_message = self.encrypt_message(line)
                self.socket.send(encrypted_message.encode('utf-8'))
            except Exception as e:
                print(f"Failed to send message: {e}")
                self.connected = False
        elif not self.connected:
            print("You are not connected. Use '/connect username server_address' first.")
        return False

    def do_connect(self, arg):
        if self.connected:
            print("You are already connected!")
            return

        args = arg.split()
        if len(args) != 2:
            print("Usage: /connect username server_address")
            return

        self.username = args[0]
        server_address = args[1]

        # Handle ngrok TCP URLs
        if "tcp://" in server_address:
            server_address = server_address.replace("tcp://", "")

        # Parse host and port
        if ":" in server_address:
            self.host, port_str = server_address.split(":")
            try:
                self.port = int(port_str)
            except ValueError:
                print("Port must be a number.")
                return
        else:
            self.host = server_address
            self.port = 8000  # Default port

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Attempting to connect to {self.host}:{self.port}...")
            self.socket.connect((self.host, self.port))

            # STEP 1: Receive server's public key
            server_public_key_pem = self.socket.recv(4096)
            self.server_public_key = serialization.load_pem_public_key(
                server_public_key_pem,
                backend=default_backend()
            )

            # STEP 2: Send client's public key to server
            public_key_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            self.socket.send(public_key_pem)

            # STEP 3: Generate and send session key encrypted with server's public key
            self.session_key = os.urandom(32)  # 256-bit key for AES
            self.iv = os.urandom(16)  # Initialization vector

            encrypted_session_key = self.server_public_key.encrypt(
                self.session_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            encrypted_iv = self.server_public_key.encrypt(
                self.iv,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # Send encrypted session key and IV
            self.socket.send(len(encrypted_session_key).to_bytes(4, byteorder='big'))
            self.socket.send(encrypted_session_key)
            self.socket.send(len(encrypted_iv).to_bytes(4, byteorder='big'))
            self.socket.send(encrypted_iv)

            # STEP 4: Send encrypted username
            encrypted_username = self.encrypt_message(self.username)
            self.socket.send(encrypted_username.encode('utf-8'))

            self.connected = True
            threading.Thread(target=self.receive_messages, daemon=True).start()
            print(f"Securely connected to the server as {self.username}")

        except Exception as e:
            print(f"Failed to connect: {e}")

    # Remaining methods similar to original, but with encryption/decryption

    def receive_messages(self):
        while self.connected:
            try:
                encrypted_message = self.socket.recv(2048).decode('utf-8')
                if not encrypted_message:
                    print("Disconnected from server.")
                    self.connected = False
                    break

                # Decrypt the message
                message = self.decrypt_message(encrypted_message)
                print(f"\n{message}\n{self.prompt}", end='')
            except Exception as e:
                print(f"\nLost connection to server: {e}")
                self.connected = False
                break

    # Override to make all commands start with '/'
    def get_names(self):
        return [f'/{n[3:]}' if n.startswith('do_') else n for n in dir(self.__class__) if n.startswith('do_')]

    def completenames(self, text, *ignored):
        dotext = 'do_' + text[1:] if text.startswith('/') else 'do_' + text
        return [f'/{a[3:]}' for a in self.get_names() if a.startswith(dotext)]

    def onecmd(self, line):
        if line.startswith('/'):
            cmd, arg, line = self.parseline(line[1:])  # Remove the slash
            if not line:
                return self.emptyline()
            if cmd is None:
                return self.default(line)
            if cmd == '':
                return self.default(line)
            if cmd == 'EOF':
                return self.default(line)
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                return self.default(line)
            return func(arg)
        else:
            return self.default(line)


if __name__ == "__main__":
    client = ChatClient()
    try:
        client.cmdloop()
    except KeyboardInterrupt:
        print("\nExiting chat client.")
        if client.connected:
            client.socket.close()