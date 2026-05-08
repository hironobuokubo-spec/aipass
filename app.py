import streamlit as st
import random
import datetime
import pandas as pd

# --- ページ設定 ---
st.set_page_config(page_title="GenAI Passport 2026 攻略", page_icon="🎓", layout="centered")

# --- カスタムCSS (スマホ最適化) ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #0F172A; color: white; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #f1f5f9; border-radius: 10px 10px 0 0; padding: 10px 20px; }
    .card { background-color: white; padding: 20px; border-radius: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); margin-bottom: 20px; border: 1px solid #e2e8f0; }
    .correct { color: #10b981; font-weight: bold; }
    .wrong { color: #ef4444; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 初期データ (2026年シラバス準拠) ---
QUESTIONS = [
    {
        "id": "Q1", "category": "ガバナンス・法令", "difficulty": "standard",
        "question": "2025年6月に交付された「AI新法」における、事業者の主な義務は次のうちどれか？",
        "choices": ["AIの完全な利用停止義務", "特定のリスクに対する協力義務と透明性の確保", "すべてのAI生成物への課税", "AI開発の事前許可制"],
        "correct": 1, "explanation": "AI新法は、推進とリスク対応の両立を図るもので、事業者に重大なリスクへの対応協力や透明性の確保を求めています。"
    },
    {
        "id": "Q2", "category": "活用技術", "difficulty": "basic",
        "question": "ハルシネーションを抑制するために、外部の信頼できる情報を検索して回答を生成する仕組みを何と呼ぶか？",
        "choices": ["RLHF", "GAN", "RAG", "Fine-tuning"],
        "correct": 2, "explanation": "RAG (Retrieval-Augmented Generation) は検索拡張生成と呼ばれ、外部知識を回答に組み込む手法です。"
    },
    {
        "id": "Q3", "category": "活用技術", "difficulty": "advanced",
        "question": "AIエージェントが外部ツールやAPIと接続するための標準プロトコルの名称は？",
        "choices": ["REST API", "MCP (Model Context Protocol)", "gRPC", "JSON-RPC"],
        "correct": 1, "explanation": "2026年シラバスで重要視されるMCPは、モデルと外部データの連携を標準化する仕組みです。"
    }
    # 実際にはここに30問以上のデータを追加
]

# --- セッション状態の初期化 ---
if 'history' not in st.session_state:
    st.session_state.history = []
if 'review_list' not in st.session_state:
    st.session_state.review_list = set()
if 'current_exam' not in st.session_state:
    st.session_state.current_exam = None

# --- アプリ画面構成 ---
tab_home, tab_practice, tab_review, tab_exam, tab_stats = st.tabs(["🏠 ホーム", "✍ 演習", "📚 復習", "⏱ 模試", "📊 分析"])

# --- ホーム画面 ---
with tab_home:
    st.title("GenAI Passport 2026 攻略")
    st.markdown(f"""
    <div class="card">
        <h3>🎯 学習進捗</h3>
        <p>試験日（6月15日想定）まで残り <b>{(datetime.date(2026, 6, 15) - datetime.date.today()).days}日</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("総回答数", len(st.session_state.history))
    with col2:
        st.metric("復習待ち", len(st.session_state.review_list))

    if st.button("今日の10問を解く"):
        st.info("演習タブに移動して開始してください")

# --- 演習画面 ---
with tab_practice:
    st.subheader("今日の10問")
    q_idx = st.session_state.get('q_idx', 0)
    
    if q_idx < 3: # デモ用に3問
        q = QUESTIONS[q_idx]
        st.markdown(f"**第 {q_idx+1} 問** / カテゴリ: {q['category']}")
        st.write(q['question'])
        
        answer = st.radio("選択肢を選んでください", q['choices'], key=f"q_{q_idx}")
        
        if st.button("回答する", key=f"btn_{q_idx}"):
            is_correct = (q['choices'].index(answer) == q['correct'])
            if is_correct:
                st.success("正解！ " + q['explanation'])
            else:
                st.error("不正解... 解説: " + q['explanation'])
                st.session_state.review_list.add(q['id'])
            
            # 履歴追加
            st.session_state.history.append({"id": q['id'], "correct": is_correct})
            st.session_state.q_idx = q_idx + 1
            st.rerun()
    else:
        st.success("本日の演習は完了です！")
        if st.button("もう一度最初から"):
            st.session_state.q_idx = 0
            st.rerun()

# --- 復習画面 ---
with tab_review:
    st.subheader("復習が必要な問題")
    if not st.session_state.review_list:
        st.write("現在、復習リストは空です。素晴らしい！")
    else:
        for q_id in list(st.session_state.review_list):
            q_data = next(item for item in QUESTIONS if item["id"] == q_id)
            with st.expander(f"問題: {q_data['question'][:20]}..."):
                st.write(q_data['question'])
                st.write(f"正解: {q_data['choices'][q_data['correct']]}")
                if st.button("理解した（リストから削除）", key=f"del_{q_id}"):
                    st.session_state.review_list.remove(q_id)
                    st.rerun()

# --- 模擬試験 ---
with tab_exam:
    st.subheader("模擬試験モード (60問/60分)")
    st.warning("本番形式での演習です。途中で中断できません。")
    if st.button("模試を開始する"):
        st.write("（※現在デモ版のため準備中です。問題データを順次追加してください）")

# --- 分析画面 ---
with tab_stats:
    st.subheader("学習履歴分析")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        correct_rate = df['correct'].mean() * 100
        st.write(f"現在の総合正答率: **{correct_rate:.1f}%**")
        st.line_chart(df['correct'].astype(int))
    else:
        st.write("データがまだありません。")

