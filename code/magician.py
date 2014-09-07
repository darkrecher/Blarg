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

date de la dernière relecture-commentage : 05/10/2010

la classe pour gérer le magicien.

Vocabulaire et comportement du magicien (magicien de base) :

Trucs gérés par ce magicien de base :
 - Collision avec le héros, qui se fait Hurt et perd un point de vie.
 - Collision avec les bullets.
 - Gestions des points de vie. Anim de morts / d'explosion.
 - Comptabilisation du nombre de magiciens tués / explosés.
 - Montée de niveau initiale (LevelUp), au moment de la création du magicien.

Trucs pas gérés :
 - Le magicien de base ne se déplace pas.
 - Les montées de niveau du magicien de base n'ont aucun effet.
 - Le magicien de base ne fait pas de montée de niveau au fur à mesure du temps,
   il fait quand même les montée initiale. (Quand on veut créer un magicien ayant
   directement le niveau 5, par exemple)


pour d'autres explications sur les magiciens :
 - comment sont gérés les collisions avec les bullets que tire le héros
 - l'évolution de ces états (APPEARING, ALIVE, HURT, ...)
voir le fichier cobulmag.py

pour les trois types de mort du magicien, (NAKED, SHIT et ROTATE), il y a
une fonction initDyingXX et UpdateDyingXXX.
On choisit le type de mort et on doit exécuter la fonction Init correspondante,
puis à chaque cycle on exécute la Update correspondante.
C'est la liste BRANCH_DYING_FUNCTION qui s'occupe de ça.

Quand le magicien explose (BURSTING) y'a qu'une anim. Pas le choix

PUTAIN Y'A UNE LIGNE TROP LONGUE ET JE LA TROUVE PAS CA M'ENERVE !
Y'A LA BARRE DE DEFILEMENT HORIOZONTAL DANS NOTEPAD++ ET JE COMPREND PAS POURQUOI
MERDE !! MERDE !!! MERDE !! MERERERDE MERDE !!!
Ah non c'est bon. C'est notepad++ qui plante. Fallait fermer-rouvrir le fichier.
Bizarre quand même.

idée à la con : essayer de faire hériter le magicien de SimpleSprite. Comme ça pour ses
animations de mort, y'a juste à définir la liste d'image et de décalage qui va bien,
et à faire l'update du SimpleSprite. Y'aurait juste un peu de bidouille à faire
au niveau des SPRITE_ALIVE et SPRITE_DEAD, qu'il faut convertir en currentState de magicien.
Objection rejetée. Quand le magicien crève, on crée un simple sprite avec l'anim de sa mort
Mais le magicien lui-même n'est pas un simple sprite. Ce serait zarb et ça me plait pas.
"""

import pygame

from common import (centeredRandom, randRange,
                    GAME_SIZE_X, GAME_RECT, pyRect, oppRect)

from sprsimpl import SPRITE_ALIVE, SPRITE_DEAD, SpriteSimple

#le magicien utilise le Simple Sprite Generator pour générer des Sprite "Fume" qui sorte
#de son cul lorsqu'il est DYING_NAKED, et pis des morceaux quand il BURST
from sprsigen import SpriteSimpleGenerator

from yargler import (theSoundYargler, SND_MAG_BURST, SND_MAG_DYING_ROTATE,
                     SND_MAG_DYING_SHIT, SND_MAG_DYING_FART, SND_MAG_HURT)


#liste des identifeurs d'images du magicen
(IMG_NORMAL,           #image du magicien normal
 IMG_DYING_NAKED,      #image de l'anim DYING_NAKED
 IMG_HURT,             #image du magicien quand il se prend une balle mais qu'il creve pas.
) = range(3)

#préfixe dans les noms de fichiers image du magicien.
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
(APPEARING,         #en train d'apparaître à l'écran
 ALIVE,             #vivant, etat normal
 HURT,              #en train de se prendre une/plusieurs balles dans la gueule
 DYING,             #en train de crever (animation à la con du magicien qui meurt)
 BURSTING,          #en train d'exploser (anim à la con)
 DEAD,              #mort. La boucle principale du jeu doit le supprimer.
) = range(6)

#nombre de point de vie initial du magicien. Un bullet enlève un point de vie.
LIFE_POINT_INIT = 2

#nombre de points de dégats que doit se prendre le magicien en une seule fois, pour se faire BURST
#En théorie, le BURST s'applique même si il reste des points de vie au magicien.
#(Quand on se prend plein de points de dégats d'un coup, on crève automatiquement, même si on
#était en super forme au départ). En pratique, osef, car le magicien a moins de points
#de vie que le nombre de points de dégats d'un BURST.
DAMAGE_FOR_BURSTING = 3

#le magicien doit rester dans l'écran, mais il peut dépasser un peu à droite et en bas. Ca donne
#l'impression qu'il arrive d'autre part. Wouhou !!!
#Nombre de pixel qu'il a le droit de dépasser à droite
CLAMPING_MARGIN_RIGHT = 25
#Nombre de pixel qu'il a le droit de dépasser en bas
CLAMPING_MARGIN_BOTTOM = 35
#zone de clamping, dans laquelle le magicien doit rester.
#on tient compte de la marge à ajouter en haut et en bas.
#(petite disgression : quand on modifie l'attribut right ou bottom,
#ça change pas la taille du rectangle. Ca le déplace !! Je m'ai fait avoir au début.)
MAGI_RECT_CLAMPING = pyRect(GAME_RECT.x,
                            GAME_RECT.y,
                            GAME_RECT.width + CLAMPING_MARGIN_RIGHT,
                            GAME_RECT.height + CLAMPING_MARGIN_BOTTOM)


#décalage de l'image normale vers l'image hurt
DECALAGE_NORM_HURT = pyRect(-1, 0)
DECALAGE_HURT_NORM = oppRect(DECALAGE_NORM_HURT)

#les 3 animations possibles de mort du magicien.
#(lorsqu'il meurt, on en choisit une au hasard)
(DYING_ROTATE,   #Le magicien tournoye, et se pète la gueule vers le bas en une splendide courbe
 DYING_SHIT,     #Le magicien se tranforme en caca qui dégouline
 DYING_NAKED,    #Le magicien paume ses fringues et s'envole vers le haut en pétant.
) = range(3)

#j'ai besoin de ce truc parce que je dois pouvoir choisir au hasard entre l'une des morts possibles
#donc faites pas chier OK?
LIST_DYING_TYPE = (DYING_ROTATE, DYING_SHIT, DYING_NAKED)

#juste deux identifiants à la con, pour savoir quelle fonction on veut récupérer
#lorsqu'on cherche la fonction init/update correspondant à la mort choisie
BRANCH_DYING_INIT = 0
BRANCH_DYING_UPDATE = 1

#décalage à appliquer lorsqu'on passe de l'image du magicien normal à l'image DYING_NAKED
DECAL_DYING_NAKED = pyRect(0, 2)

#Période de mouvement quand le magicien est DYING_NAKE (il bouge 1 fois tous les X cycles. X=2)
DYIND_NAKED_MOVE_PERIOD = 2

#nombre de cycle de jeu à attendre entre 2 pets du magicien, quand il DYING_NAKED
#le nombre de cycle est calculé aléatoirement, entre la valeur min et la valeur max
FART_PERIOD_MAX = 20
FART_PERIOD_MIN = 5

#décalage entre l'image du magicien et la position de départ du sprite de pet
DECAL_MAGICIAN_FART = pyRect(10, 26)



class Magician(pygame.sprite.Sprite):
    """
    le sprite qui est le magicien
    """

    def __init__(self, dicMagicienImg, spriteSimpleGenerator,
                 posStart, level=1):
        """
        constructeur. (thx captain obvious)

        entrée :
            dicMagicienImg        : dictionnaire de correspondance identifiant d'image -> image

            spriteSimpleGenerator : classe eponyme. Pour que le magicien génère
                                    des petits sprites si il a envie (quand il pete, ou burste)

            posStart              : Rect. position du coin superieur gauche du sprite, à l'écran.

            level                 : int. Valeur initiale du level du magicien. (ne sert pas à
                                    grand chose pour le magicien de base, mais les autres, oui)
        """
        pygame.sprite.Sprite.__init__(self)

        #init d'un tas de truc.
        self.dicMagicienImg = dicMagicienImg
        self.spriteSimpleGenerator = spriteSimpleGenerator
        self.image = dicMagicienImg[IMG_NORMAL]
        self.rect = pygame.Rect(posStart.topleft + MAGICIAN_SIZE.size)

        #définition du level. On peut pas fixer directement le level souhaité, car à priori,
        #on sait pas ce que fait la fonction levelUp. donc faut les monter un par un.
        self.resetToLevelOne()
        for _ in xrange(1, level):
            self.levelUp()

        #génération du sprite qui fait l'anim d'apparition du magicien.
        #(c'est pas géré par cette classe-ci, mais par un simpleSprite)
        #le magicien garde une référence sur le SimpleSprite de son anim d'apparition,
        #Ca lui permettra de savoir quand cet anim est terminée.
        fonc = self.spriteSimpleGenerator.generateMagAppearing
        self.spriteAppearing = fonc(posStart)

        #Au début, le magicien ne peut pas agir, il fait son anim d'apparition
        self.currentState = APPEARING

        self.lifePoint = LIFE_POINT_INIT

        #Yeaaaahh. Je trouve ça super cool de pouvoir faire ça, crac, directos !!
        #c'est un dictionnaire avec :
        # -    clé : l'identifiant de l'état du magicien
        # - valeur : la fonction update à appeler quand le magicien est dans cet état
        #
        #Je fout pas ce dico en const. Comme ça je branche vers les fonctions de l'instance de
        #classe, et non pas vers les fonctions de la classe. C'est plus logique.
        #Et si j'hérite vers une autre classe et que je change les fonctions d'update,
        #ça me pètera pas à la gueule. (D'autant plus que je le fais, cet héritage)
        self.BRANCH_UPDATE = {
            HURT      : self.updateHurt,
            DYING     : self.updateDying,
            ALIVE     : self.updateNormal,
            APPEARING : self.updateAppearing,
            BURSTING  : self.dieImmediatlyBlarg,
            #quand le magicien est DEAD, on n'est plus censé exécuter son update.
            #je branch un petit coup quand même vers une fonction à la con,
            #pour plus de robustaysse.
            DEAD      : self.dieImmediatlyBlarg,
        }

        #init d'un dico qui fait les branchements : type de mort -> fonctions à exécuter
        #Pour la même raison que ci-dessus, ce dico est créé ici, et pas en const.
        #Les valeurs de ce dico sont des tuples de 2 element :
        # - fonction qu'il faut lancer au début, lorsqu'on veut initialiser
        #   l'anim de mort correspondante du magicien.
        # - fonction à lancer à chaque cycle, pour updater l'anim de mort.
        #   on update jusqu'à ce qu'elle soit finie, et que l'objet magicien soit deleté
        #
        #Pour certaines morts, la fonction d'update est dieImmediatlyBlarg. Ca veut dire
        #qu'il n'y a plus rien à faire, et on delete le magicien tout de suite. Ce sont
        #les morts où l'animation est entièrement gérée par des SimpleSprite, qui ont
        #été générés lors de l'appel de la fonction Init.
        self.BRANCH_DYING_FUNCTION = {
            DYING_ROTATE : (self.initDyingRotate, self.dieImmediatlyBlarg),
            DYING_SHIT   : (self.initDyingShit,   self.dieImmediatlyBlarg),
            DYING_NAKED  : (self.initDyingNaked,  self.updateDyingNaked),
        }


    def isMoveFinished(self):
        """
        permet d'indiquer au code extérieur si le magicien a fini son mouvement ou pas
        """
        #on renvoie tout de suite True, car le magicien de base ne bouge pas
        return True


    def resetToLevelOne(self):
        """
        initialise/réinitialise le level à 1, et remet les caractéristiques dépendante du level
        à leur valeur initiale pourrite.
        """
        self.level = 1
        #le magicien de base n'a rien de plus à se réinitialiser


    def levelUp(self):
        """
        Fonction permettant au magicien de faire un levelUp et de monter ses caractéristiques.
        """
        self.level += 1
        #le magi de base n'a rien de plus à upper.


    def TakeStimuliTouchedHero(self):
        """
        fonction exécutée par le code extérieur, lorsque le magicien vient de toucher le héros,
        et de lui faire mal. paf !!
        """
        #Le magicien revient au niveau 1 quand il a fait mal au joueur.
        #ça permet de diminuer le risque d'une autre collision très vite,
        #à peine quelques cycles plus tard. Car ça ne serait pas très gentil pour le joueur.
        self.resetToLevelOne()


    def hitByBullet(self, Damage):
        """
        Fonction à exécuter par le code extérieur.
        La fonction permet d'indiquer au magicien qu'il s'est pris des bullets dans la gueule.

        entrées :
            Damage. int. Nombre de points de dégâts ( = nombre de bullets qui le touchent)

        plat-dessert :
            identifiant de l'état actuel du magicien, après qu'il s'est pris le bullet.
            Ca peut être HURT, ou DYING, ou BURSTING
        """

        #si le magicien se prend X bullets d'un coup, il explose direct : BURST. (X = 3)
        #on ne contrôle même pas ses points de vie restants. (Pis de toutes façons il en a que 2)
        #Il y a une anim de mourage spécifique au BURST
        if Damage >= DAMAGE_FOR_BURSTING:
            self.initBursting()
            #va renvoyer l'état BURSTING
            return self.currentState

        #on retire le nombre de points de dégâts aux points de vie du magicien.
        self.lifePoint -= Damage

        if self.lifePoint <= 0:

            #plus de points de vie, donc le magicien va crever.
            self.currentState = DYING

            #choix au hasard d'un moyen de crevage.
            dyingTypeIndex = randRange(len(LIST_DYING_TYPE))
            dyingType = LIST_DYING_TYPE[dyingTypeIndex]
            #récupération vers la fonction initialisant le moyen de mourage choisi
            dyingTypeBranching = self.BRANCH_DYING_FUNCTION[dyingType]
            funcDyingInit = dyingTypeBranching[BRANCH_DYING_INIT]
            #exécution de cette fonction
            funcDyingInit()

        else:

            #le magicien ne va pas BURST, et il a encore des points de vie.
            #Donc il a juste mal (HURT)

            #C'est une fonction séparée qui gère ce cas, car il faut pouvoir la surcharger
            #quand on fait les classes-fifilles.
            self.hitByBulletButNotDead(Damage)

        return self.currentState


    def hitByBulletButNotDead(self, Damage):
        """
        fonction définissant les actions à faire quand le magicien s'est pris
        des bullets, mais qu'il n'en est pas mort. (il est HURT)

        entrées :
            Damage. int. Nombre de points de dégâts ( = nombre de bullets qui le touchent)
        """

        #pas de diminution des points de vie. Déjà fait par la fonction appelante (hitByBullet)

        self.currentState = HURT

        #changement de l'image du sprite et application du décalage
        self.image = self.dicMagicienImg[IMG_HURT]
        self.rect.move(DECALAGE_NORM_HURT.topleft)
        #son qui fait "arh je suis un magicien et j'ai mal"
        theSoundYargler.playSound(SND_MAG_HURT)

        #pour les classes dérivées du magician : lorsqu'il est hurt, on peut
        #rajouter des trucs ici. Par exemple, l'initialisation d'un mouvement de recul
        #on peut auissi ajouter un compteur, pour que le magicien reste hurt
        #un certain temps. Quand c'est fini, on exécutera la fonction unHurt
        #(il faut gérer tout ça par rapport au code qu'on met dans la fonction updateHurt


    def updateNormal(self):
        """
        update du magicien (fonction qui se lance à chaque cycle de jeu)
        cas où le magicien est dans son état normal (ALIVE)
        """
        #ici, on peut gérer des mouvements du magicien,
        #des montées de niveau, plein d'autres trucs
        #dans cette classe de base, on ne fait rien.
        pass


    def unHurt(self):
        """
        fonction à lancer quand le magicien s'est fait HURT, et qu'il faut
        le remettre dans l'état normal
        """
        #et donc oui, on le remet dans l'état normals
        self.currentState = ALIVE

        #retour à l'image de sprite du magicien normal, et application du décalage.
        self.image = self.dicMagicienImg[IMG_NORMAL]
        self.rect.move(DECALAGE_HURT_NORM.topleft)


    def updateHurt(self):
        """
        update du magicien (fonction qui se lance à chaque cycle de jeu)
        Cas où le magicien s'est pris des dégats y'a pas longtemps (HURT)
        """
        #ici, on peut faire un mouvement, ou d'autres choses.
        #mais il faut obligatoirement exécuter unHurt au bout d'un certain nombre de cycle,
        #pour le magicien de base, on fait unHurt immédiatement. (on va au plus simple)
        self.unHurt()


    def initBursting(self):
        """
        Fonction pemettant d'initialiser l'anim
        et les SpriteSimple du magicien qui explose (BURST)
        """

        self.currentState = BURSTING

        #son : "spflark !!"
        theSoundYargler.playSound(SND_MAG_BURST)

        # --- génération des parties du corps ensanglantés qui s'envolent ---
        # chaque partie du corps est un simple sprite, générée bien comme il
        # faut par le SimpleSpriteGenerator. La position de départ des parties
        # du corps est prise à partir de la position du magicien, avec un petit
        #décalage en plus.

        #le bras droit
        armPosStartRight = self.rect.move(pyRect(10, 2).topleft)
        self.spriteSimpleGenerator.generateMagBurstArmRight(armPosStartRight)

        #le bras gauche
        armPosStartLeft = self.rect.move(pyRect(0, 2).topleft)
        self.spriteSimpleGenerator.generateMagBurstArmLeft(armPosStartLeft)

        #la tête
        headPosStart = self.rect.move(pyRect(5, -3).topleft)
        self.spriteSimpleGenerator.generateMagBurstHead(headPosStart)

        #le simple sprite de l'anim du corps en train d'exploser.
        self.spriteSimpleGenerator.generateMagBurstSplat(self.rect)


    def initDyingRotate(self):
        """
        Fonction à lancer lorsque le magicien va crever dans l'animation DYING_ROTATE.
        """

        self.currentDyingState = DYING_ROTATE

        #son : "heeuehhaauuehheuuuaarrghh !!"
        theSoundYargler.playSound(SND_MAG_DYING_ROTATE)

        #génération d'un SimpleSprite, représentant un magicien qui meurt en tournoyant
        #et en planant en une magnifique parabole qui finit dans les tréfonds du bas de l'écran.
        self.spriteSimpleGenerator.generateMagDyingRotate(self.rect)


    def initDyingShit(self):
        """
        Fonction à lancer lorsque le magicien va crever dans l'animation DYING_SHIT.
        """

        self.currentDyingState = DYING_SHIT

        #son : "heuarshblorf !!"
        theSoundYargler.playSound(SND_MAG_DYING_SHIT)

        #on génère un spriteSimple, représentant l'anim de transformation en merde.
        self.spriteSimpleGenerator.generateMagDyingShit(self.rect)


    def initDyingNaked(self):
        """
        Fonction à lancer lorsque le magicien va crever dans l'animation DYING_NAKED.

        On peut pas se contenter de génrer cette anim avec uniquement des SpriteSimple,
        car le magicien, quand il s'envole tout nu, génère des petits nuages de pets.
        Les nuages de pets sont des SpriteSimple. Mais leur génération ne peut pas
        être confiée à un SpriteSimple, car ils ne sont pas prévus pour ça.

        Donc l'objet magicien est toujours présent pendant un DYING_NAKED,
        et on le détruit lorsque l'anim est finie.
        """

        self.currentDyingState = DYING_NAKED

        #changement de l'image du sprite, et application du décalage qui va avec
        self.image = self.dicMagicienImg[IMG_DYING_NAKED]
        self.rect.move_ip(DECAL_DYING_NAKED.topleft)

        #initialisation des trucs pour le mouvement. (vers le haut, sans accel)
        #en fait y'aura une accel en X, aléatoire vers la gauche ou la droite,
        #mais on la rajoutera plus tard.
        self.moveCounter = DYIND_NAKED_MOVE_PERIOD
        self.speed = pyRect(0, -4)
        self.currentAccel = pyRect()

        #ça y'en aura besoin pour savoir quand le magicien est sorti de l'écran.
        self.image_height = self.image.get_height()

        #compteur avant le prochain pets, pour savoir quand générer un SimpleSprite de type "Fume"
        self.fartCounter = randRange(FART_PERIOD_MIN, FART_PERIOD_MAX)


    def updateDyingNaked(self):
        """
        fonction update de l'anim de mort DYING_NAKED
        """

        # --- gestion des prouts du magicien ---

        #diminution du compteur avant le prochain pets.
        self.fartCounter -= 1

        if self.fartCounter == 0:

            # il faut péter !!!
            #détermination de la position d'où générer le prout
            fartPosStart = self.rect.move(DECAL_MAGICIAN_FART.topleft)
            #génération du prout (c'est un SimpleSprite de type Fume).
            self.spriteSimpleGenerator.generateFume(fartPosStart)
            #son qui fait prout. prout !!
            theSoundYargler.playSound(SND_MAG_DYING_FART)
            #reinit du compteur de prout, pour la prochaine génération.
            self.fartCounter = randRange(FART_PERIOD_MIN, FART_PERIOD_MAX)

        # --- gestion du mouvement du magicien ---

        #diminution du compteur avant le prochain mouvement.
        self.moveCounter -= 1

        if self.moveCounter == 0:

            # il faut bouger.
            #on applique une petite accélération aléatoire sur la vitesse en X.
            #comme ça le magicien monte en zigzagouillant, ce qui est fort rigolo.
            self.speed.left = centeredRandom(2)

            #application de la vitesse sur la position
            self.rect.move_ip(self.speed.topleft)

            #quand il sort complètement de l'écran par le haut, le magicien peut être deleté.
            if self.rect.top < -self.image_height:
                self.currentState = DEAD

            #Reinit du compteur avant le prochain mouvement
            self.moveCounter = DYIND_NAKED_MOVE_PERIOD


    def dieImmediatlyBlarg(self):
        """
        fonction a exécuter quand le magicien est mort, qu'on a géré son anim de mort,
        et qu'on a plus du tout besoin de lui (l'objet de magicien peut être deleté).
        """

        #c'est le code extérieur qui s'occupe de la supression effective de l'objet magicien
        #(puisque c'est aussi lui qui s'est occupé de le créer).
        #on prévient le code extérieur qu'il faut deleter en fixant son état à DEAD.
        self.currentState = DEAD


    def updateDying(self):
        """
        Haha, ça c'est une fonction qu'elle est rigolote.
        C'est juste pour savoir quelle fonction updateDyingXXX il faut exécuter,
        en fonction du type de Dying. Mais c'est fait de manière classe et raffinée.
        """

        #on récupère la liste de fonction gérant le type de DYING actuel.
        dyingTypeBranching = self.BRANCH_DYING_FUNCTION[self.currentDyingState]
        #dans cette liste, on récupère la fonction pour l'update
        funcDyingUpdate = dyingTypeBranching[BRANCH_DYING_UPDATE]
        #exécution de cette fonction. Woot !!!
        funcDyingUpdate()


    def updateAppearing(self):
        """
        fonction update. Cas où le magicien est en train d'apparaître (APPEARING)

        Le magicien n'a pratiquement rien à faire pendant qu'il est appearing, car l'anim
        est gérée par un SimpleSprite. Le magicien se contente d'inspecter le SimpleSprite
        pour voir si il a terminé son anim ou pas.
        """

        #sécurité un peu inutile. Quand le self.spriteAppearing est devenu None, c'est forcément
        #que la fin de l'anim d'apparition a été prise en compte.
        #Donc on n'exécute plus cette fonction. Mais bon, hop, soyons fou.
        if self.spriteAppearing is not None:

            if self.spriteAppearing.currentState == SPRITE_DEAD:

                #l'anim d'apparition du magicien est terminé, donc on change son état.
                self.currentState = ALIVE

                #et on vire la référence au simpleSprite d'apparition. Y'en a plus besoin
                #car on ne l'affiche plus. (Il n'est plus dans le groupe de sprite
                #rassemblant tous les SimpleSprite)
                self.spriteAppearing = None


    def update(self):
        """
        fonction générique pour l'update du magicien.
        Celle là aussi elle est classe, comme la fonction préprécédente.
        """

        #on récupère la bonne fonction, selon l'état actuel
        funcUpdate = self.BRANCH_UPDATE[self.currentState]
        #et on l'exécute.  Tadzaaaamm !!
        funcUpdate()

