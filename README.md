# Chatbot Annonces Légales

## Lancer l'application

<p align="center">
  <a href="https://augu-gif-projet-chatbot-app-oj9sw8.streamlit.app/">
    <img src="https://streamlit.io/images/brand/streamlit-logo-primary-colormark-darktext.png" alt="Streamlit App" width="200"/>
  </a>
</p>
 

Un chatbot intelligent conçu pour répondre aux questions les plus fréquentes sur les annonces légales : types d'annonces, obligations de publication, délais, informations à fournir, etc. Développé dans le cadre d’un stage, ce projet s’appuie sur un moteur de traitement du langage naturel (NLP) pour comprendre les demandes des utilisateurs et fournir des réponses claires, contextualisées et faciles d’accès.

## Ce que le chatbot peut comprendre

Le chatbot repose sur une base de connaissances structurée (legal_data.json) lui permettant de répondre automatiquement aux questions les plus courantes sur les annonces légales.

Il comprend des formulations variées autour des thématiques suivantes :

### Création d’entreprise

Exemples de questions :

Comment créer une entreprise ?

Quelles sont les étapes pour créer une société ?

Je veux monter ma boîte, que dois-je faire ?

### Modification des statuts

Exemples de questions :

Comment modifier les statuts de ma société ?

Je veux changer le gérant ou l’adresse de l’entreprise.

Quelles sont les démarches pour changer les statuts ?

### Dissolution d’une entreprise

Exemples de questions :

Comment fermer ma société ?

Quelles sont les démarches de dissolution ?

Faut-il publier un avis pour liquider ?

### Tarifs des annonces légales

Exemples de questions :

Combien coûte une annonce légale ?

C’est quoi le tarif pour publier ?

Je veux un devis, comment faire ?

### Délais de publication

Exemples de questions :

En combien de temps une annonce est-elle publiée ?

C’est urgent, pouvez-vous publier demain ?

Quels sont vos délais de traitement ?

### Zones de publication

Exemples de questions :

Dans quels départements publiez-vous ?

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
