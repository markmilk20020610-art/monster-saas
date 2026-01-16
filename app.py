import streamlit as st
import google.generativeai as genai
import time
from supabase import create_client, Client

# ==============================================================================
# 1. 核心配置 (已更名为 XENOGENESIS)
# ==============================================================================
st.set_page_config(
    page_title="XENOGENESIS | Intelligent Lifeform Engine", # 浏览器标签页名称
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
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
# 2. UI 升级：深海实验室风格
# ==============================================================================
st.markdown("""
<style>
    /* 全局背景：深海/虚空 */
    .stApp {
        background: linear-gradient(180deg, #020617 0%, #0f172a 50%, #000000 100%);
        color: #cbd5e1;
    }
    
    /* 字体优化 */
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background-color: #0b1120;
        border-right: 1px solid #1e293b;
    }

    /* 标题样式 */
    h1, h2, h3 { font-family: 'Cinzel', serif; letter-spacing: 2px; }
    p, li { font-family: 'Lora', serif; font-size: 1.05rem; line-height: 1.7; }

    /* 输入框 */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        font-family: 'Lora', serif;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        color: #f8fafc !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.2);
    }

    /* 按钮 */
    div.stButton > button {
        background: linear-gradient(to right, #4f46e5, #6366f1);
        color: white;
        border: none;
        font-family: 'Cinzel', serif;
        font-weight: bold;
        transition: all 0.4s ease;
    }
    div.stButton > button:hover {
        letter-spacing: 2px;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.6);
    }

    /* 结果卡片 */
    .report-container {
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid #334155;
        padding: 35px;
        border-radius: 4px;
        margin-bottom: 30px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.6);
        position: relative;
        overflow: hidden;
    }
    .report-container::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 100%; height: 3px;
        background: linear-gradient(90deg, transparent, #6366f1, transparent);
    }

    /* 等级差异 */
    .report-gold { border-left: 3px solid #f59e0b; }
    .report-silver { border-left: 3px solid #94a3b8; }
    
    blockquote {
        border-left: 2px solid #6366f1;
        background: #1e1b4b;
        padding: 15px;
        font-style: italic;
        color: #a5b4fc;
    }

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
    except Exception as e: st.error(f"❌ ACCESS DENIED: {e}")

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user: 
            try: supabase.table("profiles").insert({"id": response.user.id, "tier": "standard"}).execute()
            except: pass
            st.success("✅ SUBJECT REGISTERED.")
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
        st.toast("✅ SPECIMEN ARCHIVED", icon="🧬")
        time.sleep(1)
    except: st.error("Archive Failure")

def load_archives():
    try: return supabase.table("archives").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute().data
    except: return []

# ==============================================================================
# 4. 登录页 (BRAND REFRESH: XENOGENESIS)
# ==============================================================================
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # 🟢 更新点：登录页标题
        st.markdown("<br><br><h1 style='text-align: center; color: #6366f1;'>XENOGENESIS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; font-family: Cinzel;'>INTELLIGENT LIFEFORM ENGINE</p>", unsafe_allow_html=True)
        
        tab_l, tab_r = st.tabs(["ACCESS", "ENLIST"])
        with tab_l:
            e = st.text_input("ID", key="l_e")
            p = st.text_input("KEY", type="password", key="l_p")
            if st.button("ENTER LAB", use_container_width=True): login_user(e, p)
        with tab_r:
            ne = st.text_input("ID", key="r_e")
            np = st.text_input("KEY", type="password", key="r_p")
            if st.button("REGISTER", use_container_width=True): register_user(ne, np)
    st.stop()

# ==============================================================================
# 5. 主控界面 (V14 XENOGENESIS)
# ==============================================================================
TIER_CONFIG = {
    "standard": {"count": 1, "label": "JUNIOR RESEARCHER", "style": "report-standard"},
    "silver":   {"count": 2, "label": "SENIOR XENOLOGIST", "style": "report-silver"},
    "gold":     {"count": 3, "label": "DIRECTOR", "style": "report-gold"}
}
user_tier = st.session_state.tier
if user_tier not in TIER_CONFIG: user_tier = "standard"
config = TIER_CONFIG[user_tier]

# --- 侧边栏 ---
with st.sidebar:
    # 🟢 更新点：侧边栏标题
    st.title("🧬 XENOGENESIS")
    st.caption(f"ID: {st.session_state.user.email.split('@')[0]}")
    st.divider()
    
    st.markdown(f"**RANK: {config['label']}**")
    
    st.markdown("### 🔬 ANALYSIS PROTOCOLS")
    if user_tier == 'gold':
        st.markdown("✅ **Morphology Scan**")
        st.markdown("✅ **Behavioral Profiling**")
        st.markdown("✅ **Deep-Dive Metaphysics**")
    elif user_tier == 'silver':
        st.markdown("✅ **Morphology Scan**")
        st.markdown("✅ **Behavioral Profiling**")
        st.markdown("🔒 *Metaphysics (Locked)*")
    else:
        st.markdown("✅ **Morphology Scan**")
        st.markdown("🔒 *Behavioral Profiling (Locked)*")
        st.markdown("🔒 *Metaphysics (Locked)*")
        
    st.divider()
    if st.button("LEAVE LAB"): logout()

# --- 主内容 ---
# 🟢 更新点：主标题
st.title("🧪 XENOLOGY LAB")
st.markdown("*\"Evolution begins where reality ends.\"*")

tab_lab, tab_data = st.tabs(["🧬 SYNTHESIZE", "📂 SPECIMENS"])

with tab_lab:
    col_g, col_i = st.columns([1, 3])
    with col_g:
        genre = st.selectbox("ECOLOGICAL CONTEXT", 
            ["Cosmic Horror (宇宙恐怖)", "Dark Fantasy (黑暗奇幻)", "Cybernetic (赛博改造)", 
             "Folklore/Myth (民俗神话)", "Post-Apocalyptic (废土)", "Surrealism (超现实)"])
    with col_i:
        user_input = st.text_area("SEED DATA", height=100, placeholder="Input a concept: A mirror that reflects guilt, A tree growing from a corpse, The sound of silence...")

    if st.button("⚗️ INITIATE GENESIS", type="primary", use_container_width=True):
        if not user_input:
            st.warning("⚠️ Seed data required for synthesis.")
        else:
            genai.configure(api_key=google_key)
            monster_count = config['count']
            
            # --- XENOGENESIS PROMPT ---
            prompt = f"""
            **IDENTITY**: You are 'XENOGENESIS', an AI designed to extrapolate biological impossibilities.
            **GOAL**: Create **{monster_count}** creature concepts that provide **deep narrative inspiration** for an author.
            **CONTEXT**: {genre}. **SEED**: "{user_input}".
            
            **PHILOSOPHY**: A true monster is not just scary; it is a walking contradiction, a metaphor, or a biological impossibility.
            **GOLD TIER RULE**: If count >= 3, the final entity is a "Concept Entity" (Abstract/Metaphysical Boss).

            **OUTPUT FORMAT PER ENTITY (Use Markdown, be poetic yet clinical)**:
            ---
            ## 🧬 [LATIN/SCIENTIFIC NAME] (Common Name: [Name])
            *(Archetype: [e.g. The Tragic Devourer, The Silent Observer])*

            ### 👁️ PHYSIOLOGICAL PARADOX (The "Look")
            * **Anatomy**: [Describe its body, but focus on the *wrongness*. e.g. "It has eyes, but they are on the inside of its throat."]
            * **The Texture**: [Sensory details. e.g. "Feels like wet velvet," "Smells like ozone and old blood."]
            * **Evolutionary Logic**: [Why does it exist? e.g. "It evolved to hunt creatures that can only be seen in mirrors."]

            ### 🕯️ BEHAVIOR & RITUAL (The "Habit")
            * **The Idle State**: [What does it do when not fighting? e.g. "It arranges human teeth into perfect circles," "It weeps softly while eating."]
            * **Interaction**: [How does it react to being seen? e.g. "It freezes and mimics the observer's posture."]
            
            ### 🗣️ TONGUE & OBSCURITY (The "Sound")
            * **Vocalization**: [Describe the sound. e.g. "Like grinding stones," "A frequency that causes nosebleeds."]
            * **Obscure Language**: [If it speaks, give a sample line in a made-up language or cryptic riddle. e.g. *"Kla-thrum... you taste like forgotten years..."*]
            
            ### 🩸 THE AUTHOR'S BREAKTHROUGH (The "Idea")
            * **The Metaphor**: [What does this monster represent conceptually? e.g. "The fear of dementia," "The inevitability of decay."]
            * **Plot Hook**: [A unique way to introduce it that isn't just a jump scare.]
            * **The Loot (with Lore)**: [An item it drops that tells a sad or scary story.]

            ---
            """
            
            with st.spinner(f'Xenogenesis Sequence Initiated...'):
                try:
                    generation_config = genai.types.GenerationConfig(temperature=0.95) # 极高的创造性
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    res = model.generate_content(prompt, generation_config=generation_config)
                    st.session_state.current_result = res.text
                    st.session_state.current_input = f"[{genre}] {user_input}"
                except Exception as e:
                    st.error(f"Synthesis Error: {e}")

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
            if st.button("💾 ARCHIVE SPECIMEN"):
                save_archive(st.session_state.current_input, st.session_state.current_result)
        with c2:
            st.download_button("📥 EXPORT DOSSIER", st.session_state.current_result, "xenogenesis_report.md")

with tab_data:
    archives = load_archives()
    if not archives:
        st.caption("No biological data found.")
    else:
        for item in archives:
            with st.expander(f"📁 {item['created_at'][:10]} | {item['title']}"):
                st.markdown(item['content'])
