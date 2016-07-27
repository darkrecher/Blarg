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

date de la dernière relecture-commentage : 06/10/2010

classe dérivée du magicien.
Le magiline se déplace d'un point vers un autre en ligne droite, et s'arrête.
Plus son level est haut, plus il bouge vite.
Son level ne varie pas dans le temps. Il reste fixé à la valeur initiale
"""

import pygame

from common import pyRect

#ça c'est pour faire le mouvement en ligne du magicien
from movline import MovingPointOnLine

from magician import (Magician,
                      APPEARING, ALIVE, HURT, DYING, BURSTING, DEAD)

#quand le magiline se fait HURT, il reste immobile pendant un certain temps.
#Il n'a pas de mouvement de recul comme le magirand, pour pas le dévier de sa trajectoire
#Ce dictionnaire donne le nombre de cycle que le magiline reste Hurt, en fonction du
#nombre de bullet qu'il s'est pris d'un seul coup.
#comme dans la classe Magirand, avec le DIC_HURT_MOVEMENT_FROM_DAMAGE,
#y'a que le premier élément de ce dictionnaire qui sert vraiment à quelque chose. M'en fout.
DIC_HURT_TOTAL_PERIOD_FROM_DAMAGE = {
  1 : 40,
  2 : 52,
}

#choix d'une valeur par défaut pour ce temps de Hurt, si jamais le magicien se prend
#un nombre de bullet non prévu par le dico ci-dessus. Ca sert à rien non plus, mais
#je m'en contrfous. Je fais du code générique moi.
DEFAULT_HURT_TOTAL_PERIOD = DIC_HURT_TOTAL_PERIOD_FROM_DAMAGE[2]

#quand le magicien finit son mouvement en ligne droite, si il est à gauche
#de cette respect line, il bougera à droite. C'est obligé de faire comme ça,
#sinon, le héros ne pourra pas du tout le tuer ! Le héros pourra pas passer derrière
#et lui tirer un coup de flingue.
RESPECT_LINE_X = 80

#période de déplacement, en nombre de cycle, pour un magicien de level 1.
#La période est inversement proportionnelle au level.
#un level 1 bouge 1 fois tous les X cycles, un level 2 bouge 2 fois tous les X cycles, etc...
#Et donc ici, X = 3
DELAY_MOVE = 3

class MagiLine(Magician):
    """
    le sprite qui est le magicien
    """

    def __init__(self, dicMagicienImg, spriteSimpleGenerator,
                 posStart, posEnd, level=1):
        """
        constructeur. (thx captain obvious)

        entrée :
            dicMagicienImg, spriteSimpleGenerator, level : voir classe-mère

            posStart : Rect. position de départ du coin superieur gauche du sprite, à l'écran.

            posEnd   : Rect. position d'arrivée du coin-coin sup gauche du sprite.
        """

        #appel du constructeur de la classe-mère. (Maman !!!)
        Magician.__init__(self, dicMagicienImg,
                          spriteSimpleGenerator, posStart, level)

        self.posEnd = pygame.rect.Rect(posEnd)

        #classe permettant de gérer le déplacement d'un point en ligne droite.
        #On l'utilise pour déterminer les valeurs successives des coordonnées du magiline.
        self.movingPointOnLine = MovingPointOnLine(posStart, self.posEnd)

        #indique si le magiline a finit son mouvement ou pas. Le mouvement inclus
        #le déplacement vers le point d'arrivée, suivi de l'éventuel petit décalage vers
        #la droite de RESPECT_LINE_X, pour laisser un peu de place au joueur qui pourra tuer
        #le magiline. (répétition de "magiline" dans cette phrase, chai pas comment faire mieux.
        self.isMoveFinishedBool = False

        #compteur de mouvement. (Delay, période, level, proportionnel, tout ça)
        self.moveCounter = 0

        #fonction à utiliser dans l'update du magicien, pour gérer son mouvement.
        self.currentFuncupdateNorm = self.updateNormMoveOnLine


    def isMoveFinished(self):
        """
        voir description de la fonction dans la classe de base (Magician)
        """

        #captain obvious. Sinon, voir descript de cet attribut juste ci-dessus.
        return self.isMoveFinishedBool


    def hitByBulletButNotDead(self, Damage):
        """
        fonction définissant les actions à faire quand le magicien s'est pris
        des bullets, mais qu'il n'en est pas mort. (il est HURT)

        entrées :
            Damage. int. Nombre de points de dégâts ( = nombre de bullets qui le touchent)
        """

        Magician.hitByBulletButNotDead(self, Damage)

        #détermination du temps que le magicien va rester HURT, à partir du nombre
        #de bullets qui vient de le toucher (Damage).
        self.hurtTotalPeriod = DIC_HURT_TOTAL_PERIOD_FROM_DAMAGE.get(
            Damage,
            DEFAULT_HURT_TOTAL_PERIOD
        )

        #compteur pour le temps de HURT
        self.hurtCounter = self.hurtTotalPeriod


    def updateNormMoveOnLine(self):
        """
        fonction de l'update dans l'état normal (ALIVE)
        cas où le mouvement en cours est celui de la ligne droite.
        """

        #on augmente le compteur de mouvement. (+ le level est haut, + le magi bouge vite)
        self.moveCounter += self.level

        #mouvement d'un pas, autant de fois qu'on a de période de mouvement.
        while self.moveCounter >= DELAY_MOVE:

            self.moveCounter -= DELAY_MOVE

            #on fait avancer d'un pixel le point qui guide le déplacement du magiline
            self.movingPointOnLine.advanceOneStep()
            #et juste après, on lui pique ses coordonnées pour les mettre directos sur le magiline
            self.rect.x = self.movingPointOnLine.x
            self.rect.y = self.movingPointOnLine.y

            if self.movingPointOnLine.isMoveFinished():

                #quand le point guidant le déplacement est arrivé à destination, eh bien
                #le magiline aussi. Il faut donc rebrancher la fonction d'update effectuant
                #le déplacement actuel du magiline.

                if self.rect.x >= RESPECT_LINE_X:

                    #le magiline est à droite de la respect line, il a donc vraiment
                    #complètement fini son mouvement. On se branche vers la fonction
                    #qui ne fait plus aucun mouvement, et on indique que le mouvement est fini.
                    self.currentFuncupdateNorm = self.updateNormStayPut
                    self.isMoveFinishedBool = True

                else:

                    #le magiline doit se déplacer à droite de la respect line, on
                    #se branche vers la fonction qui fait ce mouvement.
                    self.currentFuncupdateNorm = self.updateNormMoveRespectX

                return


    def updateNormMoveRespectX(self):
        """
        fonction de l'update dans l'état normal (ALIVE)
        cas où le mouvement en cours est le mouvement vers la droite,
        pour se retrouver après la RESPECT_LINE_X
        """

        #on augmente le compteur de mouvement. (+ le level est haut, + le magi bouge vite)
        self.moveCounter += self.level

        #mouvement d'un pas, autant de fois qu'on a de période de mouvement.
        while self.moveCounter >= DELAY_MOVE:

            self.moveCounter -= DELAY_MOVE

            #on fait juste un petit mouvement vers la droite.
            self.rect.x += 1

            if self.rect.x >= RESPECT_LINE_X:

                #le magiline est à droite de la respect line, il a donc vraiment
                #complètement fini son mouvement. On se branche vers la fonction
                #qui ne fait plus aucun mouvement, et on indique que le mouvement est fini.
                #
                #factorisation fail. Ces deux lignes de code et la condition ci-dessus,
                #on les retrouve exactement pareil dans la fonction précédente. osef.
                self.currentFuncupdateNorm = self.updateNormStayPut
                self.isMoveFinishedBool = True
                return


    def updateNormStayPut(self):
        """
        fonction de l'update dans l'état normal (ALIVE)
        cas où tous les mouvements sont finis. Y'a plus rien à faire.

        Fun fact : j'ai appelé la fonciton "stay put" pour 3 raisons :
         - c'est une vraie expression qui existe
         - c'est ce que dit Beethro Budkin à son neveu Halph dans le jeu
           "DROD : Journey to the Rooted Hold"
         - en franglais, ça fait : "reste pute". Ce qui va bien pour un connard de magicien.
        """

        #tout ce blabla pour faire un pass. Bravo, moi-même.
        pass


    def updateNormal(self):
        """
        update du magicien (fonction à lancer à chaque cycle de jeu)
        cas où le magicien est dans son état normal (ALIVE)
        """

        #On a juste a exécuter la bonne fonction, correspondant au mouvement du moment,
        #Les fonctions de la couche en-dessous se démerdent.
        self.currentFuncupdateNorm()


    def updateHurt(self):
        """
        update du magicien (fonction à lancer à chaque cycle de jeu)
        cas où le magicien s'est pris une/plusieurs bullet. (HURT)
        on devrait dire HURTED, mais vous connaissez les angliches avec leur putain
        de verbe irrégulier de merde...

        le magicien revient à l'état ALIVE au bout d'un certain nombre de cycle.
        il n'a pas de mouvement de hurt. Sinon, ça risquerait de le dévier de sa
        ligne initiale.
        """

        self.hurtCounter -= 1

        if self.hurtCounter <= 0:
            self.unHurt()
