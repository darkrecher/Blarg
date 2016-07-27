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

date de la dernière relecture-commentage : 14/10/2010

putain de grosse classe qui gère le Héros.
Les sprites de la tête et du corps. Les actions, les états, ...

Un peu de vocabulaire :

clamping : contrainte imposée à un objet rectangulaire, pour le forcer
à rester dans un rectangle englobant.
L'objet "héros" est clampingué dans le rectangle de l'écran du jeu.

rearm : action de faire schla-schlak le fusil à pompe, pour virer
la douille après avoir tiré une cartouche.

recharge/reload : remettre des cartouches dans le fusil.
(quand il est complètement vide, ou quand il est pas
complètement plein)

stimuli : valeur booléenne correspondant à une action
que peut faire le héros (ex : tirer, recharger).
si la valeur est True : le héros a reçu un signal
indiquant qu'il doit faire l'action correspondante.
(l'origine du signal est indéterminée mais osef).
Selon son état, le héros va faire l'action tout de suite, ou pas.
Lorsqu'il est reçu et accepté, un stimuli est toujours gardé en mémoire
jusqu'à ce qu'il soit traité.

Note importante : on dit "un stimuli" et "des stimulis"
le premier bouffon qui vient me ressortir des cours de latin,
je les lui fait bouffer.

Je viens de cracher un giga-mollard dans mon mouchoir. Super classe.
Je crois que tous mes voisins de bus me prennent pour un azertyuiop. osef.
"""

import pygame

from common import (GAME_RECT, pyRect, oppRect, randRange,
                    NONE_COUNT, HERO_LIFE_POINT_INITIAL,
                    STIMULI_HERO_MOVE, STIMULI_HERO_FIRE, STIMULI_HERO_RELOAD)

from cobulmag import CollHandlerBulletMagi
from sprsigen import SpriteSimpleGenerator

import herobody
import herohead
from scoremn import ScoreManager

from yargler import (theSoundYargler, SND_GUN_REARM, SND_GUN_FIRE,
                     SND_HERO_HURT, SND_GUN_RELOAD, SND_HERO_DIE)

#nombre maximum de cartouche dans le flingue.
#(Avant que le héros ne doive obligatoirement recharger)
NBR_MAX_CARTOUCHE = 8

#largeur et hauteur globale du héros. Ca servira pour le clamping du héros dans l'aire de jeu
#Ces hauteur et largeur sont indépendante des sprites qui composent le héros
HERO_WIDTH  = 23
HERO_HEIGHT = 32

# --- décalages (X, Y), lorsque le héros est dans l'état "NORMAL" ---

#décalage entre la position du héros et le sprite du corps du héros
DECAL_POS_BODY = pyRect(0, 8)
#décalage entre la position du héros et le sprite de la tête du héros
DECAL_POS_HEAD = pyRect(4, 0)
#décalage entre la position du héros et le point d'où
#partent les bullets du flingue
DECAL_POS_FIRE = pyRect(23, 19)
#décalage entre la position du héros et le point d'où partent les
#Little Shell (les douilles qui tombent).
DECAL_POS_LITTLESHELL = pyRect(5, 6)

# --- décalage à appliquer au sprite du corps du héros, lorsqu'on change l'image
#de ce sprite. (car le coin supérieur gauche de chaque image ne correspond pas
#tout à fait au même endroit du corps du héros). ---

#les iimages mentionnées ici sont les images de la classe HeroBody
#décalage quand on passe de l'image "NORMAL" à l'image "HURT"
DECAL_NORM_HURT     = pyRect(+4,  0)
#décalage quand on passe de l'image "NORMAL" à l'image "RAISE_A"
DECAL_NORM_RAISE1   = pyRect(+3, -1)
#décalage quand on passe de l'image "RAISE_A" à l'image "RAISE_B"
DECAL_RAISE1_RAISE2 = pyRect(+1, -5)
#décalage quand on passe de l'image "RAISE_B" à "ARMINGE"
DECAL_RAISE2_ARM    = pyRect( 0, +1)

#memes décalage, mais les images d'arrivée et de départ sont inversés
#on les détermine en prenant les coordonnées opposées des décalages correspondants
DECAL_HURT_NORM     = oppRect(DECAL_NORM_HURT)
DECAL_RAISE1_NORM   = oppRect(DECAL_NORM_RAISE1)
DECAL_RAISE2_RAISE1 = oppRect(DECAL_RAISE1_RAISE2)
DECAL_ARM_RAISE2    = oppRect(DECAL_RAISE2_ARM)
#TRODO : je l'ai déjà dit mais c'est de la merde ces décalages.
#Ils ont rien à foutre là en fait. C'est le HeroBody qui devrait les gérer.

#liste de rect.
#indique la distance de recul à appliquer sur le héros.
#elem 1 : distance X de recul immédiatement après le tir.
#elem 2 : distance X de recul un cycle de jeu après le tir.
#Si on met plus d'élément, ce sera pas géré. (osef)
#là j'ai pas mis de recul en Y, mais je pourrais.
FIRE_RECUL = (pyRect(-4), pyRect(-2))

#identifiant des stimulis que peut recevoir le héros dans sa gueule.
#FIRE : le héros doit tirer
#RELOAD : le héros doit recharger
#il y a également le stimuli "Hurt", quand le héros se fait toucher par un magicien.
#mais celui là doit être immédiatement pris en compte quand il est reçu. donc pas la peine
#de le stocker en mémoire.
(FIRE, RELOAD) = range(2)

#identifiant des états du héros
#voir fonction definestateMachine pour leur description.
(NORMAL,
 RAISE_ARMING_1,
 RAISE_ARMING_2,
 LOWER_1,
 LOWER_2,
 FIRING,
 ARMING,
 ARMED,
 RAISE_REL_1,
 RAISE_REL_2,
 RELOADING_1,
 RELOADING_2,
 HURT,
 DYING,
 DEAD,
) = range(15)

#si on veut faire du debug : utiliser cette liste plutot qu'un range.
#("NORMAL", "RAISE_ARMING_1", "RAISE_ARMING_2", "LOWER_1", "LOWER_2", "FIRING", "ARMING", "ARMED",
# "RAISE_REL_1", "RAISE_REL_2", "RELOADING_1", "RELOADING_2", "HURT", "DYING", "DEAD")

#liste des états durant lesquels on ne prend pas en compte le stimuli de FIRE
#car le héros est déjà en train de tirer, ou il vient de le faire,
#ou il se fait cogner dessus (HURT)
LIST_STATE_NO_STIMULI_FIRE = (RAISE_ARMING_1, RAISE_ARMING_2,
                              FIRING, ARMING, ARMED, HURT)

#identifiant plus cool pour plus de clarté.
#c'est utilisé dans les petites fonctions liés à la machine à état.
#il faut pouvoir indiquer à la fonction principale de la machine si
#l'une de ces fonctions a changé l'état, ou pas.
FUNCTION_CHANGED_STATE = True
FUNCTION_DID_NOT_CHANGED_STATE = False

# --- valeurs pour gérer le mouvement de recul du héros quand il est HURT ---

#TRODO : ouais, un movingPoint avec une position, un mouvement initial, et une accélération,
#Ce serait pas mal. (Genre un dérivé de movingPoint.)
#Pour la version 2. De toutes façon le plus urgent ce sera pas ça, mais les hotPoint de merde
#fun fact : j'ai passé certainement plus de temps à expliquer dans les commentaires que
#mon manque de gestion des hotPointest merdique, que je n'en aurais passé à ajouter cette gestion.

#distance (X ou Y) minimale nécessaire entre le héros et le magicien qui l'a touché, pour que
#le héros fasse un mouvement de recul sur l'axe (X ou Y) concerné.
HURT_RECUL_DIST = 8

#valeurs initiale du mouvement. Dans le cas où le mouvement est droit, ou en diagonale
HURT_MOVE_INIT_STRAIGHT = 5
HURT_MOVE_INIT_DIAG = 3

#décélération du mouvement. Dans le cas où le mouvement est droit, ou en diagonale
HURT_DECEL_STRAIGHT = 2
HURT_DECEL_DIAG = 1

#période de mouvement (nbre de cycle)
HURT_MOVE_PERIOD = 2

#période de décélération (nbre de cycle)
HURT_DECEL_PERIOD = 4

#nombre de mouvement de recul à effectuer
HURT_NBR_MOVE = 5

#décalage entre la position du héros, et le point de départ des giclures de sang
#(ce décalage est prévu avec le corps du héros dans l'état HURT.
DECAL_HURT_BLOOD = pyRect(8, 0)

#nombre de giclures de sang à balancer quand le héros se fait HURT.
#(Quand HURT, il n'y a qu'une giclure, mais elle est grosse)
NBR_BLOOD_HURT  = 30

#nombre de giclures de sang à balancer quand le héros est DYING.
#(Quand DYING, il y a plusieurs petites giclures de sang successives, et en même temps,
#le héros tourne la tête)
NBR_BLOOD_DYING =  10

#délai (nombre de cycle) entre deux petites giclures de sang de l'état DYING.
#à chaque fois, le délai est calculé en random entre les valeurs min et max.
DELAY_BLOOD_DYING_MIN =  5
DELAY_BLOOD_DYING_MAX = 30



class Hero():
    """
    Le mec avec le shotgun, qu'on le dirige. Bordel.
    """

    def __init__(self, dicHeroBodyImg, dicHeroHeadImg, coordStart,
                 collHandlerBulletMagi, spriteSimpleGenerator,
                 ammoViewer, lifePointViewer, scoreManager, dogDom):
        """
        constructeur. (thx captain obvious)

        entrée :
            dicHeroBodyImg : dictionnaire de correspondance
                             identifiant d'image -> image du corps
            dicHeroHeadImg : dictionnaire de correspondance
                             identifiant d'image -> image de la tête
            coordStart     : tuple (X, Y). Coordonnées initiale du héros
            collHandlerBulletMagi : classe gérant les collisions
                                    entre les bullets tirées par le héros et les magiciens
            spriteSimpleGenerator : classe éponyme. permet de générer des SimpleSprite,
                                    par exemple, la flamme du flingue.
            ammoViewer            : classe épongiforme. affichage des cartouches dans le flingue.
            lifePointViewer       : classe épongiforme. affichage des points de vie.
            scoreManager          : classe poney-ime. gestion du score, des hiscore, ...
            dogDom                : boolean. Indique si le héros perd des vies ou pas.
        """

        self.collHandlerBulletMagi = collHandlerBulletMagi
        self.spriteSimpleGenerator = spriteSimpleGenerator
        self.ammoViewer = ammoViewer
        self.lifePointViewer = lifePointViewer
        self.scoreManager = scoreManager
        self.dogDom = dogDom

        #initialisation du dictionnaire de correspondance stimuli -> fonction à exécuter
        self.dicFuncFromStimuli = {
            STIMULI_HERO_MOVE   : self.addMoveInBuffer,
            STIMULI_HERO_FIRE   : self.takeStimuliFire,
            STIMULI_HERO_RELOAD : self.takeStimuliReload,
        }

        #création d'un Rect donnant la position X, Y du héros, et sa taille globale
        self.rectPos = pyRect(coordStart.x, coordStart.y,
                              HERO_WIDTH, HERO_HEIGHT)

        #self.areaAuthorized est donc le rectangle dans lequel la position
        #du héros a le droit d'être.
        self.areaAuthorized = pygame.Rect(GAME_RECT)

        #clamping un peu crade, que je fais manuellement dans makeBufferMove.
        #la zone de mouvement du héros est diminué en bas à droite de la taille du héros.
        #Comme ça on gère le clamping uniquement avec une position X,Y
        #et non pas un rectangle avec une pos X, Y et une taille.
        #Si la taille du héros change pendant le jeu, ça pète. Mais comme ça n'arrive pas, osef.
        self.areaAuthorized.width -= HERO_WIDTH
        self.areaAuthorized.height -= HERO_HEIGHT

        # ------ Init du corps et de la tête du héros ---------

        #on applique une seule fois au début le décalage de coordonnées
        #entre le héros et le corps du héros
        rectHeroBody = self.rectPos.move(DECAL_POS_BODY.topleft)
        self.heroBody = herobody.HeroBody(dicHeroBodyImg, rectHeroBody)
        #pareil pour la tête : on applique une seule fois au début le décalage.
        rectHeroHead = self.rectPos.move(DECAL_POS_HEAD.topleft)
        self.heroHead = herohead.HeroHead(dicHeroHeadImg, rectHeroHead)

        # ------ Init de plein de variables importantes ---------

        #variables int indiquant les mouvements du héros à faire
        #au prochain cycle
        self.rectMoveBuffer = pyRect()

        #liste contenant l'état des stimulis (FIRE, RECHARGE)
        self.stimuli = [False, False]

        #variable compteur. Indique le nombre de cycle de jeux avant
        #le prochain changement automatique d'état, (si il y a changement auto à faire)
        self.stateTimer = NONE_COUNT

        #variable indiquant l'identifiant de l'état en cours.
        self.currentState = NORMAL

        #nombre de cartouche en cours dans le flingue.
        self.nbrCartouche = NBR_MAX_CARTOUCHE

        #les points de vie
        self.lifePoint = HERO_LIFE_POINT_INITIAL

        #boolean qui indique si le héros doit réarmer ou pas.
        self.mustRearm = False

        #crac boum !! définition de la mega machine à état.
        self.definestateMachine()


    def addMoveInBuffer(self, rectMove):
        """
        ajoute un mouvement à faire pour le héros.
        le mouvement n'est pas effectif tout de suite,
        il faut exécuter MakeBufferMove

        entrée : rect(X, Y) : coordonnées du mouvement (int)
        """
        self.rectMoveBuffer.move_ip(rectMove.topleft)


    def makeBufferMove(self):
        """
        bouge le héros selon ce qu'on lui a foutu dans son buffer de mouvement.
        clampage manuel dans le rectangle areaAuthorized

        y'a des tests tout pouillave, je sais qu'il existe le rect.clamp,
        mais c'est utile que si t'as des sprite unique qui se baladent.
        Là j'ai un héros avec deux sprites. Donc pas mieux.
        """

        # --- contrôle du clamping ---
        #le but de ces contrôles sera de réajuster les valeurs de mouvement
        #self.rectMoveBuffer, de façon à ce que le mouvement
        #ne fasse plus sortir le héros de l'écran.

        #clamping X, sur le mur gauche. A faire si je dois bouger à gauche, et que ma
        #position d'arrivée après ce mouvement dépasse la limite du mur gauche de areaAuthorized:
        if self.rectMoveBuffer.x < 0 and \
           self.rectPos.x + self.rectMoveBuffer.x < self.areaAuthorized.left:

            #il faut réajuster le mouvement pour arriver à la limite du mur.
            #Si le héros a déjà dépassé le mur gauche, ça va créer un
            #mouvement inverse qui le fait revenir à la limite.
            #ça arrive jamais. Mais si ça arrivait, ça serait normal.
            self.rectMoveBuffer.x = self.areaAuthorized.left - self.rectPos.x

        #les autrse clampings, c'est pareil. Je répète pas les commentaires.
        #je raconte déjà assez de conneries comme ça.

        #clamping X, sur le mur droit
        if self.rectMoveBuffer.x > 0 and \
           self.rectPos.x + self.rectMoveBuffer.x > self.areaAuthorized.right:

            self.rectMoveBuffer.x = self.areaAuthorized.right - self.rectPos.x

        #clamping Y, sur le mur du haut
        if self.rectMoveBuffer.y < 0 and \
           self.rectPos.y + self.rectMoveBuffer.y < self.areaAuthorized.top:

            self.rectMoveBuffer.y = self.areaAuthorized.top - self.rectPos.y

        #clamping Y, sur le mur du bas
        if self.rectMoveBuffer.y > 0 and \
           self.rectPos.y + self.rectMoveBuffer.y > self.areaAuthorized.bottom:

            self.rectMoveBuffer.y = self.areaAuthorized.bottom - self.rectPos.y

        #antislash de merde... çay moche

        # --- application du mouvement, maintenant qu'il est réajusté par le clamping ---
        #il faut appliquer le mouvement sur tous les trucs à bouger.
        #position du héros
        self.rectPos.move_ip(self.rectMoveBuffer.topleft)
        #position du corps du héros
        self.heroBody.rect.move_ip(self.rectMoveBuffer.topleft)
        #position de la tête du héros
        self.heroHead.rect.move_ip(self.rectMoveBuffer.topleft)

        #remise à zero des buffers de mouvement.
        self.rectMoveBuffer.topleft = (0, 0)


    def definestateMachine(self):
        """
        putain de dictionnaire gérant les différents états du héros.

        clé : identifiant de l'état
        valeur : putain de gros tuple, contenant les
                 infos correspondantes à cet état
          0) identifiant de l'image du corps.
          1) fonction à exécuter si on a reçu le stimuli FIRE.
             Ou None. Dans ce cas on ne fait rien et on garde le stimuli en reserve
          2) fonction à exécuter si on a reçu le stimuli RELOAD.
             Ou None. Dans ce cas on ne fait rien et on garde le stimuli en reserve
          3) temps d'attente avant le changement automatique vers l'état suivant.
             si c'est NONE_COUNT : pas de changement automatique
          4) identifiant de l'état suivant, pour le changement auto.
             si c'est None, pas de changement automatique.
          5) tuple (X,Y) de décalage du sprite HeroBody lors du changement auto.
             Ou None. Dans ce cas, pas de décalage.
          6) fonction à exécuter juste avant le changement auto.
             Ou None. Dans ce cas, pas de fonction à exécuter.
          7) fonction à exécuter à chaque cycle, tant qu'on est dans cet état
             Ou None. Dans ce cas, pas de fonction à exécuter à chaque cycle.

        les états sont configurés pour respecter les règles suivantes :
         - on réarme immédiatement et obligatoirement juste après avoir tiré.
           Mais le rearm peut être reporté suite à un HURT
           (le héros s'est pris un coup dans la gueule)
         - il faut lever le flingue pour réarmer, et aussi pour recharger.
           on peut faire les deux à la suite, (réarmer puis recharger) quand le flingue est levé
         - quand on commence de recharger, on le fait jusqu'à ce que le flingue soit rempli,
           sauf si on reçoit le stimuli FIRE pendant qu'on recharge. Dans ce cas,
           on abaisse le flingue et on tire.
         - on commence obligatoirement le rechargement quand il n'y a plus aucune cartouche
         - y'a pas de réarmement après avoir rechargé. On voit ça dans certains jeux,
           et je trouve ça bizarre. (c'est peut être comme ça en vrai. mais m'en fout)
         - on peut pas tirer si y'a plus de cartouche (thx cptn obvious), même avec
           le stimuli FIRE.
        """

        self.stateMachine = {
            NORMAL           : (
                #etat normal. Le héros ne tire pas et ne recharge pas.
                herobody.IMG_NORMAL,
                self.fire,            self.startReload,    NONE_COUNT,
                None,                 None,                None,
                None),

            FIRING           : (
                #le héros est en train de tirer.
                herobody.IMG_NORMAL,
                None,                 None,                3,
                RAISE_ARMING_1,       DECAL_NORM_RAISE1,   self.fireRecul,
                None),

            RAISE_ARMING_1   : (
                #le héros et en train de lever le flingue (img 1) afin de réarmer.
                herobody.IMG_RAISE_A,
                None,                 None,                3,
                RAISE_ARMING_2,       DECAL_RAISE1_RAISE2, None,
                None),

            RAISE_ARMING_2   : (
                #le héros et en train de lever le flingue (img 2) afin de réarmer.
                herobody.IMG_RAISE_B,
                None,                 None,                3,
                ARMING,               DECAL_RAISE2_ARM,    self.arming,
                None),

            ARMING           : (
                #le héros réarme. schla-schlak !!
                herobody.IMG_ARMINGE,
                None,                 None,                7,
                ARMED,                DECAL_ARM_RAISE2,    self.armingIsDone,
                None),

            LOWER_1          : (
                #le héros est en train de rabaisser le flingue (img 1)
                herobody.IMG_RAISE_A,
                None,                 None,                2,
                NORMAL,               DECAL_RAISE1_NORM,   None,
                None),

            LOWER_2          : (
                #le héros est en train de rabaisser le flingue (img 2)
                herobody.IMG_RAISE_B,
                None,                 None,                2,
                LOWER_1,              DECAL_RAISE2_RAISE1, None,
                None),

            ARMED            : (
            #le héros a le flingue levé. Il vient de réarmer.
            #A la fin de cet état, on rabaisse le flingue, ou on commence un
            #rechargement si on a le stimuli RELOAD
                herobody.IMG_RAISE_B,
                None,                 None,                3,
                LOWER_1,              DECAL_RAISE2_RAISE1, self.reloadPerhaps,
                None),

            RAISE_REL_1      : (
            #le héros et en train de lever le flingue (img 1) afin de recharger.
                herobody.IMG_RAISE_A,
                self.fireIfGotShell, None,                 3,
                RAISE_REL_2,         DECAL_RAISE1_RAISE2,  None,
                None),

            RAISE_REL_2      : (
            #le héros et en train de lever le flingue (img 2) afin de recharger.
                herobody.IMG_RAISE_B,
                self.fireIfGotShell, None,                 3,
                RELOADING_1,         None,                 None,
                None),

            RELOADING_1      : (
                #le héros recharge (img 1)
                herobody.IMG_RELOAD_A,
                self.fireIfGotShell, None,                 8,
                RELOADING_2,         None,                 None,
                None),

            RELOADING_2      : (
                #le héros recharge (img 2)
                #l'ajout effectif de la cartouche dans le flingue se fait une fois
                #que cet état est terminé.
                herobody.IMG_RELOAD_B,
                self.fireIfGotShell, None,                8,
                LOWER_2,             None,                self.reloadOneShell,
                None),

            HURT             : (
                #le héros s'est pris un coup dans la gueule.
                herobody.IMG_HURT,
                None,                None,                 32,
                NORMAL,              DECAL_HURT_NORM,      self.endOfHurt,
                self.makeHurtMovement),

            DYING            : (
                #le héros est en train de crever.
                herobody.IMG_HURT,
                None,                None,                 120,
                DEAD,                None,                 self.endOfDying,
                self.updateDying),

            DEAD             : (
                #le héros a crevé.
                herobody.IMG_HURT,
                None,                None,                NONE_COUNT,
                None,                None,                None,
                None),
        }


    def advanceStateOneStep(self):
        """
        fonction a exécuter à chaque cycle de jeu.
        elle gère toute la machine à état du héros.
        """

        #récupération de toutes les infos de l'état courant, à partir du dictionnaire
        #de la machine à état.
        (stateImg, functionStimuliFire, functionStimuliReload,
         stateTimerInitial, nextState, rectDecalageImgNextState,
         functionEndState, functionEachCycle,
        ) = self.stateMachine[self.currentState]

        #exécution de la fonction correspondante au stimuli FIRE, si il
        #y en a une dans l'état courant, et si on a le stimuli
        if functionStimuliFire is not None and self.stimuli[FIRE]:
            #on exécute la fonction, et on regarde si elle s'est occupée elle-même de faire
            #un changement d'état, alors, on n'a plus rien à faire pour
            #ce cycle de jeu, et on quitte tout de suite.
            #sinon, il faut continuer de gérer l'état courant.
            if functionStimuliFire() == FUNCTION_CHANGED_STATE:
                return

        #pareil mais avec le RELOAD
        if functionStimuliReload is not None and self.stimuli[RELOAD]:
            #pareil
            if functionStimuliReload() == FUNCTION_CHANGED_STATE:
                return

        #gestion éventuelle du changement automatique d'état.
        if nextState is not None:

            self.stateTimer -= 1

            if self.stateTimer == 0:

                #On doit faire un changement automatique d'état.

                if functionEndState is not None:

                    #il y a une fonction à exécuter avant le changement d'état auto, on l'exécute.
                    if functionEndState() == FUNCTION_DID_NOT_CHANGED_STATE:

                        #si la fonction ne s'est pas occupée elle-même de faire un
                        #changement d'état, alors il faut faire le changement auto, comme prévu.
                        #sinon, on n'a plus rien à faire.
                        self.changeState(nextState, rectDecalageImgNextState)

                else:

                    #quand y'a pas de fonction à lancer à la fin d'un état, on se contente
                    #d'effectuer le changement automatique vers l'état suivant
                    self.changeState(nextState, rectDecalageImgNextState)

        #exécution de la fonction à exécuter à chaque cycle. Si il y en a une.
        if functionEachCycle is not None:
            functionEachCycle()


    def changeState(self, nextState, rectDecalageImg=None):
        """
        fonction à exécuter pour passer d'un état à un autre. (lors d'un changement
        automatique d'état, ou à une autre occasion quelconque. Genre un goûter-cocktail)

        entrée :
          nextState : identifiant de l'état suivant

          rectDecalageImg : rect(X,Y) de décalage de merde à appliquer au corps du héros.
                            pour pas que ça fasse des petits mouvements bizarres.
                            (géré à l'arrache)
                            Si None, pas de décalage à appliquer
        """

        #récupération des infos de l'état suivant (pas l'état courant, osef)
        #On n'a pas besoin de choper toute les infos. que les trucs du début.
        #d'où le [:4]
        (imgIdState, functionStimuliFire, functionStimuliReload,
         stateTimerInitial,
        ) = self.stateMachine[nextState][:4]

        #on réinitialise le compteur de changement auto d'état avec celui de l'état suivant.
        self.stateTimer = stateTimerInitial
        #on redéfinit la valeur de l'état courant.
        self.currentState = nextState
        #on change l'image du héros, en appliquant éventuellement le décalage.
        # BIG BIG TRODO : la gestion des décalages doit pas être faite comme ça
        # C'est vraiment pourri. Il faut que ce soit HeroBody qui le gère.
        # Avec un dictionnaire { ( img_avant, img_après) : valeur_decalage }
        self.heroBody.changeImg(imgIdState, rectDecalageImg)

    #je m'en souviens de ces trucs. Ca m'a fait bizarrrrrrre......

    def takeStimuliFire(self):
        """
        active le stimuli pour tirer un coup de fusil. pan !!!
        Le héros tire tout de suite si possible
        Le stimuli n'est pas pris en compte si le héros est déjà en train de tirer ou de réarmer.
        Ca permet d'éviter que 2 coups soient tirés si le joueur appuie un peu trop longtemps.
        Car de manière générale, les stimulis sont enregistrés pour plus tard si ils ne sont
        pas traitable tout de suite.
        """
        if self.currentState not in LIST_STATE_NO_STIMULI_FIRE:
            self.stimuli[FIRE] = True


    def takeStimuliReload(self):
        """
        active le stimuli pour recharger les cartouches. shlink shink shlink
        Le héros rechargera tout de suite si possible, sinon on remettra ça à plus tard.
        On ne prend pas en compte le stimuli si le fusil est déjà chargé au max
        On le prend pas non plus en compte si le héros est HURT
        """
        if self.nbrCartouche < NBR_MAX_CARTOUCHE and self.currentState != HURT:
            self.stimuli[RELOAD] = True


    def takeStimuliGeneric(self, idStimuli, param):
        """
        permet de recevoir un stimuli venant du joueur. N'importe quel stimuli

        entrée :
             idStimuli : identifiant du stimuli qu'on reçoit (move, fire, reload)
             param : tuple. liste des param du stimuli. (ça peut être un tuple vide)
        """

        #on récupère la fonction correspondante au stimuli
        func = self.dicFuncFromStimuli[idStimuli]
        #on exécute cette fonction avec les param fournis.
        func(*param)


    def fire(self):
        """
        Tire un coup de fusil. (Si cela est possible)
        Pan !!!

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        #il faut avoir au moins une cartouche pour tirer
        if self.nbrCartouche == 0:
            #on ne peut pas tirer. Donc on ne change pas d'état.
            #La gestion de la stateMachine s'occupe du reste.
            return FUNCTION_DID_NOT_CHANGED_STATE

        #il reste au moins une cartouche.
        #on change l'état du héros pour qu'il tire un coup (ha ha ha)
        self.changeState(FIRING)
        #on fait bouger le héros avec la première valeur de recul.
        self.addMoveInBuffer(FIRE_RECUL[0])
        #une cartouche en moins.
        self.nbrCartouche -= 1
        #indication à l'afficheur des cartouches que y'a eu un coup de feu.
        self.ammoViewer.takeStimuliFire()
        #le son du coup de feu : pan!!
        theSoundYargler.playSound(SND_GUN_FIRE)
        #on garde en souvenir qu'il faut réarmer
        #(si jamais le héros ne peut pas le faire immédiatement après,
        #genre si il se fait hurt ou une connerie comme ça)
        self.mustRearm = True

        #on détermine d'où partent les bullets
        posFire = self.rectPos.move(DECAL_POS_FIRE.topleft)

        #gestion de la collision des bullets avec les magiciens
        #le CollisionHandler calcule les trajectoires des balles, avertit les
        #magiciens touchés, qui indiquent si ils sont morts ou explosés.
        #le CollisionHandler renvoie un tuple contenant le nombre de magiciens explosés
        #et le nombre tués. Tout cela se passe de manière instantanée, hop paf crac.
        scoreTuple = self.collHandlerBulletMagi.heroFiresBullets(posFire)

        if scoreTuple != (0, 0):

            #y'a eu des morts chez les magiciens
            (addMagiBurst, addMagiKilledNotBurst) = scoreTuple
            #on enregistre ces morts dans le scoreManager
            self.scoreManager.updateScore(addMagiBurst, addMagiKilledNotBurst)

            #si au moins un magicien a été explosé, la tête du héros sourit
            #(le sourire s'arrêtera automatiquement au bout d'un certain temps
            if addMagiBurst > 0:
                self.heroHead.startSmiling()

        #affichage du sprite de la flamme. On la place à la position du tir,
        #mais on tient compte de la première valeur de recul. Ca fait plus mieux à l'oeil.
        #C'est un peu crade car j'utilise cette valeur de recul à deux endroits différents :
        #une fois pour bouger le héros, et une autre fois pour la flamme. Oh ça se tient en fait.
        posFlame = posFire.move(FIRE_RECUL[0].topleft)
        self.spriteSimpleGenerator.generateFlame(posFlame)

        #annulation du stimuli, puisqu'il a été pris en compte.
        self.stimuli[FIRE] = False
        #On a changé d'état. La stateMachine n'aura rien de plus à faire
        return FUNCTION_CHANGED_STATE


    def fireRecul(self):
        """
        Petite fonction un peu à la con, pour appliquer le reste du recul.
        Elle est exécuté à la fin du FIRE.

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        #on fait reculer de la deuxième valeur de recul de la liste
        # (moins importante que la première valeur)
        self.addMoveInBuffer(FIRE_RECUL[1])
        #y'a pas eu de changement d'état.
        return FUNCTION_DID_NOT_CHANGED_STATE


    def arming(self):
        """
        Fonction qui s'exécute quand le héros est en train de réarmer. (entre l'image
        de levage du flingue et l'image du réarmement).

        sortie : valeur FUNCTION_CHANGED_STATE ou FUNCTION_DID_NOT_CHANGED_STATE
        """
        #son : "shla-shlak !!"
        theSoundYargler.playSound(SND_GUN_REARM)
        #y'a pas eu de changement d'état.
        return FUNCTION_DID_NOT_CHANGED_STATE


    def armingIsDone(self):
        """
        Fonction qui s'exécute une fois que le héros a fait un rearm.
        (soit immédiatement après avoir tiré,
         soit que entre temps il s'est fait Hurt une ou plusieurs fois)

        sortie : valeur FUNCTION_CHANGED_STATE ou FUNCTION_DID_NOT_CHANGED_STATE
        """

        self.mustRearm = False
        #on prévient l'afficheur des cartouches que y'a eu un réarmement.
        #(Il va décaler les cartouches)
        self.ammoViewer.takeStimuliRearm()

        #génération d'un SimpleSprite : la petite cartouche qui part en tournoyant
        #derrière le héros.
        posLittleShell = self.rectPos.move(DECAL_POS_LITTLESHELL.topleft)
        self.spriteSimpleGenerator.generateLittleShell(posLittleShell)

        #y'a pas eu de changement d'état.
        return FUNCTION_DID_NOT_CHANGED_STATE


    def startReload(self):
        """
        Commence le rechargement du flingue.
        C'est la stateMachine qui gère toute seule le fait que le rechargement soit
        automatique, jusqu'à ce que le flingue soit plein.

         sortie : valeur FUNCTION_CHANGED_STATE ou
                         FUNCTION_DID_NOT_CHANGED_STATE
        """

        #on commence le rechargement que si le nombre de cartouche est pas au max.
        #(précaution un peu inutile car on prend pas le stimuli si on est au max.)
        #mais je préfère comme ça. "blindage double-épaisseur" comme dirait l'autre grand glandu
        if self.nbrCartouche < NBR_MAX_CARTOUCHE:
            #le héros commence à lever son flingue pour recharger.
            #(notez le passage en paramètre du décalage d'image pourri. J'en ai déjà parlé.)
            self.changeState(RAISE_REL_1, DECAL_NORM_RAISE1)
            #on a changé d'état
            return FUNCTION_CHANGED_STATE
        else:
            #on n'a rien fait
            return FUNCTION_DID_NOT_CHANGED_STATE


    def reloadOneShell(self):
        """
        fonction a exécuter quand le héros a pu recharger une cartouche dans le flingue.
        Elle est exécuté à la fin de l'état RELOADING_2

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        #une cartouche de plus !!!
        self.nbrCartouche += 1
        #on prévient l'afficheur de cartouche qu'il doit en rajouter une.
        self.ammoViewer.takeStimuliReload()
        #son de reloadage de cartouche : cli-clik.
        theSoundYargler.playSound(SND_GUN_RELOAD)

        if self.nbrCartouche < NBR_MAX_CARTOUCHE:
            #si il manque encore des cartouches, on repart au début de l'état du rechargeage
            #comme ça, ça fera encore une cartouche de plus dans quelques temps.
            self.changeState(RELOADING_1)
            #on a changé d'état
            return FUNCTION_CHANGED_STATE
        else:
            #y'a plus de cartouche à mettre. On supprime le stimuli de rechargement.
            self.stimuli[RELOAD] = False
            #on n'a pas changé d'état. Ca va se remettre tout seul à l'état NORMAL
            return FUNCTION_DID_NOT_CHANGED_STATE


    def reloadPerhaps(self):
        """
        fonction appelé après avoir tiré un coup et réarmé (le flingue est toujours levé).
        Elle permet de commencer un rechargement,
         - soit à l'arrache, si il n'y a plus du tout de cartouche dans le flingue
         - soit si le joueur a demandé un rechargement pendant le tir.

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        if self.nbrCartouche == 0 or self.stimuli[RELOAD]:
            #on passe directement à l'état de rechargement. On ne lève pas le flingue
            #pour recharger, car cela a déjà été fait.
            self.changeState(RELOADING_1)
            #un changement d'état a eu lieu.
            return FUNCTION_CHANGED_STATE
        else:
            #il s'est rien passé.
            return FUNCTION_DID_NOT_CHANGED_STATE


    def fireIfGotShell(self):
        """
        rabaisse le flingue pour tirer, alors que le héros est en train de
        recharger. Ne fait rien si y'a plus du tout de cartouche

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        #on peut pas tirer, même si le joueur l'a demandé. On fait rien
        #le rechargement va se continuer tout seul.
        if self.nbrCartouche == 0:
            #il s'est rien passé.
            return FUNCTION_DID_NOT_CHANGED_STATE

        #on oublie qu'on avait envie de recharger. (tirer est prioritaire)
        self.stimuli[RELOAD] = False

        #Pour prendre en compte le Fire, on se contente d'amorcer le baissage du flingue.
        #le stimuli de FIRE est toujours à True. Donc le tir se fera tout seul, quand
        #on sera revenu à l'état NORMAL.

        if self.currentState == RAISE_REL_1:
            #le héros avait à peine commencé de lever son flingue. On peut le rabaisser
            #directement tout de suite.
            self.changeState(NORMAL, DECAL_RAISE1_NORM)
        else:
            #le héros a le flingue complètement levé (et il est peut être même en train de
            #recharger. Donc il faut passer par l'étape intermédiaire pour abaisser le flingue.
            self.changeState(LOWER_1, DECAL_RAISE2_RAISE1)

        #on a changé d'état.
        return FUNCTION_CHANGED_STATE


    def takeStimuliHurt(self, posEnemy):
        """
        fonction qui s'exécute quand le héros s'est fait toucher par un magicien,
        et que donc il se prend un coup dans la gueule (il se fait HURT la gueule)

        entrées :
            posEnemy : rect(Xn Y) : position du magicien qui a fait mal au héro
                       cela permet de définir dans quelle direction de HURT le héro
                       doit bouger. (Il va aller dans le sens opposé au magicien)

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        if self.currentState in (HURT, DYING, DEAD):
            #on peut pas se faire HURT pendant qu'on est HURT, ni quand on crève.
            #Donc on quitte toute de suite, en signalant qu'il ne s'est rien passé.
            return FUNCTION_DID_NOT_CHANGED_STATE

        #supression d'un point de vie, sauf si mode spécial. Héhé.
        if not self.dogDom:
            #et paf ! on vire un point de vie au héro.
            self.lifePoint -= 1
            #hurt du lifepointviewer. permet de supprimer l'affichage d'un point de vie.
            self.lifePointViewer.takeStimuliHurt()

        #arrêtage de sourire si le héros était en train de sourire
        self.heroHead.stopSmiling()

        #on vire le stimuli RELOAD. Si le joueur était en train de recharger, il devra réappuyer
        #sur la touche de rechargeage. Bien fait.
        self.stimuli[RELOAD] = False
        #Oh et puis celui de Fire aussi, tant qu'à faire. Faut pas me faire chier.
        self.stimuli[FIRE] = False

        #calcul du mouvement de recul lié au Hurt.
        self.determineHurtMovement(posEnemy)

        #Gestion pourrie des décalages de sprite
        #A partir de l'état en cours, il faut "redescendre" progressivement les etats de
        #levage du flingue, jusqu'à arriver à l'état normal.
        #(en appliquant à chaque fois les décalages qui vont bien),
        #et enfin, on peut mettre l'image de HURT, avec le décalage NORM -> HURT
        #TRODO : les hotPoint, bien entendu.
        if self.currentState == ARMING:

            self.heroBody.rect.move_ip(DECAL_ARM_RAISE2.topleft)
            self.currentState = LOWER_2

        if self.currentState in [ RAISE_ARMING_2, RAISE_REL_2, ARMED,
                                  RELOADING_1, RELOADING_2, LOWER_2 ]:

            self.heroBody.rect.move_ip(DECAL_RAISE2_RAISE1.topleft)
            self.currentState = LOWER_1

        if self.currentState in [ RAISE_ARMING_1, RAISE_REL_1, LOWER_1 ]:

            self.heroBody.rect.move_ip(DECAL_RAISE1_NORM.topleft)
            self.currentState = NORMAL

        #détermination de la position de départ des giclures de sang. splatch !
        self.posBlood = self.rectPos.move(DECAL_HURT_BLOOD.topleft)

        if self.lifePoint >= 0:

            #Le héros n'est pas encore mort.
            #génération d'un gros tas de sang !!
            funcGenBlood = self.spriteSimpleGenerator.generateSomeBlood
            funcGenBlood(self.posBlood, NBR_BLOOD_HURT)

            #changement de l'etat vers HURT
            self.changeState(HURT, DECAL_NORM_HURT)
            #le son du héros qui a mal : argh !!
            theSoundYargler.playSound(SND_HERO_HURT)

        else:

            #le héros n'a plus de point de vie, il doit mouwwwriiiiiir. (etat = DYING)
            #initialisation du compteur de giclage de sang + tournage de tête
            #comme c'est à 0, ça va exécuter la fonction dyingBloodTurnHead tout de
            #suite après, et après ça recommencera et etc.
            self.counterBlood = 0

            #changement de l'etat.
            self.changeState(DYING, DECAL_NORM_HURT)

        #on a fait un changement d'état.
        return FUNCTION_CHANGED_STATE


    def endOfHurt(self):
        """
        fonction a exécuter à la fin de l'etat HURT. Il faut faire revenir le héros à
        l'état normal. Et prendre en compte les éventuels événements qu'on pouvait
        pas prendre en compte pendant qu'on était HURT (réarmement et rechargement)
        """

        #on fait le réarmage si le héros s'est fait interrompte par le hurt
        #alors qu'il faisait son réarmage juste après le Fire.
        if self.mustRearm:
            #encore du décalage de mayrde
            self.heroBody.rect.move_ip(DECAL_HURT_NORM.topleft)
            self.changeState(RAISE_ARMING_1, DECAL_NORM_RAISE1)
            return FUNCTION_CHANGED_STATE

        #si 0 cartouches, on lance automatiquement un rechargement.
        if self.nbrCartouche == 0:
            #encore du décalage de mayrde
            self.heroBody.rect.move_ip(DECAL_HURT_NORM.topleft)
            self.changeState(RAISE_REL_1, DECAL_NORM_RAISE1)
            return FUNCTION_CHANGED_STATE

        #Les deux blocs ci-dessus serait factorisable. Je le fait pas parce qu'ils
        #auront que 2 lignes chacun quand j'aurais géré le hotPoint. Et ça vaut pas le coup
        #de facto 2 lignes, surtout si l'une d'elle est un return.

        #si y'a pas d'événement spéciaux, y'a rien à faire
        #La machine à état va faire revenir tout seul à l'état normal.
        return FUNCTION_DID_NOT_CHANGED_STATE


    def determineHurtMovement(self, posEnemy):
        """
        détermine la direction, l'accélération, la période et le nombre de mouvement
        de Hurt à effectuer.
        Quand le héros se fait Hurt, il bouge automatiquement pendant quelques cycles,
        dans une des 4 directions, ou en diagonale, de façon à s'éloigner du magicien
        qui l'a touché.
        Le joueur peut continuer de diriger le héros pendant qu'il est Hurt. Les deux
        mouvements s'additionneront.

        entrées :
            posEnemy : rect(Xn Y) : position du magicien qui a fait mal au héro
                       cela permet de définir dans quelle direction de HURT le héro
                       doit bouger. (Il va aller dans le sens opposé au magicien)

        plats-dessert : rien. Mais définition d'un tas de variables :
        self.rectHurtMove, self.rectHurtAccel, ...
        """

        #init des variables indiquant les mouvements sur les axes X et Y.
        #3 valeurs possibles :
        # -1 : mvt gauche/haut
        #  0 : pas de mvt
        # +1 : mvt droite/bas
        hurtMoveDirX = 0
        hurtMoveDirY = 0

        #si il y a une distance assez grande sur l'axe X, entre le magicien et le héros
        #alors le héros fera un mouvement sur le X
        if abs(self.rectPos.centerx - posEnemy.centerx) > HURT_RECUL_DIST:
            #détermination du sens du mouvement sur X (faut s'éloigner du magicien)
            if self.rectPos.centerx > posEnemy.centerx:
                hurtMoveDirX = +1
            else:
                hurtMoveDirX = -1

        #si il y a une distance assez grande sur l'axe Y, entre le magicien et le héros
        #alors le héros fera un mouvement sur le Y
        if abs(self.rectPos.centery - posEnemy.centery) > HURT_RECUL_DIST:
            #détermination du sens du mouvement sur Y (faut s'éloigner du magicien)
            if self.rectPos.centery > posEnemy.centery:
                hurtMoveDirY = +1
            else:
                hurtMoveDirY = -1

        #on détermine si le mouvement à faire est tout droit, dans l'une des 4 directions,
        #ou en diagonale.
        if hurtMoveDirX != 0 and hurtMoveDirY != 0:
            #le mouvement est droit. On initialise le déplacement initial et
            #la décélération a des valeurs assez importantes, car on bouge que dans une
            #seule direction.
            hurtMoveInit = HURT_MOVE_INIT_DIAG
            hurtDecel = HURT_DECEL_DIAG
        elif hurtMoveDirX != 0 or hurtMoveDirY != 0:
            #le mouvement est diagonal. On intialise le déplacement initial et la décélération
            #à des valeurs plus faibles. Car ce déplacement se fera sur les deux directions.
            #Donc faut contrebalancer cela, voyez.
            hurtMoveInit = HURT_MOVE_INIT_STRAIGHT
            hurtDecel = HURT_DECEL_STRAIGHT
        else:
            #on n'a déterminé aucun mouvement. Dans ce cas, on met à l'arrache, par défaut,
            #un mouvement droit, vers la gauche, et basta
            hurtMoveDirX = -1
            hurtMoveDirY = 0
            hurtMoveInit = HURT_MOVE_INIT_STRAIGHT
            hurtDecel = HURT_DECEL_STRAIGHT

        #détermination du Rect contenant les coordonnées de déplacement initiale,
        #en fonction de la valeur de déplacement et des directions.
        self.rectHurtMove = pyRect(hurtMoveDirX * hurtMoveInit,
                                   hurtMoveDirY * hurtMoveInit)

        #détermination du Rect contenant les coordonnées d'accélération.
        #Je le définit à partir de hurtDecel, et du coup, faut foutre des "moins".
        #car la deceleration est l'opposé de l'acceleration
        self.rectHurtAccel = pyRect(-hurtMoveDirX * hurtDecel,
                                    -hurtMoveDirY * hurtDecel)

        #compteur pour la période de mouvement
        self.hurtMoveCounter = HURT_MOVE_PERIOD
        #compteur pour la période d'accélération (décélération en fait, blabla)
        self.hurtAccelCounter = HURT_DECEL_PERIOD
        #nombre de mouvement de Hurt restant à faire.
        self.hurtNbrMoveLeft = HURT_NBR_MOVE


    def makeHurtMovement(self):
        """
        effectuage du mouvement de Hurt. Fonction à exécuter à chaque cycle,
        pendant le Hurt.

        Alors c'est du code qui se retrouve un peu pareil ailleurs. (mouvement des SimpleSprite)
        Bon, je vois pas trop comment le factoriser. Ou alors avec une classe MovingPointAccel
        Mais c'est pousser le vice un peu loin. Pis en plus c'est chiant parce qu'il
        faudrait sans arrêt transférer les coordonnées du MovingPointAccel vers le hero.
        Donc pas de facto. Désolé
        """

        #Il n'y a rien à faire pendant le Hurt si on a fini tous les mouvements.
        if self.hurtNbrMoveLeft <= 0:
            return

        # --- application du mouvement sur la position ---
        #     (pas tout à fait, en fait c'est : ajout du mouvement au buffer de mouvement)

        self.hurtMoveCounter -= 1

        if self.hurtMoveCounter == 0:
            self.hurtMoveCounter = HURT_MOVE_PERIOD
            self.addMoveInBuffer(self.rectHurtMove)
            #diminution du compteur indiquant le nombre de mouvement de Hurt restant à faire.
            self.hurtNbrMoveLeft -= 1

        # --- application de l'accélération sur le mouvement. ---

        self.hurtAccelCounter -= 1

        if self.hurtAccelCounter == 0:
            self.hurtAccelCounter = HURT_DECEL_PERIOD
            self.rectHurtMove.move_ip(self.rectHurtAccel.topleft)


    def dyingBloodTurnHead(self):
        """
        Fonction a exécuter de temps en temps, pour faire l'anim du héros qui meurt.

        La fonction fait tourner la tête du héros, génère une petite giclure de sang,
        et détermine dans combien de cycle il faudra re-exécuter cette fonction.

        On ne cherche pas à déterminer à quel moment il faudrait arrêter d'exécuter cette fonction
        Ca va s'arrêter tout seul, car le jeu arrête la partie quelques temps après que le
        héros soit mouru.
        """

        #tournage de tete du héros. S'il regardait à gauche, il regardera à droite, et vice-versa.
        self.heroHead.turnHead()

        #réactualisation de la position de génération du sang.
        #car le héros a peut-être bougé à cause des hurtMovements
        self.posBlood = self.rectPos.move(DECAL_HURT_BLOOD.topleft)

        #génération d'une petite giclure de sang.
        funcGenBlood = self.spriteSimpleGenerator.generateSomeBlood
        funcGenBlood(self.posBlood, NBR_BLOOD_DYING)

        #le son du héros qui a mal : argh !!
        theSoundYargler.playSound(SND_HERO_HURT)

        #recalcul, avec un peu de random, du temps avant qu'on re-exécute cette fonction.
        self.counterBlood = randRange(DELAY_BLOOD_DYING_MIN,
                                      DELAY_BLOOD_DYING_MAX)


    def updateDying(self):
        """
        fonction a exécuter à chaque cycle, quand le héros est en train de crever,
        pour faire son animation de crevage.
        """

        #réalisation du mouvement de Hurt.
        #(Même quand le héros meurt, on fait les mouvements de Hurt)
        self.makeHurtMovement()

        #exécution périodique-de-temps-en-temps de l'anim de crevage (sang + tournage de tête)
        self.counterBlood -= 1

        if self.counterBlood <= 0:
            self.dyingBloodTurnHead()


    def endOfDying(self):
        """
        fonction qui s'exécute quand le héros est vraiment mort (après son anim de crevage)
        """
        #y'a rien de spécial à faire car c'est géré par le jeu. On balance juste un son cool.
        theSoundYargler.playSound(SND_HERO_DIE)
        #y'a pas eu de changement d'état.
        return FUNCTION_DID_NOT_CHANGED_STATE
