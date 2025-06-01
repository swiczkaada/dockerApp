# Projet Django DockerApp

Ce projet est une application Django prête à être déployée et développée localement.  
Ce guide explique comment installer, configurer et lancer le projet.

---

## Prérequis

- Docker  
- Docker Compose
- Git
- (Optionnel) Ngrok

---

## Installation

### 1. **Cloner le dépôt**

```bash
git clone https://github.com/swiczkaada/dockerApp.git
cd dockerApp
```

### 2. **Démarrer les services Docker**

```bash
docker compose up --build -d
```

### 3. **Exécuter les migrations**

```bash
docker compose exec web python manage.py migrate
```

### 4. **Créer un compte administrateur**

C’est obligatoire pour se connecter à l’interface d’administration Django.

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. **Installer Tailwind CSS**

L’interface utilise Tailwind pour le design. Vous devez l’installer et le démarrer :

```bash
docker compose exec web python manage.py tailwind install
docker compose exec web python manage.py tailwind start
```
Laissez la commande **tailwind start tourner en parallèle (dans un second terminal par exemple)**, elle compile automatiquement le CSS.

## Configuration

### Fichier `.env`

Le projet utilise un fichier `.env` pour stocker les variables d'environnement sensibles (clés secrètes, paramètres spécifiques à l'environnement).

Un fichier `.env_example` est fourni pour vous guider dans la création de votre propre fichier `.env`.

### 6. **Renommer le fichier `.env_example` en `.env`**

```bash
cd src/
mv .env_example .env
```
### 7. **Génération des clés**

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

### 8. **Utilisation réseau local ou via ngrok (important pour les QR codes)**

Par défaut, les QR codes générés utiliseront localhost, ce qui ne fonctionnera pas sur un autre appareil que votre PC.

Vous avez deux options :

- **Option 1 – Utiliser votre adresse IP locale (sur le même réseau Wi-Fi)**

a. Trouver Trouvez votre IP locale :

Méthode 1 – Via le terminal :

```bash
# Sur Windows
ipconfig

# Sur Mac / Linux
ifconfig
```

Méthode 2 – Via les paramètres Wi-Fi :

- Allez dans les paramètres de votre Wi-Fi (ordinateur ou téléphone)

- Cliquez sur le réseau Wi-Fi connecté

- Recherchez la ligne "Adresse IP" ou "IPv4"
Recherchez une adresse du type : 192.168.x.x ou 10.0.x.x

b. Dans le fichier `.env`, décommentez, modifiez ou ajoutez ces lignes :

```bash
DOMAIN_IP=192.168.1.42 # Remplacez par votre IP
PROTOCOL=http
PORT=8000
```
Vous pourrez maintenant scanner les QR codes depuis votre téléphone sur le même réseau Wi-Fi.

- **Option 2 – Utiliser Ngrok (accessible depuis Internet)**

a. Installez ngrok : https://ngrok.com/download

b. Lancez ngrok :
```bash
ngrok http 8000
```
Ngrok vous affichera une URL du type :

```cpp
https://3d07-xxxx.ngrok-free.app
```

c. Décommentez et modifiez le fichier .env :
```
DOMAIN_NGROK=3d07-xxxx.ngrok-free.app
PROTOCOL_PROD=https
```

### 9. **Relancer Docker pour appliquer la configuration**
```bash
cd ..
docker compose down
docker compose up -d
```

### 10. **📦 Installer la base de données GeoLite2**
Le fichier `GeoLite2-City.mmdb` est nécessaire pour les fonctionnalités de géolocalisation, mais il est trop volumineux pour être versionné dans le dépôt Git.

Un fichier compressé `GeoLite2-City_20250528.tar.gz` est fourni séparément. Voici comment l’installer :
```bash
mkdir -p src/dockerApp/geoip && \
tar -xvzf GeoLite2-City_20250528.tar.gz && \
mv GeoLite2-City_20250528/GeoLite2-City.mmdb src/dockerApp/geoip/
```

## Lancer le projet 

Ouvrez votre navigateur et allez sur :

Application principale : http://localhost:8000

Interface admin Django : http://localhost:8000/admin

## Commandes Django utiles
**Pour installer Tailwind CSS et lancer sa compilation**

```bash

python manage.py tailwind install
python manage.py tailwind start
```
**Créer les fichiers de migration**

```bash
docker compose exec web python manage.py makemigrations
```

**Appliquer les migrations**

```bash
docker compose exec web python manage.py migrate
```

**Créer un super utilisateur**

```bash
docker compose exec web python manage.py createsuperuser
```


## 📂 Arborescence du projet (simplifiée)
```csharp
dockerApp/
├── data/                   ← Contient la base SQLite (via Docker)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── src/                    ← Projet Django et apps
│   ├── manage.py
│   ├── dockerApp/
│   ├── accounts/
└──── ...
```



