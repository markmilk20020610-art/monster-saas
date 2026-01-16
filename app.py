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

# --- 2. 样式：纯美式军方终端风格 ---
st.markdown("""
<style>
    /* 全局背景色：深黑 */
    .stApp { background-color: #0e1117; }
    
    /* 核心报告容器：黑底绿字，CRT显示器风格 */
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
    
    /* 警告框 */
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
    
    /* 小标题高亮 */
    h1, h2, h3 { color: #33ff00 !important; font-family: 'Courier New'; }
</style>
""", unsafe_allow_html=True)

# --- 3. 安全获取 API Key (从 Secrets 读取) ---
try:
    my_secret_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("⛔ SYSTEM ERROR: Secrets not configured. Please check Streamlit settings.")
    st.stop()
except KeyError:
    st.error("⛔ SYSTEM ERROR: 'GOOGLE_API_KEY' not found in Secrets.")
    st.stop()

# --- 4. 商业逻辑：密码库 ---
# 在这里定义你的“售卖密码”
VALID_ACCESS_CODES = ["HUNTER-2026", "VIP-8888", "TEST-FREE"]

# 初始化防刷计时器
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

# --- 5. 侧边栏 (全英文界面 - 模拟美军终端) ---
with st.sidebar:
    st.title("☢️ VANGUARD PRO")
    st.caption("US-GOV SECURE TERMINAL")
    st.markdown("---")
    
    # 密码输入
    user_code = st.text_input("🔑 ENTER ACCESS CODE:", type="password")
    
    # 验证逻辑
    if user_code in VALID_ACCESS_CODES:
        st.success("✅ ACCESS GRANTED")
        st.caption("STATUS: ACTIVE AGENT")
        access_granted = True
    elif user_code:
        st.error("⛔ INVALID CODE")
        access_granted = False
    else:
        st.info("🔒 AUTHENTICATION REQUIRED")
        access_granted = False
        
    st.markdown("---")
    
    # 功能菜单 (英文)
    doc_type = st.selectbox("ARCHIVE TYPE", 
        ["NECROPSY REPORT", "RECOVERED AUDIO", "SCP PROTOCOL"])
    
    # 权限滑块
    clearance = st.select_slider("SECURITY CLEARANCE", 
        options=["LEVEL 1 (Public)", "LEVEL 2 (Restricted)", "LEVEL 3 (Secret)", "OMNI (Eyes Only)"])
    
    st.caption(f"Clearance Status: {clearance}")

# --- 6. 主界面 ---
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")

# 未解锁状态
if not access_granted:
    st.warning("⚠️ UNAUTHORIZED PERSONNEL")
    st.markdown("Access to this terminal is restricted to Vanguard Agents.")
    st.markdown("Please enter your Access Code in the sidebar.")
    st.stop()

# 解锁后显示输入框
st.markdown("**INSTRUCTION:** Enter entity description (Chinese or English accepted). Output will be in English.")
user_input = st.text_area("TARGET SUBJECT:", height=100)
generate_btn = st.button("INITIATE RETRIEVAL", type="primary")

# --- 7. 核心生成逻辑 ---
if generate_btn and user_input:
    
    # A. 防刷检查 (冷却时间 5 秒)
    current_time = time.time()
    time_diff = current_time - st.session_state.last_request_time
    if time_diff < 5:
        st.warning("⚠️ TERMINAL BUSY. STANDBY...")
        st.stop()
    st.session_state.last_request_time = current_time

    # B. 配置 API
    genai.configure(api_key=my_secret_key)
    
    try:
        # 使用 Flash 模型 (速度快、成本低)
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        with st.spinner('TRANSLATING & DECRYPTING...'):
            
            # --- 🧠 V6.1 Prompt: 中文输入 -> 英文硬核输出 ---
            prompt = f"""
            **SYSTEM ROLE**: You are the central mainframe of 'Vanguard', a top-secret US paranormal research organization.
            **USER INPUT**: "{user_input}"
            **MODE**: {doc_type}
            **CLEARANCE**: {clearance}
            
            **🚫 LANGUAGE CONSTRAINT (CRITICAL)**: 
            - Regardless of whether the User Input is in Chinese, Spanish, or English, **THE OUTPUT MUST BE 100% IN NATIVE, HIGH-LEVEL ENGLISH**.
            - Do not include any Chinese characters in the final report.
            - Adapt Chinese concepts into Western Sci-Fi/Horror terms (e.g., "僵尸" -> "Reanimated Necrotic Host").
            
            **🕵️ REDACTION RULES**:
            - If Clearance is 'LEVEL 1' or 'LEVEL 2': You MUST hide sensitive info (specific dates, exact locations, casualty numbers, origin theories) using black bars like '████'.
            - If 'OMNI': Show FULL TRUTH. No censorship.
            
            **📄 CONTENT STRUCTURE**:
            1. **HEADER**: ID Code, Date (2026), Location.
            2. **MAIN DOSSIER**: 
               - Use hard sci-fi terminology (e.g., "bio-luminescent", "necrotic tissue", "gamma radiation").
               - Include specific data tables (Height, Weight, Toxicity, Threat Level).
            3. **🧬 EVOLUTIONARY PROJECTION**: 
               - Describe 2 theoretical mutations/stages if the entity is not contained.
            4. **🎒 ASSET RECOVERY**: 
               - List "Loot Drops" (organs/tech that can be harvested).
               - List 1 "Adventure Hook" (a rumor or mission idea for field agents).
            
            **TONE**: Cold, Clinical, Lovecraftian Horror.
            **FORMAT**: Markdown.
            """
            
            # C. 发送请求
            response = model.generate_content(prompt)
            
            # D. 展示结果
            st.markdown('<div class="warning-box">⚠️ TOP SECRET // NOFORN</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
            
            # E. 下载按钮
            st.download_button("💾 DOWNLOAD FILE", response.text, "vanguard_report.md")

    except Exception as e:
        st.error(f"❌ SYSTEM FAILURE: {e}")
