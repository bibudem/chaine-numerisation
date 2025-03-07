# Script de test pour l'environnement d'exécution

import sys
import time

def main():
    print("Ceci est un message en stdout.", flush=True)
    time.sleep(1)
    print("Ceci est un message d'erreur en stderr.", file=sys.stderr, flush=True)
    time.sleep(1)
    print("Fin du script.", flush=True)

if __name__ == "__main__":
    main()
