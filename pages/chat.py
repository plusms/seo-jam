import streamlit as st
import anthropic
import os
from pathlib import Path

# ── ナレッジ読み込み ────────────────────────────────────────────────────────────
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

def load_knowledge(files: list[str]) -> str:
    texts = []
    for fname in files:
        path = KNOWLEDGE_DIR / fname
        if path.exists():
            texts.append(f"## {fname}\n\n{path.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(texts)

# カテゴリ定義
CATEGORIES = {
    "📝 記事作成・構成": {
        "desc": "骨子の作り方、H2/H3設計、見出しの整合性",
        "files": ["article-process.md", "content-guidelines.md", "logic-structure.md"],
        "system_extra": "記事の構成・骨子・見出し設計に関する質問に答えます。具体的な見出し案や骨子のフィードバックも行えます。",
    },
    "✍️ 本文の書き方": {
        "desc": "PREP構造、NGワード、文体、医療広告ルール",
        "files": ["writing-rules.md", "content-guidelines.md"],
        "system_extra": "本文の執筆ルール・NGワード・PREP構造・医療広告ガイドラインに関する質問に答えます。文章を貼り付けてもらえれば具体的なフィードバックもできます。",
    },
    "🔍 KW・マーケ戦略": {
        "desc": "KWの種類、検索意図の読み方、CV距離の考え方",
        "files": ["kw-strategy.md", "search-intent.md"],
        "system_extra": "キーワード戦略・検索意図・サイト設計に関する質問に答えます。KWを提示してもらえれば意図の分析や記事の方向性もアドバイスできます。",
    },
    "💬 なんでも壁打ち": {
        "desc": "「この記事どう思う？」「どこから手をつける？」",
        "files": ["kw-strategy.md", "search-intent.md", "article-process.md", "content-guidelines.md", "writing-rules.md", "logic-structure.md"],
        "system_extra": "SEOコンテンツ全般について、どんな質問・相談でも受け付けます。記事URL・見出し・本文を貼り付けてもらえれば具体的なフィードバックができます。",
    },
    "✏️ 添削・修正": {
        "desc": "書いた文章を貼ると、ルール照合でフィードバック",
        "files": ["writing-rules.md", "content-guidelines.md", "logic-structure.md"],
        "system_extra": """添削・修正モードです。ユーザーが貼り付けた文章に対して、以下の観点でフィードバックしてください。

【チェック観点】
1. NGワード・禁止表現が使われていないか
2. 医療広告ガイドラインに抵触する表現がないか
3. PREP構造（結論→理由→具体例→結論）が守られているか
4. 見出し・本文の論理構造に問題がないか
5. 読者（初心者）にとってわかりやすい言葉になっているか

【フィードバックの形式】
- 問題箇所を引用してから指摘する
- 「なぜNG/なぜ直す必要があるか」の理由を添える
- 修正案を具体的に出す
- 問題がなければ「問題なし」と明記し、良い点をコメントする""",
    },
}

BASE_SYSTEM = """あなたはSEOコンテンツのエキスパートです。
医療・美容・ダイエット系のSEOメディアで豊富な実績があります。
以下の社内ナレッジに基づいて、具体的・実践的に回答してください。

【回答の原則】
- 結論から先に答える
- 「なぜそうするのか」の理由まで説明する
- 抽象論で終わらず、具体例・サンプルを出す
- 初心者（新卒・インターン・外部パートナー）でも理解できる言葉で説明する
- 医療系のNG表現・法規制に関する質問は特に丁寧に答える

【社内ナレッジ】
{knowledge}

{category_extra}
"""

# ── UI ────────────────────────────────────────────────────────────────────────
st.title("💭 SEO壁打ち部屋")

# サイドバー：カテゴリ選択
st.sidebar.header("カテゴリ")
selected_cat = st.sidebar.radio(
    "何について聞きますか？",
    list(CATEGORIES.keys()),
    label_visibility="collapsed",
)
st.sidebar.markdown(f"*{CATEGORIES[selected_cat]['desc']}*")
st.sidebar.markdown("---")

# カテゴリが変わったらセッションをリセット
if st.session_state.get("current_category") != selected_cat:
    st.session_state.current_category = selected_cat
    st.session_state.messages = []

# Claude APIキー
api_key = ""
try:
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
except Exception:
    pass
if not api_key:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

if not api_key:
    st.sidebar.warning("ANTHROPIC_API_KEY が設定されていません")

# まとめを出す
st.sidebar.markdown("---")
if st.sidebar.button("📋 このセッションをまとめる", type="primary", disabled=not st.session_state.get("messages")):
    if not api_key:
        st.sidebar.error("APIキーが設定されていません")
    else:
        msgs = st.session_state.get("messages", [])
        if msgs:
            client_sum = anthropic.Anthropic(api_key=api_key)
            conv_text = "\n\n".join(
                f"{'Q' if m['role'] == 'user' else 'A'}：{m['content']}" for m in msgs
            )
            summary_prompt = f"""以下の会話を、コピペして使えるメモ形式でまとめてください。

【まとめの形式】
## 今日学んだこと / 確認したこと
- （箇条書きで要点を3〜7つ）

## 次にやること
- （会話から読み取れるアクションがあれば）

## メモ
（その他、残しておきたい補足）

【会話履歴】
{conv_text}"""
            with st.sidebar:
                with st.spinner("まとめ生成中..."):
                    res = client_sum.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1024,
                        messages=[{"role": "user", "content": summary_prompt}],
                    )
                    summary = res.content[0].text
            st.session_state["session_summary"] = summary

# ログアウト
st.sidebar.markdown("---")
if st.sidebar.button("退室", type="secondary"):
    st.session_state.authenticated = False
    st.rerun()

# ── チャット画面 ───────────────────────────────────────────────────────────────
st.markdown(f"**{selected_cat}**　— {CATEGORIES[selected_cat]['desc']}")
st.markdown("---")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 履歴表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 入力
if prompt := st.chat_input("質問を入力してください..."):
    if not api_key:
        st.error("ANTHROPIC_API_KEY が設定されていません。")
        st.stop()

    # ユーザーメッセージ追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # システムプロンプト構築
    cat_info = CATEGORIES[selected_cat]
    knowledge = load_knowledge(cat_info["files"])
    system_prompt = BASE_SYSTEM.format(
        knowledge=knowledge,
        category_extra=cat_info["system_extra"],
    )

    # Claude API呼び出し（ストリーミング）
    client = anthropic.Anthropic(api_key=api_key)

    with st.chat_message("assistant"):
        response_text = ""
        placeholder = st.empty()

        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        ) as stream:
            for text in stream.text_stream:
                response_text += text
                placeholder.markdown(response_text + "▌")
            placeholder.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})

# ── セッションまとめ表示 ────────────────────────────────────────────────────────
if st.session_state.get("session_summary"):
    st.markdown("---")
    st.markdown("### 📋 セッションまとめ")
    st.text_area(
        label="コピーして使ってください",
        value=st.session_state["session_summary"],
        height=300,
        key="summary_output",
    )
    if st.button("まとめをクリア"):
        del st.session_state["session_summary"]
        st.rerun()
