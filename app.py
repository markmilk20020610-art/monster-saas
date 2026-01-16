import streamlit as st
import google.generativeai as genai
import time

# --- 1. 页面配置：黑客帝国风格 (V3.2 STABLE) ---
st.set_page_config(
    page_title="VANGUARD | Xeno-Archives",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入 CSS：黑底绿字，CRT 显示器风格
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .report-container {
        font-family: 'Courier New', Courier, monospace;
        color: #33ff00;
        background-color: #000000;
        padding: 25px;
        border: 1px solid #33ff00;
        box-shadow: 0 0 15px rgba(51, 255, 0, 0.2);
        border-radius: 5px;
        line-height: 1.6;
        margin-top: 20px;
    }
    .warning-box {
        background-color: #330000;
        color: #ff3333;
        padding: 15px;
        border: 2px solid #ff0000;
        text-align: center;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 20px;
        animation: blink 2s infinite;
    }
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# --- 2. 侧边栏 ---
with st.sidebar:
    st.title("☢️ VANGUARD OS v3.2")
    st.caption("SECURE TERMINAL ACCESS")
    st.markdown("---")
    
    api_key = st.text_input("🔑 ACCESS KEY (Google API):", type="password")
    
    st.markdown("### 📡 MISSION PARAMETERS")
    doc_type = st.selectbox("ARCHIVE TYPE", 
        ["NECROPSY_REPORT (尸检报告)", "AUDIO_TRANSCRIPT (录音记录)", "CONTAINMENT_PROTOCOL (收容协议)"])
    
    clearance = st.select_slider("SECURITY CLEARANCE", options=["LEVEL 1", "LEVEL 2", "LEVEL 3", "OMNI-CLASSIFIED"])
    
    st.markdown("---")
    st.code("STATUS: CONNECTED\nLATENCY: 12ms\nENCRYPTION: AES-256", language="text")

# --- 3. 主界面 ---
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")
st.markdown("**INSTRUCTION:** Enter target entity description to retrieve secure documentation.")

user_input = st.text_area("TARGET DESCRIPTION (e.g., Deep-sea worm mimicking voices):", height=100)
generate_btn = st.button("INITIATE RETRIEVAL PROTOCOL", type="primary")

# --- 4. 核心逻辑 ---
if generate_btn and user_input and api_key:
    # 配置 API
    genai.configure(api_key=api_key)
    
    try:
        # 🟢 修复点：使用 'gemini-1.5-flash'，这是目前最通用的版本
        # 如果这个也报错，下方的 except 代码块会自动帮你查找可用的模型
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        # 🟢 模拟黑客解密动画
        status_text = st.empty()
        progress_bar = st.progress(0)
        logs = ["Handshaking with Vanguard Server...", "Bypassing Firewall Layer 7...", "Decrypting Bio-Signature...", "Compiling Final Dossier..."]
        
        for i, log in enumerate(logs):
            status_text.code(f">_ {log}")
            progress_bar.progress((i + 1) * 25)
            time.sleep(0.2)
            
        status_text.empty()
        progress_bar.empty()
        
        # --- 🧠 Prompt Engineering ---
        base_rules = f"""
        **SYSTEM ROLE**: Central computer of secret org 'Vanguard'.
        **USER INPUT**: "{user_input}"
        **SECURITY**: {clearance}
        **OUTPUT**: Markdown. 
        **MANDATORY**: End with 'TRANSLATED SUMMARY' in Chinese.
        """

        if "NECROPSY" in doc_type:
            prompt = base_rules + """
            **MODE**: PATHOLOGY REPORT. Author: Dr. Aris Thorne. Tone: Cold, Clinical.
            **CONTENT**: Header (ID, Date), Vital Metrics Table (pH, Density), Gross Anatomy (Texture), Abnormality, Toxicology.
            """
        elif "AUDIO" in doc_type:
            prompt = base_rules + """
            **MODE**: AUDIO TRANSCRIPT. Source: Black Box. Tone: Panic.
            **CONTENT**: Metadata, Timestamped Transcript [00:01:XX], Sound Effects *[text]*, Corrupted Data [ERROR].
            """
        else:
            prompt = base_rules + """
            **MODE**: SCP STYLE PROTOCOL. Tone: Bureaucratic.
            **CONTENT**: WARNING BOX, CLASS (KETER/EUCLID), PROCEDURES (Numbered), INCIDENT SUMMARY.
            """

        with st.spinner('RENDERING FINAL DOCUMENT...'):
            response = model.generate_content(prompt)
        
        # 结果展示
        st.markdown('<div class="warning-box">⚠️ CLASSIFIED MATERIAL - DO NOT DISTRIBUTE</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
        st.download_button("💾 DOWNLOAD ENCRYPTED FILE", response.text, "vanguard_dossier.md")

    except Exception as e:
        # 🔴 自动诊断逻辑：如果出错，打印错误并尝试列出可用模型
        st.error(f"❌ CONNECTION ERROR: {e}")
        st.warning("⚠️ 正在尝试自动诊断可用模型，请查看下方列表：")
        try:
            st.write("您的 API Key 支持以下模型（请将其中一个名字告诉开发者）：")
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    st.code(m.name)
        except:
            st.error("无法连接 Google 服务器。请检查您的网络或 API Key 是否正确。")

elif generate_btn and not api_key:
    st.error("⛔ ACCESS DENIED: Please enter your API Key in the sidebar.")
