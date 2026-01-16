import streamlit as st
import google.generativeai as genai
import time
from supabase import create_client, Client

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="VANGUARD | Memory Core",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. 样式美化 ---
st.markdown("""
<style>
    .stApp { background-color: #050505; }
    .report-container {
        font-family: 'Courier New', Courier, monospace;
        color: #00ff41; background-color: #000; padding: 25px; border: 1px solid #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.1); margin-bottom: 20px;
    }
    .archive-card {
        border: 1px solid #333; background: #111; padding: 15px; margin-bottom: 10px; border-radius: 5px;
    }
    /* 隐藏默认菜单 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. 初始化连接 ---
try:
    google_key = st.secrets["GOOGLE_API_KEY"]
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error(f"⛔ CONFIG ERROR: {e}")
    st.stop()

# --- 4. 身份验证逻辑 ---
if 'user' not in st.session_state: st.session_state.user = None
if 'clearance' not in st.session_state: st.session_state.clearance = "LEVEL 1"

def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = response.user
        # 👑 权限判断
        if email == "markmilk20020610@gmail.com": 
            st.session_state.clearance = "OMNI"
        else:
            st.session_state.clearance = "LEVEL 1"
        st.rerun()
    except Exception as e:
        st.error(f"❌ Login Failed: {e}")

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user: st.success("✅ Success! Please Login.")
    except Exception as e:
        st.error(f"❌ Error: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()

# --- 5. 数据库读写逻辑 (V9 新增) ---
def save_archive(title, content):
    try:
        data = {
            "user_id": st.session_state.user.id,
            "title": title if title else "Unknown Subject",
            "content": content
        }
        supabase.table("archives").insert(data).execute()
        st.toast("✅ ARCHIVE SAVED TO DATABASE", icon="💾")
        time.sleep(1) # 给一点时间刷新
    except Exception as e:
        st.error(f"Save Failed: {e}")

def load_archives():
    try:
        # 只查当前用户的记录，按时间倒序
        response = supabase.table("archives").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Load Failed: {e}")
        return []

# --- 6. 界面 A: 登录页 ---
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><h1 style='text-align: center; color: #00ff41;'>☢️ VANGUARD SYSTEM</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
        with tab1:
            e = st.text_input("Email", key="l_e")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("ENTER", use_container_width=True): login_user(e, p)
        with tab2:
            ne = st.text_input("New Email", key="r_e")
            np = st.text_input("New Password", type="password", key="r_p")
            if st.button("JOIN", use_container_width=True): register_user(ne, np)
    st.stop()

# ==============================================================================
# --- 7. 界面 B: 主程序 (V9 双模式) ---
# ==============================================================================

# 侧边栏
with st.sidebar:
    st.write(f"USER: **{st.session_state.user.email}**")
    st.info(f"CLEARANCE: **{st.session_state.clearance}**")
    if st.button("LOGOUT"): logout()
    st.divider()
    
    # 权限滑块
    current_clr = st.session_state.clearance
    if current_clr == "OMNI":
        user_choice_clr = st.select_slider("OVERRIDE", options=["LEVEL 1", "LEVEL 2", "LEVEL 3", "OMNI"], value="OMNI")
    else:
        st.warning("🔒 UPGRADE REQUIRED")
        user_choice_clr = "LEVEL 1"

st.title("🗄️ CLASSIFIED DATABASE")

# 核心标签页布局
tab_gen, tab_hist = st.tabs(["📡 NEW SCAN (生成)", "📂 MY ARCHIVES (历史)"])

# --- 🟢 TAB 1: 生成新内容 ---
with tab_gen:
    doc_type = st.selectbox("ARCHIVE TYPE", ["NECROPSY REPORT", "FIELD RECORDING", "SCP PROTOCOL"])
    user_input = st.text_area("TARGET SUBJECT:", height=80, placeholder="e.g. A mechanical shark in the desert...")
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        gen_btn = st.button("INITIATE SCAN", type="primary")

    # 生成逻辑
    if gen_btn and user_input:
        genai.configure(api_key=google_key)
        prompt = f"""
        **ROLE**: Vanguard Mainframe. **INPUT**: "{user_input}". **MODE**: {doc_type}. **CLEARANCE**: {user_choice_clr}.
        **CONSTRAINT**: English Only. Verbose.
        **REDACTION**: L1/L2 redact secrets. OMNI show all.
        **CONTENT**: HEADER, PHYSICAL, BEHAVIOR, INCIDENT, EVOLUTION, ASSETS.
        **FORMAT**: Markdown.
        """
        
        with st.spinner('PROCESSING...'):
            try:
                # 🟢 修复点：改回了 gemini-pro，保证能用
                model = genai.GenerativeModel('gemini-pro')
                res = model.generate_content(prompt)
                
                # 存入 Session State 防止刷新丢失
                st.session_state.current_result = res.text
                st.session_state.current_input = user_input
                
            except Exception as e:
                st.error(f"Connection Failed: {e}")

    # 显示结果 & 保存按钮
    if 'current_result' in st.session_state:
        st.markdown('<div class="warning-box">⚠️ CLEARANCE VERIFIED</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-container">{st.session_state.current_result}</div>', unsafe_allow_html=True)
        
        # 保存按钮区域
        st.markdown("---")
        c1, c2 = st.columns([1, 1])
        with c1:
            # 点击保存，把当前内容写入 Supabase
            if st.button("💾 SAVE TO ARCHIVES"):
                # 用输入的前20个字做标题
                title_preview = st.session_state.current_input[:30] + "..."
                save_archive(title_preview, st.session_state.current_result)
        with c2:
            st.download_button("📥 DOWNLOAD FILE", st.session_state.current_result, "dossier.md")

# --- 🟡 TAB 2: 查看历史 ---
with tab_hist:
    st.caption("RETRIEVING ENCRYPTED RECORDS...")
    
    # 每次点这个 tab 都会去数据库拉取最新列表
    my_archives = load_archives()
    
    if not my_archives:
        st.info("No records found. Generate something first!")
    else:
        for item in my_archives:
            # 使用折叠框显示每一条历史
            with st.expander(f"📄 {item['created_at'][:10]} | {item['title']}"):
                st.markdown(f"**ID:** {item['id']}")
                st.markdown(item['content'])
                st.button("DELETE", key=f"del_{item['id']}", help="Feature coming in V10")
