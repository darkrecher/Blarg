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

date de la derni�re relecture-commentage : 16/03/2011

Menu affichant l'histoire, sous forme d'un texte qui d�file. Waouf ! Truc de malade !
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

#hauteur, en pixels, sur laquelle on fait d�filer les textes de l'histoire.
STORY_SCROLL_HEIGHT = 280
#Je fout cette hauteur dans un rect, pour pouvoir profiter des fonctions cools des rects.
RECT_STORY_SCROLL_HEIGHT = pyRect(0, STORY_SCROLL_HEIGHT)

#abscisse du milieu de l'�cran. Tous les textes sont centr�es horizontalement au milieu.
X_MIDDLE = SCREEN_RECT.width / 2

#liste de tuple regroupant toutes les infos des MenuText.
#Chaque tuple contient 2 �l�ments :
# - coordonn�es finales du MenuText dans le gigantesque SubMenu affichant l'histoire.
#    "finales", �a veut dire : "Quand le scrolling vertical est termin�".
# - identifiant du texte � afficher, dans la classe txtStock.
#
#Le truc cool, c'est de s'arranger pour que
#coordonn�e Y du MenuText le plus haut + hauteur du scrolling = bas de l'�cran.
#Comme �a, au d�but, on voit pas du tout de texte, et il appara�t lentement par le bas.
#Il aurait falu r�fl�chir un peu plus � tout �a si le texte n'avait pas tenu
#enti�rement dans l'�cran. Mais l� �a tient, donc c'est cool.
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
    menu pour afficher le superbe sc�nario du jeu. Avec le scrolling et tout.
    """

    def __init__(self, surfaceDest, dicImg, fontLittle):
        """
        constructeur. (thx captain obvious)

        entr�e :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontLittle : objet pygame.font.Font. police de caract�res affichant le texte en petit.
        """

        MenuManager.__init__(self, surfaceDest, dicImg)

        self.fontLittle = fontLittle

        # --- Cr�ation des MenuElem de type MenuText, d�finissant le blabla de l'histoire ---

        #liste qui contiendra tous les MenuText du blabla de l'histoire.
        listSubMenuText = []

        for coord, idTxtStock in LIST_INFO_MENU_TEXT:

            #d�termination des coordonn�es initiales du MenuText, dans le SubMenu.
            #(C'est la coordonn�e de base + la hauteur du scrolling).
            #Et apr�s on fera remonter tout �a.
            rectCoord = RECT_STORY_SCROLL_HEIGHT.move(coord)

            #cr�ation du MenuText et ajout dans la liste.
            menuElem = MenuText(rectCoord, fontLittle,
                                idTxtStock, alignX=ALIGN_CENTER_X)

            listSubMenuText.append(menuElem)

        #tuplifiage de la liste contenant tous les textes, pour acc�l�rer l'ex�cution du code.
        listSubMenuText = tuple(listSubMenuText)

        # --- Cr�ation du SubMenu contenant tous les MenuText du blabla des cr�dits. ---

        #Le SubMenu prend tout l'�cran en hauteur et en largeur. Il contient les MenuText
        #Sa scrollLimits, c'est la hauteur du scrolling � effectuer, tout connement.
        param = (pyRect(0, 0, 400, 300), listSubMenuText,
                 (0, STORY_SCROLL_HEIGHT))

        self.msubStoryText = MenuSubMenu(*param)

        # --- Cr�ation du MenuElem invisible liant la touche Esc � la fonction mactScrollEnd ---

        manyScrollEnd = MenuSensitiveAnyKeyButton(self.mactScrollEnd)

        # --- Rangement de tous les MenuElem cr��s, dans la grande liste globale. ---

        #Ah ben y'a que trois MenuElem dans cette grande liste. On peut la cr�er directement.
        #(on ne met pas la liste de tous les MenuText pr�c�demment cr��s. On met le SubMenu
        #contenant tous ces MenuText).
        self.listMenuElem = (mkeyQuitEsc, manyScrollEnd, self.msubStoryText)

        self.initFocusCyclingInfo()


    def startMenu(self):
        """
        fonction qui s'ex�cute au d�but de l'activation du menu
        (voir description de la fonction dans la classe-m�re)
        """
        #on remet le scrolling � la position tout en haut. (Y = 0)
        self.msubStoryText.scrollSetPosition()
        #son de la musique de pas(star wars). tu tu tuluuuu tu tuluuuu tu tuluuuu.
        theSoundYargler.playSound(SND_STORY_MUSIC)


    def periodicAction(self):
        """
        fonction du menu effectuant une action p�riodique. (Voir description dans MenuManager)
        """

        #tant que la hauteur de scrolling n'a pas �t� atteinte, on fait un petit coup de
        #scrolling vers le haut, (plus exactement, on fait un d�placement du rect d'affichage
        #du submenu vers le bas, mais �a revient au m�me).
        if self.msubStoryText.sourceRectToBlit.y < STORY_SCROLL_HEIGHT:
            self.msubStoryText.scrollVertically(+2)
            return (IHMSG_REDRAW_MENU, )

        #le scrolling a �t� effectu�. Y'a rien � faire, glandage philosophique, puis on se casse.
        return IHMSG_VOID


    def mactScrollEnd(self):
        """
        fonction ex�cut�e quand on appuie sur Esc.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        Si le scrolling est pas finie, on le finit directos d'un seul coup.
        Si il est fini, on quitte le menu.
        """

        if self.msubStoryText.sourceRectToBlit.y < STORY_SCROLL_HEIGHT:
            #Le scrolling est pas fini. On fixe la position du SubMenu � la position finale. Paf.
            self.msubStoryText.scrollSetPosition(STORY_SCROLL_HEIGHT)
            return (IHMSG_REDRAW_MENU, )

        #Le scrolling est fini. On envoie un message de quittage du menu.
        return (IHMSG_QUIT, )

