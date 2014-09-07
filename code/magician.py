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

date de la derni�re relecture-commentage : 05/10/2010

la classe pour g�rer le magicien.

Vocabulaire et comportement du magicien (magicien de base) :

Trucs g�r�s par ce magicien de base :
 - Collision avec le h�ros, qui se fait Hurt et perd un point de vie.
 - Collision avec les bullets.
 - Gestions des points de vie. Anim de morts / d'explosion.
 - Comptabilisation du nombre de magiciens tu�s / explos�s.
 - Mont�e de niveau initiale (LevelUp), au moment de la cr�ation du magicien.

Trucs pas g�r�s :
 - Le magicien de base ne se d�place pas.
 - Les mont�es de niveau du magicien de base n'ont aucun effet.
 - Le magicien de base ne fait pas de mont�e de niveau au fur � mesure du temps,
   il fait quand m�me les mont�e initiale. (Quand on veut cr�er un magicien ayant
   directement le niveau 5, par exemple)


pour d'autres explications sur les magiciens :
 - comment sont g�r�s les collisions avec les bullets que tire le h�ros
 - l'�volution de ces �tats (APPEARING, ALIVE, HURT, ...)
voir le fichier cobulmag.py

pour les trois types de mort du magicien, (NAKED, SHIT et ROTATE), il y a
une fonction initDyingXX et UpdateDyingXXX.
On choisit le type de mort et on doit ex�cuter la fonction Init correspondante,
puis � chaque cycle on ex�cute la Update correspondante.
C'est la liste BRANCH_DYING_FUNCTION qui s'occupe de �a.

Quand le magicien explose (BURSTING) y'a qu'une anim. Pas le choix

PUTAIN Y'A UNE LIGNE TROP LONGUE ET JE LA TROUVE PAS CA M'ENERVE !
Y'A LA BARRE DE DEFILEMENT HORIOZONTAL DANS NOTEPAD++ ET JE COMPREND PAS POURQUOI
MERDE !! MERDE !!! MERDE !! MERERERDE MERDE !!!
Ah non c'est bon. C'est notepad++ qui plante. Fallait fermer-rouvrir le fichier.
Bizarre quand m�me.

id�e � la con : essayer de faire h�riter le magicien de SimpleSprite. Comme �a pour ses
animations de mort, y'a juste � d�finir la liste d'image et de d�calage qui va bien,
et � faire l'update du SimpleSprite. Y'aurait juste un peu de bidouille � faire
au niveau des SPRITE_ALIVE et SPRITE_DEAD, qu'il faut convertir en currentState de magicien.
Objection rejet�e. Quand le magicien cr�ve, on cr�e un simple sprite avec l'anim de sa mort
Mais le magicien lui-m�me n'est pas un simple sprite. Ce serait zarb et �a me plait pas.
"""

import pygame

from common import (centeredRandom, randRange,
                    GAME_SIZE_X, GAME_RECT, pyRect, oppRect)

from sprsimpl import SPRITE_ALIVE, SPRITE_DEAD, SpriteSimple

#le magicien utilise le Simple Sprite Generator pour g�n�rer des Sprite "Fume" qui sorte
#de son cul lorsqu'il est DYING_NAKED, et pis des morceaux quand il BURST
from sprsigen import SpriteSimpleGenerator

from yargler import (theSoundYargler, SND_MAG_BURST, SND_MAG_DYING_ROTATE,
                     SND_MAG_DYING_SHIT, SND_MAG_DYING_FART, SND_MAG_HURT)


#liste des identifeurs d'images du magicen
(IMG_NORMAL,           #image du magicien normal
 IMG_DYING_NAKED,      #image de l'anim DYING_NAKED
 IMG_HURT,             #image du magicien quand il se prend une balle mais qu'il creve pas.
) = range(3)

#pr�fixe dans les noms de fichiers image du magicien.
IMG_FILENAME_PREFIX = "m"

#correspondance entre nom de fichier court et identifiant d'image
#pour trouver le vrai nom du fichier : <prefix> + <nomcourt> + ".png"
LIST_IMG_FILE_SHORT_NAME = (
 (IMG_NORMAL,      "norm"),
 (IMG_DYING_NAKED, "naked"),
 (IMG_HURT,        "hurt"),
)

#taille du magicien. (J'aurais pu prendre directos les tailles de son image,
#mais j'avais pas envie)
MAGICIAN_SIZE  = pyRect(0, 0, 21, 33)

#les etats du magicien
(APPEARING,         #en train d'appara�tre � l'�cran
 ALIVE,             #vivant, etat normal
 HURT,              #en train de se prendre une/plusieurs balles dans la gueule
 DYING,             #en train de crever (animation � la con du magicien qui meurt)
 BURSTING,          #en train d'exploser (anim � la con)
 DEAD,              #mort. La boucle principale du jeu doit le supprimer.
) = range(6)

#nombre de point de vie initial du magicien. Un bullet enl�ve un point de vie.
LIFE_POINT_INIT = 2

#nombre de points de d�gats que doit se prendre le magicien en une seule fois, pour se faire BURST
#En th�orie, le BURST s'applique m�me si il reste des points de vie au magicien.
#(Quand on se prend plein de points de d�gats d'un coup, on cr�ve automatiquement, m�me si on
#�tait en super forme au d�part). En pratique, osef, car le magicien a moins de points
#de vie que le nombre de points de d�gats d'un BURST.
DAMAGE_FOR_BURSTING = 3

#le magicien doit rester dans l'�cran, mais il peut d�passer un peu � droite et en bas. Ca donne
#l'impression qu'il arrive d'autre part. Wouhou !!!
#Nombre de pixel qu'il a le droit de d�passer � droite
CLAMPING_MARGIN_RIGHT = 25
#Nombre de pixel qu'il a le droit de d�passer en bas
CLAMPING_MARGIN_BOTTOM = 35
#zone de clamping, dans laquelle le magicien doit rester.
#on tient compte de la marge � ajouter en haut et en bas.
#(petite disgression : quand on modifie l'attribut right ou bottom,
#�a change pas la taille du rectangle. Ca le d�place !! Je m'ai fait avoir au d�but.)
MAGI_RECT_CLAMPING = pyRect(GAME_RECT.x,
                            GAME_RECT.y,
                            GAME_RECT.width + CLAMPING_MARGIN_RIGHT,
                            GAME_RECT.height + CLAMPING_MARGIN_BOTTOM)


#d�calage de l'image normale vers l'image hurt
DECALAGE_NORM_HURT = pyRect(-1, 0)
DECALAGE_HURT_NORM = oppRect(DECALAGE_NORM_HURT)

#les 3 animations possibles de mort du magicien.
#(lorsqu'il meurt, on en choisit une au hasard)
(DYING_ROTATE,   #Le magicien tournoye, et se p�te la gueule vers le bas en une splendide courbe
 DYING_SHIT,     #Le magicien se tranforme en caca qui d�gouline
 DYING_NAKED,    #Le magicien paume ses fringues et s'envole vers le haut en p�tant.
) = range(3)

#j'ai besoin de ce truc parce que je dois pouvoir choisir au hasard entre l'une des morts possibles
#donc faites pas chier OK?
LIST_DYING_TYPE = (DYING_ROTATE, DYING_SHIT, DYING_NAKED)

#juste deux identifiants � la con, pour savoir quelle fonction on veut r�cup�rer
#lorsqu'on cherche la fonction init/update correspondant � la mort choisie
BRANCH_DYING_INIT = 0
BRANCH_DYING_UPDATE = 1

#d�calage � appliquer lorsqu'on passe de l'image du magicien normal � l'image DYING_NAKED
DECAL_DYING_NAKED = pyRect(0, 2)

#P�riode de mouvement quand le magicien est DYING_NAKE (il bouge 1 fois tous les X cycles. X=2)
DYIND_NAKED_MOVE_PERIOD = 2

#nombre de cycle de jeu � attendre entre 2 pets du magicien, quand il DYING_NAKED
#le nombre de cycle est calcul� al�atoirement, entre la valeur min et la valeur max
FART_PERIOD_MAX = 20
FART_PERIOD_MIN = 5

#d�calage entre l'image du magicien et la position de d�part du sprite de pet
DECAL_MAGICIAN_FART = pyRect(10, 26)



class Magician(pygame.sprite.Sprite):
    """
    le sprite qui est le magicien
    """

    def __init__(self, dicMagicienImg, spriteSimpleGenerator,
                 posStart, level=1):
        """
        constructeur. (thx captain obvious)

        entr�e :
            dicMagicienImg        : dictionnaire de correspondance identifiant d'image -> image

            spriteSimpleGenerator : classe eponyme. Pour que le magicien g�n�re
                                    des petits sprites si il a envie (quand il pete, ou burste)

            posStart              : Rect. position du coin superieur gauche du sprite, � l'�cran.

            level                 : int. Valeur initiale du level du magicien. (ne sert pas �
                                    grand chose pour le magicien de base, mais les autres, oui)
        """
        pygame.sprite.Sprite.__init__(self)

        #init d'un tas de truc.
        self.dicMagicienImg = dicMagicienImg
        self.spriteSimpleGenerator = spriteSimpleGenerator
        self.image = dicMagicienImg[IMG_NORMAL]
        self.rect = pygame.Rect(posStart.topleft + MAGICIAN_SIZE.size)

        #d�finition du level. On peut pas fixer directement le level souhait�, car � priori,
        #on sait pas ce que fait la fonction levelUp. donc faut les monter un par un.
        self.resetToLevelOne()
        for _ in xrange(1, level):
            self.levelUp()

        #g�n�ration du sprite qui fait l'anim d'apparition du magicien.
        #(c'est pas g�r� par cette classe-ci, mais par un simpleSprite)
        #le magicien garde une r�f�rence sur le SimpleSprite de son anim d'apparition,
        #Ca lui permettra de savoir quand cet anim est termin�e.
        fonc = self.spriteSimpleGenerator.generateMagAppearing
        self.spriteAppearing = fonc(posStart)

        #Au d�but, le magicien ne peut pas agir, il fait son anim d'apparition
        self.currentState = APPEARING

        self.lifePoint = LIFE_POINT_INIT

        #Yeaaaahh. Je trouve �a super cool de pouvoir faire �a, crac, directos !!
        #c'est un dictionnaire avec :
        # -    cl� : l'identifiant de l'�tat du magicien
        # - valeur : la fonction update � appeler quand le magicien est dans cet �tat
        #
        #Je fout pas ce dico en const. Comme �a je branche vers les fonctions de l'instance de
        #classe, et non pas vers les fonctions de la classe. C'est plus logique.
        #Et si j'h�rite vers une autre classe et que je change les fonctions d'update,
        #�a me p�tera pas � la gueule. (D'autant plus que je le fais, cet h�ritage)
        self.BRANCH_UPDATE = {
            HURT      : self.updateHurt,
            DYING     : self.updateDying,
            ALIVE     : self.updateNormal,
            APPEARING : self.updateAppearing,
            BURSTING  : self.dieImmediatlyBlarg,
            #quand le magicien est DEAD, on n'est plus cens� ex�cuter son update.
            #je branch un petit coup quand m�me vers une fonction � la con,
            #pour plus de robustaysse.
            DEAD      : self.dieImmediatlyBlarg,
        }

        #init d'un dico qui fait les branchements : type de mort -> fonctions � ex�cuter
        #Pour la m�me raison que ci-dessus, ce dico est cr�� ici, et pas en const.
        #Les valeurs de ce dico sont des tuples de 2 element :
        # - fonction qu'il faut lancer au d�but, lorsqu'on veut initialiser
        #   l'anim de mort correspondante du magicien.
        # - fonction � lancer � chaque cycle, pour updater l'anim de mort.
        #   on update jusqu'� ce qu'elle soit finie, et que l'objet magicien soit delet�
        #
        #Pour certaines morts, la fonction d'update est dieImmediatlyBlarg. Ca veut dire
        #qu'il n'y a plus rien � faire, et on delete le magicien tout de suite. Ce sont
        #les morts o� l'animation est enti�rement g�r�e par des SimpleSprite, qui ont
        #�t� g�n�r�s lors de l'appel de la fonction Init.
        self.BRANCH_DYING_FUNCTION = {
            DYING_ROTATE : (self.initDyingRotate, self.dieImmediatlyBlarg),
            DYING_SHIT   : (self.initDyingShit,   self.dieImmediatlyBlarg),
            DYING_NAKED  : (self.initDyingNaked,  self.updateDyingNaked),
        }


    def isMoveFinished(self):
        """
        permet d'indiquer au code ext�rieur si le magicien a fini son mouvement ou pas
        """
        #on renvoie tout de suite True, car le magicien de base ne bouge pas
        return True


    def resetToLevelOne(self):
        """
        initialise/r�initialise le level � 1, et remet les caract�ristiques d�pendante du level
        � leur valeur initiale pourrite.
        """
        self.level = 1
        #le magicien de base n'a rien de plus � se r�initialiser


    def levelUp(self):
        """
        Fonction permettant au magicien de faire un levelUp et de monter ses caract�ristiques.
        """
        self.level += 1
        #le magi de base n'a rien de plus � upper.


    def TakeStimuliTouchedHero(self):
        """
        fonction ex�cut�e par le code ext�rieur, lorsque le magicien vient de toucher le h�ros,
        et de lui faire mal. paf !!
        """
        #Le magicien revient au niveau 1 quand il a fait mal au joueur.
        #�a permet de diminuer le risque d'une autre collision tr�s vite,
        #� peine quelques cycles plus tard. Car �a ne serait pas tr�s gentil pour le joueur.
        self.resetToLevelOne()


    def hitByBullet(self, Damage):
        """
        Fonction � ex�cuter par le code ext�rieur.
        La fonction permet d'indiquer au magicien qu'il s'est pris des bullets dans la gueule.

        entr�es :
            Damage. int. Nombre de points de d�g�ts ( = nombre de bullets qui le touchent)

        plat-dessert :
            identifiant de l'�tat actuel du magicien, apr�s qu'il s'est pris le bullet.
            Ca peut �tre HURT, ou DYING, ou BURSTING
        """

        #si le magicien se prend X bullets d'un coup, il explose direct : BURST. (X = 3)
        #on ne contr�le m�me pas ses points de vie restants. (Pis de toutes fa�ons il en a que 2)
        #Il y a une anim de mourage sp�cifique au BURST
        if Damage >= DAMAGE_FOR_BURSTING:
            self.initBursting()
            #va renvoyer l'�tat BURSTING
            return self.currentState

        #on retire le nombre de points de d�g�ts aux points de vie du magicien.
        self.lifePoint -= Damage

        if self.lifePoint <= 0:

            #plus de points de vie, donc le magicien va crever.
            self.currentState = DYING

            #choix au hasard d'un moyen de crevage.
            dyingTypeIndex = randRange(len(LIST_DYING_TYPE))
            dyingType = LIST_DYING_TYPE[dyingTypeIndex]
            #r�cup�ration vers la fonction initialisant le moyen de mourage choisi
            dyingTypeBranching = self.BRANCH_DYING_FUNCTION[dyingType]
            funcDyingInit = dyingTypeBranching[BRANCH_DYING_INIT]
            #ex�cution de cette fonction
            funcDyingInit()

        else:

            #le magicien ne va pas BURST, et il a encore des points de vie.
            #Donc il a juste mal (HURT)

            #C'est une fonction s�par�e qui g�re ce cas, car il faut pouvoir la surcharger
            #quand on fait les classes-fifilles.
            self.hitByBulletButNotDead(Damage)

        return self.currentState


    def hitByBulletButNotDead(self, Damage):
        """
        fonction d�finissant les actions � faire quand le magicien s'est pris
        des bullets, mais qu'il n'en est pas mort. (il est HURT)

        entr�es :
            Damage. int. Nombre de points de d�g�ts ( = nombre de bullets qui le touchent)
        """

        #pas de diminution des points de vie. D�j� fait par la fonction appelante (hitByBullet)

        self.currentState = HURT

        #changement de l'image du sprite et application du d�calage
        self.image = self.dicMagicienImg[IMG_HURT]
        self.rect.move(DECALAGE_NORM_HURT.topleft)
        #son qui fait "arh je suis un magicien et j'ai mal"
        theSoundYargler.playSound(SND_MAG_HURT)

        #pour les classes d�riv�es du magician : lorsqu'il est hurt, on peut
        #rajouter des trucs ici. Par exemple, l'initialisation d'un mouvement de recul
        #on peut auissi ajouter un compteur, pour que le magicien reste hurt
        #un certain temps. Quand c'est fini, on ex�cutera la fonction unHurt
        #(il faut g�rer tout �a par rapport au code qu'on met dans la fonction updateHurt


    def updateNormal(self):
        """
        update du magicien (fonction qui se lance � chaque cycle de jeu)
        cas o� le magicien est dans son �tat normal (ALIVE)
        """
        #ici, on peut g�rer des mouvements du magicien,
        #des mont�es de niveau, plein d'autres trucs
        #dans cette classe de base, on ne fait rien.
        pass


    def unHurt(self):
        """
        fonction � lancer quand le magicien s'est fait HURT, et qu'il faut
        le remettre dans l'�tat normal
        """
        #et donc oui, on le remet dans l'�tat normals
        self.currentState = ALIVE

        #retour � l'image de sprite du magicien normal, et application du d�calage.
        self.image = self.dicMagicienImg[IMG_NORMAL]
        self.rect.move(DECALAGE_HURT_NORM.topleft)


    def updateHurt(self):
        """
        update du magicien (fonction qui se lance � chaque cycle de jeu)
        Cas o� le magicien s'est pris des d�gats y'a pas longtemps (HURT)
        """
        #ici, on peut faire un mouvement, ou d'autres choses.
        #mais il faut obligatoirement ex�cuter unHurt au bout d'un certain nombre de cycle,
        #pour le magicien de base, on fait unHurt imm�diatement. (on va au plus simple)
        self.unHurt()


    def initBursting(self):
        """
        Fonction pemettant d'initialiser l'anim
        et les SpriteSimple du magicien qui explose (BURST)
        """

        self.currentState = BURSTING

        #son : "spflark !!"
        theSoundYargler.playSound(SND_MAG_BURST)

        # --- g�n�ration des parties du corps ensanglant�s qui s'envolent ---
        # chaque partie du corps est un simple sprite, g�n�r�e bien comme il
        # faut par le SimpleSpriteGenerator. La position de d�part des parties
        # du corps est prise � partir de la position du magicien, avec un petit
        #d�calage en plus.

        #le bras droit
        armPosStartRight = self.rect.move(pyRect(10, 2).topleft)
        self.spriteSimpleGenerator.generateMagBurstArmRight(armPosStartRight)

        #le bras gauche
        armPosStartLeft = self.rect.move(pyRect(0, 2).topleft)
        self.spriteSimpleGenerator.generateMagBurstArmLeft(armPosStartLeft)

        #la t�te
        headPosStart = self.rect.move(pyRect(5, -3).topleft)
        self.spriteSimpleGenerator.generateMagBurstHead(headPosStart)

        #le simple sprite de l'anim du corps en train d'exploser.
        self.spriteSimpleGenerator.generateMagBurstSplat(self.rect)


    def initDyingRotate(self):
        """
        Fonction � lancer lorsque le magicien va crever dans l'animation DYING_ROTATE.
        """

        self.currentDyingState = DYING_ROTATE

        #son : "heeuehhaauuehheuuuaarrghh !!"
        theSoundYargler.playSound(SND_MAG_DYING_ROTATE)

        #g�n�ration d'un SimpleSprite, repr�sentant un magicien qui meurt en tournoyant
        #et en planant en une magnifique parabole qui finit dans les tr�fonds du bas de l'�cran.
        self.spriteSimpleGenerator.generateMagDyingRotate(self.rect)


    def initDyingShit(self):
        """
        Fonction � lancer lorsque le magicien va crever dans l'animation DYING_SHIT.
        """

        self.currentDyingState = DYING_SHIT

        #son : "heuarshblorf !!"
        theSoundYargler.playSound(SND_MAG_DYING_SHIT)

        #on g�n�re un spriteSimple, repr�sentant l'anim de transformation en merde.
        self.spriteSimpleGenerator.generateMagDyingShit(self.rect)


    def initDyingNaked(self):
        """
        Fonction � lancer lorsque le magicien va crever dans l'animation DYING_NAKED.

        On peut pas se contenter de g�nrer cette anim avec uniquement des SpriteSimple,
        car le magicien, quand il s'envole tout nu, g�n�re des petits nuages de pets.
        Les nuages de pets sont des SpriteSimple. Mais leur g�n�ration ne peut pas
        �tre confi�e � un SpriteSimple, car ils ne sont pas pr�vus pour �a.

        Donc l'objet magicien est toujours pr�sent pendant un DYING_NAKED,
        et on le d�truit lorsque l'anim est finie.
        """

        self.currentDyingState = DYING_NAKED

        #changement de l'image du sprite, et application du d�calage qui va avec
        self.image = self.dicMagicienImg[IMG_DYING_NAKED]
        self.rect.move_ip(DECAL_DYING_NAKED.topleft)

        #initialisation des trucs pour le mouvement. (vers le haut, sans accel)
        #en fait y'aura une accel en X, al�atoire vers la gauche ou la droite,
        #mais on la rajoutera plus tard.
        self.moveCounter = DYIND_NAKED_MOVE_PERIOD
        self.speed = pyRect(0, -4)
        self.currentAccel = pyRect()

        #�a y'en aura besoin pour savoir quand le magicien est sorti de l'�cran.
        self.image_height = self.image.get_height()

        #compteur avant le prochain pets, pour savoir quand g�n�rer un SimpleSprite de type "Fume"
        self.fartCounter = randRange(FART_PERIOD_MIN, FART_PERIOD_MAX)


    def updateDyingNaked(self):
        """
        fonction update de l'anim de mort DYING_NAKED
        """

        # --- gestion des prouts du magicien ---

        #diminution du compteur avant le prochain pets.
        self.fartCounter -= 1

        if self.fartCounter == 0:

            # il faut p�ter !!!
            #d�termination de la position d'o� g�n�rer le prout
            fartPosStart = self.rect.move(DECAL_MAGICIAN_FART.topleft)
            #g�n�ration du prout (c'est un SimpleSprite de type Fume).
            self.spriteSimpleGenerator.generateFume(fartPosStart)
            #son qui fait prout. prout !!
            theSoundYargler.playSound(SND_MAG_DYING_FART)
            #reinit du compteur de prout, pour la prochaine g�n�ration.
            self.fartCounter = randRange(FART_PERIOD_MIN, FART_PERIOD_MAX)

        # --- gestion du mouvement du magicien ---

        #diminution du compteur avant le prochain mouvement.
        self.moveCounter -= 1

        if self.moveCounter == 0:

            # il faut bouger.
            #on applique une petite acc�l�ration al�atoire sur la vitesse en X.
            #comme �a le magicien monte en zigzagouillant, ce qui est fort rigolo.
            self.speed.left = centeredRandom(2)

            #application de la vitesse sur la position
            self.rect.move_ip(self.speed.topleft)

            #quand il sort compl�tement de l'�cran par le haut, le magicien peut �tre delet�.
            if self.rect.top < -self.image_height:
                self.currentState = DEAD

            #Reinit du compteur avant le prochain mouvement
            self.moveCounter = DYIND_NAKED_MOVE_PERIOD


    def dieImmediatlyBlarg(self):
        """
        fonction a ex�cuter quand le magicien est mort, qu'on a g�r� son anim de mort,
        et qu'on a plus du tout besoin de lui (l'objet de magicien peut �tre delet�).
        """

        #c'est le code ext�rieur qui s'occupe de la supression effective de l'objet magicien
        #(puisque c'est aussi lui qui s'est occup� de le cr�er).
        #on pr�vient le code ext�rieur qu'il faut deleter en fixant son �tat � DEAD.
        self.currentState = DEAD


    def updateDying(self):
        """
        Haha, �a c'est une fonction qu'elle est rigolote.
        C'est juste pour savoir quelle fonction updateDyingXXX il faut ex�cuter,
        en fonction du type de Dying. Mais c'est fait de mani�re classe et raffin�e.
        """

        #on r�cup�re la liste de fonction g�rant le type de DYING actuel.
        dyingTypeBranching = self.BRANCH_DYING_FUNCTION[self.currentDyingState]
        #dans cette liste, on r�cup�re la fonction pour l'update
        funcDyingUpdate = dyingTypeBranching[BRANCH_DYING_UPDATE]
        #ex�cution de cette fonction. Woot !!!
        funcDyingUpdate()


    def updateAppearing(self):
        """
        fonction update. Cas o� le magicien est en train d'appara�tre (APPEARING)

        Le magicien n'a pratiquement rien � faire pendant qu'il est appearing, car l'anim
        est g�r�e par un SimpleSprite. Le magicien se contente d'inspecter le SimpleSprite
        pour voir si il a termin� son anim ou pas.
        """

        #s�curit� un peu inutile. Quand le self.spriteAppearing est devenu None, c'est forc�ment
        #que la fin de l'anim d'apparition a �t� prise en compte.
        #Donc on n'ex�cute plus cette fonction. Mais bon, hop, soyons fou.
        if self.spriteAppearing is not None:

            if self.spriteAppearing.currentState == SPRITE_DEAD:

                #l'anim d'apparition du magicien est termin�, donc on change son �tat.
                self.currentState = ALIVE

                #et on vire la r�f�rence au simpleSprite d'apparition. Y'en a plus besoin
                #car on ne l'affiche plus. (Il n'est plus dans le groupe de sprite
                #rassemblant tous les SimpleSprite)
                self.spriteAppearing = None


    def update(self):
        """
        fonction g�n�rique pour l'update du magicien.
        Celle l� aussi elle est classe, comme la fonction pr�pr�c�dente.
        """

        #on r�cup�re la bonne fonction, selon l'�tat actuel
        funcUpdate = self.BRANCH_UPDATE[self.currentState]
        #et on l'ex�cute.  Tadzaaaamm !!
        funcUpdate()

