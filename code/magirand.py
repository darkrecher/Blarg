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

classe dérivée du magicien
le magirand est un magicien qui se déplace au hasard. Plus son level est haut, plus il bouge vite.
Son level augmente avec le temps.

Le magicien peut un peu dépasser de l'écran, mais que par la droite et/ou le bas,
et quand il dépasse, on lui remet un petit mouvement vers la gauche et/ou le haut,
pour le remettre progressivement dans l'écran.

Il se déplace au hasard. Mais y'a quand même une inertie dans ses mouvements.

Vocabulaire :

RespectLine : ligne verticale imaginaire (chaque instance de magirand à la sienne).
Lorsque le magicien se trouve à gauche de cette limite, on lui ajoute un petit
mouvement vers la droite.

Cela permet d'éviter que le magicien se rapproche trop vite du bord gauche de l'écran,
là où, à priori, se trouve le héros, puisqu'il tire ses coups
de flingue vers la droite.

capacité d'accélération : Pour modifier la trajectoire du magicien,
on ajoute un vecteur d'accélération à son vecteur de vitesse.
le vecteur d'accélération est déterminé au hasard, mais il est borné à des valeurs
limites. Ces valeurs limites, c'est la capacité d'accélération.
En gros, c'est un peu l'inverse de l'inertie.

Tous les X cycles de jeu, le magicien effectue un "LevelUp" : il devient un peu plus dangereux
X est défini par la constante LEVEL_UP_PERIOD

LevelUp :
La vitesse max du magicien augmente, ainsi que sa capacité d'accélération.
Sa "RespectLine" est déplacée vers la gauche. Il pourra donc plus facilement aller
emmerder le joueur.

Au bout d'un moment, la vitesse max n'augmente plus. Pareil pour la capacité d'accélération.
et la RespectLine ne se déplace plus.
Et lorsque le magicien a atteint un LEVEL_MAX, il ne fait plus de LevelUp.

Pour plus de blabla, voir la classe de base magician.py
"""

import pygame

from common import centeredRandom, GAME_RECT, pyRect

from magician import (Magician,
                      APPEARING, ALIVE, HURT, DYING, BURSTING, DEAD,
                      MAGI_RECT_CLAMPING)


#capacité d'accélaration initiale et maximale
ACCEL_CAP_INIT = 1
ACCEL_CAP_MAX  = 9
#période (nombre de cycle de jeu) de renouvellement et d'application de l'accélération.
#tous les ACCEL_PERIOD, le magicien redéfinit son accélération, et l'applique
#une fois à son mouvement. Entre deux ACCEL_PERIOD, il n'y a pas d'accélération.
ACCEL_PERIOD = 4

#vitesse limite initiale et maximale.
#(vitesse limite = vitesse max, j'ai pas forcément choisi le bon mot. osef)
SPEED_LIMIT_INIT = 2
SPEED_LIMIT_MAX = 14
#période d'application du vecteur de vitesse à la position.
#le magicien ne bouge pas à tous les cycles de jeu). Il bouge tous les MOVE_PERIOD cycles
MOVE_PERIOD = 2

#période entre chaque LevelUp du magicien
LEVEL_UP_PERIOD = 180
#Le magicien peut augmenter son level jusqu'au LEVEL_MAX
LEVEL_MAX = 15

#abscisse initiale de la RespectLine
RESPECT_LINE_INIT = GAME_RECT.left + (GAME_RECT.width * 4) / 5
#distance de déplacement de la RespectLine lors d'un LevelUp
REPECT_LINE_LEVELUP_DECREMENT = GAME_RECT.width / 5
#mouvement à ajouter vers la droite si le magicien dépasse la respectLine
RESPECT_LINE_MOVEMENT = 2

#mouvement à appliquer si le magicien sort de l'écran à droite ou en bas
#mouvement appliqué vers la gauche
BORDER_RIGHT_MOVEMENT = 3
#mouvement appliqué vers le haut
BORDER_BOTTOM_MOVMENT = 3

#dictionnaire définissant le mouvement de recul du magicien, en fonction
#des dégats qu'il se prend dans la gueule.
#clé : nombre de bullet que se prend le magicien d'un coup.
#valeur : tuple de 2 éléments.
# - hurtPeriod. nombre de cycle à attendre entre chaque mouvement de recul
# - listMovementXWhenHurt. Déplacement X du recul du magicien. (pas de depl Y)
#   cette liste est foutue à l'envers, parce que je trouvais ça plus cool comme ça.
#   Par exemple, pour le cas où il se prend 1 bullet,
#   le magicien va se déplacer de 4, et attendre 4 cycles
#   puis se déplacer de 3, et attendre encore 4 cycles
#   puis se redéplacer de 3, et attendre encore 4 cycles, etc.
DIC_HURTINFOMOV_FROM_DAMAGE = {
    1 : (4, (0, 0, 0, 1, 1, 2, 2, 3, 3, 4)),
    2 : (4, (0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 6)),
}
#mouvement de recul par défaut, si le magicien se prend un nombre de bullet
#non spécifié par le dictionnaire ci-dessus.
DEFAULT_HURTINFOMOV = DIC_HURTINFOMOV_FROM_DAMAGE[2]

#pour info, y'a que le premier élément de ce dictionnaire qui sert vraiment à quelque chose.
#car le magicien a 2 points de vie. Donc si il se prend 2 points de dégats ou plus,
#on lui applique pas de mouvement de hurt, mais on le crève direct.
#J'aime bien faire de l'inutile, voyez.


class MagiRand(Magician):
    """
    magicien qui se déplace au hasard, youpi.
    """

    def __init__(self, dicMagicienImg, spriteSimpleGenerator,
                 posStart, level=1):
        """
        constructeur. (thx captain obvious)

        entrée :
            voir la classe-mère. C'est les mêmes
        """
        #appel du constructeur de la classe-mère. (Maman !!!)
        Magician.__init__(self, dicMagicienImg,
                          spriteSimpleGenerator, posStart, level)

        #init du mouvement et de l'accélération, à des valeurs de 0.
        self.razMovementAndAcceleration()


    def isMoveFinished(self):
        """
        voir description de la fonction dans la classe de base (Magician)
        """
        #on renvoie toujours False, car le magicien random bouge tout le temps
        return False


    def razMovementAndAcceleration(self):
        """
        fixe le mouvement et l'accélération à (0,0) : pas de mouvement, et pas d'accel
        initialise les compteurs pour les périodes de mouvement et d'accélération.
        """

        #les vecteurs de mouvement et d'accélération sont stockés dand des Rects,
        #dont osef le width et le height.
        #Ca permet de profiter de toutes les fonctions cool des Rects (move, clamp, ...)

        #compteur pour l'accélération
        self.accelCounter = ACCEL_PERIOD
        #accélération à (0, 0)
        self.currentAccel = pyRect()

        #compteur pour le mouvement
        self.moveCounter = MOVE_PERIOD
        #mouvement à (0, 0)
        self.speed = pyRect()


    def resetToLevelOne(self):
        """
        initialise/réinitialise le level à 1, et remet les caractéristiques dépendante du level
        à leur valeur initiale pourrite.
        """

        Magician.resetToLevelOne(self)

        #capacité d'accélération et vitesse limite.
        self.accelCap = ACCEL_CAP_INIT
        self.speedLimit = SPEED_LIMIT_INIT
        #définit un rect, centré sur 0, et ayant comme demi-longueur self.speedLimit
        #(voir corps de la fonction)
        self.defineSpeedLimitClampingFromSpeedLimit()

        #compteur por la période d'augmentation du niveau
        self.levelUpCounter = LEVEL_UP_PERIOD

        self.respectLine = RESPECT_LINE_INIT

        #mouvement et accélération à (0, 0).
        #et init des compteurs pour les périodes de move et d'accel
        self.razMovementAndAcceleration()


    def defineSpeedLimitClampingFromSpeedLimit(self):
        """
        définit l'attribut self.speedLimitClamping, en fonction de l'attribut self.speedLimit
        self.speedLimitClamping est un rect centré sur 0,
        et ayant comme demi-longueur self.speedLimit
        on pourra s'en servir pour limiter la vitesse courante,
        qui doit rester dans les valeurs de speedLimit.
        Et y'aura juste besoin d'un simple clamping, plutôt qu'un tas de if à la con.
        """

        #on définit spd, juste pour raccourcir le nom, sinon c'est chiant.
        spd = self.speedLimit
        #le rect va du point (-spd, -spd) jusqu'au point (+spd, +spd)
        self.speedLimitClamping = pyRect(-spd, -spd, 2*spd, 2*spd)


    def levelUp(self):
        """
        Le magicien fait un levelUp et il monte ses caractéristiques.
        """

        Magician.levelUp(self)

        #on recule la respectLine
        self.respectLine -= REPECT_LINE_LEVELUP_DECREMENT

        #augmentation de la vitesse limite.
        if self.speedLimit < SPEED_LIMIT_MAX:
            self.speedLimit += 1
            #la speedLimit a changé, donc on doit redéfinir le rect de clamping de speedLimit.
            self.defineSpeedLimitClampingFromSpeedLimit()

        #augmentation de la capacité d'accélération.
        if self.accelCap < ACCEL_CAP_MAX:
            self.accelCap += 1


    def hitByBulletButNotDead(self, Damage):
        """
        fonction définissant les actions à faire quand le magicien s'est pris
        des bullets, mais qu'il n'en est pas mort. (il est HURT)

        entrées :
            Damage. int. Nombre de points de dégâts ( = nombre de bullets qui le touchent)
        """

        Magician.hitByBulletButNotDead(self, Damage)

        #on choisit dans le dico DIC_HURTINFOMOV_FROM_DAMAGE une période, et une liste
        #de mouvement de recul, en fonction du Damage que se prend le magicien.
        #Il y a une période et une liste par défaut, si jamais le dico est pas assez complet.
        (self.hurtPeriod,
         self.listMovementXWhenHurt,
        ) = DIC_HURTINFOMOV_FROM_DAMAGE.get(Damage, DEFAULT_HURTINFOMOV)

        #compteur pour la période de mouvement
        self.hurtCounter = self.hurtPeriod
        #curseur sur le mouvement de recul en cours, dans la liste. (qu'on parcourt à l'envers
        #mais ça je l'ai déjà dit)
        self.hurtMovementCursor = len(self.listMovementXWhenHurt) - 1


    def updateNormal(self):
        """
        update du magicien (fonction à lancer à chaque cycle de jeu)
        cas où le magicien est dans son état normal (ALIVE)
        """

        Magician.updateNormal(self)

        # --- gérage de l'accélération et de la vitesse ---

        self.accelCounter -= 1

        if self.accelCounter == 0:

            self.accelCounter = ACCEL_PERIOD
            #on redéfinit l'accélération, avec des valeurs au hasard,
            #bornée à la capacité d'accélération.
            self.currentAccel = pyRect(centeredRandom(self.accelCap),
                                       centeredRandom(self.accelCap))

        #application de l'accélération à la vitesse.
        self.speed.move_ip(self.currentAccel.topleft)
        #clampage de la vitesse, pour qu'elle ne dépasse pas la vitesse limite,
        #ni en X, ni en -X, ni en Y, ni en -Y. (C'est rigolo ce que je dis)
        self.speed.clamp_ip(self.speedLimitClamping)

        # --- gérage de la position, en fonction de la vitesse. ---

        self.moveCounter -= 1

        if self.moveCounter == 0:

            self.moveCounter = MOVE_PERIOD

            #application de la vitesse sur la position du magicien
            self.rect.move_ip(self.speed.topleft)

            #ajout du petit mouvement vers la droite si le magicien
            #est à gauche de la RespectLine
            if self.rect.left < self.respectLine:
                self.rect.x += RESPECT_LINE_MOVEMENT

            #ajout du mouvement vers la gauche si sorti de l'écran à droite
            if self.rect.right > GAME_RECT.right:
                self.rect.x -= BORDER_RIGHT_MOVEMENT

            #ajout du mouvement vers le haut si sorti de l'écran en bas
            if self.rect.bottom > GAME_RECT.bottom:
                self.rect.y -= BORDER_BOTTOM_MOVMENT

            #clampage pour que le magicien reste (à peu près) dans l'écran
            self.rect.clamp_ip(MAGI_RECT_CLAMPING)

            #rien n'est fait pour éloigner le magicien d'un bord de l'écran en haut et à gauche.
            #Du coup, il peut y rester coller pendant un certain temps.
            #je trouve ça rigolo, ça fait comme une mouche à merde qui s'acharne contre une vitre.

        # --- gérage du LeveUp (uniquement si le level en cours n'a pas atteint LEVEL_MAX ---

        if self.level < LEVEL_MAX:

            self.levelUpCounter -= 1

            if self.levelUpCounter == 0:
                self.levelUpCounter = LEVEL_UP_PERIOD
                self.levelUp()


    def updateHurt(self):
        """
        update du magicien (fonction à lancer à chaque cycle de jeu)
        cas où le magicien s'est pris une/plusieurs bullet. (HURT)

        le magicien a un mouvement de recul, tous les X cycles.
        Puis il revient à l'état ALIVE
        """

        #là, on n'exécute pas la super-classe. Sinon le magicien se fait unHurt
        #tout de suite, et c'est pas ce qu'on veut.

        self.hurtCounter -= 1

        if self.hurtCounter <= 0:

            self.hurtCounter = self.hurtPeriod

            #on récupère la distance de mouvement du Hurt, et on le fout en deplacement X
            #pas de déplacement Y pendant un HURT. osef.
            moveXHurt = self.listMovementXWhenHurt[self.hurtMovementCursor]
            moveHurt = pyRect(moveXHurt, 0)

            #application du mouvement du Hurt, et clamping du magicien dans l'écran.
            self.rect.move_ip(moveHurt.topleft)
            self.rect.clamp_ip(MAGI_RECT_CLAMPING)

            #déplacement du curseur pointant sur le mouvement de Hurt courant.
            self.hurtMovementCursor -= 1

            #Si le curseur arrive au début de la liste, on a fait tous les mouvements
            #de recul du Hurt. Le magicien revient à son état normal (ALIVE)
            if self.hurtMovementCursor == 0:

                #on réinitialise son mouvement et son accélération à (0, 0) (bien fait !)
                self.razMovementAndAcceleration()
                self.unHurt()
