freeze les libraries pour les garder en memoire 
```bash
pip freeze > requirements.txt
```

supprimer django 
```bash
pip uninstall django
```

Installer les libraries de requirement :
```bash
pip install -r requirements.txt 
```

Creer structure app django
```bash
django-admin startproject dockerApp
```
```bash
django-admin help {commande}
```

lancer un serveur local
django-admin mais ici
```bash
python manage.py runserver
```

Pour lancer la base de donnée
```bash
ppython manage.py migrate 
```

Pour creer une app :
```bash
python manage.py startapp blog
```

Telecharger Pillow pour les images :
```bash
pip install Pillow
```


Créer fichiers de migrations : (historique des changements de la bdd)
```bash
python manage.py makemigrations
```

Migrer ses fichiers 
```bash
python manage.py migrate
```

Creer un super utilisateur

```bash
 python manage.py createsuperuser
```

Installer la bibliotheque pour qrcode
```bash
pip install qrcode[pil]
```


Installer la bilbiotheque pour crypter les adresses ip :
```bash
pip install cryptography
```

Installer Django REST Framework (DRF) (pour exporter les donnes)
```bash
pip install djangorestframework
```

https://www.youtube.com/watch?v=odIR-00ggVI
$ python manage.py runserver 192.168.1.149:8000
