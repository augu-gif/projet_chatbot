import json
import spacy
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import numpy as np
from difflib import SequenceMatcher
import logging
from datetime import datetime
import re
from ..nlp.intent_classifier import IntentClassifier

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class IntentMatcher:
    def __init__(self, data_file: str = "legal_data.json", similarity_threshold: float = 0.5):
        """
        Initialise le détecteur d'intentions avec spaCy et le fichier de données
        
        Args:
            data_file: Chemin vers le fichier JSON contenant les données
            similarity_threshold: Seuil de similarité minimum (0-1)
        """
        self.data_file = data_file
        self.similarity_threshold = similarity_threshold
        self.knowledge_base = self._load_data()
        
        # Chargement du modèle spaCy français
        try:
            self.nlp = spacy.load("fr_core_news_md")
            logger.info("✅ Modèle spaCy fr_core_news_md chargé avec succès")
        except IOError:
            logger.error("❌ Erreur: Le modèle spaCy 'fr_core_news_md' n'est pas installé.")
            logger.info("📦 Installez-le avec: python -m spacy download fr_core_news_md")
            raise
        
        # Chargement du classificateur d'intentions
        model_path = Path("models/intent_classifier")
        if model_path.exists():
            self.intent_classifier = IntentClassifier.load(str(model_path))
            logger.info("✅ Classificateur d'intentions chargé")
        else:
            self.intent_classifier = None
            logger.warning("⚠️ Aucun modèle de classification d'intentions trouvé")
    
    def _load_data(self) -> Dict:
        """Charge les données depuis le fichier JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✅ Données chargées depuis {self.data_file}")
                logger.info(f"📊 {len(data.get('categories', {}))} catégories trouvées")
                return data
        except FileNotFoundError:
            logger.error(f"❌ Erreur: Fichier {self.data_file} non trouvé")
            raise
        except json.JSONDecodeError:
            logger.error(f"❌ Erreur: Format JSON invalide dans {self.data_file}")
            raise
    
    def _preprocess_text(self, text: str) -> str:
        """Prétraite le texte pour la comparaison"""
        # Conversion en minuscules et suppression des accents
        text = text.lower().strip()
        # Suppression de la ponctuation
        text = ''.join(c for c in text if c.isalnum() or c.isspace())
        return text
    
    def _calculate_string_similarity(self, text1: str, text2: str) -> float:
        """Calcule la similarité entre deux textes avec SequenceMatcher"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _calculate_vector_similarity(self, text1: str, text2: str) -> float:
        """Calcule la similarité vectorielle avec spaCy"""
        doc1 = self.nlp(text1)
        doc2 = self.nlp(text2)
        
        if doc1.has_vector and doc2.has_vector:
            return doc1.similarity(doc2)
        return 0.0
    
    def _calculate_keyword_match_score(self, user_input: str, keywords: List[str]) -> float:
        """Calcule un score basé sur la présence des mots-clés"""
        user_input = self._preprocess_text(user_input)
        user_words = set(user_input.split())
        
        # Score pour les mots-clés exacts
        exact_matches = sum(1 for keyword in keywords if self._preprocess_text(keyword) in user_words)
        
        # Score pour les mots-clés partiels
        partial_matches = sum(1 for keyword in keywords 
                            if any(self._preprocess_text(keyword) in word 
                                  for word in user_words))
        
        # Score pour les mots-clés similaires
        similar_matches = sum(1 for keyword in keywords 
                            if any(self._calculate_string_similarity(self._preprocess_text(keyword), word) > 0.8 
                                  for word in user_words))
        
        # Combinaison des scores avec des poids
        total_score = (
            exact_matches * 1.0 +      # Score complet pour les correspondances exactes
            partial_matches * 0.7 +    # Score partiel pour les correspondances partielles
            similar_matches * 0.5      # Score plus faible pour les similarités
        )
        
        # Normalisation du score
        max_possible_score = len(keywords) * 1.0
        return min(total_score / max_possible_score, 1.0) if max_possible_score > 0 else 0.0
    
    def find_best_match(self, user_input: str) -> Tuple[Optional[str], float, Optional[Dict]]:
        """
        Trouve la meilleure correspondance pour l'entrée utilisateur
        
        Args:
            user_input: Le texte saisi par l'utilisateur
            
        Returns:
            Tuple contenant:
            - L'ID de la catégorie correspondante (ou None)
            - Le score de confiance (0-1)
            - Les données de la catégorie (or None)
        """
        logger.info(f"🔍 Analyse de la requête: '{user_input}'")
        
        # Si le classificateur d'intentions est disponible, l'utiliser en premier
        if self.intent_classifier:
            intent, confidence = self.intent_classifier.predict(user_input)
            if confidence > self.similarity_threshold:
                logger.info(f"✅ Intention détectée par le classificateur: {intent} (score: {confidence:.2f})")
                
                # Si c'est une FAQ
                if intent.startswith("faq_"):
                    faq_id = intent[4:]  # Enlever le préfixe "faq_"
                    faq_data = self.knowledge_base.get("faq", {}).get(faq_id)
                    if faq_data:
                        return intent, confidence, faq_data
                
                # Si c'est une catégorie principale
                category_data = self.knowledge_base.get("categories", {}).get(intent)
                if category_data:
                    return intent, confidence, category_data
        
        # Si le classificateur n'est pas disponible ou n'a pas trouvé de correspondance,
        # utiliser la méthode traditionnelle
        user_input = self._preprocess_text(user_input)
        best_match = None
        best_score = 0.0
        best_category_data = None
        
        # Parcours des catégories principales
        for category_id, category in self.knowledge_base.get("categories", {}).items():
            logger.info(f"\n📌 Analyse de la catégorie: {category.get('title', category_id)}")
            
            # 1. Score des mots-clés
            keyword_score = self._calculate_keyword_match_score(
                user_input,
                category.get("keywords", [])
            )
            logger.info(f"  - Score mots-clés: {keyword_score:.2f}")
            
            # 2. Score des exemples
            example_scores = []
            for example in category.get("examples", {}).get("questions", []):
                example = self._preprocess_text(example)
                # Similarité de chaînes
                string_similarity = self._calculate_string_similarity(user_input, example)
                # Similarité vectorielle
                vector_similarity = self._calculate_vector_similarity(user_input, example)
                # Score combiné
                score = (string_similarity * 0.4) + (vector_similarity * 0.6)
                example_scores.append(score)
            
            example_score = max(example_scores) if example_scores else 0.0
            logger.info(f"  - Score exemples: {example_score:.2f}")
            
            # 3. Score des variations
            variation_scores = []
            for variation in category.get("examples", {}).get("variations", []):
                variation = self._preprocess_text(variation)
                # Similarité de chaînes
                string_similarity = self._calculate_string_similarity(user_input, variation)
                # Similarité vectorielle
                vector_similarity = self._calculate_vector_similarity(user_input, variation)
                # Score combiné
                score = (string_similarity * 0.4) + (vector_similarity * 0.6)
                variation_scores.append(score)
            
            variation_score = max(variation_scores) if variation_scores else 0.0
            logger.info(f"  - Score variations: {variation_score:.2f}")
            
            # Score final combiné
            final_score = (
                keyword_score * 0.5 +      # 50% pour les mots-clés
                example_score * 0.3 +      # 30% pour les exemples
                variation_score * 0.2       # 20% pour les variations
            )
            logger.info(f"  - Score final: {final_score:.2f}")
            
            if final_score > best_score:
                best_score = final_score
                best_match = category_id
                best_category_data = category
        
        # Parcours des FAQ
        for faq_id, faq in self.knowledge_base.get("faq", {}).items():
            logger.info(f"\n📌 Analyse de la FAQ: {faq.get('title', faq_id)}")
            
            # 1. Score des mots-clés
            keyword_score = self._calculate_keyword_match_score(
                user_input,
                faq.get("keywords", [])
            )
            logger.info(f"  - Score mots-clés: {keyword_score:.2f}")
            
            # 2. Score des exemples
            example_scores = []
            for example in faq.get("examples", {}).get("questions", []):
                example = self._preprocess_text(example)
                # Similarité de chaînes
                string_similarity = self._calculate_string_similarity(user_input, example)
                # Similarité vectorielle
                vector_similarity = self._calculate_vector_similarity(user_input, example)
                # Score combiné
                score = (string_similarity * 0.4) + (vector_similarity * 0.6)
                example_scores.append(score)
            
            example_score = max(example_scores) if example_scores else 0.0
            logger.info(f"  - Score exemples: {example_score:.2f}")
            
            # 3. Score des variations
            variation_scores = []
            for variation in faq.get("examples", {}).get("variations", []):
                variation = self._preprocess_text(variation)
                # Similarité de chaînes
                string_similarity = self._calculate_string_similarity(user_input, variation)
                # Similarité vectorielle
                vector_similarity = self._calculate_vector_similarity(user_input, variation)
                # Score combiné
                score = (string_similarity * 0.4) + (vector_similarity * 0.6)
                variation_scores.append(score)
            
            variation_score = max(variation_scores) if variation_scores else 0.0
            logger.info(f"  - Score variations: {variation_score:.2f}")
            
            # Score final combiné
            final_score = (
                keyword_score * 0.5 +      # 50% pour les mots-clés
                example_score * 0.3 +      # 30% pour les exemples
                variation_score * 0.2       # 20% pour les variations
            )
            logger.info(f"  - Score final: {final_score:.2f}")
            
            if final_score > best_score:
                best_score = final_score
                best_match = f"faq_{faq_id}"
                best_category_data = faq
        
        # Vérification du seuil de confiance
        if best_score < self.similarity_threshold:
            logger.info(f"❌ Aucune correspondance trouvée (meilleur score: {best_score:.2f} < {self.similarity_threshold})")
            return None, 0.0, None
        
        logger.info(f"✅ Meilleure correspondance: {best_match} (score: {best_score:.2f})")
        return best_match, best_score, best_category_data
    
    def get_response(self, user_input: str) -> str:
        """
        Obtient une réponse appropriée pour l'entrée utilisateur
        
        Args:
            user_input: Le texte saisi par l'utilisateur
            
        Returns:
            La réponse du chatbot
        """
        # Vérification des salutations
        greetings = ["bonjour", "salut", "hello", "bonsoir"]
        if user_input.lower() in greetings:
            return "Bonjour ! Je suis votre assistant pour les annonces légales. Comment puis-je vous aider ?"
        
        # Vérification des adieux
        goodbyes = ["au revoir", "bye", "adieu", "à bientôt"]
        if user_input.lower() in goodbyes:
            return "Au revoir ! N'hésitez pas à revenir si vous avez d'autres questions."
        
        category_id, confidence, category_data = self.find_best_match(user_input)
        
        if category_data and category_data.get("responses"):
            # Sélection aléatoire d'une réponse
            import random
            response = random.choice(category_data["responses"])
            if isinstance(response, dict):
                return response.get("content", "Je ne comprends pas votre question.")
            return response
        
        return "Je n'ai pas compris votre demande. Pouvez-vous reformuler ?"
    
    def get_category_info(self, category_id: str) -> Optional[Dict]:
        """Récupère les informations d'une catégorie par son ID"""
        return self.knowledge_base.get("categories", {}).get(category_id)
    
    def get_all_categories(self) -> Dict:
        """Récupère toutes les catégories"""
        return self.knowledge_base.get("categories", {})
    
    def get_metadata(self) -> Dict:
        """Récupère les métadonnées du fichier"""
        return self.knowledge_base.get("metadata", {}) 