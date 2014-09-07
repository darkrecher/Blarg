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

date de la dernière relecture-commentage : 24/02/2010

Element de menu qui réagit à un appuyage de touche.
Mais ça réagit PAS à un lâchage de touche, ni à une touche déjà appuyée.
Parce que j'avais pas envie de le faire et/ou que je l'ai géré autrement. Na !

"""

import pygame
from common   import IHMSG_VOID
from menuelem import MenuElem



class MenuSensitiveKey(MenuElem):
    """
    blabla. Appuyage de touche.
    """

    def __init__(self, funcAction, stimKey):
        """
        constructeur. (thx captain obvious)

        entrée :
            funcAction : référence vers la fonction à exécuter quand ce menuElem est activé.
                (c.à.d. quand le joueur appuira sur la touche associée à ce menuSensitiveKey.)

            stimKey : identifiant de la touche à laquelle il faut réagir. "How do you react ?"
                      on utilise les identifiants de pygame.locals : K_xxx
        """

        #init de la mother-classe. mother-fucker !!
        MenuElem.__init__(self)

        self.funcAction = funcAction
        self.stimKey = stimKey


    def takeStimuliKeys(self, dictKeyPressed, keyCodeDown, keyCharDown):
        """
        prise en compte des touches appuyées par le joueur.
        (voir description dans la classe MenuElem)
        """

        #On teste si la touche requise est appuyée.
        if keyCodeDown == self.stimKey:
            #Ca correspond. donc il faut exécuter la fonction pointée par funcAction,
            #et renvoyer le ihmsgInfo de cette fonction, tel quel.
            return self.funcAction()

        #Sinon, on branle rien. Et on renvoie un ihmsgInfo vide.
        return IHMSG_VOID
