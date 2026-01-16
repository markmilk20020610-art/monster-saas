import streamlit as st
import google.generativeai as genai

# 页面基础设置
st.set_page_config(page_title="VANGUARD | Xeno-Archives", page_icon="🧬", layout="wide")

# 注入一点“黑客帝国”风格的CSS
st.markdown("""
<style>
    .report-font { font-family: 'Courier New', monospace; color: #e0e0e0; background-color: #1e1e1e; padding: 20px; border-left: 5px solid #ff4b4b; }
</style>
""", unsafe_allow_html=True)

# 侧边栏：输入钥匙的地方
with st.sidebar:
    st.title("🧬 VANGUARD SYSTEM")
    st.markdown("---")
    # 这里就是你刚才申请的 Key 发挥作用的地方
    api_key = st.text_input("输入你的 Google API Key:", type="password")
    
    st.markdown("### 参数设置")
    doc_type = st.selectbox("文档类型", ["尸检报告 (Necropsy Report)", "遭遇记录 (Encounter Log)", "收容协议 (Containment Protocol)"])
    tone_level = st.slider("恐怖等级 (1-5)", 1, 5, 4)

# 主界面
st.title("📂 机密档案生成器 (Xeno-Archives)")
st.write("输入核心概念，生成一份绝密的异常生物档案。")

user_input = st.text_area("输入生物特征 (中文即可，例如：寄生在声带里的深海蠕虫):", height=100)
generate_btn = st.button("生成档案 (GENERATE)", type="primary")

# 核心逻辑
if generate_btn and user_input and api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest') 
        
        with st.spinner('正在解密 Vanguard 数据库...'):
            # 上帝提示词
            prompt = f"""
            **ROLE**: You are Dr. Aris Thorne, chief pathologist for a secret organization 'Vanguard'.
            **TASK**: Write a **{doc_type}** for: "{user_input}".
            **RULES**:
            1. Format: Official Classified Document. Include ID, Date, Location.
            2. Content: Use pseudo-scientific jargon (Latin names, biological metrics).
            3. Tone: Cold, clinical, horror level {tone_level}/5.
            4. Redaction: Use '████' to hide sensitive info.
            5. **OUTPUT LANGUAGE**: English (for the main report) followed by a short Chinese summary.
            """
            response = model.generate_content(prompt)
            
            st.success("档案检索成功")
            st.markdown(f'<div class="report-font">{response.text}</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"错误: {e}")
elif generate_btn and not api_key:
    st.warning("⚠️ 请在左侧边栏输入你的 API Key")
