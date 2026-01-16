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

# --- 2. 样式：增强沉浸感 ---
st.markdown("""
<style>
    .stApp { background-color: #050505; }
    .report-container {
        font-family: 'Courier New', Courier, monospace;
        color: #00ff41; /* 经典的黑客绿 */
        background-color: #000000;
        padding: 40px;
        border: 2px solid #00ff41;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.2);
        margin-top: 20px;
        border-radius: 2px;
    }
    .warning-box {
        background-color: #220000;
        color: #ff3333;
        padding: 15px;
        border: 2px solid #ff0000;
        text-align: center;
        font-weight: 900;
        letter-spacing: 4px;
        text-transform: uppercase;
        margin-bottom: 25px;
        animation: blink 2s infinite;
    }
    @keyframes blink { 0% {opacity: 1;} 50% {opacity: 0.8;} 100% {opacity: 1;} }
    h1, h2, h3 { border-bottom: 1px solid #004411; padding-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. 安全获取 Key ---
try:
    my_secret_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⛔ SYSTEM ERROR: Secrets not configured.")
    st.stop()

# --- 4. 商业逻辑 ---
VALID_ACCESS_CODES = ["HUNTER-2026", "VIP-8888", "TEST-FREE"]

if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

# --- 5. 侧边栏 ---
with st.sidebar:
    st.title("☢️ VANGUARD DOSSIER")
    st.caption("SECURE DATABASE ACCESS")
    st.markdown("---")
    
    user_code = st.text_input("🔑 ENTER ACCESS CODE:", type="password")
    
    if user_code in VALID_ACCESS_CODES:
        st.success("✅ IDENTITY VERIFIED")
        access_granted = True
    elif user_code:
        st.error("⛔ INVALID CREDENTIALS")
        access_granted = False
    else:
        st.info("🔒 LOGIN REQUIRED")
        access_granted = False
        
    st.markdown("---")
    doc_type = st.selectbox("ARCHIVE TYPE", ["NECROPSY REPORT", "FIELD RECORDING", "SCP PROTOCOL"])
    clearance = st.select_slider("SECURITY CLEARANCE", options=["LEVEL 1 (Public)", "LEVEL 2 (Restricted)", "LEVEL 3 (Secret)", "OMNI (Eyes Only)"])

# --- 6. 主界面 ---
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")

if not access_granted:
    st.warning("⚠️ ACCESS DENIED. PLEASE AUTHENTICATE.")
    st.stop()

st.markdown("**INSTRUCTION:** Enter subject description. System will generate a comprehensive English dossier.")
user_input = st.text_area("TARGET SUBJECT:", height=100)
generate_btn = st.button("INITIATE DEEP SCAN", type="primary")

# --- 7. 核心生成逻辑 ---
def try_generate(model_name, prompt):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response, None
    except Exception as e:
        return None, str(e)

if generate_btn and user_input:
    
    # 强制冷却 2 秒
    time.sleep(2) 
    genai.configure(api_key=my_secret_key)
    
    # 模型列表
    model_list = ['gemini-1.5-flash', 'gemini-1.5-flash-8b', 'gemini-1.5-pro']
    
    success = False
    final_response = None
    
    # --- 🧠 V7.0 PROMPT: 加量不加价 ---
    prompt = f"""
    **SYSTEM ROLE**: You are the central intelligence mainframe of 'Vanguard', a clandestine paranormal research organization.
    **USER INPUT**: "{user_input}"
    **MODE**: {doc_type}
    **CLEARANCE**: {clearance}
    
    **CONSTRAINT**: 
    - **OUTPUT MUST BE 100% IN NATIVE, ATMOSPHERIC ENGLISH.**
    - No Chinese characters.
    - **LENGTH**: The report must be DETAILED and VERBOSE. Do not summarize.
    
    **🕵️ REDACTION STRATEGY (CRITICAL)**:
    - **LEVEL 1/2**: Do not just hide the name. Describe the *horror* of the unknown. Use phrases like "Subject emits a sound that causes [REDACTED]" or "The skin feels like [REDACTED]". Make the user curious.
    - **OMNI**: Reveal everything. No censorship.
    
    **📄 CONTENT STRUCTURE (Fill each section with detail)**:
    
    1.  **HEADER**: ID Code, Date (2026), Site Location, Containment Class.
    
    2.  **PHYSICAL & SENSORY DESCRIPTION**:
        - Don't just list size. Describe the *smell* (e.g., ozone, rotting kelp).
        - Describe the *sound* it makes.
        - Describe the *texture* of its skin/carapace.
        - *If L1/L2, redact the specific biological origins but keep the scary descriptions.*
    
    3.  **BEHAVIORAL PSYCHOLOGY**:
        - How does it hunt? Does it toy with prey?
        - Does it have hive-mind intelligence?
    
    4.  **INCIDENT REPORT #892 (Narrative)**:
        - A short paragraph describing a failed containment attempt or first contact.
        - Include a quote from a soldier or scientist (e.g., "It... it looked at me.").
    
    5.  **🧬 EVOLUTIONARY TRAJECTORY** (OMNI/L3 focus):
        - Theoretical mutations if fed different energy sources.
    
    6.  **🎒 ASSET & WEAKNESS ANALYSIS**:
        - **Vitals**: HP estimate, Armor Class equivalent.
        - **Weakness**: Specific chemical or energy types (e.g., "Vulnerable to Liquid Nitrogen").
        - **Loot**: Useful organs for crafting.
    
    **TONE**: Lovecraftian, Clinical, High-Stakes.
    **FORMAT**: Markdown with bolding and bullet points.
    """

    with st.spinner('ACCESSING DEEP STORAGE...'):
        for model_name in model_list:
            response, error = try_generate(model_name, prompt)
            if response:
                final_response = response
                success = True
                break 
            else:
                time.sleep(1) # 重试等待
    
    if success and final_response:
        st.markdown('<div class="warning-box">⚠️ CLEARANCE VERIFIED // EYES ONLY</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-container">{final_response.text}</div>', unsafe_allow_html=True)
        st.download_button("💾 DOWNLOAD DOSSIER", final_response.text, "vanguard_dossier.md")
    else:
        st.error("❌ CONNECTION LOST. PLEASE RETRY.")
