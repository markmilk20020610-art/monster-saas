import streamlit as st
import google.generativeai as genai
import time

# --- 1. 页面配置：黑客帝国风格 ---
st.set_page_config(
    page_title="VANGUARD | Xeno-Archives",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入 CSS：让字体看起来像 80 年代的 CRT 显示器，带微弱发光效果
st.markdown("""
<style>
    .report-container {
        font-family: 'Courier New', monospace;
        color: #33ff00; /* 骇客绿 */
        background-color: #000000;
        padding: 25px;
        border: 1px solid #33ff00;
        box-shadow: 0 0 10px #33ff00;
        border-radius: 5px;
        line-height: 1.6;
    }
    .warning-box {
        background-color: #330000;
        color: #ff3333;
        padding: 10px;
        border: 1px solid #ff0000;
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .stApp { background-color: #0e1117; }
</style>
""", unsafe_allow_html=True)

# --- 2. 侧边栏 ---
with st.sidebar:
    st.title("☢️ VANGUARD OS v3.1")
    st.markdown("---")
    
    api_key = st.text_input("🔑 ACCESS KEY (Google API):", type="password")
    
    st.markdown("### 📡 MISSION PARAMETERS")
    doc_type = st.selectbox("ARCHIVE TYPE", 
        ["NECROPSY_REPORT (尸检)", "AUDIO_TRANSCRIPT (录音)", "CONTAINMENT_PROTOCOL (收容)"])
    
    # 增加更多细节选项，让用户觉得自己在控制复杂的系统
    clearance = st.select_slider("SECURITY CLEARANCE", options=["LEVEL 1", "LEVEL 2", "LEVEL 3", "OMNI-CLASSIFIED"])
    
    st.markdown("---")
    st.caption("SERVER STATUS: CONNECTED\nLATENCY: 42ms\nENCRYPTION: AES-256")

# --- 3. 主界面 ---
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")
st.markdown("Enter target entity parameters to retrieve secure documentation.")

user_input = st.text_area("TARGET DESCRIPTION (e.g., Deep-sea worm mimicking voices):", height=100)
generate_btn = st.button("INITIATE RETRIEVAL PROTOCOL", type="primary")

# --- 4. 核心逻辑 ---
if generate_btn and user_input and api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest') 
        
        # 🟢 沉浸式体验：模拟黑客解密过程
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        logs = [
            "Handshaking with Vanguard Server...",
            "Bypassing Firewall Layer 7...",
            "Decrypting Bio-Signature...",
            "Retrieving Corrupted Files...",
            "Compiling Final Dossier..."
        ]
        
        for i, log in enumerate(logs):
            status_text.text(f">_ {log}")
            progress_bar.progress((i + 1) * 20)
            time.sleep(0.3) # 故意暂停一下，制造紧张感
            
        status_text.empty()
        progress_bar.empty()
        
        # --- 🧠 V3.0 超级提示词工程 ---
        
        # 公共规则 (所有模式通用)
        base_rules = f"""
        **SYSTEM INSTRUCTION**: You are the central computer of a secret paranormal organization.
        **USER INPUT**: "{user_input}"
        **SECURITY LEVEL**: {clearance}
        **OUTPUT FORMAT**: Markdown. Use horizontal rules (---) to separate sections.
        **MANDATORY**: Include a section at the very end called "TRANSLATED SUMMARY" in Chinese (中文简报).
        """

        # 模式 A: 尸检 (增加生化表格)
        if "NECROPSY" in doc_type:
            prompt = base_rules + """
            **MODE**: PATHOLOGY REPORT
            **AUTHOR**: Dr. Aris Thorne (Chief Xenopathologist)
            **TONE**: Cold, Visceral, Highly Technical.
            
            **CONTENT REQUIREMENTS**:
            1. **HEADER**: ID, Date, Autopsy No.
            2. **VITAL METRICS TABLE**: Create a Markdown table with specific numbers for: pH Level, Tissue Density, Radioactivity (mSv), Unknown Isotopes.
            3. **GROSS ANATOMY**: Describe the texture using words like 'viscous', 'calcified', 'necrotic'.
            4. **ABNORMALITY**: Describe one organ that defies physics.
            5. **TOXICOLOGY**: List chemical compounds found in the blood.
            
            **STYLE**: Use code blocks for raw data. Use bold for key findings.
            """

        # 模式 B: 录音 (增加时间戳和环境音)
        elif "AUDIO" in doc_type:
            prompt = base_rules + """
            **MODE**: RECOVERED AUDIO TRANSCRIPT
            **SOURCE**: Damaged Black Box Recorder.
            **TONE**: Panic, Confusion, Screaming.
            
            **CONTENT REQUIREMENTS**:
            1. **METADATA**: Recording duration, Noise floor level.
            2. **TRANSCRIPT**: Use specific timestamp format `[00:01:42]`.
            3. **SOUND EFFECTS**: Use *italics* for sounds like *[Wet tearing sound]*, *[Static interference]*, *[Inhuman screeching]*.
            4. **THE CLIMAX**: The speaker must realize something horrifying right before the recording cuts off.
            5. **CORRUPTION**: Randomly insert `[DATA_CORRUPTED]` or `ERROR_Hex_5F` in the text.
            """

        # 模式 C: 收容 (增加各种图标和警告)
        else:
            prompt = base_rules + """
            **MODE**: CONTAINMENT PROTOCOL (SCP Style)
            **AUTHOR**: Overwatch Command.
            **TONE**: Authoritative, Bureaucratic, Zero Tolerance.
            
            **CONTENT REQUIREMENTS**:
            1. **WARNING BOX**: Start with a visual warning about "Cognitohazard".
            2. **CLASS**: Assign an esoteric class (e.g., KETER, APOLLYON).
            3. **SPECIAL CONTAINMENT PROCEDURES**: Numbered list. Be extremely specific (e.g., "Liquid Nitrogen at -200°C").
            4. **INCIDENT REPORT**: A brief summary of what happens if it escapes.
            
            **STYLE**: Use ⚠️ emojis for warnings. Use ALL CAPS for critical instructions.
            """

        # 生成
        response = model.generate_content(prompt)
        
        # --- 5. 结果展示 ---
        st.markdown('<div class="warning-box">⚠️ CLASSIFIED MATERIAL - DO NOT DISTRIBUTE</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
        
        # 下载按钮
        st.download_button("💾 DOWNLOAD ENCRYPTED FILE", response.text, "vanguard_dossier.md")

    except Exception as e:
        st.error(f"❌ SYSTEM CRITICAL FAILURE: {e}")

elif generate_btn and not api_key:
    st.error("⛔ ACCESS DENIED: MISSING API KEY")
