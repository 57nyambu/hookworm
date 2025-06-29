Hookworm
Version 1.0.0
Hookworm is a lightweight, Flask-based GitHub webhook server designed for efficient and secure automated deployments in low-resource environments. It listens for GitHub push events, validates webhook signatures, triggers shell-based deployments, and provides real-time feedback via Telegram notifications and an optional web-based dashboard.

🚀 Features

Lightweight Design: Optimized to run on minimal hardware, requiring as little as 512MB of RAM.
Secure Webhook Validation: Verifies GitHub webhook payloads using HMAC signature authentication.
Comprehensive Logging: Records all webhook activity and deployment outcomes to local log files.
Real-Time Notifications: Sends deployment status (success/failure) to configured Telegram chats.
Web Dashboard: Provides a simple UI for manual testing and displays the timestamp of the last received push event.
System Integration: Includes built-in support for systemd service management and customizable deploy.sh scripts.


🗂️ Project Structure
hookworm/
├── app.py                 # Core Flask application
├── config.py              # Configuration (webhook secrets, Telegram bot token, etc.)
├── deploy.sh              # Customizable deployment script
├── logs/                  # Directory for webhook and deployment logs
├── static/                # Static assets for the web dashboard
├── templates/             # HTML templates for the web UI
├── requirements.txt       # Python dependencies
└── systemd/hookworm.service # Example systemd service file


🛠️ Installation
Prerequisites

Python 3.8+
GitHub repository with webhook support
Telegram bot token (for notifications)
Optional: systemd for service management

Steps

Clone the Repository
git clone https://github.com/yourusername/hookworm.git
cd hookworm


Set Up a Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies
pip install -r requirements.txt


Configure Environment

Copy config.example.py to config.py:cp config.example.py config.py


Edit config.py to include your GitHub webhook secret, Telegram bot token, and other settings.


Set Up Deployment Script

Modify deploy.sh to include your deployment commands (e.g., git pull, docker-compose up, etc.).
Ensure deploy.sh is executable:chmod +x deploy.sh




Run the Server
python app.py


Optional: Configure as a Systemd Service

Copy the provided systemd/hookworm.service to /etc/systemd/system/.
Enable and start the service:sudo systemctl enable hookworm.service
sudo systemctl start hookworm.service






🔧 Configuration
Edit config.py to customize Hookworm's behavior:
# config.py
GITHUB_WEBHOOK_SECRET = "your-github-webhook-secret"
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
TELEGRAM_CHAT_ID = "your-telegram-chat-id"
LOG_PATH = "logs/hookworm.log"
DEPLOY_SCRIPT = "deploy.sh"
WEB_UI_ENABLED = True
PORT = 5000


GITHUB_WEBHOOK_SECRET: Secret key for GitHub webhook HMAC validation.
TELEGRAM_BOT_TOKEN: Token for your Telegram bot.
TELEGRAM_CHAT_ID: Chat ID for receiving notifications.
LOG_PATH: Path for storing logs.
DEPLOY_SCRIPT: Path to the deployment script.
WEB_UI_ENABLED: Enable/disable the web dashboard.
PORT: Port for the Flask server.


🌐 Webhook Setup

In your GitHub repository, go to Settings > Webhooks > Add webhook.
Set the Payload URL to http://your-server:5000/webhook.
Choose Content type as application/json.
Enter your Secret (must match GITHUB_WEBHOOK_SECRET in config.py).
Select Send me everything or specific events (e.g., push).
Click Add webhook.


🖥️ Web Dashboard
If enabled (WEB_UI_ENABLED = True), access the dashboard at http://your-server:5000/. Features include:

View the timestamp of the last received push event.
Manually trigger a test deployment (requires authentication, if configured).
Inspect recent webhook activity.


📜 Logging
Hookworm logs all webhook events and deployment outcomes to the file specified in LOG_PATH. Example log entry:
2025-06-29 12:34:56 [INFO] Received push event from repository yourusername/your-repo
2025-06-29 12:34:57 [SUCCESS] Deployment script executed successfully


🔔 Telegram Notifications
Hookworm sends deployment status updates to the configured Telegram chat. Example messages:

🟢 Success: "Deployment completed for yourusername/your-repo at 2025-06-29 12:34:57"
🔴 Failure: "Deployment failed for yourusername/your-repo. Check logs for details."

To set up a Telegram bot:

Create a bot via BotFather to get a token.
Start a chat with your bot and get the chat ID using /getid or an external service.


🧪 Testing

Local Testing: Use curl to simulate a GitHub webhook:curl -X POST http://localhost:5000/webhook -H "X-Hub-Signature-256: sha256=your-hmac-signature" -H "Content-Type: application/json" -d '{"ref": "refs/heads/main", "repository": {"name": "your-repo"}}'


Web UI Testing: Access the dashboard and use the manual trigger (if enabled).


🤝 Contributing
Contributions are welcome! To contribute:

Fork the repository.
Create a feature branch (git checkout -b feature/your-feature).
Commit your changes (git commit -m "Add your feature").
Push to the branch (git push origin feature/your-feature).
Open a pull request.

Please ensure your code follows PEP 8 and includes tests where applicable.

📄 License
Hookworm is licensed under the MIT License.

📞 Support
For issues, feature requests, or questions, please open an issue on the GitHub repository.
