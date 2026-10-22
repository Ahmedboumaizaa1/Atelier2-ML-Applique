"""Compare deux fichiers de résultats avec la règle de la séance (>= 5 tickets d'écart).

    python code/comparer.py resultats/A.json resultats/B.json
"""
import json
import sys

from evaluation import afficher_rapport

SEUIL_TICKETS = 5


def charger(chemin):
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def comparer_fichiers(chemin_a, chemin_b):
    a, b = charger(chemin_a), charger(chemin_b)
    nom_a, nom_b = f"{a['modele']} / {a['consigne']}", f"{b['modele']} / {b['consigne']}"
    ma, mb = a["metriques"], b["metriques"]

    afficher_rapport(ma, f"A = {nom_a}")
    afficher_rapport(mb, f"B = {nom_b}")

    print("\n" + "=" * 60)
    print(f"{'':<14}{'A':>12}{'B':>12}")
    print(f"{'macro-F1':<14}{ma['macro_f1']:>12.3f}{mb['macro_f1']:>12.3f}")
    print(f"{'accuracy':<14}{ma['accuracy']:>12.3f}{mb['accuracy']:>12.3f}")
    print(f"{'corrects':<14}{ma['correct']:>12}{mb['correct']:>12}")
    print(f"{'invalides':<14}{ma['invalides']:>12}{mb['invalides']:>12}")
    print(f"{'durée (s)':<14}{a['duree_s']:>12}{b['duree_s']:>12}")

    ecart = ma["correct"] - mb["correct"]
    print(f"\nÉcart en tickets : {ecart:+d} (seuil de décision : {SEUIL_TICKETS})")
    if abs(ecart) >= SEUIL_TICKETS:
        gagnant = nom_a if ecart > 0 else nom_b
        print(f"VERDICT : {gagnant} est meilleur (écart >= {SEUIL_TICKETS} tickets).")
    else:
        print("VERDICT : pas de différence mesurable.")

    # Tickets où les deux se contredisent
    pb = {p["id"]: p for p in b["predictions"]}
    desaccords = [(p, pb[p["id"]]) for p in a["predictions"]
                  if p["id"] in pb and p["prediction"] != pb[p["id"]]["prediction"]]
    print(f"\nTickets où A et B diffèrent : {len(desaccords)}")
    for pa, pbb in desaccords:
        ok_a = "OK " if pa["prediction"] == pa["reference"] else "ERR"
        ok_b = "OK " if pbb["prediction"] == pbb["reference"] else "ERR"
        print(f"  {pa['id']} ref={pa['reference']:<11} A={pa['prediction']:<12}{ok_a} "
              f"B={pbb['prediction']:<12}{ok_b} | {pa['texte'][:70]}")

    # Catégorie la plus fragile pour chaque candidat
    for nom, m in ((nom_a, ma), (nom_b, mb)):
        pire = min(m["par_classe"].items(), key=lambda kv: kv[1]["f1"])
        print(f"\nCatégorie la plus fragile pour {nom} : {pire[0]} (F1 = {pire[1]['f1']:.3f})")

    # Erreurs sur tickets ambigus
    for nom, d in ((nom_a, a), (nom_b, b)):
        err = [p for p in d["predictions"] if p["prediction"] != p["reference"]]
        amb = sum(p["ambigu"] for p in err)
        print(f"{nom} : {len(err)} erreurs dont {amb} sur tickets ambigus")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    comparer_fichiers(sys.argv[1], sys.argv[2])
