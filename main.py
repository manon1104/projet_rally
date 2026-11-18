"""
Installer pygame (une seule fois) :      pip install pygame
Lancer le jeu :                          python main.py

Touches :
    Espace                    démarrer la course
    Flèches (ou Z Q S D)      accélérer, freiner, tourner
    R                         recommencer
    Échap                     quitter

Les fichiers (dans l'ordre où les lire) :
    reglages.py      toutes les valeurs modifiables : nombre de tours, vitesse,
                     largeur de piste, échelle, couleurs…
    mes_circuits.py  les circuits, écrits comme des listes de points. Ajoutez les vôtres.
    voiture.py       classe Voiture : comment la voiture avance (aucun affichage).
    circuit.py       classe Circuit : la piste, et « la voiture est-elle sur la piste ? ».
    jeu.py           classe Jeu : la fenêtre, la boucle de jeu, le clavier, le dessin.
    main.py          ce fichier : il lance le jeu.
"""

from jeu import Jeu

if __name__ == "__main__":
    jeu = Jeu()
    jeu.lancer()

