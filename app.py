import streamlit as st
import google.generativeai as genai
import time
from supabase import create_client, Client

# ==============================================================================
# 1. 核心配置
# ==============================================================================
st.set_page_config(
    page_title="XENOGENESIS | Void Terminal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed" # 默认收起侧边栏，沉浸感更强
)

try:
    google_key = st.secrets["GOOGLE_API_KEY"]
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error(f"⛔ SYSTEM FAILURE: {e}")
    st.stop()

# ==============================================================================
# 2. UI 究极进化：虚空终端 (CSS Magic)
# ==============================================================================
st.markdown("""
<style>
    /* --- 全局动画背景：深空呼吸 --- */
    @keyframes drift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    .stApp {
        background: linear-gradient(-45deg, #000000, #0f0c29, #302b63, #020617);
        background-size: 400% 400%;
        animation: drift 15s ease infinite;
        color: #e0e0e0;
        font-family: 'Courier New', monospace; /* 全局代码风 */
    }

    /* --- 字体引入 --- */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
    
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 0 0 10px rgba(99, 102, 241, 0.8);
    }
    
    p, div, label, input, textarea {
        font-family: 'Share Tech Mono', monospace !important;
    }

    /* --- 输入框：全息投影风格 --- */
    .stTextInput input, .stTextArea textarea {
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: #00ffcc !important;
        border: 1px solid rgba(0, 255, 204, 0.2) !important;
        border-radius: 0px !important; /* 硬朗的直角 */
        border-left: 3px solid #00ffcc !important;
        box-shadow: inset 0 0 20px rgba(0, 255, 204, 0.05);
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        background-color: rgba(0, 255, 204, 0.1) !important;
        box-shadow: 0 0 15px rgba(0, 255, 204, 0.4), inset 0 0 20px rgba(0, 255, 204, 0.1);
        border-left: 5px solid #00ffcc !important;
    }

    /* --- 按钮：赛博朋克充能 --- */
    div.stButton > button {
        background: transparent !important;
        border: 1px solid #6366f1 !important;
        color: #6366f1 !important;
        border-radius: 0px !important;
        padding: 10px 25px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 900;
        transition: all 0.3s;
        box-shadow: 0 0 5px rgba(99, 102, 241, 0.2);
    }
    
    div.stButton > button:hover {
        background: #6366f1 !important;
        color: #fff !important;
        box-shadow: 0 0 25px rgba(99, 102, 241, 0.8);
        text-shadow: 0 0 5px #fff;
        transform: scale(1.02);
    }

    /* --- 登录框特效容器 --- */
    .login-box {
        border: 1px solid rgba(99, 102, 241, 0.3);
        background: rgba(10, 10, 20, 0.8);
        padding: 40px;
        box-shadow: 0 0 50px rgba(0,0,0,0.8);
        backdrop-filter: blur(10px);
        position: relative;
    }
    /* 四角装饰线 */
    .login-box::before {
        content: ""; position: absolute; top: -1px; left: -1px; width: 20px; height: 20px;
        border-top: 2px solid #6366f1; border-left: 2px solid #6366f1;
    }
    .login-box::after {
        content: ""; position: absolute; bottom: -1px; right: -1px; width: 20px; height: 20px;
        border-bottom: 2px solid #6366f1; border-right: 2px solid #6366f1;
    }

    /* --- 结果报告：异星石板风格 --- */
    .report-container {
        background: rgba(5, 5, 10, 0.9);
        border: 1px solid #333;
        border-top: 3px solid #6366f1;
        padding: 30px;
        margin-top: 20px;
        position: relative;
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
    }
    
    /* 扫描线动画 */
    .report-container::after {
        content: " ";
        display: block;
        position: absolute;
        top: 0; left: 0; bottom: 0; right: 0;
        background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        z-index: 2;
        background-size: 100% 2px, 3px 100%;
        pointer-events: none;
    }

    /* 侧边栏优化 */
    [data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #333;
    }

    /* 隐藏杂项 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. 身份与数据库
# ==============================================================================
if 'user' not in st.session_state: st.session_state.user = None
if 'tier' not in st.session_state: st.session_state.tier = "standard"

def get_user_tier(user_id):
    try:
        res = supabase.table("profiles").select("tier").eq("id", user_id).execute()
        if res.data: return res.data[0]['tier']
        supabase.table("profiles").insert({"id": user_id, "tier": "standard"}).execute()
        return "standard"
    except: return "standard"

def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = response.user
        st.session_state.tier = get_user_tier(response.user.id)
        st.rerun()
    except Exception as e: st.error(f"❌ BIO-SCAN FAILED: {e}")

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user: 
            try: supabase.table("profiles").insert({"id": response.user.id, "tier": "standard"}).execute()
            except: pass
            st.success("✅ DNA RECORDED. PLEASE AUTHENTICATE.")
    except Exception as e: st.error(f"❌ MUTATION ERROR: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.tier = "standard"
    st.rerun()

def save_archive(title, content):
    try:
        data = {"user_id": st.session_state.user.id, "title": title[:50], "content": content}
        supabase.table("archives").insert(data).execute()
        st.toast("DATA ENCRYPTED & UPLOADED", icon="💾")
        time.sleep(1)
    except: st.error("Storage Corrupted")

def load_archives():
    try: return supabase.table("archives").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute().data
    except: return []

# ==============================================================================
# 4. 登录页：异星闸门 (The Airlock)
# ==============================================================================
if not st.session_state.user:
    # 布局居中
    col_spacer_l, col_main, col_spacer_r = st.columns([1, 1.5, 1])
    
    with col_main:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # 使用 HTML 容器包裹，应用 'login-box' 样式
        st.markdown("""
        <div class='login-box'>
            <h1 style='text-align: center; color: #6366f1; margin-bottom: 0;'>XENOGENESIS</h1>
            <p style='text-align: center; color: #00ffcc; letter-spacing: 2px; font-size: 0.8em;'>INTELLIGENT LIFEFORM ENGINE v15.0</p>
            <hr style='border-color: #333;'>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_reg = st.tabs(["[ AUTHENTICATE ]", "[ NEW SUBJECT ]"])
        
        with tab_login:
            st.write("")
            email = st.text_input("GENETIC SIGNATURE (EMAIL)", key="l_e", placeholder="ENTER ID...")
            pwd = st.text_input("ACCESS SEQUENCE (PASSWORD)", type="password", key="l_p", placeholder="******")
            st.write("")
            if st.button(">> INITIATE LINK <<", use_container_width=True): login_user(email, pwd)
            
        with tab_reg:
            st.write("")
            new_email = st.text_input("NEW SIGNATURE", key="r_e")
            new_pwd = st.text_input("NEW SEQUENCE", type="password", key="r_p")
            st.write("")
            if st.button(">> IMPRINT DNA <<", use_container_width=True): register_user(new_email, new_pwd)
            
    st.stop()

# ==============================================================================
# 5. 主控界面：虚空控制台 (The Void Deck)
# ==============================================================================
TIER_CONFIG = {
    "standard": {"count": 1, "label": "LVL.1 RESEARCHER", "style": "report-standard"},
    "silver":   {"count": 2, "label": "LVL.2 XENOLOGIST", "style": "report-silver"},
    "gold":     {"count": 3, "label": "LVL.3 DIRECTOR", "style": "report-gold"}
}
user_tier = st.session_state.tier
if user_tier not in TIER_CONFIG: user_tier = "standard"
config = TIER_CONFIG[user_tier]

# --- 侧边栏 HUD ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#00ffcc; font-size:1.5em;'>SYSTEM STATUS</h2>", unsafe_allow_html=True)
    st.caption(f"OPERATOR: {st.session_state.user.email.split('@')[0]}")
    st.divider()
    
    st.markdown(f"**CLEARANCE: <span style='color:#6366f1'>{config['label']}</span>**", unsafe_allow_html=True)
    
    st.markdown("### 🧬 PROCESSORS")
    if user_tier == 'gold':
        st.markdown("🟢 CORE 1: ONLINE")
        st.markdown("🟢 CORE 2: ONLINE")
        st.markdown("🟣 CORE 3: METAPHYSICS READY")
    elif user_tier == 'silver':
        st.markdown("🟢 CORE 1: ONLINE")
        st.markdown("🟢 CORE 2: ONLINE")
        st.markdown("🔴 CORE 3: OFFLINE")
    else:
        st.markdown("🟢 CORE 1: ONLINE")
        st.markdown("🔴 CORE 2: OFFLINE")
        st.markdown("🔴 CORE 3: OFFLINE")
        
    st.divider()
    if st.button(">> SEVER LINK <<"): logout()

# --- 主界面 ---
st.title("XENOGENESIS // TERMINAL")

# 顶部导航模拟
tab_main, tab_db = st.tabs(["[ 01: GENESIS ]", "[ 02: ARCHIVES ]"])

with tab_main:
    col_input, col_viz = st.columns([2, 1])
    
    with col_input:
        genre = st.selectbox("ECOLOGICAL PARAMETER", 
            ["Cosmic Horror", "Dark Fantasy", "Cybernetic Organism", 
             "Folklore & Myth", "Post-Apocalyptic", "Surrealism"])
             
        user_input = st.text_area("SEED DATA INPUT", height=150, 
            placeholder="// Enter conceptual keywords...\n// Example: A mirror that reflects guilt\n// Example: A clockwork angel rusting in the rain")

    with col_viz:
        st.markdown(f"""
        <div style="border: 1px dashed #333; padding: 20px; height: 100%; color: #666; font-size: 0.8em;">
            <p><strong>[ SIMULATION PARAMETERS ]</strong></p>
            <p>BATCH SIZE: <span style="color:#00ffcc">{config['count']}</span></p>
            <p>COMPLEXITY: <span style="color:#6366f1">HIGH</span></p>
            <p>MODE: NARRATIVE INSPIRATION</p>
            <br>
            <p><em>Waiting for seed data...</em></p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    if st.button(">> EXECUTE GENESIS PROTOCOL <<", type="primary", use_container_width=True):
        if not user_input:
            st.warning(">> ERROR: NO SEED DATA DETECTED")
        else:
            genai.configure(api_key=google_key)
            monster_count = config['count']
            
            prompt = f"""
            **IDENTITY**: You are 'XENOGENESIS', an ancient AI interpreting biological chaos.
            **GOAL**: Create **{monster_count}** creature concepts for a **{genre}** story.
            **SEED**: "{user_input}".
            
            **DIRECTIVE**: Focus on Paradox, Metaphor, and Sensory Horror.
            **GOLD TIER**: Final entity is ABSTRACT/METAPHYSICAL.

            **OUTPUT FORMAT (Markdown)**:
            ---
            ## 🧬 [NAME] (Common: [Name])
            *(Archetype: [Role])*

            ### 👁️ VISUAL PARADOX
            * **Anatomy**: [The wrongness of its body]
            * **Texture**: [Sensory details]

            ### 🕯️ RITUAL
            * **Idle**: [What it does alone]
            * **Reaction**: [How it reacts to observation]
            
            ### 🗣️ OBSCURITY
            * **Sound**: [Audio description]
            * **Line**: [Cryptic dialogue]
            
            ### 🩸 INSPIRATION
            * **Metaphor**: [Concept represented]
            * **Scene**: [Encounter prompt]
            * **Loot**: [Item + Lore]
            ---
            """
            
            with st.spinner(f'// PARSING REALITY... // COMPILING DNA...'):
                try:
                    # 模拟一点延迟，增加科技感
                    time.sleep(1) 
                    generation_config = genai.types.GenerationConfig(temperature=0.95)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    res = model.generate_content(prompt, generation_config=generation_config)
                    st.session_state.current_result = res.text
                    st.session_state.current_input = f"[{genre}] {user_input}"
                except Exception as e:
                    st.error(f"SYSTEM CRASH: {e}")

    # 结果展示
    if 'current_result' in st.session_state:
        # 使用 HTML 渲染复杂的 Dossier 样式
        st.markdown(f"""
        <div class='report-container'>
            <h3 style="color:#6366f1; border-bottom:1px solid #333; padding-bottom:10px;">>> GENESIS COMPLETE <<</h3>
            <div style="font-family: 'Share Tech Mono', monospace; color: #a5b4fc;">
                {st.session_state.current_result}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(">> ARCHIVE TO DATABASE <<"):
                save_archive(st.session_state.current_input, st.session_state.current_result)
        with c2:
            st.download_button(">> DOWNLOAD DOSSIER <<", st.session_state.current_result, "xenogenesis_log.md")

with tab_db:
    archives = load_archives()
    if not archives:
        st.markdown("<p style='text-align:center; color:#666;'>// DATABASE EMPTY //</p>", unsafe_allow_html=True)
    else:
        for item in archives:
            with st.expander(f"FILE_ID: {item['created_at'][:10]} | {item['title']}"):
                st.markdown(item['content'])
