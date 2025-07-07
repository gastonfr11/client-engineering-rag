import streamlit as st
import requests

#Configuración de la URL de la API
API_URL = "http://localhost:8080/ask"

st.title("Watsonx.ai Q&A Tester")

#Inputs de usuario
question = st.text_area("Enter your question about Watsonx.ai", height=100)
k = st.slider("Number of passages to retrieve (k)", min_value=1, max_value=10, value=3)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        # Llamada al endpoint /ask
        payload = {"question": question, "k": k}
        try:
            resp = requests.post(API_URL, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            st.error(f"Error calling API: {e}")
        else:
            # Mostrar respuesta
            st.subheader("Answer")
            st.write(data["answer"])
            
            st.subheader("Sources")
            for i, src in enumerate(data["sources"], 1):
                st.markdown(f"**{i}.** {src}")
