import streamlit as st
import google.generativeai as genai
import time

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="VANGUARD | Xeno-Archives",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入 CSS：黑底绿字
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
    st.title("☢️ VANGUARD OS v3.4")
    st.caption("CORE: GEMINI FLASH (STABLE)")
    st.markdown("---")
    
    api_key = st.text_input("🔑 ACCESS KEY:", type="password")
    
    st.markdown("### 📡 MISSION PARAMETERS")
    doc_type = st.selectbox("ARCHIVE TYPE", 
        ["NECROPSY_REPORT (尸检报告)", "AUDIO_TRANSCRIPT (录音记录)", "CONTAINMENT_PROTOCOL (收容协议)"])
    
    clearance = st.select_slider("SECURITY CLEARANCE", options=["LEVEL 1", "LEVEL 2", "LEVEL 3", "OMNI-CLASSIFIED"])
    
    st.markdown("---")
    st.code("STATUS: ONLINE\nQUOTA: UNLIMITED\nENCRYPTION: AES-256", language="text")

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
        # 🟢 修复点：使用你列表中最稳、额度最高的 'gemini-flash-latest'
        # 这个模型每分钟允许请求 15 次以上，几乎不会报错
        model = genai.GenerativeModel('gemini-flash-latest') 
        
        # 🟢 模拟黑客解密动画
        status_text = st.empty()
        progress_bar = st.progress(0)
        logs = ["Rerouting to High-Speed Node...", "Bypassing Firewall...", "Decrypting Bio-Signature...", "Compiling Final Dossier..."]
        
        for i, log in enumerate(logs):
            status_text.code(f">_ {log}")
            progress_bar.progress((i + 1) * 25)
            time.sleep(0.1) # 加快一点速度
            
        status_text.empty()
        progress_bar.empty()
        
        # --- 🧠 Prompt Engineering ---
        base_rules = f"""
        **SYSTEM ROLE**: You are the central computer of a secret paranormal organization 'Vanguard'.
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
        # 如果还是报错，说明你需要休息1分钟
        st.error(f"❌ OVERLOAD: {e}")
        if "429" in str(e):
            st.warning("⚠️ 系统过热（配额耗尽）。请喝口水，等待 60 秒后再试，Google 会自动重置你的免费额度。")

elif generate_btn and not api_key:
    st.error("⛔ ACCESS DENIED: Please enter your API Key in the sidebar.")
