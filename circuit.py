"""
Un circuit est fait de SEGMENTS : chaque point est relié au suivant, et le
dernier au premier.

        point 0 ──── point 1 ──── point 2 ── … ── dernier point
           ▲                                           │
           └───────────────────────────────────────────┘

La piste, c'est tout ce qui est à moins d'une demi-largeur (6 m) de ces
segments. Pour savoir si la voiture est sur la piste, on calcule donc sa
distance au segment le plus proche.

Comme la classe Voiture, cette classe ne dessine rien (le dessin est dans jeu.py).
"""

import math


def distance_point_segment(px, py, a, b):
    """Distance entre le point (px, py) et le segment qui va du point a au point b.

    Idée : on cherche le point du segment le plus proche de (px, py).
    On le repère par un nombre t : t = 0 au début du segment (a), t = 1 à la fin (b),
    t = 0.5 au milieu. On calcule t par projection, puis on le garde entre 0 et 1
    pour rester sur le segment.
    """
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    longueur_au_carre = dx * dx + dy * dy
    if longueur_au_carre == 0:                     # segment réduit à un point
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / longueur_au_carre
    t = max(0.0, min(1.0, t))
    plus_proche_x = ax + t * dx
    plus_proche_y = ay + t * dy
    return math.hypot(px - plus_proche_x, py - plus_proche_y)


class Circuit:
    """La piste : sa ligne centrale (une liste de points) et sa largeur."""

    def __init__(self, nom, points, largeur):
        if len(points) < 3:
            raise ValueError("Un circuit a besoin d'au moins 3 points.")
        self.nom = nom
        self.points = points
        self.largeur = largeur

        # Les segments : (point de début, point de fin). Le dernier revient au premier.
        # « % len(points) » ramène l'indice à 0 quand on dépasse la fin de la liste.
        self.segments = []
        for i in range(len(points)):
            self.segments.append((points[i], points[(i + 1) % len(points)]))

        # La longueur d'un tour : la somme des longueurs des segments.
        self.longueur = 0.0
        for a, b in self.segments:
            self.longueur = self.longueur + math.hypot(b[0] - a[0], b[1] - a[1])

        # Le départ : le premier point, orienté vers le deuxième.
        self.x_depart, self.y_depart = points[0]
        x_suivant, y_suivant = points[1]
        self.angle_depart = math.atan2(y_suivant - self.y_depart, x_suivant - self.x_depart)

    def distance_au_centre(self, x, y):
        """Distance (m) entre le point (x, y) et la ligne centrale de la piste."""
        plus_petite = math.inf
        for a, b in self.segments:
            plus_petite = min(plus_petite, distance_point_segment(x, y, a, b))
        return plus_petite

    def est_sur_la_piste(self, x, y):
        """Vrai si le point (x, y) est sur la piste."""
        return self.distance_au_centre(x, y) <= self.largeur / 2
