import os
import streamlit as st
import requests
#Configuración de la URL de la API
BACKEND_BASE = os.getenv("BACKEND_URL", "http://localhost:8080")
API_URL = f"{BACKEND_BASE}/ask"

st.title("Watsonx.ai Q&A Tester")

if "history" not in st.session_state:
    st.session_state.history = [] 
if "sources" not in st.session_state:
    st.session_state.sources = []
if "question" not in st.session_state:
    st.session_state.question = ""

#Inputs de usuario
question = st.text_area("Enter your question about Watsonx.ai", height=100)
k = st.slider("Number of sources to retrieve (k)", min_value=1, max_value=10, value=3)

col1, col2 = st.columns(2)
with col1:
    if st.button("Ask"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            payload = {
                "question": question.strip(),
                "k": k,
                "history": st.session_state.history
            }
            try:
                resp = requests.post(API_URL, json=payload, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                # Actualizar estado
                st.session_state.history = data.get("history", [])
                st.session_state.sources = data.get("sources", [])
                st.session_state.question = ""
            except Exception as e:
                st.error(f"Error calling API: {e}")
with col2:
    if st.button("Reset chat"):
        st.session_state.history = []
        st.session_state.sources = []
        st.session_state.question = ""

# Mostrar conversación
st.subheader("Conversation")
for msg in st.session_state.history:
    role, text = msg.split(":", 1)
    display_role = "You" if role.strip().lower() == "user" else "Assistant"
    st.markdown(f"**{display_role}:** {text.strip()}")

# Mostrar fuentes de la última respuesta
if st.session_state.sources:
    st.subheader("Sources for the last answer")
    for idx, src in enumerate(st.session_state.sources, 1):
        st.markdown(f"{idx}. {src}")