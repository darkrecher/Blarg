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

date de la dernière relecture-commentage : 29/09/2010

classe qui génère les coordonnées des patterns de magiciens

vocabulaire :

semi-amplitude de random sur une variable X : valeur entière.
la variable X a une valeur de départ, et on la modifie un peu au hasard, pour le fun.
X peut être modifié dans l'intervalle suivant : [ X - semi-amplitude , X + semi-amplitude ]

amplitude de random négative sur une variable X. valeur entière.
comme la semii-amplitude, mais X est modifié dans l'intervalle suivant : [ X - amplitude, X ]

amplitude de random positive : blabla [ X, X + amplitude ]

Pour tous les patterns, on s'autorise à placer les magiciens en dehors de l'écran si ils sont
trop à droite ou trop en bas. (Ca donne l'impression qu'ils arrivent de plus loin, et c'est cool)
Mais on les place pas trop en haut ou trop à gauche. Sinon ça rentre dans le mur du haut, ou
dans les éléments du menu. Et ça ferait tout pourri.

TRODO : c'est pas clair entre ce qui est randomisé sur place (décalage, point de départ du cercle,
et ce qui est randomisé ailleurs (isClockWise, etc.)
Faudra régler ça quand on aura un peu plus de "matière". Hahahahah aaaa !!!!!! fuck.
Ou alors faut pas le régler du tout, on laisse comme ça et on s'en fout.
"""

import math  #yeaaahh !!! cosinus et sinus FTW !!
import pygame

from common import (GAME_RECT, pyRect, centeredRandom, randRange, randBoole,
                    SHIFT_PREC, NOT_FLOATING_PREC)

from magician import MAGICIAN_SIZE

# --- noms de tous les patterns existants

(PAT_RAND,                       #placement des magiciens au hasard
 PAT_CIRCLE,                     #un cercle de magicien autour du héros
 PAT_DIAG,                       #les 4 diagonales de magiciens autour du héros
 PAT_LINE_VERTIC_TO_LEFT,        #ligne verticale, magiciens allant de droite à gauche
 PAT_LINE_VERTIC_TO_RIGHT,       #ligne verticale, dans l'autre sens
 PAT_LINE_HORIZ_TO_UP,           #ligne horizontale, magicien allant de bas en haut
 PAT_LINE_HORIZ_TO_DOWN,         #bla
 PAT_LINE_SWAP_VERTIC_TO_LEFT,   #ligne verticale de droite à gauche,
                                 #mais les magiciens du haut vont en bas, et vice-et-versaaaaa
 PAT_LINE_SWAP_VERTIC_TO_RIGHT,  #pareil, mais de gauche à droite
 PAT_LINE_SWAP_HORIZ_TO_UP,      #ligne horizontale de bas en haut, mais les magiciens de droite
                                 #vont à gauche, et lycée-de-versailles (jeu de mot nul, merci)
 PAT_LINE_SWAP_HORIZ_TO_DOWN,    #bla
) = range(11)

# --- définition de trucs pour les patterns de LINE VERTIC.

#dans un pattern de ligne vertical, on donne une coordonnée X, qui sera la même pour tous
#les magiciens. Cette coordonnée X sera un peu randomizée, pour le fun.
#on ne donne pas de coordonnées Y pour le pattern, juste le nombre de magiciens.
#les magiciens seront placés de façon à prendre toute la hauteur de l'aire de jeu.
#mais on randomisera un peu le Y du premier magicien de la ligne, et l'écart Y
#entre chaque magicien.


#semi-amplitude du random sur la coordonnée X du pattern.
PTN_VERTIC_X_RAND_SEMI_AMPL = 10
#amplitude (positive) du random sur la position Y du premier magicien du pattern
PTN_VERTIC_Y_RAND_AMPL_START = 15
#amplitude (négative) du random sur la taille Y de la ligne verticale
#sur laquelle se répartiront les magiciens.
PTN_VERTIC_Y_RAND_AMPL_SIZE = 15

#A cause de cette randomisation, et de la taille des magiciens, il faut prévoir
#une marge de sécurité. on ne place pas les magiciens sur toute la hauteur de l'aire de jeu.
#il faut donc enlever la hauteur du magicien, et le décalage maximum du random sur
#la coordonnée Y du premier magicien.
#on ne retire pas PTN_VERTIC_Y_RAND_AMPL_SIZE. Car cette amplitude de random est négative
#(elle est retirée à l'écartement de base entre les magiciens. En fait ça ajoute de la marge)
LENGTH_TO_REMOVE = PTN_VERTIC_Y_RAND_AMPL_START + MAGICIAN_SIZE.height
PTN_VERTIC_HEIGHT = GAME_RECT.height - LENGTH_TO_REMOVE

# --- définition de trucs pour les patterns de LINE HORIZ.

#blabla, voir LINE VERTIC

#semi-amplitude du random sur la coordonnée Y du pattern.
PTN_HORIZ_Y_RAND_SEMI_AMPL = 10
#amplitude (positive) du random sur la position X du premier magicien du pattern
PTN_HORIZ_X_RAND_AMPL_START = 20
#amplitude (négative) du random sur la taille X de la ligne horizontale
#sur laquelle se répartiront les magiciens.
PTN_HORIZ_X_RAND_AMPL_SIZE = 20

#blabla pareil que VERTIC
LENGTH_TO_REMOVE = PTN_HORIZ_X_RAND_AMPL_START + MAGICIAN_SIZE.width
PTN_HORIZ_WIDTH = GAME_RECT.width - LENGTH_TO_REMOVE

# --- définition de trucs pour les patterns de LINE HORIZ et VERTIC.

# ces deux patterns ont une coordonnée principale (coord 1 = X pour le vertic, Y pour le horiz)
# et une coordonnée secondaire (coord 2 = Y pour le horiz, X pour le vertic)

#Indique si on inverse les positions d'arrivée des magiciens (SWAP), ou pas (KEEP).
#Quand on est KEEP, les magiciens se déplacent en ligne horizontale ou verticale.
#Quand on est SWAP, les magiciens passent tous plus ou moins par le centre de l'écran.
SWAP = True
KEEP = False

#définition des patterns de line, (verticale ou horizontale, haha)
(LINE_VERTIC,  #les magiciens seront générés sur une ligne verticale
 LINE_HORIZ,   # blabla ligne horizontale
) = range(2)

#big dictionnaire de config des patterns de LINE.
# clé : type du pattern.
# valeur : tuple de 5 éléments :
#          - semi-amplitude de random sur la coordonnée 1
#          - amplitude sur le départ de la coord 2
#          - amplitude sur l'écartement entre magicien, de la coord 2
#          - valeur de départ de la coordonnée 2 (Sans aucun rand)
#          - taille de la ligne (coord 2) sur laquelle répartir les magiciens du patterns)
DICT_LINE_INFO = {

  LINE_VERTIC : (PTN_VERTIC_X_RAND_SEMI_AMPL,
                 PTN_VERTIC_Y_RAND_AMPL_START,
                 PTN_VERTIC_Y_RAND_AMPL_SIZE,
                 GAME_RECT.y,
                 PTN_VERTIC_HEIGHT,
                ),

  LINE_HORIZ  : (PTN_HORIZ_Y_RAND_SEMI_AMPL,
                 PTN_HORIZ_X_RAND_AMPL_START,
                 PTN_HORIZ_X_RAND_AMPL_SIZE,
                 GAME_RECT.x,
                 PTN_HORIZ_WIDTH,
                ),
}

#Rect contenant les coordonnées principale de départ et de fin des Pattern de Line.
#on les mets aux bords de l'aire de jeu, mais à une distance de 15
# (donc on inflate de -15*2, oui faut suivre, oui.)
# PL = PAT_LINE = PATTERN DE LINE putain. Je l'avais dit qu'il fallait suivre
PL_RECT_START = GAME_RECT.inflate(-30, -30)

#coordonnées principale de départ. (On les sorts du Rect, c'est plus pratique)
#il faut retirer la taille du magicien aux coordonnées dee bas et de droite. Car
#quand on positionne un magi, on donne son coin supérieur gauche. Du coup, faut se
#rajouter cette marge sinon les magi seront créés en dehors de l'écran.
PL_UP    = PL_RECT_START.top
PL_DOWN  = PL_RECT_START.bottom - MAGICIAN_SIZE.height
PL_LEFT  = PL_RECT_START.left
PL_RIGHT = PL_RECT_START.right - MAGICIAN_SIZE.width

#encore un dictionnaire de config des patterns de LINE, mais un peu plus précis cette fois-ci.
#clé : identifiant du pattern
#valeur : tuple de 4 éléments :
#         - type du pattern (param whichCoord)
#         - coordonnée 1 de départ des magiciens du pattern (param c1Start)
#         - coordonnée 1 de fin des magiciens du pattern (param c1End)
#         - SWAP / KEEP (voir plus haut)
#
#                                 whichCoord,  c1Start,  c1End,    swapPos
DIC_PAT_LINE_INFO = {
 PAT_LINE_VERTIC_TO_LEFT       : (LINE_VERTIC, PL_RIGHT, PL_LEFT,  KEEP) ,
 PAT_LINE_VERTIC_TO_RIGHT      : (LINE_VERTIC, PL_LEFT,  PL_RIGHT, KEEP) ,
 PAT_LINE_HORIZ_TO_UP          : (LINE_HORIZ , PL_DOWN,  PL_UP,    KEEP) ,
 PAT_LINE_HORIZ_TO_DOWN        : (LINE_HORIZ , PL_UP,    PL_DOWN,  KEEP) ,
 PAT_LINE_SWAP_VERTIC_TO_LEFT  : (LINE_VERTIC, PL_RIGHT, PL_LEFT,  SWAP) ,
 PAT_LINE_SWAP_VERTIC_TO_RIGHT : (LINE_VERTIC, PL_LEFT,  PL_RIGHT, SWAP) ,
 PAT_LINE_SWAP_HORIZ_TO_UP     : (LINE_HORIZ , PL_DOWN,  PL_UP,    SWAP) ,
 PAT_LINE_SWAP_HORIZ_TO_DOWN   : (LINE_HORIZ , PL_UP,    PL_DOWN,  SWAP) ,
}

# --- définition de trucs pour le pattern PAT_CIRCLE

#nombre maximal de points sur le cercle
NBR_POINT_CIRCLE = 256

#rayon de base (en pixel) du cercle
CIRCLE_RAY = 100

#liste des angles trignomométrique des points du cercle.
#hahaha ! j'ai écrit trignomométrique !!
ANGLE_LIST = tuple([ (indexPoint * 2 * math.pi) / NBR_POINT_CIRCLE
                      for indexPoint in range(NBR_POINT_CIRCLE)
                   ])

#liste de Rect. Les points du cercle.
CIRCLE_COORD_LIST = tuple([ pyRect(math.cos(angle) * CIRCLE_RAY,
                                   math.sin(angle) * CIRCLE_RAY)
                            for angle in ANGLE_LIST
                          ])

# --- définition de trucs pour le pattern PAT_DIAG

#distance initiale (en pixel) entre le magicien et le joueur
#enfin c'est pas exactement la distance. c'est la distance vertic ou horiz d'une diagonale
#pour avoir la vraie distance, faut faire DIAG_DIST_INIT * <racine de 2>, mtlmsf
DIAG_DIST_INIT = 60

#pixel vertic et horiz ajoutée à la distance de diag initiale, pour placer les autrse magiciens
#après qu'on ait placé les 4 premiers sur les 4 diago.
DIAG_DIST_STEP = 12

#les magiciens ne sont pas placés exactement sur les diagonales. on les bouge un peu en random,
#juste parce que c'est cool.
#semi-amplitude de random en X, sur les coordonnées des magiciens.
DIAG_DIST_X_RAND_SEMI_AMPL = 10
#semi-amplitude Y
DIAG_DIST_Y_RAND_SEMI_AMPL =  8

#direction des diagonales. C'est dans l'ordre trigo. C'est pas si important que ça,
#mais un peu quand même
DIAG_LIST_DIR = (
 ( -1, -1),  #gauche haut. < ^
 ( -1, +1),  #gauche bas.  < V
 ( +1, +1),  #droite bas   > V
 ( +1, -1),  #droite haut  > ^
)

# --- définition de trucs pour les pattern PAT_CIRCLE et PAT_DIAG

#amplitude de migration en X et en Y.
#quand on crée un pattern de cercle ou de diagonale, si le héros est trop en haut et/ou trop
#à gauche de l'écran, y'a des magiciens qu'on peut pas placer. Dans ce cas, on part
#des coordonnées d'un magicien qu'on a pu placer, on migre un peu vers la droite et le bas
#(en random) et on place notre magicien. (Et ainsi de suite pour tous les magi qu'on pas
#pu être placés.
#amplitude positive de migration en X
MIGR_X_RAND_AMPL = 20
#amplitude positive de migration en Y
MIGR_Y_RAND_AMPL = 15


class MagicianListCoordBuilder():
    """
    classe qui gère la création des magiciens (de tout poil) (hahaha).
    merde, j'ai déjà dit ça dans le maggen.py. Du coup elle est plus drôle du tout ma phrase.
    """

    def __init__(self, hero):
        """
        constructeur. (thx captain obvious)

        entrée : hero : référence vers le héros. C'est juste pour choper
                        sa position, quand on veut faire un cercle ou un diag
                        autour de lui.
        """
        #dictionnaire de correspondance entre les types de pattern centré sur un point,
        #et la fonction permettant de le générer. (beurkh, mal au ventre)
        #je suis obligé de le foutre là, le dico, car je dois pointer sur les fonctions
        #de cette classe. TRODO : voir si on peut pas le sortir d'ici quand même
        self.DIC_PAT_CENTER_FUNCTION = {
            PAT_CIRCLE : self.generateCirclePattern,
            PAT_DIAG   : self.generateDiagPattern,
        }

        self.hero = hero


    def generateLinePattern(self, nbrMagi, whichCoord, c1Start,
                            reverseStartSide, c1End=None, swapPos=None):
        """
        génère les coordonnéez pour un pattern de ligne (horiz on vertic)

        entrées :
            nbrMagi : int. nombre de magicien à mettre dans le pattern.
            whichCoord : type de pattern. LINE_VERTIC ou LINE_HORIZ
            c1Start :  int. valeur de la coordonnée principale (coord 1)
                       (X pour une vertic, Y pour une horiz)
            reverseStartSide : boolean. indique dans quel ordre ont range les magiciens
                (Ca aura une influence sur l'ordre dans lequels ils apparaîtront, si jamais
                ils apparaissent un par un). si LINE_VERTIC :
                False : ordre de haut en bas, True : ordre de bas en haut.
                si LINE_HORIZ :
                False : ordre de gauche à droite, True : ordre de droite à gauche
            c1End : si None, on ne fabrique pas les coordonnées de fin
                    si int, indique la valeur de la coordonnée principale de fin (coord 1)
            swapPos : si c1 vaut None, ce param ne sert à rien. Sinon, c'est SWAP ou KEEP
                      indique si on échange les coordonnées de fin entre les magiciens.

        plat-dessert :
            tuple de 2 éléments :
             - liste de Rect de nbrMagi éléments. coordonnées de départ pour les
               magis du pattern à créer.
             - soit None, soit liste de Rect de nbrMagi éléments (coordonnée de fin).
               ça dépend si on a demandé à créer les coordonnées de fin ou pas, via le param c1End
        """

        #récupération de la config lié au type de pattern (VERTIC ou HORIZ)
        (c1RandSemiAmpl, c2RandAmplStart, c2RandAmplSize, c2Start, c2Size,
        ) = DICT_LINE_INFO[whichCoord]

        #ajout de la composante random sur la coordonnée principale de départ
        c1StartRand = c1Start + centeredRandom(c1RandSemiAmpl)

        #calcul de la taille de la ligne sur laquelle on va répartir les magiciens
        #avec un petit coup de random à amplitude négative dessus)
        #on la met en négatif car ça permet  d'être sûr que ça dépassera pas l'écran.
        c2sizeRand = c2Size - randRange(c2RandAmplSize)
        #calcul de la distance entre les magiciens.
        c2Step = c2sizeRand / nbrMagi
        #calcul de la coordonnée secondaire de départ du premier magicien de la ligne.
        #on ajoute c2Step/2, parce que on va faire comme ça en fait :
        #bord. 1/2 dist. magi.     dist.        magi.       dist.      magi. 1/2 dist. bord
        #   |   ---------  *  ------------------  *  ------------------  *  ---------   |
        #ha! le schéma de la mort! Ouais, finalement je vais me droguer, au lieu de coder des jeux
        c2StartRand = c2Start + c2Step / 2 + randRange(c2RandAmplStart)

        #création d'une liste allant de 0 à nbrMagi-1, pour après, créer les coord 2
        if reverseStartSide:
            #la liste doit être mise à l'envers.
            #on compte de 0 à nbrMagi-1, et on inverse la liste. ( c'est ce que fait le [::-1] )
            #je veux pas directement compter de nbrMagi-1 à 0, car ça fait du code mega moche :
            # range(nbrMagi-1, -1, -1). Je l'aurais fait si c'était une grosse liste.
            c2ListMagi = range(nbrMagi)[::-1]
        else:
            #y'a juste à compter, sans inverser.
            c2ListMagi = range(nbrMagi)

        #création des valeurs de la coordonnée secondaire, à partir de la liste.
        c2ListMagi = [ magi * c2Step + c2StartRand for magi in c2ListMagi ]

        #création des Rect rassemblant la liste des coord 1 et des coord 2,
        #en les mettant au bon endroit, (X ou Y), selon le type de ligne.
        if whichCoord == LINE_VERTIC:
            #c1 dans X, c2 dans Y. captain obvious
            listCoordStart = [ pyRect(c1StartRand, c2Magi)
                               for c2Magi in c2ListMagi ]
        else:
            #c1 dans Y, c2 dans X. captain obvious
            listCoordStart = [ pyRect(c2Magi, c1StartRand)
                               for c2Magi in c2ListMagi ]

        #si on n'a pas demandé les coordonnées de fin, on peut se barrer tout de suite.
        if c1End is None:
            return listCoordStart, None

        #ajout de la composante random sur la coordonnée principale de fin
        c1EndRand = c1End + centeredRandom(c1RandSemiAmpl)

        #la coordonnée secondaire de début et la secondaire de fin sont les mêmes
        #création des Rect rassemblant les listes des coords de fin,
        if whichCoord == LINE_VERTIC:
            #c1 dans X, c2 dans Y. captain obvious
            listCoordEnd = [ pyRect(c1EndRand, c2Magi)
                             for c2Magi in c2ListMagi ]
        else:
            #c1 dans Y, c2 dans X. captain obvious
            listCoordEnd = [ pyRect(c2Magi, c1EndRand)
                             for c2Magi in c2ListMagi ]

        #on inverse les coordonnées de fin si on est en SWAP (voir blabla au début du fichier)
        if swapPos == SWAP:
            listCoordEnd.reverse()

        return listCoordStart, listCoordEnd


    def rayCenterMigrCoords(self, listCoordStart,
                            center, isClockWise, rayCoef=NOT_FLOATING_PREC):
        """
        fonction qui fait plein de truc pour les patterns PAT_CIRCLE et PAT_DIAG :
         - applique le clockWise
         - le coef du rayon,
         - le décalage vers le centre,
         - la migration à l'arrache des points qui sont pas dans l'écran.

        entrées :
            listCoordStart : liste de Rect, contenant les coordonnées de départ des magiciens.
                             Elles sont arrangées selon le pattern qu'on veut, on s'en fout.
                             Mais ça doit être un pattern avec un centre, pour l'instant : (0, 0)
                             Certaines coord pourront se retrouver en dehors de l'écran.
                             Ce sera corrigé.
            center : Rect. coordonnées du vrai centre autour duquel on veut construire le pattern.
                     (à priori, autour du héros)
            isClockWise : boolean. indique si on range les coordonnées des magiciens
                          dans le sens des aiguilles d'une montre, ou dans le sens inverse.
            rayCoef : int (en virgule pas flottante). coefficient d'agrandissement-retrecissement
                      de la distance entre les coordonnées des magiciens et le centre.
                      NOT_FLOATING_PREC correspond à un coef de 1.

        plat-dessert :
            listCoordStart : liste de Rect, avec autant d'éléments que la liste passés en
                             paramètres. Mais le contenu a été arrangé comme il faut.
        """

        #inversion de l'ordre des coordonnées d'arrivée. Quand on les associera à des magiciens,
        #on les verra apparaître dans un ordre ou un autre.
        if not isClockWise:
            listCoordStart.reverse()

        #application du coef sur la distance magicien-centre.
        if rayCoef != NOT_FLOATING_PREC:
            for circPoint in listCoordStart:
                #multiplication par le coef, qui est en virgule-pas-flottante
                circPoint.x = (circPoint.x * rayCoef) >> SHIFT_PREC
                circPoint.y = (circPoint.y * rayCoef) >> SHIFT_PREC

        #déplacement des points vers le vrai centre, indiqué en param
        centerCoord = center.topleft
        for circPoint in listCoordStart:
            circPoint.move_ip(centerCoord)

        #récupération du nombre de point que y'a au départ
        lenInitlistCoordStart =  len(listCoordStart)

        #supression des points qui dépasse en haut et à gauche.
        #on autorise le dépassement en bas et à droite, (voir blabla plus haut)
        listCoordStart = [ circPoint for circPoint in listCoordStart
                           if circPoint.x > GAME_RECT.left and
                              circPoint.y > GAME_RECT.top
                         ]

        #nombre de points qui ont été supprimés, et que donc il faut remettre
        nbrPointRemoved = lenInitlistCoordStart - len(listCoordStart)

        #migration à l'arrache des points qui ont été viré.

        for _ in xrange(nbrPointRemoved):

            #choix à l'arrache d'un point valide (toujours dans l'écran)

            if len(listCoordStart) == 0:
                #il n'y a plus aucun point valide, on les a tous virés.
                #fabrication super à l'arrache d'un point valide. (à droite du centre)
                circPoint = pyRect(center.x + CIRCLE_RAY, center.y)
            else:
                #il y a un ou plusieurs points valides
                #on en prend un au hasard.
                circPoint = listCoordStart[randRange(len(listCoordStart))]

            #migration du point, vers le bas et la droite, afin de trouver à l'arrache
            #un autre point valide à partir du premier.(pas de limite sur les bords droit et bas)
            pointArrache = pyRect(circPoint.x + randRange(MIGR_X_RAND_AMPL),
                                  circPoint.y + randRange(MIGR_Y_RAND_AMPL))

            #et ajout à l'arrache dans la liste.
            #à l'itération suivante de la boucle, on risque de repartir ce point créé à l'arrache,
            #pour en refabriquer un autre, encore plus décalé. C'est zarb, mais je m'en cogne.
            listCoordStart.append(pointArrache)

        return listCoordStart


    def generateCirclePattern(self, nbrMagi, center, isClockWise,
                              coordEnd=None, rayCoef=NOT_FLOATING_PREC):
        """
        construit les coordonnées d'un pattern PAT_CIRCLE. Les points sont
        répartis plus ou moins régulièrement, en cercle, autour d'un centre donné,
        et selon un rayon de base de CIRCLE_RAY (constante = 100), auquel on applique un coef.

        entrées :
            nbrMagi : int. nombre de magicien à mettre dans le pattern.

            center,
            isClockWise,
            rayCoef : voir les params de la fonction rayCenterMigrCoords

            coordEnd : si None, on ne fabrique pas les coordonnées de fin
                       si autre chose, on les fabrique.

        plat-dessert :
            tuple de 2 éléments :
             - liste de Rect de nbrMagi éléments. coordonnées de départ pour les
               magis du pattern à créer.
             - soit None, soit liste de Rect de nbrMagi éléments (coordonnée de fin).
               ça dépend si on a demandé à créer les coord de fin ou pas, via le param coordEnd
        """

        #on a déjà tout pleins de coordonnées précalculées, pour un cercle de centre(0, 0),
        #et de rayon CIRCLE_RAY. On commence par prendre des points de ce cercle,

        #on veut des points régulièrement réparti sur le cercle. Donc on calcule tous les combien
        #de qu'on doit prendre un point. (français power !)
        stepPoint = NBR_POINT_CIRCLE / nbrMagi

        #si y'a plus de magi que de points de cercle, on se chope un 0. Or faut quand même
        #avancer un minimum dans la sélection des points
        #c'est un truc à la con qui arrivera jamais, mais on fout quand même la sécurité.
        if stepPoint == 0:
            stepPoint = 1

        #On démarre de n'importe quel point du cercle. Osef.
        startPointIndex = randRange(NBR_POINT_CIRCLE)
        #index du point d'arrivée du cercle (sans tenir compte du modulo-tour-du-compteur-fuck
        endPointIndex = startPointIndex + nbrMagi*stepPoint

        #récupération des index de points du cercle.
        listPointIndex = range(startPointIndex, endPointIndex, stepPoint)
        #pour les index trop grands, on leur fait faire un tour du compteur avec un modulo
        listPointIndex = [ pointIndex % NBR_POINT_CIRCLE
                           for pointIndex in listPointIndex ]

        #récupération des coordonnées des points du cercle, à partir des index
        listCoordStart = [ pygame.rect.Rect(CIRCLE_COORD_LIST[pointIndex])
                           for pointIndex in listPointIndex ]

        #fonction qui arrange plein de trucs avec les coordonnées du cercle
        #(voir description de la fonction)
        param = (listCoordStart, center, isClockWise, rayCoef)
        listCoordStart = self.rayCenterMigrCoords(*param)

        #si on n'a pas demandé les coordonnées d'arrivée des magiciens, on s'en va direct.
        if coordEnd is None:
            return listCoordStart, None

        #sinon, on les construit. C'est facile, c'est le centre du cercle.
        listCoordEnd = (center, ) * nbrMagi

        return listCoordStart, listCoordEnd


    def generateDiagPattern(self, nbrMagi, center, isClockWise,
                            coordEnd=None, rayCoef=NOT_FLOATING_PREC):
        """
        Construit les coordonnées d'un PAT_DIAG. Les points sont répartis équitablement sur les
        4 diagonales partant d'un centre donné. La distance initiale centre-point
        est de DIAG_DIST_INIT. Lorsqu'on a placé 4 magiciens sur les 4 diag, on augmente
        cette distance de DIAG_DIST_STEP, et ainsi de suite.
        On peut appliquer un coef sur toutes ces distances.
        Les points sont un peu randomizés autour de la diagonale.

        entrées :
            nbrMagi : int. nombre de magicien à mettre dans le pattern.

            center,
            isClockWise,
            rayCoef : voir les params de la fonction rayCenterMigrCoords

            coordEnd : si None, on ne fabrique pas les coordonnées de fin
                       si autre chose, on les fabrique.

        plat-dessert :
            tuple de 2 éléments :
             - liste de Rect de nbrMagi éléments. coordonnées de départ pour les
               magis du pattern à créer.
             - soit None, soit liste de Rect de nbrMagi éléments (coordonnée de fin).
               ça dépend si on a demandé à créer les coord de fin ou pas, via le param coordEnd
        """

        #on commence d'abord par créer les points du pattern autour du centre (0, 0),
        #sans aucun coef.

        #init de l'index sur les diagonales, il varie de 0 à 3.
        #Là, on part de n'importe laquelle des 4 diagonales, osef.
        diagCursor = randRange(len(DIAG_LIST_DIR))
        #distance (juste sur le X ou le Y) entre le centre et le point
        currentDistance = DIAG_DIST_INIT
        #liste qu'on va rempliture au fur et à mesure (Liane Foly)
        listCoordStart = []

        for indexMagi in xrange(nbrMagi):

            #on chope le tuple avec des +1 / -1 correspondant à la diagonale courante
            currentDiag = DIAG_LIST_DIR[diagCursor]

            #détermination des coordonnées du point, en fonction de la diag choisi.
            #copier-coller pas bien. Eventuellement, factoriser ce tout petit bout de code
            if currentDiag[0] == -1:
                coordX = -currentDistance
            else:
                coordX = +currentDistance

            if currentDiag[1] == -1:
                coordY = -currentDistance
            else:
                coordY = +currentDistance

            #création du point et ajout dans la liste
            coordStart = pyRect(coordX, coordY)
            listCoordStart.append(coordStart)

            #mise à jour de l'index de la diagonale. On compte de 0 à 3 en faisant des tours
            diagCursor += 1
            if diagCursor >= len(DIAG_LIST_DIR):
                diagCursor = 0

            #Toutes les 4 fois, mais seulement à partir de la quatrième fois,
            #on augmente la currentDistance. ça fait : 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, ...
            if indexMagi & 3 == 3:
                currentDistance += DIAG_DIST_STEP

        #ajout d'un petit peu de random sur tous les points. Comme ça, pour rire.
        for point in listCoordStart:
            point.x += centeredRandom(DIAG_DIST_X_RAND_SEMI_AMPL)
            point.y += centeredRandom(DIAG_DIST_Y_RAND_SEMI_AMPL)

        #fonction qui arrange plein de trucs avec les coordonnées du cercle
        #(voir description de la fonction)
        param = (listCoordStart, center, isClockWise, rayCoef)
        listCoordStart = self.rayCenterMigrCoords(*param)

        #si on n'a pas demandé les coordonnées d'arrivée des magiciens, on s'en va direct.
        if coordEnd is None:
            return listCoordStart, None

        #sinon, on les construit. C'est facile, c'est le centre du pattern.
        listCoordEnd = (center, ) * nbrMagi

        return listCoordStart, listCoordEnd


    def generateRandPattern(self, nbrMagi, coordEnd=None):
        """
        génère un pattern de magicien avec tout random : les positions de départ et d'arrivée

        entrées :
            nbrMagi : int. nombre de magicien à mettre dans le pattern.
            coordEnd : si None, on ne fabrique pas les coordonnées de fin
                       si autre chose, on les fabrique.

        plat-dessert :
            tuple de 2 éléments :
             déjà blablaté dans les fonctions plus haut. S'y référer, bordel
        """

        #création d'une liste de Rect avec les coordonnées complètement random,
        #mais comprises dans l'aire de jeu, quand même.
        listCoordStart = [ pyRect(randRange(GAME_RECT.width) + GAME_RECT.left,
                                  randRange(GAME_RECT.height) + GAME_RECT.top)
                           for _ in xrange(nbrMagi)
                         ]

        #si on n'a pas demandé les coordonnées d'arrivée des magiciens, on s'en va direct.
        if coordEnd is None:
            return listCoordStart, None

        #création d'une autre liste de Rect random, pour les coordonnées d'arrivée
        listCoordEnd = [ pyRect(randRange(GAME_RECT.width) + GAME_RECT.left,
                                randRange(GAME_RECT.height) + GAME_RECT.top)
                         for _ in xrange(nbrMagi)
                       ]

        return listCoordStart, listCoordEnd


    def generatePattern(self, patternType, nbrMagi,
                        coordEnd=None, rayCoef=NOT_FLOATING_PREC):
        """
        grosse fonction de la mort qui reprend toute les autres. Permet de créer un pattern
        comme il faut, juste à partir de son type, et d'un minimum de config

        entrées :
            patternType : identifiant du type de pattern
            nbrMagi : int. nombre de magicien à mettre dans le pattern.
            coordEnd : si None, on ne fabrique pas les coordonnées de fin
                       si autre chose, on les fabrique.
            rayCoef : int (en virgule pas flottante). utilisé uniquement si le type du pattern
                      est PAT_CIRCLE ou PAT_DIAG. indique le coefficient
                      d'agrandissement-retrecissement de la distance entre les coordonnées
                      des magiciens et le centre. NOT_FLOATING_PREC correspond à un coef de 1.

        plat-dessert :
            un pattern, comme d'hab. Voir les fonctions ci-dessus.
        """

        #on teste si le pattern est de type LINE
        patternLineInfo = DIC_PAT_LINE_INFO.get(patternType)

        if patternLineInfo is not None:

            #il est de type LINE. On récupère la config de ce pattern
            whichCoord, c1Start, c1End, swapPos = patternLineInfo

            #choix en random de l'ordre d'apparition des magiciens.
            #(ça a pas trop d'importance)
            reverseStartSide = randBoole()

            #propagation du fait qu'on veuille pas les coord d'arrivée
            if coordEnd is None:
                c1End = None

            #rassemblement de tous les params de config permettant de créer le pattern,
            #et appel de la fonction qui va le créer.

            param = (nbrMagi, whichCoord, c1Start,
                     reverseStartSide, c1End, swapPos)

            return self.generateLinePattern(*param)

        elif patternType in self.DIC_PAT_CENTER_FUNCTION:

            #le pattern est de type "centré autour d'un point".
            #on chope la fonction correspondante qui permettra de le créer.

            #Pas top car j'accède deux fois de suite à DIC_PAT_CENTER_FUNCTION.
            #mais la seule autre solution, c'est de faire un else tout simple,
            #puis un get, puis un test si None ou pas. Et j'ai pas envie d'une
            #imbrication de if en plus. Là. Voilà. Là. Llalaalalalala
            funcPat = self.DIC_PAT_CENTER_FUNCTION[patternType]

            #choix en random de l'ordre d'apparition des magiciens.
            #(ça a pas trop d'importance)
            isClockWise = randBoole()

            #rassemblement de tous les params de config permettant de créer le pattern,
            #et appel de la fonction qui va le créer.

            #ATTENTION, truc important ! On remarquera que j'indique, pour le paramètre center,
            #la valeur self.hero.rectPos, qui correspond au coordonnées du héros.
            #Ce n'est pas la valeur directe de ses coordonnées, c'est une référence
            #vers ses coordonnées. Cette référence est transmise à chaque magicien.
            #Bon, et ça change quoi ?
            #les magiciens de type MAGI_LINE prennent en compte leur coordonnée d'arrivée au
            #moment de leur création. Si ils ne sont pas tous créés en même temps (il y a du
            #delay entre eux), et que le héros bouge pendance ce temps, ils ne vont pas tous
            #se rendre au même point.
            #Dans le jeu, quand on voit un cercle de magicien se créer petit à petit autour de
            #soi, les magiciens ne vont pas tous se rendre au milieu du cercle. Ils iront un peu
            #n'importe où, selon la façon dont le héros a bougé.
            #En fait j'ai pas fait exprès d'avoir fait comme ça au début. Et après je me suis
            #dit que c'était plutôt cool. Ca augmente la difficulté de ces patterns.

            #Voilà j'ai fini de blablater, on peut reprendre.

            param = (nbrMagi, self.hero.rectPos, isClockWise,
                     coordEnd, rayCoef)

            return funcPat(*param)

        else:
            #le pattern n'est ni un LINE, ni centré autour d'un point.
            #Par défaut, on génère un pattern total random, et crac.
            return self.generateRandPattern(nbrMagi, coordEnd)

