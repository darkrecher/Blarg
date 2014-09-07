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

date de la dernière relecture-commentage : 16/03/2011

Menu affichant l'histoire, sous forme d'un texte qui défile. Waouf ! Truc de malade !
"""

import pygame

from common import (pyRect,
                    IHMSG_REDRAW_MENU, IHMSG_QUIT, IHMSG_VOID, SCREEN_RECT)

from menucomn import mkeyQuitEsc
from lamoche  import ALIGN_CENTER_X
from menuanyk import MenuSensitiveAnyKeyButton
from menutxt  import MenuText
from menusubm import MenuSubMenu
from txtstock import txtStock
from menumng  import MenuManager
from yargler  import theSoundYargler, SND_STORY_MUSIC

#hauteur, en pixels, sur laquelle on fait défiler les textes de l'histoire.
STORY_SCROLL_HEIGHT = 280
#Je fout cette hauteur dans un rect, pour pouvoir profiter des fonctions cools des rects.
RECT_STORY_SCROLL_HEIGHT = pyRect(0, STORY_SCROLL_HEIGHT)

#abscisse du milieu de l'écran. Tous les textes sont centrées horizontalement au milieu.
X_MIDDLE = SCREEN_RECT.width / 2

#liste de tuple regroupant toutes les infos des MenuText.
#Chaque tuple contient 2 éléments :
# - coordonnées finales du MenuText dans le gigantesque SubMenu affichant l'histoire.
#    "finales", ça veut dire : "Quand le scrolling vertical est terminé".
# - identifiant du texte à afficher, dans la classe txtStock.
#
#Le truc cool, c'est de s'arranger pour que
#coordonnée Y du MenuText le plus haut + hauteur du scrolling = bas de l'écran.
#Comme ça, au début, on voit pas du tout de texte, et il apparaît lentement par le bas.
#Il aurait falu réfléchir un peu plus à tout ça si le texte n'avait pas tenu
#entièrement dans l'écran. Mais là ça tient, donc c'est cool.
LIST_INFO_MENU_TEXT = (
    (( X_MIDDLE,  20), txtStock.STORY_01      ),
    (( X_MIDDLE,  40), txtStock.STORY_02      ),
    (( X_MIDDLE,  70), txtStock.STORY_03      ),
    (( X_MIDDLE,  90), txtStock.STORY_04      ),
    (( X_MIDDLE, 110), txtStock.STORY_05      ),
    (( X_MIDDLE, 150), txtStock.STORY_SURVIVE ),
    (( X_MIDDLE, 180), txtStock.STORY_SCRL_01 ),
    (( X_MIDDLE, 200), txtStock.STORY_SCRL_02 ),
    (( X_MIDDLE, 220), txtStock.STORY_SCRL_03 ),
    (( X_MIDDLE, 260), txtStock.STORY_DO_STHG ),
)



class MenuManagerStory(MenuManager):
    """
    menu pour afficher le superbe scénario du jeu. Avec le scrolling et tout.
    """

    def __init__(self, surfaceDest, dicImg, fontLittle):
        """
        constructeur. (thx captain obvious)

        entrée :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontLittle : objet pygame.font.Font. police de caractères affichant le texte en petit.
        """

        MenuManager.__init__(self, surfaceDest, dicImg)

        self.fontLittle = fontLittle

        # --- Création des MenuElem de type MenuText, définissant le blabla de l'histoire ---

        #liste qui contiendra tous les MenuText du blabla de l'histoire.
        listSubMenuText = []

        for coord, idTxtStock in LIST_INFO_MENU_TEXT:

            #détermination des coordonnées initiales du MenuText, dans le SubMenu.
            #(C'est la coordonnée de base + la hauteur du scrolling).
            #Et après on fera remonter tout ça.
            rectCoord = RECT_STORY_SCROLL_HEIGHT.move(coord)

            #création du MenuText et ajout dans la liste.
            menuElem = MenuText(rectCoord, fontLittle,
                                idTxtStock, alignX=ALIGN_CENTER_X)

            listSubMenuText.append(menuElem)

        #tuplifiage de la liste contenant tous les textes, pour accélérer l'exécution du code.
        listSubMenuText = tuple(listSubMenuText)

        # --- Création du SubMenu contenant tous les MenuText du blabla des crédits. ---

        #Le SubMenu prend tout l'écran en hauteur et en largeur. Il contient les MenuText
        #Sa scrollLimits, c'est la hauteur du scrolling à effectuer, tout connement.
        param = (pyRect(0, 0, 400, 300), listSubMenuText,
                 (0, STORY_SCROLL_HEIGHT))

        self.msubStoryText = MenuSubMenu(*param)

        # --- Création du MenuElem invisible liant la touche Esc à la fonction mactScrollEnd ---

        manyScrollEnd = MenuSensitiveAnyKeyButton(self.mactScrollEnd)

        # --- Rangement de tous les MenuElem créés, dans la grande liste globale. ---

        #Ah ben y'a que trois MenuElem dans cette grande liste. On peut la créer directement.
        #(on ne met pas la liste de tous les MenuText précédemment créés. On met le SubMenu
        #contenant tous ces MenuText).
        self.listMenuElem = (mkeyQuitEsc, manyScrollEnd, self.msubStoryText)

        self.initFocusCyclingInfo()


    def startMenu(self):
        """
        fonction qui s'exécute au début de l'activation du menu
        (voir description de la fonction dans la classe-mère)
        """
        #on remet le scrolling à la position tout en haut. (Y = 0)
        self.msubStoryText.scrollSetPosition()
        #son de la musique de pas(star wars). tu tu tuluuuu tu tuluuuu tu tuluuuu.
        theSoundYargler.playSound(SND_STORY_MUSIC)


    def periodicAction(self):
        """
        fonction du menu effectuant une action périodique. (Voir description dans MenuManager)
        """

        #tant que la hauteur de scrolling n'a pas été atteinte, on fait un petit coup de
        #scrolling vers le haut, (plus exactement, on fait un déplacement du rect d'affichage
        #du submenu vers le bas, mais ça revient au même).
        if self.msubStoryText.sourceRectToBlit.y < STORY_SCROLL_HEIGHT:
            self.msubStoryText.scrollVertically(+2)
            return (IHMSG_REDRAW_MENU, )

        #le scrolling a été effectué. Y'a rien à faire, glandage philosophique, puis on se casse.
        return IHMSG_VOID


    def mactScrollEnd(self):
        """
        fonction exécutée quand on appuie sur Esc.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        Si le scrolling est pas finie, on le finit directos d'un seul coup.
        Si il est fini, on quitte le menu.
        """

        if self.msubStoryText.sourceRectToBlit.y < STORY_SCROLL_HEIGHT:
            #Le scrolling est pas fini. On fixe la position du SubMenu à la position finale. Paf.
            self.msubStoryText.scrollSetPosition(STORY_SCROLL_HEIGHT)
            return (IHMSG_REDRAW_MENU, )

        #Le scrolling est fini. On envoie un message de quittage du menu.
        return (IHMSG_QUIT, )

