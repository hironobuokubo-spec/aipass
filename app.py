import streamlit as st
import random
import datetime
import pandas as pd
import google.generativeai as genai

# --- API設定 (Secretsから取得) ---
genai.configure(api_key=st.secrets["api_key"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- ページ設定 ---
st.set_page_config(page_title="生成AIパスポート2026攻略", page_icon="🎓")

# --- データの読み込み (JSONファイルがない場合のサンプル) ---
# 本来は data/questions.json から読み込む処理をここに入れます
QUESTIONS = [
    {"id": "Q1", "category": "ガバナンス", "question": "AI新法(2025年6月交付)の目的は？", "choices": ["規制のみ", "推進とリスク対応", "開発禁止", "課税"], "correct": 1, "explanation": "推進とリスク管理の両立が目的です。"},
    {"id": "Q2", "category": "技術", "question": "RAGの利点は？", "choices": ["高速化", "ハルシネーション抑制", "画像生成", "翻訳"], "correct": 1, "explanation": "外部知識を参照することで、嘘（ハルシネーション）を減らします。"}
]

# --- セッション状態の初期化 ---
if 'history' not in st.session_state: st.session_state.history = []
if 'review_list' not in st.session_state: st.session_state.review_list = set()

# --- サイドバー (ナビゲーション) ---
st.sidebar.title("メニュー")
menu = st.sidebar.radio("移動先", ["🏠 ホーム", "✍ 問題演習", "📚 復習リスト", "⏱ 模擬試験", "📊 学習分析"])

# --- 🏠 ホーム画面 (サクッと1問 & 毎日トピック) ---
if menu == "🏠 ホーム":
    st.title("🎓 学習コーチ")
    
    # 1. カウントダウン
    days_left = (datetime.date(2026, 6, 15) - datetime.date.today()).days
    st.metric("6月試験まであと", f"{days_left} 日")

    # 2. 今日の1分トピック (Geminiが生成)
    st.subheader("💡 今日の重点トピック")
    if st.button("AIに最新トピックを教えてもらう"):
        with st.spinner("生成中..."):
            res = model.generate_content("生成AIパスポート2026年試験に出そうな最新用語（RAGやAIエージェント、AI新法など）から1つ選んで、1分で読める解説を書いて。")
            st.info(res.text)

    # 3. ささっと1問
    st.subheader("⚡ ささっと1問")
    q = random.choice(QUESTIONS)
    st.write(q['question'])
    ans = st.radio("答えを選択", q['choices'], key="quick_q")
    if st.button("回答チェック"):
        if q['choices'].index(ans) == q['correct']:
            st.success("正解！ " + q['explanation'])
        else:
            st.error("残念... 解説: " + q['explanation'])
            st.session_state.review_list.add(q['id'])

# --- ✍ 問題演習 (PRD: カテゴリ別など) ---
elif menu == "✍ 問題演習":
    st.title("📝 問題演習")
    category = st.selectbox("カテゴリ選択", ["すべて", "生成AI基礎", "活用技術", "法律・倫理"])
    # 演習ロジックをここに実装...
    st.write("カテゴリ別の問題が表示されます（開発中）")

# --- 📚 復習リスト (PRD: 間違えた問題) ---
elif menu == "📚 復習リスト":
    st.title("🔍 弱点克服")
    if not st.session_state.review_list:
        st.write("復習が必要な問題はありません！完璧です。")
    else:
        for q_id in list(st.session_state.review_list):
            st.warning(f"問題ID: {q_id} がリストにあります。")

# --- ⏱ 模擬試験 (PRD: 60問/60分) ---
elif menu == "⏱ 模擬試験":
    st.title("🏁 模擬試験モード")
    st.write("本番と同じ60問・60分で挑戦します。")
    if st.button("試験開始"):
        st.session_state.start_time = datetime.datetime.now()
        st.info("タイマー開始しました。")

# --- 📊 学習分析 ---
elif menu == "📊 学習分析":
    st.title("📈 学習レポート")
    st.write("これまでの正答率や傾向を分析します。")
