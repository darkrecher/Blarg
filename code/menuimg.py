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

date de la dernière relecture-commentage : 17/02/2011

élément de menu qui affiche une image.
Cet élément de menu ne prend pas le focus et ne réagit pas aux clics de souris.
Mais y'en a un autre qui le fait.
"""

import pygame

from common   import pyRect, getRectDrawZone
from menuelem import MenuElem



class MenuImage(MenuElem):
    """
    image qu'on clique pas dessus, car ça sert à rien.
    """

    def __init__(self, rectPos, theImg):
        """
        constructeur. (thx captain obvious)

        entrée :
            rectPos : Rect(X, Y). Position du coin supérieur gauche du texte.
                      Comme d'hab', les coordonnées sont exprimées localement, par rapport au
                      conteneur de cet élément. Donc y'a des décalages qui s'appliquent, ou pas.

            theImg : pygame.Surface. oui bon ben c'est l'image qu'on va utiliser quoi.
        """

        #constructeur de la mother-class. (Ce constructeur fixe self.rectDrawZone à None,
        #et c'est pas ce qu'on veut. Mais on le redéfinit plus loin).
        MenuElem.__init__(self)

        self.rectPos = rectPos
        self.theImg = theImg

        #définition de la zone dans laquelle cet élément s'affiche, en fonction de l'image
        self.rectDrawZone = getRectDrawZone(self.rectPos, self.theImg)


    def draw(self, surfaceDest):
        """
        dessin de l'élément de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #y'a juste à blitter la surface de l'image sur la surface de destination.
        surfaceDest.blit(self.theImg, self.rectDrawZone)

