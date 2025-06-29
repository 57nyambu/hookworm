# Hookworm

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/hookworm/releases)
[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.0+-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/yourusername/hookworm/actions)
[![Code Style](https://img.shields.io/badge/code%20style-PEP8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Maintenance](https://img.shields.io/badge/maintained-yes-green.svg)](https://github.com/yourusername/hookworm/graphs/commit-activity)

> A lightweight, secure Flask-based GitHub webhook server for automated deployments in low-resource environments.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## 🎯 Overview

Hookworm is designed for developers and DevOps engineers who need a reliable, lightweight solution for automated deployments triggered by GitHub webhooks. It's particularly suited for:

- **Small to medium-scale projects** requiring automated CI/CD
- **Resource-constrained environments** (VPS, Raspberry Pi, etc.)
- **Teams needing real-time deployment notifications** via Telegram
- **Projects requiring secure webhook validation** and comprehensive logging

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🚀 **Lightweight Design** | Runs efficiently on minimal hardware (512MB RAM minimum) |
| 🔒 **Secure Validation** | HMAC SHA-256 signature verification for GitHub webhooks |
| 📊 **Comprehensive Logging** | Detailed logs of all webhook events and deployment outcomes |
| 📱 **Real-time Notifications** | Telegram integration for instant deployment status updates |
| 🌐 **Web Dashboard** | Optional web UI for monitoring and manual deployment triggers |
| ⚙️ **System Integration** | Built-in systemd service support for production deployments |
| 🛠️ **Customizable Scripts** | Flexible deployment script configuration |

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/hookworm.git
cd hookworm

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your settings
cp config.example.py config.py
# Edit config.py with your credentials

# Make deployment script executable
chmod +x deploy.sh

# Run the server
python app.py
```

## 🛠️ Installation

### Prerequisites

- **Python 3.8+**
- **GitHub repository** with webhook support
- **Telegram bot token** (for notifications)
- **systemd** (optional, for service management)

### Detailed Setup

1. **Clone and Navigate**
   ```bash
   git clone https://github.com/yourusername/hookworm.git
   cd hookworm
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Application**
   ```bash
   cp config.example.py config.py
   ```
   Edit `config.py` with your specific settings (see [Configuration](#configuration) section).

5. **Prepare Deployment Script**
   ```bash
   chmod +x deploy.sh
   ```
   Customize `deploy.sh` with your deployment commands.

6. **Run Application**
   ```bash
   python app.py
   ```

### Production Deployment (systemd)

For production environments, set up Hookworm as a systemd service:

```bash
# Copy service file
sudo cp systemd/hookworm.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable hookworm.service
sudo systemctl start hookworm.service

# Check status
sudo systemctl status hookworm.service
```

## ⚙️ Configuration

Configure Hookworm by editing `config.py`:

```python
# config.py
GITHUB_WEBHOOK_SECRET = "your-github-webhook-secret"
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
TELEGRAM_CHAT_ID = "your-telegram-chat-id"
LOG_PATH = "logs/hookworm.log"
DEPLOY_SCRIPT = "deploy.sh"
WEB_UI_ENABLED = True
PORT = 5000
```

### Configuration Parameters

| Parameter | Description | Required |
|-----------|-------------|----------|
| `GITHUB_WEBHOOK_SECRET` | Secret key for GitHub webhook HMAC validation | ✅ |
| `TELEGRAM_BOT_TOKEN` | Token for your Telegram bot | ✅ |
| `TELEGRAM_CHAT_ID` | Chat ID for receiving notifications | ✅ |
| `LOG_PATH` | Path for storing application logs | ❌ |
| `DEPLOY_SCRIPT` | Path to your deployment script | ❌ |
| `WEB_UI_ENABLED` | Enable/disable the web dashboard | ❌ |
| `PORT` | Port for the Flask server | ❌ |

## 🔧 Usage

### GitHub Webhook Setup

1. Navigate to your GitHub repository
2. Go to **Settings** → **Webhooks** → **Add webhook**
3. Configure the webhook:
   - **Payload URL**: `http://your-server:5000/webhook`
   - **Content type**: `application/json`
   - **Secret**: Your `GITHUB_WEBHOOK_SECRET`
   - **Events**: Select "Push events" or "Send me everything"
4. Click **Add webhook**

### Web Dashboard

Access the dashboard at `http://your-server:5000/` when `WEB_UI_ENABLED = True`:

- View last received push event timestamp
- Manually trigger test deployments
- Monitor recent webhook activity

### Telegram Bot Setup

1. **Create Bot**: Message [@BotFather](https://t.me/botfather) on Telegram
2. **Get Token**: Follow BotFather's instructions to create a bot and get the token
3. **Get Chat ID**: Start a chat with your bot and use a service to get your chat ID

## 📁 Project Structure

```
hookworm/
├── app.py                    # Core Flask application
├── config.py                 # Configuration settings
├── deploy.sh                 # Customizable deployment script
├── requirements.txt          # Python dependencies
├── logs/                     # Log files directory
│   └── hookworm.log         # Application logs
├── static/                   # Static assets for web UI
├── templates/                # HTML templates
├── systemd/                  # System service files
│   └── hookworm.service     # systemd service configuration
└── README.md                # This file
```

## 📋 API Documentation

### Webhook Endpoint

**POST** `/webhook`

Receives GitHub webhook payloads and triggers deployments.

**Headers:**
- `X-Hub-Signature-256`: GitHub HMAC signature
- `Content-Type`: `application/json`

**Response:**
- `200 OK`: Webhook received and processed successfully
- `400 Bad Request`: Invalid payload or signature
- `500 Internal Server Error`: Deployment script execution failed

### Dashboard Endpoint

**GET** `/`

Serves the web dashboard interface (when enabled).

## 📊 Logging

Hookworm maintains comprehensive logs at the configured `LOG_PATH`:

```
2025-06-29 12:34:56 [INFO] Received push event from repository yourusername/your-repo
2025-06-29 12:34:57 [SUCCESS] Deployment script executed successfully
2025-06-29 12:35:01 [ERROR] Deployment failed: Command returned non-zero exit status
```

## 📱 Telegram Notifications

Automatic status updates are sent to your configured Telegram chat:

- 🟢 **Success**: "Deployment completed for yourusername/your-repo at 2025-06-29 12:34:57"
- 🔴 **Failure**: "Deployment failed for yourusername/your-repo. Check logs for details."

## 🧪 Testing

### Local Testing

Simulate GitHub webhooks using curl:

```bash
curl -X POST http://localhost:5000/webhook \
  -H "X-Hub-Signature-256: sha256=your-hmac-signature" \
  -H "Content-Type: application/json" \
  -d '{"ref": "refs/heads/main", "repository": {"name": "your-repo"}}'
```

### Web UI Testing

Access the dashboard and use the manual trigger feature (when authentication is configured).

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines

- Follow **PEP 8** coding standards
- Include **tests** for new features
- Update **documentation** for any API changes
- Ensure **backward compatibility** when possible

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- 🐛 **Bug Reports**: [Open an issue](https://github.com/yourusername/hookworm/issues/new?template=bug_report.md)
- ✨ **Feature Requests**: [Request a feature](https://github.com/yourusername/hookworm/issues/new?template=feature_request.md)
- 💬 **Questions**: [Start a discussion](https://github.com/yourusername/hookworm/discussions)
- 📧 **Security Issues**: Contact us privately at security@yourdomain.com

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

[Report Bug](https://github.com/yourusername/hookworm/issues) • [Request Feature](https://github.com/yourusername/hookworm/issues) • [View Documentation](https://github.com/yourusername/hookworm/wiki)

</div>
