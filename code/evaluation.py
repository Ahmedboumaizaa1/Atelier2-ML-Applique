"""Métriques écrites à la main : precision, recall, F1, macro-F1, matrice de confusion."""
from classifieur import CATEGORIES


def matrice_confusion(refs, preds, categories=CATEGORIES):
    """Lignes = vraie catégorie, colonnes = prédiction (+ colonne 'invalide')."""
    colonnes = list(categories) + ["invalide"]
    m = {c: {p: 0 for p in colonnes} for c in categories}
    for r, p in zip(refs, preds):
        m[r][p if p in categories else "invalide"] += 1
    return m


def metriques_par_classe(refs, preds, categories=CATEGORIES):
    res = {}
    for c in categories:
        vp = sum(1 for r, p in zip(refs, preds) if r == c and p == c)
        fp = sum(1 for r, p in zip(refs, preds) if r != c and p == c)
        fn = sum(1 for r, p in zip(refs, preds) if r == c and p != c)
        precision = vp / (vp + fp) if (vp + fp) else 0.0
        recall = vp / (vp + fn) if (vp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        res[c] = {"precision": precision, "recall": recall, "f1": f1,
                  "vp": vp, "fp": fp, "fn": fn, "support": vp + fn}
    return res


def calculer_metriques(refs, preds, categories=CATEGORIES):
    par_classe = metriques_par_classe(refs, preds, categories)
    bons = sum(1 for r, p in zip(refs, preds) if r == p)
    return {
        "n": len(refs),
        "correct": bons,
        "accuracy": bons / len(refs),
        "macro_f1": sum(v["f1"] for v in par_classe.values()) / len(categories),
        "invalides": sum(1 for p in preds if p not in categories),
        "par_classe": par_classe,
        "matrice": matrice_confusion(refs, preds, categories),
    }


def afficher_matrice(m):
    colonnes = list(next(iter(m.values())).keys())
    entete = "vrai \\ prédit"
    print(f"{entete:<14}" + "".join(f"{c[:11]:>12}" for c in colonnes))
    for vrai, ligne in m.items():
        print(f"{vrai:<14}" + "".join(f"{ligne[c]:>12}" for c in colonnes))


def afficher_rapport(met, titre=""):
    if titre:
        print(f"\n=== {titre} ===")
    print(f"Tickets : {met['n']}  | corrects : {met['correct']}  | invalides : {met['invalides']}")
    print(f"Accuracy : {met['accuracy']:.3f}   MACRO-F1 : {met['macro_f1']:.3f}\n")
    print(f"{'catégorie':<14}{'precision':>10}{'recall':>10}{'f1':>8}{'support':>9}")
    for c, v in met["par_classe"].items():
        print(f"{c:<14}{v['precision']:>10.3f}{v['recall']:>10.3f}{v['f1']:>8.3f}{v['support']:>9}")
    print("\nMatrice de confusion :")
    afficher_matrice(met["matrice"])
