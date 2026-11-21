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
                      IMAGES_PAR_SECONDE, LARGEUR_FENETRE, LARGEUR_PISTE, NOMBRE_DE_TOURS, CAPACITE_RESERVOIRE, ALPHA, CONSO, COULEUR_VOITURE_2,)
from voiture import Voiture


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

        # Circuits disponibles
        self.circuits_disponibles = list(CIRCUITS.keys())
        self.circuit_selectionne = (self.circuits_disponibles.index(CIRCUIT_CHOISI))
        self.en_marche = True
        self.surface_detection = pygame.Surface(self.ecran.get_size())
        self.charger_circuit(self.circuits_disponibles[self.circuit_selectionne])
        self.nouvelle_partie()
        self.etat = "choix_circuit"


    # pour faire la course après avoir lancé le bon circuit
    def charger_circuit(self, nom_circuit):

        self.circuit = Circuit( nom_circuit, CIRCUITS[nom_circuit], LARGEUR_PISTE )
        if nom_circuit == "rectangle":
            self.troncons = [
                (0, 10, (90, 90, 96)),
                (10, 20, (255, 255, 255)),
                (20, 26, (77, 47, 25))]

        elif nom_circuit == "circuit_2":
            self.troncons = [
                (0, 10, (90, 90, 96)),
                (10, 20, (255, 255, 255)),
                (20, 26, (90, 90, 96))]

        elif nom_circuit == "circuit_rond":
            self.troncons = [
                (0, 20, (90, 90, 96)),
                (20, 60, (77, 47, 25))]

        elif nom_circuit == "circuit_3":
            self.troncons = [
                (0, 20, (90, 90, 96)),
                (20, 46, (77, 47, 25))]

        elif nom_circuit == "circuit_4":
            self.troncons = [
                (0, 40, (90, 90, 96)),
                (40, 59, (255, 255, 255))]

        self.nouvelle_partie()

    def nouvelle_partie(self):
        """Remet la voiture sur la ligne de départ et le chrono à zéro."""
        self.voiture = Voiture(self.circuit.x_depart, self.circuit.y_depart+3, self.circuit.angle_depart) # penser à rajouter self pour le dérapage
        self.voiture2 = Voiture(self.circuit.x_depart,self.circuit.y_depart - 3,self.circuit.angle_depart)
        # la ligne de départ n'est pas dans le même sens pour le circuit rond
        if self.circuit.nom == "circuit_rond":
            self.voiture = Voiture(self.circuit.x_depart -3 , self.circuit.y_depart, self.circuit.angle_depart)  # penser à rajouter self pour le dérapage
            self.voiture2 = Voiture(self.circuit.x_depart +3 , self.circuit.y_depart, self.circuit.angle_depart)

        self.etat = "accueil"
        self.temps = 0.0                  # temps de course, en secondes
        self.reserve_de_temps = 0.0       # voir « le pas de temps fixe » en haut du fichier
        self.sur_la_piste = True
        self.sur_la_piste2 = True
        self.tour = 1
        self.tour2 = 1
        self.temps_tour_1 = 0.0
        self.temps_tour2_1 = 0.0
        self.temps_tour_2 = 0.0
        self.temps_tour2_2 = 0.0
        self.temps_tour_3 = 0.0
        self.temps_tour2_3 = 0.0
        self.last_pos_valide = (self.circuit.x_depart, self.circuit.y_depart)
        self.last_pos_valide2 = (self.circuit.x_depart, self.circuit.y_depart)
        self.sortie = True
        self.sortie2 = True
        self.temps_sortie = 0
        self.temps_sortie2 = 0
        self.penalite = [0,0,0]
        self.penalite2 = [0,0,0]
        self.penalite_tot = 0
        self.penalite_tot2 = 0
        self.essence = CAPACITE_RESERVOIRE
        self.essence2 = CAPACITE_RESERVOIRE
        self.couleur_sous_roues = self.surface_detection.get_at((int(self.voiture.x),int(self.voiture.y)))[:3]
        self.est_dans_ravitaillement = False
        self.est_dans_ravitaillement2 = False
        # numéro du tour en cours
        # À FAIRE (partie 1) : ajouter ici ce qu'il faut pour compter les tours,
        # mémoriser le temps de chaque tour et le dernier point valide.


# permet de remettre la voiture au centre de la piste avec un angle nul
    def centre_piste_proche(self, x, y):
        distance_min = float("inf")
        meilleur_point = None
        meilleur_angle = 0
        for (ax, ay), (bx, by) in self.circuit.segments:
            dx = bx - ax
            dy = by - ay
            longueur2 = dx ** 2 + dy ** 2
            if longueur2 == 0:
                continue
            t = ((x - ax) * dx + (y - ay) * dy) / longueur2
            t = max(0, min(1, t))
            px = ax + t * dx
            py = ay + t * dy
            distance = math.hypot(x - px, y - py)
            if distance < distance_min:
                distance_min = distance
                meilleur_point = (px, py)
                meilleur_angle = math.atan2(dy, dx)
        return meilleur_point, meilleur_angle


    def compter_tour(self):
        # dépend du circuit choisi
        if self.circuit.nom == "rectangle" or self.circuit.nom == "circuit_2" or self.circuit.nom == "circuit_4":
            if self.temps > 5 and self.voiture.x >= self.circuit.x_depart and self.voiture.ancien_x <= self.circuit.x_depart and abs((self.voiture.y - self.circuit.y_depart))<= self.circuit.largeur/2:
                if self.tour ==1:
                    self.temps_tour_1 = self.temps
                elif self.tour ==2:
                    self.temps_tour_2 = self.temps - self.temps_tour_1
                elif self.tour ==3:
                    self.temps_tour_3 = self.temps - self.temps_tour_1- self.temps_tour_2
                self.tour += 1
                if self.tour == (NOMBRE_DE_TOURS+1):
                    self.etat = 'fin'

        if self.circuit.nom == "circuit_rond":
            if self.temps > 5 and self.voiture.y >= self.circuit.y_depart and self.voiture.ancien_y <= self.circuit.y_depart and abs((self.voiture.x - self.circuit.x_depart))<= self.circuit.largeur/2:
                if self.tour ==1:
                    self.temps_tour_1 = self.temps
                elif self.tour ==2:
                    self.temps_tour_2 = self.temps - self.temps_tour_1
                elif self.tour ==3:
                    self.temps_tour_3 = self.temps - self.temps_tour_1 - self.temps_tour_2
                self.tour += 1
                if self.tour == (NOMBRE_DE_TOURS+1):
                    self.etat = 'fin'

        if self.circuit.nom == "circuit_3":
            if self.temps > 5 and self.voiture.x <= self.circuit.x_depart and self.voiture.ancien_x >= self.circuit.x_depart and abs((self.voiture.y - self.circuit.y_depart))<= self.circuit.largeur/2:
                if self.tour ==1:
                    self.temps_tour_1 = self.temps
                elif self.tour ==2:
                    self.temps_tour_2 = self.temps - self.temps_tour_1
                elif self.tour ==3:
                    self.temps_tour_3 = self.temps - self.temps_tour_1- self.temps_tour_2
                self.tour += 1
                if self.tour == (NOMBRE_DE_TOURS+1):
                    self.etat = 'fin'


    def compter_tour2(self):
        # dépend du circuit choisi
        if self.circuit.nom == "rectangle" or self.circuit.nom == "circuit_2" or self.circuit.nom == "circuit_4":
            if self.temps > 5 and self.voiture2.x >= self.circuit.x_depart and self.voiture2.ancien_x <= self.circuit.x_depart and abs((self.voiture2.y - self.circuit.y_depart))<= self.circuit.largeur/2:
                if self.tour2 ==1:
                    self.temps_tour_1 = self.temps
                elif self.tour2 ==2:
                    self.temps_tour_2 = self.temps - self.temps_tour2_1
                elif self.tour2 ==3:
                    self.temps_tour_3 = self.temps - self.temps_tour2_1- self.temps_tour2_2
                self.tour2 += 1
                if self.tour2 == (NOMBRE_DE_TOURS+1):
                    self.etat = 'fin'

        if self.circuit.nom == "circuit_rond":
            if self.temps > 5 and self.voiture2.y >= self.circuit.y_depart and self.voiture2.ancien_y <= self.circuit.y_depart and abs((self.voiture2.x - self.circuit.x_depart))<= self.circuit.largeur/2:
                if self.tour2 ==1:
                    self.temps_tour_1 = self.temps
                elif self.tour2 ==2:
                    self.temps_tour_2 = self.temps - self.temps_tour2_1
                elif self.tour2 ==3:
                    self.temps_tour_3 = self.temps - self.temps_tour2_1 - self.temps_tour2_2
                self.tour2 += 1
                if self.tour2 == (NOMBRE_DE_TOURS+1):
                    self.etat = 'fin'

        if self.circuit.nom == "circuit_3":
            if self.temps > 5 and self.voiture2.x <= self.circuit.x_depart and self.voiture2.ancien_x >= self.circuit.x_depart and abs((self.voiture2.y - self.circuit.y_depart))<= self.circuit.largeur/2:
                if self.tour2 ==1:
                    self.temps_tour2_1 = self.temps
                elif self.tour2 ==2:
                    self.temps_tour2_2 = self.temps - self.temps_tour2_1
                elif self.tour2 ==3:
                    self.temps_tour2_3 = self.temps - self.temps_tour2_1- self.temps_tour2_2
                self.tour2 += 1
                if self.tour2 == (NOMBRE_DE_TOURS+1):
                    self.etat = 'fin'

    def derniere_pos_valide(self):
        if self.sur_la_piste == True:
            self.last_pos_valide = (self.voiture.x, self.voiture.y)

    def derniere_pos_valide2(self):
        if self.sur_la_piste2 == True:
            self.last_pos_valide2 = (self.voiture2.x, self.voiture2.y)


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
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_marche = False
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.en_marche = False
                elif self.etat == "choix_circuit":
                    # pour faire le choix du circuit
                    if evenement.key == pygame.K_RIGHT:
                        self.circuit_selectionne = (self.circuit_selectionne + 1) % len(self.circuits_disponibles)
                    elif evenement.key == pygame.K_LEFT:
                        self.circuit_selectionne = (self.circuit_selectionne - 1) % len(self.circuits_disponibles)
                    elif evenement.key == pygame.K_RETURN:
                        nom = self.circuits_disponibles[self.circuit_selectionne]
                        self.charger_circuit(nom)
                elif evenement.key == pygame.K_SPACE and self.etat == "accueil":
                    self.etat = "course"
                elif evenement.key == pygame.K_r:
                    self.nouvelle_partie()

    def lire_commandes_clavier(self):
        """Transforme les touches enfoncées en commandes : (accélération, braquage)."""
        touches = pygame.key.get_pressed()

        acceleration = 0.0                                   # aucune touche : roue libre
        if touches[pygame.K_UP]:
            acceleration = ACCELERATION
        elif touches[pygame.K_DOWN]:
            acceleration = -FREINAGE
        braquage = 0.0
        braquage_max = math.radians(BRAQUAGE_MAX_DEGRES)
        if touches[pygame.K_LEFT]:
            braquage = -braquage_max                         # négatif : à gauche
        elif touches[pygame.K_RIGHT]:
            braquage = braquage_max                          # positif : à droite

        return acceleration, braquage

    def lire_commandes_deuxieme_voiture(self):
        """Transforme les touches enfoncées en commandes : (accélération, braquage)."""
        touches = pygame.key.get_pressed()

        acceleration = 0.0  # aucune touche : roue libre
        if touches[pygame.K_z]:
            acceleration = ACCELERATION
        elif touches[pygame.K_s]:
            acceleration = -FREINAGE
        braquage = 0.0
        braquage_max = math.radians(BRAQUAGE_MAX_DEGRES)
        if  touches[pygame.K_q]:
            braquage = -braquage_max  # négatif : à gauche
        elif touches[pygame.K_d]:
            braquage = braquage_max  # positif : à droite

        return acceleration, braquage

    def consommation(self):
        return  ALPHA*self.voiture.vitesse*self.voiture.vitesse + CONSO

    def consommation2(self):
        return ALPHA * self.voiture2.vitesse * self.voiture2.vitesse + CONSO


    # La fonction faire_un_pas gere les voitures 1 et 2 en même temps.
    # Il aurait surement été plus judicieux de coder une fonction faire_un_pas_2 pour gérer la voiture 2 mais
    # je n'y ai pensé qu'après et ce programme fonctionnant quand même, je l'ai gardé

    def faire_un_pas(self):
        """Un pas de simulation de DT secondes."""
        # 1) Lire les commandes
        # joueur 1
        acceleration, braquage = self.lire_commandes_clavier()
        self.voiture.avancer(acceleration, braquage, DT)
        # joueur 2
        acceleration2, braquage2 = self.lire_commandes_deuxieme_voiture()
        self.voiture2.avancer(acceleration2, braquage2, DT)

        self.temps = self.temps + DT

        # on remet le ravitaillement à faux
        self.est_dans_ravitaillement = False
        self.est_dans_ravitaillement2 = False

        # 3) Voiture 1 sur la piste ?
        self.sur_la_piste = self.circuit.est_sur_la_piste(self.voiture.x, self.voiture.y)
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
            elif (self.temps - self.temps_sortie) > 1:

                centre, angle = self.centre_piste_proche(
                    self.last_pos_valide[0],
                    self.last_pos_valide[1]
                )

                if centre is not None:
                    self.voiture.x = centre[0]
                    self.voiture.y = centre[1]
                    self.voiture.angle = angle

                self.sortie = True

        self.compter_tour()
        self.derniere_pos_valide()

        # Voiture 2 sur la piste
        self.sur_la_piste2 = self.circuit.est_sur_la_piste(self.voiture2.x, self.voiture2.y)
        if self.sur_la_piste2 == False:
            self.voiture2.vitesse = self.voiture2.vitesse / 1.1
            if self.sortie2 == True:
                self.temps_sortie2 = self.temps
                self.penalite_tot2 = self.penalite_tot2 + 1
                self.sortie2 = False
                if self.tour2 == 1:
                    self.penalite2[0] += 1
                elif self.tour2 == 2:
                    self.penalite2[1] += 1
                elif self.tour2 == 3:
                    self.penalite2[2] += 1
            elif (self.temps - self.temps_sortie2) > 1:

                centre2, angle2 = self.centre_piste_proche(self.last_pos_valide2[0], self.last_pos_valide2[1])

                if centre2 is not None:
                    self.voiture2.x = centre2[0]
                    self.voiture2.y = centre2[1]
                    self.voiture2.angle = angle2

                self.sortie2 = True

        self.compter_tour2()
        self.derniere_pos_valide2()

        # Gestion de l'escence_1
        if self.essence > 0:
            self.essence = self.essence - self.consommation()
        if self.essence <= 0:
            self.essence = 0
            self.voiture.vitesse = 0
        # Gestion de l'essence_2
        if self.essence2 > 0:
            self.essence2 = self.essence2 - self.consommation2()
        if self.essence2 <= 0:
            self.essence2 = 0
            self.voiture2.vitesse = 0

        # Ravitaillement_1

        if (self.circuit.nom == "rectangle" and abs(54- self.voiture.x) <= 10 and abs(59-self.voiture.y) <= 10):
            self.est_dans_ravitaillement = True
        elif (self.circuit.nom == "circuit_rond" and abs(self.voiture.x - 91) <= 10 and abs(self.voiture.y - 166)<= 10) :
            self.est_dans_ravitaillement = True
        elif (self.circuit.nom == "circuit_2" and abs(self.voiture.x-312) <= 10 and abs(self.voiture.y-40) <= 10):
            self.est_dans_ravitaillement = True
        elif (self.circuit.nom == "circuit_3" and abs(self.voiture.x-359) <= 10 and abs(self.voiture.y-217) <= 10):
            self.est_dans_ravitaillement = True
        elif (self.circuit.nom == "circuit_4" and  abs(self.voiture.x- 242) <= 10 and abs(self.voiture.y -62) <= 10):
            self.est_dans_ravitaillement = True

        if self.est_dans_ravitaillement == True and self.essence <= CAPACITE_RESERVOIRE:
            self.essence = self.essence + 0.5

        # Ravitaillement_2

        if (self.circuit.nom == "rectangle" and abs(54- self.voiture2.x) <= 10 and abs(59-self.voiture2.y) <= 10):
            self.est_dans_ravitaillement2 = True
        elif (self.circuit.nom == "circuit_rond" and abs(self.voiture2.x - 91) <= 10 and abs(self.voiture2.y - 166)<= 10) :
            self.est_dans_ravitaillement2 = True
        elif (self.circuit.nom == "circuit_2" and abs(self.voiture2.x-312) <= 10 and abs(self.voiture2.y-40) <= 10):
            self.est_dans_ravitaillement2 = True
        elif (self.circuit.nom == "circuit_3" and abs(self.voiture2.x-359) <= 10 and abs(self.voiture2.y-217) <= 10):
            self.est_dans_ravitaillement2 = True
        elif (self.circuit.nom == "circuit_4" and  abs(self.voiture2.x- 242) <= 10 and abs(self.voiture2.y -62) <= 10):
            self.est_dans_ravitaillement2 = True

        if self.est_dans_ravitaillement2 == True and self.essence2 <= CAPACITE_RESERVOIRE:
            self.essence2 = self.essence2 + 0.5




        largeur, hauteur = self.surface_detection.get_size()
        x, y = self.vers_ecran(self.voiture.x, self.voiture.y)
        if 0 <= x < largeur and 0 <= y < hauteur:
            self.couleur_sous_roues = self.surface_detection.get_at((int(x), int(y)))[:3]
        else:
            self.couleur_sous_roues = None


    # Le dessin
    def vers_ecran(self, x, y):
        """Convertit un point du circuit (en mètres) en position à l'écran (en pixels)."""
        return (x * ECHELLE, HAUTEUR_BANDEAU + y * ECHELLE)

    def dessiner(self):
        """Redessine tout l'écran, puis l'affiche."""
        if self.etat == "choix_circuit":
            self.dessiner_choix_circuit()
            pygame.display.flip()
            return
        self.ecran.fill(COULEUR_HERBE)
        self.dessiner_piste()
        self.dessiner_voiture()
        self.dessiner_autre_voiture()
        self.dessiner_bandeau()
        if self.etat == "course" and not self.sur_la_piste:
            self.ecrire_au_centre("HORS PISTE", self.grande_police, COULEUR_VOITURE, HAUTEUR_FENETRE // 2 - 30)
        if self.etat == "course" and not self.sur_la_piste2:
            self.ecrire_au_centre("HORS PISTE", self.grande_police, COULEUR_VOITURE_2, HAUTEUR_FENETRE // 2 + 15)
        if self.etat == "accueil":
            self.dessiner_accueil()
        if self.etat == "fin":
            self.dessiner_fin()
        if self.etat == "course" and self.est_dans_ravitaillement:
            self.ecrire_au_centre("RAVITAILLEMENT EN COURS", self.grande_police, COULEUR_VOITURE, HAUTEUR_FENETRE // 2 - 30)
        if self.etat == "course" and self.est_dans_ravitaillement2:
            self.ecrire_au_centre("RAVITAILLEMENT EN COURS", self.grande_police, COULEUR_VOITURE_2, HAUTEUR_FENETRE // 2 +15 )
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
                    pygame.draw.circle(self.surface_detection, couleur, self.vers_ecran(x, y), int(demi_largeur * ECHELLE))
                # tracer du ravitaillement
                if self.circuit.nom == "rectangle":
                    centre = self.vers_ecran(54, 59)
                    pygame.draw.circle(self.ecran,(0, 230, 100),centre,int(10 * ECHELLE),2)
                    pygame.draw.circle(self.ecran, (0, 230, 100), centre, int(5 * ECHELLE))
                elif self.circuit.nom == "circuit_rond":
                    centre = self.vers_ecran(91, 166)
                    pygame.draw.circle(self.ecran, (0, 230, 100), centre, int(10 * ECHELLE), 2)
                    pygame.draw.circle(self.ecran, (0, 230, 100), centre, int(5 * ECHELLE))
                elif self.circuit.nom == "circuit_2":
                    centre = self.vers_ecran(312, 40)
                    pygame.draw.circle(self.ecran, (0, 230, 100), centre, int(10 * ECHELLE), 2)
                    pygame.draw.circle(self.ecran, (0, 230, 100), centre, int(5 * ECHELLE))
                elif self.circuit.nom == "circuit_3":
                    centre = self.vers_ecran(359, 217)
                    pygame.draw.circle(self.ecran, (0, 230, 100), centre, int(10 * ECHELLE), 2)
                    pygame.draw.circle(self.ecran, (0, 230, 100), centre, int(5 * ECHELLE))
                elif self.circuit.nom == "circuit_4":
                    centre = self.vers_ecran(242, 62)
                    pygame.draw.circle(self.ecran, (0, 230, 100), centre, int(10 * ECHELLE), 2)
                    pygame.draw.circle(self.ecran, (0, 230, 100), centre, int(5 * ECHELLE))


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

    def dessiner_autre_voiture(self):
        fraction = self.reserve_de_temps / DT if self.etat == "course" else 1.0

        coins = [
            self.vers_ecran(x, y)
            for x, y in self.voiture2.coins(fraction, AGRANDIR_VOITURE)
        ]

        pygame.draw.polygon(self.ecran, (30, 100, 220), coins)
        pygame.draw.line(self.ecran, COULEUR_BORD, coins[0], coins[1], 3)



    def dessiner_bandeau(self):
        """La bande du haut : tour, temps, vitesse."""
        pygame.draw.rect(self.ecran, COULEUR_BANDEAU, (0, 0, LARGEUR_FENETRE, HAUTEUR_BANDEAU))
        texte = ( f"Temps : {formater_temps(self.temps)} ")
        self.ecrire(texte, 20, 18, COULEUR_TEXTE)
        texte_bas = (f" Tour : {self.tour2} / {NOMBRE_DE_TOURS}   "
                     f" Vitesse : {self.voiture2.vitesse_kmh():.0f} km/h"
                     f"     Essence : {self.essence2:.0f} L                         ")
        self.ecrire_au_centre(texte_bas, self.police , (30, 100, 220), 48)

        texte_haut = (f" Tour : {self.tour} / {NOMBRE_DE_TOURS}   "
                      f" Vitesse : {self.voiture.vitesse_kmh():.0f} km/h"
                      f"     Essence : {self.essence:.0f} L                         ")
        self.ecrire_au_centre(texte_haut, self.police, COULEUR_VOITURE, 18)
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

    def dessiner_choix_circuit(self):

        self.ecran.fill(COULEUR_HERBE)
        self.ecrire("Choix du circuit : ", 15, 50, COULEUR_TEXTE, self.grande_police)
        nom = self.circuits_disponibles[self.circuit_selectionne]
        nom_affiche = nom.replace("_", " ").upper()
        self.ecrire(nom_affiche,450, 50, (255,220,0), self.grande_police)
        self.ecrire_au_centre("<  Fleche gauche / droite  >", self.police, COULEUR_TEXTE, HAUTEUR_FENETRE - 85)
        self.ecrire_au_centre("ENTREE pour valider", self.police, COULEUR_TEXTE, HAUTEUR_FENETRE - 50)
        points = CIRCUITS[nom]
        largeur_zone = LARGEUR_FENETRE - 160
        hauteur_zone = HAUTEUR_FENETRE - 260
        x_min = min(x for x, y in points)
        x_max = max(x for x, y in points)
        y_min = min(y for x, y in points)
        y_max = max(y for x, y in points)
        largeur_circuit = max(x_max - x_min, 1)
        hauteur_circuit = max(y_max - y_min, 1)

        # Mise en forme
        echelle = min(largeur_zone / largeur_circuit, hauteur_zone / hauteur_circuit)

        centre_x = LARGEUR_FENETRE / 2
        centre_y = HAUTEUR_FENETRE / 2
        points_ecran = []
        for x, y in points:
            px = centre_x + (x - (x_min + x_max) / 2) * echelle
            py = centre_y + (y - (y_min + y_max) / 2) * echelle
            points_ecran.append((int(px), int(py)))

        # Dessin de la piste
        pygame.draw.lines( self.ecran, COULEUR_BORD, True, points_ecran,24)
        pygame.draw.lines(self.ecran,(90, 90, 96),True,points_ecran,18)


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