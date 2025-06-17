import spacy
from spacy.tokens import Doc
from spacy.training import Example
from spacy.cli.train import train
from pathlib import Path
import json
import logging
from typing import Dict, List, Optional, Tuple
import random

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class IntentClassifier:
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialise le classificateur d'intentions
        
        Args:
            model_path: Chemin vers un modèle spaCy pré-entraîné (optionnel)
        """
        if model_path and Path(model_path).exists():
            self.nlp = spacy.load(model_path)
            logger.info(f"✅ Modèle chargé depuis {model_path}")
        else:
            # Chargement du modèle de base français
            self.nlp = spacy.load("fr_core_news_md")
            # Ajout du pipe de classification si non présent
            if "textcat" not in self.nlp.pipe_names:
                self.nlp.add_pipe("textcat")
            logger.info("✅ Modèle de base français chargé")
        
        # Configuration du classificateur
        self.textcat = self.nlp.get_pipe("textcat")
        self.categories = set()
    
    def prepare_training_data(self, data_file: str) -> List[Example]:
        """
        Prépare les données d'entraînement à partir du fichier JSON
        
        Args:
            data_file: Chemin vers le fichier JSON contenant les données
            
        Returns:
            Liste d'exemples spaCy pour l'entraînement
        """
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        examples = []
        
        # Traitement des catégories principales
        for category_id, category in data.get("categories", {}).items():
            self.categories.add(category_id)
            
            # Ajout des exemples de questions
            for question in category.get("examples", {}).get("questions", []):
                doc = self.nlp(question)
                cats = {cat: 1.0 if cat == category_id else 0.0 for cat in self.categories}
                example = Example.from_dict(doc, {"cats": cats})
                examples.append(example)
            
            # Ajout des variations
            for variation in category.get("examples", {}).get("variations", []):
                doc = self.nlp(variation)
                cats = {cat: 1.0 if cat == category_id else 0.0 for cat in self.categories}
                example = Example.from_dict(doc, {"cats": cats})
                examples.append(example)
        
        # Traitement des FAQ
        for faq_id, faq in data.get("faq", {}).items():
            category_id = f"faq_{faq_id}"
            self.categories.add(category_id)
            
            # Ajout des exemples de questions
            for question in faq.get("examples", {}).get("questions", []):
                doc = self.nlp(question)
                cats = {cat: 1.0 if cat == category_id else 0.0 for cat in self.categories}
                example = Example.from_dict(doc, {"cats": cats})
                examples.append(example)
            
            # Ajout des variations
            for variation in faq.get("examples", {}).get("variations", []):
                doc = self.nlp(variation)
                cats = {cat: 1.0 if cat == category_id else 0.0 for cat in self.categories}
                example = Example.from_dict(doc, {"cats": cats})
                examples.append(example)
        
        # Mélange des exemples
        random.shuffle(examples)
        return examples
    
    def train(self, training_data: List[Example], output_dir: str, n_iter: int = 30):
        """
        Entraîne le classificateur
        
        Args:
            training_data: Liste d'exemples d'entraînement
            output_dir: Répertoire de sortie pour le modèle
            n_iter: Nombre d'itérations d'entraînement
        """
        # Configuration de l'entraînement
        train_config = {
            "pipeline": ["textcat"],
            "lang": "fr",
            "optimize": "efficiency",
            "components": {
                "textcat": {
                    "architecture": "simple_cnn",
                    "exclusive_classes": True
                }
            }
        }
        
        # Création du répertoire de sortie
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Préparation de l'optimiseur
        optimizer = self.nlp.begin_training()
        for i in range(n_iter):
            random.shuffle(training_data)
            losses = {}
            for example in training_data:
                self.nlp.update([example], drop=0.5, losses=losses, sgd=optimizer)
            logger.info(f"Iteration {i+1}/{n_iter}, Losses: {losses}")

        self.save(output_dir)
        logger.info(f"✅ Modèle entraîné et sauvegardé dans {output_dir}")
    
    def predict(self, text: str) -> Tuple[str, float]:
        """
        Prédit l'intention d'un texte
        
        Args:
            text: Le texte à analyser
            
        Returns:
            Tuple contenant l'ID de l'intention et le score de confiance
        """
        doc = self.nlp(text)
        cats = doc.cats
        
        if not cats:
            return "", 0.0
        
        # Trouver la catégorie avec le meilleur score
        best_cat = max(cats.items(), key=lambda x: x[1])
        return best_cat
    
    def save(self, output_dir: str):
        """
        Sauvegarde le modèle
        
        Args:
            output_dir: Répertoire de sortie
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        self.nlp.to_disk(output_path)
        logger.info(f"✅ Modèle sauvegardé dans {output_dir}")
    
    @classmethod
    def load(cls, model_dir: str) -> 'IntentClassifier':
        """
        Charge un modèle sauvegardé
        
        Args:
            model_dir: Répertoire contenant le modèle
            
        Returns:
            Instance du classificateur avec le modèle chargé
        """
        classifier = cls()
        classifier.nlp = spacy.load(model_dir)
        classifier.textcat = classifier.nlp.get_pipe("textcat")
        return classifier 