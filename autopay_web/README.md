# AutoPay Web

AutoPay web project package.

Current uploaded version: `autopay_web_v42.zip`.

## What is included in v42

- Streamlit-based AutoPay admin/dashboard UI.
- Oracle dashboard bridge.
- Reports module.
- RabbitQM page.
- AutoPay Amount Java API monitoring.
- RabbitMQ reverse proxy support through `/rabbitmq/`.
- Nginx sample config: `nginx_rabbitmq_proxy.conf`.

## Security note

Before publishing to GitHub, real passwords/secrets must be replaced with placeholders.

Use placeholders like:

```text
CHANGE_ME_POSTGRES_PASSWORD
CHANGE_ME_ORACLE_PASSWORD
CHANGE_ME_ADMIN_PASSWORD
```

## Run example

```bash
cd /opt/autopay
pip install -r requirements.txt
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## Default install path

```text
/opt/autopay
```

Do not use versioned install paths like `/opt/autopay_web_v42` on the server.
