#/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Blarg version 1.0

    La page du jeu sur indieDB : http://www.indiedb.com/games/blarg
    Liens vers d'autres jeux sur mon blog : http://recher.wordpress.com/jeux
    Mon twitter : http://twitter.com/_Recher_

    Ce superbe jeu, son code source, ses images, et son euh... contenu sonore est disponible,
    au choix, sous la licence Art Libre ou la licence CC-BY-SA

    Copyright 2010 R�ch�r
    Copyleft : cette oeuvre est libre, vous pouvez la redistribuer et/ou la modifier selon les
    termes de la Licence Art Libre. Vous trouverez un exemplaire de cette Licence sur le site
    Copyleft Attitude http://www.artlibre.org ainsi que sur d'autres sites.

    Creative Commons - Paternit� - Partage des Conditions Initiales � l'Identique 2.0 France
    http://creativecommons.org/licenses/by-sa/2.0/fr/deed.fr

date de la derni�re relecture-commentage : 15/10/2010

la classe pour g�rer un point qui se d�place (� peu pr�s) dans une direction donn�e

C'est un point dans un espace en 2D, auquel on associe un d�placement en ligne droite,
le d�placement est approximationn� expr�s, pour que ses coordonn�es soit
toujours des nombres entiers (donc pour avoir le pixel correspondant)
c'est con c'que je viens de dire. Captain Obvious, putain !

Y'a un d�placement primaire et un d�placement secondaire.

Ca permet par exemple d'avoir un point qui avance tout le temps sur l'axe des X,
mais qui se d�place d'un pixel vers le haut uniquement 1 fois sur 3.
ou 4 fois sur 7. Enfin on fait ce qu'on veut.

vocabulaire :

listTotalMove : liste de Rect(X,Y), indiquant la liste des mouvements � faire par
le MovingPoint. Cette liste contient la somme des d�placements primaire et secondaire.
A chaque cycle, le MovingPoint effectue un mouvement de cette liste, et avance �
l'�l�ment suivant. Quand il est arriv� au bout de la liste, il revient au d�but
Donc le mouvement pourrait ne jamais s'arr�ter.

BIG TRODO : un MovingPointOnParabol avec mouvement initial et acc�l�ration,
en virgule pas-flottante / fraction, ou je sais pas quoi.
comme �a je pourrais m'en servir pour plein de trucs.
Je sais pas lesquels, mais plein de trucs. (au moins le SimpleSprite)

"""

import pygame
from common import pyRect

#permet d'indiquer sur quelle coordonn�es se trouve le mouvement secondaire du MovingPoint
(MOVE_ON_X,    # le mouvement se trouve sur la coordonn�es X
 MOVE_ON_Y,    # le mouvement se trouve sur la coordonn�es Y
 MOVE_NONE,    # y'a pas de mouvement secondaire, et crac !
) = range(3)

#mouvement par d�faut. Rect(0, 0), c'est � dire pas de mouvement
DEFAULT_MAIN_MOVE = pyRect()


#Je met cette fonction � l'ext�rieur de la classe. Pour la rendre disponible au code
#ext�rieur. Comme �a, on peut se calculer soi-m�me sa listTotalMove et la refiler
#tel quelle � un objet MovingPoint. Ca peut �viter de recalculer plusieurs fois une
#m�me listTotalMove
def calculateListTotalMove(mainMove, listSecMove, indexSecMove):
    """
    calcule une listTotalMove � partir d'un d�placement secondaire et
    d'un d�placement primaire donn�.

    entr�es :
        mainMove     : rect (X, Y) indiquant le d�placement principal.
                       ce d�placement sera appliqu� � chaque cycle..

        listSecMove  : liste de int, repr�sentant le d�placement secondaire.
                       A chaque cycle, on utilise l'�l�ment courant de cette liste
                       pour se d�placer sur une coordonn�e (X ou Y), et on avance d'un �l�ment

        indexSecMove : index de coordonn�s sur laquelle appliquer le mouvement secondaire.
                       il faut indiquer : MOVE_ON_X, MOVE_ON_Y ou MOVE_NONE

    plat-dessert :
        listTotalMove : liste de Rect (X, Y)
    """
    #construction de listSecMoveCoords : une liste de tuple (X,Y) contenant la succession
    #de mouvement secondaire. (le mouvement est placc� dans la bonne coordonn�e)
    if indexSecMove == MOVE_ON_X:
        listSecMoveCoords = [ pyRect(elem, 0) for elem in listSecMove ]
    elif indexSecMove == MOVE_ON_Y:
        listSecMoveCoords = [ pyRect(0, elem) for elem in listSecMove ]
    else:
        #pas de mouvement secondaire. Donc une liste d'un seul elem avec des 0
        listSecMoveCoords = [ pyRect(0, 0), ]

    #on ajoute le mouvement principal � cette liste de tuple(X,Y)
    #contenant les mouvements secondaires.
    #comme �a, on a une liste contenant la somme des deux mouvements.
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

        entr�es :

          rectPos      : rect (X, Y) coordonn�es de d�part.

          mainMove, listSecMove, indexSecMove : voir fonction calculateListTotalMove
          Il y a des param�tres par d�faut, si on les laisse tel quel, y'a aucun mouvement.
          Si on d�finit le param indexSecMove, faut obligatoirement d�finir listSecMove,
          sinon �a p�te.

          listTotalMove : lorsque ce param�tre est d�fini, il prend la priorit� sur
          les autres (mainMove, listSecMove, indexSecMove). Ca permet de d�finir
          directement la listTotalMove, si on l'a pr�calcul�e ailleurs.
        """

        pygame.Rect.__init__(self, rectPos.topleft, (0, 0))

        if listTotalMove is not None:
            #listTotalMove a �t� pass� en param�tre. On le prend directement
            #et y'a pas besoin de plus de donn�es.
            self.listTotalMove = listTotalMove
        else:
            #listTotalMove n'a pas �t� pass�. On doit le calculer avec les
            #autres param�tres pass�s � la fonction.
            param = (mainMove, listSecMove, indexSecMove)
            self.listTotalMove = calculateListTotalMove(*param)

        #curseur indiquant sur quelle �l�ment de la liste de mouvement
        #on se trouve actuellement.
        self.cursorListMove = 0


    def advanceOneStep(self):
        """
        fonction permettant de faire avancer d'un pas le MovingPoint.

        La fonction modifie les coordonn�es du rect. (Le MovingPoint est h�rit� d'un rect)
        """

        #application d'un mouvement � partir de listTotalMove,
        #qui contient les mouvements principaux et secondaires.
        self.move_ip(self.listTotalMove[self.cursorListMove].topleft)

        #on fait avancer le curseur de liste de mouvement.
        #Si on a d�pass�, on revient � 0
        self.cursorListMove += 1
        if self.cursorListMove == len(self.listTotalMove):
            self.cursorListMove = 0


    def isMoveFinished(self):
        """
        indique si le mouvement du point est fini.

        plat-dessert :
            boolean : False : Mouvement pas fini. True : Mouvement fini.

        L� comme �a elle sert � rien cette fonction. Mais je la surcharge quand je fais
        h�riter cette classe pour d�finir MovingPointOnLine.

        TRODO (version 2, parce que l� je m'en tape) : une classe g�n�rique MovingPointBase,
        qui est d�riv�e en MovingPointOnDir (ce serait cette classe) et MovingPointOnLine
        """

        #Le mouvement n'est jamais fini, car on se d�place dans une direction.
        #Y'a pas de point d'arriv�e
        return False


