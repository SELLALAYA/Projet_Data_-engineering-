# ─── ÉTAPE 1 : Choisir l'image de base ───────────────
# On part d'une image Python déjà prête
# python:3.11-slim = Python 3.11 + système Linux minimal
FROM python:3.11-slim

# ─── ÉTAPE 2 : Définir le dossier de travail ────────
# C'est comme faire "cd /app" dans le conteneur
WORKDIR /app

# ─── ÉTAPE 3 : Copier les dépendances ───────────────
# On copie requirements.txt du PC vers le conteneur
COPY requirements.txt .

# ─── ÉTAPE 4 : Installer les dépendances ───────────
# Installer tous les packages Python listés dans requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ─── ÉTAPE 5 : Copier le code ──────────────────────
# Copier tout le code de l'app du PC vers le conteneur
COPY . .

# ─── ÉTAPE 6 : Exposer le port ────────────────────
# Dire à Docker que l'app écoute sur le port 8501
EXPOSE 8501

# ─── ÉTAPE 7 : Commande de démarrage ─────────────
# Quand le conteneur démarre, lancer cette commande
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
