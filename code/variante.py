"""Étape 6 : on fige le MODÈLE et on change la CONSIGNE (v1 -> v2).

    python code/variante.py --modele llama-3.3-70b-versatile
Réutilise le résultat v1 s'il existe déjà.
"""
import argparse

from classifieur import MODELE_GRAND
from comparer import comparer_fichiers
from evaluer import executer, nom_fichier

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modele", default=MODELE_GRAND)
    a = ap.parse_args()

    f1 = nom_fichier(a.modele, "v1")
    if not f1.exists():
        executer(a.modele, "v1")
    f2 = executer(a.modele, "v2")
    comparer_fichiers(f1, f2)
