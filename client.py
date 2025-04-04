# import socket
# import threading
# import cmd
# import sys
#
#
# class ChatClient(cmd.Cmd):
#     prompt = '> '
#     intro = "Welcome to the Python Chat Room! Type 'help' for a list of commands."
#
#     def __init__(self, host='192.168.1.4', port=8000):
#         super().__init__()
#         self.host = host
#         self.port = port
#         self.socket = None
#         self.connected = False
#         self.username = None
#
#     def do_connect(self, arg):
#         """Connect to the chat server: connect username"""
#         if self.connected:
#             print("You are already connected!")
#             return
#
#         args = arg.split()
#         if len(args) != 1:
#             print("Usage: connect username")
#             return
#
#         self.username = args[0]
#         try:
#             self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             self.socket.connect((self.host, self.port))
#             self.socket.send(self.username.encode('utf-8'))
#             self.connected = True
#
#             # Start a thread to receive messages
#             threading.Thread(target=self.receive_messages, daemon=True).start()
#             print(f"Connected to the server as {self.username}")
#         except Exception as e:
#             print(f"Failed to connect: {e}")
#
#     def do_say(self, arg):
#         """Send a message to the chat room: say message"""
#         if not self.connected:
#             print("You are not connected. Use 'connect username' first.")
#             return
#
#         if not arg:
#             print("Usage: say message")
#             return
#
#         try:
#             self.socket.send(arg.encode('utf-8'))
#         except:
#             print("Failed to send message. You might be disconnected.")
#             self.connected = False
#
#     def do_quit(self, arg):
#         """Exit the chat client"""
#         if self.connected:
#             try:
#                 self.socket.close()
#             except:
#                 pass
#         print("Goodbye!")
#         return True
#
#     def receive_messages(self):
#         while self.connected:
#             try:
#                 message = self.socket.recv(1024).decode('utf-8')
#                 if not message:
#                     print("Disconnected from server.")
#                     self.connected = False
#                     break
#                 print(f"\n{message}\n{self.prompt}", end='')
#             except:
#                 print("\nLost connection to server.")
#                 self.connected = False
#                 break
#
#
# if __name__ == "__main__":
#     ChatClient().cmdloop()


# import socket
# import threading
# import cmd
# import sys
#
#
# class ChatClient(cmd.Cmd):
#     prompt = '> '
#     intro = "Welcome to the Python Chat Room! Type 'help' for a list of commands."
#
#     def __init__(self):
#         super().__init__()
#         self.host = None
#         self.port = 8000
#         self.socket = None
#         self.connected = False
#         self.username = None
#
#     def do_connect(self, arg):
#         """Connect to the chat server: connect username server_ip [port]"""
#         if self.connected:
#             print("You are already connected!")
#             return
#
#         args = arg.split()
#         if len(args) < 2 or len(args) > 3:
#             print("Usage: connect username server_ip [port]")
#             return
#
#         self.username = args[0]
#         self.host = args[1]
#
#         if len(args) == 3:
#             try:
#                 self.port = int(args[2])
#             except ValueError:
#                 print("Port must be a number.")
#                 return
#
#         try:
#             self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             print(f"Attempting to connect to {self.host}:{self.port}...")
#             self.socket.connect((self.host, self.port))
#             self.socket.send(self.username.encode('utf-8'))
#             self.connected = True
#
#             # Start a thread to receive messages
#             threading.Thread(target=self.receive_messages, daemon=True).start()
#             print(f"Connected to the server at {self.host}:{self.port} as {self.username}")
#         except Exception as e:
#             print(f"Failed to connect: {e}")
#
#     def do_say(self, arg):
#         """Send a message to the chat room: say message"""
#         if not self.connected:
#             print("You are not connected. Use 'connect username server_ip [port]' first.")
#             return
#
#         if not arg:
#             print("Usage: say message")
#             return
#
#         try:
#             self.socket.send(arg.encode('utf-8'))
#         except:
#             print("Failed to send message. You might be disconnected.")
#             self.connected = False
#
#     def do_quit(self, arg):
#         """Exit the chat client"""
#         if self.connected:
#             try:
#                 self.socket.close()
#             except:
#                 pass
#         print("Goodbye!")
#         return True
#
#     def receive_messages(self):
#         while self.connected:
#             try:
#                 message = self.socket.recv(1024).decode('utf-8')
#                 if not message:
#                     print("Disconnected from server.")
#                     self.connected = False
#                     break
#                 print(f"\n{message}\n{self.prompt}", end='')
#             except:
#                 print("\nLost connection to server.")
#                 self.connected = False
#                 break
#
#
# if __name__ == "__main__":
#     ChatClient().cmdloop()


# import socket
# import threading
# import cmd
# import sys
# import re
#
#
# class ChatClient(cmd.Cmd):
#     prompt = '> '
#     intro = "Welcome to the Python Chat Room! Type 'help' for a list of commands."
#
#     def __init__(self):
#         super().__init__()
#         self.host = None
#         self.port = 8000
#         self.socket = None
#         self.connected = False
#         self.username = None
#
#     def do_connect(self, arg):
#         """Connect to the chat server: connect username server_address
#         server_address can be:
#         - IP:port (e.g. 192.168.1.10:8000)
#         - hostname:port (e.g. 0.tcp.ngrok.io:12345)
#         - Just IP or hostname (will use default port 8000)"""
#         if self.connected:
#             print("You are already connected!")
#             return
#
#         args = arg.split()
#         if len(args) != 2:
#             print("Usage: connect username server_address")
#             print("server_address examples: 192.168.1.10:8000, 0.tcp.ngrok.io:12345")
#             return
#
#         self.username = args[0]
#         server_address = args[1]
#
#         # Handle ngrok TCP URLs
#         if "tcp://" in server_address:
#             server_address = server_address.replace("tcp://", "")
#
#         # Parse host and port
#         if ":" in server_address:
#             self.host, port_str = server_address.split(":")
#             try:
#                 self.port = int(port_str)
#             except ValueError:
#                 print("Port must be a number.")
#                 return
#         else:
#             self.host = server_address
#             self.port = 8000  # Default port
#
#         try:
#             self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             print(f"Attempting to connect to {self.host}:{self.port}...")
#             self.socket.connect((self.host, self.port))
#             self.socket.send(self.username.encode('utf-8'))
#             self.connected = True
#
#             # Start a thread to receive messages
#             threading.Thread(target=self.receive_messages, daemon=True).start()
#             print(f"Connected to the server at {self.host}:{self.port} as {self.username}")
#         except Exception as e:
#             print(f"Failed to connect: {e}")
#
#     def do_say(self, arg):
#         """Send a message to the chat room: say message"""
#         if not self.connected:
#             print("You are not connected. Use 'connect username server_address' first.")
#             return
#
#         if not arg:
#             print("Usage: say message")
#             return
#
#         try:
#             self.socket.send(arg.encode('utf-8'))
#         except:
#             print("Failed to send message. You might be disconnected.")
#             self.connected = False
#
#     def do_quit(self, arg):
#         """Exit the chat client"""
#         if self.connected:
#             try:
#                 self.socket.close()
#             except:
#                 pass
#         print("Goodbye!")
#         return True
#
#     def receive_messages(self):
#         while self.connected:
#             try:
#                 message = self.socket.recv(1024).decode('utf-8')
#                 if not message:
#                     print("Disconnected from server.")
#                     self.connected = False
#                     break
#                 print(f"\n{message}\n{self.prompt}", end='')
#             except:
#                 print("\nLost connection to server.")
#                 self.connected = False
#                 break
#
#
# if __name__ == "__main__":
#     ChatClient().cmdloop()


import socket
import threading
import cmd
import sys
import os


class ChatClient(cmd.Cmd):
    prompt = '> '
    intro = "Welcome to the Python Chat Room! Type 'help' for a list of commands.\nType messages directly to send them or use commands with '/'."

    def __init__(self):
        super().__init__()
        self.host = None
        self.port = 8000
        self.socket = None
        self.connected = False
        self.username = None

    def default(self, line):
        """Handle direct messages without requiring the 'say' command"""
        if self.connected and line:
            # Send the message directly
            try:
                self.socket.send(line.encode('utf-8'))
            except:
                print("Failed to send message. You might be disconnected.")
                self.connected = False
        elif not self.connected:
            print("You are not connected. Use '/connect username server_address' first.")
        return False  # Don't exit

    def do_connect(self, arg):
        """Connect to the chat server: /connect username server_address
        server_address can be:
        - IP:port (e.g. 192.168.1.10:8000)
        - hostname:port (e.g. 0.tcp.ngrok.io:12345)
        - Just IP or hostname (will use default port 8000)"""
        if self.connected:
            print("You are already connected!")
            return

        args = arg.split()
        if len(args) != 2:
            print("Usage: /connect username server_address")
            print("server_address examples: 192.168.1.10:8000, 0.tcp.ngrok.io:12345")
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
            self.socket.send(self.username.encode('utf-8'))
            self.connected = True

            # Start a thread to receive messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
            print(f"Connected to the server at {self.host}:{self.port} as {self.username}")
            print("Start typing messages directly - no need to use 'say' command")
        except Exception as e:
            print(f"Failed to connect: {e}")

    def do_quit(self, arg):
        """Exit the chat client: /quit"""
        if self.connected:
            try:
                self.socket.close()
            except:
                pass
        print("Goodbye!")
        return True

    def do_who(self, arg):
        """See who is online (if server supports it): /who"""
        if not self.connected:
            print("You are not connected. Use '/connect username server_address' first.")
            return

        try:
            self.socket.send("/who".encode('utf-8'))
        except:
            print("Failed to send command. You might be disconnected.")
            self.connected = False

    def do_clear(self, arg):
        """Clear the screen: /clear"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def emptyline(self):
        """Do nothing on empty line"""
        pass

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

    # Override to make all commands start with '/'
    def get_names(self):
        return [f'/{n[3:]}' if n.startswith('do_') else n for n in dir(self.__class__) if n.startswith('do_')]

    def completenames(self, text, *ignored):
        dotext = 'do_' + text[1:] if text.startswith('/') else 'do_' + text
        return [f'/{a[3:]}' for a in self.get_names() if a.startswith(dotext)]

    def onecmd(self, line):
        """Interpret the argument as though it had been typed in response
        to the prompt.

        This may be overridden, but should not normally need to be;
        see the precmd() and postcmd() methods for useful execution hooks.
        The return value is a flag indicating whether interpretation of
        commands by the interpreter should stop.

        """
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