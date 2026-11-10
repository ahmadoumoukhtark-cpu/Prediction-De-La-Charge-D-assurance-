import requests

# URL de base de l'API
url_base = "http://127.0.0.1:5000"

# Test de la route d'accueil
reponse_accueil = requests.get(url_base + "/")
print("Réponse de la route d'accueil :", reponse_accueil.text)
print("-" * 60)

# Données d'exemple (données brutes, comme un vrai utilisateur les enverrait)
donnees_exemple = {
    "age": 30,
    "imc": 25.0,
    "sexe": "homme",
    "fumeur": "non",
    "region": "sud-ouest"
}

# Test de la route de prédiction
reponse_prediction = requests.post(url_base + "/predict", json=donnees_exemple)
print("Code HTTP :", reponse_prediction.status_code)
print("Réponse de la route de prédiction :", reponse_prediction.text)
print("-" * 60)

# Bonus : tester plusieurs profils
profils = [
    {"age": 45, "imc": 32.5, "sexe": "femme", "fumeur": "oui", "region": "nord-est"},
    {"age": 22, "imc": 21.0, "sexe": "homme", "fumeur": "non", "region": "sud-est"},
    {"age": 60, "imc": 28.0, "sexe": "femme", "fumeur": "non", "region": "nord-ouest"},
]

for profil in profils:
    reponse = requests.post(url_base + "/predict", json=profil)
    print(profil, "->", reponse.json())