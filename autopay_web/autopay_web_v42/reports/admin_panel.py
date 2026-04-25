import pandas as pd
import streamlit as st
from auth import (
    load_users, create_user, update_user_role, update_user_password, update_user_active,
    rename_full_name, current_user, load_roles, get_role_names, create_role,
    update_role_permissions, delete_role
)
from config import BASE_MENU, ADMIN_MENU

ALL_MENU_ITEMS = BASE_MENU + ADMIN_MENU


def _normalize_allowed_menu(value):
    if value == "*":
        return ALL_MENU_ITEMS.copy()
    return [item for item in (value or []) if item in ALL_MENU_ITEMS]


def render():
    st.subheader("⚙️ Админ панель")
    st.caption("Фойдаланувчилар, роллар, ҳуқуқлар ва парольларни бошқариш")
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Фойдаланувчилар", "➕ Яратиш", "🛡️ Роллар", "🔑 Пароль"])

    with tab1:
        users = load_users()
        if users:
            df = pd.DataFrame(users)
            if "password_hash" in df.columns:
                df["password_hash"] = "********"
            st.dataframe(df, use_container_width=True, hide_index=True)

            usernames = [u["username"] for u in users]
            selected = st.selectbox("Фойдаланувчини танланг", usernames)
            user = next((u for u in users if u["username"] == selected), None)

            if user:
                col1, col2 = st.columns(2)
                role_names = get_role_names()
                with col1:
                    full_name = st.text_input("Ф.И.Ш", value=user.get("full_name", selected))
                    role = st.selectbox("Роль", role_names, index=role_names.index(user.get("role", role_names[0])))
                with col2:
                    active = st.toggle("Фаол", value=user.get("is_active", True))
                    st.caption(f"Логин: {selected}")

                c1, c2, c3 = st.columns(3)
                if c1.button("💾 Ф.И.Ш сақлаш", use_container_width=True):
                    ok, msg = rename_full_name(selected, full_name)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()

                if c2.button("🛡️ Роль сақлаш", use_container_width=True):
                    ok, msg = update_user_role(selected, role)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()

                if c3.button("🔄 Фаолликни сақлаш", use_container_width=True):
                    if selected == current_user().get("username") and not active:
                        st.error("Ўзингизни ўчира олмайсиз")
                    else:
                        ok, msg = update_user_active(selected, active)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()
        else:
            st.info("Фойдаланувчилар йўқ")

    with tab2:
        with st.form("create_user_form", clear_on_submit=True):
            username = st.text_input("Янги логин")
            full_name = st.text_input("Ф.И.Ш")
            role_names = get_role_names()
            default_index = role_names.index("operator") if "operator" in role_names else 0
            role = st.selectbox("Роль", role_names, index=default_index)
            password = st.text_input("Пароль", type="password")
            password2 = st.text_input("Парольни тасдиқлаш", type="password")
            is_active = st.checkbox("Фаол", value=True)
            submitted = st.form_submit_button("➕ Фойдаланувчи яратиш", use_container_width=True)

        if submitted:
            if not username.strip():
                st.error("Логин киритинг")
            elif len(password) < 4:
                st.error("Пароль камида 4 белги бўлсин")
            elif password != password2:
                st.error("Пароллар мос эмас")
            else:
                ok, msg = create_user(username, full_name, password, role, is_active)
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

    with tab3:
        st.markdown("#### 🛡️ Роль яратиш ва ҳуқуқ бериш")
        role_col1, role_col2 = st.columns([1.1, 1])
        with role_col1:
            with st.form("create_role_form", clear_on_submit=True):
                role_name = st.text_input("Янги роль номи")
                role_desc = st.text_input("Изоҳ")
                allow_all = st.checkbox("Барча пунктлар", value=False)
                selected_menu = st.multiselect("Керакли пунктларни танланг", ALL_MENU_ITEMS, default=[])
                create_submitted = st.form_submit_button("➕ Роль яратиш", use_container_width=True)
            if create_submitted:
                allowed_menu = "*" if allow_all else selected_menu
                ok, msg = create_role(role_name, allowed_menu, role_desc)
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()

        with role_col2:
            roles = load_roles()
            if roles:
                role_names = [r.get("name") for r in roles]
                selected_role = st.selectbox("Мавжуд роль", role_names, key="existing_role_select")
                role_obj = next((r for r in roles if r.get("name") == selected_role), None)
                if role_obj:
                    edit_desc_key = f"role_desc_edit__{selected_role}"
                    edit_all_key = f"role_allow_all__{selected_role}"
                    edit_menu_key = f"role_menu_edit__{selected_role}"
                    with st.form(f"edit_role_form__{selected_role}"):
                        role_desc_edit = st.text_input(
                            "Изоҳни таҳрирлаш",
                            value=role_obj.get("description", ""),
                            key=edit_desc_key,
                        )
                        allow_all_edit = st.checkbox(
                            "Барча пунктлар",
                            value=role_obj.get("allowed_menu") == "*",
                            key=edit_all_key,
                        )
                        picked = _normalize_allowed_menu(role_obj.get("allowed_menu"))
                        selected_menu_edit = st.multiselect(
                            "Роль учун пунктлар",
                            ALL_MENU_ITEMS,
                            default=picked,
                            key=edit_menu_key,
                            disabled=allow_all_edit,
                        )
                        c1, c2 = st.columns(2)
                        save_clicked = c1.form_submit_button("💾 Роль ҳуқуқларини сақлаш", use_container_width=True)
                        delete_clicked = c2.form_submit_button("🗑️ Рольни ўчириш", use_container_width=True)

                    if save_clicked:
                        allowed_menu = "*" if allow_all_edit else selected_menu_edit
                        ok, msg = update_role_permissions(selected_role, allowed_menu, role_desc_edit)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()
                    if delete_clicked:
                        ok, msg = delete_role(selected_role)
                        (st.success if ok else st.error)(msg)
                        if ok:
                            st.rerun()
            st.caption("Админ панель ҳуқуқи учун `⚙️ Админ панель` пунктни ҳам танланг ёки `Барча пунктлар`ни беринг.")

    with tab4:
        users = load_users()
        usernames = [u["username"] for u in users]
        selected_for_pass = st.selectbox("Паролини ўзгартириш", usernames, key="pass_user")
        new_pass = st.text_input("Янги пароль", type="password", key="new_pass")
        new_pass2 = st.text_input("Янги парольни тасдиқлаш", type="password", key="new_pass2")
        if st.button("🔑 Парольни янгилаш", use_container_width=True):
            if len(new_pass) < 4:
                st.error("Пароль камида 4 белги бўлсин")
            elif new_pass != new_pass2:
                st.error("Пароллар мос эмас")
            else:
                ok, msg = update_user_password(selected_for_pass, new_pass)
                (st.success if ok else st.error)(msg)
