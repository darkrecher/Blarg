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

menu tout simple, qui affiche un mini-blabla de 2 lignes juste apr�s que le joueur ait entr�
son nom, lors du premier lancement du jeu.
Les 2 lignes de textes ne sont pas forc�ment les m�mes selon le nom saisi.
"""

import pygame

from common import pyRectTuple, SCREEN_RECT

from menucomn import manyQuit
from lamoche  import ALIGN_CENTER_X
from menutxt  import MenuText
from txtstock import txtStock
from menumng  import MenuManager


#abscisse du milieu de l'�cran. (captain obvious)
X_MIDDLE = SCREEN_RECT.width / 2

#liste d'info permettant de cr�er les MenuText de ce menu.
#(En fait, on les affichera pas tous en m�me temps. On choisira en fonction du nom du joueur)
#Chaque tuple contient 2 �l�ments :
# - coordonn�es du MenuText � l'�cran.
# - identifiant du texte � afficher, dans la classe txtStock.
LIST_INFO_MENU_TEXT_ALL = (
    (( X_MIDDLE, 70), txtStock.NAME_LIE_NORM_1),
    (( X_MIDDLE, 90), txtStock.NAME_LIE_NORM_2),
    (( X_MIDDLE, 70), txtStock.NAME_LIE_DOG_1),
    (( X_MIDDLE, 90), txtStock.NAME_LIE_DOG_2),
)

#valeur d'index, dans LIST_INFO_MENU_TEXT_ALL, permettant de d�finir quels MenuText de cette
#liste on doit afficher. Si on est en mode normal, on affiche tous les MenuText du d�but
#de la liste jusqu'� INDEX_SEP_NORM_DOG (exclus). Si le edoGedoM a �t� activ�, on affiche
#tous les MenuText de INDEX_SEP_NORM_DOG (inclus) � la fin de la liste.
INDEX_SEP_NORM_DOG = 2


class MenuManagerNameIsALie(MenuManager):
    """
    menu pour afficher du blabla apr�s la saisie du nom.
    """

    def __init__(self, surfaceDest, dicImg, fontLittle, archivist):
        """
        constructeur. (thx captain obvious)

        entr�e :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontLittle : objet pygame.font.Font. police de caract�res affichant le texte en petit.

            archivist : objet de la classe �poney-ime, qui g�re le fichier de sauvegarde,
                        et qui permet de savoir si on peut activer le edoGedoM.
        """

        MenuManager.__init__(self, surfaceDest, dicImg)

        self.fontLittle = fontLittle
        self.archivist = archivist

        #nom saisi par le joueur. On l'initialise � une valeur � la con, juste pour un peu
        #plus de "robustesse". Haha.
        self.nameTyped = ""

        # --- Cr�ation de tous les MenuElem (ils seront pas tous affich�s) ---

        #cr�ation de tous les MenuText, selon les infos indiqu�es dans LIST_INFO_MENU_TEXT_ALL.
        listMenuTextAll = [ MenuText(pyRectTuple(coord), fontLittle,
                                     idTxtStock, alignX=ALIGN_CENTER_X)

                            for coord, idTxtStock in LIST_INFO_MENU_TEXT_ALL
                          ]

        #s�paration en deux listes. Les MenuText � afficher si on est en mode normal
        self.listMenuTextNorm   = tuple(listMenuTextAll[:INDEX_SEP_NORM_DOG])
        #Et les MenuText � afficher si le edoGedoM est activ�.
        self.listMenuTextDogDom = tuple(listMenuTextAll[INDEX_SEP_NORM_DOG:])

        # --- Cr�atio nde la grande liste regroupant tous les MenuElem du menu ---

        #manyQuit est le MenuElem liant toutes les touches et les clics de souris � la fonction
        #de quittage du menu en cours.
        #On ajoute dans la liste les MenuText du mode normal. (Par d�faut, on consid�re qu'on
        #est dans ce mode).
        self.listMenuElem = (manyQuit, ) + self.listMenuTextNorm

        self.initFocusCyclingInfo()


    def setNameTyped(self, nameTyped):
        """
        fonction a ex�cuter par le code ext�rieur, permettant d'indiquer � ce menu
        quel est le nom que le joueur a saisi.

        entr�es : nameTyped. string unicode. nom saisi par le joueur.
        """

        #et paf, on s'enregistre �a dans uen variable � soi.
        self.nameTyped = nameTyped


    def startMenu(self):
        """
        fonction qui s'ex�cute au d�but de l'activation du menu
        (voir description de la fonction dans la classe-m�re)
        """

        #si le nom saisi permet d'activer le edoGedoM, alors il faut refaire la liste des
        #MenuElem du menu.
        if self.archivist.isDogDomEdocValid(self.nameTyped):
            #on garde le MenuElem qui fait quitter le menu. Et on prend les MenuText
            #sp�cifiques au EdogEdom.
            self.listMenuElem = (manyQuit, ) + self.listMenuTextDogDom
