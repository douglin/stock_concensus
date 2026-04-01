import streamlit as st
import google.generativeai as genai
import yfinance as yf
import os
from datetime import datetime
from dotenv import load_dotenv

# --- 1. CONFIG & SECRETS ---
load_dotenv()
# This line makes it work both locally (.env) and on Streamlit Cloud (Secrets)
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Missing API Key. Check Streamlit Secrets or .env file.")
    st.stop()

genai.configure(api_key=api_key)
MODEL_ID = "gemini-3-flash-preview"
today_date = datetime.now().strftime("%B %d, %Y")

st.set_page_config(page_title="Institutional Stock Advisor", layout="wide")

# --- 2. LIVE DATA FEED ---
def get_market_data():
    tickers = {"S&P 500": "^GSPC", "Nasdaq": "^IXIC", "Brent Crude": "BZ=F"}
    results = {}
    for label, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="2d")
            price = hist['Close'].iloc[-1]
            change = ((price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            results[label] = (price, change)
        except:
            results[label] = (0.0, 0.0)
    return results

# --- 3. SIDEBAR: LIVE METRICS ---
with st.sidebar:
    st.header(f"📊 Market Snapshot")
    st.caption(f"Last Sync: {today_date}")
    data = get_market_data()
    for label, (val, chg) in data.items():
        st.metric(label, f"{val:,.2f}", f"{chg:+.2f}%")
    
    st.divider()
    st.info("💡 **ATL Tip:** Markets are currently volatile due to the Iran-Israel de-escalation headlines.")

# --- 4. MAIN UI ---
st.title("🏦 Investment Committee Consensus")
user_question = st.text_input("Ask the Board:", value="What's the forecast for the S&P 500?")

if st.button("Convene the Committee"):
    try:
        model = genai.GenerativeModel(MODEL_ID)
        sp_price = data.get("S&P 500", (0,0))[0]
        
        with st.spinner("Analyzing signals..."):
            prompt = f"""
            Question: {user_question}
            Date: {today_date}
            Context: S&P 500 is at {sp_price:,.2f}. 
            
            Instructions: Provide an ultra-concise institutional report for the SPECIFIC target.
            1. **The Conductor (Lead Partner):** Frame the high-level debate.
            2. **Macro Hawk:** Interest rates and energy impact.
            3. **Value Purist:** Fundamentals vs. 2026 multiples.
            4. **Growth Optimist:** AI and enterprise cloud tailwinds.
            5. **Risk Manager:** Black Swan geopolitical threats.
            6. **The Verdict:** 12-month Low/High and a one-word Action Signal.
            """
            response = model.generate_content(prompt)
            st.markdown("---")
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Error: {e}")