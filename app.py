import streamlit as st
import google.generativeai as genai
import time

# --- 1. 页面配置：黑客帝国风格 (V3.1 FIX) ---
st.set_page_config(
    page_title="VANGUARD | Xeno-Archives",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入 CSS：黑底绿字，CRT 显示器风格
st.markdown("""
<style>
    /* 全局背景 */
    .stApp { background-color: #0e1117; }
    
    /* 报告容器 */
    .report-container {
        font-family: 'Courier New', Courier, monospace;
        color: #33ff00; /* 骇客绿 */
        background-color: #000000;
        padding: 25px;
        border: 1px solid #33ff00;
        box-shadow: 0 0 15px rgba(51, 255, 0, 0.2);
        border-radius: 5px;
        line-height: 1.6;
        margin-top: 20px;
    }
    
    /* 警告框 */
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
    st.title("☢️ VANGUARD OS v3.1")
    st.caption("SECURE TERMINAL ACCESS")
    st.markdown("---")
    
    # 密码输入框
    api_key = st.text_input("🔑 ACCESS KEY (Google API):", type="password")
    
    st.markdown("### 📡 MISSION PARAMETERS")
    doc_type = st.selectbox("ARCHIVE TYPE", 
        ["NECROPSY_REPORT (尸检报告)", "AUDIO_TRANSCRIPT (录音记录)", "CONTAINMENT_PROTOCOL (收容协议)"])
    
    # 安全等级滑块
    clearance = st.select_slider("SECURITY CLEARANCE", options=["LEVEL 1", "LEVEL 2", "LEVEL 3", "OMNI-CLASSIFIED"])
    
    st.markdown("---")
    st.code("STATUS: CONNECTED\nLATENCY: 42ms\nENCRYPTION: AES-256", language="text")

# --- 3. 主界面 ---
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")
st.markdown("**INSTRUCTION:** Enter target entity description to retrieve secure documentation from the Vanguard Database.")

# 用户输入区
user_input = st.text_area("TARGET DESCRIPTION (e.g., Deep-sea worm mimicking voices):", height=100)
generate_btn = st.button("INITIATE RETRIEVAL PROTOCOL", type="primary")

# --- 4. 核心逻辑 (The Brain) ---
if generate_btn and user_input and api_key:
    try:
        # 配置 API
        genai.configure(api_key=api_key)
        
        # 🟢 修复点：使用标准的稳定版模型名称
        model = genai.GenerativeModel('gemini-1.5-pro') 
        
        # 🟢 沉浸式体验：模拟黑客解密动画
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        logs = [
            "Handshaking with Vanguard Server...",
            "Bypassing Firewall Layer 7...",
            "Decrypting Bio-Signature...",
            "Retrieving Corrupted Files...",
            "Compiling Final Dossier..."
        ]
        
        # 进度条动画
        for i, log in enumerate(logs):
            status_text.code(f">_ {log}")
            progress_bar.progress((i + 1) * 20)
            time.sleep(0.3) # 暂停 0.3 秒制造真实感
            
        # 清除进度条
        status_text.empty()
        progress_bar.empty()
        
        # --- 🧠 超级提示词工程 (Prompt Engineering) ---
        
        # 基础规则
        base_rules = f"""
        **SYSTEM ROLE**: You are the central computer of a secret paranormal organization 'Vanguard'.
        **USER INPUT**: "{user_input}"
        **SECURITY CLEARANCE**: {clearance}
        **OUTPUT FORMAT**: Markdown. Use horizontal rules (---) to separate sections.
        **MANDATORY**: Include a section at the very end called "TRANSLATED SUMMARY" in Chinese (中文简报).
        """

        # 分流逻辑
        if "NECROPSY" in doc_type:
            prompt = base_rules + """
            **MODE**: PATHOLOGY REPORT
            **AUTHOR**: Dr. Aris Thorne (Chief Xenopathologist)
            **TONE**: Cold, Visceral, Highly Technical.
            **CONTENT**:
            1. **HEADER**: ID, Date, Autopsy No.
            2. **VITAL METRICS TABLE**: Create a Markdown table with: pH Level, Tissue Density, Radioactivity (mSv).
            3. **GROSS ANATOMY**: Describe the texture using words like 'viscous', 'calcified', 'necrotic'.
            4. **ABNORMALITY**: Describe one organ that defies physics.
            5. **TOXICOLOGY**: List chemical compounds found in the blood.
            **STYLE**: Use code blocks for raw data.
            """

        elif "AUDIO" in doc_type:
            prompt = base_rules + """
            **MODE**: RECOVERED AUDIO TRANSCRIPT
            **SOURCE**: Damaged Black Box Recorder.
            **TONE**: Panic, Confusion, Screaming.
            **CONTENT**:
            1. **METADATA**: Recording duration, Noise floor level.
            2. **TRANSCRIPT**: Use specific timestamp format `[00:01:42]`.
            3. **SOUND EFFECTS**: Use *italics* for sounds like *[Wet tearing sound]*, *[Static interference]*.
            4. **THE CLIMAX**: The speaker must realize something horrifying right before the recording cuts off.
            5. **CORRUPTION**: Randomly insert `[DATA_CORRUPTED]` or `ERROR_Hex_5F` in the text.
            """

        else: # Containment Protocol
            prompt = base_rules + """
            **MODE**: CONTAINMENT PROTOCOL (SCP Style)
            **AUTHOR**: Overwatch Command.
            **TONE**: Authoritative, Bureaucratic, Zero Tolerance.
            **CONTENT**:
            1. **WARNING**: Start with a visual warning about "Cognitohazard".
            2. **CLASS**: Assign an esoteric class (e.g., KETER, APOLLYON).
            3. **SPECIAL PROCEDURES**: Numbered list. Be extremely specific (e.g., "Liquid Nitrogen at -200°C").
            4. **INCIDENT REPORT**: A brief summary of what happens if it escapes.
            **STYLE**: Use ⚠️ emojis for warnings. Use ALL CAPS for critical instructions.
            """

        # 开始生成
        with st.spinner('RENDERING FINAL DOCUMENT...'):
            response = model.generate_content(prompt)
        
        # --- 5. 结果展示 ---
        st.markdown('<div class="warning-box">⚠️ CLASSIFIED MATERIAL - DO NOT DISTRIBUTE</div>', unsafe_allow_html=True)
        
        # 显示生成的报告（应用黑客风格 CSS）
        st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
        
        # 下载按钮
        st.download_button(
            label="💾 DOWNLOAD ENCRYPTED FILE",
            data=response.text,
            file_name="vanguard_dossier.md",
            mime="text/markdown"
        )

    except Exception as e:
        st.error(f"❌ SYSTEM CRITICAL FAILURE: {e}")
        st.info("Try checking your API Key or Internet Connection.")

elif generate_btn and not api_key:
    st.error("⛔ ACCESS DENIED: MISSING API KEY (请在侧边栏输入密钥)")
