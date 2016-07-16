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

date de la derni�re relecture-commentage : 14/10/2010

putain de grosse classe qui g�re le H�ros.
Les sprites de la t�te et du corps. Les actions, les �tats, ...

Un peu de vocabulaire :

clamping : contrainte impos�e � un objet rectangulaire, pour le forcer
� rester dans un rectangle englobant.
L'objet "h�ros" est clampingu� dans le rectangle de l'�cran du jeu.

rearm : action de faire schla-schlak le fusil � pompe, pour virer
la douille apr�s avoir tir� une cartouche.

recharge/reload : remettre des cartouches dans le fusil.
(quand il est compl�tement vide, ou quand il est pas
compl�tement plein)

stimuli : valeur bool�enne correspondant � une action
que peut faire le h�ros (ex : tirer, recharger).
si la valeur est True : le h�ros a re�u un signal
indiquant qu'il doit faire l'action correspondante.
(l'origine du signal est ind�termin�e mais osef).
Selon son �tat, le h�ros va faire l'action tout de suite, ou pas.
Lorsqu'il est re�u et accept�, un stimuli est toujours gard� en m�moire
jusqu'� ce qu'il soit trait�.

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
#(Avant que le h�ros ne doive obligatoirement recharger)
NBR_MAX_CARTOUCHE = 8

#largeur et hauteur globale du h�ros. Ca servira pour le clamping du h�ros dans l'aire de jeu
#Ces hauteur et largeur sont ind�pendante des sprites qui composent le h�ros
HERO_WIDTH  = 23
HERO_HEIGHT = 32

# --- d�calages (X, Y), lorsque le h�ros est dans l'�tat "NORMAL" ---

#d�calage entre la position du h�ros et le sprite du corps du h�ros
DECAL_POS_BODY = pyRect(0, 8)
#d�calage entre la position du h�ros et le sprite de la t�te du h�ros
DECAL_POS_HEAD = pyRect(4, 0)
#d�calage entre la position du h�ros et le point d'o�
#partent les bullets du flingue
DECAL_POS_FIRE = pyRect(23, 19)
#d�calage entre la position du h�ros et le point d'o� partent les
#Little Shell (les douilles qui tombent).
DECAL_POS_LITTLESHELL = pyRect(5, 6)

# --- d�calage � appliquer au sprite du corps du h�ros, lorsqu'on change l'image
#de ce sprite. (car le coin sup�rieur gauche de chaque image ne correspond pas
#tout � fait au m�me endroit du corps du h�ros). ---

#les iimages mentionn�es ici sont les images de la classe HeroBody
#d�calage quand on passe de l'image "NORMAL" � l'image "HURT"
DECAL_NORM_HURT     = pyRect(+4,  0)
#d�calage quand on passe de l'image "NORMAL" � l'image "RAISE_A"
DECAL_NORM_RAISE1   = pyRect(+3, -1)
#d�calage quand on passe de l'image "RAISE_A" � l'image "RAISE_B"
DECAL_RAISE1_RAISE2 = pyRect(+1, -5)
#d�calage quand on passe de l'image "RAISE_B" � "ARMINGE"
DECAL_RAISE2_ARM    = pyRect( 0, +1)

#memes d�calage, mais les images d'arriv�e et de d�part sont invers�s
#on les d�termine en prenant les coordonn�es oppos�es des d�calages correspondants
DECAL_HURT_NORM     = oppRect(DECAL_NORM_HURT)
DECAL_RAISE1_NORM   = oppRect(DECAL_NORM_RAISE1)
DECAL_RAISE2_RAISE1 = oppRect(DECAL_RAISE1_RAISE2)
DECAL_ARM_RAISE2    = oppRect(DECAL_RAISE2_ARM)
#TRODO : je l'ai d�j� dit mais c'est de la merde ces d�calages.
#Ils ont rien � foutre l� en fait. C'est le HeroBody qui devrait les g�rer.

#liste de rect.
#indique la distance de recul � appliquer sur le h�ros.
#elem 1 : distance X de recul imm�diatement apr�s le tir.
#elem 2 : distance X de recul un cycle de jeu apr�s le tir.
#Si on met plus d'�l�ment, ce sera pas g�r�. (osef)
#l� j'ai pas mis de recul en Y, mais je pourrais.
FIRE_RECUL = (pyRect(-4), pyRect(-2))

#identifiant des stimulis que peut recevoir le h�ros dans sa gueule.
#FIRE : le h�ros doit tirer
#RELOAD : le h�ros doit recharger
#il y a �galement le stimuli "Hurt", quand le h�ros se fait toucher par un magicien.
#mais celui l� doit �tre imm�diatement pris en compte quand il est re�u. donc pas la peine
#de le stocker en m�moire.
(FIRE, RELOAD) = range(2)

#identifiant des �tats du h�ros
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

#liste des �tats durant lesquels on ne prend pas en compte le stimuli de FIRE
#car le h�ros est d�j� en train de tirer, ou il vient de le faire,
#ou il se fait cogner dessus (HURT)
LIST_STATE_NO_STIMULI_FIRE = (RAISE_ARMING_1, RAISE_ARMING_2,
                              FIRING, ARMING, ARMED, HURT)

#identifiant plus cool pour plus de clart�.
#c'est utilis� dans les petites fonctions li�s � la machine � �tat.
#il faut pouvoir indiquer � la fonction principale de la machine si
#l'une de ces fonctions a chang� l'�tat, ou pas.
FUNCTION_CHANGED_STATE = True
FUNCTION_DID_NOT_CHANGED_STATE = False

# --- valeurs pour g�rer le mouvement de recul du h�ros quand il est HURT ---

#TRODO : ouais, un movingPoint avec une position, un mouvement initial, et une acc�l�ration,
#Ce serait pas mal. (Genre un d�riv� de movingPoint.)
#Pour la version 2. De toutes fa�on le plus urgent ce sera pas �a, mais les hotPoint de merde
#fun fact : j'ai pass� certainement plus de temps � expliquer dans les commentaires que
#mon manque de gestion des hotPointest merdique, que je n'en aurais pass� � ajouter cette gestion.

#distance (X ou Y) minimale n�cessaire entre le h�ros et le magicien qui l'a touch�, pour que
#le h�ros fasse un mouvement de recul sur l'axe (X ou Y) concern�.
HURT_RECUL_DIST = 8

#valeurs initiale du mouvement. Dans le cas o� le mouvement est droit, ou en diagonale
HURT_MOVE_INIT_STRAIGHT = 5
HURT_MOVE_INIT_DIAG = 3

#d�c�l�ration du mouvement. Dans le cas o� le mouvement est droit, ou en diagonale
HURT_DECEL_STRAIGHT = 2
HURT_DECEL_DIAG = 1

#p�riode de mouvement (nbre de cycle)
HURT_MOVE_PERIOD = 2

#p�riode de d�c�l�ration (nbre de cycle)
HURT_DECEL_PERIOD = 4

#nombre de mouvement de recul � effectuer
HURT_NBR_MOVE = 5

#d�calage entre la position du h�ros, et le point de d�part des giclures de sang
#(ce d�calage est pr�vu avec le corps du h�ros dans l'�tat HURT.
DECAL_HURT_BLOOD = pyRect(8, 0)

#nombre de giclures de sang � balancer quand le h�ros se fait HURT.
#(Quand HURT, il n'y a qu'une giclure, mais elle est grosse)
NBR_BLOOD_HURT  = 30

#nombre de giclures de sang � balancer quand le h�ros est DYING.
#(Quand DYING, il y a plusieurs petites giclures de sang successives, et en m�me temps,
#le h�ros tourne la t�te)
NBR_BLOOD_DYING =  10

#d�lai (nombre de cycle) entre deux petites giclures de sang de l'�tat DYING.
#� chaque fois, le d�lai est calcul� en random entre les valeurs min et max.
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

        entr�e :
            dicHeroBodyImg : dictionnaire de correspondance
                             identifiant d'image -> image du corps
            dicHeroHeadImg : dictionnaire de correspondance
                             identifiant d'image -> image de la t�te
            coordStart     : tuple (X, Y). Coordonn�es initiale du h�ros
            collHandlerBulletMagi : classe g�rant les collisions
                                    entre les bullets tir�es par le h�ros et les magiciens
            spriteSimpleGenerator : classe �ponyme. permet de g�n�rer des SimpleSprite,
                                    par exemple, la flamme du flingue.
            ammoViewer            : classe �pongiforme. affichage des cartouches dans le flingue.
            lifePointViewer       : classe �pongiforme. affichage des points de vie.
            scoreManager          : classe poney-ime. gestion du score, des hiscore, ...
            dogDom                : boolean. Indique si le h�ros perd des vies ou pas.
        """

        self.collHandlerBulletMagi = collHandlerBulletMagi
        self.spriteSimpleGenerator = spriteSimpleGenerator
        self.ammoViewer = ammoViewer
        self.lifePointViewer = lifePointViewer
        self.scoreManager = scoreManager
        self.dogDom = dogDom

        #initialisation du dictionnaire de correspondance stimuli -> fonction � ex�cuter
        self.dicFuncFromStimuli = {
            STIMULI_HERO_MOVE   : self.addMoveInBuffer,
            STIMULI_HERO_FIRE   : self.takeStimuliFire,
            STIMULI_HERO_RELOAD : self.takeStimuliReload,
        }

        #cr�ation d'un Rect donnant la position X, Y du h�ros, et sa taille globale
        self.rectPos = pyRect(coordStart.x, coordStart.y,
                              HERO_WIDTH, HERO_HEIGHT)

        #self.areaAuthorized est donc le rectangle dans lequel la position
        #du h�ros a le droit d'�tre.
        self.areaAuthorized = pygame.Rect(GAME_RECT)

        #clamping un peu crade, que je fais manuellement dans makeBufferMove.
        #la zone de mouvement du h�ros est diminu� en bas � droite de la taille du h�ros.
        #Comme �a on g�re le clamping uniquement avec une position X,Y
        #et non pas un rectangle avec une pos X, Y et une taille.
        #Si la taille du h�ros change pendant le jeu, �a p�te. Mais comme �a n'arrive pas, osef.
        self.areaAuthorized.width -= HERO_WIDTH
        self.areaAuthorized.height -= HERO_HEIGHT

        # ------ Init du corps et de la t�te du h�ros ---------

        #on applique une seule fois au d�but le d�calage de coordonn�es
        #entre le h�ros et le corps du h�ros
        rectHeroBody = self.rectPos.move(DECAL_POS_BODY.topleft)
        self.heroBody = herobody.HeroBody(dicHeroBodyImg, rectHeroBody)
        #pareil pour la t�te : on applique une seule fois au d�but le d�calage.
        rectHeroHead = self.rectPos.move(DECAL_POS_HEAD.topleft)
        self.heroHead = herohead.HeroHead(dicHeroHeadImg, rectHeroHead)

        # ------ Init de plein de variables importantes ---------

        #variables int indiquant les mouvements du h�ros � faire
        #au prochain cycle
        self.rectMoveBuffer = pyRect()

        #liste contenant l'�tat des stimulis (FIRE, RECHARGE)
        self.stimuli = [False, False]

        #variable compteur. Indique le nombre de cycle de jeux avant
        #le prochain changement automatique d'�tat, (si il y a changement auto � faire)
        self.stateTimer = NONE_COUNT

        #variable indiquant l'identifiant de l'�tat en cours.
        self.currentState = NORMAL

        #nombre de cartouche en cours dans le flingue.
        self.nbrCartouche = NBR_MAX_CARTOUCHE

        #les points de vie
        self.lifePoint = HERO_LIFE_POINT_INITIAL

        #boolean qui indique si le h�ros doit r�armer ou pas.
        self.mustRearm = False

        #crac boum !! d�finition de la mega machine � �tat.
        self.definestateMachine()


    def addMoveInBuffer(self, rectMove):
        """
        ajoute un mouvement � faire pour le h�ros.
        le mouvement n'est pas effectif tout de suite,
        il faut ex�cuter MakeBufferMove

        entr�e : rect(X, Y) : coordonn�es du mouvement (int)
        """
        self.rectMoveBuffer.move_ip(rectMove.topleft)


    def makeBufferMove(self):
        """
        bouge le h�ros selon ce qu'on lui a foutu dans son buffer de mouvement.
        clampage manuel dans le rectangle areaAuthorized

        y'a des tests tout pouillave, je sais qu'il existe le rect.clamp,
        mais c'est utile que si t'as des sprite unique qui se baladent.
        L� j'ai un h�ros avec deux sprites. Donc pas mieux.
        """

        # --- contr�le du clamping ---
        #le but de ces contr�les sera de r�ajuster les valeurs de mouvement
        #self.rectMoveBuffer, de fa�on � ce que le mouvement
        #ne fasse plus sortir le h�ros de l'�cran.

        #clamping X, sur le mur gauche. A faire si je dois bouger � gauche, et que ma
        #position d'arriv�e apr�s ce mouvement d�passe la limite du mur gauche de areaAuthorized:
        if self.rectMoveBuffer.x < 0 and \
           self.rectPos.x + self.rectMoveBuffer.x < self.areaAuthorized.left:

            #il faut r�ajuster le mouvement pour arriver � la limite du mur.
            #Si le h�ros a d�j� d�pass� le mur gauche, �a va cr�er un
            #mouvement inverse qui le fait revenir � la limite.
            #�a arrive jamais. Mais si �a arrivait, �a serait normal.
            self.rectMoveBuffer.x = self.areaAuthorized.left - self.rectPos.x

        #les autrse clampings, c'est pareil. Je r�p�te pas les commentaires.
        #je raconte d�j� assez de conneries comme �a.

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

        #antislash de merde... �ay moche

        # --- application du mouvement, maintenant qu'il est r�ajust� par le clamping ---
        #il faut appliquer le mouvement sur tous les trucs � bouger.
        #position du h�ros
        self.rectPos.move_ip(self.rectMoveBuffer.topleft)
        #position du corps du h�ros
        self.heroBody.rect.move_ip(self.rectMoveBuffer.topleft)
        #position de la t�te du h�ros
        self.heroHead.rect.move_ip(self.rectMoveBuffer.topleft)

        #remise � zero des buffers de mouvement.
        self.rectMoveBuffer.topleft = (0, 0)


    def definestateMachine(self):
        """
        putain de dictionnaire g�rant les diff�rents �tats du h�ros.

        cl� : identifiant de l'�tat
        valeur : putain de gros tuple, contenant les
                 infos correspondantes � cet �tat
          0) identifiant de l'image du corps.
          1) fonction � ex�cuter si on a re�u le stimuli FIRE.
             Ou None. Dans ce cas on ne fait rien et on garde le stimuli en reserve
          2) fonction � ex�cuter si on a re�u le stimuli RELOAD.
             Ou None. Dans ce cas on ne fait rien et on garde le stimuli en reserve
          3) temps d'attente avant le changement automatique vers l'�tat suivant.
             si c'est NONE_COUNT : pas de changement automatique
          4) identifiant de l'�tat suivant, pour le changement auto.
             si c'est None, pas de changement automatique.
          5) tuple (X,Y) de d�calage du sprite HeroBody lors du changement auto.
             Ou None. Dans ce cas, pas de d�calage.
          6) fonction � ex�cuter juste avant le changement auto.
             Ou None. Dans ce cas, pas de fonction � ex�cuter.
          7) fonction � ex�cuter � chaque cycle, tant qu'on est dans cet �tat
             Ou None. Dans ce cas, pas de fonction � ex�cuter � chaque cycle.

        les �tats sont configur�s pour respecter les r�gles suivantes :
         - on r�arme imm�diatement et obligatoirement juste apr�s avoir tir�.
           Mais le rearm peut �tre report� suite � un HURT
           (le h�ros s'est pris un coup dans la gueule)
         - il faut lever le flingue pour r�armer, et aussi pour recharger.
           on peut faire les deux � la suite, (r�armer puis recharger) quand le flingue est lev�
         - quand on commence de recharger, on le fait jusqu'� ce que le flingue soit rempli,
           sauf si on re�oit le stimuli FIRE pendant qu'on recharge. Dans ce cas,
           on abaisse le flingue et on tire.
         - on commence obligatoirement le rechargement quand il n'y a plus aucune cartouche
         - y'a pas de r�armement apr�s avoir recharg�. On voit �a dans certains jeux,
           et je trouve �a bizarre. (c'est peut �tre comme �a en vrai. mais m'en fout)
         - on peut pas tirer si y'a plus de cartouche (thx cptn obvious), m�me avec
           le stimuli FIRE.
        """

        self.stateMachine = {
            NORMAL           : (
                #etat normal. Le h�ros ne tire pas et ne recharge pas.
                herobody.IMG_NORMAL,
                self.fire,            self.startReload,    NONE_COUNT,
                None,                 None,                None,
                None),

            FIRING           : (
                #le h�ros est en train de tirer.
                herobody.IMG_NORMAL,
                None,                 None,                3,
                RAISE_ARMING_1,       DECAL_NORM_RAISE1,   self.fireRecul,
                None),

            RAISE_ARMING_1   : (
                #le h�ros et en train de lever le flingue (img 1) afin de r�armer.
                herobody.IMG_RAISE_A,
                None,                 None,                3,
                RAISE_ARMING_2,       DECAL_RAISE1_RAISE2, None,
                None),

            RAISE_ARMING_2   : (
                #le h�ros et en train de lever le flingue (img 2) afin de r�armer.
                herobody.IMG_RAISE_B,
                None,                 None,                3,
                ARMING,               DECAL_RAISE2_ARM,    self.arming,
                None),

            ARMING           : (
                #le h�ros r�arme. schla-schlak !!
                herobody.IMG_ARMINGE,
                None,                 None,                7,
                ARMED,                DECAL_ARM_RAISE2,    self.armingIsDone,
                None),

            LOWER_1          : (
                #le h�ros est en train de rabaisser le flingue (img 1)
                herobody.IMG_RAISE_A,
                None,                 None,                2,
                NORMAL,               DECAL_RAISE1_NORM,   None,
                None),

            LOWER_2          : (
                #le h�ros est en train de rabaisser le flingue (img 2)
                herobody.IMG_RAISE_B,
                None,                 None,                2,
                LOWER_1,              DECAL_RAISE2_RAISE1, None,
                None),

            ARMED            : (
            #le h�ros a le flingue lev�. Il vient de r�armer.
            #A la fin de cet �tat, on rabaisse le flingue, ou on commence un
            #rechargement si on a le stimuli RELOAD
                herobody.IMG_RAISE_B,
                None,                 None,                3,
                LOWER_1,              DECAL_RAISE2_RAISE1, self.reloadPerhaps,
                None),

            RAISE_REL_1      : (
            #le h�ros et en train de lever le flingue (img 1) afin de recharger.
                herobody.IMG_RAISE_A,
                self.fireIfGotShell, None,                 3,
                RAISE_REL_2,         DECAL_RAISE1_RAISE2,  None,
                None),

            RAISE_REL_2      : (
            #le h�ros et en train de lever le flingue (img 2) afin de recharger.
                herobody.IMG_RAISE_B,
                self.fireIfGotShell, None,                 3,
                RELOADING_1,         None,                 None,
                None),

            RELOADING_1      : (
                #le h�ros recharge (img 1)
                herobody.IMG_RELOAD_A,
                self.fireIfGotShell, None,                 8,
                RELOADING_2,         None,                 None,
                None),

            RELOADING_2      : (
                #le h�ros recharge (img 2)
                #l'ajout effectif de la cartouche dans le flingue se fait une fois
                #que cet �tat est termin�.
                herobody.IMG_RELOAD_B,
                self.fireIfGotShell, None,                8,
                LOWER_2,             None,                self.reloadOneShell,
                None),

            HURT             : (
                #le h�ros s'est pris un coup dans la gueule.
                herobody.IMG_HURT,
                None,                None,                 32,
                NORMAL,              DECAL_HURT_NORM,      self.endOfHurt,
                self.makeHurtMovement),

            DYING            : (
                #le h�ros est en train de crever.
                herobody.IMG_HURT,
                None,                None,                 120,
                DEAD,                None,                 self.endOfDying,
                self.updateDying),

            DEAD             : (
                #le h�ros a crev�.
                herobody.IMG_HURT,
                None,                None,                NONE_COUNT,
                None,                None,                None,
                None),
        }


    def advanceStateOneStep(self):
        """
        fonction a ex�cuter � chaque cycle de jeu.
        elle g�re toute la machine � �tat du h�ros.
        """

        #r�cup�ration de toutes les infos de l'�tat courant, � partir du dictionnaire
        #de la machine � �tat.
        (stateImg, functionStimuliFire, functionStimuliReload,
         stateTimerInitial, nextState, rectDecalageImgNextState,
         functionEndState, functionEachCycle,
        ) = self.stateMachine[self.currentState]

        #ex�cution de la fonction correspondante au stimuli FIRE, si il
        #y en a une dans l'�tat courant, et si on a le stimuli
        if functionStimuliFire is not None and self.stimuli[FIRE]:
            #on ex�cute la fonction, et on regarde si elle s'est occup�e elle-m�me de faire
            #un changement d'�tat, alors, on n'a plus rien � faire pour
            #ce cycle de jeu, et on quitte tout de suite.
            #sinon, il faut continuer de g�rer l'�tat courant.
            if functionStimuliFire() == FUNCTION_CHANGED_STATE:
                return

        #pareil mais avec le RELOAD
        if functionStimuliReload is not None and self.stimuli[RELOAD]:
            #pareil
            if functionStimuliReload() == FUNCTION_CHANGED_STATE:
                return

        #gestion �ventuelle du changement automatique d'�tat.
        if nextState is not None:

            self.stateTimer -= 1

            if self.stateTimer == 0:

                #On doit faire un changement automatique d'�tat.

                if functionEndState is not None:

                    #il y a une fonction � ex�cuter avant le changement d'�tat auto, on l'ex�cute.
                    if functionEndState() == FUNCTION_DID_NOT_CHANGED_STATE:

                        #si la fonction ne s'est pas occup�e elle-m�me de faire un
                        #changement d'�tat, alors il faut faire le changement auto, comme pr�vu.
                        #sinon, on n'a plus rien � faire.
                        self.changeState(nextState, rectDecalageImgNextState)

                else:

                    #quand y'a pas de fonction � lancer � la fin d'un �tat, on se contente
                    #d'effectuer le changement automatique vers l'�tat suivant
                    self.changeState(nextState, rectDecalageImgNextState)

        #ex�cution de la fonction � ex�cuter � chaque cycle. Si il y en a une.
        if functionEachCycle is not None:
            functionEachCycle()


    def changeState(self, nextState, rectDecalageImg=None):
        """
        fonction � ex�cuter pour passer d'un �tat � un autre. (lors d'un changement
        automatique d'�tat, ou � une autre occasion quelconque. Genre un go�ter-cocktail)

        entr�e :
          nextState : identifiant de l'�tat suivant

          rectDecalageImg : rect(X,Y) de d�calage de merde � appliquer au corps du h�ros.
                            pour pas que �a fasse des petits mouvements bizarres.
                            (g�r� � l'arrache)
                            Si None, pas de d�calage � appliquer
        """

        #r�cup�ration des infos de l'�tat suivant (pas l'�tat courant, osef)
        #On n'a pas besoin de choper toute les infos. que les trucs du d�but.
        #d'o� le [:4]
        (imgIdState, functionStimuliFire, functionStimuliReload,
         stateTimerInitial,
        ) = self.stateMachine[nextState][:4]

        #on r�initialise le compteur de changement auto d'�tat avec celui de l'�tat suivant.
        self.stateTimer = stateTimerInitial
        #on red�finit la valeur de l'�tat courant.
        self.currentState = nextState
        #on change l'image du h�ros, en appliquant �ventuellement le d�calage.
        # BIG BIG TRODO : la gestion des d�calages doit pas �tre faite comme �a
        # C'est vraiment pourri. Il faut que ce soit HeroBody qui le g�re.
        # Avec un dictionnaire { ( img_avant, img_apr�s) : valeur_decalage }
        self.heroBody.changeImg(imgIdState, rectDecalageImg)

    #je m'en souviens de ces trucs. Ca m'a fait bizarrrrrrre......

    def takeStimuliFire(self):
        """
        active le stimuli pour tirer un coup de fusil. pan !!!
        Le h�ros tire tout de suite si possible
        Le stimuli n'est pas pris en compte si le h�ros est d�j� en train de tirer ou de r�armer.
        Ca permet d'�viter que 2 coups soient tir�s si le joueur appuie un peu trop longtemps.
        Car de mani�re g�n�rale, les stimulis sont enregistr�s pour plus tard si ils ne sont
        pas traitable tout de suite.
        """
        if self.currentState not in LIST_STATE_NO_STIMULI_FIRE:
            self.stimuli[FIRE] = True


    def takeStimuliReload(self):
        """
        active le stimuli pour recharger les cartouches. shlink shink shlink
        Le h�ros rechargera tout de suite si possible, sinon on remettra �a � plus tard.
        On ne prend pas en compte le stimuli si le fusil est d�j� charg� au max
        On le prend pas non plus en compte si le h�ros est HURT
        """
        if self.nbrCartouche < NBR_MAX_CARTOUCHE and self.currentState != HURT:
            self.stimuli[RELOAD] = True


    def takeStimuliGeneric(self, idStimuli, param):
        """
        permet de recevoir un stimuli venant du joueur. N'importe quel stimuli

        entr�e :
             idStimuli : identifiant du stimuli qu'on re�oit (move, fire, reload)
             param : tuple. liste des param du stimuli. (�a peut �tre un tuple vide)
        """

        #on r�cup�re la fonction correspondante au stimuli
        func = self.dicFuncFromStimuli[idStimuli]
        #on ex�cute cette fonction avec les param fournis.
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
            #on ne peut pas tirer. Donc on ne change pas d'�tat.
            #La gestion de la stateMachine s'occupe du reste.
            return FUNCTION_DID_NOT_CHANGED_STATE

        #il reste au moins une cartouche.
        #on change l'�tat du h�ros pour qu'il tire un coup (ha ha ha)
        self.changeState(FIRING)
        #on fait bouger le h�ros avec la premi�re valeur de recul.
        self.addMoveInBuffer(FIRE_RECUL[0])
        #une cartouche en moins.
        self.nbrCartouche -= 1
        #indication � l'afficheur des cartouches que y'a eu un coup de feu.
        self.ammoViewer.takeStimuliFire()
        #le son du coup de feu : pan!!
        theSoundYargler.playSound(SND_GUN_FIRE)
        #on garde en souvenir qu'il faut r�armer
        #(si jamais le h�ros ne peut pas le faire imm�diatement apr�s,
        #genre si il se fait hurt ou une connerie comme �a)
        self.mustRearm = True

        #on d�termine d'o� partent les bullets
        posFire = self.rectPos.move(DECAL_POS_FIRE.topleft)

        #gestion de la collision des bullets avec les magiciens
        #le CollisionHandler calcule les trajectoires des balles, avertit les
        #magiciens touch�s, qui indiquent si ils sont morts ou explos�s.
        #le CollisionHandler renvoie un tuple contenant le nombre de magiciens explos�s
        #et le nombre tu�s. Tout cela se passe de mani�re instantan�e, hop paf crac.
        scoreTuple = self.collHandlerBulletMagi.heroFiresBullets(posFire)

        if scoreTuple != (0, 0):

            #y'a eu des morts chez les magiciens
            (addMagiBurst, addMagiKilledNotBurst) = scoreTuple
            #on enregistre ces morts dans le scoreManager
            self.scoreManager.updateScore(addMagiBurst, addMagiKilledNotBurst)

            #si au moins un magicien a �t� explos�, la t�te du h�ros sourit
            #(le sourire s'arr�tera automatiquement au bout d'un certain temps
            if addMagiBurst > 0:
                self.heroHead.startSmiling()

        #affichage du sprite de la flamme. On la place � la position du tir,
        #mais on tient compte de la premi�re valeur de recul. Ca fait plus mieux � l'oeil.
        #C'est un peu crade car j'utilise cette valeur de recul � deux endroits diff�rents :
        #une fois pour bouger le h�ros, et une autre fois pour la flamme. Oh �a se tient en fait.
        posFlame = posFire.move(FIRE_RECUL[0].topleft)
        self.spriteSimpleGenerator.generateFlame(posFlame)

        #annulation du stimuli, puisqu'il a �t� pris en compte.
        self.stimuli[FIRE] = False
        #On a chang� d'�tat. La stateMachine n'aura rien de plus � faire
        return FUNCTION_CHANGED_STATE


    def fireRecul(self):
        """
        Petite fonction un peu � la con, pour appliquer le reste du recul.
        Elle est ex�cut� � la fin du FIRE.

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        #on fait reculer de la deuxi�me valeur de recul de la liste
        # (moins importante que la premi�re valeur)
        self.addMoveInBuffer(FIRE_RECUL[1])
        #y'a pas eu de changement d'�tat.
        return FUNCTION_DID_NOT_CHANGED_STATE


    def arming(self):
        """
        Fonction qui s'ex�cute quand le h�ros est en train de r�armer. (entre l'image
        de levage du flingue et l'image du r�armement).

        sortie : valeur FUNCTION_CHANGED_STATE ou FUNCTION_DID_NOT_CHANGED_STATE
        """
        #son : "shla-shlak !!"
        theSoundYargler.playSound(SND_GUN_REARM)
        #y'a pas eu de changement d'�tat.
        return FUNCTION_DID_NOT_CHANGED_STATE


    def armingIsDone(self):
        """
        Fonction qui s'ex�cute une fois que le h�ros a fait un rearm.
        (soit imm�diatement apr�s avoir tir�,
         soit que entre temps il s'est fait Hurt une ou plusieurs fois)

        sortie : valeur FUNCTION_CHANGED_STATE ou FUNCTION_DID_NOT_CHANGED_STATE
        """

        self.mustRearm = False
        #on pr�vient l'afficheur des cartouches que y'a eu un r�armement.
        #(Il va d�caler les cartouches)
        self.ammoViewer.takeStimuliRearm()

        #g�n�ration d'un SimpleSprite : la petite cartouche qui part en tournoyant
        #derri�re le h�ros.
        posLittleShell = self.rectPos.move(DECAL_POS_LITTLESHELL.topleft)
        self.spriteSimpleGenerator.generateLittleShell(posLittleShell)

        #y'a pas eu de changement d'�tat.
        return FUNCTION_DID_NOT_CHANGED_STATE


    def startReload(self):
        """
        Commence le rechargement du flingue.
        C'est la stateMachine qui g�re toute seule le fait que le rechargement soit
        automatique, jusqu'� ce que le flingue soit plein.

         sortie : valeur FUNCTION_CHANGED_STATE ou
                         FUNCTION_DID_NOT_CHANGED_STATE
        """

        #on commence le rechargement que si le nombre de cartouche est pas au max.
        #(pr�caution un peu inutile car on prend pas le stimuli si on est au max.)
        #mais je pr�f�re comme �a. "blindage double-�paisseur" comme dirait l'autre grand glandu
        if self.nbrCartouche < NBR_MAX_CARTOUCHE:
            #le h�ros commence � lever son flingue pour recharger.
            #(notez le passage en param�tre du d�calage d'image pourri. J'en ai d�j� parl�.)
            self.changeState(RAISE_REL_1, DECAL_NORM_RAISE1)
            #on a chang� d'�tat
            return FUNCTION_CHANGED_STATE
        else:
            #on n'a rien fait
            return FUNCTION_DID_NOT_CHANGED_STATE


    def reloadOneShell(self):
        """
        fonction a ex�cuter quand le h�ros a pu recharger une cartouche dans le flingue.
        Elle est ex�cut� � la fin de l'�tat RELOADING_2

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        #une cartouche de plus !!!
        self.nbrCartouche += 1
        #on pr�vient l'afficheur de cartouche qu'il doit en rajouter une.
        self.ammoViewer.takeStimuliReload()
        #son de reloadage de cartouche : cli-clik.
        theSoundYargler.playSound(SND_GUN_RELOAD)

        if self.nbrCartouche < NBR_MAX_CARTOUCHE:
            #si il manque encore des cartouches, on repart au d�but de l'�tat du rechargeage
            #comme �a, �a fera encore une cartouche de plus dans quelques temps.
            self.changeState(RELOADING_1)
            #on a chang� d'�tat
            return FUNCTION_CHANGED_STATE
        else:
            #y'a plus de cartouche � mettre. On supprime le stimuli de rechargement.
            self.stimuli[RELOAD] = False
            #on n'a pas chang� d'�tat. Ca va se remettre tout seul � l'�tat NORMAL
            return FUNCTION_DID_NOT_CHANGED_STATE


    def reloadPerhaps(self):
        """
        fonction appel� apr�s avoir tir� un coup et r�arm� (le flingue est toujours lev�).
        Elle permet de commencer un rechargement,
         - soit � l'arrache, si il n'y a plus du tout de cartouche dans le flingue
         - soit si le joueur a demand� un rechargement pendant le tir.

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        if self.nbrCartouche == 0 or self.stimuli[RELOAD]:
            #on passe directement � l'�tat de rechargement. On ne l�ve pas le flingue
            #pour recharger, car cela a d�j� �t� fait.
            self.changeState(RELOADING_1)
            #un changement d'�tat a eu lieu.
            return FUNCTION_CHANGED_STATE
        else:
            #il s'est rien pass�.
            return FUNCTION_DID_NOT_CHANGED_STATE


    def fireIfGotShell(self):
        """
        rabaisse le flingue pour tirer, alors que le h�ros est en train de
        recharger. Ne fait rien si y'a plus du tout de cartouche

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        #on peut pas tirer, m�me si le joueur l'a demand�. On fait rien
        #le rechargement va se continuer tout seul.
        if self.nbrCartouche == 0:
            #il s'est rien pass�.
            return FUNCTION_DID_NOT_CHANGED_STATE

        #on oublie qu'on avait envie de recharger. (tirer est prioritaire)
        self.stimuli[RELOAD] = False

        #Pour prendre en compte le Fire, on se contente d'amorcer le baissage du flingue.
        #le stimuli de FIRE est toujours � True. Donc le tir se fera tout seul, quand
        #on sera revenu � l'�tat NORMAL.

        if self.currentState == RAISE_REL_1:
            #le h�ros avait � peine commenc� de lever son flingue. On peut le rabaisser
            #directement tout de suite.
            self.changeState(NORMAL, DECAL_RAISE1_NORM)
        else:
            #le h�ros a le flingue compl�tement lev� (et il est peut �tre m�me en train de
            #recharger. Donc il faut passer par l'�tape interm�diaire pour abaisser le flingue.
            self.changeState(LOWER_1, DECAL_RAISE2_RAISE1)

        #on a chang� d'�tat.
        return FUNCTION_CHANGED_STATE


    def takeStimuliHurt(self, posEnemy):
        """
        fonction qui s'ex�cute quand le h�ros s'est fait toucher par un magicien,
        et que donc il se prend un coup dans la gueule (il se fait HURT la gueule)

        entr�es :
            posEnemy : rect(Xn Y) : position du magicien qui a fait mal au h�ro
                       cela permet de d�finir dans quelle direction de HURT le h�ro
                       doit bouger. (Il va aller dans le sens oppos� au magicien)

        sortie : valeur FUNCTION_CHANGED_STATE ou
                        FUNCTION_DID_NOT_CHANGED_STATE
        """

        if self.currentState in (HURT, DYING, DEAD):
            #on peut pas se faire HURT pendant qu'on est HURT, ni quand on cr�ve.
            #Donc on quitte toute de suite, en signalant qu'il ne s'est rien pass�.
            return FUNCTION_DID_NOT_CHANGED_STATE

        #supression d'un point de vie, sauf si mode sp�cial. H�h�.
        if not self.dogDom:
            #et paf ! on vire un point de vie au h�ro.
            self.lifePoint -= 1
            #hurt du lifepointviewer. permet de supprimer l'affichage d'un point de vie.
            self.lifePointViewer.takeStimuliHurt()

        #arr�tage de sourire si le h�ros �tait en train de sourire
        self.heroHead.stopSmiling()

        #on vire le stimuli RELOAD. Si le joueur �tait en train de recharger, il devra r�appuyer
        #sur la touche de rechargeage. Bien fait.
        self.stimuli[RELOAD] = False
        #Oh et puis celui de Fire aussi, tant qu'� faire. Faut pas me faire chier.
        self.stimuli[FIRE] = False

        #calcul du mouvement de recul li� au Hurt.
        self.determineHurtMovement(posEnemy)

        #Gestion pourrie des d�calages de sprite
        #A partir de l'�tat en cours, il faut "redescendre" progressivement les etats de
        #levage du flingue, jusqu'� arriver � l'�tat normal.
        #(en appliquant � chaque fois les d�calages qui vont bien),
        #et enfin, on peut mettre l'image de HURT, avec le d�calage NORM -> HURT
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

        #d�termination de la position de d�part des giclures de sang. splatch !
        self.posBlood = self.rectPos.move(DECAL_HURT_BLOOD.topleft)

        if self.lifePoint >= 0:

            #Le h�ros n'est pas encore mort.
            #g�n�ration d'un gros tas de sang !!
            funcGenBlood = self.spriteSimpleGenerator.generateSomeBlood
            funcGenBlood(self.posBlood, NBR_BLOOD_HURT)

            #changement de l'etat vers HURT
            self.changeState(HURT, DECAL_NORM_HURT)
            #le son du h�ros qui a mal : argh !!
            theSoundYargler.playSound(SND_HERO_HURT)

        else:

            #le h�ros n'a plus de point de vie, il doit mouwwwriiiiiir. (etat = DYING)
            #initialisation du compteur de giclage de sang + tournage de t�te
            #comme c'est � 0, �a va ex�cuter la fonction dyingBloodTurnHead tout de
            #suite apr�s, et apr�s �a recommencera et etc.
            self.counterBlood = 0

            #changement de l'etat.
            self.changeState(DYING, DECAL_NORM_HURT)

        #on a fait un changement d'�tat.
        return FUNCTION_CHANGED_STATE


    def endOfHurt(self):
        """
        fonction a ex�cuter � la fin de l'etat HURT. Il faut faire revenir le h�ros �
        l'�tat normal. Et prendre en compte les �ventuels �v�nements qu'on pouvait
        pas prendre en compte pendant qu'on �tait HURT (r�armement et rechargement)
        """

        #on fait le r�armage si le h�ros s'est fait interrompte par le hurt
        #alors qu'il faisait son r�armage juste apr�s le Fire.
        if self.mustRearm:
            #encore du d�calage de mayrde
            self.heroBody.rect.move_ip(DECAL_HURT_NORM.topleft)
            self.changeState(RAISE_ARMING_1, DECAL_NORM_RAISE1)
            return FUNCTION_CHANGED_STATE

        #si 0 cartouches, on lance automatiquement un rechargement.
        if self.nbrCartouche == 0:
            #encore du d�calage de mayrde
            self.heroBody.rect.move_ip(DECAL_HURT_NORM.topleft)
            self.changeState(RAISE_REL_1, DECAL_NORM_RAISE1)
            return FUNCTION_CHANGED_STATE

        #Les deux blocs ci-dessus serait factorisable. Je le fait pas parce qu'ils
        #auront que 2 lignes chacun quand j'aurais g�r� le hotPoint. Et �a vaut pas le coup
        #de facto 2 lignes, surtout si l'une d'elle est un return.

        #si y'a pas d'�v�nement sp�ciaux, y'a rien � faire
        #La machine � �tat va faire revenir tout seul � l'�tat normal.
        return FUNCTION_DID_NOT_CHANGED_STATE


    def determineHurtMovement(self, posEnemy):
        """
        d�termine la direction, l'acc�l�ration, la p�riode et le nombre de mouvement
        de Hurt � effectuer.
        Quand le h�ros se fait Hurt, il bouge automatiquement pendant quelques cycles,
        dans une des 4 directions, ou en diagonale, de fa�on � s'�loigner du magicien
        qui l'a touch�.
        Le joueur peut continuer de diriger le h�ros pendant qu'il est Hurt. Les deux
        mouvements s'additionneront.

        entr�es :
            posEnemy : rect(Xn Y) : position du magicien qui a fait mal au h�ro
                       cela permet de d�finir dans quelle direction de HURT le h�ro
                       doit bouger. (Il va aller dans le sens oppos� au magicien)

        plats-dessert : rien. Mais d�finition d'un tas de variables :
        self.rectHurtMove, self.rectHurtAccel, ...
        """

        #init des variables indiquant les mouvements sur les axes X et Y.
        #3 valeurs possibles :
        # -1 : mvt gauche/haut
        #  0 : pas de mvt
        # +1 : mvt droite/bas
        hurtMoveDirX = 0
        hurtMoveDirY = 0

        #si il y a une distance assez grande sur l'axe X, entre le magicien et le h�ros
        #alors le h�ros fera un mouvement sur le X
        if abs(self.rectPos.centerx - posEnemy.centerx) > HURT_RECUL_DIST:
            #d�termination du sens du mouvement sur X (faut s'�loigner du magicien)
            if self.rectPos.centerx > posEnemy.centerx:
                hurtMoveDirX = +1
            else:
                hurtMoveDirX = -1

        #si il y a une distance assez grande sur l'axe Y, entre le magicien et le h�ros
        #alors le h�ros fera un mouvement sur le Y
        if abs(self.rectPos.centery - posEnemy.centery) > HURT_RECUL_DIST:
            #d�termination du sens du mouvement sur Y (faut s'�loigner du magicien)
            if self.rectPos.centery > posEnemy.centery:
                hurtMoveDirY = +1
            else:
                hurtMoveDirY = -1

        #on d�termine si le mouvement � faire est tout droit, dans l'une des 4 directions,
        #ou en diagonale.
        if hurtMoveDirX != 0 and hurtMoveDirY != 0:
            #le mouvement est droit. On initialise le d�placement initial et
            #la d�c�l�ration a des valeurs assez importantes, car on bouge que dans une
            #seule direction.
            hurtMoveInit = HURT_MOVE_INIT_DIAG
            hurtDecel = HURT_DECEL_DIAG
        elif hurtMoveDirX != 0 or hurtMoveDirY != 0:
            #le mouvement est diagonal. On intialise le d�placement initial et la d�c�l�ration
            #� des valeurs plus faibles. Car ce d�placement se fera sur les deux directions.
            #Donc faut contrebalancer cela, voyez.
            hurtMoveInit = HURT_MOVE_INIT_STRAIGHT
            hurtDecel = HURT_DECEL_STRAIGHT
        else:
            #on n'a d�termin� aucun mouvement. Dans ce cas, on met � l'arrache, par d�faut,
            #un mouvement droit, vers la gauche, et basta
            hurtMoveDirX = -1
            hurtMoveDirY = 0
            hurtMoveInit = HURT_MOVE_INIT_STRAIGHT
            hurtDecel = HURT_DECEL_STRAIGHT

        #d�termination du Rect contenant les coordonn�es de d�placement initiale,
        #en fonction de la valeur de d�placement et des directions.
        self.rectHurtMove = pyRect(hurtMoveDirX * hurtMoveInit,
                                   hurtMoveDirY * hurtMoveInit)

        #d�termination du Rect contenant les coordonn�es d'acc�l�ration.
        #Je le d�finit � partir de hurtDecel, et du coup, faut foutre des "moins".
        #car la deceleration est l'oppos� de l'acceleration
        self.rectHurtAccel = pyRect(-hurtMoveDirX * hurtDecel,
                                    -hurtMoveDirY * hurtDecel)

        #compteur pour la p�riode de mouvement
        self.hurtMoveCounter = HURT_MOVE_PERIOD
        #compteur pour la p�riode d'acc�l�ration (d�c�l�ration en fait, blabla)
        self.hurtAccelCounter = HURT_DECEL_PERIOD
        #nombre de mouvement de Hurt restant � faire.
        self.hurtNbrMoveLeft = HURT_NBR_MOVE


    def makeHurtMovement(self):
        """
        effectuage du mouvement de Hurt. Fonction � ex�cuter � chaque cycle,
        pendant le Hurt.

        Alors c'est du code qui se retrouve un peu pareil ailleurs. (mouvement des SimpleSprite)
        Bon, je vois pas trop comment le factoriser. Ou alors avec une classe MovingPointAccel
        Mais c'est pousser le vice un peu loin. Pis en plus c'est chiant parce qu'il
        faudrait sans arr�t transf�rer les coordonn�es du MovingPointAccel vers le hero.
        Donc pas de facto. D�sol�
        """

        #Il n'y a rien � faire pendant le Hurt si on a fini tous les mouvements.
        if self.hurtNbrMoveLeft <= 0:
            return

        # --- application du mouvement sur la position ---
        #     (pas tout � fait, en fait c'est : ajout du mouvement au buffer de mouvement)

        self.hurtMoveCounter -= 1

        if self.hurtMoveCounter == 0:
            self.hurtMoveCounter = HURT_MOVE_PERIOD
            self.addMoveInBuffer(self.rectHurtMove)
            #diminution du compteur indiquant le nombre de mouvement de Hurt restant � faire.
            self.hurtNbrMoveLeft -= 1

        # --- application de l'acc�l�ration sur le mouvement. ---

        self.hurtAccelCounter -= 1

        if self.hurtAccelCounter == 0:
            self.hurtAccelCounter = HURT_DECEL_PERIOD
            self.rectHurtMove.move_ip(self.rectHurtAccel.topleft)


    def dyingBloodTurnHead(self):
        """
        Fonction a ex�cuter de temps en temps, pour faire l'anim du h�ros qui meurt.

        La fonction fait tourner la t�te du h�ros, g�n�re une petite giclure de sang,
        et d�termine dans combien de cycle il faudra re-ex�cuter cette fonction.

        On ne cherche pas � d�terminer � quel moment il faudrait arr�ter d'ex�cuter cette fonction
        Ca va s'arr�ter tout seul, car le jeu arr�te la partie quelques temps apr�s que le
        h�ros soit mouru.
        """

        #tournage de tete du h�ros. S'il regardait � gauche, il regardera � droite, et vice-versa.
        self.heroHead.turnHead()

        #r�actualisation de la position de g�n�ration du sang.
        #car le h�ros a peut-�tre boug� � cause des hurtMovements
        self.posBlood = self.rectPos.move(DECAL_HURT_BLOOD.topleft)

        #g�n�ration d'une petite giclure de sang.
        funcGenBlood = self.spriteSimpleGenerator.generateSomeBlood
        funcGenBlood(self.posBlood, NBR_BLOOD_DYING)

        #le son du h�ros qui a mal : argh !!
        theSoundYargler.playSound(SND_HERO_HURT)

        #recalcul, avec un peu de random, du temps avant qu'on re-ex�cute cette fonction.
        self.counterBlood = randRange(DELAY_BLOOD_DYING_MIN,
                                      DELAY_BLOOD_DYING_MAX)


    def updateDying(self):
        """
        fonction a ex�cuter � chaque cycle, quand le h�ros est en train de crever,
        pour faire son animation de crevage.
        """

        #r�alisation du mouvement de Hurt.
        #(M�me quand le h�ros meurt, on fait les mouvements de Hurt)
        self.makeHurtMovement()

        #ex�cution p�riodique-de-temps-en-temps de l'anim de crevage (sang + tournage de t�te)
        self.counterBlood -= 1

        if self.counterBlood <= 0:
            self.dyingBloodTurnHead()


    def endOfDying(self):
        """
        fonction qui s'ex�cute quand le h�ros est vraiment mort (apr�s son anim de crevage)
        """
        #y'a rien de sp�cial � faire car c'est g�r� par le jeu. On balance juste un son cool.
        theSoundYargler.playSound(SND_HERO_DIE)
        #y'a pas eu de changement d'�tat.
        return FUNCTION_DID_NOT_CHANGED_STATE
