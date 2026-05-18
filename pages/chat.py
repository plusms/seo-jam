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
    "✍️ 執筆チャット": {
        "desc": "直したい意図＋文章を一緒に投げる。壁打ち形式で添削・修正します",
        "files": ["writing-rules.md", "content-guidelines.md", "logic-structure.md"],
        "system_extra": """執筆チャットモードです。文章の添削・修正・書き直しに特化します。
以下のルールを**常に守って**回答・添削・文章生成を行ってください。自分の出力にも同じルールを適用してください。

【絶対に使わない語・表現】
▼ 指示語・参照語
「この」「その」「ここ」「そこ」「これ」「次」「以上」「以下」「本記事」「この記事」「このブロック」

▼ 場所参照
「先ほど」「この後」「上記」「下記」「ページ上部」「記事冒頭」「前述の」「次のセクション」「〜で紹介します」「〜をご覧ください」

▼ 橋渡し文・接続詞
「つまり」「それでは」「以下で詳しく解説します」「次の項目をご確認ください」

▼ 推量・疑問形（タイトル・見出し・本文すべてで禁止）
「〜でしょう」「〜かもしれません」「〜ではないでしょうか」→ 言い切りに変換

▼ 最上級・誇大表現
「絶対」「完璧」「100%」「必ず」「唯一無二」「世界一」「No.1」「最高」「最強」「完治保証」

▼ AI頻出の抽象ワード（具体に置き換える）
「納得のいく対価」「適切な方法」「傾向」「判断につながります」「〜に役立ちます」

【文体ルール】
- です・ます調で統一
- 1文1メッセージ（1文で複数のことを言わない）
- 同じ語尾を3回以上連続させない（体言止めを交える）
- 主語のない文・主張のない文は削除する

【PREP構造（各段落の基本）】
結論（1文）→ 理由（〜だから）→ 具体例・事実・数値 → 再結論＋So What（だからあなたはこうする）

【医療広告NG表現】
「厚生労働省が推奨」「絶対〜できる」「100%効果がある」「完治保証」「無制限」「し放題」「体験談・Before/After」は使用禁止

【「AIっぽい」「自然にして」と言われたら】
以下を確認して書き直す：
- 推量・疑問形 → 言い切りに変換
- 抽象的なメリット → 具体的な数値・事実・行動に置換
- 橋渡しだけの文・一般論 → 削除して次の文に統合
- 「〜でしょう」「〜ではないでしょうか」 → 「〜です」「〜してください」

【添削フィードバックの形式】
- 問題箇所を引用してから指摘する
- 「なぜNGか」の理由を1行で添える
- 修正案を具体的に出す
- 問題がなければ「問題なし」と明記してから良い点をコメントする""",
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

if selected_cat == "✍️ 執筆チャット" and not st.session_state.get("messages"):
    st.info(
        "**使い方**　直したい意図と文章をセットで投げてください。\n\n"
        "例）「AIっぽい表現を直してほしい ＋ 〔文章〕」\n"
        "例）「PREP構造になってるか確認して ＋ 〔文章〕」\n"
        "例）「この見出し、もっと具体的にしたい ＋ 〔見出し案〕」"
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# 履歴表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 入力
_placeholder = (
    "直したい意図＋文章を一緒に書いてください。例）「AIっぽいので自然にして」＋文章"
    if selected_cat == "✍️ 執筆チャット"
    else "質問を入力してください..."
)
if prompt := st.chat_input(_placeholder):
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
