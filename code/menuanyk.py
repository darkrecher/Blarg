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

date de la dernière relecture-commentage : 24/02/2011

Element de menu qui réagit à un appuyage de touche et/ou un clic de bouton de souris.
Mais n'importe quelle touche/bouton.
C'est de l'appuyage KEY_DOWN, obligatoirement. Pas de KEY_PRESSED.
Pis pour les bouton c'est aussi que du MOUSE_DOWN, pas de MOUSE_PRESSED (pasque j'avais envie)
"""

import pygame
from common   import IHMSG_VOID
from menuelem import MenuElem



class MenuSensitiveAnyKeyButton(MenuElem):
    """
    voili voilà, voyez.
    """

    def __init__(self, funcAction, sensiKeys=True, sensiMouseClick=True):
        """
        constructeur. (thx captain obvious)

        entrée :
            funcAction : référence vers la fonction à exécuter quand ce MenuElem est activé.
                (C'est à dire quand le joueur appuie sur une touche, ou clique)

            sensiKeys : booléen. Indique si ce MenuElem réagit aux touches, ou pas

            sensiMouseClick : booléen. Indique si il réagit aux clics gauche, ou pas.
        """

        #init de la mother-classe. mother-fucker !!
        MenuElem.__init__(self)

        self.funcAction = funcAction
        self.sensiKeys = sensiKeys
        self.sensiMouseClick = sensiMouseClick


    def takeStimuliKeys(self, dictKeyPressed, keyCodeDown, keyCharDown):
        """
        prise en compte des touches appuyées par le joueur.
        (voir description dans la classe MenuElem)
        """

        #On est sensible aux appuyages de touches. N'importe lesquels.
        #Donc faut exécuter la fonction pointée par funcAction,
        #et propager les messages d'ihm renvoyés par cette fonction, tel quel.
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
        #Donc faut exécuter la fonction pointée par funcAction,
        #et propager les messages d'ihm renvoyés par cette fonction, tel quel.
        if self.sensiMouseClick and mouseDown:
            return self.funcAction()

        #Sinon, on branle rien. Et on renvoie un ihmsgInfo vide.
        return IHMSG_VOID
