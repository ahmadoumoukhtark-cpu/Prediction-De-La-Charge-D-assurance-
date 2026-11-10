# 1. Image de base : un Linux léger avec Python déjà installé
FROM python:3.13-slim

# 2. Dossier de travail à l'intérieur du conteneur
WORKDIR /app

# 3. Copier d'abord la liste des dépendances (optimise le cache Docker)
COPY requirements.txt .

# 4. Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copier le code et le modèle
COPY main.py .
COPY modele_gb.pkl .

# 6. Indiquer le port utilisé par l'API
EXPOSE 5000

# 7. Commande lancée au démarrage du conteneur
CMD ["python", "main.py"]