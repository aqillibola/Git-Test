import json
import subprocess
import time
from datetime import datetime

import pandas as pd
import streamlit as st

API_URL = "http://online.xalqsugurta.uz/xs/ins/autopay/amount"
DEFAULT_PINFL = "12345678901234"
CONTENT_TYPE = "application/json"
COMMAND_TIMEOUT = 25
HISTORY_LIMIT = 30


def _run_amount_request(pinfl: str):
    payload = json.dumps({"pinfl": pinfl}, ensure_ascii=False)
    cmd = [
        "curl",
        "-sS",
        "-i",
        "-X",
        "POST",
        "-H",
        f"Content-Type: {CONTENT_TYPE}",
        "-d",
        payload,
        API_URL,
    ]
    started = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT,
            check=False,
        )
        elapsed_ms = round((time.time() - started) * 1000, 2)
        output = ((result.stdout or "") + ("\n" + result.stderr if result.stderr else "")).strip()
        return result.returncode, output, elapsed_ms, payload
    except Exception as exc:
        elapsed_ms = round((time.time() - started) * 1000, 2)
        return 1, str(exc), elapsed_ms, payload


def _split_response(raw_output: str):
    if not raw_output:
        return "", ""

    normalized = raw_output.replace("\r\n", "\n")
    if "\n\n" in normalized:
        header_text, body = normalized.split("\n\n", 1)
    else:
        header_text, body = normalized, ""
    return header_text.strip(), body.strip()


def _extract_status_code(header_text: str):
    for line in header_text.splitlines():
        line = line.strip()
        if line.upper().startswith("HTTP/"):
            parts = line.split()
            if len(parts) >= 2 and parts[1].isdigit():
                return int(parts[1]), line
    return None, None


def _format_json_body(body: str):
    if not body:
        return body
    try:
        return json.dumps(json.loads(body), indent=2, ensure_ascii=False)
    except Exception:
        return body


def render(start_dt=None, end_dt=None):
    st.subheader("🌐 AutoPay Amount API мониторинг")
    st.caption(f"POST {API_URL}")

    pinfl = st.text_input("PINFL", value=DEFAULT_PINFL, key="autopay_amount_pinfl")
    if not pinfl:
        st.warning("PINFL киритинг.")
        return pd.DataFrame()

    rc, output, elapsed_ms, payload = _run_amount_request(pinfl.strip())
    header_text, body = _split_response(output)
    status_code, status_line = _extract_status_code(header_text)
    formatted_body = _format_json_body(body)

    history_key = "autopay_amount_history"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state[history_key].append(
        {
            "Time": timestamp,
            "PINFL": pinfl.strip(),
            "Status": "OK" if rc == 0 and status_code and 200 <= status_code < 300 else "FAIL",
            "HTTP code": status_code if status_code is not None else 0,
            "Response time (ms)": elapsed_ms,
            "Body length": len(body or ""),
        }
    )
    st.session_state[history_key] = st.session_state[history_key][-HISTORY_LIMIT:]
    history_df = pd.DataFrame(st.session_state[history_key])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("HTTP code", str(status_code) if status_code is not None else "N/A")
    c2.metric("Response time", f"{elapsed_ms:.2f} ms")
    c3.metric("Body length", len(body or ""))
    c4.metric("Command status", "OK" if rc == 0 else "FAIL")

    if status_line:
        st.info(status_line)
    elif rc != 0:
        st.error("curl command failed.")

    if not history_df.empty:
        st.markdown("### Response time history")
        st.line_chart(history_df.set_index("Time")[["Response time (ms)"]], use_container_width=True)

        st.markdown("### HTTP status history")
        st.bar_chart(history_df.set_index("Time")[["HTTP code"]], use_container_width=True)

        st.markdown("### Recent requests")
        st.dataframe(history_df, use_container_width=True, hide_index=True)

    st.markdown("### Request")
    st.code(
        f"curl -i -X POST -H \"Content-Type: application/json\" -d '{payload}' \"{API_URL}\"",
        language="bash",
    )

    st.markdown("### Response headers")
    st.code(header_text or "(no headers)", language="http")

    st.markdown("### Response body")
    st.code(formatted_body or "(empty body)", language="json")

    return history_df
