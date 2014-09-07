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

date de la dernière relecture-commentage : 17/02/2011

le fichier de code principal avec pas grand chose dedans, mais c'est cool.

remarques générales sur la généralité de mon code :

Les lignes de code ne dépassent jamais 80 caractères
Les lignes de commentaire ne dépassent jamais 100 caractères.
Ouais c'est bizarre. Mais j'avais envie.

Quand je met le mot-clé "TRODO", c'est pour dire que y'a un truc à faire, mais je le ferais 
plus tard (ou jamais). Normalement on dit "TODO" pour faire genre ouais je suis anglais. Mais
moi j'avais envie d'un autre mot. Et puis ça fait "trou doux".

Pour définir des coordonnées, utiliser tout le temps des rect, avec width et height à 0
et pas des tuple (X,Y). car y'a plein de fonctions cools avec les rects.
Pour créer un rect avec que le X, Y, sans être obligé d'écrire les putains de 0 des sizes,
utiliser ma fonction common.pyRect. Et y'a un common.pyRectTuple aussi
"""

import sys
import pygame

from common import securedPrint
from mainclas import MainClass

#paramètre à passer à la ligne de commande, permettant de lancer le jeu en mode fenêtre.
#Car le mode plein écran déconne parfois sur PC, avec certaines config.
PARAM_FORCE_WINDOWED_MODE = "FORCE_WINDOWED"

# --- programme principal. ---
#tiens elle sert à rien la ligne ci-dessus. On le voit bien que c'est le programme principal.

if __name__ == "__main__":

    securedPrint("coucou")

    #Récupération éventuelle du paramètre, pour savoir si on doit se mettre en mode fenêtre.
    if len(sys.argv) > 1 and sys.argv[1] == PARAM_FORCE_WINDOWED_MODE:
        forceWindowed = True
    else:
        forceWindowed = False

    pygame.init()

    #création de la putain de classe qui contient tout le putain de code, et les
    #putains d'initialisations.
    theFuckingMainClass = MainClass(forceWindowed)

    #lancement du putain de code de la putain de classe qui va exécuter le putain de jeu.
    theFuckingMainClass.main()

    pygame.quit()

    securedPrint("tchaw")
