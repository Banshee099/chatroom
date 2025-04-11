#!/bin/bash

# Exit on error
set -e

echo "Starting setup process for Chatroom application..."

# Install ngrok
echo "Installing ngrok..."
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc \
  | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null \
  && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" \
  | sudo tee /etc/apt/sources.list.d/ngrok.list \
  && sudo apt update \
  && sudo apt install ngrok

# Install Python virtual environment
echo "Installing Python virtual environment..."
sudo apt-get install -y python3-venv

# Install net-tools
echo "Installing net-tools..."
sudo apt-get install -y net-tools

# Create and activate virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create systemd service file
echo "Creating systemd service file..."
sudo tee /etc/systemd/system/chat.service > /dev/null << EOL
[Unit]
Description=Python server daemon
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER/chatroom
ExecStart=/home/$USER/chatroom/.venv/bin/python /home/$USER/chatroom/server.py --port 8000

[Install]
WantedBy=multi-user.target
EOL

# Enable and start the service
echo "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable chat.service
sudo systemctl start chat.service

echo "Setup complete! The chatroom server should now be running on port 8000."
echo "You can check the status with: sudo systemctl status chat.service"