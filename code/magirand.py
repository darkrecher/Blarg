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

classe d�riv�e du magicien
le magirand est un magicien qui se d�place au hasard. Plus son level est haut, plus il bouge vite.
Son level augmente avec le temps.

Le magicien peut un peu d�passer de l'�cran, mais que par la droite et/ou le bas,
et quand il d�passe, on lui remet un petit mouvement vers la gauche et/ou le haut,
pour le remettre progressivement dans l'�cran.

Il se d�place au hasard. Mais y'a quand m�me une inertie dans ses mouvements.

Vocabulaire :

RespectLine : ligne verticale imaginaire (chaque instance de magirand � la sienne).
Lorsque le magicien se trouve � gauche de cette limite, on lui ajoute un petit
mouvement vers la droite.

Cela permet d'�viter que le magicien se rapproche trop vite du bord gauche de l'�cran,
l� o�, � priori, se trouve le h�ros, puisqu'il tire ses coups
de flingue vers la droite.

capacit� d'acc�l�ration : Pour modifier la trajectoire du magicien,
on ajoute un vecteur d'acc�l�ration � son vecteur de vitesse.
le vecteur d'acc�l�ration est d�termin� au hasard, mais il est born� � des valeurs
limites. Ces valeurs limites, c'est la capacit� d'acc�l�ration.
En gros, c'est un peu l'inverse de l'inertie.

Tous les X cycles de jeu, le magicien effectue un "LevelUp" : il devient un peu plus dangereux
X est d�fini par la constante LEVEL_UP_PERIOD

LevelUp :
La vitesse max du magicien augmente, ainsi que sa capacit� d'acc�l�ration.
Sa "RespectLine" est d�plac�e vers la gauche. Il pourra donc plus facilement aller
emmerder le joueur.

Au bout d'un moment, la vitesse max n'augmente plus. Pareil pour la capacit� d'acc�l�ration.
et la RespectLine ne se d�place plus.
Et lorsque le magicien a atteint un LEVEL_MAX, il ne fait plus de LevelUp.

Pour plus de blabla, voir la classe de base magician.py
"""

import pygame

from common import centeredRandom, GAME_RECT, pyRect

from magician import (Magician,
                      APPEARING, ALIVE, HURT, DYING, BURSTING, DEAD,
                      MAGI_RECT_CLAMPING)


#capacit� d'acc�laration initiale et maximale
ACCEL_CAP_INIT = 1
ACCEL_CAP_MAX  = 9
#p�riode (nombre de cycle de jeu) de renouvellement et d'application de l'acc�l�ration.
#tous les ACCEL_PERIOD, le magicien red�finit son acc�l�ration, et l'applique
#une fois � son mouvement. Entre deux ACCEL_PERIOD, il n'y a pas d'acc�l�ration.
ACCEL_PERIOD = 4

#vitesse limite initiale et maximale.
#(vitesse limite = vitesse max, j'ai pas forc�ment choisi le bon mot. osef)
SPEED_LIMIT_INIT = 2
SPEED_LIMIT_MAX = 14
#p�riode d'application du vecteur de vitesse � la position.
#le magicien ne bouge pas � tous les cycles de jeu). Il bouge tous les MOVE_PERIOD cycles
MOVE_PERIOD = 2

#p�riode entre chaque LevelUp du magicien
LEVEL_UP_PERIOD = 180
#Le magicien peut augmenter son level jusqu'au LEVEL_MAX
LEVEL_MAX = 15

#abscisse initiale de la RespectLine
RESPECT_LINE_INIT = GAME_RECT.left + (GAME_RECT.width * 4) / 5
#distance de d�placement de la RespectLine lors d'un LevelUp
REPECT_LINE_LEVELUP_DECREMENT = GAME_RECT.width / 5
#mouvement � ajouter vers la droite si le magicien d�passe la respectLine
RESPECT_LINE_MOVEMENT = 2

#mouvement � appliquer si le magicien sort de l'�cran � droite ou en bas
#mouvement appliqu� vers la gauche
BORDER_RIGHT_MOVEMENT = 3
#mouvement appliqu� vers le haut
BORDER_BOTTOM_MOVMENT = 3

#dictionnaire d�finissant le mouvement de recul du magicien, en fonction
#des d�gats qu'il se prend dans la gueule.
#cl� : nombre de bullet que se prend le magicien d'un coup.
#valeur : tuple de 2 �l�ments.
# - hurtPeriod. nombre de cycle � attendre entre chaque mouvement de recul
# - listMovementXWhenHurt. D�placement X du recul du magicien. (pas de depl Y)
#   cette liste est foutue � l'envers, parce que je trouvais �a plus cool comme �a.
#   Par exemple, pour le cas o� il se prend 1 bullet,
#   le magicien va se d�placer de 4, et attendre 4 cycles
#   puis se d�placer de 3, et attendre encore 4 cycles
#   puis se red�placer de 3, et attendre encore 4 cycles, etc.
DIC_HURTINFOMOV_FROM_DAMAGE = {
    1 : (4, (0, 0, 0, 1, 1, 2, 2, 3, 3, 4)),
    2 : (4, (0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 6)),
}
#mouvement de recul par d�faut, si le magicien se prend un nombre de bullet
#non sp�cifi� par le dictionnaire ci-dessus.
DEFAULT_HURTINFOMOV = DIC_HURTINFOMOV_FROM_DAMAGE[2]

#pour info, y'a que le premier �l�ment de ce dictionnaire qui sert vraiment � quelque chose.
#car le magicien a 2 points de vie. Donc si il se prend 2 points de d�gats ou plus,
#on lui applique pas de mouvement de hurt, mais on le cr�ve direct.
#J'aime bien faire de l'inutile, voyez.


class MagiRand(Magician):
    """
    magicien qui se d�place au hasard, youpi.
    """

    def __init__(self, dicMagicienImg, spriteSimpleGenerator,
                 posStart, level=1):
        """
        constructeur. (thx captain obvious)

        entr�e :
            voir la classe-m�re. C'est les m�mes
        """
        #appel du constructeur de la classe-m�re. (Maman !!!)
        Magician.__init__(self, dicMagicienImg,
                          spriteSimpleGenerator, posStart, level)

        #init du mouvement et de l'acc�l�ration, � des valeurs de 0.
        self.razMovementAndAcceleration()


    def isMoveFinished(self):
        """
        voir description de la fonction dans la classe de base (Magician)
        """
        #on renvoie toujours False, car le magicien random bouge tout le temps
        return False


    def razMovementAndAcceleration(self):
        """
        fixe le mouvement et l'acc�l�ration � (0,0) : pas de mouvement, et pas d'accel
        initialise les compteurs pour les p�riodes de mouvement et d'acc�l�ration.
        """

        #les vecteurs de mouvement et d'acc�l�ration sont stock�s dand des Rects,
        #dont osef le width et le height.
        #Ca permet de profiter de toutes les fonctions cool des Rects (move, clamp, ...)

        #compteur pour l'acc�l�ration
        self.accelCounter = ACCEL_PERIOD
        #acc�l�ration � (0, 0)
        self.currentAccel = pyRect()

        #compteur pour le mouvement
        self.moveCounter = MOVE_PERIOD
        #mouvement � (0, 0)
        self.speed = pyRect()


    def resetToLevelOne(self):
        """
        initialise/r�initialise le level � 1, et remet les caract�ristiques d�pendante du level
        � leur valeur initiale pourrite.
        """

        Magician.resetToLevelOne(self)

        #capacit� d'acc�l�ration et vitesse limite.
        self.accelCap = ACCEL_CAP_INIT
        self.speedLimit = SPEED_LIMIT_INIT
        #d�finit un rect, centr� sur 0, et ayant comme demi-longueur self.speedLimit
        #(voir corps de la fonction)
        self.defineSpeedLimitClampingFromSpeedLimit()

        #compteur por la p�riode d'augmentation du niveau
        self.levelUpCounter = LEVEL_UP_PERIOD

        self.respectLine = RESPECT_LINE_INIT

        #mouvement et acc�l�ration � (0, 0).
        #et init des compteurs pour les p�riodes de move et d'accel
        self.razMovementAndAcceleration()


    def defineSpeedLimitClampingFromSpeedLimit(self):
        """
        d�finit l'attribut self.speedLimitClamping, en fonction de l'attribut self.speedLimit
        self.speedLimitClamping est un rect centr� sur 0,
        et ayant comme demi-longueur self.speedLimit
        on pourra s'en servir pour limiter la vitesse courante,
        qui doit rester dans les valeurs de speedLimit.
        Et y'aura juste besoin d'un simple clamping, plut�t qu'un tas de if � la con.
        """

        #on d�finit spd, juste pour raccourcir le nom, sinon c'est chiant.
        spd = self.speedLimit
        #le rect va du point (-spd, -spd) jusqu'au point (+spd, +spd)
        self.speedLimitClamping = pyRect(-spd, -spd, 2*spd, 2*spd)


    def levelUp(self):
        """
        Le magicien fait un levelUp et il monte ses caract�ristiques.
        """

        Magician.levelUp(self)

        #on recule la respectLine
        self.respectLine -= REPECT_LINE_LEVELUP_DECREMENT

        #augmentation de la vitesse limite.
        if self.speedLimit < SPEED_LIMIT_MAX:
            self.speedLimit += 1
            #la speedLimit a chang�, donc on doit red�finir le rect de clamping de speedLimit.
            self.defineSpeedLimitClampingFromSpeedLimit()

        #augmentation de la capacit� d'acc�l�ration.
        if self.accelCap < ACCEL_CAP_MAX:
            self.accelCap += 1


    def hitByBulletButNotDead(self, Damage):
        """
        fonction d�finissant les actions � faire quand le magicien s'est pris
        des bullets, mais qu'il n'en est pas mort. (il est HURT)

        entr�es :
            Damage. int. Nombre de points de d�g�ts ( = nombre de bullets qui le touchent)
        """

        Magician.hitByBulletButNotDead(self, Damage)

        #on choisit dans le dico DIC_HURTINFOMOV_FROM_DAMAGE une p�riode, et une liste
        #de mouvement de recul, en fonction du Damage que se prend le magicien.
        #Il y a une p�riode et une liste par d�faut, si jamais le dico est pas assez complet.
        (self.hurtPeriod,
         self.listMovementXWhenHurt,
        ) = DIC_HURTINFOMOV_FROM_DAMAGE.get(Damage, DEFAULT_HURTINFOMOV)

        #compteur pour la p�riode de mouvement
        self.hurtCounter = self.hurtPeriod
        #curseur sur le mouvement de recul en cours, dans la liste. (qu'on parcourt � l'envers
        #mais �a je l'ai d�j� dit)
        self.hurtMovementCursor = len(self.listMovementXWhenHurt) - 1


    def updateNormal(self):
        """
        update du magicien (fonction � lancer � chaque cycle de jeu)
        cas o� le magicien est dans son �tat normal (ALIVE)
        """

        Magician.updateNormal(self)

        # --- g�rage de l'acc�l�ration et de la vitesse ---

        self.accelCounter -= 1

        if self.accelCounter == 0:

            self.accelCounter = ACCEL_PERIOD
            #on red�finit l'acc�l�ration, avec des valeurs au hasard,
            #born�e � la capacit� d'acc�l�ration.
            self.currentAccel = pyRect(centeredRandom(self.accelCap),
                                       centeredRandom(self.accelCap))

        #application de l'acc�l�ration � la vitesse.
        self.speed.move_ip(self.currentAccel.topleft)
        #clampage de la vitesse, pour qu'elle ne d�passe pas la vitesse limite,
        #ni en X, ni en -X, ni en Y, ni en -Y. (C'est rigolo ce que je dis)
        self.speed.clamp_ip(self.speedLimitClamping)

        # --- g�rage de la position, en fonction de la vitesse. ---

        self.moveCounter -= 1

        if self.moveCounter == 0:

            self.moveCounter = MOVE_PERIOD

            #application de la vitesse sur la position du magicien
            self.rect.move_ip(self.speed.topleft)

            #ajout du petit mouvement vers la droite si le magicien
            #est � gauche de la RespectLine
            if self.rect.left < self.respectLine:
                self.rect.x += RESPECT_LINE_MOVEMENT

            #ajout du mouvement vers la gauche si sorti de l'�cran � droite
            if self.rect.right > GAME_RECT.right:
                self.rect.x -= BORDER_RIGHT_MOVEMENT

            #ajout du mouvement vers le haut si sorti de l'�cran en bas
            if self.rect.bottom > GAME_RECT.bottom:
                self.rect.y -= BORDER_BOTTOM_MOVMENT

            #clampage pour que le magicien reste (� peu pr�s) dans l'�cran
            self.rect.clamp_ip(MAGI_RECT_CLAMPING)

            #rien n'est fait pour �loigner le magicien d'un bord de l'�cran en haut et � gauche.
            #Du coup, il peut y rester coller pendant un certain temps.
            #je trouve �a rigolo, �a fait comme une mouche � merde qui s'acharne contre une vitre.

        # --- g�rage du LeveUp (uniquement si le level en cours n'a pas atteint LEVEL_MAX ---

        if self.level < LEVEL_MAX:

            self.levelUpCounter -= 1

            if self.levelUpCounter == 0:
                self.levelUpCounter = LEVEL_UP_PERIOD
                self.levelUp()


    def updateHurt(self):
        """
        update du magicien (fonction � lancer � chaque cycle de jeu)
        cas o� le magicien s'est pris une/plusieurs bullet. (HURT)

        le magicien a un mouvement de recul, tous les X cycles.
        Puis il revient � l'�tat ALIVE
        """

        #l�, on n'ex�cute pas la super-classe. Sinon le magicien se fait unHurt
        #tout de suite, et c'est pas ce qu'on veut.

        self.hurtCounter -= 1

        if self.hurtCounter <= 0:

            self.hurtCounter = self.hurtPeriod

            #on r�cup�re la distance de mouvement du Hurt, et on le fout en deplacement X
            #pas de d�placement Y pendant un HURT. osef.
            moveXHurt = self.listMovementXWhenHurt[self.hurtMovementCursor]
            moveHurt = pyRect(moveXHurt, 0)

            #application du mouvement du Hurt, et clamping du magicien dans l'�cran.
            self.rect.move_ip(moveHurt.topleft)
            self.rect.clamp_ip(MAGI_RECT_CLAMPING)

            #d�placement du curseur pointant sur le mouvement de Hurt courant.
            self.hurtMovementCursor -= 1

            #Si le curseur arrive au d�but de la liste, on a fait tous les mouvements
            #de recul du Hurt. Le magicien revient � son �tat normal (ALIVE)
            if self.hurtMovementCursor == 0:

                #on r�initialise son mouvement et son acc�l�ration � (0, 0) (bien fait !)
                self.razMovementAndAcceleration()
                self.unHurt()
