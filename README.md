# Chatbot Annonces Légales

## 🚀 Lancer l'application

<p align="center">
  <a href="https://augu-gif-projet-chatbot-app-oj9sw8.streamlit.app/">
    <img src="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png" alt="Streamlit App" width="200"/>
  </a>
</p>
 

Un chatbot intelligent conçu pour répondre aux questions les plus fréquentes sur les annonces légales : types d'annonces, obligations de publication, délais, informations à fournir, etc. Développé dans le cadre d’un stage, ce projet s’appuie sur un moteur de traitement du langage naturel (NLP) pour comprendre les demandes des utilisateurs et fournir des réponses claires, contextualisées et faciles d’accès.

## Fonctionnalités

- Interface graphique conviviale avec Tkinter
- Traitement du langage naturel avec spaCy
- Base de connaissances extensible en JSON
- Reconnaissance des intentions et des entités
- Historique des conversations

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/augu-gif/projet-chatbot.git

cd projet-chatbot

```

2. Créez un environnement virtuel et activez-le :
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

## Utilisation

Pour lancer le chatbot :
```bash
python src/main.py
```

## Structure du Projet

```
.
├── src/
│   ├── core/
│   │   └── chatbot.py          # Logique principale du chatbot
│   ├── data/
│   │   └── data_manager.py     # Gestion des données
│   ├── ui/
│   │   └── chatbot_gui.py      # Interface graphique
│   └── main.py                 # Point d'entrée
├── tests/                      # Tests unitaires
├── legal_data.json            # Base de connaissances
├── requirements.txt           # Dépendances
└── README.md                 # Documentation
```

## Personnalisation

### Ajouter de nouvelles réponses

Modifiez le fichier `legal_data.json` pour ajouter de nouvelles catégories ou FAQ :

```json
{
    "categories": {
        "nouvelle_categorie": {
            "name": "Nom de la catégorie",
            "keywords": ["mot", "clé", "liste"],
            "responses": [
                "Réponse 1",
                "Réponse 2"
            ]
        }
    }
}
```
[Retour au portfolio](https://github.com/augu-gif/mon-portfolio-data-analyst/blob/main/README.md)
