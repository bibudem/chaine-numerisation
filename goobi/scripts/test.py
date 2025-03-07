# Script de test pour l'environnement d'exécution
# Il ne fait que sortir en stdout les paramètres qu'il reçoit

import sys

def main():

    # Vérifier s'il y a des arguments
    if len(sys.argv) < 2:
        print("Aucun paramètre fourni.")
        return
    
    # Afficher chaque paramètre sur une ligne
    for arg in sys.argv[1:]:  # Ignorer le premier élément (nom du script)
        print(arg)

if __name__ == "__main__":
    main()
