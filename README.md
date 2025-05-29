# Projet Django DockerApp

Ce projet est une application Django prête à être déployée et développée localement.  
Ce guide explique comment installer, configurer et lancer le projet.

---

## Prérequis

- Python 3.10+ (ou version compatible)
- pip
- Git
- (Optionnel) un environnement virtuel Python (`venv` recommandé)

---

## Installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/ton-utilisateur/ton-projet.git
cd ton-projet
```

2. **Créer un environnement virtuel (optionnel mais recommandé)**

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows, utilisez `venv\Scripts\activate`
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

## Configuration

### Fichier `.env`

Le projet utilise un fichier `.env` pour stocker les variables d'environnement sensibles (clés secrètes, paramètres spécifiques à l'environnement).

Un fichier `.env_example` est fourni pour vous guider dans la création de votre propre fichier `.env`.

4. **Renommer le fichier `.env_example` en `.env`**

```bash
cd src/
mv .env_example .env
```
5. **Génération des clés**

- Clé Fernet

```bash
python src/generate_ferney_key.py
```
Copiez la clé générée et remplacez la valeur de DJANGO_FERNET_KEY dans votre `.env`.

- Clé secrète Django

```bash
python src/generate_secret_key.py
```
Copiez la clé et mettez-la dans la variable DJANGO_SECRET_KEY de votre `.env`.

## Lancer le projet 

6. **Lancer le serveur de développement (par défaut localhost:8000) **

```bash
python manage.py runserver
```

7. **Pour accéder à l'application depuis un autre appareil, utilisez l'adresse IP locale de votre machine**

```bash
python manage.py runserver 0.0.0.0:8000 # Remplacer 0.0.0.0 par votre adresse ip 
```

## Commandes Django utiles
**Pour installer Tailwind CSS et lancer sa compilation**

```bash

python manage.py tailwind install
python manage.py tailwind start
```
**Créer les fichiers de migration**

```bash
python manage.py makemigrations
```

**Appliquer les migrations**

```bash
python manage.py migrate
```

**Créer un super utilisateur**

```bash
python manage.py createsuperuser
```



