import streamlit as st
from src.core.chatbot import LegalAnnouncementChatbot

st.set_page_config(page_title="Chatbot Annonces Légales", page_icon="💬")
st.title("💬 Chatbot - Annonces Légales")

# Initialisation du chatbot
chatbot = LegalAnnouncementChatbot(data_file="legal_data.json")

# Zone de saisie
question = st.text_input("Pose ta question sur les annonces légales :")

if question:
    reponse = chatbot.get_response(question)
    st.markdown(f"**Réponse :** {reponse}")
