from .data.data_manager import DataManager
from .core.chatbot import LegalAnnouncementChatbot
from .ui.chatbot_gui import ChatbotGUI

def main():
    """Point d'entrée principal de l'application"""
    # Initialisation du chatbot avec le chemin du fichier JSON
    chatbot = LegalAnnouncementChatbot("legal_data.json")
    
    # Lancement de l'interface graphique
    gui = ChatbotGUI(chatbot)
    gui.run()

if __name__ == "__main__":
    main() 