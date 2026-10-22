# Atelier 2 — Choisir un modèle sur preuves

## Installation
1. Copiez `tickets.csv` dans `data/`.
2. `python -m pip install groq`
3. Clé API (PowerShell) : `$env:GROQ_API_KEY = "gsk_votre_cle"`

## Commandes (depuis le dossier `atelier2/`)
```
python code/essai.py          # test de la clé + liste des modèles (vérifiez les noms !)
python code/explorer.py       # exploration du CSV
python code/evaluer.py --modele llama-3.3-70b-versatile --consigne v1 --limite 5   # test rapide
python code/evaluer.py --modele llama-3.3-70b-versatile --consigne v1
python code/evaluer.py --modele llama-3.1-8b-instant   --consigne v1
python code/comparer.py resultats/llama-3.3-70b-versatile__v1.json resultats/llama-3.1-8b-instant__v1.json
python code/variante.py --modele llama-3.1-8b-instant  # consigne v1 vs v2, modèle figé
```
Si un nom de modèle n'existe plus, changez `MODELE_GRAND` / `MODELE_PETIT` dans `code/classifieur.py`
ou passez `--modele`.

## Budget de requêtes (palier gratuit : 1 000/jour)
Chaque run = 72 requêtes (~2,5 min). Les 4 évaluations (grand v1, petit v1, + 2 en v2) = 288 requêtes.

## Rendu
`code/`, `resultats/*.json`, et `fiche_decision.md` complétée avec les chiffres de `comparer.py`.
