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

date de la derni�re relecture-commentage : 21/03/2011

Menu affichant l'image du h�ros crev�, ainsi que les scores. Et qui attend qu'on appuie
sur Entr�e ou sur Esc.
"""

import pygame
import pygame.locals
pygl = pygame.locals

from common   import pyRectTuple, IHMSG_QUIT, IHMSG_PLAY_ONCE_MORE, IHMSG_VOID

from menucomn import mkeyQuitEsc, IMG_BG_BLARG

from menukey  import MenuSensitiveKey
from menutxt  import MenuText
from menumng  import MenuManager
from txtstock import txtStock


#liste de tuple regroupant toutes les infos des MenuText statiques, � afficher � l'�cran
#(y'a tous les MenuText, sauf ceux affichant les valeurs des scores)
#Chaque tuple contient 2 �l�ments :
# - coordonn�es du MenuText � l'�cran.
# - identifiant du texte � afficher, dans la classe txtStock.
LIST_MENU_TEXT_INFO = (
    (( 10,   7), txtStock.DEAD_PHRASE_1),
    (( 10,  27), txtStock.DEAD_PHRASE_2),
    (( 30, 195), txtStock.DEAD_BURST),
    (( 30, 215), txtStock.DEAD_KILL),
    ((110, 240), txtStock.DEAD_SCORE),
    (( 50, 275), txtStock.DEAD_KEYS),
)

#liste des coordonn�es des 3 MenuText affichant les valeurs des scores. L'ordre est important.
LIST_STAT_COORD = ((280, 195), #nombre de magiciens explos�s
                   (280, 215), #nombre total de magiciens tu�s
                   (170, 240)) #score total



class MenuManagerHeroDead(MenuManager):
    """
    menu � afficher quand le h�ros il meuraille.
    """

    def __init__(self, surfaceDest, dicImg, fontDefault):
        """
        constructeur. (thx captain obvious)

        entr�e :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault : objet pygame.font.Font. police de caract�res par d�faut.
        """

        #init de la mother-class. On passe IMG_BG_BLARG dans le param�tre identifiant
        #l'image de fond. Car pour ce menu, c'est pas l'image de fond par d�faut.
        #C'est l'image avec le h�ros mort transform� en botteule de mana.
        MenuManager.__init__(self, surfaceDest, dicImg, IMG_BG_BLARG)

        self.fontDefault = fontDefault

        # --- Cr�ation des MenuElem de type MenuText, affichant tout le blabla et les scores ---

        #cr�ation des MenuText affichant le texte statique (donc pas les scores)
        #Et rangement dans listMenuText
        listMenuText = [ MenuText(pyRectTuple(coord),
                                  self.fontDefault,
                                  idTxtStock)
                         for (coord, idTxtStock) in LIST_MENU_TEXT_INFO ]

        listMenuText = tuple(listMenuText)

        #Cr�ation des MenuText affichant les trois scores.
        listMtxtStat = [ MenuText(pyRectTuple(coord),
                                  self.fontDefault,
                                  text="0")
                         for coord in LIST_STAT_COORD ]

        #Les textes de ces MenuText doivent �tre remise � jour avant chaque activation du menu.
        #C'est pourquoi, il ne faut pas perdre les MenuText au fond fin d'une liste.
        #Donc on en conserve une r�f�rence en self.
        (self.mtxtStatBurst,
         self.mtxtStatKill,
         self.mtxtStatScore,
        ) = listMtxtStat

        # --- Cr�ation du MenuElem liant la touche Entr�e � la fonction idoinette ---

        param = (self.mactPlayOnceMore, pygl.K_RETURN)
        mkeyPlayOnceMore = MenuSensitiveKey(*param)

        # --- Rassemblement de tous les MenuElem dans une graaaaande liste ---

        #Liste avec les quelques MenuElem qu'on a cr�� ici et l�
        listSomeMenuElem = (mkeyQuitEsc,
                            mkeyPlayOnceMore,
                            self.mtxtStatBurst,
                            self.mtxtStatKill,
                            self.mtxtStatScore)

        #concat de la liste des MenuText statiques et de la liste de tous les autres MenuElem
        self.listMenuElem = listMenuText + listSomeMenuElem

        self.initFocusCyclingInfo()


    def mactPlayOnceMore(self):
        """
        fonction qui s'ex�cute quand le joueur appuie sur Entr�e.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        #on renvoie le message indiquant qu'il faut quitter le menu, ainsi qu'un message
        #sp�cifique, indiquant qu'on veut rejouer encore une fois. Le code ext�rieur doit
        #r�cup�rer ce message et relancer une partie. (Si il le fait pas, il est pas gentil).
        #(Pour info: le MenuElem de ce menu li� � la touche Esc renvoie uniquement IHMSG_QUIT)
        return (IHMSG_QUIT, IHMSG_PLAY_ONCE_MORE)


    def updateMenuTextStat(self, statBurst, statKill, statScore):
        """
        met � jour les valeurs des stats dans les MenuText.

        entr�es :
            statBurst : int. nombre de magiciens explos�s
            statKill  : int. nombre total de magiciens tu�s
            statScore : int. score total.
        """

        #liste de correspondance entre le MenuText affichant une stat et la stat.
        #liste de tuple de 2 elem : (le MenuText, la valeur de la stat)
        listCorrespondanceMenuTextStatValue = (
            (self.mtxtStatBurst, statBurst),
            (self.mtxtStatKill,  statKill),
            (self.mtxtStatScore, statScore)
        )

        #modification du texte pour les 3 MenuText, avec la nouvelle statValue
        #au passage, conversion int -> str de ces statValue
        for menuText, statValue in listCorrespondanceMenuTextStatValue:
            menuText.changeFontAndText(newText=str(statValue))
