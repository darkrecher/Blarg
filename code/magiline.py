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

date de la derni�re relecture-commentage : 06/10/2010

classe d�riv�e du magicien.
Le magiline se d�place d'un point vers un autre en ligne droite, et s'arr�te.
Plus son level est haut, plus il bouge vite.
Son level ne varie pas dans le temps. Il reste fix� � la valeur initiale
"""

import pygame

from common import pyRect

#�a c'est pour faire le mouvement en ligne du magicien
from movline import MovingPointOnLine

from magician import (Magician,
                      APPEARING, ALIVE, HURT, DYING, BURSTING, DEAD)

#quand le magiline se fait HURT, il reste immobile pendant un certain temps.
#Il n'a pas de mouvement de recul comme le magirand, pour pas le d�vier de sa trajectoire
#Ce dictionnaire donne le nombre de cycle que le magiline reste Hurt, en fonction du
#nombre de bullet qu'il s'est pris d'un seul coup.
#comme dans la classe Magirand, avec le DIC_HURT_MOVEMENT_FROM_DAMAGE,
#y'a que le premier �l�ment de ce dictionnaire qui sert vraiment � quelque chose. M'en fout.
DIC_HURT_TOTAL_PERIOD_FROM_DAMAGE = {
  1 : 40,
  2 : 52,
}

#choix d'une valeur par d�faut pour ce temps de Hurt, si jamais le magicien se prend
#un nombre de bullet non pr�vu par le dico ci-dessus. Ca sert � rien non plus, mais
#je m'en contrfous. Je fais du code g�n�rique moi.
DEFAULT_HURT_TOTAL_PERIOD = DIC_HURT_TOTAL_PERIOD_FROM_DAMAGE[2]

#quand le magicien finit son mouvement en ligne droite, si il est � gauche
#de cette respect line, il bougera � droite. C'est oblig� de faire comme �a,
#sinon, le h�ros ne pourra pas du tout le tuer ! Le h�ros pourra pas passer derri�re
#et lui tirer un coup de flingue.
RESPECT_LINE_X = 80

#p�riode de d�placement, en nombre de cycle, pour un magicien de level 1.
#La p�riode est inversement proportionnelle au level.
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

        entr�e :
            dicMagicienImg, spriteSimpleGenerator, level : voir classe-m�re

            posStart : Rect. position de d�part du coin superieur gauche du sprite, � l'�cran.

            posEnd   : Rect. position d'arriv�e du coin-coin sup gauche du sprite.
        """

        #appel du constructeur de la classe-m�re. (Maman !!!)
        Magician.__init__(self, dicMagicienImg,
                          spriteSimpleGenerator, posStart, level)

        self.posEnd = pygame.rect.Rect(posEnd)

        #classe permettant de g�rer le d�placement d'un point en ligne droite.
        #On l'utilise pour d�terminer les valeurs successives des coordonn�es du magiline.
        self.movingPointOnLine = MovingPointOnLine(posStart, self.posEnd)

        #indique si le magiline a finit son mouvement ou pas. Le mouvement inclus
        #le d�placement vers le point d'arriv�e, suivi de l'�ventuel petit d�calage vers
        #la droite de RESPECT_LINE_X, pour laisser un peu de place au joueur qui pourra tuer
        #le magiline. (r�p�tition de "magiline" dans cette phrase, chai pas comment faire mieux.
        self.isMoveFinishedBool = False

        #compteur de mouvement. (Delay, p�riode, level, proportionnel, tout �a)
        self.moveCounter = 0

        #fonction � utiliser dans l'update du magicien, pour g�rer son mouvement.
        self.currentFuncupdateNorm = self.updateNormMoveOnLine


    def isMoveFinished(self):
        """
        voir description de la fonction dans la classe de base (Magician)
        """

        #captain obvious. Sinon, voir descript de cet attribut juste ci-dessus.
        return self.isMoveFinishedBool


    def hitByBulletButNotDead(self, Damage):
        """
        fonction d�finissant les actions � faire quand le magicien s'est pris
        des bullets, mais qu'il n'en est pas mort. (il est HURT)

        entr�es :
            Damage. int. Nombre de points de d�g�ts ( = nombre de bullets qui le touchent)
        """

        Magician.hitByBulletButNotDead(self, Damage)

        #d�termination du temps que le magicien va rester HURT, � partir du nombre
        #de bullets qui vient de le toucher (Damage).
        self.hurtTotalPeriod = DIC_HURT_TOTAL_PERIOD_FROM_DAMAGE.get(
            Damage,
            DEFAULT_HURT_TOTAL_PERIOD
        )

        #compteur pour le temps de HURT
        self.hurtCounter = self.hurtTotalPeriod


    def updateNormMoveOnLine(self):
        """
        fonction de l'update dans l'�tat normal (ALIVE)
        cas o� le mouvement en cours est celui de la ligne droite.
        """

        #on augmente le compteur de mouvement. (+ le level est haut, + le magi bouge vite)
        self.moveCounter += self.level

        #mouvement d'un pas, autant de fois qu'on a de p�riode de mouvement.
        while self.moveCounter >= DELAY_MOVE:

            self.moveCounter -= DELAY_MOVE

            #on fait avancer d'un pixel le point qui guide le d�placement du magiline
            self.movingPointOnLine.advanceOneStep()
            #et juste apr�s, on lui pique ses coordonn�es pour les mettre directos sur le magiline
            self.rect.x = self.movingPointOnLine.x
            self.rect.y = self.movingPointOnLine.y

            if self.movingPointOnLine.isMoveFinished():

                #quand le point guidant le d�placement est arriv� � destination, eh bien
                #le magiline aussi. Il faut donc rebrancher la fonction d'update effectuant
                #le d�placement actuel du magiline.

                if self.rect.x >= RESPECT_LINE_X:

                    #le magiline est � droite de la respect line, il a donc vraiment
                    #compl�tement fini son mouvement. On se branche vers la fonction
                    #qui ne fait plus aucun mouvement, et on indique que le mouvement est fini.
                    self.currentFuncupdateNorm = self.updateNormStayPut
                    self.isMoveFinishedBool = True

                else:

                    #le magiline doit se d�placer � droite de la respect line, on
                    #se branche vers la fonction qui fait ce mouvement.
                    self.currentFuncupdateNorm = self.updateNormMoveRespectX

                return


    def updateNormMoveRespectX(self):
        """
        fonction de l'update dans l'�tat normal (ALIVE)
        cas o� le mouvement en cours est le mouvement vers la droite,
        pour se retrouver apr�s la RESPECT_LINE_X
        """

        #on augmente le compteur de mouvement. (+ le level est haut, + le magi bouge vite)
        self.moveCounter += self.level

        #mouvement d'un pas, autant de fois qu'on a de p�riode de mouvement.
        while self.moveCounter >= DELAY_MOVE:

            self.moveCounter -= DELAY_MOVE

            #on fait juste un petit mouvement vers la droite.
            self.rect.x += 1

            if self.rect.x >= RESPECT_LINE_X:

                #le magiline est � droite de la respect line, il a donc vraiment
                #compl�tement fini son mouvement. On se branche vers la fonction
                #qui ne fait plus aucun mouvement, et on indique que le mouvement est fini.
                #
                #factorisation fail. Ces deux lignes de code et la condition ci-dessus,
                #on les retrouve exactement pareil dans la fonction pr�c�dente. osef.
                self.currentFuncupdateNorm = self.updateNormStayPut
                self.isMoveFinishedBool = True
                return


    def updateNormStayPut(self):
        """
        fonction de l'update dans l'�tat normal (ALIVE)
        cas o� tous les mouvements sont finis. Y'a plus rien � faire.

        Fun fact : j'ai appel� la fonciton "stay put" pour 3 raisons :
         - c'est une vraie expression qui existe
         - c'est ce que dit Beethro Budkin � son neveu Halph dans le jeu
           "DROD : Journey to the Rooted Hold"
         - en franglais, �a fait : "reste pute". Ce qui va bien pour un connard de magicien.
        """

        #tout ce blabla pour faire un pass. Bravo, moi-m�me.
        pass


    def updateNormal(self):
        """
        update du magicien (fonction � lancer � chaque cycle de jeu)
        cas o� le magicien est dans son �tat normal (ALIVE)
        """

        #On a juste a ex�cuter la bonne fonction, correspondant au mouvement du moment,
        #Les fonctions de la couche en-dessous se d�merdent.
        self.currentFuncupdateNorm()


    def updateHurt(self):
        """
        update du magicien (fonction � lancer � chaque cycle de jeu)
        cas o� le magicien s'est pris une/plusieurs bullet. (HURT)
        on devrait dire HURTED, mais vous connaissez les angliches avec leur putain
        de verbe irr�gulier de merde...

        le magicien revient � l'�tat ALIVE au bout d'un certain nombre de cycle.
        il n'a pas de mouvement de hurt. Sinon, �a risquerait de le d�vier de sa
        ligne initiale.
        """

        self.hurtCounter -= 1

        if self.hurtCounter <= 0:
            self.unHurt()
