import streamlit as st
import google.generativeai as genai
import time
from supabase import create_client, Client

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="VANGUARD | Access Control",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. 样式美化 (增加了一些金色元素代表VIP) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; }
    .report-container {
        font-family: 'Courier New', Courier, monospace;
        color: #00ff41; background-color: #000; padding: 25px; border: 1px solid #00ff41;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.1); margin-bottom: 20px;
    }
    .vip-badge {
        background-color: #FFD700; color: #000; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em;
    }
    .free-badge {
        background-color: #333; color: #ccc; padding: 2px 8px; border-radius: 4px; font-size: 0.8em;
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

# --- 4. 身份验证逻辑 (核心升级) ---
if 'user' not in st.session_state: st.session_state.user = None
if 'tier' not in st.session_state: st.session_state.tier = "free" # 默认为免费
if 'clearance' not in st.session_state: st.session_state.clearance = "LEVEL 1"

def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = response.user
        
        # 🕵️‍♂️ 查花名册：看看这个用户是不是 VIP
        try:
            profile_res = supabase.table("profiles").select("tier").eq("id", response.user.id).execute()
            if profile_res.data and len(profile_res.data) > 0:
                st.session_state.tier = profile_res.data[0]['tier']
            else:
                # 如果花名册里没名字，说明是新来的，自动注册为 free
                supabase.table("profiles").insert({"id": response.user.id, "tier": "free"}).execute()
                st.session_state.tier = "free"
        except:
            st.session_state.tier = "free" # 出错就当免费处理
            
        st.rerun()
    except Exception as e:
        st.error(f"❌ Login Failed: {e}")

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user: 
            # 注册成功后，立刻在花名册里写上 'free'
            try:
                supabase.table("profiles").insert({"id": response.user.id, "tier": "free"}).execute()
            except:
                pass 
            st.success("✅ Success! Please Login.")
    except Exception as e:
        st.error(f"❌ Error: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.tier = "free"
    st.rerun()

# --- 5. 数据库存档逻辑 ---
def save_archive(title, content):
    try:
        # 🔒 只有 VIP 才能无限存 (这里演示权限控制，暂不强制拦截，只做提示)
        data = {
            "user_id": st.session_state.user.id,
            "title": title if title else "Unknown Subject",
            "content": content
        }
        supabase.table("archives").insert(data).execute()
        st.toast("✅ ARCHIVE SAVED", icon="💾")
        time.sleep(1)
    except Exception as e:
        st.error(f"Save Failed: {e}")

def load_archives():
    try:
        response = supabase.table("archives").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute()
        return response.data
    except:
        return []

# --- 6. 界面 A: 登录页 ---
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><h1 style='text-align: center; color: #00ff41;'>☢️ VANGUARD LOGIN</h1>", unsafe_allow_html=True)
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
# --- 7. 界面 B: 主程序 (权限分级版) ---
# ==============================================================================

# 侧边栏
with st.sidebar:
    st.write(f"USER: **{st.session_state.user.email}**")
    
    # 🌟 显示会员徽章
    if st.session_state.tier == 'pro':
        st.markdown('<span class="vip-badge">👑 PRO MEMBER</span>', unsafe_allow_html=True)
        st.success("All Systems Online.")
    else:
        st.markdown('<span class="free-badge">🌑 FREE TIER</span>', unsafe_allow_html=True)
        st.info("Limited Access.")

    if st.button("LOGOUT"): logout()
    st.divider()
    
    # 🔒 权限滑块逻辑 (最核心的改动)
    if st.session_state.tier == 'pro':
        # VIP: 可以随便滑
        st.write("🔓 **CLEARANCE OVERRIDE**")
        st.session_state.clearance = st.select_slider("SET LEVEL", options=["LEVEL 1", "LEVEL 2", "LEVEL 3", "OMNI"], value="OMNI")
    else:
        # FREE: 锁死在 Level 1
        st.write("🔒 **CLEARANCE LOCKED**")
        st.warning("Upgrade to PRO to access higher levels.")
        st.session_state.clearance = st.select_slider("SET LEVEL", options=["LEVEL 1"], value="LEVEL 1", disabled=True)

st.title("🗄️ CLASSIFIED DATABASE")

# 核心标签页
tab_gen, tab_hist = st.tabs(["📡 NEW SCAN", "📂 ARCHIVES"])

# --- 🟢 TAB 1: 生成 ---
with tab_gen:
    doc_type = st.selectbox("ARCHIVE TYPE", ["NECROPSY REPORT", "FIELD RECORDING", "SCP PROTOCOL"])
    user_input = st.text_area("TARGET SUBJECT:", height=80, placeholder="e.g. A mechanical shark in the desert...")
    
    gen_btn = st.button("INITIATE SCAN", type="primary")

    if gen_btn and user_input:
        genai.configure(api_key=google_key)
        
        # 根据权限决定 Prompt 的深度
        clr_prompt = st.session_state.clearance
        
        prompt = f"""
        **ROLE**: Vanguard Mainframe. **INPUT**: "{user_input}". **MODE**: {doc_type}. 
        **CLEARANCE**: {clr_prompt}.
        **USER TIER**: {st.session_state.tier}.
        **CONSTRAINT**: English Only. Verbose. Markdown.
        """
        
        with st.spinner('PROCESSING...'):
            try:
                # 统一使用稳定的 Flash 模型
                model = genai.GenerativeModel('gemini-2.0-flash')
                res = model.generate_content(prompt)
                st.session_state.current_result = res.text
                st.session_state.current_input = user_input
            except Exception as e:
                st.error(f"Connection Failed: {e}")

    # 显示结果
    if 'current_result' in st.session_state:
        # VIP 才有特殊的金色提示框，普通人是绿色
        if st.session_state.tier == 'pro':
             st.markdown('<div style="border:1px solid gold; padding:10px; color:gold; margin-bottom:10px;">👑 OMNI CLEARANCE VERIFIED</div>', unsafe_allow_html=True)
        else:
             st.markdown('<div class="warning-box">⚠️ STANDARD ACCESS</div>', unsafe_allow_html=True)
             
        st.markdown(f'<div class="report-container">{st.session_state.current_result}</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("💾 SAVE TO ARCHIVES"):
                title_preview = st.session_state.current_input[:30] + "..."
                save_archive(title_preview, st.session_state.current_result)
        with c2:
            st.download_button("📥 DOWNLOAD", st.session_state.current_result, "dossier.md")

# --- 🟡 TAB 2: 历史 ---
with tab_hist:
    # 可以在这里加个逻辑：普通用户只能看最近 3 条，VIP 看全部
    my_archives = load_archives()
    if not my_archives:
        st.info("No records found.")
    else:
        for item in my_archives:
            with st.expander(f"📄 {item['created_at'][:10]} | {item['title']}"):
                st.markdown(item['content'])
