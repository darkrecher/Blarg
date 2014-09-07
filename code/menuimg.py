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

date de la derni�re relecture-commentage : 17/02/2011

�l�ment de menu qui affiche une image.
Cet �l�ment de menu ne prend pas le focus et ne r�agit pas aux clics de souris.
Mais y'en a un autre qui le fait.
"""

import pygame

from common   import pyRect, getRectDrawZone
from menuelem import MenuElem



class MenuImage(MenuElem):
    """
    image qu'on clique pas dessus, car �a sert � rien.
    """

    def __init__(self, rectPos, theImg):
        """
        constructeur. (thx captain obvious)

        entr�e :
            rectPos : Rect(X, Y). Position du coin sup�rieur gauche du texte.
                      Comme d'hab', les coordonn�es sont exprim�es localement, par rapport au
                      conteneur de cet �l�ment. Donc y'a des d�calages qui s'appliquent, ou pas.

            theImg : pygame.Surface. oui bon ben c'est l'image qu'on va utiliser quoi.
        """

        #constructeur de la mother-class. (Ce constructeur fixe self.rectDrawZone � None,
        #et c'est pas ce qu'on veut. Mais on le red�finit plus loin).
        MenuElem.__init__(self)

        self.rectPos = rectPos
        self.theImg = theImg

        #d�finition de la zone dans laquelle cet �l�ment s'affiche, en fonction de l'image
        self.rectDrawZone = getRectDrawZone(self.rectPos, self.theImg)


    def draw(self, surfaceDest):
        """
        dessin de l'�l�ment de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #y'a juste � blitter la surface de l'image sur la surface de destination.
        surfaceDest.blit(self.theImg, self.rectDrawZone)

