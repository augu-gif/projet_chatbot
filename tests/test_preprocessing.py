import unittest
from src.core.intent_matcher import IntentMatcher

class TestPreprocessing(unittest.TestCase):
    def setUp(self):
        """Initialisation avant chaque test"""
        self.intent_matcher = IntentMatcher()
    
    def test_preprocessing(self):
        """Test du prétraitement des questions"""
        test_cases = [
            {
                "input": "Est-ce que je peux créer une entreprise ?",
                "expected": "pouvoir créer entreprise"
            },
            {
                "input": "Je voudrais savoir comment faire pour publier une annonce légale",
                "expected": "savoir publier annonce légal"
            },
            {
                "input": "J'aimerais savoir les démarches pour créer une société",
                "expected": "savoir démarche créer société"
            },
            {
                "input": "Pourriez-vous me dire le prix d'une annonce légale ?",
                "expected": "dire prix annonce légal"
            },
            {
                "input": "Est-il possible de changer l'adresse de mon entreprise ?",
                "expected": "possible changer adresse entreprise"
            },
            {
                "input": "J'ai besoin de faire une déclaration de cessation d'activité",
                "expected": "faire déclaration cessation activité"
            },
            {
                "input": "Comment faire pour modifier les statuts de ma société ?",
                "expected": "modifier statut société"
            },
            {
                "input": "Je souhaite connaître les formalités pour une dissolution",
                "expected": "connaître formalité dissolution"
            }
        ]
        
        for test_case in test_cases:
            processed = self.intent_matcher._preprocess_text(test_case["input"])
            self.assertEqual(
                processed,
                test_case["expected"],
                f"Le prétraitement de '{test_case['input']}' a donné '{processed}' au lieu de '{test_case['expected']}'"
            )

if __name__ == '__main__':
    unittest.main() 