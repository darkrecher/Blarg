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

date de la dern�re relecture-commentage : 15/10/2010

Simple Sprite Manager
Classe � la con, qui g�re un group de SpriteSimple. Elle ex�cute leurs update,
Et les d�truit si besoin.

C'est elle qui s'occupe de cr�er les SpriteSimple qu'elle g�re.
Mais il faut lui filer toutes les caract�ristiques du sprite,
qu'elle transmet tels quels � sa fonction constructeur __init__
(J'ai jamais su comment accorder ce putain de "tel quel", alors que je l'utilise tout le temps.
Fait chier. Puisque c'est �a, je dirais "teckel" maintenant)
"""

import pygame

from common import pyRect, NONE_COUNT

#yeaaahh !!! je viens de m'apercevoir que pour �viter d'�crire les antislash de fin de ligne
#de mes couilles, il suffit d'�crire l'import entre parenth�ses. Ha ha, �a m�ritera au moins
#un article dans mon blog �a.
from sprsimpl import (IMG_LOOP_ETERNAL,
                      END_ON_IMG_LOOP, END_ON_OUT_GAME_AREA, END_NEVER,
                      SPRITE_ALIVE, SPRITE_DEAD,
                      SpriteSimple)


#h�ritage d'un spriteGroup ? Au lieu de mettre le spriteGroup � l'int�rieur ?
#Nan je pense pas. Parce que la classe se permet d'ajouter/supprimer d'elle-m�me des
#sprites du group. Donc elle g�re un group. Elle "n'est pas" un group.
class SpriteSimpleManager():
    """
    Je sais jamais quoi dire ici.
    """

    def __init__(self, allSprites):
        """
        constructeur. (thx captain obvious)

        entr�es :
         - allSprites : Group de sprite, qui contient tous les sprites du jeu.
                        Il faut mettre les SpriteSimple dedans.
        """

        self.allSprites = allSprites

        #�a c'est le groupe de sprite qui contient juste les SpriteSimple.
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

        entr�es : voir fonction SpriteSimple.__init__
                  c'est le m�me bazar.

        plat-dessert : le spriteSimple g�n�r�.
        """

        #cr�ation du nouveau SpriteSimple, en transmettant les param�tres, juste paf comme �a.
        paramSprite = (listImgInfo, posStart, nbrImgLoop, endCondition,
                       moveRect, movePeriod, accelRect, accelPeriod,
                       makeDecalCenter)

        spriteSimple = SpriteSimple(*paramSprite)

        #ajout du nouveau sprite dans le gros groupe global allSprites, et dans le petit
        #groupe personnel du SpriteSimpleManager.
        self.allSprites.add(spriteSimple)
        self.simpleSpriteGroup.add(spriteSimple)

        #on renvoie le spriteSimple g�n�r�, �a peut �ventuellement servir pour le code ext�rieur
        return spriteSimple


    def updateAndRemoveSprites(self):
        """
        ex�cute la fonction update sur tous les SimpleSprite,
        supprime les SimpleSprite qui doivent crever.
        """

        #update puis remove, ou remove puis update ? Wat is the best ?
        #Je ne sais pas, et osef. update puis remove me semble le plus optimis�.
        #Comme �a, on se traine pas des sprite morts pendant un cycle de plus.

        for sprite in self.simpleSpriteGroup:
            sprite.update()

        #on r�cup�re la liste des SpriteSimple ayant leur �tat � SPRITE_DEAD.
        #C'est � dire la liste des SpriteSimple � supprimer.
        listSpriteToRemove = [ sprite for sprite in self.simpleSpriteGroup
                               if sprite.currentState == SPRITE_DEAD ]

        #on enl�ve les SpriteSimple des deux groups de sprites.
        #Et apr�s ils se d�truiront tout seul, car ils ont plus de r�f�rence. Youpi !!
        for sprite in listSpriteToRemove:
            self.allSprites.remove(sprite)
            self.simpleSpriteGroup.remove(sprite)

