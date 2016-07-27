#/usr/bin/env python
# -*- coding: utf-8 -*-
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

date de la dernière relecture-commentage : 15/10/2010

la classe pour gérer un point qui se déplace (à peu près) dans une direction donnée

C'est un point dans un espace en 2D, auquel on associe un déplacement en ligne droite,
le déplacement est approximationné exprès, pour que ses coordonnées soit
toujours des nombres entiers (donc pour avoir le pixel correspondant)
c'est con c'que je viens de dire. Captain Obvious, putain !

Y'a un déplacement primaire et un déplacement secondaire.

Ca permet par exemple d'avoir un point qui avance tout le temps sur l'axe des X,
mais qui se déplace d'un pixel vers le haut uniquement 1 fois sur 3.
ou 4 fois sur 7. Enfin on fait ce qu'on veut.

vocabulaire :

listTotalMove : liste de Rect(X,Y), indiquant la liste des mouvements à faire par
le MovingPoint. Cette liste contient la somme des déplacements primaire et secondaire.
A chaque cycle, le MovingPoint effectue un mouvement de cette liste, et avance à
l'élément suivant. Quand il est arrivé au bout de la liste, il revient au début
Donc le mouvement pourrait ne jamais s'arrêter.

BIG TRODO : un MovingPointOnParabol avec mouvement initial et accélération,
en virgule pas-flottante / fraction, ou je sais pas quoi.
comme ça je pourrais m'en servir pour plein de trucs.
Je sais pas lesquels, mais plein de trucs. (au moins le SimpleSprite)

"""

import pygame
from common import pyRect

#permet d'indiquer sur quelle coordonnées se trouve le mouvement secondaire du MovingPoint
(MOVE_ON_X,    # le mouvement se trouve sur la coordonnées X
 MOVE_ON_Y,    # le mouvement se trouve sur la coordonnées Y
 MOVE_NONE,    # y'a pas de mouvement secondaire, et crac !
) = range(3)

#mouvement par défaut. Rect(0, 0), c'est à dire pas de mouvement
DEFAULT_MAIN_MOVE = pyRect()


#Je met cette fonction à l'extérieur de la classe. Pour la rendre disponible au code
#extérieur. Comme ça, on peut se calculer soi-même sa listTotalMove et la refiler
#tel quelle à un objet MovingPoint. Ca peut éviter de recalculer plusieurs fois une
#même listTotalMove
def calculateListTotalMove(mainMove, listSecMove, indexSecMove):
    """
    calcule une listTotalMove à partir d'un déplacement secondaire et
    d'un déplacement primaire donné.

    entrées :
        mainMove     : rect (X, Y) indiquant le déplacement principal.
                       ce déplacement sera appliqué à chaque cycle..

        listSecMove  : liste de int, représentant le déplacement secondaire.
                       A chaque cycle, on utilise l'élément courant de cette liste
                       pour se déplacer sur une coordonnée (X ou Y), et on avance d'un élément

        indexSecMove : index de coordonnés sur laquelle appliquer le mouvement secondaire.
                       il faut indiquer : MOVE_ON_X, MOVE_ON_Y ou MOVE_NONE

    plat-dessert :
        listTotalMove : liste de Rect (X, Y)
    """
    #construction de listSecMoveCoords : une liste de tuple (X,Y) contenant la succession
    #de mouvement secondaire. (le mouvement est placcé dans la bonne coordonnée)
    if indexSecMove == MOVE_ON_X:
        listSecMoveCoords = [ pyRect(elem, 0) for elem in listSecMove ]
    elif indexSecMove == MOVE_ON_Y:
        listSecMoveCoords = [ pyRect(0, elem) for elem in listSecMove ]
    else:
        #pas de mouvement secondaire. Donc une liste d'un seul elem avec des 0
        listSecMoveCoords = [ pyRect(0, 0), ]

    #on ajoute le mouvement principal à cette liste de tuple(X,Y)
    #contenant les mouvements secondaires.
    #comme ça, on a une liste contenant la somme des deux mouvements.
    listSecMoveCoords = [ rectElem.move(mainMove.topleft)
                          for rectElem in listSecMoveCoords
                        ]

    #transformation de la liste en tuple, juste parce que c'est cool.
    #et utilisation d'un autre nom.
    listTotalMove = tuple(listSecMoveCoords)

    return listTotalMove



class MovingPoint(pygame.Rect):
    """
    blabla. Voir debut du fichier.
    """

    def __init__(self, rectPos, mainMove=DEFAULT_MAIN_MOVE,
                 listSecMove=None, indexSecMove=MOVE_NONE, listTotalMove=None):
        """
        constructeur (thx captain opbvious)

        entrées :

          rectPos      : rect (X, Y) coordonnées de départ.

          mainMove, listSecMove, indexSecMove : voir fonction calculateListTotalMove
          Il y a des paramètres par défaut, si on les laisse tel quel, y'a aucun mouvement.
          Si on définit le param indexSecMove, faut obligatoirement définir listSecMove,
          sinon ça pète.

          listTotalMove : lorsque ce paramètre est défini, il prend la priorité sur
          les autres (mainMove, listSecMove, indexSecMove). Ca permet de définir
          directement la listTotalMove, si on l'a précalculée ailleurs.
        """

        pygame.Rect.__init__(self, rectPos.topleft, (0, 0))

        if listTotalMove is not None:
            #listTotalMove a été passé en paramètre. On le prend directement
            #et y'a pas besoin de plus de données.
            self.listTotalMove = listTotalMove
        else:
            #listTotalMove n'a pas été passé. On doit le calculer avec les
            #autres paramètres passés à la fonction.
            param = (mainMove, listSecMove, indexSecMove)
            self.listTotalMove = calculateListTotalMove(*param)

        #curseur indiquant sur quelle élément de la liste de mouvement
        #on se trouve actuellement.
        self.cursorListMove = 0


    def advanceOneStep(self):
        """
        fonction permettant de faire avancer d'un pas le MovingPoint.

        La fonction modifie les coordonnées du rect. (Le MovingPoint est hérité d'un rect)
        """

        #application d'un mouvement à partir de listTotalMove,
        #qui contient les mouvements principaux et secondaires.
        self.move_ip(self.listTotalMove[self.cursorListMove].topleft)

        #on fait avancer le curseur de liste de mouvement.
        #Si on a dépassé, on revient à 0
        self.cursorListMove += 1
        if self.cursorListMove == len(self.listTotalMove):
            self.cursorListMove = 0


    def isMoveFinished(self):
        """
        indique si le mouvement du point est fini.

        plat-dessert :
            boolean : False : Mouvement pas fini. True : Mouvement fini.

        Là comme ça elle sert à rien cette fonction. Mais je la surcharge quand je fais
        hériter cette classe pour définir MovingPointOnLine.

        TRODO (version 2, parce que là je m'en tape) : une classe générique MovingPointBase,
        qui est dérivée en MovingPointOnDir (ce serait cette classe) et MovingPointOnLine
        """

        #Le mouvement n'est jamais fini, car on se déplace dans une direction.
        #Y'a pas de point d'arrivée
        return False


