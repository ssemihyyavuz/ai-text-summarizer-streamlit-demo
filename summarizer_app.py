import streamlit as st
from openai import OpenAI
import jwt
from urllib.parse import urlencode, parse_qs
import requests
import os

# ========== GOOGLE OAUTH2 CONFIG ==========
client_id = st.secrets["google"]["client_id"]
client_secret = st.secrets["google"]["client_secret"]
redirect_uri = "https://ai-text-summarizer-app-demo.streamlit.app/"  # Deploy URL

auth_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://oauth2.googleapis.com/token"
userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"

# ========== HANDLE AUTH FLOW ==========
code = st.query_params.get("code", [None])[0]

if code and "user" not in st.session_state:
    # Step 1: Exchange code for access token
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    token_response = requests.post(token_url, data=data)
    token_json = token_response.json()

    access_token = token_json.get("access_token")
    id_token = token_json.get("id_token")

    # Step 2: Get user info
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info = requests.get(userinfo_url, headers=headers).json()

    # Step 3: Store user in session state
    st.session_state["user"] = {
        "name": user_info.get("name"),
        "email": user_info.get("email"),
        "picture": user_info.get("picture")
    }

    # Step 4: Clean up URL
    st.query_params.clear()
    st.rerun()

# ========== UI ==========
st.title("🧠 AI Text Summarizer")

if "user" not in st.session_state:
    # Login button
    params = urlencode({
        "client_id": client_id,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": redirect_uri,
        "access_type": "offline",
        "prompt": "consent"
    })
    login_link = f"{auth_url}?{params}"
    st.markdown(f"[Login with Google]({login_link})", unsafe_allow_html=True)
    st.stop()

# Show user info
user = st.session_state["user"]

# Eğer isim yoksa varsayılana düş
name = user.get("name", "User")
st.success(f"Welcome, {name} 👋")

# Eğer profil fotoğrafı varsa göster
if user.get("picture"):
    st.image(user["picture"], width=80)

# ========== OPENAI API ==========
api_key = st.secrets["openai"]["api_key"]
client = OpenAI(api_key=api_key)

# ========== INPUT & SUMMARIZATION ==========
user_input = st.text_area("Enter your text:", height=250)

if st.button("Summarize"):
    if not user_input.strip():
        st.warning("Please enter a text.")
    else:
        with st.spinner("Generating the Summary..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful text summarizer."},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.7,
                    max_tokens=300,
                )
                st.success("Summary:")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error Occurred: {e}")
