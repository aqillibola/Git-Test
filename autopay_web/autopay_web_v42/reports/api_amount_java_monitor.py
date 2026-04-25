import json
import time
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

API_URL = "http://online.xalqsugurta.uz/xs/ins/autopay/amount"
DEFAULT_PINFL = "12345678901234"
REQUEST_TIMEOUT = 25
HISTORY_LIMIT = 30


JAVA_TEMPLATE = '''public LoanAmountResponse getLoanAmount(String pinfl) {
    String url = "http://online.xalqsugurta.uz/xs/ins/autopay/amount";

    Map<String, String> requestBody = new HashMap<>();
    requestBody.put("pinfl", pinfl != null ? pinfl : "");

    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));

    HttpEntity<Map<String, String>> entity = new HttpEntity<>(requestBody, headers);

    try {
        log.info("Sending request to ORDS: URL={}, Body={}", url, requestBody);
        ResponseEntity<LoanAmountResponse> response = restTemplate.postForEntity(url, entity, LoanAmountResponse.class);
        return response.getBody();
    } catch (HttpClientErrorException | HttpServerErrorException e) {
        log.error("REST Error from XalqSugurta API: Status={}, Body={}",
                  e.getStatusCode(), e.getResponseBodyAsString());
        throw new ExternalServiceException("Ошибка внешнего сервиса: " + e.getRawStatusCode());
    } catch (Exception e) {
        log.error("Unknown error while calling XalqSugurta API", e);
        throw e;
    }
}'''


def _run_java_style_request(pinfl: str):
    payload = {"pinfl": pinfl if pinfl is not None else ""}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    started = time.time()
    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
        elapsed_ms = round((time.time() - started) * 1000, 2)
        return response, elapsed_ms, payload, None
    except Exception as exc:
        elapsed_ms = round((time.time() - started) * 1000, 2)
        return None, elapsed_ms, payload, str(exc)



def _format_body(text: str):
    if not text:
        return text
    try:
        return json.dumps(json.loads(text), indent=2, ensure_ascii=False)
    except Exception:
        return text



def render(start_dt=None, end_dt=None):
    st.subheader("☕ AutoPay Amount Java API мониторинг")
    st.caption("Spring RestTemplate логикаси бўйича алоҳида текширув")

    pinfl = st.text_input("PINFL", value=DEFAULT_PINFL, key="autopay_amount_java_pinfl")
    if pinfl is None:
        pinfl = ""

    response, elapsed_ms, payload, error_text = _run_java_style_request(pinfl.strip())

    history_key = "autopay_amount_java_history"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_code = response.status_code if response is not None else None
    body_text = response.text if response is not None else ""
    st.session_state[history_key].append(
        {
            "Time": timestamp,
            "PINFL": pinfl.strip(),
            "Status": "OK" if response is not None and response.ok else "FAIL",
            "HTTP code": status_code if status_code is not None else 0,
            "Response time (ms)": elapsed_ms,
            "Body length": len(body_text or ""),
        }
    )
    st.session_state[history_key] = st.session_state[history_key][-HISTORY_LIMIT:]
    history_df = pd.DataFrame(st.session_state[history_key])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("HTTP code", str(status_code) if status_code is not None else "N/A")
    c2.metric("Response time", f"{elapsed_ms:.2f} ms")
    c3.metric("Body length", len(body_text or ""))
    c4.metric("Result", "OK" if response is not None and response.ok else "FAIL")

    if error_text:
        st.error(error_text)
    elif response is not None:
        if response.ok:
            st.success(f"HTTP {response.status_code} {response.reason}")
        else:
            st.error(f"HTTP {response.status_code} {response.reason}")

    if not history_df.empty:
        st.markdown("### Response time history")
        st.line_chart(history_df.set_index("Time")[["Response time (ms)"]], use_container_width=True)

        st.markdown("### HTTP status history")
        st.bar_chart(history_df.set_index("Time")[["HTTP code"]], use_container_width=True)

        st.markdown("### Recent requests")
        st.dataframe(history_df, use_container_width=True, hide_index=True)

    st.markdown("### Java service method")
    st.code(JAVA_TEMPLATE, language="java")

    st.markdown("### Request payload")
    st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")

    st.markdown("### Request headers")
    st.code("Content-Type: application/json\nAccept: application/json", language="http")

    if response is not None:
        st.markdown("### Response headers")
        headers_text = "\n".join(f"{k}: {v}" for k, v in response.headers.items())
        st.code(headers_text or "(no headers)", language="http")

        st.markdown("### Response body")
        st.code(_format_body(response.text) or "(empty body)", language="json")

    return history_df
