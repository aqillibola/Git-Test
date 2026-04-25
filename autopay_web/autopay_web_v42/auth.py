import json, hashlib, secrets, base64, time
from pathlib import Path
import streamlit as st

USERS_FILE = Path(__file__).resolve().parent / "users.json"
ROLES_FILE = Path(__file__).resolve().parent / "roles.json"
SESSIONS_FILE = Path(__file__).resolve().parent / "sessions.json"
SESSION_TTL_SECONDS = 1800
DEFAULT_ROLE_NAMES = ["admin", "operator", "viewer"]


def _get_query_sid():
    try:
        sid = st.query_params.get("sid")
        return str(sid) if sid else None
    except Exception:
        return None


def _set_query_sid(session_id: str | None):
    try:
        if session_id:
            st.query_params["sid"] = session_id
        elif "sid" in st.query_params:
            del st.query_params["sid"]
    except Exception:
        pass


def _load_sessions():
    if not SESSIONS_FILE.exists():
        return []
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_sessions(sessions):
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def _cleanup_sessions(sessions=None):
    now = time.time()
    sessions = _load_sessions() if sessions is None else sessions
    cleaned = [s for s in sessions if now - float(s.get("last_seen", 0)) <= SESSION_TTL_SECONDS]
    if cleaned != sessions:
        _save_sessions(cleaned)
    return cleaned


def get_session_id():
    if "session_id" in st.session_state and st.session_state["session_id"]:
        _set_query_sid(st.session_state["session_id"])
        return st.session_state["session_id"]

    query_sid = _get_query_sid()
    if query_sid:
        st.session_state["session_id"] = query_sid
    else:
        st.session_state["session_id"] = secrets.token_hex(16)
        _set_query_sid(st.session_state["session_id"])
    return st.session_state["session_id"]


def register_session(user: dict):
    session_id = get_session_id()
    sessions = _cleanup_sessions()
    now = time.time()
    updated = False
    for sess in sessions:
        if sess.get("session_id") == session_id:
            sess.update({
                "username": user.get("username"),
                "full_name": user.get("full_name", user.get("username")),
                "role": user.get("role", "viewer"),
                "last_seen": now,
            })
            updated = True
            break
    if not updated:
        sessions.append({
            "session_id": session_id,
            "username": user.get("username"),
            "full_name": user.get("full_name", user.get("username")),
            "role": user.get("role", "viewer"),
            "last_seen": now,
        })
    _save_sessions(sessions)


def touch_session():
    user = st.session_state.get("user")
    if not user:
        return
    register_session(user)


def remove_session():
    session_id = st.session_state.get("session_id")
    if not session_id:
        return
    sessions = [s for s in _load_sessions() if s.get("session_id") != session_id]
    _save_sessions(sessions)


def get_active_sessions():
    return _cleanup_sessions()


def get_active_session_users():
    seen = set()
    users = []
    for sess in _cleanup_sessions():
        username = sess.get("username") or "unknown"
        if username in seen:
            continue
        seen.add(username)
        users.append({
            "username": username,
            "full_name": sess.get("full_name", username),
            "role": sess.get("role", "viewer"),
        })
    return users

def _default_roles():
    return [
        {"name": "admin", "allowed_menu": "*", "description": "Тўлиқ ҳуқуқ"},
        {"name": "operator", "allowed_menu": [
            "📊 Dashboard", "💸 Келиб тушган пул ва қолдиқ", "🚫 Ечилмайдиган карталар (Имтиёзли)",
            "🏆 Топ Қарздорлар", "📋 Қарздорлар (Барча)", "🕐 Пул ечишга қулай соатлар",
            "📈 Кунлик статистика (%)", "🔍 Хатоликлар таҳлили", "🔎 ЖШШИР бўйича қидирув"
        ], "description": "Ишчи ҳуқуқлар"},
        {"name": "viewer", "allowed_menu": ["📊 Dashboard", "💸 Келиб тушган пул ва қолдиқ", "🔎 ЖШШИР бўйича қидирув"], "description": "Фақат кўриш"},
    ]

def _pbkdf2_hash(password: str, salt: bytes | None = None) -> str:
    if salt is None:
        salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return base64.b64encode(salt).decode() + "$" + base64.b64encode(dk).decode()

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_b64, _ = stored_hash.split("$", 1)
        salt = base64.b64decode(salt_b64.encode())
        expected = _pbkdf2_hash(password, salt)
        return secrets.compare_digest(expected, stored_hash)
    except Exception:
        return False

def make_password_hash(password: str) -> str:
    return _pbkdf2_hash(password)

def load_users():
    if not USERS_FILE.exists():
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def load_roles():
    if not ROLES_FILE.exists():
        save_roles(_default_roles())
    with open(ROLES_FILE, "r", encoding="utf-8") as f:
        roles = json.load(f)
    return roles or _default_roles()

def save_roles(roles):
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(roles, f, ensure_ascii=False, indent=2)

def get_role_names():
    return [r.get("name") for r in load_roles()]

def find_role(role_name: str):
    return next((r for r in load_roles() if r.get("name") == role_name), None)

def create_role(role_name: str, allowed_menu, description: str = ""):
    role_name = role_name.strip()
    if not role_name:
        return False, "Роль номи бўш бўлмасин"
    if find_role(role_name):
        return False, "Бу роль аллақачон мавжуд"
    roles = load_roles()
    roles.append({"name": role_name, "allowed_menu": allowed_menu or [], "description": description.strip()})
    save_roles(roles)
    return True, "Роль яратилди"

def update_role_permissions(role_name: str, allowed_menu, description: str = ""):
    roles = load_roles()
    for role in roles:
        if role.get("name") == role_name:
            role["allowed_menu"] = allowed_menu if allowed_menu else []
            role["description"] = description.strip()
            save_roles(roles)
            return True, "Роль ҳуқуқлари янгиланди"
    return False, "Роль топилмади"

def delete_role(role_name: str):
    if role_name in ["admin", "operator", "viewer"]:
        return False, "Стандарт ролларни ўчириб бўлмайди"
    users = load_users()
    if any(u.get("role") == role_name for u in users):
        return False, "Бу роль бириктирилган фойдаланувчилар бор"
    roles = [r for r in load_roles() if r.get("name") != role_name]
    save_roles(roles)
    return True, "Роль ўчирилди"

def get_allowed_menu_for_role(role_name: str, full_menu: list[str]) -> list[str]:
    role = find_role(role_name)
    if not role:
        return full_menu if role_name == "admin" else []
    allowed = role.get("allowed_menu", [])
    if allowed == "*":
        return full_menu
    return [item for item in full_menu if item in allowed]

def find_user(username: str):
    for user in load_users():
        if user.get("username") == username:
            return user
    return None

def authenticate(username: str, password: str):
    user = find_user(username)
    if not user or not user.get("is_active", True):
        return None
    return user if verify_password(password, user.get("password_hash", "")) else None

def current_user():
    return st.session_state.get("user", {})

def current_role():
    return current_user().get("role", "viewer")

def is_admin():
    return current_role() == "admin"

def login_form():
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Кириш", use_container_width=True)
    if submitted:
        user = authenticate(username.strip(), password)
        if user:
            st.session_state["authenticated"] = True
            st.session_state["user"] = {
                "username": user.get("username"),
                "full_name": user.get("full_name", user.get("username")),
                "role": user.get("role", "viewer"),
            }
            st.session_state["selected_report"] = "💸 Келиб тушган пул ва қолдиқ"
            register_session(st.session_state["user"])
            _set_query_sid(get_session_id())
            st.rerun()
        else:
            st.error("❌ Логин ёки пароль нотўғри")

def logout():
    remove_session()
    _set_query_sid(None)
    for key in ["authenticated", "user", "session_id", "selected_report"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def require_auth():
    if bool(st.session_state.get("authenticated", False)):
        _set_query_sid(get_session_id())
        return True

    query_sid = _get_query_sid()
    if not query_sid:
        return False

    for sess in _cleanup_sessions():
        if sess.get("session_id") == query_sid:
            st.session_state["session_id"] = query_sid
            st.session_state["authenticated"] = True
            st.session_state["user"] = {
                "username": sess.get("username"),
                "full_name": sess.get("full_name", sess.get("username", "Unknown")),
                "role": sess.get("role", "viewer"),
            }
            st.session_state.setdefault("selected_report", "💸 Келиб тушган пул ва қолдиқ")
            register_session(st.session_state["user"])
            _set_query_sid(query_sid)
            return True
    return False

def create_user(username: str, full_name: str, password: str, role: str, is_active: bool = True):
    username = username.strip()
    if not username:
        return False, "Логин бўш бўлмаслиги керак"
    if find_user(username):
        return False, "Бу логин аллақачон мавжуд"
    if role not in get_role_names():
        return False, "Нотўғри роль"
    users = load_users()
    users.append({
        "username": username,
        "full_name": full_name.strip() or username,
        "password_hash": make_password_hash(password),
        "role": role,
        "is_active": is_active,
    })
    save_users(users)
    return True, "Фойдаланувчи яратилди"

def update_user_role(username: str, role: str):
    if role not in get_role_names():
        return False, "Нотўғри роль"
    users = load_users()
    for user in users:
        if user.get("username") == username:
            user["role"] = role
            save_users(users)
            if st.session_state.get("user", {}).get("username") == username:
                st.session_state["user"]["role"] = role
            return True, "Роль янгиланди"
    return False, "Фойдаланувчи топилмади"

def update_user_password(username: str, new_password: str):
    users = load_users()
    for user in users:
        if user.get("username") == username:
            user["password_hash"] = make_password_hash(new_password)
            save_users(users)
            return True, "Пароль янгиланди"
    return False, "Фойдаланувчи топилмади"

def update_user_active(username: str, is_active: bool):
    users = load_users()
    for user in users:
        if user.get("username") == username:
            user["is_active"] = is_active
            save_users(users)
            return True, "Фаоллик ҳолати янгиланди"
    return False, "Фойдаланувчи топилмади"

def rename_full_name(username: str, full_name: str):
    users = load_users()
    for user in users:
        if user.get("username") == username:
            user["full_name"] = full_name.strip() or username
            save_users(users)
            if st.session_state.get("user", {}).get("username") == username:
                st.session_state["user"]["full_name"] = full_name.strip() or username
            return True, "Ф.И.Ш янгиланди"
    return False, "Фойдаланувчи топилмади"
