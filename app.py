import streamlit as st
import google.generativeai as genai
import time
from supabase import create_client, Client

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="VANGUARD | Cloud Access",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #050505; }
    /* 登录框美化 */
    .auth-box { border: 2px solid #00ff41; padding: 30px; border-radius: 5px; background: #000; text-align: center;}
    /* 报告样式 */
    .report-container {
        font-family: 'Courier New', Courier, monospace;
        color: #00ff41; background-color: #000; padding: 30px; border: 2px solid #00ff41;
        box-shadow: 0 0 30px rgba(0, 255, 65, 0.2); margin-top: 20px;
    }
    .warning-box {
        background-color: #220000; color: #ff3333; padding: 15px; border: 2px solid #ff0000;
        text-align: center; font-weight: 900; letter-spacing: 4px; text-transform: uppercase; margin-bottom: 25px;
    }
    /* 隐藏默认菜单 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. 初始化连接 ---
# 从 Secrets 获取钥匙
try:
    google_key = st.secrets["GOOGLE_API_KEY"]
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    
    # 连接 Supabase
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error(f"⛔ SYSTEM ERROR: 配置缺失。请检查 Secrets。错误信息: {e}")
    st.stop()

# --- 4. 身份验证逻辑 (Auth Logic) ---

if 'user' not in st.session_state:
    st.session_state.user = None
if 'clearance' not in st.session_state:
    st.session_state.clearance = "LEVEL 1" # 默认等级

def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = response.user
        
        # 👑 管理员后门：如果是你的邮箱，直接给最高权限
        # ⚠️ 把下面的 'admin@vanguard.com' 换成你自己的邮箱
        if email == "markmilk20020610@gmail.com": 
            st.session_state.clearance = "OMNI"
        else:
            # 普通用户逻辑：未来可以在这里读取数据库里的会员状态
            st.session_state.clearance = "LEVEL 1" # 默认新用户是 L1
            
        st.rerun()
    except Exception as e:
        st.error(f"❌ Login Failed: {e}")

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            st.success("✅ Registration Successful! Please switch to Login tab.")
    except Exception as e:
        st.error(f"❌ Registration Failed: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.clearance = "LEVEL 1"
    st.rerun()

# --- 5. 界面 A: 登录/注册页 ---
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><h1 style='text-align: center; color: #00ff41;'>☢️ VANGUARD GATEWAY</h1>", unsafe_allow_html=True)
        st.info("⚠️ SECURE CONNECTION REQUIRED")
        
        tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
        
        with tab1: # 登录
            email_in = st.text_input("Email", key="l_email")
            pass_in = st.text_input("Password", type="password", key="l_pass")
            if st.button("AUTHENTICATE", type="primary", use_container_width=True):
                login_user(email_in, pass_in)
        
        with tab2: # 注册
            st.caption("New Agent Enrollment")
            new_email = st.text_input("Enter Email", key="r_email")
            new_pass = st.text_input("Create Password (min 6 chars)", type="password", key="r_pass")
            if st.button("CREATE ID", use_container_width=True):
                register_user(new_email, new_pass)
    
    st.stop() # 没登录就停在这里

# ==============================================================================
# --- 6. 界面 B: 主程序 (SaaS 核心) ---
# ==============================================================================

# 侧边栏
with st.sidebar:
    st.title("☢️ COMMAND CENTER")
    st.write(f"Agent: **{st.session_state.user.email}**")
    st.info(f"CLEARANCE: **{st.session_state.clearance}**")
    
    if st.button("LOGOUT"):
        logout()
        
    st.markdown("---")
    doc_type = st.selectbox("ARCHIVE TYPE", ["NECROPSY REPORT", "FIELD RECORDING", "SCP PROTOCOL"])
    
    # 权限控制逻辑
    current_clearance = st.session_state.clearance
    
    # 如果是 OMNI，显示滑块让他玩
    if current_clearance == "OMNI":
        user_choice_clearance = st.select_slider("ADMIN OVERRIDE", options=["LEVEL 1", "LEVEL 2", "LEVEL 3", "OMNI"], value="OMNI")
    else:
        # 如果是 LEVEL 1，锁死
        st.warning("🔒 UPGRADE TO UNLOCK FULL ACCESS")
        st.caption("Current Plan: Free Tier")
        user_choice_clearance = "LEVEL 1" # 强制覆盖

# 主界面
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")

# 生成逻辑 (复用稳定版)
if 'last_time' not in st.session_state: st.session_state.last_time = 0

user_input = st.text_area("TARGET SUBJECT:", height=100)
gen_btn = st.button("INITIATE SCAN", type="primary")

def try_generate(model, prompt):
    try:
        m = genai.GenerativeModel(model)
        return m.generate_content(prompt), None
    except Exception as e:
        return None, str(e)

if gen_btn and user_input:
    # 冷却检查
    if time.time() - st.session_state.last_time < 2:
        st.warning("⚠️ COOLING DOWN...")
        st.stop()
    st.session_state.last_time = time.time()

    genai.configure(api_key=google_key)
    
    prompt = f"""
    **SYSTEM ROLE**: Central mainframe of 'Vanguard'.
    **USER INPUT**: "{user_input}"
    **MODE**: {doc_type}
    **CLEARANCE**: {user_choice_clearance}
    
    **CONSTRAINT**: OUTPUT IN ENGLISH. NO CHINESE. VERBOSE MODE.
    **REDACTION**: 
    - LEVEL 1/2: Describe horror but REDACT specific data/origins.
    - OMNI: Show ALL truth.
    
    **CONTENT**: HEADER, PHYSICAL(Scent/Sound), BEHAVIOR, INCIDENT, EVOLUTION, ASSETS.
    **FORMAT**: Markdown.
    """

    with st.spinner('ACCESSING DATABASE...'):
        res, err = try_generate('gemini-1.5-flash', prompt)
        if not res: # 如果 Flash 挂了试 Pro
             res, err = try_generate('gemini-1.5-pro', prompt)

    if res:
        st.markdown('<div class="warning-box">⚠️ CLEARANCE VERIFIED</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-container">{res.text}</div>', unsafe_allow_html=True)
        st.download_button("💾 DOWNLOAD", res.text, "dossier.md")
    else:
        st.error("❌ CONNECTION FAILED")
