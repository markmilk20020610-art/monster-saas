import streamlit as st
import google.generativeai as genai
import sys

st.set_page_config(page_title="System Diagnostics", page_icon="🔧")

st.title("🔧 VANGUARD SYSTEM DIAGNOSTICS")

# 1. 检查驱动版本
try:
    lib_version = genai.__version__
except:
    lib_version = "Unknown (Too Old)"

st.write(f"**🛠️ AI Driver Version:** `{lib_version}`")
st.info("💡 Note: If version is below 0.7.0, you MUST update requirements.txt")

# 2. 检查可用模型
st.write("---")
st.write("### 📡 SCANNING FOR MODELS...")

try:
    # 尝试连接谷歌
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    found_any = False
    # 列出所有模型
    for m in genai.list_models():
        # 只显示能生成文本的模型
        if 'generateContent' in m.supported_generation_methods:
            st.success(f"✅ FOUND: `{m.name}`")
            found_any = True
            
    if not found_any:
        st.error("❌ No text generation models found. Check API Key or Region.")

except Exception as e:
    st.error(f"⚠️ CRITICAL ERROR: {e}")
    st.warning("Please check your .streamlit/secrets.toml file.")
