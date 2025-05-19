import streamlit as st
from openai import OpenAI

# secrets.toml üzerinden API key çekiliyor
api_key = st.secrets["openai"]["api_key"]
client = OpenAI(api_key=api_key)

st.title("🧠 AI Text Summarizer")

user_input = st.text_area("Enter your text:", height=250)

if st.button("Summarize"):
    # Kullanıcıdan gelen metin boşsa uyarı ver
    if not user_input.strip():
        st.warning("Please enter a text.")
    else:
        with st.spinner("Generating the Summary..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a text summarizer."},
                        {"role": "user", "content": f"{user_input}"}
                    ],
                    temperature=0.7,
                    max_tokens=300,
                )
                st.success("Summary:")
                st.write(response.choices[0].message.content)

            except Exception as e:
                st.error(f"Error Occured: {e}")
