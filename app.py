import streamlit as st
import google.generativeai as genai
import time

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="VANGUARD | Xeno-Archives",
    page_icon="☢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. 样式 ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .report-container {
        font-family: 'Courier New', Courier, monospace;
        color: #33ff00;
        background-color: #000000;
        padding: 30px;
        border: 1px solid #33ff00;
        box-shadow: 0 0 20px rgba(51, 255, 0, 0.15);
        margin-top: 20px;
        border-radius: 5px;
    }
    .warning-box {
        background-color: #330000;
        color: #ff3333;
        padding: 10px;
        border: 1px solid #ff0000;
        text-align: center;
        font-weight: bold;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 安全获取 Key ---
try:
    my_secret_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("⛔ SYSTEM ERROR: Secrets not configured.")
    st.stop()

# --- 4. 商业逻辑 ---
VALID_ACCESS_CODES = ["HUNTER-2026", "VIP-8888", "TEST-FREE"]

if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

# --- 5. 侧边栏 ---
with st.sidebar:
    st.title("☢️ VANGUARD PRO")
    st.caption("FAILSAFE SYSTEM: ONLINE")
    st.markdown("---")
    
    user_code = st.text_input("🔑 ENTER ACCESS CODE:", type="password")
    
    if user_code in VALID_ACCESS_CODES:
        st.success("✅ ACCESS GRANTED")
        access_granted = True
    elif user_code:
        st.error("⛔ INVALID CODE")
        access_granted = False
    else:
        st.info("🔒 AUTHENTICATION REQUIRED")
        access_granted = False
        
    st.markdown("---")
    doc_type = st.selectbox("ARCHIVE TYPE", ["NECROPSY REPORT", "RECOVERED AUDIO", "SCP PROTOCOL"])
    clearance = st.select_slider("SECURITY CLEARANCE", options=["LEVEL 1", "LEVEL 2", "LEVEL 3", "OMNI"])

# --- 6. 主界面 ---
st.title("🗄️ CLASSIFIED XENO-ARCHIVES")

if not access_granted:
    st.warning("⚠️ RESTRICTED ACCESS")
    st.stop()

st.markdown("**INSTRUCTION:** Enter description (Chinese accepted). System will auto-translate.")
user_input = st.text_area("TARGET SUBJECT:", height=100)
generate_btn = st.button("INITIATE RETRIEVAL", type="primary")

# --- 7. 核心逻辑：自动漫游模型 ---
def try_generate(model_name, prompt):
    """尝试使用指定模型生成，如果失败返回错误信息"""
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response, None # 成功
    except Exception as e:
        return None, str(e) # 失败

if generate_btn and user_input:
    
    # 稍微冷却一下 (3秒)
    time.sleep(1) 
    
    genai.configure(api_key=my_secret_key)
    
    # 🟢 备选模型列表（按优先级排序）
    # 1. Flash Latest (通常最稳，额度最高)
    # 2. Gemini 2.0 Flash (最新，但容易限速)
    # 3. Gemini Pro (保底)
    model_list = [
        'gemini-flash-latest', 
        'gemini-2.0-flash', 
        'gemini-1.5-flash-latest',
        'gemini-pro'
    ]
    
    success = False
    final_response = None
    
    # 构建 Prompt
    prompt = f"""
    **SYSTEM ROLE**: Central mainframe of 'Vanguard'.
    **USER INPUT**: "{user_input}"
    **MODE**: {doc_type}
    **CLEARANCE**: {clearance}
    
    **CONSTRAINT**: 
    - OUTPUT MUST BE 100% IN NATIVE ENGLISH. 
    - No Chinese in output.
    
    **REDACTION**:
    - If Clearance is LEVEL 1/2: Hide sensitive data with '████'.
    - If OMNI: Show ALL.
    
    **CONTENT**:
    1. HEADER (ID, Date, Loc)
    2. MAIN DOSSIER (Sci-Fi Tone, Metrics)
    3. 🧬 EVOLUTION (2 stages)
    4. 🎒 ASSETS (Loot & Hook)
    """

    with st.spinner('SEARCHING AVAILABLE NEURAL LINKS...'):
        # 循环尝试模型
        for model_name in model_list:
            status_placeholder = st.empty()
            status_placeholder.caption(f"Trying connection node: {model_name}...")
            
            response, error = try_generate(model_name, prompt)
            
            if response:
                final_response = response
                success = True
                status_placeholder.success(f"Connected via {model_name}")
                time.sleep(0.5)
                status_placeholder.empty()
                break # 成功了就跳出循环
            else:
                # 如果是 429 (限速)，打印警告并继续尝试下一个
                if "429" in error:
                    st.warning(f"⚠️ Node {model_name} busy (Rate Limit). Rerouting...")
                # 如果是 404 (找不到)，继续下一个
                elif "404" in error:
                    st.warning(f"⚠️ Node {model_name} offline. Rerouting...")
                else:
                    st.error(f"⚠️ Node {model_name} failed: {error}")
    
    # 结果展示
    if success and final_response:
        st.markdown('<div class="warning-box">⚠️ TOP SECRET // NOFORN</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-container">{final_response.text}</div>', unsafe_allow_html=True)
        st.download_button("💾 DOWNLOAD FILE", final_response.text, "vanguard_report.md")
    else:
        st.error("❌ ALL NODES FAILED. Please wait 1 minute and try again.")
        st.caption("系统繁忙，所有模型都在冷却中。请稍等片刻。")
