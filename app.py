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
        
        with st.spinner("Board is in session..."):
            prompt = f"""
            Target: {user_question}
            Date: {today_date} | S&P 500: {sp_price:,.2f}
            
            Instructions: Act as an Investment Committee. Provide a sophisticated, high-density report. 
            FORMAT: Use 2-3 precise bullet points per agent. Avoid conversational filler or intros.

            1. **The Conductor:** State the primary technical/fundamental conflict for this target.
            2. **The Macro Hawk:** Impact of $107 oil and the current 4.3% yield environment.
            3. **The Value Purist:** P/E multiples vs. historical 5-year averages for this asset.
            4. **The Growth Optimist:** Specific 2026/2027 enterprise catalysts and AI integration.
            5. **The Risk Manager:** Primary 'Black Swan' or geopolitical risk to the supply chain.
            6. **The Verdict:** - A 12-month Price Range (Low/High).
               - A one-sentence final justification.
               - One-word Signal: (ACCUMULATE / NEUTRAL / TRIM).
            """
            
            # We remove the 'max_tokens' restriction to let it finish its thoughts
            response = model.generate_content(prompt)
            st.markdown("---")
            st.markdown(response.text)
    except Exception as e:
        st.error(f"Technical Error: {e}")