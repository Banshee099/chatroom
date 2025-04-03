import socket
import threading
import cmd
import sys


class ChatClient(cmd.Cmd):
    prompt = '> '
    intro = "Welcome to the Python Chat Room! Type 'help' for a list of commands."

    def __init__(self, host='192.168.1.4', port=8000):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.username = None

    def do_connect(self, arg):
        """Connect to the chat server: connect username"""
        if self.connected:
            print("You are already connected!")
            return

        args = arg.split()
        if len(args) != 1:
            print("Usage: connect username")
            return

        self.username = args[0]
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.socket.send(self.username.encode('utf-8'))
            self.connected = True

            # Start a thread to receive messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            print(f"Connected to the server as {self.username}")
        except Exception as e:
            print(f"Failed to connect: {e}")

    def do_say(self, arg):
        """Send a message to the chat room: say message"""
        if not self.connected:
            print("You are not connected. Use 'connect username' first.")
            return

        if not arg:
            print("Usage: say message")
            return

        try:
            self.socket.send(arg.encode('utf-8'))
        except:
            print("Failed to send message. You might be disconnected.")
            self.connected = False

    def do_quit(self, arg):
        """Exit the chat client"""
        if self.connected:
            try:
                self.socket.close()
            except:
                pass
        print("Goodbye!")
        return True

    def receive_messages(self):
        while self.connected:
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if not message:
                    print("Disconnected from server.")
                    self.connected = False
                    break
                print(f"\n{message}\n{self.prompt}", end='')
            except:
                print("\nLost connection to server.")
                self.connected = False
                break


if __name__ == "__main__":
    ChatClient().cmdloop()