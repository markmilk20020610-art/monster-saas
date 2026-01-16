import streamlit as st
import google.generativeai as genai
import time
from supabase import create_client, Client

# ==============================================================================
# 1. 核心配置与初始化
# ==============================================================================
st.set_page_config(
    page_title="VANGUARD | Bio-Weapon Database",
    page_icon="☣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化数据库连接
try:
    google_key = st.secrets["GOOGLE_API_KEY"]
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error(f"⛔ SYSTEM FAILURE: Config Error - {e}")
    st.stop()

# ==============================================================================
# 2. 深度 UI 优化 (V11 深空雷达主题)
# ==============================================================================
st.markdown("""
<style>
    /* 全局背景：深空雷达渐变 */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a1a1a 0%, #000000 90%);
        color: #e0e0e0;
    }
    
    /* 侧边栏美化 */
    [data-testid="stSidebar"] {
        background-color: #0a0a0a;
        border-right: 1px solid #333;
    }

    /* 输入框样式 */
    .stTextArea textarea {
        background-color: #111;
        color: #00ff41;
        border: 1px solid #333;
        font-family: 'Courier New', monospace;
    }

    /* 报告卡片：像机密文件一样 */
    .report-container {
        background: rgba(20, 20, 20, 0.8);
        border: 1px solid #333;
        border-left: 5px solid #00ff41; /* 默认绿色 */
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
        font-family: 'Courier New', monospace;
        line-height: 1.6;
    }
    
    /* 会员等级卡片样式 */
    .report-gold { border-left: 5px solid #FFD700; box-shadow: 0 0 15px rgba(255, 215, 0, 0.1); }
    .report-silver { border-left: 5px solid #C0C0C0; box-shadow: 0 0 10px rgba(192, 192, 192, 0.1); }
    .report-standard { border-left: 5px solid #444; }

    /* 徽章样式 */
    .badge { padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 0.85em; display: inline-block; margin-bottom: 10px; }
    .badge-gold { background: linear-gradient(45deg, #FFD700, #B8860B); color: black; box-shadow: 0 0 10px #FFD700; }
    .badge-silver { background: linear-gradient(45deg, #E0E0E0, #A9A9A9); color: black; }
    .badge-std { background: #333; color: #888; border: 1px solid #555; }

    /* 按钮特效 */
    div.stButton > button {
        background-color: #00ff41;
        color: black;
        border: none;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00cc33;
        box-shadow: 0 0 15px #00ff41;
        color: white;
    }
    
    /* 隐藏杂项 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. 身份验证与数据库逻辑
# ==============================================================================
if 'user' not in st.session_state: st.session_state.user = None
if 'tier' not in st.session_state: st.session_state.tier = "standard"

def get_user_tier(user_id):
    """从 Profiles 表获取用户等级"""
    try:
        res = supabase.table("profiles").select("tier").eq("id", user_id).execute()
        if res.data: return res.data[0]['tier']
        # 如果没记录，插入默认 standard
        supabase.table("profiles").insert({"id": user_id, "tier": "standard"}).execute()
        return "standard"
    except:
        return "standard"

def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state.user = response.user
        st.session_state.tier = get_user_tier(response.user.id)
        st.rerun()
    except Exception as e:
        st.error(f"❌ ACCESS DENIED: {e}")

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user: 
            try:
                supabase.table("profiles").insert({"id": response.user.id, "tier": "standard"}).execute()
            except: pass
            st.success("✅ ID CREATED. PLEASE LOGIN.")
    except Exception as e:
        st.error(f"❌ ERROR: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.tier = "standard"
    st.rerun()

def save_archive(title, content):
    try:
        data = {"user_id": st.session_state.user.id, "title": title[:50], "content": content}
        supabase.table("archives").insert(data).execute()
        st.toast("✅ DATA ENCRYPTED & SAVED", icon="💾")
        time.sleep(1)
    except:
        st.error("Save Failed")

def load_archives():
    try:
        return supabase.table("archives").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute().data
    except:
        return []

# ==============================================================================
# 4. 登录界面 (极简风)
# ==============================================================================
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><h1 style='text-align: center; color: #00ff41; letter-spacing: 5px;'>☢️ VANGUARD</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>BIOLOGICAL ASSET MANAGEMENT SYSTEM</p>", unsafe_allow_html=True)
        
        tab_l, tab_r = st.tabs(["IDENTIFICATION", "RECRUITMENT"])
        with tab_l:
            e = st.text_input("CODENAME (Email)", key="l_e")
            p = st.text_input("PASSCODE", type="password", key="l_p")
            if st.button("AUTHENTICATE", use_container_width=True): login_user(e, p)
        with tab_r:
            ne = st.text_input("NEW CODENAME", key="r_e")
            np = st.text_input("NEW PASSCODE", type="password", key="r_p")
            if st.button("INITIATE", use_container_width=True): register_user(ne, np)
    st.stop()

# ==============================================================================
# 5. 主控界面 (V11.5 深渊档案版)
# ==============================================================================

# 定义会员权益配置
TIER_CONFIG = {
    "standard": {"count": 1, "label": "STANDARD", "color": "badge-std", "style": "report-standard"},
    "silver":   {"count": 2, "label": "SILVER CLASS", "color": "badge-silver", "style": "report-silver"},
    "gold":     {"count": 3, "label": "GOLD CLASS", "color": "badge-gold", "style": "report-gold"}
}

user_tier = st.session_state.tier
# 防止数据库乱填，兜底为 standard
if user_tier not in TIER_CONFIG: user_tier = "standard"

config = TIER_CONFIG[user_tier]

# --- 侧边栏：展示身份和资源 ---
with st.sidebar:
    st.markdown(f"<div class='badge {config['color']}'>{config['label']}</div>", unsafe_allow_html=True)
    st.write(f"OPERATOR: **{st.session_state.user.email.split('@')[0]}**")
    
    st.divider()
    st.markdown("### 🧬 GENERATION QUOTA")
    
    # 动态展示：资源槽位
    if user_tier == 'gold':
        st.markdown("🟢 **Subject Alpha** (Active)")
        st.markdown("🟢 **Subject Beta** (Active)")
        st.markdown("🟢 **Subject Omega** (BOSS Active)")
    elif user_tier == 'silver':
        st.markdown("🟢 **Subject Alpha** (Active)")
        st.markdown("🟢 **Subject Beta** (Active)")
        st.markdown("🔒 *Subject Omega (Locked)*")
    else:
        st.markdown("🟢 **Subject Alpha** (Active)")
        st.markdown("🔒 *Subject Beta (Locked)*")
        st.markdown("🔒 *Subject Omega (Locked)*")
        
    st.info(f"Current Output: {config['count']} Unit(s)")
    
    st.divider()
    if st.button("TERMINATE SESSION"): logout()

# --- 主界面 ---
st.title("🧬 GENETIC FORGE")

tab_scan, tab_db = st.tabs(["🚀 DEPLOYMENT", "📂 ARCHIVES"])

# --- TAB 1: 生成 (核心逻辑) ---
with tab_scan:
    # 输入区
    col_in, col_stat = st.columns([3, 1])
    with col_in:
        user_input = st.text_area("INPUT PARAMETERS", height=100, placeholder="Enter keywords: Cybernetic Zombie, Ancient Temple, Radiation, Snowstorm...")
    with col_stat:
        st.markdown("#### STATUS")
        st.write(f"System: **ONLINE**")
        st.write(f"Tier: **{config['label']}**")
        st.write(f"Batch Size: **{config['count']} Entities**")
    
    if st.button("🧬 SYNTHESIZE ORGANISM", type="primary", use_container_width=True):
        if not user_input:
            st.warning("⚠️ INPUT REQUIRED")
        else:
            genai.configure(api_key=google_key)
            
            # --- V11.5 核心升级：程序化生成的 Prompt ---
            monster_count = config['count']
            
            prompt = f"""
            **ROLE**: Hardcore RPG Mechanics Designer & Evolutionary Biologist.
            **TASK**: Generate **{monster_count}** monster entities based on keyword: "{user_input}".
            
            **⚙️ CORE GENERATION RULES (CRITICAL)**:
            1. **ENVIRONMENTAL SYNERGY**: Skills MUST strictly match the environment. (e.g., A swamp creature uses methane gas/mud; A cybernetic creature uses hacking/lasers). NO generic magic unless specified.
            2. **RANDOMIZED ARCHETYPES**: For each monster, randomly pick a role: [Tank / Glass Cannon / Crowd Control / Stealth Assassin / Summoner]. Do not make them all the same.
            3. **GOLD TIER BOSS**: The final entity (if count >= 3) must be a "RAID BOSS" with multi-stage mechanics.
            
            **OUTPUT FORMAT PER ENTITY (Strict Markdown)**:
            
            ---
            ## 🧬 [ENTITY NAME]
            *(Archetype: [Insert Random Role])*
            
            > *"A flavor text quote describing the horror of encountering this beast."*
            
            ### 👁️ PHYSIOLOGY & HABITAT
            * **Visuals**: [Detailed description focusing on how environment shaped its body]
            * **Habitat**: [Specific location details within the user's theme]
            
            ### 🎲 DYNAMIC COMBAT ABILITIES (RNG Generated)
            * **Passive: [Name]**
              * *Effect*: [Logic-based passive. e.g., "Thick Fur" reduces Cold Dmg, "Slime Body" ignores physical blunt dmg]
            * **Skill 1: [Name] (Type: [Physical/Elemental/Mental])**
              * *Mechanic*: [Detailed combat logic. e.g., "Burrows underground and strikes from below, causing 'Bleeding' status."]
            * **Skill 2: [Name] (Type: [Area of Effect/Debuff])**
              * *Mechanic*: [Environmental interaction. e.g., "Smashes the ground to create tremors" or "Absorbs nearby electricity to heal."]
            * **Ultimate: [Name]**
              * *Devastation*: [A high-damage signature move]
            
            ### 🦋 EVOLUTION & MUTATION
            * **Metamorphosis**: Evolving from **[Larva Name]** -> **[Current]** -> **[Future Horror Name]**.
            * **Trigger**: Evolution happens if [Specific Condition, e.g., "It eats 100kg of metal"].
            
            ### 💰 LOOT & HARVEST
            * **Crafting Material**: [Name] (Used to make: [Armor/Potion])
            * **Rare Artifact**: [Weapon/Item Name]
              * *Attribute*: [Specific Stat, e.g., "+20% Poison Resistance"]
              * *Hidden Lore*: [Why is this item valuable?]
            
            ### 🕵️‍♂️ VANGUARD INTEL (Hooks)
            * **Weakness**: [Specific elemental or tactical weakness]
            * **Plot Hook**: [A mystery or quest trigger related to this monster]
            
            ---
            """
            
            with st.spinner(f'RUNNING COMBAT SIMULATION FOR {monster_count} ENTITIES...'):
                try:
                    # 使用 Flash 模型，并调高随机性 (temperature)
                    generation_config = genai.types.GenerationConfig(temperature=0.85)
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    res = model.generate_content(prompt, generation_config=generation_config)
                    
                    st.session_state.current_result = res.text
                    st.session_state.current_input = user_input
                except Exception as e:
                    st.error(f"Synthesis Failed: {e}")

    # 结果展示区
    if 'current_result' in st.session_state:
        # 根据等级应用不同的边框颜色
        css_class = config['style']
        st.markdown(f"""
        <div class='report-container {css_class}'>
            {st.session_state.current_result}
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾 SAVE TO DATABASE"):
                save_archive(st.session_state.current_input, st.session_state.current_result)
        with c2:
            st.download_button("📥 EXPORT DATA", st.session_state.current_result, "specimens.md")

# --- TAB 2: 档案库 ---
with tab_db:
    archives = load_archives()
    if not archives:
        st.caption("NO BIOLOGICAL RECORDS FOUND. INITIATE NEW SCAN.")
    else:
        for item in archives:
            # 这里的样式也根据当前等级稍微美化一下
            with st.expander(f"📅 {item['created_at'][:10]} | {item['title']}"):
                st.markdown(item['content'])
