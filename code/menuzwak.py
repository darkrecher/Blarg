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

Menu utilis� pour la pr�sentation au d�but. Il affiche que d'alle, et attend qu'on appuie sur une
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

        entr�e :

            surfaceDest : voir constructeur de MenuManager. (Pour ce MenuManager,
                je me sers pas de cette surface. Mais le param est obligatoire).
                J'ai pas voulu le rendre facultatif, car il est pass� aux MenuElem internes,
                et tout �a. Ca marcherait si on colle None dans ce param, et qu'il n'y a
                pas d'images de fond, et pas de MenuElem affichant quelque chose. Donc �a
                marcherait pour ce menu en particulier. Mais je veux pas prendre le risque.
                La robustesse, c'est mieux.

            waitLimit : int. Nombre de cycle � attendre avant de quitter automatiquement le menu.
        """

        #on passe pas le dicImg, donc le menu ne peut pas choper l'image de
        #fond par d�faut, donc il affiche pas d'image de fond. C'est ce que je veux.
        #Parce qu'en fait l'image de pr�sentation est d�j� affich�e � l'�cran. On n'y touche pas.
        MenuManager.__init__(self, surfaceDest)

        self.waitLimit = waitLimit
        #Compteur de nombre de cycle, avant d'atteindre la waitLimit et de quitter.
        self.waitCounter = 0

        #Y'a qu'un seul MenuElem, et il affiche rien. C'est le MenuElem qui fait quitter le
        #menu en cours d�s qu'on appuie sur une touche (n'importe laquelle), ou qu'on clique.
        self.listMenuElem = (manyQuit, )


    def periodicAction(self):
        """
        Fonction p�riodique, qui s'ex�cute � chaque cycle.
        (voir description de la fonction dans MenuManager)
        """

        #augmentation du compteur. Oui, captain obvious.
        self.waitCounter += 1

        #Si on a compt� jusqu'� la fin, on envoie le message d'ihm de quittage du menu en cours.
        if self.waitCounter >= self.waitLimit:
            return (IHMSG_QUIT, )

        #Sinon, ben y'a rien � branler
        return IHMSG_VOID

