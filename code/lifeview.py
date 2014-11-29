#/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Blarg version 1.0

    La page du jeu sur indieDB : http://www.indiedb.com/games/blarg
    Liens vers d'autres jeux sur mon blog : http://recher.wordpress.com/jeux
    Mon twitter : http://twitter.com/_Recher_

    Ce superbe jeu, son code source, ses images, et son euh... contenu sonore est disponible,
    au choix, sous la licence Art Libre ou la licence CC-BY-SA

    Copyright 2010 Réchèr
    Copyleft : cette oeuvre est libre, vous pouvez la redistribuer et/ou la modifier selon les
    termes de la Licence Art Libre. Vous trouverez un exemplaire de cette Licence sur le site
    Copyleft Attitude http://www.artlibre.org ainsi que sur d'autres sites.

    Creative Commons - Paternité - Partage des Conditions Initiales à l'Identique 2.0 France
    http://creativecommons.org/licenses/by-sa/2.0/fr/deed.fr

date de la dernière relecture-commentage : 01/10/2010

la classe pour gérer l'affichage des points de vie. ( = les vestes en jean)

Dans tout ce module de code, "veste en jean" et "life point", ça désigne ezguegtement la même choz

Lorsque le joueur perd un point de vie, on supprime pas tout de suite
la veste en jean correspondante. On la fait clignoter un peu. C'est classe.

 --- comment c'est foutu, la gestion du clignotement quand on perd un point de vie ? ---
J'ai fait un clignotement, mais qui diminue de manière randomisatoire.
donc y'a deux curseurs.
le blinkCounter et le blinkRandomCursor.

A chaque cycle :

  si le blinkRandomCursor > blinkCounter, la veste est affiché, sinon , elle ne l'est pas.

  variation du blinkCounter : il diminue de 1 en 1, à partir de 50, jusqu'à 0

  variation du blinkRandomCursor : il varie en random de 0 à 50, mais avec une inertie.
  on utilise une autre variable : blinkRandomEnd. random total de 0 à 50
    - blinkRandomCursor tente d'atteindre blinkRandomEnd, en augmentant/diminuant de 5
    - lorsque blinkRandomCursor = blinkRandomEnd, on recalcule blinkRandomEnd,
      toujours en total random de 0 à 50
  pour que ça tombe juste, le blinkRandomEnd et le blinkRandomCursor sont tout le temps
  des multiples de 5. A tout moment. En fait il y a une "RandomGrid", représentant
  le domaine de valeurs autorisé pour blinkRandomCursor et blinkRandomEnd.
  Ce domaine de valeur est : 0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50 (ou pas 50, osef)
"""

import pygame

from common import pyRect, HERO_LIFE_POINT_INITIAL, NONE_COUNT, randRange

#liste des identifiants d'images. Youpi
(imgVeste,
) = range(1)

#correspondance identifiant d'image -> nom du fichier.
LIST_VESTEJEAN_IMG_FILENAME = (
 (imgVeste, "vestjean"),
)

#les points de vie sont réparties en 2 colonnes quinquoncées (hahaha)
#abscisse de la première colonne (quinquoncées (hahaha))
VESTE_X1 = 23
#abscisse de la deuxième colonne (nan je répète pas)
VESTE_X2 = 13
#ordonnay du haut de la colonne
VESTE_Y_START = 30
#distance Y entre chaque veste
VESTE_Y_ADD = 20

#nombre maximal de veste en jean affiché. J'ai prévu un peu de marge par rapport
#au nombre de point de vie réel, si jamais je rajoute un truc, un bonus ou autre
NBR_MAX_VESTE = 5

#coordonnées X des vestes. Ca fait (X1, X2, X1, X2, X1, ...)
listeCoordX = ((VESTE_X1, VESTE_X2) * NBR_MAX_VESTE)[:NBR_MAX_VESTE]

#coordonnée Y des vestes. une liste qui s'incrémente, tout simplement
listeCoordY = tuple( [ VESTE_Y_START + iVeste * VESTE_Y_ADD
                       for iVeste in range(NBR_MAX_VESTE) ])

#coordonnée X, Y des vestes
listeCoord = zip(listeCoordX, listeCoordY)

#liste de Rect, contenant les coordonnées des vestes en jean.
#C'est dans l'ordre dans lequel on vire les points de vie :
#les derniers éléments (donc ceux du bas) sont virés en premier)
LIST_COORD_VESTEJEAN = tuple( [ pyRect(coord[0], coord[1])
                                for coord in listeCoord
                              ])

# --- config du clignotement d'une veste quand on perd un point de vie ---

#valeur initiale du blinkCounter
BLINK_COUNTER_INIT = 50
#pas de décrémentation de blinkCounter
BLINK_COUNTER_STEP = 1
#pas de déplacement (incr ou decr) de blinkRandomCursor
BLINK_RANDOM_STEP = 5
#grille de random, utilisé pour recalculer le blinkRandomEnd
#(car il faut qu'il soit un multiple de 5, donc on prend un random sur la grid,
#puis on le multiplie par le Random Step)
BLINK_RANDOM_GRID = BLINK_COUNTER_INIT / BLINK_RANDOM_STEP

class LifePointViewer():
    """
    ktefne ktefene
    """

    def __init__(self, dicLifePointViewerImg):
        """
        constructeur. (thx captain obvious)

        entrée :
            dicLifePointViewerImg : dictionnaire de correspondance
                entre les identifiants d'image des vestes en jean, et les
                images elle-même. Même si ça sert à rien parce que y'a
                qu'une seule image. Youpi !!!
        """

        self.dicLifePointViewerImg = dicLifePointViewerImg

        #groupe de sprite contenalt les life point qui doivent être affichés à l'instant T
        #Le life point en cours de clignotement, si il y en a un, n'arrête pas de
        #s'enlever et se retirer de ce groupe.
        #(j'aime bien l'expression "l'instant T", ça fait vraiment prof ridicule.
        #le truc encore plus ridicule c'est de dire "à la date T=0".)
        self.groupLifePoints = pygame.sprite.RenderUpdates()

        #liste des sprites de life point affichés.
        #La liste contient aussi le sprite en cours de clignotement.
        self.listLifePoints = []

        #nombre de life point affiché actuellement
        self.lifePointViewed = HERO_LIFE_POINT_INITIAL

        #nombre de life point à virer en clignotement.
        #(on peut les faire clignoter que un par un, donc si le joueur perd plein de
        #vie très rapidement, faut stocker en souvenir tout ceux qu'il faut virer,
        self.lifePointToRemove = 0

        #blinkCounter. (voir plus haut). Quand il vaut NONE_COUNT, aucun life point
        #n'est en cours de clignotement.
        self.blinkCounter = NONE_COUNT

        #indique si le life point en cours de clignotement est affiché ou pas.
        #ne sert à rien si y'a pas de life point en cours de clignotement
        self.blinkLifeVisible = True

        #création des sprites, positionnement, image, ajout dans
        #le groupe groupLifePoints, et dans la liste listLifePoints
        for i in xrange(self.lifePointViewed):

            #création, et définition de l'image utilisée
            sprLifePoint = pygame.sprite.Sprite()
            sprLifePoint.image = self.dicLifePointViewerImg[imgVeste]

            #placement du sprite dans l'écran, en utilisant le super quinquonçage
            #précédemment calculé.
            sprLifePoint.rect = pygame.rect.Rect(LIST_COORD_VESTEJEAN[i])

            #ajout dans le groupe (car au début, on les affiche tous), et dans la liste.
            self.groupLifePoints.add(sprLifePoint)
            self.listLifePoints.append(sprLifePoint)


    def takeStimuliHurt(self):
        """
        Fonctions de prise en compte des stimulis envoyé par le code extérieur.
        (Plus exactement la classe Hero)

        Cette fonction est appelée par le code extérieur quand le héros se prend un magicien
        dans la gueule, et qu'il perd un point de vie.
        """

        #on se contente d'enregistrer qu'il faut virer un point de vie de plus.
        #on s'en occuperaaprès, quand ce sera le moment (clignotement, tout ça tout ça)
        if len(self.listLifePoints) > 0:
            self.lifePointToRemove += 1


    def determineIsUpdatingSthg(self):
        """
        Permet d'indiquer au code extérieur que quelque chose a bougé dans l'affichage,
        et qu'il faudrait voir à réactualiser les life point dans l'écran principal.

        Il y a un update à partir du moment où un life point est en cours de clignotement.
        C'est un peu "mal dégrossi", on pourrait dire que y'a update que quand le life point
        vient d'apparaître ou de disparaître. Ca ferait moins de réaffichage inutile.
        Mais osef.

        plat-dessert : booléen. True : faut réactualiser. False : faut pas
        """

        #update si y'a des life point en stock à faire clignoter pour plus tard.
        #ou si y'a un life point en cours de clignotement.
        updatingConditions = (self.lifePointToRemove > 0,
                              self.blinkCounter is not NONE_COUNT)

        #any : renvoie True si y'a au moins un True dans la liste.
        isUpdatingSthg = any(updatingConditions)
        return isUpdatingSthg


    def calculateRandomGridValue(self):
        """
        recalcule le BlinkRandomEnd (et la valeur initiale de blinkRandomCurrent)
        Il faut une valeur random entre 0 et BLINK_COUNTER_INIT, mais qui soit
        un multiple de BLINK_RANDOM_STEP.
        Dans la config actuelle c'est entre 0 et 50, par multiple de 5.
        Donc random( 0 à 10 ) * 5. Oui bon ça va on a compris !!!

        plat-dessert :
             int. valeur du random
        """
        return randRange(BLINK_RANDOM_GRID) * BLINK_RANDOM_STEP


    def update(self):
        """
        grosse fonction qui fait clignoter le life point, quand c'est le moment,
        et qui vire définitivement les life point lorsque le clignoting est fini.
        """

        # --- ajout d'un life point en cours de clignotage ---

        #cet ajout est fait si il faut virer au moins un life point, et si y'a
        #pas d'autres life point en cours de clignotage.
        if self.lifePointToRemove > 0 and self.blinkCounter is NONE_COUNT:

            #hop, c'est pris en compte, donc un life point de moins à virer.
            self.lifePointToRemove -= 1

            #on vérifie quand même qu'il reste au moins un life point d'affiché dans la liste.
            #sinon on peut rien faire clignoter.
            #Normalement, ça arrive jamais de demander à virer plus de life point que ce
            #qu'il y en a. Mais une petite sécurité, c'est pas du luxe.
            if len(self.listLifePoints) > 0:

                #on crée une référence sur le sprite en cours de clignotement
                #(on le prend à la fin de la lite)
                self.sprLifePointBlinking = self.listLifePoints[-1]
                #init du blinkCounter
                self.blinkCounter = BLINK_COUNTER_INIT

                #init des blinkRandom. On leur donne une valeur quelconque, on s'en fout.
                #mais faut quand même qu'ils restent dans leur domaine de valeur autorisé,
                #c'est à dire la RandomGrid
                self.blinkRandomEnd = self.calculateRandomGridValue()
                self.blinkRandomCursor = self.calculateRandomGridValue()

        # --- faisage clignoter le life point qui, si il y en a un ---

        if self.blinkCounter is not NONE_COUNT:

            # - affichage ou pas du life point -
            #on détermine si le life point doit être affiché ou pas, dans la situation actuelle
            blinkLifeMustBeVisible = self.blinkCounter > self.blinkRandomCursor

            #si le life point doit être affiché alors qu'il ne l'est pas,
            #il faut l'ajouter au groupe de sprite self.groupLifePoints
            if blinkLifeMustBeVisible and not self.blinkLifeVisible:
                self.groupLifePoints.add(self.sprLifePointBlinking)
                self.blinkLifeVisible = True

            #si le life point ne doit pas être affiché alors qu'il l'est,
            #il faut le virer du groupe de sprite self.groupLifePoints
            if not blinkLifeMustBeVisible and self.blinkLifeVisible:
                self.groupLifePoints.remove(self.sprLifePointBlinking)
                self.blinkLifeVisible = False

            # - évolution du blinkCounter. -
            #C'est pas dur, il diminue en continue
            self.blinkCounter -= BLINK_COUNTER_STEP

            # - évolution du blinkRandom. -

            #on rapproche blinkRandomCursor de blinkRandomEnd, d'un pas (pas = BLINK_RANDOM_STEP)
            if self.blinkRandomCursor > self.blinkRandomEnd:
                self.blinkRandomCursor -= BLINK_RANDOM_STEP
            elif self.blinkRandomCursor < self.blinkRandomEnd:
                self.blinkRandomCursor += BLINK_RANDOM_STEP

            #si les deux se sont rejoints, on recalcule blinkRandomEnd,
            #pour refaire varier le blinkRandomCursor au cycle prochain.
            #si blinkRandomEnd retombe pil poil sur blinkRandomCursor, c'est pas grave.
            #il sera re-re-calculé au prochain cycle.
            if self.blinkRandomCursor == self.blinkRandomEnd:
                self.blinkRandomEnd = self.calculateRandomGridValue()

            # --- supression du life point si il a arrêté de clignoter ---

            if self.blinkCounter == 0:

                #on arrête le clignotement en cours.
                self.blinkCounter = NONE_COUNT

                #enlevage final du life point du groupe de sprite.
                #(le remove ne fait rien, mais ne plante pas, si le life point était déjà
                #viré avant)
                self.groupLifePoints.remove(self.sprLifePointBlinking)

                #suppression finale du life point de la liste. pop !!!
                #(le pop sans paramètre vire ledernier élément)
                self.listLifePoints.pop()

                #réinitialisation du booléen indiquant si le life point en cours de clignotement
                #est affiché, ou pas.
                #(En fait, là il s'agira du prochain life point qu'on fera clignoter.
                #et au départ, ce prochain life point est initalement affiché. Héhé)
                self.blinkLifeVisible = True

