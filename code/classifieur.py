"""Briques communes : chargement des tickets, consignes, appel au modèle."""
import csv
import json
import re
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FICHIER_TICKETS = RACINE / "data" / "tickets.csv"
DOSSIER_RESULTATS = RACINE / "resultats"

CATEGORIES = ["facturation", "technique", "compte", "commercial"]

# Modèles Groq (palier gratuit). Vérifiez les noms avec essai.py : ils évoluent.
MODELE_GRAND = "openai/gpt-oss-120b"
MODELE_PETIT = "openai/gpt-oss-20b"

PAUSE = 2.1  # 30 requêtes/minute => une requête toutes les 2 s minimum

# --- Consigne v1 : simple -------------------------------------------------
CONSIGNE_V1 = """Tu es un agent de routage du guichet d'une entreprise.
Classe le ticket du client dans UNE seule catégorie parmi :
facturation, technique, compte, commercial.

Réponds uniquement avec un objet JSON de la forme :
{"categorie": "<une des quatre catégories>"}"""

# --- Consigne v2 : avec règles d'annotation et départage ------------------
CONSIGNE_V2 = """Tu es un agent de routage du guichet d'une entreprise.
Classe le ticket du client dans UNE seule catégorie parmi :
facturation, technique, compte, commercial.

Définitions :
- facturation : un montant, une facture, un paiement, un remboursement.
- technique : un service qui ne fonctionne pas comme prévu.
- compte : l'accès au compte ou les données personnelles.
- commercial : le choix d'une offre, un abonnement, une résiliation.

Départage : si plusieurs catégories s'appliquent, retiens l'INTENTION PRINCIPALE
du client, c'est-à-dire ce qu'il veut obtenir, et non ce qu'il décrit en chemin.
Les messages peuvent être sans accents, sans ponctuation ou en style SMS.

Réponds uniquement avec un objet JSON de la forme :
{"categorie": "<une des quatre catégories>"}"""

CONSIGNES = {"v1": CONSIGNE_V1, "v2": CONSIGNE_V2}


def charger_tickets(chemin=FICHIER_TICKETS):
    """Lit tickets.csv (séparateur détecté) et renvoie une liste de dicts."""
    chemin = Path(chemin)
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        echantillon = f.read(4096)
        f.seek(0)
        try:
            dialecte = csv.Sniffer().sniff(echantillon, delimiters=",;\t")
        except csv.Error:
            dialecte = csv.excel
        lecteur = csv.DictReader(f, dialect=dialecte)
        tickets = []
        for ligne in lecteur:
            ligne = {(k or "").strip().lower(): (v or "").strip() for k, v in ligne.items()}
            tickets.append(
                {
                    "id": ligne["id"],
                    "texte": ligne["texte"],
                    "categorie": ligne["categorie"].lower(),
                    "ambigu": int(ligne.get("ambigu") or 0),
                }
            )
    return tickets


def creer_client():
    from groq import Groq  # import tardif : explorer.py marche sans groq

    return Groq()  # lit GROQ_API_KEY dans l'environnement


def extraire_categorie(texte):
    """Extrait la catégorie d'une réponse brute (même parsing pour tous les modèles)."""
    if not texte:
        return None
    try:
        cat = str(json.loads(texte).get("categorie", "")).strip().lower()
        if cat in CATEGORIES:
            return cat
    except (json.JSONDecodeError, AttributeError):
        pass
    m = re.search(r'"categorie"\s*:\s*"([^"]+)"', texte)
    if m and m.group(1).strip().lower() in CATEGORIES:
        return m.group(1).strip().lower()
    trouvees = [c for c in CATEGORIES if re.search(r"\b" + c + r"\b", texte.lower())]
    return trouvees[0] if len(trouvees) == 1 else None


def classifier(client, modele, consigne, texte, essais=4):
    """Renvoie (categorie, brut). categorie vaut 'invalide' si la sortie est inexploitable."""
    from groq import BadRequestError, RateLimitError  # import tardif

    brut = ""
    mode_json = True
    for tentative in range(essais):
        try:
            params = dict(
                model=modele,
                temperature=0,
                messages=[
                    {"role": "system", "content": consigne},
                    {"role": "user", "content": texte},
                ],
            )
            if mode_json:
                params["response_format"] = {"type": "json_object"}
            rep = client.chat.completions.create(**params)
            brut = rep.choices[0].message.content or ""
            return (extraire_categorie(brut) or "invalide"), brut
        except RateLimitError:
            attente = 20 * (tentative + 1)
            print(f"   ! limite de débit — nouvel essai dans {attente}s")
            time.sleep(attente)
        except BadRequestError as e:
            # ex. le modèle n'a pas produit un JSON valide : on réessaie sans le mode JSON strict
            print(f"   ! requête refusée : {str(e)[:200]}")
            print("     -> nouvel essai sans response_format")
            mode_json = False
        except Exception as e:  # réseau, etc.
            print(f"   ! erreur ({type(e).__name__}) — nouvel essai dans 3s")
            time.sleep(3)
    return "invalide", brut