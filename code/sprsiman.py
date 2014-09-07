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

date de la dernère relecture-commentage : 15/10/2010

Simple Sprite Manager
Classe à la con, qui gère un group de SpriteSimple. Elle exécute leurs update,
Et les détruit si besoin.

C'est elle qui s'occupe de créer les SpriteSimple qu'elle gère.
Mais il faut lui filer toutes les caractéristiques du sprite,
qu'elle transmet tels quels à sa fonction constructeur __init__
(J'ai jamais su comment accorder ce putain de "tel quel", alors que je l'utilise tout le temps.
Fait chier. Puisque c'est ça, je dirais "teckel" maintenant)
"""

import pygame

from common import pyRect, NONE_COUNT

#yeaaahh !!! je viens de m'apercevoir que pour éviter d'écrire les antislash de fin de ligne
#de mes couilles, il suffit d'écrire l'import entre parenthèses. Ha ha, ça méritera au moins
#un article dans mon blog ça.
from sprsimpl import (IMG_LOOP_ETERNAL,
                      END_ON_IMG_LOOP, END_ON_OUT_GAME_AREA, END_NEVER,
                      SPRITE_ALIVE, SPRITE_DEAD,
                      SpriteSimple)


#héritage d'un spriteGroup ? Au lieu de mettre le spriteGroup à l'intérieur ?
#Nan je pense pas. Parce que la classe se permet d'ajouter/supprimer d'elle-même des
#sprites du group. Donc elle gère un group. Elle "n'est pas" un group.
class SpriteSimpleManager():
    """
    Je sais jamais quoi dire ici.
    """

    def __init__(self, allSprites):
        """
        constructeur. (thx captain obvious)

        entrées :
         - allSprites : Group de sprite, qui contient tous les sprites du jeu.
                        Il faut mettre les SpriteSimple dedans.
        """

        self.allSprites = allSprites

        #ça c'est le groupe de sprite qui contient juste les SpriteSimple.
        #on s'en sert juste comme d'une liste de Sprite, (ajouts/suppr/parcourage)
        self.simpleSpriteGroup = pygame.sprite.Group()


    def addSpriteSimple(self, listImgInfo, posStart,
                        nbrImgLoop=IMG_LOOP_ETERNAL,
                        endCondition=END_ON_OUT_GAME_AREA,
                        moveRect=pyRect(), movePeriod=NONE_COUNT,
                        accelRect=pyRect(), accelPeriod=NONE_COUNT,
                        makeDecalCenter=False):
        """
        fonction pour ajouter un SpriteSimple dans le SpriteSimpleManager.

        entrées : voir fonction SpriteSimple.__init__
                  c'est le même bazar.

        plat-dessert : le spriteSimple généré.
        """

        #création du nouveau SpriteSimple, en transmettant les paramètres, juste paf comme ça.
        paramSprite = (listImgInfo, posStart, nbrImgLoop, endCondition,
                       moveRect, movePeriod, accelRect, accelPeriod,
                       makeDecalCenter)

        spriteSimple = SpriteSimple(*paramSprite)

        #ajout du nouveau sprite dans le gros groupe global allSprites, et dans le petit
        #groupe personnel du SpriteSimpleManager.
        self.allSprites.add(spriteSimple)
        self.simpleSpriteGroup.add(spriteSimple)

        #on renvoie le spriteSimple généré, ça peut éventuellement servir pour le code extérieur
        return spriteSimple


    def updateAndRemoveSprites(self):
        """
        exécute la fonction update sur tous les SimpleSprite,
        supprime les SimpleSprite qui doivent crever.
        """

        #update puis remove, ou remove puis update ? Wat is the best ?
        #Je ne sais pas, et osef. update puis remove me semble le plus optimisé.
        #Comme ça, on se traine pas des sprite morts pendant un cycle de plus.

        for sprite in self.simpleSpriteGroup:
            sprite.update()

        #on récupère la liste des SpriteSimple ayant leur état à SPRITE_DEAD.
        #C'est à dire la liste des SpriteSimple à supprimer.
        listSpriteToRemove = [ sprite for sprite in self.simpleSpriteGroup
                               if sprite.currentState == SPRITE_DEAD ]

        #on enlève les SpriteSimple des deux groups de sprites.
        #Et après ils se détruiront tout seul, car ils ont plus de référence. Youpi !!
        for sprite in listSpriteToRemove:
            self.allSprites.remove(sprite)
            self.simpleSpriteGroup.remove(sprite)

