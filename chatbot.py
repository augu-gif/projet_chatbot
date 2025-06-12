import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
import difflib
import spacy
from spacy.matcher import Matcher
import numpy as np
from .data_manager import DataManager

class LegalAnnouncementChatbot:
    def __init__(self, data_manager: DataManager):
        """
        Initialise le chatbot avec un fichier de données JSON et le modèle spaCy
        
        Args:
            data_manager: Instance de DataManager pour gérer les données
        """
        self.data_manager = data_manager
        self.knowledge_base = data_manager.knowledge_base
        self.conversation_history = []
        
        # Chargement du modèle spaCy français
        try:
            self.nlp = spacy.load("fr_core_news_md")
            print("✅ Modèle spaCy fr_core_news_md chargé avec succès")
        except IOError:
            print("❌ Erreur: Le modèle spaCy 'fr_core_news_md' n'est pas installé.")
            print("📦 Installez-le avec: python -m spacy download fr_core_news_md")
            raise
        
        # Initialisation du matcher pour les patterns spécifiques
        self.matcher = Matcher(self.nlp.vocab)
        self.setup_patterns()
        
        self.load_data()
        
    def load_data(self):
        """Charge les données depuis le fichier JSON"""
        try:
            with open(self.data_manager.data_file, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            print(f"✅ Données chargées depuis {self.data_manager.data_file}")
        except FileNotFoundError:
            print(f"⚠️  Fichier {self.data_manager.data_file} non trouvé. Utilisation des données par défaut.")
            self.create_default_data()
        except json.JSONDecodeError:
            print(f"❌ Erreur dans le format JSON de {self.data_manager.data_file}")
            self.create_default_data()
    
    def create_default_data(self):
        """Crée un fichier de données par défaut"""
        default_data = {
            "categories": {
                "creation_entreprise": {
                    "name": "Création d'entreprise",
                    "keywords": ["création", "entreprise", "société", "statuts", "immatriculation"],
                    "responses": [
                        "Pour créer une entreprise, vous devez publier un avis de constitution dans un journal d'annonces légales.",
                        "La publication doit contenir : dénomination sociale, forme juridique, capital, siège social, objet social, durée, gérant."
                    ]
                },
                "modification_statuts": {
                    "name": "Modification des statuts",
                    "keywords": ["modification", "statuts", "changement", "adresse", "capital"],
                    "responses": [
                        "Toute modification des statuts doit faire l'objet d'une publication légale.",
                        "Les modifications courantes concernent : changement d'adresse, augmentation de capital, nomination de dirigeants."
                    ]
                },
                "dissolution": {
                    "name": "Dissolution",
                    "keywords": ["dissolution", "liquidation", "fermeture", "cessation"],
                    "responses": [
                        "La dissolution d'une société nécessite une publication d'avis de dissolution.",
                        "Vous devez publier l'avis dans les 30 jours suivant la décision de dissolution."
                    ]
                }
            },
            "faq": {
                "tarifs": {
                    "question": "Quels sont les tarifs des annonces légales ?",
                    "answer": "Les tarifs varient selon la longueur de l'annonce et le département. Contactez-nous pour un devis personnalisé."
                },
                "delais": {
                    "question": "Quels sont les délais de publication ?",
                    "answer": "Les annonces peuvent être publiées sous 24h après validation du contenu et paiement."
                },
                "juridictions": {
                    "question": "Dans quels départements publiez-vous ?",
                    "answer": "Nous couvrons tous les départements français. Précisez votre département pour connaître les journaux habilités."
                }
            },
            "contact": {
                "email": "contact@annonces-legales.fr",
                "telephone": "01 23 45 67 89",
                "horaires": "Du lundi au vendredi, 9h-18h"
            }
        }
        
        # Sauvegarde des données par défaut
        with open(self.data_manager.data_file, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        
        self.knowledge_base = default_data
        print(f"📁 Fichier {self.data_manager.data_file} créé avec des données par défaut")
    
    def setup_patterns(self):
        """Configure les patterns spécifiques pour le matcher spaCy"""
        # Patterns pour la création d'entreprise
        creation_patterns = [
            [{"LOWER": {"IN": ["créer", "création", "créé"]}}],
            [{"LOWER": "nouvelle"}, {"LOWER": {"IN": ["entreprise", "société"]}}],
            [{"LOWER": {"IN": ["statuts", "immatriculation"]}}],
        ]
        
        # Patterns pour les modifications
        modification_patterns = [
            [{"LOWER": {"IN": ["modifier", "modification", "changement"]}}],
            [{"LOWER": "changer"}, {"LOWER": {"IN": ["adresse", "siège"]}}],
            [{"LOWER": {"IN": ["augmentation", "réduction"]}, "LOWER": "capital"}],
        ]
        
        # Patterns pour la dissolution
        dissolution_patterns = [
            [{"LOWER": {"IN": ["dissolution", "fermer", "fermeture"]}}],
            [{"LOWER": {"IN": ["liquidation", "cessation"]}}],
        ]
        
        # Ajout des patterns au matcher
        self.matcher.add("CREATION", creation_patterns)
        self.matcher.add("MODIFICATION", modification_patterns)
        self.matcher.add("DISSOLUTION", dissolution_patterns)
    
    def analyze_with_spacy(self, text: str) -> Dict:
        """Analyse le texte avec spaCy pour extraire des informations"""
        doc = self.nlp(text)
        
        analysis = {
            "entities": [],
            "tokens": [],
            "lemmas": [],
            "pos_tags": [],
            "patterns": [],
            "similarity_vector": doc.vector
        }
        
        # Extraction des entités nommées
        for ent in doc.ents:
            analysis["entities"].append({
                "text": ent.text,
                "label": ent.label_,
                "description": spacy.explain(ent.label_)
            })
        
        # Extraction des tokens, lemmes et POS tags
        for token in doc:
            if not token.is_stop and not token.is_punct and len(token.text) > 2:
                analysis["tokens"].append(token.text.lower())
                analysis["lemmas"].append(token.lemma_.lower())
                analysis["pos_tags"].append(token.pos_)
        
        # Recherche de patterns
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            pattern_name = self.nlp.vocab.strings[match_id]
            analysis["patterns"].append({
                "pattern": pattern_name,
                "text": doc[start:end].text
            })
        
        return analysis
    
    def preprocess_message(self, message: str) -> Dict:
        """Prétraite le message utilisateur avec spaCy"""
        # Analyse spaCy
        spacy_analysis = self.analyze_with_spacy(message)
        
        return {
            "original": message,
            "cleaned": message.lower().strip(),
            "spacy_analysis": spacy_analysis
        }
    
    def find_best_match(self, user_message: str) -> Optional[Dict]:
        """Trouve la meilleure correspondance dans la base de connaissances avec spaCy"""
        processed_message = self.preprocess_message(user_message)
        user_doc = self.nlp(user_message)
        
        best_match = None
        best_score = 0
        
        # 1. Recherche par patterns spaCy
        patterns = processed_message["spacy_analysis"]["patterns"]
        for pattern in patterns:
            pattern_name = pattern["pattern"].lower()
            if pattern_name == "creation" and "creation_entreprise" in self.knowledge_base.get("categories", {}):
                return {
                    "type": "category",
                    "data": self.knowledge_base["categories"]["creation_entreprise"],
                    "category_id": "creation_entreprise",
                    "confidence": 0.9
                }
            elif pattern_name == "modification" and "modification_statuts" in self.knowledge_base.get("categories", {}):
                return {
                    "type": "category",
                    "data": self.knowledge_base["categories"]["modification_statuts"],
                    "category_id": "modification_statuts",
                    "confidence": 0.9
                }
            elif pattern_name == "dissolution" and "dissolution" in self.knowledge_base.get("categories", {}):
                return {
                    "type": "category",
                    "data": self.knowledge_base["categories"]["dissolution"],
                    "category_id": "dissolution",
                    "confidence": 0.9
                }
        
        # 2. Recherche par similarité vectorielle dans les catégories
        for category_id, category in self.knowledge_base.get("categories", {}).items():
            # Similarité avec les mots-clés
            for keyword in category.get("keywords", []):
                keyword_doc = self.nlp(keyword)
                if user_doc.has_vector and keyword_doc.has_vector:
                    similarity = user_doc.similarity(keyword_doc)
                    if similarity > best_score and similarity > 0.5:
                        best_score = similarity
                        best_match = {
                            "type": "category",
                            "data": category,
                            "category_id": category_id,
                            "confidence": similarity
                        }
            
            # Similarité avec le nom de la catégorie
            category_name_doc = self.nlp(category.get("name", ""))
            if user_doc.has_vector and category_name_doc.has_vector:
                similarity = user_doc.similarity(category_name_doc)
                if similarity > best_score and similarity > 0.4:
                    best_score = similarity
                    best_match = {
                        "type": "category",
                        "data": category,
                        "category_id": category_id,
                        "confidence": similarity
                    }
        
        # 3. Recherche dans la FAQ avec similarité sémantique
        for faq_id, faq_item in self.knowledge_base.get("faq", {}).items():
            question = faq_item.get("question", "")
            question_doc = self.nlp(question)
            
            if user_doc.has_vector and question_doc.has_vector:
                similarity = user_doc.similarity(question_doc)
                if similarity > best_score and similarity > 0.4:
                    best_score = similarity
                    best_match = {
                        "type": "faq",
                        "data": faq_item,
                        "faq_id": faq_id,
                        "confidence": similarity
                    }
        
        # 4. Recherche par mots-clés (fallback)
        if not best_match or best_score < 0.3:
            user_tokens = processed_message["spacy_analysis"]["lemmas"]
            for category_id, category in self.knowledge_base.get("categories", {}).items():
                for keyword in category.get("keywords", []):
                    keyword_tokens = self.nlp(keyword)
                    for token in keyword_tokens:
                        if token.lemma_.lower() in user_tokens:
                            score = 0.3
                            if score > best_score:
                                best_score = score
                                best_match = {
                                    "type": "category",
                                    "data": category,
                                    "category_id": category_id,
                                    "confidence": score
                                }
        
        return best_match if best_score > 0.2 else None
    
    def get_response(self, user_message: str) -> str:
        """Génère une réponse basée sur le message utilisateur avec analyse spaCy"""
        # Analyse du message
        processed_message = self.preprocess_message(user_message)
        
        # Sauvegarde de l'historique avec analyse
        self.conversation_history.append({
            "user": user_message,
            "analysis": processed_message["spacy_analysis"],
            "timestamp": datetime.now().isoformat()
        })
        
        # Détection d'entités pour personnaliser la réponse
        entities = processed_message["spacy_analysis"]["entities"]
        org_entities = [ent for ent in entities if ent["label"] in ["ORG", "PERSON"]]
        
        # Mots-clés spéciaux
        if any(word in user_message.lower() for word in ["contact", "téléphone", "email", "joindre"]):
            contact = self.knowledge_base.get("contact", {})
            response = f"📞 Vous pouvez nous contacter :\n" \
                      f"Email: {contact.get('email', 'Non disponible')}\n" \
                      f"Téléphone: {contact.get('telephone', 'Non disponible')}\n" \
                      f"Horaires: {contact.get('horaires', 'Non disponible')}"
            
            # Personnalisation si une entité organisation est détectée
            if org_entities:
                response += f"\n\n💼 Nous pourrons vous aider pour {org_entities[0]['text']}."
            
            return response
        
        if any(word in user_message.lower() for word in ["aide", "help", "menu", "que", "comment"]):
            return self.get_help_menu()
        
        # Recherche de correspondance avec spaCy
        match = self.find_best_match(user_message)
        
        if match:
            confidence = match.get("confidence", 0)
            confidence_text = ""
            
            if confidence > 0.8:
                confidence_text = " (réponse très pertinente)"
            elif confidence > 0.6:
                confidence_text = " (réponse pertinente)"
            elif confidence > 0.4:
                confidence_text = " (réponse possible)"
            
            if match["type"] == "category":
                responses = match["data"].get("responses", [])
                if responses:
                    response = f"ℹ️ {match['data']['name']}{confidence_text}:\n\n" + "\n\n".join(responses)
                    
                    # Ajout d'informations contextuelles basées sur les entités
                    if org_entities:
                        response += f"\n\n💡 Ces informations s'appliquent à votre situation concernant {org_entities[0]['text']}."
                    
                    return response
            
            elif match["type"] == "faq":
                response = f"❓ {match['data']['question']}{confidence_text}\n\n✅ {match['data']['answer']}"
                return response
        
        # Réponse intelligente basée sur l'analyse spaCy
        tokens = processed_message["spacy_analysis"]["tokens"]
        legal_terms = ["société", "entreprise", "statuts", "capital", "gérant", "associé", "dissolution"]
        
        if any(term in tokens for term in legal_terms):
            return ("🏢 Votre question semble concerner le droit des sociétés. "
                   "Je peux vous aider avec la création d'entreprise, les modifications de statuts, "
                   "ou la dissolution. Pouvez-vous préciser votre besoin ?")
        
        # Réponse par défaut améliorée
        return ("🤔 Je ne suis pas sûr de comprendre votre question. "
               "Tapez 'aide' pour voir les sujets que je peux traiter, "
               "ou 'contact' pour nos coordonnées.\n\n"
               "💡 Vous pouvez me poser des questions sur : création d'entreprise, "
               "modification de statuts, dissolution, tarifs, délais...")
    
    def get_help_menu(self) -> str:
        """Retourne le menu d'aide"""
        menu = "📋 **Comment puis-je vous aider ?**\n\n"
        
        # Catégories disponibles
        categories = self.knowledge_base.get("categories", {})
        if categories:
            menu += "🏢 **Sujets disponibles :**\n"
            for cat_id, cat_data in categories.items():
                menu += f"• {cat_data.get('name', cat_id)}\n"
        
        menu += "\n💬 **Commandes utiles :**\n"
        menu += "• 'contact' - Nos coordonnées\n"
        menu += "• 'aide' - Ce menu\n"
        
        return menu
    
    def add_category(self, category_id: str, name: str, keywords: List[str], responses: List[str]):
        """Ajoute une nouvelle catégorie à la base de connaissances"""
        if "categories" not in self.knowledge_base:
            self.knowledge_base["categories"] = {}
        
        self.knowledge_base["categories"][category_id] = {
            "name": name,
            "keywords": keywords,
            "responses": responses
        }
        self.data_manager.save_data()
    
    def add_faq(self, faq_id: str, question: str, answer: str):
        """Ajoute une nouvelle entrée FAQ"""
        if "faq" not in self.knowledge_base:
            self.knowledge_base["faq"] = {}
        
        self.knowledge_base["faq"][faq_id] = {
            "question": question,
            "answer": answer
        }
        self.data_manager.save_data()
    
    def start_chat(self):
        """Lance l'interface de chat en ligne de commande"""
        print("🤖 Chatbot Annonces Légales (avec spaCy)")
        print("=" * 45)
        print("Tapez 'quit' pour quitter, 'aide' pour l'aide")
        print("📊 Analyse sémantique activée avec fr_core_news_md")
        print("=" * 45)
        
        while True:
            try:
                user_input = input("\n👤 Vous: ").strip()
                
                if user_input.lower() in ['quit', 'quitter', 'exit']:
                    print("👋 Au revoir !")
                    break
                
                if not user_input:
                    continue
                
                response = self.get_response(user_input)
                print(f"\n🤖 Bot: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 Au revoir !")
                break
            except Exception as e:
                print(f"❌ Erreur: {e}")
    
    def get_conversation_insights(self) -> Dict:
        """Analyse les conversations pour obtenir des insights"""
        if not self.conversation_history:
            return {"message": "Aucune conversation à analyser"}
        
        insights = {
            "total_conversations": len(self.conversation_history),
            "common_entities": {},
            "common_patterns": {},
            "topics_discussed": []
        }
        
        # Analyse des entités les plus mentionnées
        all_entities = []
        all_patterns = []
        
        for conv in self.conversation_history:
            if "analysis" in conv:
                entities = conv["analysis"].get("entities", [])
                patterns = conv["analysis"].get("patterns", [])
                
                for ent in entities:
                    all_entities.append(ent["text"])
                
                for pattern in patterns:
                    all_patterns.append(pattern["pattern"])
        
        # Comptage des entités
        from collections import Counter
        entity_counts = Counter(all_entities)
        pattern_counts = Counter(all_patterns)
        
        insights["common_entities"] = dict(entity_counts.most_common(5))
        insights["common_patterns"] = dict(pattern_counts.most_common(5))
        
        return insights

# Exemple d'utilisation et classe utilitaire pour l'administration
class ChatbotAdmin:
    def __init__(self, chatbot: LegalAnnouncementChatbot):
        self.chatbot = chatbot
    
    def interactive_add_category(self):
        """Interface interactive pour ajouter une catégorie"""
        print("\n➕ Ajouter une nouvelle catégorie")
        category_id = input("ID de la catégorie: ").strip()
        name = input("Nom de la catégorie: ").strip()
        
        print("Mots-clés (séparés par des virgules):")
        keywords_input = input().strip()
        keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
        
        print("Réponses (tapez 'FIN' sur une ligne vide pour terminer):")
        responses = []
        while True:
            response = input()
            if response.strip().upper() == 'FIN':
                break
            if response.strip():
                responses.append(response.strip())
        
        self.chatbot.add_category(category_id, name, keywords, responses)
        print("✅ Catégorie ajoutée avec succès!")
    
    def interactive_add_faq(self):
        """Interface interactive pour ajouter une FAQ"""
        print("\n➕ Ajouter une nouvelle FAQ")
        faq_id = input("ID de la FAQ: ").strip()
        question = input("Question: ").strip()
        answer = input("Réponse: ").strip()
        
        self.chatbot.add_faq(faq_id, question, answer)
        print("✅ FAQ ajoutée avec succès!")

# Point d'entrée principal
if __name__ == "__main__":
    # Vérification des dépendances
    try:
        import spacy
        spacy.load("fr_core_news_md")
    except ImportError:
        print("❌ spaCy n'est pas installé. Installez-le avec:")
        print("pip install spacy")
        print("python -m spacy download fr_core_news_md")
        exit(1)
    except OSError:
        print("❌ Le modèle fr_core_news_md n'est pas installé. Installez-le avec:")
        print("python -m spacy download fr_core_news_md")
        exit(1)
    
    # Initialisation du chatbot
    data_manager = DataManager()
    bot = LegalAnnouncementChatbot(data_manager)
    
    # Menu principal
    while True:
        print("\n" + "="*50)
        print("🤖 CHATBOT ANNONCES LÉGALES (spaCy)")
        print("="*50)
        print("1. Démarrer le chat")
        print("2. Ajouter une catégorie")
        print("3. Ajouter une FAQ")
        print("4. Voir les insights de conversation")
        print("5. Quitter")
        
        choice = input("\nChoisissez une option (1-5): ").strip()
        
        if choice == "1":
            bot.start_chat()
        elif choice == "2":
            admin = ChatbotAdmin(bot)
            admin.interactive_add_category()
        elif choice == "3":
            admin = ChatbotAdmin(bot)
            admin.interactive_add_faq()
        elif choice == "4":
            insights = bot.get_conversation_insights()
            print("\n📊 INSIGHTS DES CONVERSATIONS:")
            print(f"Total conversations: {insights.get('total_conversations', 0)}")
            if insights.get('common_entities'):
                print("Entités les plus mentionnées:", insights['common_entities'])
            if insights.get('common_patterns'):
                print("Patterns les plus détectés:", insights['common_patterns'])
        elif choice == "5":
            print("👋 Au revoir !")
            break
        else:
            print("❌ Option invalide. Veuillez choisir entre 1 et 5.")