# Pipeline LCEL - Décomposition et Synthèse de Questions

## Où les pipes LCEL ont été utilisés

Les pipes LCEL (`|`) composent les Runnables LangChain :

1. **Décomposeur** : `decompose_prompt | ChatOllama(...)` - Prompt + modèle
2. **Répondeur** : `answer_prompt | ChatOllama(...)` - Répond aux sous-questions
3. **Combinateur** : `format_runnable | combine_prompt | ChatOllama(...)` - 3 étapes
4. **Pipeline** : `decomposer | parse_subq_runnable | run_answers_runnable | combiner`

## Pourquoi batch() est utile

Le traitement par lots exécute les appels **en parallèle**. Pour 3 sous-questions : ~3x plus rapide (appels simultanés vs séquentiels).

## Résultats

### Question 1 : Latence ML
- **Sous-questions** : Optimisation Web, Qualité données, Outils ML
- **Synthèse** : Optimisation + données + bibliothèques appropriées

### Question 2 : Sécurité API
- **Sous-questions** : Authentification, Validation, Cryptage
- **Synthèse** : Auth robuste + validation entrées + chiffrement

## Exécution

```bash
pip install -r requirements.txt
python lcel_no_json_example.py
```

## Tests

```bash
python -m unittest test_decomposer.py -v
```

6 tests OK ✅
