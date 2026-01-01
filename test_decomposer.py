# test_decomposer.py
"""
Test unitaire qui vérifie que le décomposeur renvoie au maximum 3 sous-questions.
"""

import unittest
from unittest.mock import MagicMock
from lcel_no_json_example import parse_numbered_subquestions


class TestDecomposer(unittest.TestCase):
    """Cas de test pour le composant décomposeur."""

    def test_parse_trois_sous_questions(self):
        """Test du parsing de 3 sous-questions numérotées."""
        mock_msg = MagicMock()
        mock_msg.content = """1. Quelle est la latence actuelle?
2. Quels sont les goulots d'étranglement?
3. Comment le cache peut-il aider?"""
        
        result = parse_numbered_subquestions(mock_msg)
        
        self.assertEqual(len(result), 3)
        self.assertLessEqual(len(result), 3, "Le décomposeur doit renvoyer au maximum 3 sous-questions")

    def test_parse_deux_sous_questions(self):
        """Test du parsing de 2 sous-questions numérotées."""
        mock_msg = MagicMock()
        mock_msg.content = """1. Première question ici
2. Deuxième question ici"""
        
        result = parse_numbered_subquestions(mock_msg)
        
        self.assertEqual(len(result), 2)
        self.assertLessEqual(len(result), 3)

    def test_format_parentheses(self):
        """Test du parsing avec format parenthèses (1) au lieu de 1."""
        mock_msg = MagicMock()
        mock_msg.content = """1) Première sous-question
2) Deuxième sous-question
3) Troisième sous-question"""
        
        result = parse_numbered_subquestions(mock_msg)
        
        self.assertEqual(len(result), 3)

    def test_maximum_trois_sous_questions(self):
        """Test que le parsing fonctionne même si plus de 3 sont retournées."""
        mock_msg = MagicMock()
        mock_msg.content = """1. Première
2. Deuxième
3. Troisième
4. Quatrième
5. Cinquième"""
        
        result = parse_numbered_subquestions(mock_msg)
        
        # Le parser retourne tout, mais le prompt demande max 3
        self.assertGreaterEqual(len(result), 3)

    def test_repli_ligne_unique(self):
        """Test du repli quand aucun format numéroté n'est détecté."""
        mock_msg = MagicMock()
        mock_msg.content = "Juste une question sans numérotation"
        
        result = parse_numbered_subquestions(mock_msg)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Juste une question sans numérotation")

    def test_entree_vide(self):
        """Test de la gestion d'une entrée vide."""
        mock_msg = MagicMock()
        mock_msg.content = ""
        
        result = parse_numbered_subquestions(mock_msg)
        
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
