import streamlit as st
import os
from dotenv import load_dotenv

st.set_page_config(page_title="SEO JAM", page_icon="🎸", layout="wide")

# ── Password Gate ──────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🎸 SEO JAM")
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

# ── Main Home ──────────────────────────────────────────────────────────────────
load_dotenv()

st.title("🎸 SEO JAM")
st.markdown("SEOコンテンツの疑問を、壁打ちしながら解決する部屋。")
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### こんなことを聞けます

    - 📝 **記事作成・構成** — 骨子の作り方、H2/H3の設計、見出しの整合性
    - ✍️ **本文の書き方** — PREP構造、NGワード、文体統一
    - 🔍 **KW・マーケ戦略** — KWの種類、検索意図、CV距離の考え方
    - 💬 **なんでも壁打ち** — 「この記事どう思う？」「どこから手をつける？」
    """)

with col2:
    st.markdown("""
    ### 使い方

    1. 左のメニューから **Chat** を開く
    2. カテゴリを選ぶ（または「なんでも」でOK）
    3. 質問を入力する

    ### ポイント
    - 記事のURL・見出し・本文を貼り付けると具体的なフィードバックができます
    - 「なぜそうするのか」まで聞くと理解が深まります
    """)

st.markdown("---")
st.caption("Powered by Claude | SEO JAM")

# ログアウト
st.sidebar.markdown("---")
if st.sidebar.button("退室", type="secondary"):
    st.session_state.authenticated = False
    st.rerun()
