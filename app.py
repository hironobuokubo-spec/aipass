import streamlit as st
import google.generativeai as genai

# --- 初期設定 ---
st.set_page_config(page_title="生成AIパスポート2026攻略", layout="wide")
genai.configure(api_key="ここに取得したAPIキーを入れる")
model = genai.GenerativeModel('gemini-1.5-flash')

# --- アプリのUI ---
st.title("🎓 生成AIパスポート 2026年度版・学習アプリ")

tab1, tab2 = st.tabs(["📖 トピック学習", "❓ クイズ挑戦"])

# --- タブ1: トピック学習 ---
with tab1:
    topic = st.selectbox("学習したい項目を選んでください", 
                        ["AI新法とガイドライン", "RAGとAIエージェント", "著作権と知的財産権", "プロンプト設計手法"])
    
    if st.button("解説を生成"):
        with st.spinner("AIが解説を作成中..."):
            prompt = f"生成AIパスポート（2026年版）の受験者向けに、{topic}について重要ポイントを3点、初心者でもわかるように解説してください。"
            response = model.generate_content(prompt)
            st.markdown(response.text)

# --- タブ2: クイズ挑戦 ---
with tab2:
    if st.button("クイズを出題"):
        prompt = """生成AIパスポート（2026年版）のシラバスに基づき、4択問題を1問作成してください。
        【形式】
        問題文：
        A: 
        B: 
        C: 
        D: 
        正解：
        解説：
        (回答部分は折りたたみで見えないようにしてください)
        """
        response = model.generate_content(prompt)
        st.markdown(response.text)

st.sidebar.info("このアプリはGemini APIを使用して2026年試験向けにカスタマイズされています。")
