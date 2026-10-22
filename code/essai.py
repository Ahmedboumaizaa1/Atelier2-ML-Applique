"""Étape 0 : vérifier que la clé API marche et lister les modèles disponibles."""
from classifieur import MODELE_GRAND, creer_client

client = creer_client()

print("Modèles disponibles sur votre compte :")
for m in sorted(client.models.list().data, key=lambda x: x.id):
    print("  -", m.id)

rep = client.chat.completions.create(
    model=MODELE_GRAND,
    temperature=0,
    messages=[{"role": "user", "content": "Dis bonjour en une phrase."}],
)
print("\nRéponse de", MODELE_GRAND, ":", rep.choices[0].message.content)
