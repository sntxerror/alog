#!/bin/bash

# install.sh - Alog Installation Script
# This script handles the complete installation and setup of the Alog application

# Exit on any error
set -e

# Text formatting
BOLD='\033[1m'
NORMAL='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'

# Helper function to print status messages
print_status() {
    echo -e "${BOLD}${GREEN}==>${NORMAL} ${1}"
}

print_warning() {
    echo -e "${BOLD}${YELLOW}Warning:${NORMAL} ${1}"
}

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script as root or with sudo"
    exit 1
fi

# Store the actual user who ran sudo
ACTUAL_USER=${SUDO_USER:-${USER}}
USER_HOME=$(getent passwd ${ACTUAL_USER} | cut -d: -f6)

print_status "Starting Alog installation..."

# Update package lists
print_status "Updating package lists..."
apt-get update

# Install system dependencies
print_status "Installing system dependencies..."
apt-get install -y \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    console-setup \
    console-data \
    terminus-font

# Create application directory
APP_DIR="${USER_HOME}/alog"
if [ ! -d "$APP_DIR" ]; then
    print_status "Creating application directory..."
    mkdir -p "$APP_DIR"
    chown ${ACTUAL_USER}:${ACTUAL_USER} "$APP_DIR"
fi

# Set up Python virtual environment
print_status "Setting up Python virtual environment..."
su - ${ACTUAL_USER} -c "python3 -m venv ${APP_DIR}/venv"

# Install Python requirements
print_status "Installing Python dependencies..."
su - ${ACTUAL_USER} -c "${APP_DIR}/venv/bin/pip install -r ${APP_DIR}/backend/requirements.txt"

# Install frontend dependencies and build
print_status "Setting up frontend..."
cd "${APP_DIR}/frontend"
su - ${ACTUAL_USER} -c "cd ${APP_DIR}/frontend && npm install"
su - ${ACTUAL_USER} -c "cd ${APP_DIR}/frontend && npm run build"

# Set up systemd service
print_status "Setting up systemd service..."
cat > /etc/systemd/system/alog.service << EOF
[Unit]
Description=Alog AI-Powered Wearable Device Service
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=${ACTUAL_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="PYTHONPATH=${APP_DIR}"
Environment="PYTHONUNBUFFERED=1"
Environment="FORCE_COLOR=1"
Environment="ENABLED_LOG_LEVELS=EVENT,SPEECH,ERROR"
ExecStartPre=${APP_DIR}/venv/bin/python -m pip install -r ${APP_DIR}/backend/requirements.txt
ExecStart=${APP_DIR}/venv/bin/python ${APP_DIR}/backend/app.py
Restart=always
RestartSec=1
StandardOutput=journal+console
StandardError=journal+console

[Install]
WantedBy=multi-user.target
EOF

# Set up automatic login and log viewing
print_status "Setting up automatic login and log viewing..."
mkdir -p /etc/systemd/system/getty@tty1.service.d/
cat > /etc/systemd/system/getty@tty1.service.d/override.conf << EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin ${ACTUAL_USER} --noclear %I \$TERM
Type=idle
EOF

# Configure .profile for automatic log viewing
cat >> "${USER_HOME}/.profile" << EOF

# Auto-start journal following if we're on tty1
if [[ "\$(tty)" == "/dev/tty1" ]]; then
    clear
    # Export color support
    export TERM=xterm-256color
    # Follow logs with clean formatting
    exec journalctl -n 0 -f -u alog.service --no-hostname --output=cat
fi
EOF

# Set appropriate permissions
chown ${ACTUAL_USER}:${ACTUAL_USER} "${USER_HOME}/.profile"

# Configure console font
print_status "Configuring console font..."
cat > /etc/default/console-setup << EOF
ACTIVE_CONSOLES="/dev/tty[1-6]"
CHARMAP="UTF-8"
CODESET="Lat15"
FONTFACE="Terminus"
FONTSIZE="12x24"
EOF

# Update console setup
dpkg-reconfigure -f noninteractive console-setup

# Enable and start the service
print_status "Enabling and starting Alog service..."
systemctl daemon-reload
systemctl enable alog.service
systemctl start alog.service

print_status "Installation complete!"
echo -e "\nYou can now:"
echo "1. View logs directly on TTY1 (HDMI display)"
echo "2. View logs via SSH using: journalctl -f -u alog.service --no-hostname --output=cat"
echo "3. Access the web interface at: http://localhost:5000"