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

date de la dernière relecture-commentage : 17/03/2011

Menu qui s'active que au premier lancement du jeu, et qui demande au joueur d'entrer son nom.
"""

import pygame
import pygame.locals
pygl = pygame.locals

from common import (pyRect, NAME_HERO,
                    IHMSG_REDRAW_MENU, IHMSG_QUIT, IHMSG_CANCEL)

from menucomn import mkeyQuitEsc, IMG_FRAME_NAME, IMG_BUTT_OK
from txtstock import txtStock
from menukey  import MenuSensitiveKey
from menutxt  import MenuText
from menuimg  import MenuImage
from menuseim import MenuSensitiveImage
from menumng  import MenuManager
from menuedtx import MenuEditableText



class MenuManagerEnterName(MenuManager):
    """
    menu pour que le joueur entre son nom. Yay !
    """

    def __init__(self, surfaceDest, dicImg, fontDefault):
        """
        constructeur. (thx captain obvious)

        entrée :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault : objet pygame.font.Font. police de caractères par défaut.
        """

        MenuManager.__init__(self, surfaceDest, dicImg)

        self.fontDefault = fontDefault

        imgFrame = self.dicImg[IMG_FRAME_NAME]
        imgButtonOK = self.dicImg[IMG_BUTT_OK]

        # --- Création des éléments du menu ---

        #image statique de l'espèce de fenêtre qu'on fout au milieu de l'écran.
        #mimgFrameName, ça veut dire : l'image de la Frame pour saisir le Name.
        #Et non pas : l'image du nom de la frame. Parce que ça voudrait rien dire. OK put'neg' ?
        mimgFrameName = MenuImage(pyRect(100, 110), imgFrame)

        #création du texte statique demandant au joueur de saisir son nom.
        param = (pyRect(120, 115), self.fontDefault, txtStock.ENTER_NAME)
        mtxtEnterName = MenuText(*param)

        #création du bouton OK. Alors ce bouton, c'est juste une image (de bouton),
        #avec le mot "OK" écrit dessus. Le texte est vraiment en dur de dur.
        #C'est crado, je reconnais. Heureusement que "OK" c'est aussi bien anglais que français.
        param = (pyRect(185, 170), imgButtonOK, self.mactOK)
        mbutiOK = MenuSensitiveImage(*param)

        #Création du MenuElem permettant de saisir une chaîne de caractère (le nom du joueur).
        #La zone de saisie est initalisée avec le nom "officiel" du héros.
        #rah, j'aime pas cette formulation. Tous les param sont coincés à droite, et ça
        #prend plein de ligne pour que d'alle. Mais je peux pas faire ma bidouille de *param,
        #car y'en a qui sont nommé. Ou alors avec un dict mais ça devient vraiment lourd
        #TRODO : au fait c'est bien ou mal, cette écriture *param ? Je l'ai fait partout...
        self.meditPlayerName = MenuEditableText(pyRect(120, 140, 160, 20),
                                                self.fontDefault,
                                                text=NAME_HERO,
                                                maxNbrChar=15)

        #création des menuElem liant des touches à des fonctions.

        #liaisonnage des deuc touches entrée à la fonction de validation du nom.
        #(C'est la même fonction que celle qui est liée à l'appui sur le bouton "OK")
        mkeyEnterOK_1 = MenuSensitiveKey(self.mactOK, pygl.K_RETURN)
        mkeyEnterOK_2 = MenuSensitiveKey(self.mactOK, pygl.K_KP_ENTER)

        #liaisonnage de la fonction de quittage à la touche Escape.
        #(C'est pas le quittage classique. Voir description de la fonction mactQuitCancel
        mkeyQuitCancel = MenuSensitiveKey(self.mactQuitCancel, pygl.K_ESCAPE)

        # --- Rangement de tous les MenuElem créés, dans la grande liste globale. ---

        #pas besoin de faire une liste de liste comme dans d'autres MenuManager.
        #Tous les MenuElem qu'on a créé l'ont été de manière individuelle.
        #Y'a juste à les mettre bout à bout dans la liste et voilà.
        self.listMenuElem = (mimgFrameName, mtxtEnterName,
                             self.meditPlayerName, mbutiOK,
                             mkeyQuitCancel, mkeyEnterOK_1, mkeyEnterOK_2)

        #j'indique 2 en paramètre, pour que le focus se mette initialement sur
        #le MenuElem numéro 2 de la liste. C'est à dire la zone de saisie du nom du joueur.
        self.initFocusCyclingInfo(2)


    def mactOK(self):
        """
        fonction qui s'exécute quand on appuie sur le bouton OK, ou sur une touche Entrée.
        Si le joueur n'a pas saisi de nom, faut rien faire. (Et il a qu'à piger tout seul
        qu'il faut qu'il saisisse un nom, ce con.).
        Si le joueur a saisi un nom, faut quitter le menu, pour passer à la suite.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #récupération du nom saisi dans la zone de texte.
        self.nameTyped = self.meditPlayerName.theLamoche.text

        if self.nameTyped != "":
            #Le nom n'est pas vide. C'est cool. On quitte le menu. (Le code extérieur
            #s'occupe de récupérer ce nom pour en faire tout un tas de chouettes trucs avec).
            return (IHMSG_QUIT, )
        else:
            #Le nom est vide. On se contente de redessiner le menu. Il ne se passe rien de plus.
            #(Et si ça se trouve, c'est même pas la peine d'envoyer le message de redraw. boarf)
            return (IHMSG_REDRAW_MENU, )


    def mactQuitCancel(self):
        """
        fonction qui s'exécute lorsqu'on appuie sur Esc.
        Il faut quitter le menu, mais également quitter tout le jeu.
        Si le joueur appuie sur Esc à cette étape du jeu (alors que c'est le début), on considère
        que c'est parce qu'il ne veut plus jouer (dommage, c'est triste). Donc on quitte
        directement, sans prendre en compte le nom saisi, et sans l'enregistrer où que ce soye.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #Donc faut quitter le menu, d'où le IHMSG_QUIT.
        #Et il faut aussi indiquer au code extérieur que le joueur ne veut plus joueur.
        #Donc on rajoute le IHMSG_CANCEL. Le code extérieur s'occupera de détecter la présence
        #de ce message dans le tuple, et d'agir en conséquence, en quittant tout le jeu.
        #(Un peu comme Jospin, le "parti socialiste". (Le socialiste qui est parti)).
        return (IHMSG_QUIT, IHMSG_CANCEL)


