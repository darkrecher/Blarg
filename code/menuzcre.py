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

Menu affichant les cr�dits. La liste des contributeurs, la licence, etc.
"""

import pygame
import pygame.locals
pygl = pygame.locals

from common   import (pyRect, pyRectTuple, addThings,
                      IHMSG_REDRAW_MENU, IHMSG_QUIT, IHMSG_VOID)

from menucomn import (mactQuit, mkeyQuitEsc,
                      IMG_CRED_SCRL_UP, IMG_CRED_SCRL_DOWN, IMG_BACK)

from menutxt  import MenuText
from menulink import MenuLink
from menusesq import MOUSE_DOWN, MOUSE_PRESSED, MOUSE_HOVER
from menuseim import MenuSensitiveImage
from menumng  import MenuManager
from menusubm import MenuSubMenu
from txtstock import txtStock


#abr�viation de DONATORS_BOTTOM. (non, �a veut pas dire "le cul des donateurs")
#position Y des textes situ�s apr�s la liste des donateurs. (Je l'ai mis dans
#une variable car la liste des donateurs n'est pas encore fig�e).
DON_BOTT = 460

#liste de tuple regroupant les infos des MenuText affichant les textes des cr�dits.
#les tuples contiennent 3 �l�ments :
#
# - coordonn�es du MenuText dans le gigantesque SubMenu affichant tous les cr�dits.
#
# - string regroupant les caract�ristiques du MenuText :
#   . "T" : Le MenuText est un titre, faut utiliser la font standard, et non pas
#           la font affichant le texte en petit.
#   . "L" : Le MenuText est un lien internet. (L'adresse du lien, c'est le texte).
#   . A priori, on pourrait mettre le "T" et le "L" en m�me temps, mais j'ai pas essay�.
#   C'est un peu pourri d'avoir mis �a sous forme de string, au lieu de constantes
#   avec un nom plus explicite. Mais je voulait une �criture compacte.
#
# - identifiant du texte � afficher, dans la classe txtStock.
LIST_INFO_MENU_TEXT = (
    ((150,   0           ), "T" , txtStock.CRED_T_BLA,     ),
    (( 90,  30           ), ""  , txtStock.CRED_CLICK,     ),
    (( 30,  60           ), ""  , txtStock.CRED_INDIE,     ),
    ((210,  60           ), "L" , txtStock.CREDL_INDIE,    ),
    (( 30,  80           ), ""  , txtStock.CRED_ULULE,     ),
    ((210,  80           ), "L" , txtStock.CREDL_ULULE,    ),
    (( 30, 100           ), ""  , txtStock.CRED_BLOG,      ),
    ((210, 100           ), "L" , txtStock.CREDL_BLOG,     ),
    (( 30, 120           ), ""  , txtStock.CRED_42,        ),
    ((210, 120           ), "L" , txtStock.CREDL_42,       ),
    (( 30, 140           ), ""  , txtStock.CRED_TWIT,      ),
    ((210, 140           ), "L" , txtStock.CREDL_TWIT,     ),
    ((  2, 200           ), "T" , txtStock.CRED_T_DONAT,   ),
        
    ((120, 230           ), ""  , txtStock.CRED_ST_DONAT1, ),
    (( 65, 250           ), ""  , txtStock.CRED_DONAT_FK,  ),
    ((210, 250           ), "L" , txtStock.CREDL_DONAT_FK, ),
    ((135, 280           ), ""  , txtStock.CRED_ST_DONAT2, ),
    ((170, 300           ), ""  , txtStock.CRED_DONAT_KA,  ),
    ((135, 330           ), ""  , txtStock.CRED_ST_DONAT3, ),
    ((170, 350           ), ""  , txtStock.CRED_DONAT_CU,  ),
    ((175, 370           ), ""  , txtStock.CRED_DONAT_CO,  ),
    (( 95, 390           ), ""  , txtStock.CRED_DONAT_CS,  ),
    ((200, 390           ), "L" , txtStock.CREDL_DONAT_CS, ),
    (( 95, 410           ), ""  , txtStock.CRED_DONAT_CM,  ),
    ((200, 410           ), "L" , txtStock.CREDL_DONAT_CM, ),
    (( 95, 430           ), ""  , txtStock.CRED_DONAT_LA,  ),
    ((200, 430           ), "L" , txtStock.CREDL_DONAT_LA, ),
    
    #Voil�, maintenant on a d�fini tous les donateurs, on peut mettre la suite,
    #� l'ordonn�e que l'on veut.
    (( 50,  20 + DON_BOTT), ""  , txtStock.CRED_YOU,       ),
    (( 80,  80 + DON_BOTT), "T" , txtStock.CRED_T_OTHER,   ),
    (( 20, 110 + DON_BOTT), ""  , txtStock.CRED_YUSU,      ),
    ((200, 110 + DON_BOTT), "L" , txtStock.CREDL_YUSU,     ),
    (( 20, 130 + DON_BOTT), ""  , txtStock.CRED_PYG,       ),
    ((200, 130 + DON_BOTT), "L" , txtStock.CREDL_PYG,      ),    
    ((140, 170 + DON_BOTT), ""  , txtStock.CRED_LIC_1,     ),
    (( 40, 190 + DON_BOTT), ""  , txtStock.CRED_LIC_2,     ),
    (( 80, 210 + DON_BOTT), ""  , txtStock.CRED_LIC_3,     ),
    ((150, 250 + DON_BOTT), ""  , txtStock.CRED_LAL,       ),
    ((140, 270 + DON_BOTT), "L" , txtStock.CREDL_LAL,      ),
    ((110, 310 + DON_BOTT), ""  , txtStock.CRED_CC_1,      ),
    (( 55, 320 + DON_BOTT), ""  , txtStock.CRED_CC_2,      ),
    (( 50, 340 + DON_BOTT), "L" , txtStock.CREDL_CC,       ),
)



class MenuManagerCredits(MenuManager):
    """
    menu affichant le g�n�rique, avec les noms et tout.
    """

    def __init__(self, surfaceDest, dicImg, fontDefault, fontLittle):
        """
        constructeur. (thx captain obvious)

        entr�e :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault, fontLittle : objets pygame.font.Font. les polices de caract�res.
        """
        MenuManager.__init__(self, surfaceDest, dicImg)

        self.fontLittle = fontLittle

        #r�cup�ration des images n�cessaires � ce menu, � partir du gros dico d'images de menu.
        imgScrollUp = self.dicImg[IMG_CRED_SCRL_UP]
        imgScrollown = self.dicImg[IMG_CRED_SCRL_DOWN]
        imgButtonBack = self.dicImg[IMG_BACK]

        # --- Cr�ation des MenuElem de type MenuText, d�finissant le blabla des cr�dits ---

        #liste qui contiendra tous les MenuText du blabla des cr�dits.
        listSubMenuText = []

        for coord, speci, idTxtStock in LIST_INFO_MENU_TEXT:

            coord = pyRectTuple(coord)

            #choix de la police de caract�re, en fonction du type de texte
            if "T" in speci:
                #C'est un titre, on utilise la police par d�faut.
                font = fontDefault
            else:
                #C'est un texte normal, on utilise la police affichant du texte en petit.
                font = fontLittle

            #cr�ation du MenuText en fonction du type de texte
            if "L" in speci:
                #c'est un lien. On cr�e un d�riv�e de MenuText (le MenuLink).
                #On doit passer � cet objet la surface princpale sur laquelle s'affiche le jeu
                #(Car le MenuLink peut changer cette surface, si il a � virer le plein �cran)
                menuElem = MenuLink(coord, font, self.surfaceDest, idTxtStock)
            else:
                #c'est un texte normal. On cr�e un MenuText normal avec les bons params.
                menuElem = MenuText(coord, font, idTxtStock)

            #ajout de l'objet qui vient d'�tre cr��, dans la grande liste.
            listSubMenuText.append(menuElem)

        #tuplifiage de la liste contenant tous les textes, pour acc�l�rer l'ex�cution du code.
        listSubMenuText = tuple(listSubMenuText)

        # --- Cr�ation du SubMenu contenant tous les MenuText du blabla des cr�dits. ---

        #Le SubMenu prend pratiquement tout l'�cran (avec une toute petite marge en haut, et
        #une pas-trop petite marge en bas, pour les boutons).
        param = (pyRect(0, 5, 400, 275), listSubMenuText, (0, 620))
        self.msubCreditsText = MenuSubMenu(*param)

        # --- Cr�ation des boutons ---

        #liste des infos permettant de cr�er les trois boutons.
        #Ce sont des tuples de 4 �l�ments :
        # - coordonn�es du bouton, par rapport � l'�cran.
        # - image � utiliser pour le bouton
        # - funcAction � lier � ce bouton
        # - type d'activation. (un identifiant MOUSE_* tel que d�fini dans menusesq.py)
        listInfoButton = (((  0,   0), imgScrollUp,
                           self.mactScrollTextUp,   MOUSE_HOVER),

                          (( 30, 280), imgScrollown,
                           self.mactScrollTextDown, MOUSE_HOVER),

                          ((  0, 280), imgButtonBack,
                           mactQuit,                MOUSE_DOWN),
                         )

        #cr�ation d'une liste contenant les trois boutons, en fonction des infos ci-dessus.
        listMenuButImg = [
            #le 0 en dernier param, c'est le inflateDist. La zone de sensibilit�
            #aux clics est �gale � la zone de dessin. Pas de marge. Car ces
            #boutons sont des MOUSE_HOVER. (Bon, pas tous, mais osef).
            MenuSensitiveImage(pyRectTuple(coord), img, func, clickType, 0)
            for coord, img, func, clickType
            in listInfoButton
        ]

        # --- Rangement de tous les MenuElem cr��s, dans la grande liste globale. ---

        #on commence par cr�er une liste de liste, car on fait avec ce qu'on a.
        #(on ne met pas la liste de tous les MenuText pr�c�demment cr��s. On met le SubMenu
        #contenant tous ces MenuText).
        listOfListMenuElem = (tuple(listMenuButImg),
                              #ne pas oublier le petit MenuElem invisible qui sert juste �
                              #binder la touche esc sur la fonction de quittage de menu.
                              (mkeyQuitEsc, self.msubCreditsText, ))

        #et maintenant, on fait une grande liste "aplatie", en concat�nant toutes les sous-liste.
        self.listMenuElem = addThings(*listOfListMenuElem)

        self.initFocusCyclingInfo()


    def periodicAction(self):
        """
        fonction du menu effectuant une action p�riodique. (Voir description dans MenuManager)
        """

        #on utilise cette fonction pour g�rer le scrolling en continu, tant que le joueur
        #reste appuy� sur la fl�che du haut ou la fl�che du bas. C'est un peu moche de
        #metttre �a ici, mais j'ai pas eu d'autres id�es de mettage ailleurs.

        ihmsgInfo = IHMSG_VOID

        #on scrolle un petit peu vers le bas, si la touche de fl�che du bas est appuy�e
        if self.dictKeyPressed[pygl.K_DOWN]:
            ihmsgInfo += self.mactScrollTextDown()

        #pareil avec le haut.
        if self.dictKeyPressed[pygl.K_UP]:
            ihmsgInfo += self.mactScrollTextUp()

        #fun fact : si le joueur appuie en m�me temps sur la fl�che du haut et la fl�che du
        #bas, les deux scrollings sont effectu�s, mais ils s'annulent, et on ne voit rien
        #qui bouge � l'�cran. Osef oui, certes.

        #renvoi du tuple contenant les messages d'IHM. (Y'a soit une demande de redraw, soit rien)
        return ihmsgInfo


    def startMenu(self):
        """
        fonction qui s'ex�cute au d�but de l'activation du menu
        (voir description de la fonction dans la classe-m�re)
        """
        #on remet le scrolling � la position tout en haut. (Y = 0)
        self.msubCreditsText.scrollSetPosition()


    def mactScrollTextDown(self):
        """
        fonction appel�e quand on clique sur le bouton de scroll vers le bas, ou qu'on appuie
        sur la touche de fl�che du bas.
        Elle est appel�e p�riodiquement si on reste cliqu� / appuy� sur la touche.
        fun fact : elle est appel�e deux fois si on clique et que on appuie sur la touche.
        Du coup, �a fait scroller deux fois plus vite. Hu hu hu !
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        #on fait d�filer le subMenu un tout petit peu vers le bas.
        #concr�tement, on remonte vers le haut la zone d'affichage du SubMenu. Ce qui donne
        #l'impression que le contenu d�file vers le bas. Bon, osef.
        self.msubCreditsText.scrollVertically(+8)
        return (IHMSG_REDRAW_MENU, )


    def mactScrollTextUp(self):
        """
        voir fonction mactScrollTextDown, en rempla�ant les mots "bas" par "haut" et vice-versa.
        """
        self.msubCreditsText.scrollVertically(-8)
        return (IHMSG_REDRAW_MENU, )
