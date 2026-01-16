import streamlit as st
import google.generativeai as genai
import time
from supabase import create_client, Client

# ==============================================================================
# 1. 核心配置
# ==============================================================================
st.set_page_config(
    page_title="VANGUARD | Muse Engine",
    page_icon="✒️",
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
# 2. UI 升级：更具书卷气与神秘感的赛博风格
# ==============================================================================
st.markdown("""
<style>
    /* 背景：深邃的墨水蓝+星空，更有文学想象空间 */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #0f172a 0%, #000000 90%);
        color: #e2e8f0;
    }
    
    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1e293b;
    }

    /* 输入框：像打字机一样的质感 */
    .stTextArea textarea {
        background-color: rgba(30, 41, 59, 0.8) !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
        font-family: 'Georgia', serif; /* 换成衬线体，更有小说感 */
        font-size: 1.1em;
        border-radius: 4px;
        backdrop-filter: blur(5px);
    }
    .stTextArea textarea:focus {
        border: 1px solid #38bdf8 !important;
        color: #e2e8f0 !important;
    }

    /* 按钮：灵感火花 */
    div.stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        border: none;
        font-family: 'Arial', sans-serif;
        font-weight: bold;
        letter-spacing: 1px;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #60a5fa 0%, #2563eb 100%);
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
    }

    /* 结果卡片：文学档案风格 */
    .report-container {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid #334155;
        border-left: 4px solid #38bdf8;
        padding: 30px;
        border-radius: 2px;
        margin-bottom: 25px;
        font-family: 'Georgia', serif; /* 核心：内容用衬线体，易于阅读 */
        line-height: 1.8;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    /* 引用块样式 */
    blockquote {
        border-left: 3px solid #94a3b8;
        padding-left: 15px;
        color: #cbd5e1;
        font-style: italic;
        background: rgba(255,255,255,0.05);
        padding: 10px;
    }

    /* 等级样式差异 */
    .report-gold { border-left: 4px solid #f59e0b; background: rgba(20, 10, 0, 0.8); } /* 琥珀色 */
    .report-silver { border-left: 4px solid #94a3b8; }
    
    /* 隐藏杂项 */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. 身份逻辑
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
    except Exception as e: st.error(f"❌ Login Failed: {e}")

def register_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user: 
            try: supabase.table("profiles").insert({"id": response.user.id, "tier": "standard"}).execute()
            except: pass
            st.success("✅ Created. Please Login.")
    except Exception as e: st.error(f"❌ Error: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.session_state.tier = "standard"
    st.rerun()

def save_archive(title, content):
    try:
        data = {"user_id": st.session_state.user.id, "title": title[:50], "content": content}
        supabase.table("archives").insert(data).execute()
        st.toast("✅ Saved to Library", icon="📚")
        time.sleep(1)
    except: st.error("Save Failed")

def load_archives():
    try: return supabase.table("archives").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute().data
    except: return []

# ==============================================================================
# 4. 登录页
# ==============================================================================
if not st.session_state.user:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><h1 style='text-align: center; color: #38bdf8; font-family: serif;'>✒️ VANGUARD MUSE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b;'>NARRATIVE BLOCK BREAKER</p>", unsafe_allow_html=True)
        
        tab_l, tab_r = st.tabs(["AUTHOR LOGIN", "NEW WRITER"])
        with tab_l:
            e = st.text_input("Email", key="l_e")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("ENTER LIBRARY", use_container_width=True): login_user(e, p)
        with tab_r:
            ne = st.text_input("Email", key="r_e")
            np = st.text_input("Password", type="password", key="r_p")
            if st.button("REGISTER", use_container_width=True): register_user(ne, np)
    st.stop()

# ==============================================================================
# 5. 主控界面 (V13 灵感缪斯版)
# ==============================================================================
TIER_CONFIG = {
    "standard": {"count": 1, "label": "NOVICE AUTHOR", "style": "report-standard"},
    "silver":   {"count": 2, "label": "PRO AUTHOR", "style": "report-silver"},
    "gold":     {"count": 3, "label": "BESTSELLER", "style": "report-gold"}
}
user_tier = st.session_state.tier
if user_tier not in TIER_CONFIG: user_tier = "standard"
config = TIER_CONFIG[user_tier]

# --- 侧边栏 ---
with st.sidebar:
    st.caption(f"✍️ {config['label']}")
    st.write(f"USER: **{st.session_state.user.email.split('@')[0]}**")
    st.divider()
    
    st.markdown("### 📚 INSPIRATION SLOTS")
    if user_tier == 'gold':
        st.markdown("🔹 **Concept Alpha** (Active)")
        st.markdown("🔹 **Concept Beta** (Active)")
        st.markdown("🔸 **The Boss/Horror** (Active)")
    elif user_tier == 'silver':
        st.markdown("🔹 **Concept Alpha** (Active)")
        st.markdown("🔹 **Concept Beta** (Active)")
        st.markdown("🔒 *The Boss (Locked)*")
    else:
        st.markdown("🔹 **Concept Alpha** (Active)")
        st.markdown("🔒 *Concept Beta (Locked)*")
        st.markdown("🔒 *The Boss (Locked)*")
        
    st.divider()
    if st.button("EXIT LIBRARY"): logout()

# --- 主内容 ---
st.title("💡 THE MUSE ENGINE")
st.caption("Don't just spawn a monster. Spawn a story.")

tab_muse, tab_lib = st.tabs(["🧠 BRAINSTORM", "📖 ARCHIVES"])

with tab_muse:
    # --- V13 新增：流派选择器 ---
    col_genre, col_input = st.columns([1, 3])
    
    with col_genre:
        genre = st.selectbox(
            "GENRE / STYLE",
            ["Lovecraftian Horror (克苏鲁)", "Dark Fantasy (黑暗奇幻/魂系)", 
             "Sci-Fi / Cyberpunk (科幻)", "Xianxia / Eastern (东方玄幻/仙侠)", 
             "Urban Legend (都市传说)", "Post-Apocalyptic (废土)"]
        )
        st.info(f"Generating for: \n**{genre}**")

    with col_input:
        user_input = st.text_area(
            "CONTEXT / KEYWORDS", 
            height=120, 
            placeholder="e.g. A library where silence kills, An abandoned hospital, A sword made of blood..."
        )

    if st.button("🔥 IGNITE IMAGINATION", type="primary", use_container_width=True):
        if not user_input:
            st.warning("⚠️ Give me a seed (keyword) to grow a story.")
        else:
            genai.configure(api_key=google_key)
            monster_count = config['count']
            
            # --- V13 PROMPT: 侧重文学性、感官描写、语言 ---
            prompt = f"""
            **ROLE**: Best-Selling Novelist & Creative Writing Coach.
            **GOAL**: Help a writer break through "Writer's Block" by generating unique creature concepts for a **{genre}** story.
            **INPUT**: "{user_input}"
            **COUNT**: Generate **{monster_count}** entities.
            
            **CRITICAL INSTRUCTIONS**:
            1. **GENRE MATCHING**: If Xianxia, use poetic/daoist terms. If Sci-Fi, use technical horror. If Lovecraft, use madness/decay.
            2. **BREAK THE BLOCK**: Focus on *how to write* this monster, not just stats.
            3. **GOLD TIER**: If count >= 3, the last one is a Major Plot Antagonist.
            
            **OUTPUT FORMAT PER ENTITY (Markdown)**:
            ---
            ## 🖋️ [CREATURE NAME]
            *(Concept Archetype: [e.g. The Watcher, The Corrupted Guardian])*
            
            > *"Insert a short, atmospheric snippet of narration or dialogue involving this creature."*
            
            ### 👁️ SENSORY SIGNATURE (How to describe it)
            * **Visual**: [Don't just say 'big'. Describe textures, lighting, unnatural movements]
            * **Smell/Atmosphere**: [e.g., Smells like ozone and burnt hair, or the air gets cold]
            * **Sound**: [Specifics: Chittering, low-frequency hum, wet slapping sounds]
            
            ### 🗣️ LANGUAGE & OBSCURITY (The Weird Factor)
            * **Communication**: [Does it speak? Telepathy? Mimicry? Silence?]
            * **Sample Line/Sound**: [Give a specific line of dialogue or sound effect description. e.g., "It whispers your dead mother's name backwards" or "Zhh-krr-tchk..."]
            * **Habit**: [What weird thing does it do when not fighting? e.g., It organizes bones by size, it stares at mirrors.]
            
            ### 🎬 THE BREAKTHROUGH SCENE (How to introduce it)
            * **Scenario**: [A short prompt for a scene. e.g., "The protagonist thinks it's a statue until it blinks."]
            * **The Twist**: [Something unexpected about it.]
            
            ### ⚔️ INTERACTION MECHANICS (If conflict occurs)
            * **Method of Attack**: [Not just 'hits hard'. e.g., It steals memories, it ages you by touching.]
            * **Weakness**: [Narrative weakness. e.g., Cannot cross running water, afraid of its own reflection.]
            
            ### 🔗 PLOT HOOK
            * **Implication**: [What does its existence imply about the world?]
            ---
            """
            
            with st.spinner(f'weaving nightmares for {genre}...'):
                try:
                    generation_config = genai.types.GenerationConfig(temperature=0.9) # 高创造性
                    model = genai.GenerativeModel('gemini-2.0-flash')
                    res = model.generate_content(prompt, generation_config=generation_config)
                    st.session_state.current_result = res.text
                    st.session_state.current_input = f"[{genre}] {user_input}"
                except Exception as e:
                    st.error(f"Writer's Block too strong (Error): {e}")

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
            if st.button("💾 SAVE IDEA"):
                save_archive(st.session_state.current_input, st.session_state.current_result)
        with c2:
            st.download_button("📥 EXPORT TEXT", st.session_state.current_result, "story_ideas.md")

with tab_lib:
    archives = load_archives()
    if not archives:
        st.caption("Your library is empty. Go find your muse.")
    else:
        for item in archives:
            with st.expander(f"📜 {item['created_at'][:10]} | {item['title']}"):
                st.markdown(item['content'])
