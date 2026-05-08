import streamlit as st
import random
import datetime
import pandas as pd
import google.generativeai as genai
import json
import os
import time

# --- 1. データの読み込み ---
def load_data():
    path = "data/questions.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"questions": [], "topics": []}

data = load_data()
QUESTIONS = data["questions"]

# --- 2. API設定 ---
if "api_key" in st.secrets:
    genai.configure(api_key=st.secrets["api_key"])
    model = genai.GenerativeModel('gemini-2.0-flash')
else:
    st.error("APIキーをSecretsに設定してください。")

# --- 3. ページ設定 & スマホ最適化CSS ---
st.set_page_config(page_title="生成AIパスポート攻略", page_icon="🎓")
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 15px; height: 3.5em; font-weight: bold; margin-top: 10px; }
    .stAlert { border-radius: 15px; }
    div[data-testid="stExpander"] { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. セッション状態の初期化 ---
if 'history' not in st.session_state: st.session_state.history = []
if 'review_list' not in st.session_state: st.session_state.review_list = set()
if 'exam_active' not in st.session_state: st.session_state.exam_active = False

# --- 5. メインナビゲーション ---
tab_home, tab_cat, tab_review, tab_exam = st.tabs(["🏠 ホーム", "📂 カテゴリ", "📚 復習", "⏱ 模試"])

# --- 【機能1】🏠 ホーム画面 ---
with tab_home:
    st.title("🎓 生成AIパスポート対策")
    days_left = (datetime.date(2026, 6, 15) - datetime.date.today()).days
    st.metric("2026年6月試験まで", f"あと {days_left} 日")

    # AI自動トピック生成
    if "daily_topic" not in st.session_state:
        with st.spinner("今日のAIトピックを生成中..."):
            try:
                res = model.generate_content("生成AIパスポート試験向けの重要語句を1つ選び、キーワードと3行解説を書いて。")
                st.session_state.daily_topic = res.text
            except:
                st.session_state.daily_topic = "AIが混雑しています。リロードしてください。"
    st.info(st.session_state.daily_topic)
    if st.button("🔄 別のトピックを生成"):
        del st.session_state.daily_topic
        st.rerun()

# --- 【機能2】📂 カテゴリ別演習 ---
with tab_cat:
    st.subheader("📂 カテゴリ別演習")
    if QUESTIONS:
        cats = list(set([q['category'] for q in QUESTIONS]))
        selected_cat = st.selectbox("分野を選択", cats)
        cat_qs = [q for q in QUESTIONS if q['category'] == selected_cat]
        
        st.write(f"全 {len(cat_qs)} 問中")
        
        # 問題表示（セッションで管理）
        cat_key = f"idx_{selected_cat}"
        if cat_key not in st.session_state: st.session_state[cat_key] = 0
        
        idx = st.session_state[cat_key]
        if idx < len(cat_qs):
            q = cat_qs[idx]
            st.markdown(f"**Q. {q['question']}**")
            ans = st.radio("選択肢", q['choices'], key=f"cat_rad_{selected_cat}_{idx}")
            
            if st.button("回答をチェック", key=f"cat_btn_{idx}"):
                if q['choices'].index(ans) == q['correct']:
                    st.success("正解！ " + q['explanation'])
                else:
                    st.error("不正解。解説: " + q['explanation'])
                    st.session_state.review_list.add(q['id'])
                
                if st.button("次の問題へ"):
                    st.session_state[cat_key] += 1
                    st.rerun()
        else:
            st.success("このカテゴリの全問題が終了しました！")
            if st.button("最初から解く"):
                st.session_state[cat_key] = 0
                st.rerun()

# --- 【機能3】📚 復習リスト ---
with tab_review:
    st.subheader("📚 復習リスト")
    if not st.session_state.review_list:
        st.write("復習が必要な問題はありません。")
    else:
        for rid in list(st.session_state.review_list):
            q_data = next((q for q in QUESTIONS if q['id'] == rid), None)
            if q_data:
                with st.expander(f"【{q_data['category']}】 {q_data['question'][:20]}..."):
                    st.write(q_data['question'])
                    st.write(f"**正解:** {q_data['choices'][q_data['correct']]}")
                    st.write(f"**解説:** {q_data['explanation']}")
                    if st.button("覚えた！", key=f"clr_{rid}"):
                        st.session_state.review_list.remove(rid)
                        st.rerun()

# --- 【機能4】⏱ 模擬試験モード ---
with tab_exam:
    st.subheader("⏱ 模擬試験 (デモ版)")
    if not st.session_state.exam_active:
        st.write("ランダムに出題される模擬試験に挑戦します。")
        if st.button("試験開始"):
            st.session_state.exam_active = True
            st.session_state.exam_start = time.time()
            st.session_state.exam_qs = random.sample(QUESTIONS, min(len(QUESTIONS), 60))
            st.session_state.exam_answers = {}
            st.rerun()
    else:
        elapsed = int(time.time() - st.session_state.exam_start)
        st.write(f"経過時間: {elapsed // 60}分 {elapsed % 60}秒 / 60分")
        
        for i, eq in enumerate(st.session_state.exam_qs):
            st.markdown(f"**第 {i+1} 問**")
            st.write(eq['question'])
            st.session_state.exam_answers[i] = st.radio("回答を選択", eq['choices'], key=f"ex_q_{i}")
            st.divider()
        
        if st.button("試験を終了して採点"):
            score = 0
            for i, eq in enumerate(st.session_state.exam_qs):
                if eq['choices'].index(st.session_state.exam_answers[i]) == eq['correct']:
                    score += 1
                else:
                    st.session_state.review_list.add(eq['id'])
            
            st.session_state.exam_active = False
            st.balloons()
            st.success(f"試験終了！ 正解数: {score} / {len(st.session_state.exam_qs)}")
            if st.button("ホームに戻る"):
                st.rerun()
