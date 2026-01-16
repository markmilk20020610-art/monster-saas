import streamlit as st
import google.generativeai as genai
import time

# --- 1. 页面与CSS配置 ---
st.set_page_config(page_title="VANGUARD | Xeno-Archives", page_icon="☢️", layout="wide")

# CSS: 增加了蓝色和黄色的特殊区域，用于显示“进化”和“战利品”
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    
    /* 核心报告：黑底绿字 */
    .report-container {
        font-family: 'Courier New', Courier, monospace;
        color: #33ff00;
        background-color: #000000;
        padding: 25px;
        border: 1px solid #33ff00;
        box-shadow: 0 0 10px rgba(51, 255, 0, 0.1);
        margin-bottom: 20px;
    }
    
    /* 扩展模块：进化潜力 (蓝青色风格) */
    .evo-box {
        font-family: 'Courier New', Courier, monospace;
        color: #00e5ff;
        background-color: #001a20;
        padding: 15px;
        border-left: 5px solid #00e5ff;
        margin-top: 10px;
    }

    /* 扩展模块：战利品 (琥珀色风格) */
    .loot-box {
        font-family: 'Courier New', Courier, monospace;
        color: #ffcc00;
        background-color: #1a1500;
        padding: 15px;
        border-left: 5px solid #ffcc00;
        margin-top: 10px;
    }

    .warning-text { color: red; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. 逻辑设置 ---
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

# 模拟密码库
VALID_ACCESS_CODES = ["HUNTER-2026", "VIP-8888", "TEST-FREE"]

# 获取 API Key
try:
    my_secret_key = st.secrets["GOOGLE_API_KEY"]
except:
    my_secret_key = None

# --- 3. 侧边栏 ---
with st.sidebar:
    st.title("☢️ VANGUARD V5.0")
    st.caption("FULL CAMPAIGN MODE")
    st.markdown("---")
    
    user_code = st.text_input("🔑 ENTER ACCESS CODE:", type="password")
    
    if user_code in VALID_ACCESS_CODES:
        st.success("✅ ACCESS GRANTED")
        access_granted = True
    else:
        st.info("🔒 SYSTEM LOCKED")
        access_granted = False
        
    st.markdown("---")
    doc_type = st.selectbox("ARCHIVE TYPE", ["NECROPSY_REPORT", "AUDIO_TRANSCRIPT", "CONTAINMENT_PROTOCOL"])
    clearance = st.select_slider("CLEARANCE", options=["L1", "L2", "L3", "OMNI"])

# --- 4. 主界面 ---
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")

if not access_granted:
    st.warning("Please purchase Access Code to unlock terminal.")
    st.stop()

user_input = st.text_area("TARGET DESCRIPTION:", height=100)
generate_btn = st.button("INITIATE PROTOCOL", type="primary")

if generate_btn and user_input:
    # 防刷冷却 (10秒)
    current_time = time.time()
    if current_time - st.session_state.last_request_time < 10:
        st.error(f"⚠️ SYSTEM OVERHEAT: Please wait {10 - int(current_time - st.session_state.last_request_time)}s.")
        st.stop()
    st.session_state.last_request_time = current_time

    if not my_secret_key:
        st.error("Admin Key Error")
        st.stop()

    genai.configure(api_key=my_secret_key)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner('ANALYZING EVOLUTIONARY TRAJECTORIES...'):
            # --- 🧠 V5.0 Prompt: 增加了两个必须的扩展板块 ---
            prompt = f"""
            **ROLE**: Central computer of secret org 'Vanguard'.
            **USER INPUT**: "{user_input}"
            **MODE**: {doc_type}
            
            **TASK 1: MAIN REPORT (The Core)**
            - Write a creative, horror-sci-fi style report.
            - Include specific data (metrics, dimensions).
            - Output format: HTML compatible Markdown.
            
            **TASK 2: EVOLUTIONARY POTENTIAL (The Twist)**
            - Create a section titled "🧬 PROJECTED METAMORPHOSIS".
            - Describe 2 possible future forms if the entity is not contained (e.g., "If exposed to radiation, it grows wings").
            - Describe a "Trigger Event" that causes this change.
            
            **TASK 3: ASSETS & HOOKS (The Loot)**
            - Create a section titled "🎒 RECOVERABLE ASSETS".
            - List 2-3 specific "Loot Drops" (organs/items) and what they can be used for (e.g., "Acid Gland: Can be crafted into corrosive ammo").
            - List 1 "Plot Hook" (e.g., "Rumor has it this creature guards a sunken submarine").
            
            **MANDATORY**: End with 'TRANSLATED SUMMARY' in Chinese.
            """
            
            response = model.generate_content(prompt)
            
            # --- 解析与展示 (简单的文本分割，为了分别套用样式) ---
            # 这里我们让 AI 把所有内容生成在一块，然后我们用不同的 CSS 框把它包起来
            # 为了简化代码，我们将整个回答放入主框，但通过 Prompt 要求 AI 使用特定的标题
            # 这样用户阅读时会有很好的分层感
            
            st.markdown(f'<div class="report-container">{response.text}</div>', unsafe_allow_html=True)
            
            # 额外的视觉提示
            st.info("💡 TIP: The 'Projected Metamorphosis' data is theoretical. Proceed with caution.")

    except Exception as e:
        st.error(f"Error: {e}")
