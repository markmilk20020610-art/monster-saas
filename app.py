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

# --- 2. 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .report-container {
        font-family: 'Courier New', Courier, monospace;
        color: #33ff00;
        background-color: #000000;
        padding: 30px;
        border: 1px solid #33ff00;
        box-shadow: 0 0 20px rgba(51, 255, 0, 0.15);
        margin-top: 20px;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #330000;
        color: #ff3333;
        padding: 10px;
        border: 1px solid #ff0000;
        text-align: center;
        font-weight: bold;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 安全获取 Key ---
try:
    my_secret_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("⛔ SYSTEM ERROR: Secrets not configured.")
    st.stop()
except KeyError:
    st.error("⛔ SYSTEM ERROR: 'GOOGLE_API_KEY' not found in Secrets.")
    st.stop()

# --- 4. 商业逻辑 ---
VALID_ACCESS_CODES = ["HUNTER-2026", "VIP-8888", "TEST-FREE"]

if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

# --- 5. 侧边栏 ---
with st.sidebar:
    st.title("☢️ VANGUARD PRO")
    st.caption("US-GOV SECURE TERMINAL")
    st.markdown("---")
    
    user_code = st.text_input("🔑 ENTER ACCESS CODE:", type="password")
    
    if user_code in VALID_ACCESS_CODES:
        st.success("✅ ACCESS GRANTED")
        access_granted = True
    elif user_code:
        st.error("⛔ INVALID CODE")
        access_granted = False
    else:
        st.info("🔒 AUTHENTICATION REQUIRED")
        access_granted = False
        
    st.markdown("---")
    
    doc_type = st.selectbox("ARCHIVE TYPE", 
        ["NECROPSY REPORT", "RECOVERED AUDIO", "SCP PROTOCOL"])
    
    clearance = st.select_slider("SECURITY CLEARANCE", 
        options=["LEVEL 1 (Public)", "LEVEL 2 (Restricted)", "LEVEL 3 (Secret)", "OMNI (Eyes Only)"])
    
    st.caption(f"Clearance Status: {clearance}")

# --- 6. 主界面 ---
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")

if not access_granted:
    st.warning("⚠️ UNAUTHORIZED PERSONNEL")
    st.markdown("Access restricted. Please enter Access Code.")
    st.stop()

st.markdown("**INSTRUCTION:** Enter entity description (Chinese accepted). Output will be English.")
user_input = st.text_area("TARGET SUBJECT:", height=100)
generate_btn = st.button("INITIATE RETRIEVAL", type="primary")

# --- 7. 核心生成逻辑 ---
if generate_btn and user_input:
    
    current_time = time.time()
    if current_time - st.session_state.last_request_time < 5:
        st.warning("⚠️ TERMINAL BUSY. STANDBY...")
        st.stop()
    st.session_state.last_request_time = current_time

    genai.configure(api_key=my_secret_key)
    
    try:
        # 🟢 修复点：使用你列表里明确存在的 'gemini-2.0-flash'
        model = genai.GenerativeModel('gemini-2.0-flash') 
        
        with st.spinner('TRANSLATING & DECRYPTING...'):
            
            prompt = f"""
            **SYSTEM ROLE**: You are the central mainframe of 'Vanguard'.
            **USER INPUT**: "{user_input}"
            **MODE**: {doc_type}
            **CLEARANCE**: {clearance}
            
            **🚫 LANGUAGE CONSTRAINT**: 
            - **OUTPUT MUST BE 100% IN NATIVE ENGLISH**.
            - No Chinese characters in the report.
            
            **🕵️ REDACTION RULES**:
            - If Clearance is 'LEVEL 1' or 'LEVEL 2': Hide sensitive info with '████'.
            - If 'OMNI': Show FULL TRUTH.
            
            **📄 CONTENT**:
            1. **HEADER**: ID, Date, Location.
            2. **MAIN DOSSIER**: Hard sci-fi tone, specific data.
            3. **🧬 EVOLUTION**: 2 theoretical mutations.
            4. **🎒 ASSETS**: Loot drops & Adventure Hook.
            
            **FORMAT**: Markdown.
            """
            
            response = model.generate_content(prompt)
            
            st.markdown('<div class="warning-box">⚠️ TOP SECRET // NOFORN</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
            st.download_button("💾 DOWNLOAD FILE", response.text, "vanguard_report.md")

    except Exception as e:
        st.error(f"❌ SYSTEM FAILURE: {e}")
        # 如果 2.0 还不行，自动尝试备用方案
        if "404" in str(e):
             st.info("⚠️ 尝试自动切换到备用线路 (gemini-flash-latest)...")
             try:
                 model = genai.GenerativeModel('gemini-flash-latest')
                 response = model.generate_content(prompt)
                 st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
             except:
                 st.error("备用线路也无法连接。请检查 API Key 权限。")
