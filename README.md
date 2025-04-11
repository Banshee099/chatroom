# Setting Up a Chatroom Server with Ubuntu Server and VirtualBox

This guide will walk you through setting up a chatroom server using Ubuntu Server on VirtualBox, and making it accessible over the internet using ngrok.

## Requirements

### Server
- Ubuntu Server (recommended) or other Linux distribution
- Python 3.6+
- Internet connection

### Client
- Windows: Use the provided executable
- Other platforms: Python 3.6+ with required dependencies


## 1. Download and Install VirtualBox

Visit the official VirtualBox download page and download the appropriate version for your operating system:
- [https://www.virtualbox.org/wiki/Downloads](https://www.virtualbox.org/wiki/Downloads)

Install VirtualBox by following the installation wizard for your operating system.

## 2. Download Ubuntu Server

Download the latest Ubuntu Server ISO file:
- [https://ubuntu.com/download/server](https://ubuntu.com/download/server)

Choose the LTS (Long Term Support) version for better stability.

## 3. Install Ubuntu Server on VirtualBox

Follow this process to install Ubuntu Server:

1. Open VirtualBox and create a new virtual machine
2. Allocate appropriate resources (minimum 2GB RAM, 20GB disk space)
3. Mount the downloaded Ubuntu Server ISO file
4. Follow the installation wizard
5. Make sure to install OpenSSH server during installation
6. Complete the installation and reboot the VM

For a detailed visual guide, you can follow this tutorial:
- [https://www.youtube.com/watch?v=ElNalqvVaPw&t=408s](https://www.youtube.com/watch?v=ElNalqvVaPw&t=408s)

### SSH into your server

Once installed, SSH into your server using the following command in your terminal:

```bash
ssh username@server_ip_address
```

Replace `username` with your Ubuntu username and `server_ip_address` with the IP address of your virtual machine.

## 4. Update the System

First, update your system packages:

```bash
sudo apt-get update
```

## 5. Install Git

Install Git on your Ubuntu Server:

```bash
sudo apt-get install -y git
```

## 6. Clone the Chatroom Repository

Clone the chatroom application repository:

```bash
git clone https://github.com/Banshee099/chatroom.git
```

## 7. Navigate to the Project Directory

Change your working directory to the cloned repository:

```bash
cd chatroom
```

## 8. Make the Server Setup Script Executable

Give execution permission to the server setup script:

```bash
sudo chmod +x server_setup.sh
```

## 9. Make the Ngrok Script Executable

Give execution permission to the ngrok setup script:

```bash
sudo chmod +x ngrok.sh
```

## 10. Run the Server Setup Script

Execute the server setup script to install dependencies and configure the chat server:

```bash
sudo ./server_setup.sh
```

This script will set up the Python environment, install dependencies, and create a system service for your chat server.

## 11. Get Ngrok Authentication Token

1. Visit the ngrok dashboard and sign up or log in:
   - [https://dashboard.ngrok.com/get-started/setup/linux](https://dashboard.ngrok.com/get-started/setup/linux)
2. Copy your authentication token from the dashboard
3. Configure ngrok with your token:

```bash
ngrok config add-authtoken TOKEN
```

Replace `TOKEN` with your actual ngrok authentication token.

## 12. Run the Ngrok Script

Execute the ngrok setup script to create a tunnel to your chat server:

```bash
sudo ./ngrok.sh
```

This script will set up ngrok as a system service to expose your chat server to the internet.

## 13. Get the Public URL for Your Server

Retrieve the public URL that ngrok has assigned to your server:

```bash
curl http://localhost:4040/api/tunnels | grep -o "tcp://[^\"]*"
```

This will output something like:
```
tcp://0.tcp.in.ngrok.io:16704
```

Note: Your port number may be different than 16704.

## 14. Run the Chat Client

You have two options for running the client:

### Option 1: Use the Executable (Windows)
Navigate to the `client/dist` folder and run `client.exe`.

### Option 2: Run the Python Client Script
Run the client using Python:

```bash
python client.py
```

## 15. Connect to the Server

Once the client is running, connect to your server using the command:

```
/connect <username> <Public ngrok URL>
```

For example:
```
/connect JohnDoe tcp://0.tcp.in.ngrok.io:16704
```

Your chat client should now connect to your server, and you can start chatting!

## Troubleshooting

- If you can't connect to the server, check that both the chat server and ngrok services are running:
  ```bash
  sudo systemctl status chat.service
  sudo systemctl status ngrok.service
  ```
  
- Make sure your firewall settings allow connections on the required ports.

- If the ngrok URL doesn't work, try restarting the ngrok service:
  ```bash
  sudo systemctl restart ngrok.service
  ```
  
- Check the ngrok logs if you encounter issues:
  ```bash
  sudo journalctl -u ngrok.service
  ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.