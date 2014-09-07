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

date de la dernière relecture-commentage : 22/02/2011

Elément de menu qui poutre sa race, parce que non seulement il affiche une image comme un
ouf malade, mais en plus, il est focusable, et en plus-plus, il réagit aux clics.
"""

import pygame

from common import (pyRect, boundJustAttained, getRectDrawZone,
                    LIST_TRANSP_FOCUS, buildListImgLight)

from menuelem import MenuElem
from menusesq import MenuSensitiveSquare, MOUSE_DOWN, RECT_ZERO



class MenuSensitiveImage(MenuSensitiveSquare):
    """
    image qu'on clique dessus, ou pas

    Attention, au niveau du focus, c'est pas comme le MenuSensitiveText.
    Quand y'a le focus sur une image, on monte le glowage une seule fois, et on s'arrête.
    (On passe progressivement de l'image normale à l'image illuminée).
    Quand y'a le focus sur un texte, le glowage se fait en continu. Quand on arrive au
    bout de la liste des couleurs glowées, on revient au début.
    Et comme la liste des couleurs est : blanc-bleu-blanc, ça donne une impression de boing-boing.
    """

    def __init__(self, rectPos, theImg, funcAction,
                 clickType=MOUSE_DOWN, inflateDist=2):
        """
        constructeur. (thx captain obvious)

        Au niveau de l'ordre des params, j'ai essayé de faire de mon mieux pour avoir quelque
        chose de logique, homogène par rapport aux autres classes, et pratique au niveau
        des valeurs par défaut. Eh bien je garantis pas que j'y suis arrivé. Et pis j'm'en fous.

        entrée :
            rectPos, theImg :
                voir description du contructeur de MenuImage

            funcAction, clickType, inflateDist :
                voir description du contructeur de MenuSensitiveSquare
        """

        MenuElem.__init__(self)

        self.rectPos = rectPos

        # -- définition des variables utilisées pour faire glower l'image quand y'a le focus --

        #on précalcule la liste des images glowées. Quand y'a le focus sur une image,
        #on l'affiche progressivement plus claire. Eh bien c'est cette liste qu'on utilise.
        self.listImgWithLight = buildListImgLight(theImg, LIST_TRANSP_FOCUS)

        #index pointant sur la surface courante, dans la liste des surface glowées.
        #l'index 0 correspond à la surface normale (sans ajout de light).
        #Les suivantes ont été transformés avec un ajout de light.
        self.lightIndex = 0
        #step d'incrémentation dans la liste des images. (-1 ou +1 ou 0, pour reculer,
        #ou avancer, ou rien, dans la liste.)
        self.lightIndexInc = 0

        #on reprend l'image courante à partir de la liste qu'on a construite
        #(ouais, ça sert à rien cette instruction, mais c'est pour faire cool,
        #genre plus cool que self.theImg = theImg)
        self.theImg = self.listImgWithLight[self.lightIndex]

        #définition de la zone dans laquelle cet élément s'affiche, en fonction de l'image
        self.rectDrawZone = getRectDrawZone(self.rectPos, self.theImg)

        #initialisation de la zone sensible du menuElem, que la souris réagit dessus.
        param = (self, funcAction, RECT_ZERO, clickType, inflateDist)
        MenuSensitiveSquare.initSensiInterface(*param)

        #et hop, après l'initialisation, la vraie définition de la zone de où qu'elle est.
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self)


    def update(self):
        """
        voir description de cette fonction dans MenuElem
        """

        ihmsgInfo = MenuSensitiveSquare.update(self)

        #Si le déplacement de curseur dans la liste des images glowée est 0,
        #C'est qu'on est pas en train d'illuminer / de désilluminer l'image.
        #On fixe mustBeRefreshed à False, comme ça l'élément ne se réaffichera pas.
        if self.lightIndexInc == 0:
            self.mustBeRefreshed = False
            return ihmsgInfo

        #déplacement du curseur, dans la direction actuelle.
        self.lightIndex += self.lightIndexInc

        #on vérifie si on est allé au bout de la liste d'image
        #(selon la direction dans laquelle on va)
        param = (self.lightIndex, self.lightIndexInc,
                 0, len(self.listImgWithLight))

        if boundJustAttained(*param):
            self.lightIndexInc = 0

        #récupération de l'image pointée par le curseur.
        #le réaffichage de cette image se fera tout seul, lors du draw.
        self.theImg = self.listImgWithLight[self.lightIndex]

        return ihmsgInfo


    def draw(self, surfaceDest):
        """
        dessinage de l'élément de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #et hop, on blite l'image en cours, sur la surface de destination.
        #self.theImg pointe vers une image un peu, complètement, ou pas illuminée.
        #(selon l'état actuel du focus). C'est la fonction update qui s'est occupée de gérer ça.
        surfaceDest.blit(self.theImg, self.rectDrawZone)


    def takeStimuliGetFocus(self):
        """
        fonction exécutée par le code extérieur, pour prévenir que ce menuElem prend le focus
        """

        #hop paf mother-class. (On choisit carrément la mother-motherclass. De toutes façons
        #ni le MenuImage ni le MenuSensitiveSquare ne surcharge cette fonction.
        #L'important, c'est que ça fixe self.focusOn à True
        MenuElem.takeStimuliGetFocus(self)

        #Quand on a le focus, la direction de déplacement de l'index de glow,
        #c'est vers l'avant. Comme ça on affiche une image plus claire.
        self.lightIndexInc = +1

        #et il faudra redessiner l'élément à chaque cycle, pour mettre l'image plus claire.
        self.mustBeRefreshed = True


    def takeStimuliLoseFocus(self):
        """
        fonction exécutée par le code extérieur, pour prévenir que ce menuElem perd le focus
        """

        #hop paf mother-class. Et ça fixe self.focusOn à False. Captbain obvious, oui.
        MenuElem.takeStimuliLoseFocus(self)

        #Quand on perd le focus, la direction de déplacement de l'index de glow,
        #c'est vers l'arrière. Comme ça on revient vers l'image normale.
        self.lightIndexInc = -1

        #et il faudra redessiner l'élément à chaque cycle, pour remettre l'image normale.
        self.mustBeRefreshed = True

