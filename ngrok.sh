#!/bin/bash

# Exit on error
set -e

echo "Setting up ngrok service for chat server..."

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "Error: ngrok is not installed or not in PATH"
    echo "Please install ngrok first: https://ngrok.com/download"
    exit 1
fi

# Extract ngrok token from config file
if [ -f ~/.config/ngrok/ngrok.yml ]; then
    NGROK_TOKEN=$(grep authtoken ~/.config/ngrok/ngrok.yml | awk '{print $2}')
    echo "Found ngrok token in config file"
elif [ -f ~/.ngrok2/ngrok.yml ]; then
    NGROK_TOKEN=$(grep authtoken ~/.ngrok2/ngrok.yml | awk '{print $2}')
    echo "Found ngrok token in config file"
else
    echo "Error: Could not find ngrok configuration file"
    echo "Please run 'ngrok config add-authtoken YOUR_TOKEN' first"
    exit 1
fi

# Create systemd service file
echo "Creating systemd service file for ngrok..."
sudo tee /etc/systemd/system/ngrok.service > /dev/null << EOL
[Unit]
Description=ngrok TCP tunnel for chat server
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/usr/local/bin/ngrok tcp 8000
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
# Environment variables for ngrok authentication
Environment="NGROK_AUTHTOKEN=${NGROK_TOKEN}"

[Install]
WantedBy=multi-user.target
EOL

# Check if ngrok is in /usr/local/bin, if not, find its location
if [ ! -f /usr/local/bin/ngrok ]; then
    NGROK_PATH=$(which ngrok)
    if [ -n "$NGROK_PATH" ]; then
        echo "ngrok found at $NGROK_PATH, updating service file..."
        sudo sed -i "s|/usr/local/bin/ngrok|$NGROK_PATH|g" /etc/systemd/system/ngrok.service
    else
        echo "Warning: Could not find ngrok executable. Please update the ExecStart path in the service file manually."
    fi
fi

# Enable and start the service
echo "Enabling and starting ngrok service..."
sudo systemctl daemon-reload
sudo systemctl enable ngrok.service
sudo systemctl start ngrok.service

echo "ngrok service setup complete!"
echo "You can check the status with: sudo systemctl status ngrok.service"
echo "To see the public URL, run: curl http://localhost:4040/api/tunnels"