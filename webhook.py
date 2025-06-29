from flask import Flask, request, abort, render_template, jsonify
import hmac, hashlib, subprocess, os
from datetime import datetime
import requests
from dotenv import load_dotenv

# Initialize Flask app with template and static folders
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')

load_dotenv('/home/prod/finarch-backend/.env')

# Configuration constants
GITHUB_SECRET = os.environ.get("GITHUB_SECRET", "").encode()
# GitHub Configuration
GITHUB_REPO = os.environ.get("GITHUB_REPO")  # Format: owner/repo
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}"
GITHUB_PAT = os.environ.get("GITHUB_PAT") 
DISPLAY_REPO_NAME = os.environ.get("DISPLAY_NAME")
BASE_DIR = "/home/prod/devops"
DEPLOY_SCRIPT = os.path.join(BASE_DIR, "deploy.sh")
LOG_FILE = os.path.join(BASE_DIR, "webhook.log")
TIMESTAMP_FILE = os.path.join(BASE_DIR, ".last_push")
DEPLOYMENT_LOG_FILE = os.path.join(BASE_DIR, "deploy.log")

def initialize_application():
    """Ensure all required files and directories exist"""
    required_files = [DEPLOY_SCRIPT, LOG_FILE, DEPLOYMENT_LOG_FILE]
    
    for file_path in required_files:
        dir_path = os.path.dirname(file_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        
        if not os.path.exists(file_path):
            if file_path.endswith('.log'):
                open(file_path, 'a').close()
            elif file_path == DEPLOY_SCRIPT:
                raise FileNotFoundError(f"Deploy script missing at {file_path}")

# Call this at startup
initialize_application()

def check_github_updates():
    """Check if there are new commits in the GitHub repository"""
    if not GITHUB_PAT:
        log("GitHub PAT not configured - skipping update check")
        return None

    headers = {
        "Authorization": f"token {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        # Get the latest commit from GitHub
        response = requests.get(f"{GITHUB_API_URL}/commits/main", headers=headers)
        response.raise_for_status()
        latest_commit = response.json()
        
        # Get the last deployed commit (stored in a file)
        last_commit_file = os.path.join(BASE_DIR, ".last_commit")
        if os.path.exists(last_commit_file):
            with open(last_commit_file, 'r') as f:
                last_deployed_commit = f.read().strip()
        else:
            last_deployed_commit = None
            
        # Compare commits
        if last_deployed_commit == latest_commit['sha']:
            return False  # No updates
        return True  # Updates available
        
    except Exception as e:
        log(f"Failed to check GitHub updates: {str(e)}")
        return None

def save_timestamp():
    """Save the current timestamp to file"""
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'))

def log(msg):
    """Log a message to the log file"""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def get_recent_logs(count=5):
    """Get recent log entries"""
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            return [line.strip() for line in lines[-count:][::-1]]  # Newest first
    except Exception as e:
        log(f"Failed to read logs: {e}")
        return []

def get_last_deployment_output():
    """Get the last deployment output with proper error handling"""
    try:
        if not os.path.exists(DEPLOYMENT_LOG_FILE):
            log(f"Deployment log file not found at {DEPLOYMENT_LOG_FILE}")
            return "No deployment log file found (expected at: {})".format(DEPLOYMENT_LOG_FILE)
            
        with open(DEPLOYMENT_LOG_FILE, 'r') as f:
            lines = f.readlines()
            return ''.join(lines[-50:])  # Last 50 lines
    except Exception as e:
        log(f"Failed to read deployment log: {str(e)}")
        return f"Error reading deployment log: {str(e)}"

@app.route("/")
def dashboard():
    """Main dashboard view"""
    # Get last push timestamp
    if os.path.exists(TIMESTAMP_FILE):
        with open(TIMESTAMP_FILE) as f:
            last_push = f.read().strip()
    else:
        last_push = None
        
    # Get repo info
    repo_info = {
        "name": DISPLAY_REPO_NAME,
        "last_checked": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        "updates_available": check_github_updates()
    }
        
    return render_template(
        'dashboard.html',
        last_push=last_push,
        recent_logs=get_recent_logs(),
        last_deployment_output=get_last_deployment_output(),
        repo_info=repo_info
    )

@app.route("/logs")
def show_logs():
    """Show full logs view"""
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
            logs = [line.strip() for line in lines[-100:][::-1]]  # Last 100 entries, newest first
    except Exception as e:
        log(f"Failed to read logs: {e}")
        logs = []
        
    return render_template('logs.html', logs=logs)

@app.route("/webhook", methods=["POST"])
def webhook():
    """GitHub webhook handler"""
    save_timestamp()
    
    # Verify signature if secret is set
    if GITHUB_SECRET:
        signature = request.headers.get('X-Hub-Signature-256', '').split('=')[-1]
        computed_signature = hmac.new(GITHUB_SECRET, request.data, hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(signature, computed_signature):
            log("⚠️ Invalid signature received")
            abort(403, "Invalid signature")

    event = request.headers.get("X-GitHub-Event", "ping")
    
    if event == "ping":
        log("Ping received")
        return jsonify({"status": "pong"}), 200
        
    elif event == "push":
        # Check if there are actual code changes
        commits = request.json.get('commits', [])
        meaningful_changes = any(
            commit for commit in commits 
            if any(modified for modified in commit.get('modified', []) 
                  if not modified.endswith('.md'))  # Ignore markdown file changes
        )
        
        if not meaningful_changes:
            log("Push received but no meaningful changes detected")
            return jsonify({
                "status": "ignored",
                "reason": "No meaningful code changes detected"
            }), 200
            
        try:
            subprocess.Popen(["/bin/bash", DEPLOY_SCRIPT])
            log("🚀 Deployment triggered via webhook")
            
            # Save the latest commit SHA
            latest_commit = request.json.get('after')
            if latest_commit:
                with open(os.path.join(BASE_DIR, ".last_commit"), 'w') as f:
                    f.write(latest_commit)
            
            return jsonify({"status": "deployment triggered"}), 200
        except Exception as e:
            log(f"Failed to execute deploy script: {e}")
            return jsonify({"status": "deploy failed", "error": str(e)}), 500
            
    log(f"Ignored event: {event}")
    return jsonify({"status": "ignored event"}), 200

@app.route("/test", methods=["POST"])
def test_trigger():
    """Manual test trigger endpoint"""
    try:
        subprocess.Popen(["/bin/bash", DEPLOY_SCRIPT])
        log("✅ Manual test deploy triggered from web UI")
        save_timestamp()
        return dashboard()
    except Exception as e:
        log(f"Manual deploy failed: {e}")
        return render_template(
            'dashboard.html',
            last_push="Error: Deployment failed",
            recent_logs=get_recent_logs(),
            last_deployment_output=str(e)
        ), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8800)
