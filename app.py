import streamlit as st
import google.generativeai as genai
import os

# 1. SETUP & CONFIG
# Replace with your API Key (or use a second one if you want separate quotas!)
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Stock Consensus", layout="centered")

# Custom CSS for that clean iOS/Safari look you liked
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 1rem; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007AFF; color: white; }
    .agent-box { padding: 10px; border-radius: 10px; border-left: 5px solid #007AFF; margin-bottom: 10px; background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Stock Consensus")
st.caption("Multi-Agent Institutional Analysis")

# 2. THE INPUT
default_query = "What is the forecast for the S&P 500?"
user_query = st.text_input("Analysis Target:", value=default_query)

if st.button("Generate Consensus"):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        with st.spinner("Consulting the board..."):
            # SYSTEM PROMPT: The "Stock Conductor"
            conductor_prompt = f"""
            You are the 'Stock Conductor'. Lead a panel of 4 institutional experts 
            to analyze: {user_query}.
            
            Provide a response in exactly this format:
            
            ### 🏛️ THE PANEL SIGNALS
            * **The Macro Hawk:** [One sentence on interest rates/inflation impact]
            * **The Value Purist:** [One sentence on P/E ratios and fundamentals]
            * **The Growth Optimist:** [One sentence on innovation and earnings tailwinds]
            * **The Contrarian:** [One sentence on what the 'crowd' is missing]
            
            ### 📊 EXECUTIVE SUMMARY
            [A 3-sentence synthesis of the consensus]
            
            ### ⚖️ STRATEGIC DECISION MATRIX
            * **Risk Level:** [Low/Medium/High]
            * **Horizon:** [Short/Medium/Long Term]
            * **Final Signal:** [Accumulate/Hold/Trim/Avoid]
            """
            
            response = model.generate_content(conductor_prompt)
            st.markdown(response.text)

    except Exception as e:
        st.error("Quota reached or connection lost.")
        st.info("Tip: If you're using the Free Tier, consider using a separate API Key for this project to keep its quota independent from your Crypto app.")

# 3. FOOTER
st.divider()
st.caption("Data is for educational purposes. Consult a financial advisor.")