"""
LA CLASSE JEU
=============

Le jeu possède un circuit et une voiture, et les fait fonctionner ensemble.
C'est le seul fichier qui utilise pygame.

LA BOUCLE DE JEU (méthode lancer)
    Elle tourne environ 60 fois par seconde. À chaque tour :
        1. on regarde les événements (fermeture de la fenêtre, touches) ;
        2. on fait avancer la simulation ;
        3. on redessine tout l'écran.

LE PAS DE TEMPS FIXE
    Le sujet impose que la simulation avance par pas de DT = 0,1 s, alors que
    l'écran se redessine toutes les 1/60 s. On met donc le temps écoulé de
    côté dans une « réserve ». Chaque fois qu'elle contient au moins 0,1 s, on
    fait UN pas de simulation (méthode faire_un_pas) et on retire 0,1 s.

LES ÉTATS DU JEU (attribut self.etat)
    "accueil" : écran de départ, la voiture attend ;
    "course"  : la course est lancée ;
    "fin"     : la course est terminée (À FAIRE : y passer après le dernier tour).
"""

import math

import pygame

from circuit import Circuit
from mes_circuits import CIRCUITS
from reglages import (ACCELERATION, AGRANDIR_VOITURE, BRAQUAGE_MAX_DEGRES, CIRCUIT_CHOISI, COULEUR_ALERTE,
                      COULEUR_BANDEAU, COULEUR_BORD, COULEUR_HERBE, COULEUR_LIGNE_CENTRALE, COULEUR_PISTE,
                      COULEUR_TEXTE, COULEUR_VOITURE, DT, ECHELLE, FREINAGE, HAUTEUR_BANDEAU, HAUTEUR_FENETRE,
                      IMAGES_PAR_SECONDE, LARGEUR_FENETRE, LARGEUR_PISTE, NOMBRE_DE_TOURS, CAPACITE_RESERVOIRE, ALPHA, CONSO)
from voiture import Voi


def formater_temps(secondes):
    """83.4 secondes → « 1:23.4 »."""
    minutes = int(secondes // 60)
    return f"{minutes}:{secondes - 60 * minutes:04.1f}"


class Jeu:
    """La fenêtre, la boucle de jeu, le clavier et le dessin."""

    def __init__(self):
        pygame.init()
        self.ecran = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
        pygame.display.set_caption("Rally Breizh Furious")
        self.horloge = pygame.time.Clock()
        self.police = pygame.font.SysFont("arial", 22)
        self.grande_police = pygame.font.SysFont("arial", 48, bold=True)

        self.circuit = Circuit(CIRCUIT_CHOISI, CIRCUITS[CIRCUIT_CHOISI], LARGEUR_PISTE)
        self.en_marche = True
        self.nouvelle_partie()
        # a modifier si on change de circuit ou alors il faut qu'il y ait le même nombre de point ddns les deux circuits
        self.troncons = [
            (0,10, (90, 90, 96)),
            (10,20,(255,255,255)),
            (20,26,(77, 47, 25))
        ]

    def nouvelle_partie(self):
        """Remet la voiture sur la ligne de départ et le chrono à zéro."""
        self.voiture = Voiture(self.circuit.x_depart, self.circuit.y_depart, self.circuit.angle_depart)
        self.etat = "accueil"
        self.temps = 0.0                  # temps de course, en secondes
        self.reserve_de_temps = 0.0       # voir « le pas de temps fixe » en haut du fichier
        self.sur_la_piste = True
        self.tour = 1
        self.temps_tour_1 = 0.0
        self.temps_tour_2 = 0.0
        self.temps_tour_3 = 0.0
        self.last_pos_valide = (self.circuit.x_depart, self.circuit.y_depart)
        self.sortie = True
        self.temps_sortie = 0
        self.penalite = [0,0,0]
        self.penalite_tot = 0
        self.essence = CAPACITE_RESERVOIRE
        # numéro du tour en cours
        # À FAIRE (partie 1) : ajouter ici ce qu'il faut pour compter les tours,
        # mémoriser le temps de chaque tour et le dernier point valide.


    def compter_tour(self):
        if self.temps > 5 and self.voiture.x >= self.circuit.x_depart and self.voiture.ancien_x <= self.circuit.x_depart and abs((self.voiture.y - self.circuit.y_depart))<= self.circuit.largeur/2:
            if self.tour ==1:
                self.temps_tour_1 = self.temps
            elif self.tour ==2:
                self.temps_tour_2 = self.temps - self.temps_tour_1
            elif self.tour ==3:
                self.temps_tour_3 = self.temps - self.temps_tour_2
            self.tour += 1
            if self.tour == (NOMBRE_DE_TOURS+1):
                self.etat = 'fin'


    def derniere_pos_valide(self):
        if self.sur_la_piste == True:
            self.last_pos_valide = (self.voiture.x, self.voiture.y)


    def lancer(self):
        """Fait tourner le jeu jusqu'à ce qu'on ferme la fenêtre."""
        while self.en_marche:
            temps_ecoule = self.horloge.tick(IMAGES_PAR_SECONDE) / 1000   # en secondes

            # 1. Les événements
            self.gerer_evenements()

            # 2. La simulation, par pas fixes de DT
            if self.etat == "course":
                self.reserve_de_temps = self.reserve_de_temps + min(temps_ecoule, 0.25)
                while self.reserve_de_temps >= DT:
                    self.faire_un_pas()
                    self.reserve_de_temps = self.reserve_de_temps - DT

            # 3. Le dessin
            self.dessiner()
        pygame.quit()

    def gerer_evenements(self):
        """Fermeture de la fenêtre et touches Espace, R, Échap."""
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_marche = False
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.en_marche = False
                elif evenement.key == pygame.K_SPACE and self.etat == "accueil":
                    self.etat = "course"
                elif evenement.key == pygame.K_r:
                    self.nouvelle_partie()


    def lire_commandes_clavier(self):
        """Transforme les touches enfoncées en commandes : (accélération, braquage)."""
        touches = pygame.key.get_pressed()

        acceleration = 0.0                                   # aucune touche : roue libre
        if touches[pygame.K_UP] or touches[pygame.K_z]:
            acceleration = ACCELERATION
        elif touches[pygame.K_DOWN] or touches[pygame.K_s]:
            acceleration = -FREINAGE

        braquage = 0.0
        braquage_max = math.radians(BRAQUAGE_MAX_DEGRES)
        if touches[pygame.K_LEFT] or touches[pygame.K_q]:
            braquage = -braquage_max                         # négatif : à gauche
        elif touches[pygame.K_RIGHT] or touches[pygame.K_d]:
            braquage = braquage_max                          # positif : à droite

        return acceleration, braquage


    def consommation(self):
        return  ALPHA*self.voiture.vitesse*self.voiture.vitesse + CONSO

    def faire_un_pas(self):
        """Un pas de simulation de DT secondes."""
        # 1) Lire les commandes
        acceleration, braquage = self.lire_commandes_clavier()

        # 2) Mettre à jour la position
        self.voiture.avancer(acceleration, braquage, DT)
        self.temps = self.temps + DT

        # 3) La voiture est-elle sur la piste ?
        self.sur_la_piste = self.circuit.est_sur_la_piste(self.voiture.x, self.voiture.y)

        # À FAIRE (partie 1) — sortie de piste.
        #   Pour l'instant, on affiche seulement « HORS PISTE ». Le sujet demande :
        #   vitesse réduite, retour au dernier point valide, pénalité de temps.
        #   Idée : à chaque pas où la voiture est sur la piste, mémoriser sa position.
        if self.sur_la_piste == False:
            self.voiture.vitesse = self.voiture.vitesse/1.1
            if self.sortie == True:
                self.temps_sortie = self.temps
                self.penalite_tot = self.penalite_tot + 1
                self.sortie = False
                if self.tour == 1:
                    self.penalite[0] += 1
                elif self.tour == 2:
                    self.penalite[1] += 1
                elif self.tour == 3:
                    self.penalite[2] += 1
            elif (self.temps - self.temps_sortie)> 2:
                self.voiture.x = self.last_pos_valide[0]
                self.voiture.y = self.last_pos_valide[1]
                self.sortie = True

        self.compter_tour()
        self.derniere_pos_valide()

        if self.essence > 0:
            self.essence = self.essence - self.consommation()
        if self.essence <= 0:
            self.essence = 0
            self.voiture.vitesse = 0
        if 50 <= self.voiture.x <= 80 and 50 <= self.voiture.y <= 70 and self.essence < 50:
            self.essence = self.essence + 0.5






        # À FAIRE (partie 1) — compter les tours et le temps de chaque tour.
        #   Idée : un tour est bouclé quand la voiture franchit la ligne de départ
        #   (le premier point du circuit) APRÈS être passée par un point de passage
        #   situé à l'opposé du circuit. Sinon, des allers-retours sur la ligne
        #   compteraient des tours !

        # À FAIRE (partie 1) — fin de course.
        #   Après NOMBRE_DE_TOURS tours, passer à l'écran de fin : self.etat = "fin"

    # essence
    def quantite_essence(self):
        self.quantite = CAPACITE_RESERVOIRE
        while self.quantite > 0:
            self.quantite = self.quantite - self.consommation()


    # Le dessin
    def vers_ecran(self, x, y):
        """Convertit un point du circuit (en mètres) en position à l'écran (en pixels)."""
        return (x * ECHELLE, HAUTEUR_BANDEAU + y * ECHELLE)

    def dessiner(self):
        """Redessine tout l'écran, puis l'affiche."""
        self.ecran.fill(COULEUR_HERBE)
        self.dessiner_piste()
        self.dessiner_voiture()
        self.dessiner_bandeau()
        if self.etat == "course" and not self.sur_la_piste:
            self.ecrire_au_centre("HORS PISTE", self.grande_police, COULEUR_ALERTE, HAUTEUR_FENETRE // 2 - 30)
        if self.etat == "accueil":
            self.dessiner_accueil()
        if self.etat == "fin":
            self.dessiner_fin()
        pygame.display.flip()


    def dessiner_piste(self):
        """La piste : un rectangle autour de chaque segment, et un disque sur chaque point
        pour arrondir les jointures. D'abord en blanc et un peu plus large (les bords),
        puis en gris par-dessus."""
        for debut, fin, couleur in self.troncons:
            for couleur, demi_largeur in [(COULEUR_BORD, LARGEUR_PISTE / 2 + 1), (couleur, LARGEUR_PISTE / 2)]:
                for i in range(debut, min(fin, len(self.circuit.segments))):
                    (ax, ay), (bx, by) = self.circuit.segments[i]
                    longueur = math.hypot(bx - ax, by - ay)
                    px = -(by - ay) / longueur * demi_largeur
                    py = (bx - ax) / longueur * demi_largeur
                    rectangle = [self.vers_ecran(ax + px, ay + py), self.vers_ecran(bx + px, by + py),
                                 self.vers_ecran(bx - px, by - py), self.vers_ecran(ax - px, ay - py)]
                    pygame.draw.polygon(self.ecran, couleur, rectangle)
                for i in range(debut, min(fin + 1, len(self.circuit.points))):
                    x, y = self.circuit.points[i]
                    pygame.draw.circle(self.ecran, couleur, self.vers_ecran(x, y), int(demi_largeur * ECHELLE))
                pygame.draw.rect(self.ecran, (24, 93, 158), (90, 160, 30, 40))





        # La ligne centrale (fine) : ce sont les points de mes_circuits.py
        points_ecran = [self.vers_ecran(x, y) for x, y in self.circuit.points]
        pygame.draw.lines(self.ecran, COULEUR_LIGNE_CENTRALE, True, points_ecran, 1)

        # La ligne de départ : un trait blanc en travers de la piste
        angle = self.circuit.angle_depart
        x0, y0 = self.circuit.x_depart, self.circuit.y_depart
        dx, dy = -math.sin(angle) * LARGEUR_PISTE / 2, math.cos(angle) * LARGEUR_PISTE / 2
        pygame.draw.line(self.ecran, COULEUR_BORD, self.vers_ecran(x0 + dx, y0 + dy),
                         self.vers_ecran(x0 - dx, y0 - dy), 4)


    def dessiner_voiture(self):
        """La voiture : un rectangle tourné, avec un trait blanc à l'avant."""
        # Fraction du pas déjà écoulée, pour dessiner la voiture entre deux pas
        fraction = self.reserve_de_temps / DT if self.etat == "course" else 1.0
        coins = [self.vers_ecran(x, y) for x, y in self.voiture.coins(fraction, AGRANDIR_VOITURE)]
        pygame.draw.polygon(self.ecran, COULEUR_VOITURE, coins)
        pygame.draw.line(self.ecran, COULEUR_BORD, coins[0], coins[1], 3)   # l'avant

    def dessiner_bandeau(self):
        """La bande du haut : tour, temps, vitesse."""
        pygame.draw.rect(self.ecran, COULEUR_BANDEAU, (0, 0, LARGEUR_FENETRE, HAUTEUR_BANDEAU))
        texte = (f"Tour {self.tour} / {NOMBRE_DE_TOURS}        "
                 f"Temps : {formater_temps(self.temps)}        "
                 f"Vitesse : {self.voiture.vitesse_kmh():.0f} km/h"
                 f"Essence : {self.essence:.0f} L")
        self.ecrire(texte, 20, 18, COULEUR_TEXTE)
        self.ecrire("R : recommencer    Échap : quitter", LARGEUR_FENETRE - 360, 18, COULEUR_LIGNE_CENTRALE)

    def dessiner_accueil(self):
        """L'écran de départ, par-dessus le circuit."""
        self.voile()
        self.ecrire_au_centre("Rally", self.grande_police, COULEUR_TEXTE, 230)
        self.ecrire_au_centre(f"Circuit : {self.circuit.nom}   ({self.circuit.longueur:.0f} m)   "
                              f"{NOMBRE_DE_TOURS} tours", self.police, COULEUR_TEXTE, 310)
        self.ecrire_au_centre("Flèches (ou Z Q S D) pour conduire", self.police, COULEUR_TEXTE, 350)
        self.ecrire_au_centre("Appuie sur ESPACE pour démarrer", self.grande_police, COULEUR_ALERTE, 420)

    def dessiner_fin(self):
        """L'écran de fin. À FAIRE (partie 1) : afficher aussi le temps de chaque tour."""
        self.voile()
        self.ecrire_au_centre("Course terminée !", self.grande_police, COULEUR_TEXTE, 260)
        self.ecrire_au_centre(f"Temps total : {formater_temps(self.temps +2*self.penalite_tot)}", self.police, COULEUR_TEXTE, 340)
        self.ecrire_au_centre("R pour rejouer", self.police, COULEUR_TEXTE, 400)
        self.ecrire_au_centre(f"Temps tour 1 :{formater_temps(self.temps_tour_1+ 2*self.penalite[0])}, avec {self.penalite[0]} pénalités", self.police, COULEUR_TEXTE, 440)
        self.ecrire_au_centre(f"Temps tour 2 :{formater_temps(self.temps_tour_2 + 2*self.penalite[1])}, avec {self.penalite[1]} pénalités ", self.police, COULEUR_TEXTE, 480)
        self.ecrire_au_centre(f"Temps tour 3 :{formater_temps(self.temps_tour_3+ 2*self.penalite[2])}, avec {self.penalite[2]} pénalités", self.police, COULEUR_TEXTE, 520)
        self.ecrire_au_centre(f"Total des pénalités : {self.penalite_tot}" ,self.police, COULEUR_TEXTE, 560)
    # Petits outils de dessin
    def voile(self):
        """Assombrit l'écran (pour faire ressortir un texte par-dessus)."""
        voile = pygame.Surface((LARGEUR_FENETRE, HAUTEUR_FENETRE), pygame.SRCALPHA)
        voile.fill((0, 0, 0, 150))       # noir, à moitié transparent
        self.ecran.blit(voile, (0, 0))

    def ecrire(self, texte, x, y, couleur, police=None):
        """Écrit un texte à la position (x, y) de l'écran."""
        if police is None:
            police = self.police
        image = police.render(texte, True, couleur)   # pygame transforme le texte en image…
        self.ecran.blit(image, (x, y))                # … que l'on colle sur l'écran

    def ecrire_au_centre(self, texte, police, couleur, y):
        """Écrit un texte centré horizontalement, à la hauteur y."""
        image = police.render(texte, True, couleur)
        self.ecran.blit(image, ((LARGEUR_FENETRE - image.get_width()) // 2, y))