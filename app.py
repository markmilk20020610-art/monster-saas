import streamlit as st
import google.generativeai as genai
import time

# --- 1. 页面基础配置 ---
st.set_page_config(
    page_title="VANGUARD | Xeno-Archives",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. 注入 CSS 样式 (黑客终端风格) ---
st.markdown("""
<style>
    /* 全局背景色 */
    .stApp { background-color: #0e1117; }
    
    /* 核心报告容器：黑底绿字 */
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
    
    /* 警告框 */
    .warning-box {
        background-color: #330000;
        color: #ff3333;
        padding: 10px;
        border: 1px solid #ff0000;
        text-align: center;
        font-weight: bold;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 安全获取 API Key (只从 Secrets 读取) ---
try:
    # 这一行是连接你后台保险箱的唯一通道
    my_secret_key = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("⛔ 严重错误：未检测到 Secrets 配置。请回到 Streamlit 后台设置。")
    st.stop()
except KeyError:
    st.error("⛔ 严重错误：Secrets 中找不到 'GOOGLE_API_KEY' 这个名字。请检查拼写。")
    st.stop()

# --- 4. 商业逻辑：访问密码库 ---
# 只有输入这些密码的用户才能使用 (未来你可以把这里改成数据库查询)
VALID_ACCESS_CODES = ["HUNTER-2026", "VIP-8888", "TEST-FREE"]

# 初始化防刷计时器
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

# --- 5. 侧边栏设计 ---
with st.sidebar:
    st.title("☢️ VANGUARD PRO")
    st.caption("SECURE TERMINAL ACCESS")
    st.markdown("---")
    
    # 密码输入框
    user_code = st.text_input("🔑 ENTER ACCESS CODE:", type="password")
    
    # 验证逻辑
    if user_code in VALID_ACCESS_CODES:
        st.success("✅ ACCESS GRANTED")
        st.caption("PLAN: UNLIMITED")
        access_granted = True
    elif user_code:
        st.error("⛔ INVALID CODE")
        st.caption("Please purchase a key.")
        access_granted = False
    else:
        st.info("🔒 SYSTEM LOCKED")
        access_granted = False
        
    st.markdown("---")
    
    # 功能菜单
    st.markdown("### 📡 MISSION PARAMETERS")
    doc_type = st.selectbox("ARCHIVE TYPE", 
        ["NECROPSY_REPORT (尸检报告)", "AUDIO_TRANSCRIPT (录音记录)", "CONTAINMENT_PROTOCOL (收容协议)"])
    
    # 权限滑块 (影响是否打码)
    clearance = st.select_slider("SECURITY CLEARANCE", 
        options=["L1 (Restricted)", "L2 (Confidential)", "L3 (Secret)", "OMNI (Top Secret)"])
    st.caption(f"Current Clearance: {clearance}")

# --- 6. 主界面逻辑 ---
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")

# 如果没输对密码，直接停止运行
if not access_granted:
    st.warning("⚠️ SECURITY LOCKDOWN ACTIVE")
    st.markdown("### RESTRICTED ACCESS")
    st.markdown("Please verify your identity via the sidebar terminal.")
    st.stop()

# 用户输入区
st.markdown("**INSTRUCTION:** Enter target entity description to retrieve secure documentation.")
user_input = st.text_area("TARGET DESCRIPTION (e.g., Deep-sea worm mimicking voices):", height=100)
generate_btn = st.button("INITIATE RETRIEVAL PROTOCOL", type="primary")

# --- 7. 生成核心逻辑 ---
if generate_btn and user_input:
    
    # A. 防刷检查 (冷却时间 5 秒)
    current_time = time.time()
    time_diff = current_time - st.session_state.last_request_time
    if time_diff < 5:
        st.warning(f"⚠️ SYSTEM COOLING DOWN... Please wait {5 - int(time_diff)} seconds.")
        st.stop()
    st.session_state.last_request_time = current_time

    # B. 配置 API
    genai.configure(api_key=my_secret_key)
    
    try:
        # 使用最稳健的 Flash 模型
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        with st.spinner(f'DECRYPTING LEVEL [{clearance}] FILES...'):
            
            # --- C. 终极 Prompt 工程 ---
            prompt = f"""
            **ROLE**: Central computer of secret org 'Vanguard'.
            **USER INPUT**: "{user_input}"
            **MODE**: {doc_type}
            **USER CLEARANCE**: {clearance}
            
            **CRITICAL RULES**:
            1. **REDACTION**: If Clearance is 'L1' or 'L2', you MUST hide sensitive data (dates, locations, death counts, true origins) using black bars '████'. If 'OMNI', show everything.
            2. **TONE**: Horror, Sci-Fi, Clinical, Professional.
            3. **FORMAT**: Markdown.
            
            **STRUCTURE**:
            1. **MAIN REPORT**: The core documentation with specific metrics (Size, Weight, Toxicity).
            2. **🧬 PROJECTED METAMORPHOSIS**: A section describing 2 future evolutionary stages if not contained.
            3. **🎒 RECOVERABLE ASSETS**: A section listing "Loot Drops" (organs/items) and 1 "Plot Hook" for adventurers.
            
            **MANDATORY**: End with a section called 'TRANSLATED SUMMARY' in Chinese (中文简报).
            """
            
            # D. 发送请求
            response = model.generate_content(prompt)
            
            # E. 展示结果
            st.markdown('<div class="warning-box">⚠️ CLASSIFIED MATERIAL - DO NOT DISTRIBUTE</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
            
            # F. 下载按钮
            st.download_button("💾 DOWNLOAD DOSSIER", response.text, "vanguard_file.md")

    except Exception as e:
        st.error(f"❌ SYSTEM ERROR: {e}")
        st.caption("Please contact administrator if error persists.")
