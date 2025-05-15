# Chaîne de numérisation des bibliothèques de l'UdeM

## Présentation

Cet entrepôt GitHub public contient différents développements pour la chaîne de numérisation des bibliothèques de l'UdeM.

Cette chaîne est piloté en grande partie par le système [Goobi workflow](https://github.com/intranda/goobi-workflow).

Goobi n'est pas inclus dans cet entrepôt, on y trouve uniquement les ajouts ou modifications effectuées.

## Contenus

### Dossier goobi/scripts

Ce dossier contient des scripts qui peuvent être utilisés dans des étapes de workflow.

Il correspond au dossier goobi/scripts d'une installation type de Googi.

### Dossier qidenus

Ce dossier contient des scripts destinés aux opérations spécifiques
du numériseur Qidenus de la BLRCS.

Pour exécuter les scripts Python, voici ce qu'il y a à faire la première fois:

```
python -m venv .env
pip install pillow
```

Ensuite, pour chaque session d'exécution:
```
source .env/bin/activate
cd qidenus
python cropper.py [nom du dossier] #par exemple
```
