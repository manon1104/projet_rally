"""
RÉGLAGES DU JEU
===============

Toutes les valeurs que l'on peut modifier sans toucher au reste du code.
Changez un nombre, relancez le jeu (python main.py) et observez l'effet.

Unités : mètres (m), secondes (s), km/h pour la vitesse maximale,
degrés pour l'angle de braquage.
"""

# ---------------------------------------------------------------------------
# La course
# ---------------------------------------------------------------------------
CIRCUIT_CHOISI = "rectangle"     # nom d'un circuit de mes_circuits.py : "rectangle"
NOMBRE_DE_TOURS = 3              # imposé par le sujet : 3 par défaut, entre 2 et 5
LARGEUR_PISTE = 22              # m (imposé par le sujet) (12)
DT = 0.1                         # pas de temps de la simulation, en secondes (imposé par le sujet)

# ---------------------------------------------------------------------------
# La voiture (voiture de rallye du sujet)
# ---------------------------------------------------------------------------
VITESSE_MAX_KMH = 200            # km/h
ACCELERATION = 20                # m/s² quand on appuie sur « haut » (8)
FREINAGE = 5                   # m/s² quand on appuie sur « bas » (12)
VITESSE_RECUL_MAX = 5            # m/s : on peut reculer, mais lentement
BRAQUAGE_MAX_DEGRES = 50         # angle maximal des roues (imposé par le sujet) (30)
EMPATTEMENT = 2.6                # m : distance entre les roues avant et arrière
LONGUEUR_VOITURE = 8       # m (4.2)
LARGEUR_VOITURE = 4            # m  (1.8)
ACCELERATION_LATERALE_MAX = 12   # m/s² : limite le braquage à grande vitesse (voir voiture.py)
CAPACITE_RESERVOIRE = 150          # L
ALPHA = 0.0001
CONSO = 0.00001
#L/h

# ---------------------------------------------------------------------------
# L'affichage
# ---------------------------------------------------------------------------
LARGEUR_FENETRE = 1100           # pixels
HAUTEUR_FENETRE = 720            # pixels
HAUTEUR_BANDEAU = 60             # pixels : bande du haut où s'affichent le chrono et la vitesse
ECHELLE = 2.0                    # pixels par mètre. Si le circuit sort de l'écran, diminuez-la.
AGRANDIR_VOITURE = 2.0           # la voiture est dessinée 2 fois plus grande, pour bien la voir
IMAGES_PAR_SECONDE = 60

# ---------------------------------------------------------------------------
# Les couleurs : (rouge, vert, bleu), chaque valeur entre 0 et 255
# ---------------------------------------------------------------------------
COULEUR_HERBE = (76, 132, 68)
COULEUR_PISTE = (90, 90, 96)
COULEUR_BORD = (235, 235, 235)
COULEUR_LIGNE_CENTRALE = (130, 130, 138)
COULEUR_VOITURE = (220, 50, 40)
COULEUR_BANDEAU = (25, 27, 33)
COULEUR_TEXTE = (240, 240, 240)
COULEUR_ALERTE = (255, 90, 70)
COULEUR_RAVITAILLEMENT = (24, 93, 158)


