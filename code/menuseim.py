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

date de la derni�re relecture-commentage : 22/02/2011

El�ment de menu qui poutre sa race, parce que non seulement il affiche une image comme un
ouf malade, mais en plus, il est focusable, et en plus-plus, il r�agit aux clics.
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
    Quand y'a le focus sur une image, on monte le glowage une seule fois, et on s'arr�te.
    (On passe progressivement de l'image normale � l'image illumin�e).
    Quand y'a le focus sur un texte, le glowage se fait en continu. Quand on arrive au
    bout de la liste des couleurs glow�es, on revient au d�but.
    Et comme la liste des couleurs est : blanc-bleu-blanc, �a donne une impression de boing-boing.
    """

    def __init__(self, rectPos, theImg, funcAction,
                 clickType=MOUSE_DOWN, inflateDist=2):
        """
        constructeur. (thx captain obvious)

        Au niveau de l'ordre des params, j'ai essay� de faire de mon mieux pour avoir quelque
        chose de logique, homog�ne par rapport aux autres classes, et pratique au niveau
        des valeurs par d�faut. Eh bien je garantis pas que j'y suis arriv�. Et pis j'm'en fous.

        entr�e :
            rectPos, theImg :
                voir description du contructeur de MenuImage

            funcAction, clickType, inflateDist :
                voir description du contructeur de MenuSensitiveSquare
        """

        MenuElem.__init__(self)

        self.rectPos = rectPos

        # -- d�finition des variables utilis�es pour faire glower l'image quand y'a le focus --

        #on pr�calcule la liste des images glow�es. Quand y'a le focus sur une image,
        #on l'affiche progressivement plus claire. Eh bien c'est cette liste qu'on utilise.
        self.listImgWithLight = buildListImgLight(theImg, LIST_TRANSP_FOCUS)

        #index pointant sur la surface courante, dans la liste des surface glow�es.
        #l'index 0 correspond � la surface normale (sans ajout de light).
        #Les suivantes ont �t� transform�s avec un ajout de light.
        self.lightIndex = 0
        #step d'incr�mentation dans la liste des images. (-1 ou +1 ou 0, pour reculer,
        #ou avancer, ou rien, dans la liste.)
        self.lightIndexInc = 0

        #on reprend l'image courante � partir de la liste qu'on a construite
        #(ouais, �a sert � rien cette instruction, mais c'est pour faire cool,
        #genre plus cool que self.theImg = theImg)
        self.theImg = self.listImgWithLight[self.lightIndex]

        #d�finition de la zone dans laquelle cet �l�ment s'affiche, en fonction de l'image
        self.rectDrawZone = getRectDrawZone(self.rectPos, self.theImg)

        #initialisation de la zone sensible du menuElem, que la souris r�agit dessus.
        param = (self, funcAction, RECT_ZERO, clickType, inflateDist)
        MenuSensitiveSquare.initSensiInterface(*param)

        #et hop, apr�s l'initialisation, la vraie d�finition de la zone de o� qu'elle est.
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self)


    def update(self):
        """
        voir description de cette fonction dans MenuElem
        """

        ihmsgInfo = MenuSensitiveSquare.update(self)

        #Si le d�placement de curseur dans la liste des images glow�e est 0,
        #C'est qu'on est pas en train d'illuminer / de d�silluminer l'image.
        #On fixe mustBeRefreshed � False, comme �a l'�l�ment ne se r�affichera pas.
        if self.lightIndexInc == 0:
            self.mustBeRefreshed = False
            return ihmsgInfo

        #d�placement du curseur, dans la direction actuelle.
        self.lightIndex += self.lightIndexInc

        #on v�rifie si on est all� au bout de la liste d'image
        #(selon la direction dans laquelle on va)
        param = (self.lightIndex, self.lightIndexInc,
                 0, len(self.listImgWithLight))

        if boundJustAttained(*param):
            self.lightIndexInc = 0

        #r�cup�ration de l'image point�e par le curseur.
        #le r�affichage de cette image se fera tout seul, lors du draw.
        self.theImg = self.listImgWithLight[self.lightIndex]

        return ihmsgInfo


    def draw(self, surfaceDest):
        """
        dessinage de l'�l�ment de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #et hop, on blite l'image en cours, sur la surface de destination.
        #self.theImg pointe vers une image un peu, compl�tement, ou pas illumin�e.
        #(selon l'�tat actuel du focus). C'est la fonction update qui s'est occup�e de g�rer �a.
        surfaceDest.blit(self.theImg, self.rectDrawZone)


    def takeStimuliGetFocus(self):
        """
        fonction ex�cut�e par le code ext�rieur, pour pr�venir que ce menuElem prend le focus
        """

        #hop paf mother-class. (On choisit carr�ment la mother-motherclass. De toutes fa�ons
        #ni le MenuImage ni le MenuSensitiveSquare ne surcharge cette fonction.
        #L'important, c'est que �a fixe self.focusOn � True
        MenuElem.takeStimuliGetFocus(self)

        #Quand on a le focus, la direction de d�placement de l'index de glow,
        #c'est vers l'avant. Comme �a on affiche une image plus claire.
        self.lightIndexInc = +1

        #et il faudra redessiner l'�l�ment � chaque cycle, pour mettre l'image plus claire.
        self.mustBeRefreshed = True


    def takeStimuliLoseFocus(self):
        """
        fonction ex�cut�e par le code ext�rieur, pour pr�venir que ce menuElem perd le focus
        """

        #hop paf mother-class. Et �a fixe self.focusOn � False. Captbain obvious, oui.
        MenuElem.takeStimuliLoseFocus(self)

        #Quand on perd le focus, la direction de d�placement de l'index de glow,
        #c'est vers l'arri�re. Comme �a on revient vers l'image normale.
        self.lightIndexInc = -1

        #et il faudra redessiner l'�l�ment � chaque cycle, pour remettre l'image normale.
        self.mustBeRefreshed = True

