#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/autopay
SERVICE_NAME=autopay.service
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LEGACY_UNITS=(autopay_web.service web_dastur.service)

mkdir -p "$APP_DIR"

if [ ! -f "$APP_DIR/.env" ]; then
  if [ -f "$SCRIPT_DIR/.env" ]; then
    cp -f "$SCRIPT_DIR/.env" "$APP_DIR/.env"
  else
    cp -f "$SCRIPT_DIR/.env.example" "$APP_DIR/.env"
  fi
fi

if systemctl list-unit-files | grep -q '^autopay.service'; then
  systemctl stop "$SERVICE_NAME" || true
fi

for unit in "${LEGACY_UNITS[@]}"; do
  if [ -f "/etc/systemd/system/$unit" ]; then
    systemctl stop "$unit" || true
    systemctl disable "$unit" || true
    rm -f "/etc/systemd/system/$unit"
  fi
done

pkill -f "/opt/autopay/.venv/bin/streamlit run /opt/autopay/app.py" || true
sleep 1

tar --exclude='.venv' --exclude='__pycache__' --exclude='.env' -cf - -C "$SCRIPT_DIR" . | tar -xf - -C "$APP_DIR"

chmod +x "$APP_DIR/install.sh" "$APP_DIR/start.sh" "$APP_DIR/stop.sh" "$APP_DIR/restart.sh"

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --upgrade pip wheel setuptools
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/requirements.txt"

mkdir -p /root/.streamlit
cat > /root/.streamlit/config.toml <<'CFG'
[browser]
gatherUsageStats = false
CFG

cp -f "$APP_DIR/autopay.service" /etc/systemd/system/autopay.service
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"

echo "Installed to $APP_DIR"
echo "Run: systemctl restart autopay.service && systemctl status autopay.service --no-pager -l"
