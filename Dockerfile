# Utiliser une image Python 3.10 officielle
FROM python:3.10-slim

# Variables d'environnement pour éviter la création de fichiers pyc et définir le buffer stdout
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Créer et définir le dossier de travail dans le container
WORKDIR /app

# Copier les fichiers requirements.txt dans le container
COPY requirements.txt /app/

# Installer les dépendances
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copier le reste du projet dans le container
COPY . /app/

# Exposer le port 8000 (port par défaut de Django)
EXPOSE 8000

# Commande pour lancer le serveur Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
