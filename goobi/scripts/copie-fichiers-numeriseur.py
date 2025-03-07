# Script qui copie les fichiers d'un numériseur pour les mettre dans
# un dossier Goobi pour un processus
#
# Les paramètres nécessaires:
#   1: le nom (code) du numériseur (qidenus, copibook, quartz, ...)
#   2: le nom du processus ({processtitle} dans Goobi)
#   3: le chemin complet pour déposer les images ({origpath} dans Goobi)
#
# Le dossier source des images est lu depuis le fichier de configuration

import sys
import os
import configparser
import shutil

# Cette fonction déplacer les fichiers d'un dossier vers un autre (sans copie préalable)
def deplacer(src, dest):

    try:
        for fichier in os.listdir(src):
            src_fichier = os.path.join(src, fichier)
            dest_fichier = os.path.join(dest, fichier)

            if os.path.isfile(src_fichier):  # Ignorer les dossiers
                shutil.move(src_fichier, dest_fichier)

    except Exception as e:
        print(f"Erreur lors du déplacement : {e}")
        sys.exit(1)


# Cette fonction copie les fichiers et, s'il n'y a aucune erreur, les supprime
# du dossier d'origine. S'il y a erreur, elle supprime les fichiers déjà copiés.
def copier_et_supprimer(src, dest):

    fichiers_copies = []  # Liste des fichiers copiés pour un éventuel rollback
    try:
        for fichier in os.listdir(src):
            src_fichier = os.path.join(src, fichier)
            dest_fichier = os.path.join(dest, fichier)

            if os.path.isfile(src_fichier):  # Ignorer les sous-dossiers
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
    if len(sys.argv) != 4:
        print("Trois paramètres sont nécessaires pour ce script")
        sys.exit(1)

    # Le dossier du script
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)

    # On récupère les paramètres
    numeriseur = sys.argv[1]
    process = sys.argv[2]
    dest_path = sys.argv[3]

    # On lit le fichier de config
    config = configparser.ConfigParser()
    config.read(os.path.join(script_dir, "_config.ini"))

    # Le chemin de base des images du numériseur
    src_path = os.path.join(config["numeriseur"][numeriseur], process)
    if not(os.path.isdir(src_path) and os.access(src_path, os.R_OK)):
        print("Impossible de lire le dossier " + src_path)
        sys.exit(1)

    # On vérifie le chemin de destination
    if not(os.path.isdir(dest_path) and os.access(dest_path, os.W_OK)):
        print("Impossible d'écrire dans le dossier " + dest_path)
        sys.exit(1)

    # On lance la copie ou le déplacement
#    copier_et_supprimer(src_path, dest_path)   # Copie et suppression
    deplacer(src_path, dest_path)               # Déplacement

    # On supprime le dossier de numérisation
    shutil.rmtree(src_path)

    print("Fichiers de numérisation récupérés avec succès")

if __name__ == "__main__":
    main()
