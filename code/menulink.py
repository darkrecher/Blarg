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

date de la dernière relecture-commentage : 23/02/2011

Elément de menu qui poutre sa race, parce que non seulement il affiche du texte comme un
ouf malade, mais en plus, il est focusable, et en plus-plus, il réagit aux clics.
tout ça pour faire un lien vers un site internet quelconque. Préférablement avec des nichons.

Quand le joueur clique sur un lien. On lui ouvre son navigateur
internet pour aller vers ledit lien. Mais il faut qu'il puisse le voir. Donc on lui enlève
le plein écran, si il est en plein écran. Par contre, on n'enregistre pas dans le
fichier de sauvegarde qu'on est passé en mode windowed. C'est du windowed provisoire.
"""

import pygame

from common   import (securedPrint, IHMSG_REDRAW_MENU, IHMSG_VOID,
                      SCREEN_WINDOWED, SCREEN_FULL)

from menusesq import MOUSE_DOWN
from menusetx import MenuSensitiveText
from yargler  import theSoundYargler, SND_MENU_SELECT
from menucomn import theGraphModeChanger

try:
    import webbrowser
except Exception, e:
    webbrowser = None
    securedPrint("impossible de choper un navigateur internet, ceay pa grave")
    securedPrint(e)



class MenuLink(MenuSensitiveText):
    """
    texte qu'on clique dessus, et qui va vers le lien indiqué par le texte.
    """

    def __init__(self, rectPos, font, surfaceDest, idTxtStock=None,
                 text="", clickType=MOUSE_DOWN, inflateDist=5):
        """
        constructeur. (thx captain obvious)

        entrée :
            rectPos, font, idTxtStock, text : voir description du contructeur de MenuText

            clickType, inflateDist : voir description du contructeur de MenuSensitiveSquare

            surfaceDest : surface principale, sur laquelle s'affiche tout le jeu.
                          ce MenuElem se permet de la modifier (puisqu'il se permet de
                          quitter le plein écran). (Ce qui est bourrin, mais pas mieux).
        """

        self.surfaceDest = surfaceDest

        #initialisation de la classe, comme si c'était un MenuSensitiveText.
        #D'ailleurs c'en est un, oui.
        #pour cette classe, la funcAction est une fonction interne, et prédéfinie.
        #Elle ouvre le navigateur vers le lien indiqué, et elle quitte le plein écran.
        param = (self, rectPos, font,
                 self.mactQuitFullScreenAndGoToDaInterWeb,
                 idTxtStock, text, clickType, inflateDist)

        MenuSensitiveText.__init__(*param)

        #le lien où que va le navigateur, c'est le texte affiché.
        #Y'a pas le choix, et c'est fait exprès.
        self.url = self.theLamoche.text


    def mactQuitFullScreenAndGoToDaInterWeb(self):
        """
        fonction qui, comme son nom l'indique, quitte le plein écran et va vers un lien
        d'internet avec le navigateur par défaut de l'ordinateur du monsieur.

        plat-dessert : tuple de message d'ihm. (Cette fonction est bindée en interne sur
                       l'activation du MenuElem.) (C'est beau cette phrase)
        """
        #son de sélection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        ihmsgInfo = IHMSG_VOID

        if webbrowser is not None:

            #y'a moyen d'aller sur l'interweb. On va le faire, mais avant,
            #on regarde si on est en plein écran.
            if theGraphModeChanger.getScreenGlobDataVal() == SCREEN_FULL:

                #nom à rallonge de mayrde
                tGM = theGraphModeChanger

                #méchamment bourrin de changer la surface principale d'affichage ici, à l'arrache.
                #(voir même blabla dans MenuManagerMain.mactToggleFullScreen)
                self.surfaceDest = tGM.setGraphMode(SCREEN_WINDOWED)

                #On a changé de mode, donc faut tout redraw. C'est plus sûr
                ihmsgInfo += (IHMSG_REDRAW_MENU, )

            #Et ça c'est la fonction toute faite pour demander au navigateur par défaut
            #d'aller sur le lien interweb spécifié.
            webbrowser.open(self.url)

        else:

            #y'a pas moyen d'aller sur l'interweb. On balance des messages sur stdout.
            securedPrint("Allez voir le site %s !!!" % self.url)
            securedPrint("J'irais bien tout seul, mais j'y arrive pas, d'ici")

        return ihmsgInfo


    def changeLanguage(self):
        """
        changement du langage. (voir descrip dans MenuElem)
        """
        #Si y'a une version anglaise et une version française du lien internet, tout cela
        #est indiqué dans la classe txtStock, et le changeLanguage s'occupe de le gérer.
        MenuSensitiveText.changeLanguage(self)
        #on remet à jour le lien internet en fonction du nouveau texte.
        self.url = self.theLamoche.text

