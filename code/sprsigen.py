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

date de la derni�re relecture-commentage : 21/10/2010

G�n�rateur de Sprite Simple. Utilise les classes SimpleSprite et le SimpleSpriteManager,

En fait c'est juste une classe pour stocker toutes les images et valeurs de mouvement
des SimpleSprite que j'utilise dans le jeu. C'est un "entrep�t de valeurs par d�faut".
Comment �ay trop bien comment trop comment je parle trop bien. fap fap fap fap.

surprenage de conversation de 2 nanas dans le bus :
"tu sais ce qu'elle me dit � propos des tampons ? Elle force et il sort."
C'est chouette la soci�t�.
"""

import pygame

from common import (pyRect, loadImg, centeredRandom, randRange,
                    makeRotatedImg, COLOR_BLACK)

from sprsimpl import (IMG_LOOP_ETERNAL,
                      END_ON_IMG_LOOP, END_ON_OUT_GAME_AREA,
                      END_ON_OUT_DOWN, END_NEVER,
                      DECAL_ON_CENTER)

from sprsiman import SpriteSimpleManager

# --------
#infos du SimpleSprite "Fume". (prononcer avec l'accent anglais d'Oxford : fiouume)
#Bon, en fait c'est les petits prouts du magicien DYING_NAKED.

#pr�fixe des noms des fichiers images de cette anim
FUME_IMG_FILENAME_PREFIX = "fume"

#tuple de tuple de 3 elem :
# - nom de fichier court de l'image du Sprite
# - temps (nombre de cycle) entre cette image et la suivante
# - Rect(X, Y) : d�calage � appliquer lorsqu'on affiche cette image.
#voir SpriteSimple. Ce tuple correspond � la variable listImgInfo
#Sauf qu'au lieu d'avoir les images, ici on a les noms de fichiers courts.
#(y'a un fonction qui remplace l'un par l'autre, of course)
FUME_LIST_IMG_INFO_WITH_FILENAME = (
    ("a", 10, pyRect(-1, -1)),
    ("b", 10, pyRect( 1,  1))
)

# --------
#infos du SpriteSimple "Flame". La flamme qui sort du flingue du h�ros quand il tire.

FLAME_IMG_FILENAME_PREFIX = "feu"

FLAME_LIST_IMG_INFO_WITH_FILENAME = (
    ("a", 8, pyRect(0, -8)),
    ("b", 3, pyRect(0,  4))
)

# -------
#infos du SpriteSimple "Little Shell". La petite douille noire qui tombe du flingue
#quand le h�ros r�arme.

LITTLE_SHELL_IMG_FILENAME_PREFIX = "lish"

LITTLE_SHELL_IMG_INFO_WITH_FILENAME = (
    ("hor",   3, pyRect(-1, 0)),
    ("dias",  3, pyRect( 0,-1)),
    ("ver",   3, pyRect(+1, 0)),
    ("diaa",  3, pyRect( 0,+1)),
)

# -------
#infos des SpriteSimple "MagBurst". Ce sont les morceaux de corps du magicien qui partent
#en gigotant, quand le magicien meurt en explosant (BURST)
#Y'a trois sprite MagBurst diff�rents.
(ARM_LEFT,   #le bras gauche du magicien
 ARM_RIGHT,  #le bras droit
 HEAD,       #la tayte
) = range(3)

#Pour ces sprite de MagBurst, on n'a pas le tuple IMG_INFO_WITH_FILENAME.
#Quand on veut afficher un MagBurst, on cr�e sa listImgInfo � la vol�e. (wouuh, expression classe)
#voir les fonctions buildListIndexChoice et generateMagBurst* pour plus de pr�cisions.

#pour l'instant, faut juste savoir que pour chaque sprite "MagBurst", on a besoin de charger
#deux images, puis de pr�calculer deux listes d'images rotat�es � partir de ces deux images.

#Et ensuite, ce qu'on fera c'est qu'on prendra des images dans ces deux listes, un peu
#au hasard, mais pas trop, pour cr�er un mouvement de rotation ou d'oscillation du bras/t�te.
#Il y a deux listes d'images rotat�es pour chaque membre. On prend alternativement une image
#dans une liste puis dans une autre. Le meembre n'est pas tout � fait pareil dans les deux
#listes, en particulier le sang qui en sort. Ca donne l'impression que �a gigote tout
#seul, avec les nerfs qui restent, et que le sang s'�coule. C'est tr�s rigolo.

#nombre de degr� centigrades entre deux images de MagBurst pr�calcul�es et rotat�es
STEP_ANGLE_DYING_MAG_ARM = 15

#p�riode de changement d'image des MagBurst de type "arm" (les bras coup�s du magicien)
COUNTER_IMG_DYING_MAG_ARM  = 3
#p�riode de changement d'image des MagBurst de type "head" (la t�te coup�e du magicien)
COUNTER_IMG_DYING_MAG_HEAD = 5

#pr�fixe des noms de fichier pour les deux image de MagBurst de bras droit.
#pour avoir les noms de fichiers r�els, y'a juste � rajouter "a" ou "b" derri�re.
MAGBURST_ARM_RIGHT_FILENAME_PREFIX = "mbarmr"
#pareil, mais pour les deux images du bras gauche.
MAGBURST_ARM_LEFT_FILENAME_PREFIX  = "mbarml"
#les deux images de la t�te
MAGBURST_HEAD_FILENAME_PREFIX = "mbhead"

#valeur min et max utilis�e pour le random, qui d�termine combien d'image on prend
#pour faire une anim de MagBurst. (voir les fonctions buildListIndexChoice et generateMagBurst*)
MAGBURST_ARM_LIST_IMG_LEN_MIN = 2
MAGBURST_ARM_LIST_IMG_LEN_MAX = 8

# -------
#infos du SpriteSimple "MagBurstSplat". La grosse giclure de sang quand on explose un magicien.
#(la t�te et les bras qui volent sont g�r�s par d'autres SimpleSprite)
MAGBURST_SPLAT_IMG_FILENAME_PREFIX = "mbsplat"

MAGBURST_SPLAT_IMG_INFO_WITH_FILENAME = (
    ("a", 8, pyRect(+7,+6)),
    ("b", 8, pyRect( 0,-2)),
    ("c", 8, pyRect(+5,-2)),
)

# -------
#infos du SpriteSimple MagDyingShit. L'animation du magicien qui cr�ve en se tranformant en merde.

MAGI_DYING_SHIT_IMG_FILENAME_PREFIX = "mshit"

MAGI_DYING_SHIT_LIST_IMG_INFO_WITH_FILENAME = (
 ("aa",   12, pyRect(-4,  0)),
 ("ab",    8, pyRect( 2,  3)),
 ("ba",   30, pyRect( 0,  3)),
 ("bb",    8, pyRect( 0,  0)),
 ("bc",    8, pyRect( 2,  0)),
 ("bd",    8, pyRect( 3,  0)),
)

# -------
# infos du SpriteSimple MagDyingRotate. L'animation du magicien qui cr�ve en tournoyant.

#cette anim ne poss�de pas de listImgInfo comme les autres. C'est comme pour les MagBurst,
#mais en encore plus simple. On part d'une seule image (celle du magicien dans son �tat normal),
#on pr�calcule des images rotat�es de ce magicien. Et �a sera utilis�e pour l'anim.
#voir la fin de la fonction loadAllSprSimpleImgInfo

#Nombre de degr� centigrades entre deux rotations de l'image du magicien.
#c'est un nombre negatif car on tourne dans le sens antitrigonometrique mes couilles
STEP_ANGLE_DYING_ROTATE = -10

#p�riode (nbre de cycle) entre deux changements d'image de l'anim.
PERIOD_IMG_DYING_ROTATE = 1

# -------
#infos pour le SpriteSimple MagAppearing. L'anim du magicien qui apparait

MAGI_APPEAR_IMG_FILENAME_PREFIX = "mappea"

MAGI_APPEAR_LIST_IMG_INFO_WITH_FILENAME = (
 ("01",  8, pyRect(-4, -4) ),
 ("02",  5, pyRect(+1, +2) ),
 ("03",  5, pyRect(+1,  0) ),
 ("10",  5, pyRect( 0,  0) ),
 ("11",  5, pyRect( 0,  0) ),
 ("12",  5, pyRect(+1, +1) ),
)

# -------
#infos pour le spriteSimple "Blood". Les particules de sang qui giclent quand le h�ros
#se fait Hurt, ou qu'il meurt.

#pr�fixe de nom de fichier alors que y'a qu'une seule image pour l'anim. Totally useless,
#mais c'est pas grave. On n'est pas � �a pr�s.
PARTICLE_BLOOD_IMG_FILENAME_PREFIX = "p"

PARTICLE_BLOOD_LIST_IMG_INFO_WITH_FILENAME = (
 #l� j'ai mis 1, mais en vrai, je change cette valeur en live.
 #Je cr�e un listImgInfo sp�cifique pour chaque particule de blood.
 ("blood", 1, pyRect() ),
)

# -------
#infos pour le SpriteSimple "bullettSmoke"
#C'est la petite fum�e qui apparait dans le chargeur, � gauche, quand on tire une cartouche.

BULLET_SMOKE_IMG_FILENAME_PREFIX = "bul"

BULLET_SMOKE_LIST_IMG_INFO_WITH_FILENAME = (
 ("smoka", 3, pyRect(0, -2)),
 ("smokb", 4, pyRect(5,  0)),
)

# ------- gros truc qui rassemble tout

#identifiant de tous les SpriteSimple. (Sauf les MagBurst Arm et Head qui sont g�r�s autrement)
(FUME,
 FLAME,
 LITTLE_SHELL,
 MAGBURST_SPLAT,
 MAGI_DYING_SHIT,
 MAGI_APPEAR,
 PARTICLE_BLOOD,
 MAGBURST,
 MAGI_DYING_ROT,
 BULLET_SMOKE,
) = range(10)

#dictionnaire g�ant de chargement des images utilis�es pour faire les anims,
#� ranger dans des listImgInfo
# cl� : identifiant du SpriteSimple
# valeur : tuple de 2, 3 ou 4 �l�ments (voir param de la fonction loadImgInListImgInfo
# de ce fichier. C'est les m�mes)
#           - pr�fixe pour les noms des fichiers images
#           - listImgInfo avec les noms courts des fichiers images, au lieu des images elle-m�me.
#           - couleur de transparence
#           - extension du nom du fichier
#
#Sauf qu'en vrai, j'ai jamais besoin du 4eme param. Mais je pourrais en avoir.
#
#et sinon, il y a l'expression "en lieu et place", je n'ai jamais compris son int�r�t.
#C'est un pl�onasme. Ou pas. C'est pl�onastique. C'est pl�onastique !!!!
DIC_IMG_INFO_LOAD_PARAM = {
 FUME            : (FUME_IMG_FILENAME_PREFIX,
                    FUME_LIST_IMG_INFO_WITH_FILENAME),

 FLAME           : (FLAME_IMG_FILENAME_PREFIX,
                    FLAME_LIST_IMG_INFO_WITH_FILENAME),

 #pour celui-l�, c'est oblig� de sp�cifier explicitement la couleur transparente,
 #car elle est pas en haut � gauche.
 LITTLE_SHELL    : (LITTLE_SHELL_IMG_FILENAME_PREFIX,
                    LITTLE_SHELL_IMG_INFO_WITH_FILENAME,
                    COLOR_BLACK),

 MAGBURST_SPLAT  : (MAGBURST_SPLAT_IMG_FILENAME_PREFIX,
                    MAGBURST_SPLAT_IMG_INFO_WITH_FILENAME),

 MAGI_DYING_SHIT : (MAGI_DYING_SHIT_IMG_FILENAME_PREFIX,
                    MAGI_DYING_SHIT_LIST_IMG_INFO_WITH_FILENAME),

 MAGI_APPEAR     : (MAGI_APPEAR_IMG_FILENAME_PREFIX,
                    MAGI_APPEAR_LIST_IMG_INFO_WITH_FILENAME),

 PARTICLE_BLOOD  : (PARTICLE_BLOOD_IMG_FILENAME_PREFIX,
                    PARTICLE_BLOOD_LIST_IMG_INFO_WITH_FILENAME),

 BULLET_SMOKE   : (BULLET_SMOKE_IMG_FILENAME_PREFIX,
                   BULLET_SMOKE_LIST_IMG_INFO_WITH_FILENAME),
}


def loadImgInListImgInfo(prefix, listImgInfoWithFileName,
                         colorkey = -1, extension=".png"):
    """
    permet de passer d'une LIST_IMG_INFO_WITH_FILENAME � une listImgInfo.
    on remplace le premier �l�ment de chaque sous-tuple (le nom de fichier court),
    par la Surface correspondante. En chargeant le fichier image qui va bien.

    Y'a rien de pr�vu si on veut mettre la m�me image dans deux listImgInfo.
    (faut la charger deux fois)
    Je m'en occuperais plus tard, si j'en ai besoin.

    entr�es :
      - prefix : string. Pr�fixe des noms de fichier pour les images � charger.
      - listImgInfoWithFileName : voir variable FUME_LIST_IMG_INFO_WITH_FILENAME tout l� haut.
      - colorkey : voir fonction common.loadImg
      - extension : string. extension des noms de fichier image.

    plat-dessert : la listImgInfo correspondante. Avec les images charg�es dedans.
    """

    listImgInfo = []

    for imgInfoWithFileName in listImgInfoWithFileName:

        #r�cup�ration du nom court du fichier image, � partir de l'�l�ment courant (cataclop)
        shortFileName = imgInfoWithFileName[0]
        #cr�ation du nom entier � partir du nom court
        longFileName = prefix + shortFileName + extension
        #chargementde l'image. (rien de sp�cial de pr�vu si �a fail)
        imgLoaded = loadImg(longFileName, colorkey)
        #ajout dans la listImgInfo finale,
        #en recopiant les autres infos (temps et rect de d�calage), tel quel
        imgInfo = (imgLoaded, imgInfoWithFileName[1], imgInfoWithFileName[2])
        listImgInfo.append(imgInfo)

    #tuplifiage de la liste car elle va pas bouger.
    return tuple(listImgInfo)

#et le gosse il avait gerb� dans le lavabo, et tout �a. C'�tait super. J'm'en souviens
#et moi j'ai pas pleur�. J'en avais pas besoin.

def loadAllSprSimpleImgInfo(imgMagiNormal):
    """
    charge toutes les images n�cessaires � toutes les animations de Sprite.
    Y'a toute les listImgInfo, et toutes les listes d'images rotat�es.

    entr�es :
        imgMagiNormal : image du magicien quand il est dans son �tat normal.
                        Y'en a besoin pour faire l'anim de DYING_ROTATE.

    plat-dessert :
        gigantesque dictionnaire.
         - cl� : identifiant du SpriteSimple
         - listImgInfo, ou bien, dans le cas du MagBurst :
           sous-dictionnaire avec le type de membre comme cl�, et un tuple de 2 �l�ments
           contenant les listes d'images rotat�es. Oui c'est le bordel. Ben oui.
    """

    dicImgInfoSpriteSimple = {}

    # --- chargement de toutes les listImgInfo des SpriteSimple ---

    #(sauf les MagBurst, et le Mag_Dying_Rotate

    for keyImgInfo, paramLoad in DIC_IMG_INFO_LOAD_PARAM.items():

        dicImgInfoSpriteSimple[keyImgInfo] = loadImgInListImgInfo(*paramLoad)

    # --- chargement de la liste d'images rotat�e pour l'anim de MagDyingRotate ---

    #cr�ation du tuple contenant les images rotat�e de l'image du magicien normal.
    rotatImgMagDying = makeRotatedImg(imgMagiNormal, STEP_ANGLE_DYING_ROTATE)

    #cr�ation d'une listImgInfo avec ces images rotat�es, une p�riode de temps fixe
    #entre 2 images, et jamais de d�calage de hotPoint entre les images
    #(on g�rera les d�calages par rapport aux centres des imagse
    imgInfoMagDyingRot = [ (elem, PERIOD_IMG_DYING_ROTATE, pyRect())
                           for elem in rotatImgMagDying ]

    #rangement de cette listImgInfo dans le grand dictionnaire de toutes les listImgInfo
    dicImgInfoSpriteSimple[MAGI_DYING_ROT] = imgInfoMagDyingRot

    # --- chargement des listes d'images rotat�es des MagBurst ---

    # on placera ces listes dans le dico dicImgInfoSpriteSimple, avec la cl� MAGBURST
    # la valeur qu'on placera sera un sous-dictionnaire, avec plein de choses dedans,
    # voir juste apr�s.

    rotatImgMagBurst = {}

    #tuple de tuple de 4 elements :
    # - identifiant de la partie du corps du magicien qui sbleuark quand il burst
    # - pr�fixe des noms de fichiers images de cette partie du corps
    # - angle de rotation pour faire les diff�rentes images rotat�es
    # - tuple contenant les noms de fichiers courts (sans pr�fixe) des images
    listConfigRotatImg = (

        (ARM_RIGHT, MAGBURST_ARM_RIGHT_FILENAME_PREFIX,
         STEP_ANGLE_DYING_MAG_ARM, ("a", "b")),

        (ARM_LEFT,  MAGBURST_ARM_LEFT_FILENAME_PREFIX,
         STEP_ANGLE_DYING_MAG_ARM,  ("a", "b")),

        #j'ai mis un "moins" pour les angles de rotations. Comme �a, les images rotat�es
        #de la t�te seront rang�s dans le sens anti-trigo. Et c'est plus naturel que la
        #t�te tourne dans ce sens, vu qu'on d�gomme le magicien par le c�t� gauche.
        (HEAD,      MAGBURST_HEAD_FILENAME_PREFIX,
         -STEP_ANGLE_DYING_MAG_ARM,  ("a", "b")),

    )

    #le but, c'est d'alimenter le sous-dictionnaire contenu dans dicImgInfoSpriteSimple[MAGBURST],
    #avec :
    # - cl� : identifiant de la partie du corps (elem 0 du tuple ci-dessus)
    # - valeur : une liste, de deux �l�ments, correspondant respectivement
    #            aux fichiers images "a" et "b".
    #             - contenu de chaque �l�ment : la liste des images rotat�es de la partie du corps
    #               en question. Ouf, il �tait temps !!

    for confRotImg in listConfigRotatImg:

        #r�cup des infos contenues dans l'�l�ment du tuple de tuple
        idMagPart, prefixFNameImg, stepAngle, listShortFName = confRotImg

        #listRotatImgMagBurstTemp signifie "list rotated image magician bursting - Temporary"
        #et si �a vous fait chier mes noms � rallonge, allez vous faire voir ok ?
        listRotatImgMagBurstTemp = []

        for shortFName in listShortFName:
            #chargement de l'image de la partie du corps qu'on doit faire rotater.
            imgMagPart = loadImg(prefixFNameImg + shortFName + ".png")
            #cr�ation d'une liste d'image rotat�e � partir de cette image
            listRotatImg = makeRotatedImg(imgMagPart, stepAngle)
            #ajout dans la liste de deux �l�ments des images rotat�es.
            listRotatImgMagBurstTemp.append(listRotatImg)

        #dictionnaire de tuple(2) de tuple(n) de Surface rotatay. faites pas chiay
        rotatImgMagBurst[idMagPart] = tuple(listRotatImgMagBurstTemp)

    #ajout du sous-dictionnaire dans le gros dictionnaire total. A la cl� MAGBURST.
    dicImgInfoSpriteSimple[MAGBURST] = rotatImgMagBurst

    return dicImgInfoSpriteSimple



class SpriteSimpleGenerator():

    def __init__(self, spriteSimpleManager, dicImgInfoSpriteSimple):
        """
        constructeur (thx cap obvious)

        entr�es :
          spriteSimpleManager : classe SpriteSimpleManager, dans laquelle
                                on ajoutera les sprites g�n�r�s.
          dicImgInfoSpriteSimple : gros dictionnaire contenant un gros tas d'imgInfo
                                   au fait, �a devrait s'appeler des animInfo, et pas imgInfo
                                   trop tard...
        """

        self.spriteSimpleManager = spriteSimpleManager
        #je met pas le m�me nom, c'est pour en avoir un plus court.
        #parce que je m'en sers partout de ce truc et apr�s c'est le bordel.
        self.dicAll = dicImgInfoSpriteSimple

    #Info applicable � toutes les fonctions generateXXXX contenues dans cette classe :
    #Ces fonctions permettent de g�n�rer un SpriteSimple et de le refiler au SpriteSimpleManager,
    #qui s'occupera de les faire �voluer, updater, et les supprimera quand ce sera n�cessaire.
    #
    #param qu'on retrouvera tout le temps :
    #entr�es : posStart. Rect. position de d�part du sprite.
    #plat-dessert :
    #        le SpriteSimple, avec toute la config qui va bien dedans.
    #        (Ce SpriteSimple est envoy� au spriteSimpleManager, pour qu'il puisse
    #         s'en occuper. Cela va de soit)


    def generateFume(self, posStart):
        """
        G�n�ration d'un sprite "Fioume". Un pet de magicien.
        """

        #Le sprite Fume contient deux petites images de fum�e, qui d�filent une fois.
        #Il bouge un peu vers le bas, et un peu � gauche ou � droite. Mais pas trop.
        #la direction exacte du mouvement est un peu randomiz�e.
        #il n'y a pas d'acc�l�ration.
        paramSprite = (self.dicAll[FUME], posStart, 1, END_ON_IMG_LOOP,
                       pyRect(centeredRandom(2), randRange(1, 5)), 5)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateFlame(self, posStart):
        """
        G�n�ration d'un sprite Flame. Le coup de feu du flingue du h�ros.
        """

        #Le sprite Flame contient deux images de flamme, qui d�filent une fois.
        #pas de mouvement ni d'acc�l�ration.
        paramSprite = (self.dicAll[FLAME], posStart, 1, END_ON_IMG_LOOP)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateLittleShell(self, posStart):
        """
        g�n�ration d'un sprite LittleShell. La douille qui sort du fusil du h�ros.
        """

        #la LittleShell contient 4 images d'une shell qui tournoie. Le mouvement est vers
        #la gauche, et vers le haut ou le bas. L'acc�l�ration est vers le bas.
        #la LittleShell est d�truite quand elle quitte l'aire de jeu, ou quand elle
        #a fait 50 anims.
        paramSprite = (self.dicAll[LITTLE_SHELL], posStart, 50,
                       END_ON_IMG_LOOP | END_ON_OUT_GAME_AREA,
                       pyRect(randRange(-6, 0), randRange(-3, 2)), 2,
                       pyRect(0, randRange(1, 3)), 4)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateMagBurstSplat(self, posStart):
        """
        g�n�ration de la grosse tache de sang lorsqu'un magicien explose
        """

        #sprite statique, dont l'anim ne s'ex�cute qu'une fois
        paramSprite = (self.dicAll[MAGBURST_SPLAT], posStart,
                       1, END_ON_IMG_LOOP)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateMagDyingShit(self, posStart):
        """
        g�n�ration de la transformation du magicien en merde, qui se d�liquesce ensuite.
        """

        #sprite statique, dont l'anim ne s'ex�cute qu'une fois
        paramSprite = (self.dicAll[MAGI_DYING_SHIT], posStart,
                       1, END_ON_IMG_LOOP)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateMagDyingRotate(self, posStart):
        """
        g�n�ration du sprite du magicien qui meurt en tournoyant.
        """

        #le sprite part vers la droite et vers le haut.
        #il y a une acc�l�ration vers le bas. Le sprite est d�truit quand il
        #arrive en bas de l'aire de jeu.
        paramSprite = (self.dicAll[MAGI_DYING_ROT], posStart,
                       IMG_LOOP_ETERNAL, END_ON_OUT_DOWN,
                       pyRect(randRange(2, 7), randRange(-15, -8)), 2,
                       pyRect(0, 1), 2,
                       DECAL_ON_CENTER)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateMagAppearing(self, posStart):
        """
        g�n�ration du sprite du magicien qui appara�t.
        Au d�but, il a un peu une forme de bite. Et apr�s �a devient le magicien.
        Ca se voit pas trop, mais lol quand m�me.
        """

        #sprite statique, dont l'anim ne s'ex�cute qu'une fois
        paramSprite = (self.dicAll[MAGI_APPEAR], posStart, 1, END_ON_IMG_LOOP)
        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateBulletSmoke(self, posStart):
        """
        G�n�ration de la fum�e dans le chargeur de cartouche, quand le h�ros tire un coup de feu.
        """

        #Le sprite BulletSmoke contient deux images de flamme, qui d�filent une fois.
        #pas de mouvement ni d'acc�l�ration.
        paramSprite = (self.dicAll[BULLET_SMOKE], posStart, 1,END_ON_IMG_LOOP)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateSomeBlood(self, posStart, nbrBlood):
        """
        g�n�ration de plusieurs sprite de taches de sang. Pour faire une giclure. spluirk !

        chaque tache de sang est un sprite avec une seule image. Le sprite est d�truit
        si il sort de l'aire de jeu ou si son anim est finie. Mais le temps d'anim
        n'est pas le m�me pour chaque sprite.

        entr�es : nbrBlood. int. nombre de taches de sang � g�n�rer.

        plat-dessert : contrairement au aux autres fonctions generateXXXX, celle-ci
                       ne renvoie que d'alle. Et osef.
        """

        #youpiii !! boucle avec un compteur qui sert � rien. J'adore �a !
        for _ in xrange(nbrBlood):

            #temps (nbre de cycles) pour ce sprite
            timeBlood = 30 + centeredRandom(30)
            #mouvement initial vers le haut ou le bas, et vers la gauche ou la droite. (c la f�te)
            moveRect = pyRect(centeredRandom(3), randRange(-4, 2))
            moveCycle = randRange(2, 4)
            #acc�l�ration vers le bas. un peu ou pas beaucoup.
            accelRect = pyRect(0, randRange(1, 2))
            accelCycle = randRange(3, 6)

            #on r�cup�re le seul �l�ment de la listImgInfo, contenant la seule image de l'anim.
            #et on en fait une copie.
            imgInfoBloodUnique = list(self.dicAll[PARTICLE_BLOOD][0])
            #on change la p�riode de temps de cette seule image. Pour mettre le temps
            #qu'on a choisi un peu plus haut.
            imgInfoBloodUnique[1] = timeBlood
            #tuplifiage de cet �l�ment unique, et rangement de cet �l�ment dans un "sur-tuple"
            #comme �a, on a une nouvelle listImgInfo (m�me si c'est une liste avec qu'un seul
            #element dedans)
            listImgInfo = ( tuple(imgInfoBloodUnique), )

            #cr�ation du sprite avec cette listImgInfo, et les params de move et d'acccel
            #calcul�s plus haut.
            #le sprite devra se terminer quand l'anim sera termin�e. Et celle-ci n'est ex�cut�e
            #qu'une seule fois. (Mais le temps de l'anim est variable, cc'est �a qu'est cool)
            paramSpr = (listImgInfo, posStart, 1,
                        END_ON_IMG_LOOP | END_ON_OUT_GAME_AREA,
                        moveRect, moveCycle, accelRect, accelCycle)

            self.spriteSimpleManager.addSpriteSimple(*paramSpr)


    def buildListIndexChoice(self, lenBaseList,
                             lenListIndexChoiceMin, lenListIndexChoiceMax):
        """
        fonction qui pourrait + ou - �tre mise dans le common. Mais pas forc�ment.
        Donc pour l'instant elle est l�.

        fabrique une liste de tuple de 2 �l�ments int
         - le 1er elem c'est une alternance de O et de 1.
         - Le 2eme c'est une suite de chiffre qui monte et descend, sur une certaine
           quantit� de valeur choisie au hasard. Cette suite de chiffre est born�e
           entre 0 et une autre valeur. Si on d�passe la borne, �a fait le tour et
           �a revient � 0

        A quoi �a sert ? A fabriquer une liste d'index pointant sur une liste d'images rotat�es
        Comme la suite de chiffre monte puis descend, �a va faire une rotation d'oscillation
        (Ca tourne un peu dans un sens, puis dans l'autre, etc.)
        Et le 1er element (0 / 1), c'est pour pouvoir piocher alternativement dans une suite
        d'image rotat�e ou dans une autre.
        Ca sert pour les MagBurst Arm (droit ou gauche), pour lesquels on a, � chaque fois,
        2 listes rotat�es de 2 sprites un peu diff�rent.

        entr�es :
            lenBaseList : int. nombre d'�l�ment des 2 listes rotat�es.
                          Ca d�finit la borne sup�rieur pour les valeurs du 2eme elem

            lenListIndexChoiceMin,
            lenListIndexChoiceMax : int et int. Valeurs min et max pour la d�termination
                                    en random de la longueur de la suite de chiffre.
                                    (la demi-longueur, en fait, car �a monte puis descend)

        plat-dessert :
            la liste de tuple de 2 elements, comme expliqu� plus haut.
            (j'avais envie de l'expliquer plus haut. Na !!

        ex : lenBaseList = 10
             (lenListIndexChoiceMin, lenListIndexChoiceMax) = (3, 8)
             le random doit choisir un d�part entre 0 et 10 -> 7
             le random doit choisir une demi-longueur entre 3 et 8 -> 5
             donc on fera monter-descendre � partir de 7, sur 5 valeurs.
             C'est � dire de 7 � 11.
             liste qui monte et descend: 7, 8, 9, 10, 11, 10, 9, 8
             (les valeurs min et max ne sont pas r�p�t�es dans le montage-descendage)
             bornage dans lenBaseList : 7, 8, 9, 0, 1, 0, 9, 8
             ajout du 0 / 1. (le random choisit si on commence � 1 ou 0)
             (7, 0), (8, 1), (9, 0), (0, 1), (1, 0), (0, 1), (9, 0), (8, 1)

        je suis un peu con, j'aurais peut-�tre du d�composer �a en 2 fonctions. boah osef.
        """

        #on d�termine, totalement au hasard, l'index de d�part dans la liste
        #des images rotat�es.
        startIndexChoice = randRange(lenBaseList)

        #on d�termine un peu au hasard, mais entre les val min et max, la demi-longueur
        #de la liste d'index d'images rotat�es qui va monter et descendre.
        lenIndexChoice = randRange(lenListIndexChoiceMin,lenListIndexChoiceMax)

        #index de fin. Pour l'instant, il n'est pas born�e entre 0 et lenBaseList.
        #On le fera plus tard.
        endIndexChoice = startIndexChoice + lenIndexChoice

        #cr�ation de la 1�re demi-liste. (Les index montent, de start jusqu'� end)
        listIndexFirstHalf = range(startIndexChoice, endIndexChoice)

        #cr�ation de la 2eme demi-liste. (les index redescendent).

        #on commence par prendre la 1ere demi-liste, sans l'index de d�but ni celui de fin,
        #(cette instruction ne plante pas si la demi-liste de d�part n'a que 0 ou 1 elem.
        #on se chope juste une liste vide qui ne sert � rien)
        listIndexSecondHalf = listIndexFirstHalf[1:-1]

        #on inverse cette liste, pour avoir les index qui descendent.
        listIndexSecondHalf.reverse()
        #collage des deux demi-listes.
        listIndex = listIndexFirstHalf + listIndexSecondHalf

        #choix entre 0 ou 1. Pour que l'alternance 0/1 commence par une valeur au hasard.
        choiceImg = randRange(2)

        #construction finale de la liste des tuples.
        listIndexAndChoice = [ (
                                   #1er elem. Le "& 1" permet de faire l'alternance.
                                   #� partir de l�, il suffit de faire compter de 1 en 1,
                                   #en partant de n'importe quelle valeur, osef.
                                   #(et on a ajout� le choiceImg pour avoir le hasard)
                                   (elem + choiceImg) & 1,
                                   #2eme elem. On lui met un modulo. Pour qu'il
                                   #reste dans la liste des images rotat�es.
                                   elem % lenBaseList)
                               #on compte dans la liste pr�c�demment calcul�e, qui monte-descend
                               for elem in listIndex
                             ]

        return tuple(listIndexAndChoice)


    def generateMagBurstArm(self, posStart, idMagArm, rectMove, rectAccel):
        """
        construit un SpriteSimple de type MagBurst, de type-type "bras coup� qui vole"

        entr�es :
            posStart  : rect(X, Y). position initiale
            idMagArm  : choix du bras. ARM_RIGHT ou ARM_LEFT
            rectMove  : rect(X,Y). mouvement initial
            rectAccel : rect(X,Y). acc�l�ration

        la p�riode de mouvement c'est 2. La p�riode d'acc�l�ration c'est 4. Y'a pas le choix.
        J'ai d�cid� de les d�finir dans cette fonction, car c'est les m�mes quel que soit
        le type de bras (gauche ou droit)
        """

        #r�f�rence vers les 2 listes de sprites rotat�s correspondant au bras coup� choisi
        listRotatedImgArm = self.dicAll[MAGBURST][idMagArm]

        #recup du nombre d'image dans les listes rotat�es. (C'est le m�me nombre
        #dans les deux listes, on aurait pu foutre [1] �a aurait fait pareil.
        nbrImgRotated = len(listRotatedImgArm[0])

        #cr�ation � peu pr�s random de la liste des index des images rotat�es
        #les index vont pointer vers des images dans les 2 listes (voir fonc buildListIndexChoice)
        param = (nbrImgRotated,
                 MAGBURST_ARM_LIST_IMG_LEN_MIN, MAGBURST_ARM_LIST_IMG_LEN_MAX)

        listImgIndexAndChoice = self.buildListIndexChoice(*param)

        #construction de la liste des images pour l'anim. En utilisant la liste d'index
        #cr��es pr�c�demment.
        #Le temps entre 2 img est le m�me.
        #Pas de d�calage entre 2 img (on le g�rera avec un d�calage par rapport aux centres)
        listImgInfo = [ (listRotatedImgArm[elem[0]][elem[1]],
                         COUNTER_IMG_DYING_MAG_ARM,
                         pyRect()
                        ) for elem in listImgIndexAndChoice
                      ]

        #cr�ation du SpriteSimple, avec la liste d'images, et les pos, move et accel
        #indiqu�s en param�tre. on indique le d�calage par rapport aux centres (DECAL_ON_CENTER).
        #le sprite sera d�truit quand il arivera en bas de l'�cran.
        paramSprit = (listImgInfo, posStart, IMG_LOOP_ETERNAL,
                      END_ON_OUT_DOWN,
                      rectMove, 2, rectAccel, 4,
                      DECAL_ON_CENTER)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprit)


    def generateMagBurstArmRight(self, posStart):
        """
        cr�e un SpriteSimple de type MagBurst, de type-type "bras coup� qui vole",
        de type-type-type "bras droit"
        """

        #random sur move et accel. Mouvement en cloche, qui part vers la droite.
        rectMove = pyRect(randRange(2, 7), randRange(-9, -4))
        rectAccel = pyRect(0, randRange(1, 3))

        return self.generateMagBurstArm(posStart, ARM_RIGHT,
                                        rectMove, rectAccel)


    def generateMagBurstArmLeft(self, posStart):
        """
        cr�e un SpriteSimple de type MagBurst, de type-type "bras coup� qui vole",
        de type-type-type "bras gauche"
        """

        #random sur move et accel. Mouvement en cloche, qui part vers la droite, mais pas trop.
        rectMove = pyRect(randRange(1, 4), randRange(-6, -3))
        rectAccel = pyRect(0, randRange(1, 3))

        return self.generateMagBurstArm(posStart, ARM_LEFT,
                                        rectMove, rectAccel)


    def generateMagBurstHead(self, posStart):
        """
        cr�e un SpriteSimple de type MagBurst, de type-type "t�te coup�e qui vole"
        """

        #La t�te coup�e tourne dans les airs. C'est pas un mouvement de rotation
        #oscillatoire comme les bras coup�s. Du coup  c'est plus simple � faire.
        #On prend tout le temps toute la liste d'image rotat�es. Le seul choix random
        #que y'a � faire, c'est l'alternance entre les 2 listes d'images.

        #r�f�rence vers les 2 listes de sprites rotat�s correspondant � la t�te coup�e
        listRotatedImgArm = self.dicAll[MAGBURST][HEAD]

        #recup du nombre d'image dans les listes rotat�es. (C'est le m�me nombre
        #dans les deux listes, on aurait pu foutre [1] �a aurait fait pareil.
        nbrImg = len(self.dicAll[MAGBURST][HEAD][0])

        #choix entre 0 ou 1. Pour que l'alternance 0/1 permettant de choisir entre l'une
        #ou l'autre des listes rotat�es soit au hasard.
        choiceImg = randRange(2)

        #construction de la liste des index vers les images rotat�es.
        #On prend toute la liste, et � chaque element, on ajoute une valeur 0/1
        listImgIndexAndChoice = [ ( (elem + choiceImg) & 1, elem )
                                  for elem in xrange(nbrImg)
                                ]

        #construction de la liste des images pour l'anim. En utilisant la liste d'index
        #cr��es pr�c�demment.
        #Le temps entre 2 img est le m�me.
        #Pas de d�calage entre 2 img (on le g�rera avec un d�calage par rapport aux centres)
        listImgInfo = [ (self.dicAll[MAGBURST][HEAD][elem[0]][elem[1]],
                         COUNTER_IMG_DYING_MAG_HEAD,
                         pyRect()
                        ) for elem in listImgIndexAndChoice
                      ]

        #cr�ation du SpriteSimple. Mouvement en cloche, qui part vers la droite, ou pas,
        #et qui vole vers le haut bien plus que les bras. (Comme �a c'est rigolo, la t�te
        #elle peut faire une grande-grande courbe dans l'air. Youpi !!!)
        paramSprite = (listImgInfo, posStart, IMG_LOOP_ETERNAL,
                       END_ON_OUT_DOWN,
                       pyRect(randRange(0, 5), randRange(-12, -6)), 2,
                       pyRect(0, randRange(1, 3)), 4,
                       DECAL_ON_CENTER)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)

