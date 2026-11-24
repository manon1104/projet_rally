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
                      IMAGES_PAR_SECONDE, LARGEUR_FENETRE, LARGEUR_PISTE, NOMBRE_DE_TOURS, CAPACITE_RESERVOIRE, ALPHA,
                      CONSO, LONGUEUR_VOITURE, COULEUR_VOITURE_2, VITESSE_MAX_KMH, DIST_APPROCHE, MARGE_ESSENCE,
                      STATIONS, DIST_STATION)
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
        # Change en fonction du circuit sélectionné
        self.circuit_selectionne = (self.circuits_disponibles.index(CIRCUIT_CHOISI))
        self.en_marche = True
        # Initialisation du detecteur de surface (pour le dérapage, changement de mu)
        self.surface_detection = pygame.Surface(self.ecran.get_size())
        self.charger_circuit(self.circuits_disponibles[self.circuit_selectionne])
        self.nouvelle_partie()
        # Initialise au premier choix du joueur : s'il est seul ou s'ils sont deux
        self.etat = "choix_joueurs"
        # Change en fonction de si on veut jouer seul ou à deux
        self.nombre_joueurs = 1



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
        self.voiture = Voiture(self.circuit.x_depart, self.circuit.y_depart+3, self.circuit.angle_depart, self)
        # on rajoute une nouvelle voiture et on modifie la position de départ pour ne pas les superposer
        self.voiture2 = Voiture(self.circuit.x_depart,self.circuit.y_depart-3,self.circuit.angle_depart, self)
        # la ligne de départ n'est pas dans le même sens pour le circuit rond
        if self.circuit.nom == "circuit_rond":
            # Dans le circuit rond, la ligne de départ n'est pas au même endroit, on doit modifier x pour ne pas superposer les voitures
            self.voiture = Voiture(self.circuit.x_depart-3 , self.circuit.y_depart, self.circuit.angle_depart, self)
            self.voiture2 = Voiture(self.circuit.x_depart+3 , self.circuit.y_depart, self.circuit.angle_depart, self)

        self.etat = "accueil"
        self.temps = 0.0                  # temps de course, en secondes
        self.reserve_de_temps = 0.0       # voir « le pas de temps fixe » en haut du fichier
        self.sur_la_piste = True
        self.sur_la_piste2 = True

        #introduction de nouvelles variables qui permettent le compte de tours
        self.tour = 1
        self.tour2 = 1

        #introduction de variables qui permettent de noter le temps de chaque tour
        self.temps_tour_1 = 0.0
        self.temps_tour2_1 = 0.0
        self.temps_tour_2 = 0.0
        self.temps_tour2_2 = 0.0
        self.temps_tour_3 = 0.0
        self.temps_tour2_3 = 0.0

        #Initialisation des dernières positions valides (ie sur la piste)
        self.last_pos_valide = (self.circuit.x_depart, self.circuit.y_depart)
        self.last_pos_valide2 = (self.circuit.x_depart, self.circuit.y_depart)
        self.sortie = True
        self.sortie2 = True

        #intialisation de nouvelles variables qui permettent de rajouter du temps lors de sorties de piste
        self.temps_sortie = 0
        self.temps_sortie2 = 0
        self.penalite = [0,0,0]
        self.penalite2 = [0,0,0]
        self.penalite_tot = 0
        self.penalite_tot2 = 0

        # Initialisation d'une variable qui trouve la couleur de la piste sous les roues pour adapter le dérapage
        self.couleur_sous_roues = self.surface_detection.get_at((int(self.voiture.x),int(self.voiture.y)))[:3]
        self.couleur_sous_roues2 = self.surface_detection.get_at((int(self.voiture.x), int(self.voiture.y)))[:3]

        # Initialisation de la variable qui vérifie sur la voiture est dans la zone de ravitaillement
        self.est_dans_ravitaillement = False
        self.est_dans_ravitaillement2 = False

        # Initialisation de la distance initiale à l'objet (infinie car on cherche un obstacle pluq proche)
        self.distance_obstacle = float('inf')
        self.distance2_obstacle = float('inf')

        # Initialisation de variables qui gèrent la collision : on veut que les effets de la collision durent
        # un certain temps, donc on met un booléen qui vérifie qu'on est dans le premier instant de la collision,
        # puis on fait marcher cette collision pour x secondes, calculées grâce au temps de début de collision
        self.temps_debut_collision = 0
        self.collision_bool = False

        # Permet de gérer l'essence dans le cas de la voiture automatique
        self.arret_station2 = False
        self.station_servie2 = False
        self.essence_visee2 = 0

        # Modifie les paramètres du véhicule dans le cas où le joueur choisit une moto
        if self.voiture.choix == 'moto' :
            self.voiture.k = 75
            self.voiture_vitesse_max = 220
            self.voiture.reservoir = 45
            self.voiture.largeur = 0.8
            self.voiture.longueur = 3.5
        if self.voiture2.choix == 'moto' :
            self.voiture2.k = 75
            self.voiture2_vitesse_max = 220
            self.voiture2.reservoir = 45
            self.voiture2.largeur = 0.8
            self.voiture2.longueur = 3.5

        # Initialisation du reservoir d'essence
        self.essence = self.voiture.reservoir
        self.essence2 = self.voiture2.reservoir



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

    #Cette fonction permet de compter le nombre de tour effecutés par la voiture, et en combien de temps elle le fait
    def compter_tour(self):
        # La position dépend du circuit choisi
        if self.circuit.nom == "rectangle" or self.circuit.nom == "circuit_2" or self.circuit.nom == "circuit_4":
            # On vérifie que la voiture passe bien la ligne de départ en ayant pour ancienne position x antérieure à x_départ
            # On prend un temps > 5 pour que le compte de tour n'augmente pas au départ (5s de marge pour démarrer)
            if self.temps > 5 and self.voiture.x >= self.circuit.x_depart and self.voiture.ancien_x <= self.circuit.x_depart and abs((self.voiture.y - self.circuit.y_depart))<= self.circuit.largeur/2:
                if self.tour ==1:
                    # Prise en compte du temps de circuit 1
                    self.temps_tour_1 = self.temps
                elif self.tour ==2:
                    self.temps_tour_2 = self.temps - self.temps_tour_1
                elif self.tour ==3:
                    self.temps_tour_3 = self.temps - self.temps_tour_1- self.temps_tour_2
                # On ajoute un tour au nombre de tour total effectué
                self.tour += 1

                #Fictivement, lorsque la course est finie, on est à 4 tours : c'est notre condition d'arrêt
                if self.tour == (NOMBRE_DE_TOURS+1):
                    self.etat = 'fin'

        #On fait de même pour le circuit rond, mais en changeant le départ puisque la ligne est selon x
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

    #Fait de même pour la voiture 2
    def compter_tour2(self):
        # dépend du circuit choisi
        if self.circuit.nom == "rectangle" or self.circuit.nom == "circuit_2" or self.circuit.nom == "circuit_4":
            if self.temps > 5 and self.voiture2.x >= self.circuit.x_depart and self.voiture2.ancien_x <= self.circuit.x_depart and abs((self.voiture2.y - self.circuit.y_depart))<= self.circuit.largeur/2:
                if self.tour2 ==1:
                    self.temps_tour2_1 = self.temps
                elif self.tour2 ==2:
                    self.temps_tour2_2 = self.temps - self.temps_tour2_1
                elif self.tour2 ==3:
                    self.temps_tour2_3 = self.temps - self.temps_tour2_1- self.temps_tour2_2
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

    #Calcul de la dernière position valide pour pouvoir revenir sur la piste en cas de sortie
    def derniere_pos_valide(self):
        if self.sur_la_piste == True:
            self.last_pos_valide = (self.voiture.x, self.voiture.y)

    #De même pour la voiture 2
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
        """Fermeture de la fenêtre et touches Espace, R, Échap."""
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                self.en_marche = False
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    self.en_marche = False

                #On rajoute plusieurs étapes, la première étant de choisir le nombre de joueurs
                elif self.etat == "choix_joueurs":
                    if evenement.key == pygame.K_RIGHT:
                        self.nombre_joueurs = 2
                    elif evenement.key == pygame.K_LEFT:
                        self.nombre_joueurs = 1
                    elif evenement.key == pygame.K_RETURN:
                        self.etat = "choix_vehicule_j1"

                #On passe ensuite au choix du véhicule pour le joueur 1
                elif self.etat == "choix_vehicule_j1":
                    if evenement.key == pygame.K_RIGHT:
                        self.voiture.choix = "moto"
                    elif evenement.key == pygame.K_LEFT:
                        self.voiture.choix = "voiture"
                    elif evenement.key == pygame.K_RETURN:
                        self.etat = "choix_vehicule_j2" if self.nombre_joueurs == 2 else "choix_circuit"

                #S'il y a deux joueurs, on passe au choix du véhicule du joueur 2
                elif self.etat == "choix_vehicule_j2":
                    if evenement.key == pygame.K_RIGHT:
                        self.voiture2.choix = "moto"
                    elif evenement.key == pygame.K_LEFT:
                        self.voiture2.choix = "voiture"
                    elif evenement.key == pygame.K_RETURN:
                        self.etat = "choix_circuit"

                #On passe au choix du circuit
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
        braquage = 0.0
        braquage_max = math.radians(BRAQUAGE_MAX_DEGRES)

        #On ne peut commander la nouvelle voiture que si on a choisi de conduire deux joueurs
        if self.nombre_joueurs == 2 :
            if touches[pygame.K_z]:
                acceleration = ACCELERATION
            elif touches[pygame.K_s]:
                acceleration = -FREINAGE
            if  touches[pygame.K_q]:
                braquage = -braquage_max  # négatif : à gauche
            elif touches[pygame.K_d]:
                braquage = braquage_max  # positif : à droite

        return acceleration, braquage

    def consommation(self):
        return  ALPHA*self.voiture.vitesse*self.voiture.vitesse + CONSO

    def consommation2(self):
        return ALPHA * self.voiture2.vitesse * self.voiture2.vitesse + CONSO

    #Permet de conduire la voiture automatique : on choisit une stratégie qui faire suivre la piste centrale
    # à la voiture. Il faut donc calculer le point le plus proche dans les segments pour indiquer la direction à suivre
    def centre_plus_proche(self, x,y) :
        #initialisation à l'infini ; on ne peut être que plus proche
        meilleur = (float("inf"), 0, 0)

        for i, ((ax, ay), (bx, by)) in enumerate(self.circuit.segments):
            #(dx, dy) = vecteur AB
            dx, dy = bx - ax, by - ay
            #et sa norme
            longueur2 = dx * dx + dy * dy

            if longueur2 == 0:
                continue

            #trouve à quel point il faut avancer sur AB pour atteindre B
            t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / longueur2))

            #calcul de la distance à B
            d = math.hypot(x - (ax + t * dx), y - (ay + t * dy))
            if d < meilleur[0]:
                meilleur = (d, i, t)
        return meilleur

    def point_devant_sur_ligne(self, i, t, avance):
        segments = self.circuit.segments

        # On extrait le segment que l'on suit, ainsi que la longueur du segment
        (ax, ay), (bx, by) = segments[i]
        longueur = math.hypot(bx - ax, by - ay)

        # Position correspond à ce que l'on a déjà parcouru, reste ce qu'il nous faut encore parcourir
        position = longueur * t
        reste = longueur - position

        # On change de segment si besoin
        while avance > reste:
            avance -= reste
            # On passe au segment suivant en gérant le passage éventuel à un nouveau tour et on modifie nos valeurs
            i = (i + 1) % len(segments)
            (ax, ay), (bx, by) = segments[i]
            longueur = math.hypot(bx - ax, by - ay)
            position, reste = 0, longueur

        # Calcul de la distance entre la point de départ du segment et le point visé
        s = (position + avance) / max(longueur, 1e-9)

        # Renvoie les coordonnées du point visé
        return ax + s * (bx - ax), ay + s * (by - ay), i

    # Vérifie si la voiture automatique est dans la station
    def dans_station(self, voiture):
        station = STATIONS.get(self.circuit.nom)
        return (station is not None and abs(voiture.x - station[0]) <= 10 and abs(voiture.y - station[1]) <= 10)


    # Fonction qui gère la manière dont la voiture automatique s'arrête à la station essence
    def gerer_station(self, v_cible):
        station = STATIONS.get(self.circuit.nom)

        # S'il n'y a pas de station dans le circuit, pas de pb d'approvisionnement
        if station is None:
            return v_cible

        # Calcul de la distance entre la voiture et la station
        dist_st = math.hypot(station[0] - self.voiture2.x, station[1] - self.voiture2.y)

        # Vérifie si la voiture est bien derrière la station
        devant = ((station[0] - self.voiture2.x) * math.cos(self.voiture2.angle) + (station[1] - self.voiture2.y) * math.sin(self.voiture2.angle)) > 0

        #On s'éloigne de la station
        if dist_st > DIST_STATION:
            self.station_servie2 = False
            self.arret_station2 = False

        # Station dépassée sans s'être arrêtée
        if self.arret_station2 and not devant and not self.dans_station(self.voiture2):
            self.arret_station2 = False

        # Essence nécessaire pour terminer
        tours_restants = NOMBRE_DE_TOURS - self.tour2 + 1
        distance = tours_restants * self.circuit.longueur
        nb_pas = distance / (VITESSE_MAX_KMH * DT)
        besoin = MARGE_ESSENCE * nb_pas * (ALPHA * VITESSE_MAX_KMH ** 2 + CONSO)

        # Décision de s'arrêter : on n'est pas déjà arrêté, on est derrière, on n'est pas trop loin et le réservoir ne suffit pas pour finir la course
        if (not self.arret_station2 and not self.station_servie2 and dist_st < DIST_STATION and devant and self.essence2 < besoin):
            self.arret_station2 = True
            self.essence_visee2 = min(CAPACITE_RESERVOIRE, besoin)

        if not self.arret_station2:
            return v_cible

        # Arrêt dans la station : vitesse nulle tant que le réservoir n'est pas rempli comme on le souahit
        if self.dans_station(self.voiture2):
            if self.essence2 >= self.essence_visee2:
                self.arret_station2 = False
                self.station_servie2 = True
                return v_cible
            return 0

        # Ralentissement à l'approche : vitesse proportionnelle à la distance restante (sinon on dépasse la station)
        MARGE_ARRET = 5
        dist_restante = max(0.0, dist_st - MARGE_ARRET)
        v_freinage = VITESSE_MAX_KMH * dist_restante / DIST_STATION

        if self.voiture2.vitesse > v_freinage + 1:
            self.voiture2.vitesse = v_freinage + 1

        return min(v_cible, v_freinage)

    # Calcul de à quel point l'angle à venir est grand
    def courbure_devant(self, i, t, d1=20, d2=60):
        x0, y0, _ = self.point_devant_sur_ligne(i, t, 0)
        x1, y1, _ = self.point_devant_sur_ligne(i, t, d1)
        x2, y2, _ = self.point_devant_sur_ligne(i, t, d2)

        # Calcul des angles devant
        a1 = math.atan2(y1 - y0, x1 - x0)
        a2 = math.atan2(y2 - y1, x2 - x1)

        # On calcule l'angle entre les deux segments (modulo pour que atan soit dans le bon intervalle)
        return abs(math.atan2(math.sin(a2 - a1), math.cos(a2 - a1)))

    def pilote_auto(self, voiture, essence, tour):
        d, i, t = self.centre_plus_proche(voiture.x, voiture.y)
        station = STATIONS.get(self.circuit.nom)
        v_station = self.gerer_station(VITESSE_MAX_KMH)

        avance = max(15, min(60, 0.8 * voiture.vitesse + 2 * d))
        cx, cy, _ = self.point_devant_sur_ligne(i, t, avance)

        if self.arret_station2 and station is not None:
            dist_st = math.hypot(station[0] - voiture.x, station[1] - voiture.y)
            if dist_st < 50:  # on ne quitte la ligne que pour les derniers mètres
                cx, cy = station

        # --- Erreur de cap ---
        erreur = math.atan2(cy - voiture.y, cx - voiture.x) - voiture.angle
        erreur = math.atan2(math.sin(erreur), math.cos(erreur))

        # --- Braquage : gain modéré, limité selon la vitesse ---
        braquage_max = math.radians(BRAQUAGE_MAX_DEGRES)
        facteur = 1 / (1 + (voiture.vitesse / (0.8 * VITESSE_MAX_KMH)) ** 2)
        braquage_max *= max(0.6, facteur)
        braquage_voulu = max(-braquage_max, min(braquage_max, 2 * erreur))

        # --- Lissage : le braquage ne peut pas changer brusquement ---
        prec = getattr(self, "braquage_prec", 0.0)
        pas = 0.15 * math.radians(BRAQUAGE_MAX_DEGRES)  # variation max par appel
        braquage = max(prec - pas, min(prec + pas, braquage_voulu))
        self.braquage_prec = braquage

        # --- Vitesse ---
        v_cible = 0.5 * VITESSE_MAX_KMH
        courbure = self.courbure_devant(i, t, d1=20, d2=60)
        v_cible *= max(0.2, 1 - 3 * courbure)

        if d > 6:  # loin de la ligne
            v_cible = min(v_cible, VITESSE_MAX_KMH / 3)

        if abs(braquage) > 0.6 * braquage_max:  # gros braquage -> on freine
            v_cible = min(v_cible, 0.25 * VITESSE_MAX_KMH)

        v_cible = min(v_cible, v_station)

        if v_cible == 0 and voiture.vitesse <= 2:
            voiture.vitesse = 0
            acceleration = 0.0
        elif voiture.vitesse < v_cible:
            acceleration = ACCELERATION
        elif voiture.vitesse > v_cible + 0.5:
            acceleration = -FREINAGE
        else:
            acceleration = 0.0

        return acceleration, braquage


    # La fonction faire_un_pas gere les voitures 1 et 2 en même temps.
    # Il aurait surement été plus judicieux de coder une fonction faire_un_pas_2 pour gérer la voiture 2 mais
    # je n'y ai pensé qu'après et ce programme fonctionnant quand même, je l'ai gardé

    def faire_un_pas(self):
        """Un pas de simulation de DT secondes."""
        # 1) Lire les commandes
        # joueur 1
        # voiture 1 : toujours le joueur
        acceleration, braquage = self.lire_commandes_clavier()

        # La vitesse est soit décidée par le pilote auto, dans le cas où il n'y a qu'un joueur, soit par les flèches s'il y a deux joueurs
        if self.nombre_joueurs == 2 :
            acceleration2, braquage2 = self.lire_commandes_deuxieme_voiture()
        else:
            acceleration2, braquage2 = self.pilote_auto(self.voiture2, self.essence2, self.tour2)

        dx = self.voiture2.x - self.voiture.x
        dy = self.voiture2.y - self.voiture.y

        # Début de la modélisation de la collision : calcul de la distance entre les voitures et de laquelle est devant
        distance_longitudinale = (dx * math.cos(self.voiture.angle) + dy * math.sin(self.voiture.angle))
        distance_voitures = math.sqrt((self.voiture.x - self.voiture2.x) ** 2 + (self.voiture.y - self.voiture2.y) ** 2)
        puissance_collision = 2

        # 2) Mettre à jour la position
        # Dans le cas normal, pas de collision
        if distance_voitures > self.voiture.longueur and self.collision_bool == False:
            self.voiture.avancer(acceleration, braquage, DT)
            self.voiture2.avancer(acceleration2, braquage2, DT)

        # Dans le cas où il y a collision, le booléen fait en sortie qu'on sache que c'est le début de la collision
        elif self.collision_bool == False :
            self.temps_debut_collision = self.temps
            self.collision_bool = True

            # On diminue alors la vitesse des deux voitures
            self.voiture.vitesse *= 0.7
            self.voiture2.vitesse *= 0.7

            # On fait en sorte que les voitures "rebondissent" l'une sur l'autre, l'une vers l'avant, l'autre vers l'arrière
            if distance_longitudinale > 0 :
                self.voiture.vitesse = -self.voiture.vitesse
            else :
                self.voiture2.vitesse = -self.voiture2.vitesse

        # On continue la collsion : on fait rebomdirent les voitures
        elif self.collision_bool == True :
            if distance_longitudinale > 0 :
                self.voiture.x -= puissance_collision*math.cos(self.voiture.angle)
                self.voiture.y -= puissance_collision*math.sin(self.voiture.angle)
                self.voiture2.x += puissance_collision*math.cos(self.voiture2.angle)
                self.voiture2.y += puissance_collision*math.sin(self.voiture2.angle)
            else :
                self.voiture.x += puissance_collision*math.cos(self.voiture.angle)
                self.voiture.y += puissance_collision*math.sin(self.voiture.angle)
                self.voiture2.x -= puissance_collision*math.cos(self.voiture2.angle)
                self.voiture2.y -= puissance_collision*math.sin(self.voiture2.angle)

        # La collision dure 0.4s, après quoi les voitures peuvent repartir normalement, on inverse à nouveau les vitesses
        if self.temps - self.temps_debut_collision > 0.4 and self.collision_bool == True:
            if distance_longitudinale > 0 :
                self.voiture.vitesse = -self.voiture.vitesse
            else :
                self.voiture2.vitesse = -self.voiture2.vitesse
            self.collision_bool = False

        self.temps = self.temps + DT

        # on remet le ravitaillement à faux
        self.est_dans_ravitaillement = False
        self.est_dans_ravitaillement2 = False

        # 3) Voiture 1 sur la piste ?
        self.sur_la_piste = self.circuit.est_sur_la_piste(self.voiture.x, self.voiture.y)

        # À FAIRE (partie 1) — sortie de piste.
        #   Pour l'instant, on affiche seulement « HORS PISTE ». Le sujet demande :
        #   vitesse réduite, retour au dernier point valide, pénalité de temps.
        #   Idée : à chaque pas où la voiture est sur la piste, mémoriser sa position.

        # On vérifie la condition que l'on n'est pas sur la piste et on diminue alors la vitesse
        if self.sur_la_piste == False:
            self.voiture.vitesse = self.voiture.vitesse/1.1

            # Pour n'ajouter qu'une fois la pénalité, on crée un booléen qui ne change pas tant qu'on est hors de piste
            if self.sortie == True:
                self.temps_sortie = self.temps
                self.penalite_tot = self.penalite_tot + 1
                self.sortie = False

                # On compte les pénalités par tour
                if self.tour == 1:
                    self.penalite[0] += 1
                elif self.tour == 2:
                    self.penalite[1] += 1
                elif self.tour == 3:
                    self.penalite[2] += 1
            elif (self.temps - self.temps_sortie) > 1:
                #On se remet sur la dernière position valide
                centre, angle = self.centre_piste_proche(self.last_pos_valide[0],self.last_pos_valide[1])

                if centre is not None:
                    self.voiture.x = centre[0]
                    self.voiture.y = centre[1]
                    self.voiture.angle = angle

                # On remet la booléen à True
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

        if self.est_dans_ravitaillement == True and self.essence <= self.voiture.reservoir :
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

        if self.est_dans_ravitaillement2 == True and self.essence2 <= self.voiture2.reservoir:
            self.essence2 = self.essence2 + 0.5

        largeur, hauteur = self.surface_detection.get_size()
        x, y = self.vers_ecran(self.voiture.x, self.voiture.y)
        if 0 <= x < largeur and 0 <= y < hauteur:
            self.couleur_sous_roues = self.surface_detection.get_at((int(x), int(y)))[:3]
        else:
            self.couleur_sous_roues = None

        # Mise en place du radar
        # On place l'obstacle au plus loin pour qu'un autre objet soit plus proche
        self.distance_obstacle = float('inf')

        # On fait des lignes de 50
        for i in range(51) :
            # On en fait 5 sur 120 degrés
            for j in [-60, -30, 0, 30, 60] :
                angle = math.radians(j) + self.voiture.angle
                x = self.voiture.x + i*math.sin(angle)
                y = self.voiture.y + i*math.cos(angle)
                distance_radar = math.sqrt((x - self.voiture2.x) ** 2 + (y - self.voiture2.y) ** 2)

                # On calcule la distance à la piste (et on update l'obstacle le plus proche s'il est plus proche)
                if not self.circuit.est_sur_la_piste(x,y) :
                    if self.distance_obstacle > i :
                        self.distance_obstacle = i

                # On calcule la distance à la voiture 2
                if distance_radar < LONGUEUR_VOITURE/2:
                    if self.distance_obstacle < i :
                        self.distance_obstacle = i

        # On fait de même pour la voiture 2
        self.distance2_obstacle = float('inf')
        for i in range(51):
            for j in [-60, -30, 0, 30, 60]:
                angle = math.radians(j) + self.voiture2.angle
                x = self.voiture2.x + i * math.sin(angle)
                y = self.voiture2.y + i * math.cos(angle)
                distance_radar = math.sqrt((x - self.voiture.x) ** 2 + (y - self.voiture.y) ** 2)

                if not self.circuit.est_sur_la_piste(x, y):
                    if self.distance2_obstacle > i:
                        self.distance2_obstacle = i

                if distance_radar < LONGUEUR_VOITURE / 2:
                    if self.distance2_obstacle < i:
                        self.distance2_obstacle = i


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
        # On dessine le choix des joueurs en fonction de l'état
        if self.etat == "choix_joueurs":
            self.dessiner_choix_joueurs()
            pygame.display.flip()
            return

        # On dessine aussi le choix du circuit en fonction de l'état
        if self.etat == "choix_circuit":
            self.dessiner_choix_circuit()
            pygame.display.flip()
            return

        # De même pour les choix des véhicules
        if self.etat == "choix_vehicule_j1" :
            self.dessiner_choix_vehicule_j1()
            pygame.display.flip()
            return
        if self.etat == "choix_vehicule_j2" :
            self.dessiner_choix_vehicule_j2()
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
        pygame.display.flip()

    # Dessin du choix du véhicule, fonctions sur le même modèle que le choix du circuit
    def dessiner_choix_vehicule(self, numero, choix):

        self.ecran.fill(COULEUR_HERBE)
        self.ecrire_au_centre("RALLY BREIZH FURIOUS", self.grande_police, COULEUR_TEXTE, 150)
        self.ecrire_au_centre(f"Joueur {numero} : choisissez votre véhicule",
                              self.police, COULEUR_TEXTE, 250)

        # Option voiture
        couleur1 = (255, 220, 0) if choix == "voiture" else COULEUR_TEXTE
        self.ecrire_au_centre("VOITURE", self.grande_police, couleur1, 330)

        # Option moto
        couleur2 = (255, 220, 0) if choix == "moto" else COULEUR_TEXTE
        self.ecrire_au_centre("MOTO", self.grande_police, couleur2, 400)

        self.ecrire_au_centre("<  Fleches gauche / droite  >", self.police, COULEUR_TEXTE, 490)
        self.ecrire_au_centre("ENTREE pour valider", self.police, COULEUR_ALERTE, 530)

    def dessiner_choix_vehicule_j1(self):
        self.dessiner_choix_vehicule(1, self.voiture.choix)

    def dessiner_choix_vehicule_j2(self):
        self.dessiner_choix_vehicule(2, self.voiture2.choix)

    # Sur le même modèle que le choix du circuit
    def dessiner_choix_joueurs(self):

        self.ecran.fill(COULEUR_HERBE)
        self.ecrire_au_centre("RALLY BREIZH FURIOUS",self.grande_police,COULEUR_TEXTE,150)
        self.ecrire_au_centre("Choisissez le nombre de joueurs",self.police,COULEUR_TEXTE,250)

        # Option 1 joueur
        couleur1 = (255, 220, 0) if self.nombre_joueurs == 1 else COULEUR_TEXTE

        self.ecrire_au_centre("1 JOUEUR",self.grande_police,couleur1,330)

        # Option 2 joueurs
        couleur2 = (255, 220, 0) if self.nombre_joueurs == 2 else COULEUR_TEXTE

        self.ecrire_au_centre("2 JOUEURS",self.grande_police,couleur2,400)
        self.ecrire_au_centre("<  Fleches gauche / droite  >",self.police,COULEUR_TEXTE,490)
        self.ecrire_au_centre("ENTREE pour valider",self.police,COULEUR_ALERTE,530)


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
                    pygame.draw.polygon(self.surface_detection, couleur, rectangle)
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

    def dessiner_autre_voiture(self) :
        fraction = self.reserve_de_temps / DT if self.etat == "course" else 1.0
        coins = [self.vers_ecran(x, y) for x, y in self.voiture2.coins(fraction, AGRANDIR_VOITURE)]
        pygame.draw.polygon(self.ecran, (30, 100, 220), coins)
        pygame.draw.line(self.ecran, COULEUR_BORD, coins[0], coins[1], 3)

    def dessiner_bandeau(self):
        """La bande du haut : tour, temps, vitesse."""
        pygame.draw.rect(self.ecran, COULEUR_BANDEAU, (0, 0, LARGEUR_FENETRE, HAUTEUR_BANDEAU))
        texte = ( f"Temps : {formater_temps(self.temps)} ")
        self.ecrire(texte, 20, 18, COULEUR_TEXTE)
        texte_bas = (f" Tour : {self.tour2} / {NOMBRE_DE_TOURS}   "
                     f" Vitesse : {self.voiture2.vitesse_kmh():.0f} km/h"
                     f"     Essence : {self.essence2:.0f} L                         "
                     f" Distance obstacle : {self.distance_obstacle:.0f} m")
        self.ecrire_au_centre(texte_bas, self.police , (30, 100, 220), 48)

        texte_haut = (
            f" Tour : {self.tour} / {NOMBRE_DE_TOURS}   "
            f" Vitesse : {self.voiture.vitesse_kmh():.0f} km/h"
            f"     Essence : {self.essence:.0f} L"
            f"     Distance obstacle : {self.distance2_obstacle:.0f} m")
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