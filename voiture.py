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


import math
import pygame


from reglages import (ACCELERATION, ACCELERATION_LATERALE_MAX, BRAQUAGE_MAX_DEGRES, EMPATTEMENT,
                     FREINAGE, LARGEUR_VOITURE, LONGUEUR_VOITURE, VITESSE_MAX_KMH, VITESSE_RECUL_MAX, CAPACITE_RESERVOIRE)






def borner(valeur, minimum, maximum):
   """Ramène `valeur` entre `minimum` et `maximum`."""
   return max(minimum, min(maximum, valeur))




class Voiture:
   """Une voiture : position, orientation, vitesse."""


   def __init__(self, x, y, angle, jeu):
       """Crée une voiture à l'arrêt au point (x, y), orientée selon `angle` (en radians)."""
       self.x = x
       self.y = y
       self.angle = angle
       self.jeu = jeu
       self.vitesse = 0.0

       # Ajout de variables qui gèrent le dérapage
       self.debut_derap = 0.0
       self.bool_derap = False
       self.temps_derap = 0.0
       self.angle_glissement = 0.0
       self.glissement = 0.0
       self.mu = 1

       # Initialisation du choix de voiture
       self.choix = 'voiture'

       # négative en marche arrière
       self.vitesse_max = VITESSE_MAX_KMH / 3.6  # km/h → m/s
       self.k = 100
       self.reservoir = CAPACITE_RESERVOIRE


       # Position au pas précédent. Elle sert uniquement à rendre l'animation
       # fluide (voir la méthode coins). Vous pouvez l'ignorer pour l'instant.
       self.ancien_x = x
       self.ancien_y = y
       self.ancien_angle = angle

       # On gère maintenant la taille de la voiture avec une variable pour pouvoir changer dans le cas de la moto
       self.longueur = LONGUEUR_VOITURE
       self.largeur = LARGEUR_VOITURE



   def avancer(self, acceleration, braquage, dt):
       """Fait avancer la voiture pendant `dt` secondes.


       acceleration : en m/s². Positive pour accélérer, négative pour freiner
                      (puis reculer une fois arrêté).
       braquage     : angle des roues en radians. Positif : à droite.
                      Négatif : à gauche.
       """
       self.ancien_x, self.ancien_y, self.ancien_angle = self.x, self.y, self.angle


       # 0) On vérifie si l'on est dans une dirconstance de dérapage (ie si on tourne)
       touches = pygame.key.get_pressed()
       if touches[pygame.K_LEFT] or touches[pygame.K_RIGHT]:

           # Booléen qui vérifie le début du tour, calcul de l'angle de dérapage (angle entre le début du tour et l'angle actuel)
           if self.debut_tourner == True:
               self.angle_depart_derapage = self.angle
               self.debut_tourner = False
           self.angle_derapage = abs((self.angle - self.angle_depart_derapage + math.pi) % (2 * math.pi) - math.pi)

       else:
           self.debut_tourner = True
           self.angle_depart_derapage = self.angle


       #0) On cherche sur quel type de matériel on est :
       if self.jeu.couleur_sous_roues == (255,255,255) :
           self.mu = 0.3
       elif self.jeu.couleur_sous_roues == (90,90,96) :
           self.mu = 1.0
       elif self.jeu.couleur_sous_roues == (77,47,25) :
           self.mu = 0.7
       else:
           self.mu = 1.0

       # 1) On respecte les valeurs maximales.
       acceleration = borner(acceleration, -FREINAGE, ACCELERATION)
       limite = self.braquage_max()
       braquage = borner(braquage, -limite, limite)


       # 2) La vitesse change : accélération moins frottement. On modifie en même temps la direction car condition
       #condition sur le dérapage qui modifie la vitesse
       if not self.bool_derap:

           # On vérifie si la condition de dérapage est vérifiée
           if (self.vitesse ** 2) * abs(math.sin(braquage)) > self.mu * self.k:
               self.temps_derap = self.jeu.temps
               self.bool_derap = True

            # On remet la variable de début de dérapage à 0
           else:
               if (self.vitesse ** 2) * abs(math.sin(braquage)) < self.mu * self.k*0.7:
                   if self.jeu.temps - self.temps_derap > 0.4:
                       self.bool_derap = False

       frottement = ACCELERATION / self.vitesse_max

       # dans le cas du dérapage, on a plus de frottements
       if self.bool_derap:
           frottement *= 1.5

       self.vitesse = self.vitesse + (acceleration - frottement * self.vitesse) * dt
       self.vitesse = borner(self.vitesse, -VITESSE_RECUL_MAX, self.vitesse_max)

       # 3) L'orientation change (« modèle bicyclette ») : plus on va vite et
       #    plus les roues sont tournées, plus la voiture tourne vite.
       vitesse_rotation = self.vitesse * math.tan(braquage) / EMPATTEMENT

        # Si la voiture dérape, elle tourne moins vite
       if self.bool_derap:
           vitesse_rotation *= 0.95
       self.angle += vitesse_rotation * dt

       cible_glissement = 0.0

       # En dérapage, on glisse dans le sens opposé au glissement
       if self.bool_derap:
           cible_glissement = -0.25 * math.copysign(1, vitesse_rotation)

        # Pour que le dérapage ne se fasse pas directement
       facteur = min(1.0, 4.0 * dt)
       self.angle_glissement += (cible_glissement - self.angle_glissement) * facteur
       direction = self.angle + self.angle_glissement

       self.x += self.vitesse * math.cos(direction) * dt
       self.y += self.vitesse * math.sin(direction) * dt




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


       demi_longueur = self.longueur / 2 * agrandissement
       demi_largeur = self.largeur / 2 * agrandissement
       cos_a, sin_a = math.cos(angle), math.sin(angle)
       coins = []
       # (vers l'avant, vers le côté) pour chaque coin : avant gauche, avant droit, arrière droit, arrière gauche
       for avant, cote in [(demi_longueur, -demi_largeur), (demi_longueur, demi_largeur),
                           (-demi_longueur, demi_largeur), (-demi_longueur, -demi_largeur)]:
           coins.append((x + avant * cos_a - cote * sin_a,
                         y + avant * sin_a + cote * cos_a))
       return coins
