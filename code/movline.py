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

date de la derni�re relecture-commentage : O4/10/2010

la classe pour g�rer un point qui se d�place en ligne droite (mais mieux que le movpoint)
Au lieu d'indiquer un mouvement primaire et une liste de mouvement secondaire, on indique
directement le point A et le point B. Et youpi !

y'a pas de synchronisation sur la vitesse. C'est � dire qu'un point qui bouge en diagonale
ira en fait plus vite qu'un point qui bouge en ligne droite.
bon, on fera mieux la prochaine fois. Et pis osef d'abord.
"""

import pygame
from common import sign
from movpoint import MOVE_ON_X, MOVE_ON_Y, MOVE_NONE, MovingPoint


class MovingPointOnLine(MovingPoint):
    """
    un point dans un espace en 2D, auquel on associe un d�placement en ligne droite,
    le d�placement est approximationn� expr�s, pour que ses coordonn�es soit
    toujours des nombres entiers (donc pour avoir le pixel correspondant)
    c'est con c'que je viens de dire. Captain Obvious, putain !

    Le d�placement est fait de sorte qu'on aille d'un point A � un point B pil poil comme il faut,
    et que � chaque pas d'avancement, �a bouge que d'un pixel (soit un pixel adjacent, soit un
    en diagonal, mais toujours un seul pixel)

    Bon en fait y'a rien de sorcier. C'est l'algo de base pour tracer des lignes.
    Je l'expliquerais pas en d�tail, y'a surement des tas de sites qui le font mieux que moi.
    """

    def __init__(self, rectPosStart, rectPosEnd):
        """
        constructeur (thx captain opbvious)

        entr�es :
            rectPosStart : Rect. Coordonn�es de la position de d�part
            rectPosEnd   : Rect. Coordonn�es de la position d'arriv�e
        """

        #init de la classe-maman
        pygame.Rect.__init__(self, rectPosStart)

        self.rectPosStart = rectPosStart
        self.rectPosEnd = rectPosEnd

        #calcul des composantes X et Y du vecteur et de la distance A -> B
        self.vectX = rectPosEnd.x - rectPosStart.x
        self.distX = abs(self.vectX)
        self.vectY = rectPosEnd.y - rectPosStart.y
        self.distY = abs(self.vectY)

        #d�termination des directions X et Y vers lesquels on se d�place.
        #la direction donne en m�me temps le pas de d�placement. C'est les valeurs +1 ou -1
        #qu'on applique sur les coordonn�es, pour passer au pixel suivant.
        self.stepX = sign(self.vectX)
        self.stepY = sign(self.vectY)

        # --- d�terminatino du mouvement primaire (main) et du mouvement secondaire ---
        #2 cas possibles : mouvement prim X, mouvement sec Y, ou vice-versa.
        #Le mouvement primaire est effectu� � chaque pas d'avancement.
        #Le mouvement secondaire pas forc�ment. Faut avoir accumul� suffisament de points
        #dans le compteur de mouvement secondaire.
        #Le mouvement primaire est celui dont la composante (X ou Y) a la plus grande
        #distance � faire. Et le mouvement secondaire ben c'est l'autre.

        if self.distX > self.distY:

            #le mouvement primaire est sur X
            self.mainMove = MOVE_ON_X
            #correspondance distance prim et sec <- distance X et Y
            (self.distMain, self.distSec) = (self.distX, self.distY)
            #cr�ation de tuple (X, Y) contenant lez mouvements primaires et secondaires.
            self.mainMoveStep = (self.stepX, 0)
            self.secMoveStep  = (0, self.stepY)

        else:

            #le mouvement primaire est sur Y
            self.mainMove = MOVE_ON_Y
            #correspondance distance prim et sec <- distance X et Y
            (self.distMain, self.distSec) = (self.distY, self.distX)
            #cr�ation de tuple (X, Y) contenant lez mouvements primaires et secondaires.
            self.mainMoveStep = (0, self.stepY)
            self.secMoveStep  = (self.stepX, 0)

        #et �a c'est le compteur de mouvement secondaire.
        self.counterMoveSec = 0


    def isMoveFinished(self):
        """
        indique si le mouvement est fini. (Si on est arriv� jusqu'au point B)

        plat-dessert :
            boolean : False : Mouvement pas fini. True : Mouvement fini.
        """

        #le mouvement est fini si les coordonn�es courantes sont pil poil �gales
        #au coordonn�es de fin. Ca va, pas trop dur ?
        return (self.topleft == self.rectPosEnd.topleft)


    def advanceOneStep(self):
        """
        fonction permettant de faire avancer d'un pas le MovingPointOnLine.

        La fonction modifie les coordonn�es du rect. (Le MovingPointOnLine est h�rit� d'un rect)
        Si on ne fait que le mouvement primaire, on se d�placera
        sur un pixel adjacent au pixel courant.
        Si on fait le mouvement primaire et le secondaire, on se d�placera sur un pixel
        adjacent-mais-en-diagonal au pixel courant.

        Et si le mouvement est d�j� fini, on se d�place pas.
        """

        #Mmmm'voyez. C'est ce que je viens de dire.
        if self.isMoveFinished():
            return

        #on applique le mouvement primaire sur les coordonn�es courantes.
        self.move_ip(self.mainMoveStep)

        #on augmente le compteur de mouvement secondaire. (plus la distance secondaire est
        #grande, plus il faudra faire de mouvement secondaire. Donc on augmente le compteur
        #de la distance secondaire. (L� ce que je dis, c'est juste pour aider � comprendre,
        #c'est pas du tout une justification math�matique rigoureuse,, et je vous fucke).
        self.counterMoveSec += self.distSec

        #on regarde si il faudrait pas appliquer le mouvement secondaire. Plus la
        #distance primaire est grande, moins faut faire de mouvement secondaire.
        #donc on ne fait ce mouvement que quand le compteur contient au moins la
        #distance primaire. C'est comme une histoire de fraction en fait.
        #il faut faire le mouvement sec 2 fois sur 3, ou 455  fois sur 456...
        if self.counterMoveSec >= self.distMain:

            #application du mouvement secondaire
            self.counterMoveSec -= self.distMain

            #diminution du compteur de mouvement secondaire.
            self.move_ip(self.secMoveStep)

