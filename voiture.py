"""
LA CLASSE VOITURE
=================

Une voiture connaît sa position (x, y), son orientation (angle) et sa vitesse.
Elle sait faire une chose : AVANCER pendant un pas de temps, à partir de deux
commandes, l'accélération et le braquage (comme le demande le sujet).

Elle ne dessine rien et ne lit pas le clavier : c'est le rôle de jeu.py.
Ainsi, en partie 3, une intelligence artificielle pourra conduire la même
voiture en lui envoyant les mêmes commandes.

Le repère est celui de l'écran, en mètres :
    x vers la droite, y vers le BAS ;
    angle = 0 : la voiture regarde vers la droite ;
    l'angle augmente quand la voiture tourne à droite (sens des aiguilles d'une montre).
"""

'''import math
import pygame

from reglages import (ACCELERATION, ACCELERATION_LATERALE_MAX, BRAQUAGE_MAX_DEGRES, EMPATTEMENT,
                      FREINAGE, LARGEUR_VOITURE, LONGUEUR_VOITURE, VITESSE_MAX_KMH, VITESSE_RECUL_MAX)



def borner(valeur, minimum, maximum):
    """Ramène `valeur` entre `minimum` et `maximum`."""
    return max(minimum, min(maximum, valeur))


class Voiture:
    """Une voiture : position, orientation, vitesse."""

    def __init__(self, x, y, angle, jeu):
        """Crée une voiture à l'arrêt au point (x, y), orientée selon `angle` (en radians)."""
        self.x = x
        self.y = y
        self.k = 10
        self.angle = angle
        self.jeu = jeu
        self.mu = 1
        self.vitesse = 0.0                       # négative en marche arrière
        self.vitesse_max = VITESSE_MAX_KMH / 3.6  # km/h → m/s

        # Position au pas précédent. Elle sert uniquement à rendre l'animation
        # fluide (voir la méthode coins). Vous pouvez l'ignorer pour l'instant.
        self.ancien_x = x
        self.ancien_y = y
        self.ancien_angle = angle

        # Pour le dérapage :
        self.debut_tourner = True
        self.angle_depart_derapage = 0
        self.angle_derapage = 0

    def avancer(self, acceleration, braquage, dt):
        """Fait avancer la voiture pendant `dt` secondes.

        acceleration : en m/s². Positive pour accélérer, négative pour freiner
                       (puis reculer une fois arrêté).
        braquage     : angle des roues en radians. Positif : à droite.
                       Négatif : à gauche.
        """
        self.ancien_x, self.ancien_y, self.ancien_angle = self.x, self.y, self.angle

        # 0) On vérifie si l'on est dans une dirconstance de dérapage
        touches = pygame.key.get_pressed()
        if touches[pygame.K_LEFT] or touches[pygame.K_RIGHT]:
            if self.debut_tourner == True:
                self.angle_depart_derapage = self.angle
                self.debut_tourner = False
            self.angle_derapage = abs(self.angle_depart_derapage - self.angle)

        elif touches[pygame.K_UP] or touches[pygame.K_DOWN]:
            self.debut_tourner = True
            self.angle_depart_derapage = 0

        #0) On cherche sur quel type de matériel on est :
        if self.jeu.couleur_sous_roues == (255,255,255) :
            self.mu = 0.3
        elif self.jeu.couleur_sous_roues == (90,90,96) :
            self.mu = 1.0
        elif self.jeu.couleur_sous_roues == (77,47,25) :
            self.mu = 0.7


        # 1) On respecte les valeurs maximales.
        acceleration = borner(acceleration, -FREINAGE, ACCELERATION)
        limite = self.braquage_max()
        braquage = borner(braquage, -limite, limite)

        # 2) La vitesse change : accélération moins frottement.
        #    Le frottement est réglé pour que la voiture plafonne à sa vitesse maximale.
        frottement = ACCELERATION / self.vitesse_max
        #condition sur le dérapage qui modifie la vitesse
        if (self.vitesse ** 2) * abs(math.sin(self.angle_derapage)) > self.mu * self.k:
            self.vitesse = self.vitesse * 0.9
        else :
            self.vitesse = self.vitesse + (acceleration - frottement * self.vitesse) * dt
            self.vitesse = borner(self.vitesse, -VITESSE_RECUL_MAX, self.vitesse_max)


        # 3) L'orientation change (« modèle bicyclette ») : plus on va vite et
        #    plus les roues sont tournées, plus la voiture tourne vite.
        self.angle = self.angle + self.vitesse * math.tan(braquage) / EMPATTEMENT * dt


        # 4) La position change : on avance de (vitesse × dt) mètres dans la direction de l'angle.
        if (self.vitesse ** 2) * abs(math.sin(self.angle_derapage)) > self.mu * self.k:
            self.x = self.x + self.vitesse * math.cos(self.angle*1.4) * dt
            self.y = self.y + self.vitesse * math.sin(self.angle*1.4) * dt
        self.x = self.x + self.vitesse * math.cos(self.angle) * dt
        self.y = self.y + self.vitesse * math.sin(self.angle) * dt

    def braquage_max(self):
        """Braquage maximal autorisé (radians) à la vitesse actuelle.

        30° à l'arrêt, moins à grande vitesse : sans cette limite, braquer à 30°
        à 200 km/h ferait pivoter la voiture sur place. On limite l'accélération
        latérale (vitesse² × tan(braquage) / empattement) à ACCELERATION_LATERALE_MAX.
        Partie 2 : le modèle de dérapage du sujet remplacera cette limite.
        """
        limite = math.radians(BRAQUAGE_MAX_DEGRES)
        if abs(self.vitesse) > 1:
            limite = min(limite, math.atan(EMPATTEMENT * ACCELERATION_LATERALE_MAX / self.vitesse ** 2))
        return limite

    def vitesse_kmh(self):
        """La vitesse en km/h, pour l'affichage."""
        return self.vitesse * 3.6

    def coins(self, fraction=1.0, agrandissement=1.0):
        """Les 4 coins du rectangle de la voiture (en mètres), pour la dessiner.

        fraction : 1 = position actuelle, 0 = position au pas précédent, 0.5 = entre
                   les deux. Le jeu dessine la voiture ENTRE deux pas de simulation :
                   l'animation reste fluide même si la simulation n'avance que
                   10 fois par seconde.
        """
        x = self.ancien_x + fraction * (self.x - self.ancien_x)
        y = self.ancien_y + fraction * (self.y - self.ancien_y)
        angle = self.ancien_angle + fraction * (self.angle - self.ancien_angle)

        demi_longueur = LONGUEUR_VOITURE / 2 * agrandissement
        demi_largeur = LARGEUR_VOITURE / 2 * agrandissement
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        coins = []
        # (vers l'avant, vers le côté) pour chaque coin : avant gauche, avant droit, arrière droit, arrière gauche
        for avant, cote in [(demi_longueur, -demi_largeur), (demi_longueur, demi_largeur),
                            (-demi_longueur, demi_largeur), (-demi_longueur, -demi_largeur)]:
            coins.append((x + avant * cos_a - cote * sin_a,
                          y + avant * sin_a + cote * cos_a))
        return coins'''


"""""
LA CLASSE VOITURE
=================

Une voiture connaît sa position (x, y), son orientation (angle) et sa vitesse.
Elle sait faire une chose : AVANCER pendant un pas de temps, à partir de deux
commandes, l'accélération et le braquage (comme le demande le sujet).

Elle ne dessine rien et ne lit pas le clavier : c'est le rôle de jeu.py.
Ainsi, en partie 3, une intelligence artificielle pourra conduire la même
voiture en lui envoyant les mêmes commandes.

Le repère est celui de l'écran, en mètres :
    x vers la droite, y vers le BAS ;
    angle = 0 : la voiture regarde vers la droite ;
    l'angle augmente quand la voiture tourne à droite (sens des aiguilles d'une montre).
"""

import math

from reglages import (ACCELERATION, ACCELERATION_LATERALE_MAX, BRAQUAGE_MAX_DEGRES, EMPATTEMENT,
                      FREINAGE, LARGEUR_VOITURE, LONGUEUR_VOITURE, VITESSE_MAX_KMH, VITESSE_RECUL_MAX)


def borner(valeur, minimum, maximum):
    """Ramène `valeur` entre `minimum` et `maximum`."""
    return max(minimum, min(maximum, valeur))


class Voiture:
    """Une voiture : position, orientation, vitesse."""

    def __init__(self, x, y, angle):
        """Crée une voiture à l'arrêt au point (x, y), orientée selon `angle` (en radians)."""
        self.x = x
        self.y = y
        self.angle = angle
        self.vitesse = 0.0                       # négative en marche arrière
        self.vitesse_max = VITESSE_MAX_KMH / 3.6  # km/h → m/s

        # Position au pas précédent. Elle sert uniquement à rendre l'animation
        # fluide (voir la méthode coins). Vous pouvez l'ignorer pour l'instant.
        self.ancien_x = x
        self.ancien_y = y
        self.ancien_angle = angle

    def avancer(self, acceleration, braquage, dt):
        """Fait avancer la voiture pendant `dt` secondes.

        acceleration : en m/s². Positive pour accélérer, négative pour freiner
                       (puis reculer une fois arrêté).
        braquage     : angle des roues en radians. Positif : à droite.
                       Négatif : à gauche.
        """
        self.ancien_x, self.ancien_y, self.ancien_angle = self.x, self.y, self.angle

        # 1) On respecte les valeurs maximales.
        acceleration = borner(acceleration, -FREINAGE, ACCELERATION)
        limite = self.braquage_max()
        braquage = borner(braquage, -limite, limite)

        # 2) La vitesse change : accélération moins frottement.
        #    Le frottement est réglé pour que la voiture plafonne à sa vitesse maximale.
        frottement = ACCELERATION / self.vitesse_max
        self.vitesse = self.vitesse + (acceleration - frottement * self.vitesse) * dt
        self.vitesse = borner(self.vitesse, -VITESSE_RECUL_MAX, self.vitesse_max)

        # 3) L'orientation change (« modèle bicyclette ») : plus on va vite et
        #    plus les roues sont tournées, plus la voiture tourne vite.
        self.angle = self.angle + self.vitesse * math.tan(braquage) / EMPATTEMENT * dt

        # 4) La position change : on avance de (vitesse × dt) mètres dans la direction de l'angle.
        self.x = self.x + self.vitesse * math.cos(self.angle) * dt
        self.y = self.y + self.vitesse * math.sin(self.angle) * dt

    def braquage_max(self):
        """Braquage maximal autorisé (radians) à la vitesse actuelle.

        30° à l'arrêt, moins à grande vitesse : sans cette limite, braquer à 30°
        à 200 km/h ferait pivoter la voiture sur place. On limite l'accélération
        latérale (vitesse² × tan(braquage) / empattement) à ACCELERATION_LATERALE_MAX.
        Partie 2 : le modèle de dérapage du sujet remplacera cette limite.
        """
        limite = math.radians(BRAQUAGE_MAX_DEGRES)
        if abs(self.vitesse) > 1:
            limite = min(limite, math.atan(EMPATTEMENT * ACCELERATION_LATERALE_MAX / self.vitesse ** 2))
        return limite

    def vitesse_kmh(self):
        """La vitesse en km/h, pour l'affichage."""
        return self.vitesse * 3.6

    def coins(self, fraction=1.0, agrandissement=1.0):
        """Les 4 coins du rectangle de la voiture (en mètres), pour la dessiner.

        fraction : 1 = position actuelle, 0 = position au pas précédent, 0.5 = entre
                   les deux. Le jeu dessine la voiture ENTRE deux pas de simulation :
                   l'animation reste fluide même si la simulation n'avance que
                   10 fois par seconde.
        """
        x = self.ancien_x + fraction * (self.x - self.ancien_x)
        y = self.ancien_y + fraction * (self.y - self.ancien_y)
        angle = self.ancien_angle + fraction * (self.angle - self.ancien_angle)

        demi_longueur = LONGUEUR_VOITURE / 2 * agrandissement
        demi_largeur = LARGEUR_VOITURE / 2 * agrandissement
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        coins = []
        # (vers l'avant, vers le côté) pour chaque coin : avant gauche, avant droit, arrière droit, arrière gauche
        for avant, cote in [(demi_longueur, -demi_largeur), (demi_longueur, demi_largeur),
                            (-demi_longueur, demi_largeur), (-demi_longueur, -demi_largeur)]:
            coins.append((x + avant * cos_a - cote * sin_a,
                          y + avant * sin_a + cote * cos_a))
        return coins
