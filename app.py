import streamlit as st
import google.generativeai as genai
import time
from supabase import create_client, Client
import stripe # 新增：收银员

# ==============================================================================
# 1. 核心配置 & 样式注入
# ==============================================================================
st.set_page_config(
    page_title="XENOGENESIS | Void Terminal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 样式表 (保留 V15 的虚空风格) ---
st.markdown("""
<style>
    @keyframes drift { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }
    .stApp {
        background: linear-gradient(-45deg, #000000, #0f0c29, #302b63, #020617);
        background-size: 400% 400%;
        animation: drift 15s ease infinite;
        color: #e0e0e0;
        font-family: 'Courier New', monospace;
    }
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');
    h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; text-transform: uppercase; letter-spacing: 4px; text-shadow: 0 0 10px rgba(99, 102, 241, 0.8); }
    p, div, label, input, textarea { font-family: 'Share Tech Mono', monospace !important; }
    
    /* 价格卡片样式 */
    .plan-card {
        border: 1px solid #333; background: rgba(10,10,20,0.6); padding: 20px; text-align: center;
        transition: all 0.3s; cursor: pointer; position: relative;
    }
    .plan-card:hover { transform: scale(1.05); border-color: #6366f1; box-shadow: 0 0 20px rgba(99,102,241,0.3); }
    .plan-gold { border-top: 3px solid #FFD700; }
    .plan-silver { border-top: 3px solid #C0C0C0; }
    .price-tag { font-size: 2em; color: #fff; font-weight: bold; margin: 10px 0; }
    
    /* 其他 V15 样式保留... (为了节省篇幅，沿用之前的输入框和按钮样式) */
    .stTextInput input, .stTextArea textarea { background-color: rgba(0,0,0,0.6) !important; color: #00ffcc !important; border: 1px solid rgba(0,255,204,0.2) !important; }
    div.stButton > button { background: transparent !important; border: 1px solid #6366f1 !important; color: #6366f1 !important; }
    div.stButton > button:hover { background: #6366f1 !important; color: #fff !important; }
    
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. 系统初始化 (Supabase + Stripe)
# ==============================================================================
try:
    # 数据库
    supabase = create_client(st.secrets["supabase"]["url"], st.secrets["supabase"]["key"])
    # AI
    google_key = st.secrets["GOOGLE_API_KEY"]
    
    # 支付 (带容错处理：如果没有配置 Stripe，也不会崩，方便你测试)
    if "stripe" in st.secrets:
        stripe.api_key = st.secrets["stripe"]["api_key"]
        STRIPE_ENABLED = True
    else:
        STRIPE_ENABLED = False
        
except Exception as e:
    st.error(f"⛔ SYSTEM FAILURE: {e}")
    st.stop()

# ==============================================================================
# 3. 逻辑控制器 (Auth + Payment + Database)
# ==============================================================================
if 'user' not in st.session_state: st.session_state.user = None
if 'tier' not in st.session_state: st.session_state.tier = "standard"

# --- 数据库操作 ---
def get_user_tier(user_id):
    try:
        res = supabase.table("profiles").select("tier").eq("id", user_id).execute()
        if res.data: return res.data[0]['tier']
        supabase.table("profiles").insert({"id": user_id, "tier": "standard"}).execute()
        return "standard"
    except: return "standard"

def update_tier(user_id, new_tier):
    try:
        supabase.table("profiles").update({"tier": new_tier}).eq("id", user_id).execute()
        st.session_state.tier = new_tier
        st.toast(f"CLEARANCE UPDATED TO: {new_tier.upper()}", icon="👑")
    except Exception as e:
        st.error(f"UPDATE FAILED: {e}")

# --- 支付逻辑核心 ---
def create_checkout_session(plan_type):
    """创建 Stripe 支付链接"""
    if not STRIPE_ENABLED:
        st.warning("⚠️ STRIPE KEYS NOT FOUND. (Simulation Mode Active)")
        # 模拟模式：直接升级
        time.sleep(1)
        update_tier(st.session_state.user.id, plan_type)
        st.rerun()
        return
        
    try:
        # 获取 Price ID
        price_id = st.secrets["stripe"].get(f"price_{plan_type}")
        domain_url = st.secrets["stripe"].get("domain_url", "http://localhost:8501")
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='payment', # 或者 'subscription'
            success_url=domain_url + f"/?session_id={{CHECKOUT_SESSION_ID}}&tier={plan_type}",
            cancel_url=domain_url + "/?canceled=true",
        )
        return checkout_session.url
    except Exception as e:
        st.error(f"PAYMENT GATEWAY ERROR: {e}")

# --- 检查支付回调 (在页面加载时运行) ---
def check_payment_callback():
    if st.session_state.user:
        query_params = st.query_params
        if "session_id" in query_params and "tier" in query_params:
            # 这里的逻辑是：如果 URL 里有支付成功的标志，就升级用户
            # 在生产环境中，这里应该调用 stripe.checkout.Session.retrieve(session_id) 来验证真实性
            new_tier = query_params["tier"]
            st.toast("✅ PAYMENT VERIFIED. UPGRADING CLEARANCE...", icon="💳")
            update_tier(st.session_state.user.id, new_tier)
            # 清除 URL 参数，防止刷新重复触发
            st.query_params.clear()
            time.sleep(1)
            st.rerun()

# --- 认证逻辑 ---
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
            st.success("✅ DNA RECORDED.")
    except Exception as e: st.error(f"❌ ERROR: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None; st.session_state.tier = "standard"
    st.rerun()

def save_archive(title, content):
    try:
        data = {"user_id": st.session_state.user.id, "title": title[:50], "content": content}
        supabase.table("archives").insert(data).execute()
        st.toast("ENCRYPTED & UPLOADED", icon="💾")
    except: st.error("Storage Error")

def load_archives():
    try: return supabase.table("archives").select("*").eq("user_id", st.session_state.user.id).order("created_at", desc=True).execute().data
    except: return []

# ==============================================================================
# 4. 运行支付检查
# ==============================================================================
check_payment_callback()

# ==============================================================================
# 5. 登录页 (Airlock)
# ==============================================================================
if not st.session_state.user:
    col_spacer_l, col_main, col_spacer_r = st.columns([1, 1.5, 1])
    with col_main:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style='border:1px solid #6366f1; background:rgba(10,10,20,0.8); padding:40px; box-shadow:0 0 50px rgba(0,0,0,0.8); backdrop-filter:blur(10px); text-align:center;'>
            <h1 style='color:#6366f1; margin:0;'>XENOGENESIS</h1>
            <p style='color:#00ffcc; font-size:0.8em;'>INTELLIGENT LIFEFORM ENGINE v16.0</p>
            <hr style='border-color:#333;'>
        </div>
        """, unsafe_allow_html=True)
        
        tab_login, tab_reg = st.tabs(["[ AUTHENTICATE ]", "[ NEW SUBJECT ]"])
        with tab_login:
            st.write("")
            email = st.text_input("GENETIC ID", key="l_e")
            pwd = st.text_input("ACCESS KEY", type="password", key="l_p")
            st.write("")
            if st.button(">> INITIATE LINK <<", use_container_width=True): login_user(email, pwd)
        with tab_reg:
            st.write("")
            ne, np = st.text_input("NEW ID", key="r_e"), st.text_input("NEW KEY", type="password", key="r_p")
            st.write("")
            if st.button(">> IMPRINT DNA <<", use_container_width=True): register_user(ne, np)
    st.stop()

# ==============================================================================
# 6. 主控界面 (Void Deck)
# ==============================================================================
TIER_CONFIG = {
    "standard": {"count": 1, "label": "LVL.1 RESEARCHER", "style": "report-standard"},
    "silver":   {"count": 2, "label": "LVL.2 XENOLOGIST", "style": "report-silver"},
    "gold":     {"count": 3, "label": "LVL.3 DIRECTOR", "style": "report-gold"}
}
user_tier = st.session_state.tier
config = TIER_CONFIG.get(user_tier, TIER_CONFIG["standard"])

# --- 侧边栏 ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#00ffcc;'>SYSTEM STATUS</h2>", unsafe_allow_html=True)
    st.caption(f"ID: {st.session_state.user.email.split('@')[0]}")
    st.divider()
    st.markdown(f"**CLEARANCE: <span style='color:#6366f1'>{config['label']}</span>**", unsafe_allow_html=True)
    st.divider()
    if st.button(">> SEVER LINK <<"): logout()

# --- 主导航 ---
st.title("XENOGENESIS // TERMINAL")
tab_gen, tab_sub, tab_db = st.tabs(["[ 01: GENESIS ]", "[ 02: ACQUISITION ]", "[ 03: ARCHIVES ]"])

# --- TAB 1: 生成 (保留 V15 逻辑) ---
with tab_gen:
    col_input, col_viz = st.columns([2, 1])
    with col_input:
        genre = st.selectbox("ECOLOGICAL PARAMETER", ["Cosmic Horror", "Dark Fantasy", "Cybernetic Organism", "Folklore & Myth", "Post-Apocalyptic", "Surrealism"])
        user_input = st.text_area("SEED DATA INPUT", height=150, placeholder="// Enter conceptual keywords...")
    with col_viz:
        st.markdown(f"""
        <div style="border:1px dashed #333; padding:20px; height:100%; color:#666; font-size:0.8em;">
            <p>BATCH SIZE: <span style="color:#00ffcc">{config['count']}</span></p>
            <p>MODE: NARRATIVE INSPIRATION</p>
            <p>TIER: {user_tier.upper()}</p>
        </div>
        """, unsafe_allow_html=True)

    if st.button(">> EXECUTE GENESIS PROTOCOL <<", type="primary", use_container_width=True):
        if not user_input: st.warning(">> ERROR: NO SEED DATA")
        else:
            genai.configure(api_key=google_key)
            prompt = f"""
            IDENTITY: XENOGENESIS AI. GOAL: {config['count']} creatures. GENRE: {genre}. SEED: "{user_input}".
            FOCUS: Paradox, Metaphor, Sensory Horror. GOLD TIER: Final entity is ABSTRACT/METAPHYSICAL.
            OUTPUT FORMAT: Markdown Dossier.
            """
            with st.spinner('// COMPILING DNA...'):
                try:
                    res = genai.GenerativeModel('gemini-2.0-flash').generate_content(prompt)
                    st.session_state.current_result = res.text
                    st.session_state.current_input = f"[{genre}] {user_input}"
                except Exception as e: st.error(f"FAIL: {e}")

    if 'current_result' in st.session_state:
        st.markdown(f"<div style='background:rgba(5,5,10,0.9); border:1px solid #333; border-top:3px solid #6366f1; padding:30px; margin-top:20px;'><div style='font-family:Share Tech Mono; color:#a5b4fc;'>{st.session_state.current_result}</div></div>", unsafe_allow_html=True)
        if st.button(">> ARCHIVE <<"): save_archive(st.session_state.current_input, st.session_state.current_result)

# --- TAB 2: 商店/订阅 (核心新增) ---
with tab_sub:
    st.markdown("### >> CLEARANCE ACQUISITION PROTOCOL")
    st.markdown("Select a clearance level to upgrade your biological synthesis capabilities.")
    st.write("")
    
    col_std, col_slv, col_gld = st.columns(3)
    
    # Silver Plan
    with col_slv:
        st.markdown("""
        <div class='plan-card plan-silver'>
            <h3>SILVER CLASS</h3>
            <div class='price-tag'>$9 / mo</div>
            <p>2 Simultaneous Syntheses</p>
            <p>Standard Metaphysics</p>
            <p>Priority Archive Access</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(">> UPGRADE TO SILVER <<", use_container_width=True):
            url = create_checkout_session("silver")
            if url: st.link_button(">> PROCEED TO PAYMENT <<", url, use_container_width=True)

    # Gold Plan
    with col_gld:
        st.markdown("""
        <div class='plan-card plan-gold'>
            <h3 style='color:#FFD700'>GOLD CLASS</h3>
            <div class='price-tag'>$19 / mo</div>
            <p>3 Simultaneous Syntheses</p>
            <p><strong>BOSS / CONCEPT ENTITIES</strong></p>
            <p>Full Xenology Database</p>
            <p><em>Director Clearance</em></p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(">> UPGRADE TO GOLD <<", type="primary", use_container_width=True):
            url = create_checkout_session("gold")
            if url: st.link_button(">> PROCEED TO PAYMENT <<", url, use_container_width=True)

    # Current Plan Info
    with col_std:
        st.info(f"CURRENT CLEARANCE: {user_tier.upper()}")
        if user_tier == 'free' or user_tier == 'standard':
            st.markdown("*Basic access restricted to single entity synthesis.*")
        elif user_tier == 'gold':
            st.success("MAXIMUM CLEARANCE GRANTED.")

# --- TAB 3: 档案 ---
with tab_db:
    archives = load_archives()
    if not archives: st.caption("// DATABASE EMPTY //")
    else:
        for item in archives:
            with st.expander(f"FILE: {item['created_at'][:10]} | {item['title']}"):
                st.markdown(item['content'])
