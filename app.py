import streamlit as st
import os
from dotenv import load_dotenv

st.set_page_config(page_title="SEO壁打ち部屋", page_icon="💭", layout="wide")
load_dotenv()

# ── Password Gate ──────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("💭 SEO壁打ち部屋")
    st.markdown("---")
    col_c, col_r = st.columns([1, 2])
    with col_c:
        pwd = st.text_input("パスワード", type="password", placeholder="パスワードを入力")
        if st.button("入室", type="primary"):
            correct = ""
            try:
                correct = st.secrets.get("APP_PASSWORD", "")
            except Exception:
                pass
            if not correct:
                correct = os.getenv("APP_PASSWORD", "")
            if pwd and pwd == correct:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("パスワードが違います")
    st.stop()

# ── Navigation ─────────────────────────────────────────────────────────────────
pg = st.navigation([
    st.Page("pages/home.py",  title="部屋の説明", icon="📋"),
    st.Page("pages/chat.py",  title="チャット",   icon="💬"),
])
pg.run()
