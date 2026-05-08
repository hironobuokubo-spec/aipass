import streamlit as st
import random
import datetime
import pandas as pd
import google.generativeai as genai
import json
import os

# --- データの読み込み ---
def load_data():
    path = "data/questions.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"questions": [], "topics": []}

data = load_data()
QUESTIONS = data["questions"]
TOPICS = data["topics"]

# --- API設定 ---
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
    model = genai.GenerativeModel('gemini-2.0-flash') # 最新の2.0に変更
else:
    st.error("APIキーをSecretsに設定してください。")

# --- 📱 スマホ最適化CSS ---
st.markdown("""
    <style>
    /* ボタンを大きく押しやすく */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 3.5em;
        font-weight: bold;
        margin-top: 10px;
    }
    /* カード風の見た目 */
    .stAlert {
        border-radius: 15px;
    }
    /* ラジオボタン（選択肢）の間隔を広げる */
    div[data-testid="stMarkdownContainer"] > p {
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ページ設定 ---
st.set_page_config(page_title="生成AIパスポート攻略", page_icon="🎓")

# --- ナビゲーション（スマホでは上部に配置するのもアリですが、今回はタブで実装） ---
tab_home, tab_quiz, tab_review = st.tabs(["🏠 ホーム", "✍ 演習", "📚 復習"])

# --- 🏠 ホーム画面 ---
with tab_home:
    st.title("🎓 学習コーチ")
    days_left = (datetime.date(2026, 6, 15) - datetime.date.today()).days
    st.metric("6月試験まで", f"あと {days_left} 日")

    st.subheader("💡 今日のAI生成トピック")
    
    # アプリを開いた時（またはリロード時）に1回だけ自動生成する
    if "daily_topic" not in st.session_state:
        with st.spinner("AIが今日のトピックを作成中..."):
            try:
                prompt = "生成AIパスポート試験（2026年版）に出題されそうな重要キーワードを1つ選び、「【キーワード名】」という見出しのあとに、初心者向けに3行で解説してください。"
                res = model.generate_content(prompt)
                st.session_state.daily_topic = res.text
            except Exception as e:
                st.session_state.daily_topic = "現在AIがお休み中です。少し時間を置いて再読み込みしてください。"

    # 生成されたトピックを表示
    st.info(st.session_state.daily_topic)

    # 別のトピックを読みたい場合の手動更新ボタン
    if st.button("🔄 別のトピックを生成する"):
        del st.session_state.daily_topic
        st.rerun()

# --- ✍ 演習画面 ---
with tab_quiz:
    st.subheader("⚡ 1問1答")
    if QUESTIONS:
        if 'q' not in st.session_state:
            st.session_state.q = random.choice(QUESTIONS)
        
        q = st.session_state.q
        st.markdown(f"**【{q['category']}】**")
        st.write(q['question'])
        
        ans = st.radio("答えを選択", q['choices'], key="quiz_radio")
        
        if st.button("回答をチェック"):
            if q['choices'].index(ans) == q['correct']:
                st.success(f"正解！\n\n{q['explanation']}")
            else:
                st.error(f"正解は：{q['choices'][q['correct']]}\n\n{q['explanation']}")
                st.session_state.setdefault('review_list', set()).add(q['id'])
            
            if st.button("次の問題へ"):
                st.session_state.q = random.choice(QUESTIONS)
                st.rerun()

# --- 📚 復習画面 ---
with tab_review:
    st.subheader("🔍 弱点克服")
    reviews = st.session_state.get('review_list', set())
    if not reviews:
        st.write("復習リストは空です！")
    else:
        for rid in list(reviews):
            q_data = next((q for q in QUESTIONS if q['id'] == rid), None)
            if q_data:
                with st.expander(q_data['question'][:20] + "..."):
                    st.write(q_data['question'])
                    st.write(f"正解：{q_data['choices'][q_data['correct']]}")
                    if st.button("覚えた！", key=f"clear_{rid}"):
                        st.session_state.review_list.remove(rid)
                        st.rerun()
