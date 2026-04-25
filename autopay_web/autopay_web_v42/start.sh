#!/usr/bin/env bash
set -euo pipefail
cd /opt/autopay
exec /opt/autopay/.venv/bin/streamlit run /opt/autopay/app.py \
  --server.port "${AUTOPAY_PORT:-8501}" \
  --server.address "${AUTOPAY_ADDRESS:-0.0.0.0}"
