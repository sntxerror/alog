# Alog - AI-Powered Wearable Device

Alog is an AI-powered wearable device application that processes audio input using machine learning models to detect and classify sounds and speech in real-time.

## Quick Start

To get started with Alog, follow these simple steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/alog.git
   cd alog
   ```

2. Run the installation script:
   ```bash
   sudo ./install.sh
   ```

The installation script will:
- Install all necessary system dependencies
- Set up Python virtual environment
- Install Python packages
- Build the frontend
- Configure automatic login and log viewing
- Set up and start the system service

## Accessing Logs

There are three ways to view the application logs:

1. **Direct Display (HDMI)**: 
   - Connect a display via HDMI
   - The logs will automatically appear on TTY1 after boot
   - No login required - the system automatically logs in and shows logs

2. **SSH Access**:
   ```bash
   ssh khadas@your-device-ip
   journalctl -f -u alog.service --no-hostname --output=cat
   ```

3. **Log File**:
   ```bash
   tail -f /home/khadas/alog/logs/app.log
   ```

## Web Interface

Access the web interface at `http://your-device-ip:5000`

## Configuration

### Log Levels

By default, the application shows EVENT, SPEECH, and ERROR level logs. To modify this:

1. Edit the service configuration:
   ```bash
   sudo nano /etc/systemd/system/alog.service
   ```

2. Modify the ENABLED_LOG_LEVELS environment variable:
   ```ini
   Environment="ENABLED_LOG_LEVELS=EVENT,SPEECH,ERROR,DEBUG"
   ```

3. Restart the service:
   ```bash
   sudo systemctl restart alog.service
   ```

Available log levels: DEBUG, INFO, EVENT, SPEECH, WARNING, ERROR, CRITICAL

## Development

### Project Structure

```
alog/
├── audio_chunks/       # Stored audio segments
├── backend/           # Python backend
│   ├── api/          # REST API endpoints
│   ├── models/       # Data models
│   └── services/     # Core services
├── frontend/         # React frontend
│   └── src/         # Frontend source code
└── models/          # ML models
    ├── vosk/        # Speech recognition
    └── yamnet/      # Sound classification
```

### Running in Development Mode

For development, you can run the application manually:

1. Start the backend:
   ```bash
   source venv/bin/activate
   python backend/app.py
   ```

2. Start the frontend (in a separate terminal):
   ```bash
   cd frontend
   npm start
   ```

## Troubleshooting

1. **No logs appearing on HDMI display**:
   - Check if the service is running: `systemctl status alog.service`
   - Verify TTY1 configuration: `cat /etc/systemd/system/getty@tty1.service.d/override.conf`

2. **Service fails to start**:
   - Check logs: `journalctl -u alog.service -n 50`
   - Verify permissions: `ls -la ~/alog`
   - Check Python environment: `~/alog/venv/bin/python -V`

3. **No audio detection**:
   - Verify audio device: `arecord -l`
   - Check permissions: `groups khadas`
