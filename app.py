import streamlit as st
import random
import datetime
import pandas as pd
import google.generativeai as genai
import json
import os

# --- データの読み込み関数 ---
def load_data():
    # data/questions.json ファイルを探して読み込む
    path = "data/questions.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # ファイルがない場合の予備データ
        return {"questions": [], "topics": []}

data = load_data()
QUESTIONS = data["questions"]
TOPICS = data["topics"]

# --- API設定 (Secrets) ---
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("APIキーが設定されていません。StreamlitのSettings > Secretsを確認してください。")

# --- ページ設定 ---
st.set_page_config(page_title="生成AIパスポート2026攻略", page_icon="🎓")

# --- セッション状態の初期化 ---
if 'history' not in st.session_state: st.session_state.history = []
if 'review_list' not in st.session_state: st.session_state.review_list = set()

# --- サイドバーナビゲーション ---
st.sidebar.title("学習メニュー")
menu = st.sidebar.radio("機能を選択", ["🏠 ホーム", "✍ 問題演習", "📚 復習リスト", "📊 学習分析"])

# --- 🏠 ホーム画面 ---
if menu == "🏠 ホーム":
    st.title("🎓 生成AIパスポート対策")
    
    # 試験日までのカウントダウン
    days_left = (datetime.date(2026, 6, 15) - datetime.date.today()).days
    st.metric("2026年6月試験まで", f"あと {days_left} 日")

    # 今日のトピックス (JSONから1つ表示)
    st.subheader("💡 今日の重点トピック")
    if TOPICS:
        topic = random.choice(TOPICS)
        st.info(f"**{topic['title']}**\n\n{topic['content']}")
    
    # AIへの質問ボタン
    if st.button("✨ AIに最新トレンドを聞く"):
        with st.spinner("AIが思考中..."):
            res = model.generate_content("生成AIパスポート試験（2026年）に向けて、今日覚えておくべき重要キーワードを1つ選んで、3行で解説してください。")
            st.success(res.text)

    # ささっと1問
    st.divider()
    st.subheader("⚡ 1問1答")
    if QUESTIONS:
        if 'quick_q' not in st.session_state:
            st.session_state.quick_q = random.choice(QUESTIONS)
        
        q = st.session_state.quick_q
        st.write(f"**[{q['category']}]** {q['question']}")
        ans = st.radio("答えを選択", q['choices'], key="radio_quick")
        
        if st.button("回答をチェック"):
            if q['choices'].index(ans) == q['correct']:
                st.success(f"正解！ 🎉\n\n{q['explanation']}")
            else:
                st.error(f"不正解... 😢\n\n正解は「{q['choices'][q['correct']]}」です。\n\n{q['explanation']}")
                st.session_state.review_list.add(q['id'])
            # 次の問題ボタンを表示
            if st.button("次の問題をセット"):
                del st.session_state.quick_q
                st.rerun()

# --- ✍ 問題演習 ---
elif menu == "✍ 問題演習":
    st.title("📝 カテゴリ別演習")
    if QUESTIONS:
        categories = ["すべて"] + list(set([q['category'] for q in QUESTIONS]))
        selected_cat = st.selectbox("カテゴリを選択", categories)
        st.info("ここに選択したカテゴリの問題が順番に表示される機能を実装予定です。")
    else:
        st.warning("問題データが見つかりません。data/questions.jsonを確認してください。")

# --- 📚 復習リスト ---
elif menu == "📚 復習リスト":
    st.title("🔍 弱点克服")
    if not st.session_state.review_list:
        st.success("現在、復習が必要な問題はありません！この調子です。")
    else:
        for q_id in list(st.session_state.review_list):
            q_data = next((q for q in QUESTIONS if q['id'] == q_id), None)
            if q_data:
                with st.expander(f"問題: {q_data['question'][:20]}..."):
                    st.write(f"**問題:** {q_data['question']}")
                    st.write(f"**正解:** {q_data['choices'][q_data['correct']]}")
                    st.write(f"**解説:** {q_data['explanation']}")
                    if st.button("克服した！", key=f"clear_{q_id}"):
                        st.session_state.review_list.remove(q_id)
                        st.rerun()

# --- 📊 学習分析 ---
elif menu == "📊 学習分析":
    st.title("📈 学習レポート")
    st.write("日々の正答率や学習時間をグラフ化する準備をしています。")
