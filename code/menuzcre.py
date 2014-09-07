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

Menu affichant les crédits. La liste des contributeurs, la licence, etc.
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


#abréviation de DONATORS_BOTTOM. (non, ça veut pas dire "le cul des donateurs")
#position Y des textes situés après la liste des donateurs. (Je l'ai mis dans
#une variable car la liste des donateurs n'est pas encore figée).
DON_BOTT = 460

#liste de tuple regroupant les infos des MenuText affichant les textes des crédits.
#les tuples contiennent 3 éléments :
#
# - coordonnées du MenuText dans le gigantesque SubMenu affichant tous les crédits.
#
# - string regroupant les caractéristiques du MenuText :
#   . "T" : Le MenuText est un titre, faut utiliser la font standard, et non pas
#           la font affichant le texte en petit.
#   . "L" : Le MenuText est un lien internet. (L'adresse du lien, c'est le texte).
#   . A priori, on pourrait mettre le "T" et le "L" en même temps, mais j'ai pas essayé.
#   C'est un peu pourri d'avoir mis ça sous forme de string, au lieu de constantes
#   avec un nom plus explicite. Mais je voulait une écriture compacte.
#
# - identifiant du texte à afficher, dans la classe txtStock.
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
    
    #Voilà, maintenant on a défini tous les donateurs, on peut mettre la suite,
    #à l'ordonnée que l'on veut.
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
    menu affichant le générique, avec les noms et tout.
    """

    def __init__(self, surfaceDest, dicImg, fontDefault, fontLittle):
        """
        constructeur. (thx captain obvious)

        entrée :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault, fontLittle : objets pygame.font.Font. les polices de caractères.
        """
        MenuManager.__init__(self, surfaceDest, dicImg)

        self.fontLittle = fontLittle

        #récupération des images nécessaires à ce menu, à partir du gros dico d'images de menu.
        imgScrollUp = self.dicImg[IMG_CRED_SCRL_UP]
        imgScrollown = self.dicImg[IMG_CRED_SCRL_DOWN]
        imgButtonBack = self.dicImg[IMG_BACK]

        # --- Création des MenuElem de type MenuText, définissant le blabla des crédits ---

        #liste qui contiendra tous les MenuText du blabla des crédits.
        listSubMenuText = []

        for coord, speci, idTxtStock in LIST_INFO_MENU_TEXT:

            coord = pyRectTuple(coord)

            #choix de la police de caractère, en fonction du type de texte
            if "T" in speci:
                #C'est un titre, on utilise la police par défaut.
                font = fontDefault
            else:
                #C'est un texte normal, on utilise la police affichant du texte en petit.
                font = fontLittle

            #création du MenuText en fonction du type de texte
            if "L" in speci:
                #c'est un lien. On crée un dérivée de MenuText (le MenuLink).
                #On doit passer à cet objet la surface princpale sur laquelle s'affiche le jeu
                #(Car le MenuLink peut changer cette surface, si il a à virer le plein écran)
                menuElem = MenuLink(coord, font, self.surfaceDest, idTxtStock)
            else:
                #c'est un texte normal. On crée un MenuText normal avec les bons params.
                menuElem = MenuText(coord, font, idTxtStock)

            #ajout de l'objet qui vient d'être créé, dans la grande liste.
            listSubMenuText.append(menuElem)

        #tuplifiage de la liste contenant tous les textes, pour accélérer l'exécution du code.
        listSubMenuText = tuple(listSubMenuText)

        # --- Création du SubMenu contenant tous les MenuText du blabla des crédits. ---

        #Le SubMenu prend pratiquement tout l'écran (avec une toute petite marge en haut, et
        #une pas-trop petite marge en bas, pour les boutons).
        param = (pyRect(0, 5, 400, 275), listSubMenuText, (0, 620))
        self.msubCreditsText = MenuSubMenu(*param)

        # --- Création des boutons ---

        #liste des infos permettant de créer les trois boutons.
        #Ce sont des tuples de 4 éléments :
        # - coordonnées du bouton, par rapport à l'écran.
        # - image à utiliser pour le bouton
        # - funcAction à lier à ce bouton
        # - type d'activation. (un identifiant MOUSE_* tel que défini dans menusesq.py)
        listInfoButton = (((  0,   0), imgScrollUp,
                           self.mactScrollTextUp,   MOUSE_HOVER),

                          (( 30, 280), imgScrollown,
                           self.mactScrollTextDown, MOUSE_HOVER),

                          ((  0, 280), imgButtonBack,
                           mactQuit,                MOUSE_DOWN),
                         )

        #création d'une liste contenant les trois boutons, en fonction des infos ci-dessus.
        listMenuButImg = [
            #le 0 en dernier param, c'est le inflateDist. La zone de sensibilité
            #aux clics est égale à la zone de dessin. Pas de marge. Car ces
            #boutons sont des MOUSE_HOVER. (Bon, pas tous, mais osef).
            MenuSensitiveImage(pyRectTuple(coord), img, func, clickType, 0)
            for coord, img, func, clickType
            in listInfoButton
        ]

        # --- Rangement de tous les MenuElem créés, dans la grande liste globale. ---

        #on commence par créer une liste de liste, car on fait avec ce qu'on a.
        #(on ne met pas la liste de tous les MenuText précédemment créés. On met le SubMenu
        #contenant tous ces MenuText).
        listOfListMenuElem = (tuple(listMenuButImg),
                              #ne pas oublier le petit MenuElem invisible qui sert juste à
                              #binder la touche esc sur la fonction de quittage de menu.
                              (mkeyQuitEsc, self.msubCreditsText, ))

        #et maintenant, on fait une grande liste "aplatie", en concaténant toutes les sous-liste.
        self.listMenuElem = addThings(*listOfListMenuElem)

        self.initFocusCyclingInfo()


    def periodicAction(self):
        """
        fonction du menu effectuant une action périodique. (Voir description dans MenuManager)
        """

        #on utilise cette fonction pour gérer le scrolling en continu, tant que le joueur
        #reste appuyé sur la flèche du haut ou la flèche du bas. C'est un peu moche de
        #metttre ça ici, mais j'ai pas eu d'autres idées de mettage ailleurs.

        ihmsgInfo = IHMSG_VOID

        #on scrolle un petit peu vers le bas, si la touche de flèche du bas est appuyée
        if self.dictKeyPressed[pygl.K_DOWN]:
            ihmsgInfo += self.mactScrollTextDown()

        #pareil avec le haut.
        if self.dictKeyPressed[pygl.K_UP]:
            ihmsgInfo += self.mactScrollTextUp()

        #fun fact : si le joueur appuie en même temps sur la flèche du haut et la flèche du
        #bas, les deux scrollings sont effectués, mais ils s'annulent, et on ne voit rien
        #qui bouge à l'écran. Osef oui, certes.

        #renvoi du tuple contenant les messages d'IHM. (Y'a soit une demande de redraw, soit rien)
        return ihmsgInfo


    def startMenu(self):
        """
        fonction qui s'exécute au début de l'activation du menu
        (voir description de la fonction dans la classe-mère)
        """
        #on remet le scrolling à la position tout en haut. (Y = 0)
        self.msubCreditsText.scrollSetPosition()


    def mactScrollTextDown(self):
        """
        fonction appelée quand on clique sur le bouton de scroll vers le bas, ou qu'on appuie
        sur la touche de flèche du bas.
        Elle est appelée périodiquement si on reste cliqué / appuyé sur la touche.
        fun fact : elle est appelée deux fois si on clique et que on appuie sur la touche.
        Du coup, ça fait scroller deux fois plus vite. Hu hu hu !
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        #on fait défiler le subMenu un tout petit peu vers le bas.
        #concrètement, on remonte vers le haut la zone d'affichage du SubMenu. Ce qui donne
        #l'impression que le contenu défile vers le bas. Bon, osef.
        self.msubCreditsText.scrollVertically(+8)
        return (IHMSG_REDRAW_MENU, )


    def mactScrollTextUp(self):
        """
        voir fonction mactScrollTextDown, en remplaçant les mots "bas" par "haut" et vice-versa.
        """
        self.msubCreditsText.scrollVertically(-8)
        return (IHMSG_REDRAW_MENU, )
