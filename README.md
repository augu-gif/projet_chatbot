# Chatbot Annonces Légales

Un chatbot intelligent pour répondre aux questions sur les annonces légales, développé dans le cadre d'un stage pour un journal d'annonces légales.

## Fonctionnalités

- Interface graphique conviviale avec Tkinter
- Traitement du langage naturel avec spaCy
- Base de connaissances extensible en JSON
- Reconnaissance des intentions et des entités
- Historique des conversations

## Installation

1. Clonez le dépôt :
```bash
git clone [URL_DU_REPO]
cd [NOM_DU_DOSSIER]
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

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request