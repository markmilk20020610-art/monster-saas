import streamlit as st
import google.generativeai as genai
import time
from supabase import create_client, Client

# ==============================================================================
# 1. 核心配置
# ==============================================================================
st.set_page_config(
    page_title="VANGUARD | Genetic Forge",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库
try:
    google_key = st.secrets["GOOGLE_API_KEY"]
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error(f"⛔ SYSTEM FAILURE: Config Error - {e}")
    st.stop()

# ==============================================================================
# 2. UI 史诗级增强 (V12 赛博格栅主题)
# ==============================================================================
st.markdown("""
<style>
    /* --- 1. 背景优化：深空网格 + 呼吸暗角 --- */
    .stApp {
        background-color: #050505;
        background-image: 
            linear-gradient(rgba(0, 255, 65, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 65, 0.03) 1px, transparent 1px),
            radial-gradient(circle at 50% 10%, #111 0%, #000 90%);
        background-size: 30px 30px, 30px 30px, 100% 100%;
    }

    /* --- 2. 输入框：磨砂玻璃终端 --- */
    .stTextArea textarea {
        background-color: rgba(20, 20, 20, 0.7) !important;
        color: #00ff41 !important;
        border: 1px solid #333 !important;
        font-family: 'Courier New', monospace;
        border-radius: 8px;
        backdrop-filter: blur(5px);
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
        transition: border 0.3s;
    }
    .stTextArea textarea:focus {
        border: 1px solid #00ff41 !important;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
    }

    /* --- 3. 按钮：霓虹光晕 + 动态反馈 --- */
    /* 主按钮 (绿色) */
    div.stButton > button {
        background: linear-gradient(180deg, #00ff41 0%, #008f11 100%);
        color: #000;
        border: none;
        border-radius: 6px;
        font-weight: 900;
        letter-spacing: 1px;
        text-transform: uppercase;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
        transition: all 0.2s ease-in-out;
        border: 1px solid #00ff41;
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 255, 65, 0.8);
        color: #fff;
        text-shadow: 0 0 5px #000;
    }
    div.stButton > button:active {
        transform: scale(0.98);
    }

    /* --- 4. 侧边栏：深色磨砂 --- */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #222;
        box-shadow: 5px 0 15px rgba(0,0,0,0.5);
    }
    
    /* 侧边栏里的退出按钮 (改为红色警示) */
    [data-testid="stSidebar"] div.stButton > button {
        background: linear-gradient(180deg, #ff3333 0%, #990000 100%);
        border: 1px solid #ff3333;
        color: white;
        box-shadow: 0 0 10px rgba(255, 50, 50, 0.2);
    }
    [data-testid="stSidebar"] div.stButton > button:hover {
        box-shadow: 0 0 20px rgba(255, 50, 50, 0.6);
        color: white;
    }

    /* --- 5. 结果卡片：全息投影风 --- */
    .report-container {
        background: rgba(10, 15, 10, 0.85);
        border: 1px solid #333;
        border-left: 4px solid #00ff41;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8);
        margin-bottom: 20px;
        font-family: 'Courier New', monospace;
        backdrop-filter: blur(10px);
    }
    
    /* 等级差异化 */
    .report-gold { border-left: 4px solid #FFD700; background: rgba(20, 18, 5, 0.85); box-shadow: 0 0 20px rgba(255, 215, 0, 0.05); }
    .report-silver { border-left: 4px solid #C0C0C0; }

    /* --- 6. 徽章微调 --- */
    .badge { padding: 5px 12px; border-radius: 4px; font-weight: bold; font-size: 0.85em; display: inline-block; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .badge-gold { background: linear-gradient(90deg, #FFD700, #DAA520); color: black; box-shadow: 0 0 15px rgba(255, 215, 0, 0.4); }
    .badge-silver { background: linear-gradient(90deg, #E0E0E0, #B0B0B0); color: black; }
    .badge-std { background: #333; color: #888; border: 1px solid #444; }
    
    /* 隐藏顶部红线和菜单 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. 身份逻辑 (保持不变)
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
    except Exception as e: st.error(f"❌ ACCESS DENIED: {e}")

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user: 
            try: supabase.table("profiles").insert({"id": response.user.id, "tier": "standard"}).execute()
            except: pass
            st.success("✅ ID CREATED. LOGIN REQUIRED.")
    except Exception as e: st.error(f"❌ ERROR: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.tier = "standard"
    st.rerun()

def save_archive(title, content):
    try:
        data = {"user_id": st.session_state.user.id, "title": title[:50], "content": content}
        supabase.table("archives").insert(data).execute()
        st.toast("✅ ENCRYPTED & ARCHIVED", icon="💾")
        time.sleep(1)
    except: st.error("Save Failed")

def load_archives():
    try: return supabase.table("archives").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute().data
    except: return []

# ==============================================================================
# 4. 登录页 (保持极简)
# ==============================================================================
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><h1 style='text-align: center; color: #00ff41; letter-spacing: 5px; text-shadow: 0 0 10px #00ff41;'>☢️ VANGUARD</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>SECURE BIOLOGICAL ASSET TERMINAL</p>", unsafe_allow_html=True)
        
        tab_l, tab_r = st.tabs(["IDENTIFICATION", "RECRUITMENT"])
        with tab_l:
            e = st.text_input("CODENAME", key="l_e")
            p = st.text_input("PASSCODE", type="password", key="l_p")
            if st.button("AUTHENTICATE", use_container_width=True): login_user(e, p)
        with tab_r:
            ne = st.text_input("NEW CODENAME", key="r_e")
            np = st.text_input("NEW PASSCODE", type="password", key="r_p")
            if st.button("INITIATE", use_container_width=True): register_user(ne, np)
    st.stop()

# ==============================================================================
# 5. 主控界面 (V12)
# ==============================================================================
TIER_CONFIG = {
    "standard": {"count": 1, "label": "STANDARD", "color": "badge-std", "style": "report-standard"},
    "silver":   {"count": 2, "label": "SILVER CLASS", "color": "badge-silver", "style": "report-silver"},
    "gold":     {"count": 3, "label": "GOLD CLASS", "color": "badge-gold", "style": "report-gold"}
}
user_tier = st.session_state.tier
if user_tier not in TIER_CONFIG: user_tier = "standard"
config = TIER_CONFIG[user_tier]

# --- 侧边栏 ---
with st.sidebar:
    st.markdown(f"<div class='badge {config['color']}'>{config['label']}</div>", unsafe_allow_html=True)
    st.caption(f"OPERATOR ID: {st.session_state.user.email.split('@')[0].upper()}")
    
    st.divider()
    st.markdown("### 📡 SYSTEM QUOTA")
    
    if user_tier == 'gold':
        st.markdown("🟢 **Subject Alpha** (Ready)")
        st.markdown("🟢 **Subject Beta** (Ready)")
        st.markdown("🟢 **Subject Omega** (BOSS Ready)")
    elif user_tier == 'silver':
        st.markdown("🟢 **Subject Alpha** (Ready)")
        st.markdown("🟢 **Subject Beta** (Ready)")
        st.markdown("🔒 *Subject Omega (Locked)*")
    else:
        st.markdown("🟢 **Subject Alpha** (Ready)")
        st.markdown("🔒 *Subject Beta (Locked)*")
        st.markdown("🔒 *Subject Omega (Locked)*")
        
    st.divider()
    if st.button("TERMINATE SESSION"): logout()

# --- 主内容 ---
st.title("🧬 GENETIC FORGE")

tab_scan, tab_db = st.tabs(["🚀 DEPLOYMENT", "📂 ARCHIVES"])

with tab_scan:
    # 布局优化：状态栏做得更像 HUD
    c_input, c_hud = st.columns([3, 1])
    
    with c_input:
        user_input = st.text_area("INPUT PARAMETERS", height=120, placeholder="> Enter Keywords (e.g., Cyberpunk, Acid Rain, Ancient Temple)...")
    
    with c_hud:
        st.markdown(f"""
        <div style="background:rgba(20,20,20,0.5); padding:15px; border-radius:8px; border:1px solid #333;">
            <div style="color:#888; font-size:0.8em;">SYSTEM STATUS</div>
            <div style="color:#00ff41; font-weight:bold;">ONLINE</div>
            <div style="margin-top:10px; color:#888; font-size:0.8em;">TIER LEVEL</div>
            <div style="color:#fff;">{config['label']}</div>
            <div style="margin-top:10px; color:#888; font-size:0.8em;">BATCH SIZE</div>
            <div style="color:#fff;">{config['count']} ENTITIES</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("") # Spacer

    if st.button("🧬 INITIATE SYNTHESIS SEQUENCE", type="primary", use_container_width=True):
        if not user_input:
            st.warning("⚠️ INPUT PARAMETERS REQUIRED")
        else:
            genai.configure(api_key=google_key)
            monster_count = config['count']
            
            # PROMPT (保持 V11.5 的强力逻辑)
            prompt = f"""
            **ROLE**: Hardcore RPG Mechanics Designer.
            **TASK**: Generate **{monster_count}** monsters based on: "{user_input}".
            
            **RULES**:
            1. **ENVIRONMENTAL SYNERGY**: Skills MUST match the environment.
            2. **RANDOM ROLES**: [Tank / Glass Cannon / Stealth / Summoner].
            3. **BOSS**: Final entity (if count >= 3) is a RAID BOSS.
            
            **OUTPUT FORMAT (Markdown)**:
            ---
            ## 🧬 [ENTITY NAME]
            *(Role: [Insert Role])*
            > *"Flavor Text"*
            
            ### 👁️ VISUALS & HABITAT
            * **Visuals**: [Description]
            * **Habitat**: [Location]
            
            ### 🎲 COMBAT (RNG)
            * **Passive: [Name]** - [Effect]
            * **Skill 1: [Name]** - [Effect]
            * **Skill 2: [Name]** - [Effect]
            * **Ultimate: [Name]** - [High Dmg Effect]
            
            ### 🦋 EVOLUTION
            * **Stage**: [Larva] -> [Current] -> [Future]
            * **Trigger**: [Condition]
            
            ### 💰 LOOT
            * **Material**: [Name]
            * **Artifact**: [Name] (+Stats)
            
            ### 🕵️‍♂️ PLOT HOOK
            * **Secret**: [Mystery]
            ---
            """
            
            with st.spinner(f'⚡ PROCESSING {monster_count} BIO-SIGNATURES...'):
                try:
                    generation_config = genai.types.GenerationConfig(temperature=0.85)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    res = model.generate_content(prompt, generation_config=generation_config)
                    st.session_state.current_result = res.text
                    st.session_state.current_input = user_input
                except Exception as e:
                    st.error(f"SYNTHESIS ERROR: {e}")

    # 结果展示
    if 'current_result' in st.session_state:
        css_class = config['style']
        st.markdown(f"""
        <div class='report-container {css_class}'>
            {st.session_state.current_result}
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 SAVE DATA"):
                save_archive(st.session_state.current_input, st.session_state.current_result)
        with c2:
            st.download_button("📥 EXPORT LOG", st.session_state.current_result, "specimen_log.md")

with tab_db:
    archives = load_archives()
    if not archives:
        st.caption("NO RECORDS FOUND IN ARCHIVES.")
    else:
        for item in archives:
            with st.expander(f"📅 {item['created_at'][:10]} | {item['title']}"):
                st.markdown(item['content'])
