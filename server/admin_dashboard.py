import streamlit as st
import requests
import pandas as pd

API_BASE_URL = "http://localhost:8000/api"

st.title("🌴🔮 Admin Dashboard - Twilio Service")

# Function to make API requests safely
def safe_api_request(method, endpoint, **kwargs):
    try:
        response = requests.request(method, f"{API_BASE_URL}{endpoint}", timeout=10, **kwargs)
        response.raise_for_status()  # Raise an HTTPError for bad status codes (4xx, 5xx)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Failed to connect to the API. Please check the server status.")
    except requests.exceptions.Timeout:
        st.error("⏳ The API request timed out. Please try again later.")
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ HTTP error occurred: {e.response.status_code} - {e.response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"🚨 An unexpected error occurred: {e}")
    return None


# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["📋 View Subscribers", "🌙 View Nights", "📝 Post Update"])

# 📋 View Subscribers Tab
with tab1:
    st.header("📋 All Subscribers")
    subscribers = safe_api_request("GET", "/subscribers")
    if subscribers is not None:
        if isinstance(subscribers, list) and len(subscribers) > 0:
            st.dataframe(pd.DataFrame(subscribers))
        else:
            st.info("ℹ️ No subscribers found.")

# 🌙 View Nights Tab
with tab2:
    st.header("🌙 All Nights")
    nights = safe_api_request("GET", "/nights")
    if nights is not None:
        if isinstance(nights, list) and len(nights) > 0:
            st.dataframe(pd.DataFrame(nights))
        else:
            st.info("ℹ️ No nights found.")

# 📝 Post Update Tab
with tab3:
    st.header("📝 Post Update")
    update_message = st.text_input("Enter Update Message")
    if st.button("Post Update"):
        if update_message.strip():
            response = safe_api_request("POST", "/updates", json={"message": update_message})
            if response is not None:
                st.success("✅ Update posted successfully!")
        else:
            st.warning("⚠️ Please enter a valid update message before posting.")
