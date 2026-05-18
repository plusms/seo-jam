import streamlit as st

st.title("💭 SEO壁打ち部屋")
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

    1. 左のメニューから **チャット** を開く
    2. カテゴリを選ぶ（または「なんでも」でOK）
    3. 質問を入力する

    ### ポイント
    - 記事のURL・見出し・本文を貼り付けると具体的なフィードバックができます
    - 「なぜそうするのか」まで聞くと理解が深まります
    - セッションが終わったら「まとめを出す」でコピペ用メモを生成できます
    """)

st.markdown("---")

# ログアウト
if st.sidebar.button("退室", type="secondary"):
    st.session_state.authenticated = False
    st.rerun()

st.caption("Powered by Claude | SEO壁打ち部屋")
