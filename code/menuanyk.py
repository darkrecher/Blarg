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

date de la derni�re relecture-commentage : 24/02/2011

Element de menu qui r�agit � un appuyage de touche et/ou un clic de bouton de souris.
Mais n'importe quelle touche/bouton.
C'est de l'appuyage KEY_DOWN, obligatoirement. Pas de KEY_PRESSED.
Pis pour les bouton c'est aussi que du MOUSE_DOWN, pas de MOUSE_PRESSED (pasque j'avais envie)
"""

import pygame
from common   import IHMSG_VOID
from menuelem import MenuElem



class MenuSensitiveAnyKeyButton(MenuElem):
    """
    voili voil�, voyez.
    """

    def __init__(self, funcAction, sensiKeys=True, sensiMouseClick=True):
        """
        constructeur. (thx captain obvious)

        entr�e :
            funcAction : r�f�rence vers la fonction � ex�cuter quand ce MenuElem est activ�.
                (C'est � dire quand le joueur appuie sur une touche, ou clique)

            sensiKeys : bool�en. Indique si ce MenuElem r�agit aux touches, ou pas

            sensiMouseClick : bool�en. Indique si il r�agit aux clics gauche, ou pas.
        """

        #init de la mother-classe. mother-fucker !!
        MenuElem.__init__(self)

        self.funcAction = funcAction
        self.sensiKeys = sensiKeys
        self.sensiMouseClick = sensiMouseClick


    def takeStimuliKeys(self, dictKeyPressed, keyCodeDown, keyCharDown):
        """
        prise en compte des touches appuy�es par le joueur.
        (voir description dans la classe MenuElem)
        """

        #On est sensible aux appuyages de touches. N'importe lesquels.
        #Donc faut ex�cuter la fonction point�e par funcAction,
        #et propager les messages d'ihm renvoy�s par cette fonction, tel quel.
        if self.sensiKeys:
            return self.funcAction()

        #Sinon, on branle rien. Et on renvoie un ihmsgInfo vide.
        return IHMSG_VOID


    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        prise en compte des mouvements et des clics de souris.
        (voir description dans la classe MenuElem)
        """

        #On est sensible aux clics gauche, et justement, le joueur a fait un clic gauche,
        #Donc faut ex�cuter la fonction point�e par funcAction,
        #et propager les messages d'ihm renvoy�s par cette fonction, tel quel.
        if self.sensiMouseClick and mouseDown:
            return self.funcAction()

        #Sinon, on branle rien. Et on renvoie un ihmsgInfo vide.
        return IHMSG_VOID
