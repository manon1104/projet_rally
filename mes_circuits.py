"""
LES CIRCUITS
============

Un circuit est une LISTE DE POINTS (x, y), en mètres. Ces points forment la
LIGNE CENTRALE de la piste. La piste s'étend de chaque côté de cette ligne,
sur LARGEUR_PISTE mètres au total (voir reglages.py).



Les règles :
  - le PREMIER point est la ligne de départ et d'arrivée ;
  - on roule dans l'ordre des points ;
  - le dernier point est relié automatiquement au premier (inutile de le répéter) ;
  - comme sur l'écran, x va vers la DROITE et y vers le BAS ;
  - avec ECHELLE = 2, l'écran montre environ 550 m de large et 330 m de haut.

Pour créer votre circuit :
  1. copiez un exemple et changez ses points ;
  2. ajoutez-le dans le dictionnaire CIRCUITS, tout en bas de ce fichier ;
  3. choisissez-le dans reglages.py (CIRCUIT_CHOISI).
"""

# Exemple : un rectangle aux coins coupés, écrit point par point.

RECTANGLE = [
    (250, 290),   # départ / arrivée
    (440, 290),
    (490, 270),   # coin en bas à droite (2 points pour l'adoucir)
    (510, 220), (510, 90),
    (490, 40),    # coin en haut à droite
    (440, 20), (110, 20),
    (60, 40),     # coin en haut à gauche
    (40, 90), (40, 220),
    (60, 270),    # coin en bas à gauche
    (110, 290),
]

CIRCUIT_2 = [
    (250, 290),   # départ / arrivée
    (440, 290),
    (490, 270),   # coin en bas à droite (2 points pour l'adoucir)
    (510, 220), (510, 90),
    (490, 40),    # coin en haut à droite
    (440, 10),(430,10),
    (400,40), (400,180), (380,200), (360, 180), (350, 60), (320, 40), # point au centre
    (60, 40),  (40,60),   # coin en haut à gauche
    (40, 90), (40,260),
    (50, 270), (100, 270), (110, 260),   # coin en bas à gauche
    (130,100), (145,90), (160, 100),
    (190, 270), (200,290)
]

RAVITO = [
    (250, 290),   # départ / arrivée
    (440, 290),
    (490, 270),   # coin en bas à droite (2 points pour l'adoucir)
    (510, 220), (510, 90),
    (490, 40),    # coin en haut à droite
    (440, 20), (110, 20),
    (60, 40),     # coin en haut à gauche
    (40, 90),(30,60), (40, 220),
    (60, 270),    # coin en bas à gauche
    (110, 290),
]



CIRCUITS = {
    "rectangle": RECTANGLE,
    "circuit_2" : CIRCUIT_2,
    "ravito": RAVITO
}
