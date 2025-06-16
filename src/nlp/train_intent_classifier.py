import logging
from pathlib import Path
from intent_classifier import IntentClassifier

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    # Chemins des fichiers
    data_file = Path("legal_data.json")
    model_dir = Path("models/intent_classifier")
    
    # Création du classificateur
    classifier = IntentClassifier()
    
    # Préparation des données d'entraînement
    logger.info("📚 Préparation des données d'entraînement...")
    training_data = classifier.prepare_training_data(str(data_file))
    logger.info(f"✅ {len(training_data)} exemples préparés")
    
    # Entraînement du modèle
    logger.info("🎯 Début de l'entraînement...")
    classifier.train(training_data, str(model_dir), n_iter=30)
    
    # Test du modèle
    test_phrases = [
        "je veux faire une annonce légale",
        "je ferme mon entreprise",
        "changement d'adresse",
        "bonjour j'aimerais publier une annonce de création",
        "combien coûte une annonce légale"
    ]
    
    logger.info("\n🧪 Test du modèle avec quelques phrases :")
    for phrase in test_phrases:
        intent, score = classifier.predict(phrase)
        logger.info(f"Phrase: '{phrase}'")
        logger.info(f"Intention détectée: {intent} (score: {score:.2f})")
        logger.info("---")

if __name__ == "__main__":
    main() 