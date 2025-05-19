import streamlit as st
from openai import OpenAI
from streamlit_oauth import OAuth2Component
import jwt

# ========== Redirect Param Kontrolü ==========
params = st.experimental_get_query_params()

if "login" in params:
    # Login sonrası URL parametresini temizle
    st.experimental_set_query_params()

# ========== AUTHENTICATION ==========
client_id = st.secrets["google"]["client_id"]
client_secret = st.secrets["google"]["client_secret"]

oauth2 = OAuth2Component(
    client_id=client_id,
    client_secret=client_secret,
    authorize_endpoint="https://accounts.google.com/o/oauth2/auth",
    token_endpoint="https://oauth2.googleapis.com/token"
)

redirect_uri = "https://ai-text-summarizer-demo.streamlit.app/"  # Cloud'da deploy ediyorsan burayı değiştir

# Google ile login butonu
result = oauth2.authorize_button(
    name="Login with Google",
    icon="🔐",
    redirect_uri=redirect_uri,
    scope="openid email profile",
    key="google_oauth"
)

# Login işlemi başarılı olursa
if result:
    id_token = result["token"]["id_token"]
    decoded = jwt.decode(id_token, options={"verify_signature": False})

    # Kullanıcı bilgisini session'a kaydet
    st.session_state["user"] = {
        "name": decoded["name"],
        "email": decoded["email"],
        "picture": decoded["picture"]
    }

    # URL'e login paramı ekleyerek sayfayı yeniden yüklemesini sağla
    st.query_params(login="1")
    st.stop()

# ========== UI ==========
st.title("🧠 AI Text Summarizer")

# Eğer kullanıcı login olmuşsa
if "user" in st.session_state:
    user = st.session_state["user"]
    st.success(f"Welcome, {user['name']} 👋")
    st.image(user["picture"], width=80)
else:
    st.warning("You need to log in to use the summarizer.")

# ========== OpenAI Ayarı ==========
api_key = st.secrets["openai"]["api_key"]
client = OpenAI(api_key=api_key)

# ========== Metin Girişi ==========
user_input = st.text_area("Enter your text:", height=250)

# ========== Summarize Butonu ==========
if st.button("Summarize"):
    if "user" not in st.session_state:
        st.error("You must be logged in to summarize text.")
    elif not user_input.strip():
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
