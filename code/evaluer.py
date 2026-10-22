"""Évalue UN modèle avec UNE consigne sur les 72 tickets et écrit un JSON dans resultats/.

Exemples :
    python code/evaluer.py --modele llama-3.3-70b-versatile --consigne v1
    python code/evaluer.py --modele llama-3.1-8b-instant   --consigne v1
"""
import argparse
import json
import re
import time
from datetime import datetime

from classifieur import (CONSIGNES, DOSSIER_RESULTATS, MODELE_GRAND, PAUSE,
                         charger_tickets, classifier, creer_client)
from evaluation import afficher_rapport, calculer_metriques


def nom_fichier(modele, consigne):
    return DOSSIER_RESULTATS / f"{re.sub(r'[^A-Za-z0-9.-]+', '_', modele)}__{consigne}.json"


def executer(modele, consigne_nom, limite=None):
    tickets = charger_tickets()
    if limite:
        tickets = tickets[:limite]
    consigne = CONSIGNES[consigne_nom]
    client = creer_client()
    predictions = []
    debut = time.time()
    for i, t in enumerate(tickets, 1):
        cat, brut = classifier(client, modele, consigne, t["texte"])
        predictions.append({"id": t["id"], "texte": t["texte"], "reference": t["categorie"],
                            "prediction": cat, "ambigu": t["ambigu"], "brut": brut})
        marque = "ok " if cat == t["categorie"] else "ERR"
        print(f"[{i:>2}/{len(tickets)}] {t['id']} {marque} ref={t['categorie']:<11} pred={cat}")
        time.sleep(PAUSE)
    met = calculer_metriques([p["reference"] for p in predictions],
                             [p["prediction"] for p in predictions])
    sortie = {"modele": modele, "consigne": consigne_nom, "temperature": 0,
              "date": datetime.now().isoformat(timespec="seconds"),
              "duree_s": round(time.time() - debut, 1),
              "metriques": met, "predictions": predictions}
    DOSSIER_RESULTATS.mkdir(exist_ok=True)
    chemin = nom_fichier(modele, consigne_nom)
    chemin.write_text(json.dumps(sortie, ensure_ascii=False, indent=2), encoding="utf-8")
    afficher_rapport(met, f"{modele} / consigne {consigne_nom}")
    print(f"\nRésultats écrits dans {chemin}")
    return chemin


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modele", default=MODELE_GRAND)
    ap.add_argument("--consigne", default="v1", choices=list(CONSIGNES))
    ap.add_argument("--limite", type=int, help="ne traiter que N tickets (test rapide)")
    a = ap.parse_args()
    executer(a.modele, a.consigne, a.limite)
