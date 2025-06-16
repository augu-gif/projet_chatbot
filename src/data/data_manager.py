import json
from typing import Dict, Any, Optional
from pathlib import Path

class DataManager:
    def __init__(self, data_file: str = "legal_data.json"):
        """
        Initialise le gestionnaire de données
        
        Args:
            data_file (str): Chemin vers le fichier JSON contenant les données
        """
        self.data_file = data_file
        self.knowledge_base: Dict[str, Any] = {}
        self.load_data()
    
    def load_data(self) -> None:
        """Charge les données depuis le fichier JSON"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
            print(f"✅ Données chargées depuis {self.data_file}")
        except FileNotFoundError:
            print(f"⚠️  Fichier {self.data_file} non trouvé. Création des données par défaut.")
            self.create_default_data()
        except json.JSONDecodeError:
            print(f"❌ Erreur dans le format JSON de {self.data_file}")
            self.create_default_data()
    
    def save_data(self) -> None:
        """Sauvegarde les données dans le fichier JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
            print(f"✅ Données sauvegardées dans {self.data_file}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde des données: {str(e)}")
    
    def create_default_data(self) -> None:
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
                }
            },
            "contact": {
                "email": "contact@annonces-legales.fr",
                "telephone": "01 23 45 67 89",
                "horaires": "Du lundi au vendredi, 9h-18h"
            }
        }
        
        self.knowledge_base = default_data
        self.save_data()
    
    def add_category(self, category_id: str, name: str, keywords: list, responses: list) -> None:
        """Ajoute une nouvelle catégorie à la base de connaissances"""
        if "categories" not in self.knowledge_base:
            self.knowledge_base["categories"] = {}
        
        self.knowledge_base["categories"][category_id] = {
            "name": name,
            "keywords": keywords,
            "responses": responses
        }
        self.save_data()
    
    def add_faq(self, faq_id: str, question: str, answer: str) -> None:
        """Ajoute une nouvelle FAQ à la base de connaissances"""
        if "faq" not in self.knowledge_base:
            self.knowledge_base["faq"] = {}
        
        self.knowledge_base["faq"][faq_id] = {
            "question": question,
            "answer": answer
        }
        self.save_data()
    
    def get_category(self, category_id: str) -> Optional[Dict]:
        """Récupère une catégorie par son ID"""
        return self.knowledge_base.get("categories", {}).get(category_id)
    
    def get_faq(self, faq_id: str) -> Optional[Dict]:
        """Récupère une FAQ par son ID"""
        return self.knowledge_base.get("faq", {}).get(faq_id) 