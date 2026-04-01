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
        
        with st.spinner("Generating Board Matrix..."):
            prompt = f"""
            Target: {user_question}
            Context: S&P 500 @ {sp_price:,.2f}. Date: {today_date}.
            
            Instructions: Provide a high-density Markdown TABLE. 
            STRICT: One punchy sentence per cell. NO conversational filler.

            | Expert | Core Institutional Insight |
            | :--- | :--- |
            | **Macro Hawk** | Impact of $107 oil and 4.3% yields on this target. |
            | **Value Purist** | Valuation vs. 5-year average multiples. |
            | **Growth Optimist** | 2026/2027 enterprise/AI catalysts. |
            | **Risk Manager** | Primary 'Black Swan' or supply chain threat. |
            | **THE VERDICT** | [Price Range] + One-sentence summary + [SIGNAL]. |
            """
            
            response = model.generate_content(prompt)
            st.markdown("---")
            # This renders a clean, professional table in Streamlit
            st.markdown(response.text)
            
    except Exception as e:
        st.error(f"Matrix Generation Error: {e}")