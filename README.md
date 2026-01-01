# Exemple de Pipeline LCEL

## Où les pipes LCEL ont été utilisés

Les pipes LCEL (`|`) sont utilisés pour composer les composants:

1. **Décomposeur**: `decompose_prompt | ChatOpenAI(...)` - Compose le prompt avec le modèle
2. **Chaîne de réponses**: `answer_prompt | ChatOpenAI(...)` - Compose prompt et modèle pour répondre
3. **Combinateur**: `format_runnable | combine_prompt | ChatOpenAI(...)` - Pipeline à 3 étapes
4. **Pipeline complet**: `decomposer | parse_subq_runnable | run_answers_runnable | combiner`

## Pourquoi le traitement par lots (batch) est utile

La méthode `batch()` exécute toutes les sous-questions **en parallèle** plutôt que séquentiellement. Pour 3 sous-questions, cela signifie une exécution ~3x plus rapide car les appels API sont effectués simultanément au lieu d'attendre la fin de chaque réponse.

## Exécution

```bash
pip install -r requirements.txt
set OPENAI_API_KEY=votre-clé
python lcel_no_json_example.py
```

## Tests

```bash
python -m unittest test_decomposer.py -v
```
