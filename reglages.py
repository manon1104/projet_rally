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
CIRCUIT_CHOISI = "circuit_4"     # nom d'un circuit de mes_circuits.py : "rectangle"
NOMBRE_DE_TOURS = 3              # imposé par le sujet : 3 par défaut, entre 2 et 5
LARGEUR_PISTE = 12              # m (imposé par le sujet) (12)
DT = 0.1                         # pas de temps de la simulation, en secondes (imposé par le sujet)
NOMBRE_VOITURE = 2

# ---------------------------------------------------------------------------
# La voiture (voiture de rallye du sujet)
# ---------------------------------------------------------------------------
ACCELERATION = 8
VITESSE_MAX_KMH = 200
FREINAGE = 12                     # m/s² quand on appuie sur « bas »
VITESSE_RECUL_MAX = 5            # m/s : on peut reculer, mais lentement
BRAQUAGE_MAX_DEGRES = 30         # angle maximal des roues (imposé par le sujet)
EMPATTEMENT = 2.6                # m : distance entre les roues avant et arrière
LONGUEUR_VOITURE = 4.2       # m (4.2)
LARGEUR_VOITURE = 1.8            # m  (1.8)
ACCELERATION_LATERALE_MAX = 12   # m/s² : limite le braquage à grande vitesse (voir voiture.py)
CAPACITE_RESERVOIRE = 50
ALPHA = 0.0001
CONSO = 0.00001                    #L/h

VOITURES = {
    "Moto": {
        "couleur": (220, 50, 40),
        "vitesse_max": 220,
        "réservoire": 15,
        "seuil de dérapage": 0.8,
        "accélération": 10,
        "longueur": 4.2,
        "largeur": 1
    },

    "Rallye": {
        "couleur": (30, 100, 220),
        "vitesse_max": 200,
        "réservoire": 50,
        "seuil de dérapage": 1,
        "accélération": 8,
        "longueur": 4.2,
        "largeur": 1.8
    },

    "Course": {
        "couleur": (220, 50, 40),
        "vitesse_max": 280,
        "réservoire": 40,
        "seuil de dérapage": 1.2,
        "accélération": 12,
        "longueur": 4.2,
        "largeur": 1.8
    }
}

# ---------------------------------------------------------------------------
# L'affichage
# ---------------------------------------------------------------------------
LARGEUR_FENETRE = 1100           # pixels
HAUTEUR_FENETRE = 720            # pixels
HAUTEUR_BANDEAU = 80             # pixels : bande du haut où s'affichent le chrono et la vitesse
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
COULEUR_VOITURE_2 = (30, 100, 220)
COULEUR_BANDEAU = (25, 27, 33)
COULEUR_TEXTE = (240, 240, 240)
COULEUR_ALERTE = (255, 90, 70)
COULEUR_RAVITAILLEMENT = (24, 93, 158)

# ajout de qqls réglages pour le pilote automatique
DIST_STATION = 150
DIST_APPROCHE = 30
MARGE_ESSENCE = 1.15
STATIONS = {
    "rectangle": (54, 59),
    "circuit_rond": (91, 166),
    "circuit_2": (312, 40),
    "circuit_3": (359, 217),
    "circuit_4": (242, 62),}


