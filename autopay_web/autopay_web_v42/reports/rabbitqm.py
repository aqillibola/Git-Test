import streamlit as st
import streamlit.components.v1 as components

RABBITQM_DIRECT_URL = "http://192.168.10.14:15672/"
RABBITQM_PROXY_PATH = "/rabbitmq/"


def render(start_dt=None, end_dt=None):
    st.subheader("🐇 RabbitQM")
    st.caption("RabbitMQ management interface")

    st.success(
        "Ички ойнада очиш учун RabbitMQ reverse proxy орқали `/rabbitmq/` манзилга уланади. "
        "Агар серверда nginx proxy ҳали қўйилмаган бўлса, архив ичидаги `nginx_rabbitmq_proxy.conf` ни ишлатинг."
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"**Proxy path:** `{RABBITQM_PROXY_PATH}`")
    with col2:
        st.markdown(f"**Direct URL:** `{RABBITQM_DIRECT_URL}`")

    st.link_button("🌐 RabbitQM ни янги ойнада очиш", RABBITQM_PROXY_PATH, use_container_width=True)

    components.html(
        f'''
        <div style="border:1px solid #d7dbe7;border-radius:14px;overflow:hidden;background:#fff;">
            <iframe
                src="{RABBITQM_PROXY_PATH}"
                width="100%"
                height="900"
                style="border:none;background:#fff;"
                referrerpolicy="no-referrer"
            ></iframe>
        </div>
        ''',
        height=920,
        scrolling=True,
    )

    with st.expander("Nginx proxy конфиг"):
        st.code(
            """location /rabbitmq/ {
    proxy_pass http://192.168.10.14:15672/;
    proxy_http_version 1.1;

    proxy_set_header Host 192.168.10.14:15672;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection \"upgrade\";

    proxy_buffering off;
    proxy_read_timeout 3600;
    proxy_send_timeout 3600;

    proxy_hide_header X-Frame-Options;
    add_header X-Frame-Options \"SAMEORIGIN\" always;
    add_header Content-Security-Policy \"frame-ancestors 'self'\" always;
}
""",
            language="nginx",
        )

    return None
