#!/bin/bash
set -euo pipefail

# Deployment Configuration
readonly PROJECT_DIR="/home/prod/finarch-backend"
readonly SOCK_PATH="$PROJECT_DIR/gunicorn.sock"
readonly VENV="$PROJECT_DIR/venv/bin/activate"
readonly SERVICE="finarch-django.service"
readonly LOG_FILE="/home/prod/devops/webhook.log"
readonly JSON_LOG_FILE="/home/prod/devops/deploy.json.log"
readonly DEPLOYMENT_ID=$(date +"%Y%m%d-%H%M%S")

# Telegram Config
readonly TELEGRAM_API_URL="https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage"
readonly TELEGRAM_RETRY_COUNT=2
readonly TELEGRAM_TIMEOUT=5

# Init logging
exec > >(tee -a "$LOG_FILE") 2>&1

log_json() {
    local level="$1"
    local msg="$2"
    local ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "{\"timestamp\": \"$ts\", \"level\": \"$level\", \"message\": \"$msg\"}" >> "$JSON_LOG_FILE"
}

echo "🔷 Starting FinArchitect deployment $DEPLOYMENT_ID at $(date)"
echo "🔷 Running as user: $(whoami)"
log_json "INFO" "Deployment started with ID $DEPLOYMENT_ID"

send_telegram() {
    local status="$1"
    local message="$2"
    local attempt=0

    if [ -z "${TELEGRAM_TOKEN:-}" ] || [ -z "${CHAT_ID:-}" ]; then
        echo "⚠️  Telegram credentials not set"
        log_json "WARNING" "Telegram credentials not set"
        return 0
    fi

    case "$status" in
        success)
            local emoji="✅"
            local text="*Deployment Success*\\n$emoji $message\\n\\n*ID*: $DEPLOYMENT_ID"
            ;;
        failure)
            local emoji="❌"
            local text="*Deployment Failed*\\n$emoji $message\\n\\n*Host*: $(hostname)\\n*User*: $(whoami)"
            ;;
        warning)
            local emoji="⚠️"
            local text="*Deployment Warning*\\n$emoji $message"
            ;;
        *)
            local emoji="ℹ️"
            local text="*Deployment Info*\\n$emoji $message"
            ;;
    esac

    local encoded=$(echo "$text" | sed -e 's/ /%20/g' -e 's/\\n/%0A/g')

    until [ $attempt -ge $TELEGRAM_RETRY_COUNT ]; do
        code=$(curl -s -o /dev/null -w "%{http_code}" \
            --max-time $TELEGRAM_TIMEOUT \
            -X POST "$TELEGRAM_API_URL" \
            -d "chat_id=${CHAT_ID}&text=$encoded&parse_mode=Markdown")

        if [ "$code" -eq 200 ]; then
            echo "📨 Telegram notification sent ($status)"
            log_json "INFO" "Telegram sent: $status"
            return 0
        fi
        echo "⚠️ Telegram notification attempt $((attempt+1)) failed (HTTP $code)"
        attempt=$((attempt+1))
        sleep 1
    done

    echo "❌ Telegram notification failed after $TELEGRAM_RETRY_COUNT attempts"
    log_json "ERROR" "Telegram failed after retries"
    return 1
}

load_secrets() {
    echo "🔐 Loading .env secrets..."
    log_json "INFO" "Loading environment variables"
    local env_file="$PROJECT_DIR/.env"
    if [ ! -f "$env_file" ]; then
        send_telegram "failure" ".env not found"
        log_json "ERROR" ".env file missing"
        exit 1
    fi

    if [ "$(stat -c %a "$env_file")" != "600" ]; then
        send_telegram "warning" ".env has insecure permissions"
        chmod 600 "$env_file"
    fi

    set -o allexport
    source "$env_file"
    set +o allexport
    log_json "INFO" ".env loaded successfully"
}

fix_permissions() {
    echo "🔧 Checking socket permissions..."
    log_json "INFO" "Checking gunicorn.sock permissions"

    if [ -e "$SOCK_PATH" ]; then
        local owner=$(stat -c '%U:%G' "$SOCK_PATH")
        if [ "$owner" != "tom:tom" ]; then
            send_telegram "warning" "Fixing gunicorn.sock ownership"
            sudo /usr/local/bin/fix_gunicorn_sock.sh || {
                send_telegram "failure" "Failed to fix sock permissions"
                log_json "ERROR" "Failed to change sock ownership"
                exit 1
            }
        fi
    fi
}

git_update() {
    echo "🔄 Pulling latest code..."
    log_json "INFO" "Running git fetch/reset"
    cd "$PROJECT_DIR"

    git fetch origin main || {
        send_telegram "failure" "Git fetch failed"
        log_json "ERROR" "Git fetch failed"
        exit 1
    }

    git reset --hard origin/main || {
        send_telegram "failure" "Git reset failed"
        log_json "ERROR" "Git reset failed"
        exit 1
    }

    log_json "INFO" "Git updated successfully"
}

deploy() {
    load_secrets
    fix_permissions
    cd "$PROJECT_DIR"
    git_update

    if [ ! -f "$VENV" ]; then
        send_telegram "failure" "Virtualenv not found"
        log_json "ERROR" "Virtualenv missing"
        exit 1
    fi
    source "$VENV"

    echo "📦 Installing dependencies..."
    log_json "INFO" "Installing dependencies"
    pip install -r requirements.txt || {
        send_telegram "failure" "pip install failed"
        log_json "ERROR" "pip install failed"
        exit 1
    }

    echo "🔄 Running migrations..."
    log_json "INFO" "Running migrations"
    python manage.py migrate --noinput || {
        send_telegram "failure" "Migration failed"
        log_json "ERROR" "Migration failed"
        exit 1
    }

    echo "📦 Collecting static files..."
    log_json "INFO" "Collecting static files"
    python manage.py collectstatic --noinput || {
        send_telegram "failure" "Static collection failed"
        log_json "ERROR" "Static collection failed"
        exit 1
    }

    echo "♻️ Restarting Gunicorn service..."
    log_json "INFO" "Restarting service $SERVICE"
    sudo systemctl restart "$SERVICE" || {
        send_telegram "failure" "Restart failed"
        log_json "ERROR" "Service restart failed"
        exit 1
    }

    if ! systemctl is-active --quiet "$SERVICE"; then
        send_telegram "failure" "$SERVICE not running"
        log_json "ERROR" "$SERVICE not running after restart"
        exit 1
    fi

    send_telegram "success" "Deployment completed successfully"
    log_json "INFO" "Deployment finished successfully"
    echo "🎉 Deployment successful!"
}

cleanup() {
    local code=$?
    if [ $code -ne 0 ]; then
        echo "❌ Deployment failed with exit code $code"
        log_json "ERROR" "Deployment exited with code $code"
    fi
}
trap cleanup EXIT
deploy
exit 0
