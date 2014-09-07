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

date de la dernière relecture-commentage : 21/03/2011

Menu utilisé pour la présentation au début. Il affiche que d'alle, et attend qu'on appuie sur une
touche ou qu'on clique pour se quitter. Si le joueur ne fait rien , le menu se quitte tout seul au
bout d'un certain temps.
"""

import pygame

from common   import IHMSG_QUIT, IHMSG_VOID
from menucomn import manyQuit
from menumng  import MenuManager



class MenuManagerWaitOrPressAnyKey(MenuManager):

    """
    menu qui fait rien et qu'attend. Et qui quitte au bout d'un moment.
    """
    def __init__(self, surfaceDest, waitLimit):
        """
        constructeur. (thx captain obvious)

        entrée :

            surfaceDest : voir constructeur de MenuManager. (Pour ce MenuManager,
                je me sers pas de cette surface. Mais le param est obligatoire).
                J'ai pas voulu le rendre facultatif, car il est passé aux MenuElem internes,
                et tout ça. Ca marcherait si on colle None dans ce param, et qu'il n'y a
                pas d'images de fond, et pas de MenuElem affichant quelque chose. Donc ça
                marcherait pour ce menu en particulier. Mais je veux pas prendre le risque.
                La robustesse, c'est mieux.

            waitLimit : int. Nombre de cycle à attendre avant de quitter automatiquement le menu.
        """

        #on passe pas le dicImg, donc le menu ne peut pas choper l'image de
        #fond par défaut, donc il affiche pas d'image de fond. C'est ce que je veux.
        #Parce qu'en fait l'image de présentation est déjà affichée à l'écran. On n'y touche pas.
        MenuManager.__init__(self, surfaceDest)

        self.waitLimit = waitLimit
        #Compteur de nombre de cycle, avant d'atteindre la waitLimit et de quitter.
        self.waitCounter = 0

        #Y'a qu'un seul MenuElem, et il affiche rien. C'est le MenuElem qui fait quitter le
        #menu en cours dès qu'on appuie sur une touche (n'importe laquelle), ou qu'on clique.
        self.listMenuElem = (manyQuit, )


    def periodicAction(self):
        """
        Fonction périodique, qui s'exécute à chaque cycle.
        (voir description de la fonction dans MenuManager)
        """

        #augmentation du compteur. Oui, captain obvious.
        self.waitCounter += 1

        #Si on a compté jusqu'à la fin, on envoie le message d'ihm de quittage du menu en cours.
        if self.waitCounter >= self.waitLimit:
            return (IHMSG_QUIT, )

        #Sinon, ben y'a rien à branler
        return IHMSG_VOID

