from typing import Dict, List, Optional, Any
from .intent_matcher import IntentMatcher

class LegalAnnouncementChatbot:
    def __init__(self, data_file: str = "legal_data.json"):
        """
        Initialise le chatbot avec le détecteur d'intentions
        
        Args:
            data_file: Chemin vers le fichier JSON contenant les données
        """
        self.intent_matcher = IntentMatcher(data_file)
        self.conversation_history = []
    
    def get_response(self, user_message: str) -> str:
        """Génère une réponse appropriée à partir du message utilisateur"""
        # Ajout du message à l'historique
        self.conversation_history.append({"role": "user", "content": user_message})
        
        # Obtention de la réponse via le détecteur d'intentions
        response = self.intent_matcher.get_response(user_message)
        
        # Ajout de la réponse à l'historique
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def get_conversation_history(self) -> List[Dict]:
        """Retourne l'historique de la conversation"""
        return self.conversation_history
    
    def get_category_info(self, category_id: str) -> Optional[Dict]:
        """Récupère les informations d'une catégorie"""
        return self.intent_matcher.get_category_info(category_id)
    
    def get_all_categories(self) -> Dict:
        """Récupère toutes les catégories"""
        return self.intent_matcher.get_all_categories()
    
    def get_metadata(self) -> Dict:
        """Récupère les métadonnées"""
        return self.intent_matcher.get_metadata() 