# Script qui copie les fichiers du Qidenus pour les mettre dans
# un dossier sur N:
#
# Les paramètres nécessaires:
#   1: Le dossier qui contient les images à copier

import sys
import os
import shutil
import configparser

# Cette fonction copie les fichiers et, s'il n'y a aucune erreur, les supprime
# du dossier d'origine. S'il y a erreur, elle supprime les fichiers déjà copiés.
def copier_et_supprimer(src, dest):

    fichiers_copies = []  # Liste des fichiers copiés pour un éventuel rollback
    try:
        for fichier in os.listdir(src):
            src_fichier = os.path.join(src, fichier)
            dest_fichier = os.path.join(dest, fichier)
            # Ignorer les sous-dossiers et prendre les TIFF
            if (os.path.isfile(src_fichier) and src_fichier.lower().endswith((".tif", ".tiff"))):
                print(src_fichier + "...")
                shutil.copy2(src_fichier, dest_fichier)  # Copie avec métadonnées
                fichiers_copies.append(dest_fichier)

        # Si tout s'est bien passé, supprimer les fichiers source
        for fichier in os.listdir(src):
            src_fichier = os.path.join(src, fichier)
            if os.path.isfile(src_fichier):
                os.remove(src_fichier)

    except Exception as e:
        # En cas d'erreur, supprimer les fichiers copiés
        print(f"Erreur lors de la copie : {e}. Suppression des fichiers copiés...")
        for fichier in fichiers_copies:
            if os.path.exists(fichier):
                os.remove(fichier)
        sys.exit(1)

def main():

    # Vérifier si on a le bon nombre d'arguments (3)
    if len(sys.argv) != 2:
        print("Un paramètre est nécessaire pour ce script")
        sys.exit(1)

    # On récupère les paramètres
    src_path = sys.argv[1]

    # Le chemin de base des images du numériseur
    if not(os.path.isdir(src_path) and os.access(src_path, os.R_OK)):
        print("Impossible de lire le dossier " + src_path)
        sys.exit(1)

    # On lit le fichier de config
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    config = configparser.ConfigParser()
    config.read(os.path.join(script_dir, "_config.ini"))

    # On vérifie le chemin de destination, en le créant
    dest_path = os.path.join(config["dossiers"]["destination"], os.path.basename(os.path.dirname(src_path)))
    if not(os.path.isdir(dest_path)):
        os.makedirs(dest_path)
    if not(os.path.isdir(dest_path) and os.access(dest_path, os.W_OK)):
        print("Impossible d'écrire dans le dossier " + dest_path)
        sys.exit(1)

    # On lance la copie ou le déplacement
    copier_et_supprimer(src_path, dest_path)   # Copie et suppression

    # On supprime le dossier de numérisation (y compris les images originales)
    shutil.rmtree(os.path.dirname(src_path))

    print("Fichiers de numérisation copiés avec succès:")
    print(src_path)
    print("-->")
    print(dest_path)

if __name__ == "__main__":
    main()
