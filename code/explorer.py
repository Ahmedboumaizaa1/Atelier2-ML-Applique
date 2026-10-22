"""Étape 1 : explorer tickets.csv (distribution, ambigus, longueurs, exemples)."""
from collections import Counter

from classifieur import CATEGORIES, charger_tickets

tickets = charger_tickets()
n = len(tickets)
print(f"{n} tickets\n")

print("Distribution :")
cnt = Counter(t["categorie"] for t in tickets)
for c in CATEGORIES:
    print(f"  {c:<12}{cnt[c]:>3}  ({100 * cnt[c] / n:.1f} %)")
inconnues = set(cnt) - set(CATEGORIES)
if inconnues:
    print("  ATTENTION catégories inattendues :", inconnues)

amb = [t for t in tickets if t["ambigu"] == 1]
print(f"\nTickets ambigus : {len(amb)}")

longueurs = [len(t["texte"]) for t in tickets]
print(f"Longueur (caractères) : min {min(longueurs)}, max {max(longueurs)}, "
      f"moyenne {sum(longueurs) / n:.0f}")

# Baseline paresseuse : tout prédire dans la classe majoritaire
maj, k = cnt.most_common(1)[0]
print(f"\nBaseline paresseuse « {maj} » partout : accuracy = {k / n:.3f}, macro-F1 = "
      f"{(2 * (k / n) / (1 + k / n)) / 4:.3f}")

print("\nUn exemple par catégorie :")
for c in CATEGORIES:
    ex = next((t for t in tickets if t["categorie"] == c), None)
    if ex:
        print(f"  [{c}] {ex['texte'][:100]}")
