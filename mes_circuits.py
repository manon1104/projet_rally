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



# 26 points
RECTANGLE = [
    (250, 290),   # départ / arrivée
    (300,290),
    (350,290),
    (400,290),
    (440, 290),
    (490, 270),   # coin en bas à droite (2 points pour l'adoucir)
    (510, 220), (510, 200), (510,160), (510, 90),
    (490, 40),    # coin en haut à droite
    (440, 20),(400,20), (350,20), (300,20), (200,20), (110, 20),
    (60, 40),     # coin en haut à gauche
    (40, 90), (40,160), (40,200), (40, 220),
    (60, 270),    # coin en bas à gauche
    (110, 290),
    (160,290),
    (200,290),
]

# 26 points
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


# 60 points
import math
CIRCUIT_ROND = [
    (
        round(280 + 190 * math.cos(2 * math.pi * i / 60)),
        round(160 + 145 * math.sin(2 * math.pi * i / 60))
    )
    for i in range(60)
]

# 46 points
CIRCUIT_3 = [
    (462, 135), (429, 135), (395, 135),
    (362, 146), (333, 163), (303, 173), (275, 171), (246, 160), (217, 140),
    (188, 119), (159, 98), (134, 76), (126, 55), (140, 39),
    (159, 35), (179, 44), (193, 63), (199, 85), (212, 103),
    (231, 115), (253, 118), (272, 111), (289, 96),
    (306, 77), (324, 59), (342, 49), (360, 53),
    (372, 69), (372, 89),
    (361, 110), (347, 133), (336, 157), (334, 180),
    (341, 199), (358, 214), (380, 227),
    (405, 240), (430, 254), (454, 267), (478, 277),
    (501, 276), (517, 263), (523, 243),
    (515, 150), (499, 135), (478, 135),
]



# 59 points
CIRCUIT_4 = [
    (112, 310), (129, 310), (146, 310),
    (164, 310), (181, 310), (230, 310),(250, 310), (260, 290),
    (213, 195), (225, 172),
    (251, 150), (264, 139),
    (275, 129), (293, 115), (314, 107), (334, 118),
    (355, 119), (371, 102), (390, 100),
    (409, 112), (431, 110), (452, 101), (467, 83), (479, 63),
    (489, 42), (497, 19),
    (477, 15), (455, 21), (433, 27), (411, 33),
    (389, 38), (367, 43),
    (344, 47), (322, 51),
    (299, 55), (277, 58), (254, 61), (232, 65), (213, 77),  (222, 98),
    (235, 118), (217, 126), (198, 114),
    (187, 94), (168, 97), (172, 119),
    (182, 140), (191, 162), (177, 178),
    (156, 176), (139, 159),
    (126, 140), (110, 124),
    (89, 128), (68, 139),
    (55, 150), (55, 171),
    (60, 300), (73, 310)
]

CIRCUITS = {
    "rectangle": RECTANGLE,
    "circuit_2" : CIRCUIT_2,
    "circuit_3" : CIRCUIT_3,
    "circuit_4" : CIRCUIT_4,
    "circuit_rond" : CIRCUIT_ROND
}
