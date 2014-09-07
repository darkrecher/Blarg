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

date de la dernière relecture-commentage : 21/10/2010

Générateur de Sprite Simple. Utilise les classes SimpleSprite et le SimpleSpriteManager,

En fait c'est juste une classe pour stocker toutes les images et valeurs de mouvement
des SimpleSprite que j'utilise dans le jeu. C'est un "entrepôt de valeurs par défaut".
Comment çay trop bien comment trop comment je parle trop bien. fap fap fap fap.

surprenage de conversation de 2 nanas dans le bus :
"tu sais ce qu'elle me dit à propos des tampons ? Elle force et il sort."
C'est chouette la société.
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

#préfixe des noms des fichiers images de cette anim
FUME_IMG_FILENAME_PREFIX = "fume"

#tuple de tuple de 3 elem :
# - nom de fichier court de l'image du Sprite
# - temps (nombre de cycle) entre cette image et la suivante
# - Rect(X, Y) : décalage à appliquer lorsqu'on affiche cette image.
#voir SpriteSimple. Ce tuple correspond à la variable listImgInfo
#Sauf qu'au lieu d'avoir les images, ici on a les noms de fichiers courts.
#(y'a un fonction qui remplace l'un par l'autre, of course)
FUME_LIST_IMG_INFO_WITH_FILENAME = (
    ("a", 10, pyRect(-1, -1)),
    ("b", 10, pyRect( 1,  1))
)

# --------
#infos du SpriteSimple "Flame". La flamme qui sort du flingue du héros quand il tire.

FLAME_IMG_FILENAME_PREFIX = "feu"

FLAME_LIST_IMG_INFO_WITH_FILENAME = (
    ("a", 8, pyRect(0, -8)),
    ("b", 3, pyRect(0,  4))
)

# -------
#infos du SpriteSimple "Little Shell". La petite douille noire qui tombe du flingue
#quand le héros réarme.

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
#Y'a trois sprite MagBurst différents.
(ARM_LEFT,   #le bras gauche du magicien
 ARM_RIGHT,  #le bras droit
 HEAD,       #la tayte
) = range(3)

#Pour ces sprite de MagBurst, on n'a pas le tuple IMG_INFO_WITH_FILENAME.
#Quand on veut afficher un MagBurst, on crée sa listImgInfo à la volée. (wouuh, expression classe)
#voir les fonctions buildListIndexChoice et generateMagBurst* pour plus de précisions.

#pour l'instant, faut juste savoir que pour chaque sprite "MagBurst", on a besoin de charger
#deux images, puis de précalculer deux listes d'images rotatées à partir de ces deux images.

#Et ensuite, ce qu'on fera c'est qu'on prendra des images dans ces deux listes, un peu
#au hasard, mais pas trop, pour créer un mouvement de rotation ou d'oscillation du bras/tête.
#Il y a deux listes d'images rotatées pour chaque membre. On prend alternativement une image
#dans une liste puis dans une autre. Le meembre n'est pas tout à fait pareil dans les deux
#listes, en particulier le sang qui en sort. Ca donne l'impression que ça gigote tout
#seul, avec les nerfs qui restent, et que le sang s'écoule. C'est très rigolo.

#nombre de degré centigrades entre deux images de MagBurst précalculées et rotatées
STEP_ANGLE_DYING_MAG_ARM = 15

#période de changement d'image des MagBurst de type "arm" (les bras coupés du magicien)
COUNTER_IMG_DYING_MAG_ARM  = 3
#période de changement d'image des MagBurst de type "head" (la tête coupée du magicien)
COUNTER_IMG_DYING_MAG_HEAD = 5

#préfixe des noms de fichier pour les deux image de MagBurst de bras droit.
#pour avoir les noms de fichiers réels, y'a juste à rajouter "a" ou "b" derrière.
MAGBURST_ARM_RIGHT_FILENAME_PREFIX = "mbarmr"
#pareil, mais pour les deux images du bras gauche.
MAGBURST_ARM_LEFT_FILENAME_PREFIX  = "mbarml"
#les deux images de la tête
MAGBURST_HEAD_FILENAME_PREFIX = "mbhead"

#valeur min et max utilisée pour le random, qui détermine combien d'image on prend
#pour faire une anim de MagBurst. (voir les fonctions buildListIndexChoice et generateMagBurst*)
MAGBURST_ARM_LIST_IMG_LEN_MIN = 2
MAGBURST_ARM_LIST_IMG_LEN_MAX = 8

# -------
#infos du SpriteSimple "MagBurstSplat". La grosse giclure de sang quand on explose un magicien.
#(la tête et les bras qui volent sont gérés par d'autres SimpleSprite)
MAGBURST_SPLAT_IMG_FILENAME_PREFIX = "mbsplat"

MAGBURST_SPLAT_IMG_INFO_WITH_FILENAME = (
    ("a", 8, pyRect(+7,+6)),
    ("b", 8, pyRect( 0,-2)),
    ("c", 8, pyRect(+5,-2)),
)

# -------
#infos du SpriteSimple MagDyingShit. L'animation du magicien qui crève en se tranformant en merde.

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
# infos du SpriteSimple MagDyingRotate. L'animation du magicien qui crève en tournoyant.

#cette anim ne possède pas de listImgInfo comme les autres. C'est comme pour les MagBurst,
#mais en encore plus simple. On part d'une seule image (celle du magicien dans son état normal),
#on précalcule des images rotatées de ce magicien. Et ça sera utilisée pour l'anim.
#voir la fin de la fonction loadAllSprSimpleImgInfo

#Nombre de degré centigrades entre deux rotations de l'image du magicien.
#c'est un nombre negatif car on tourne dans le sens antitrigonometrique mes couilles
STEP_ANGLE_DYING_ROTATE = -10

#période (nbre de cycle) entre deux changements d'image de l'anim.
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
#infos pour le spriteSimple "Blood". Les particules de sang qui giclent quand le héros
#se fait Hurt, ou qu'il meurt.

#préfixe de nom de fichier alors que y'a qu'une seule image pour l'anim. Totally useless,
#mais c'est pas grave. On n'est pas à ça près.
PARTICLE_BLOOD_IMG_FILENAME_PREFIX = "p"

PARTICLE_BLOOD_LIST_IMG_INFO_WITH_FILENAME = (
 #là j'ai mis 1, mais en vrai, je change cette valeur en live.
 #Je crée un listImgInfo spécifique pour chaque particule de blood.
 ("blood", 1, pyRect() ),
)

# -------
#infos pour le SpriteSimple "bullettSmoke"
#C'est la petite fumée qui apparait dans le chargeur, à gauche, quand on tire une cartouche.

BULLET_SMOKE_IMG_FILENAME_PREFIX = "bul"

BULLET_SMOKE_LIST_IMG_INFO_WITH_FILENAME = (
 ("smoka", 3, pyRect(0, -2)),
 ("smokb", 4, pyRect(5,  0)),
)

# ------- gros truc qui rassemble tout

#identifiant de tous les SpriteSimple. (Sauf les MagBurst Arm et Head qui sont gérés autrement)
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

#dictionnaire géant de chargement des images utilisées pour faire les anims,
#à ranger dans des listImgInfo
# clé : identifiant du SpriteSimple
# valeur : tuple de 2, 3 ou 4 éléments (voir param de la fonction loadImgInListImgInfo
# de ce fichier. C'est les mêmes)
#           - préfixe pour les noms des fichiers images
#           - listImgInfo avec les noms courts des fichiers images, au lieu des images elle-même.
#           - couleur de transparence
#           - extension du nom du fichier
#
#Sauf qu'en vrai, j'ai jamais besoin du 4eme param. Mais je pourrais en avoir.
#
#et sinon, il y a l'expression "en lieu et place", je n'ai jamais compris son intérêt.
#C'est un pléonasme. Ou pas. C'est pléonastique. C'est pléonastique !!!!
DIC_IMG_INFO_LOAD_PARAM = {
 FUME            : (FUME_IMG_FILENAME_PREFIX,
                    FUME_LIST_IMG_INFO_WITH_FILENAME),

 FLAME           : (FLAME_IMG_FILENAME_PREFIX,
                    FLAME_LIST_IMG_INFO_WITH_FILENAME),

 #pour celui-là, c'est obligé de spécifier explicitement la couleur transparente,
 #car elle est pas en haut à gauche.
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
    permet de passer d'une LIST_IMG_INFO_WITH_FILENAME à une listImgInfo.
    on remplace le premier élément de chaque sous-tuple (le nom de fichier court),
    par la Surface correspondante. En chargeant le fichier image qui va bien.

    Y'a rien de prévu si on veut mettre la même image dans deux listImgInfo.
    (faut la charger deux fois)
    Je m'en occuperais plus tard, si j'en ai besoin.

    entrées :
      - prefix : string. Préfixe des noms de fichier pour les images à charger.
      - listImgInfoWithFileName : voir variable FUME_LIST_IMG_INFO_WITH_FILENAME tout là haut.
      - colorkey : voir fonction common.loadImg
      - extension : string. extension des noms de fichier image.

    plat-dessert : la listImgInfo correspondante. Avec les images chargées dedans.
    """

    listImgInfo = []

    for imgInfoWithFileName in listImgInfoWithFileName:

        #récupération du nom court du fichier image, à partir de l'élément courant (cataclop)
        shortFileName = imgInfoWithFileName[0]
        #création du nom entier à partir du nom court
        longFileName = prefix + shortFileName + extension
        #chargementde l'image. (rien de spécial de prévu si ça fail)
        imgLoaded = loadImg(longFileName, colorkey)
        #ajout dans la listImgInfo finale,
        #en recopiant les autres infos (temps et rect de décalage), tel quel
        imgInfo = (imgLoaded, imgInfoWithFileName[1], imgInfoWithFileName[2])
        listImgInfo.append(imgInfo)

    #tuplifiage de la liste car elle va pas bouger.
    return tuple(listImgInfo)

#et le gosse il avait gerbé dans le lavabo, et tout ça. C'était super. J'm'en souviens
#et moi j'ai pas pleuré. J'en avais pas besoin.

def loadAllSprSimpleImgInfo(imgMagiNormal):
    """
    charge toutes les images nécessaires à toutes les animations de Sprite.
    Y'a toute les listImgInfo, et toutes les listes d'images rotatées.

    entrées :
        imgMagiNormal : image du magicien quand il est dans son état normal.
                        Y'en a besoin pour faire l'anim de DYING_ROTATE.

    plat-dessert :
        gigantesque dictionnaire.
         - clé : identifiant du SpriteSimple
         - listImgInfo, ou bien, dans le cas du MagBurst :
           sous-dictionnaire avec le type de membre comme clé, et un tuple de 2 éléments
           contenant les listes d'images rotatées. Oui c'est le bordel. Ben oui.
    """

    dicImgInfoSpriteSimple = {}

    # --- chargement de toutes les listImgInfo des SpriteSimple ---

    #(sauf les MagBurst, et le Mag_Dying_Rotate

    for keyImgInfo, paramLoad in DIC_IMG_INFO_LOAD_PARAM.items():

        dicImgInfoSpriteSimple[keyImgInfo] = loadImgInListImgInfo(*paramLoad)

    # --- chargement de la liste d'images rotatée pour l'anim de MagDyingRotate ---

    #création du tuple contenant les images rotatée de l'image du magicien normal.
    rotatImgMagDying = makeRotatedImg(imgMagiNormal, STEP_ANGLE_DYING_ROTATE)

    #création d'une listImgInfo avec ces images rotatées, une période de temps fixe
    #entre 2 images, et jamais de décalage de hotPoint entre les images
    #(on gérera les décalages par rapport aux centres des imagse
    imgInfoMagDyingRot = [ (elem, PERIOD_IMG_DYING_ROTATE, pyRect())
                           for elem in rotatImgMagDying ]

    #rangement de cette listImgInfo dans le grand dictionnaire de toutes les listImgInfo
    dicImgInfoSpriteSimple[MAGI_DYING_ROT] = imgInfoMagDyingRot

    # --- chargement des listes d'images rotatées des MagBurst ---

    # on placera ces listes dans le dico dicImgInfoSpriteSimple, avec la clé MAGBURST
    # la valeur qu'on placera sera un sous-dictionnaire, avec plein de choses dedans,
    # voir juste après.

    rotatImgMagBurst = {}

    #tuple de tuple de 4 elements :
    # - identifiant de la partie du corps du magicien qui sbleuark quand il burst
    # - préfixe des noms de fichiers images de cette partie du corps
    # - angle de rotation pour faire les différentes images rotatées
    # - tuple contenant les noms de fichiers courts (sans préfixe) des images
    listConfigRotatImg = (

        (ARM_RIGHT, MAGBURST_ARM_RIGHT_FILENAME_PREFIX,
         STEP_ANGLE_DYING_MAG_ARM, ("a", "b")),

        (ARM_LEFT,  MAGBURST_ARM_LEFT_FILENAME_PREFIX,
         STEP_ANGLE_DYING_MAG_ARM,  ("a", "b")),

        #j'ai mis un "moins" pour les angles de rotations. Comme ça, les images rotatées
        #de la tête seront rangés dans le sens anti-trigo. Et c'est plus naturel que la
        #tête tourne dans ce sens, vu qu'on dégomme le magicien par le côté gauche.
        (HEAD,      MAGBURST_HEAD_FILENAME_PREFIX,
         -STEP_ANGLE_DYING_MAG_ARM,  ("a", "b")),

    )

    #le but, c'est d'alimenter le sous-dictionnaire contenu dans dicImgInfoSpriteSimple[MAGBURST],
    #avec :
    # - clé : identifiant de la partie du corps (elem 0 du tuple ci-dessus)
    # - valeur : une liste, de deux éléments, correspondant respectivement
    #            aux fichiers images "a" et "b".
    #             - contenu de chaque élément : la liste des images rotatées de la partie du corps
    #               en question. Ouf, il était temps !!

    for confRotImg in listConfigRotatImg:

        #récup des infos contenues dans l'élément du tuple de tuple
        idMagPart, prefixFNameImg, stepAngle, listShortFName = confRotImg

        #listRotatImgMagBurstTemp signifie "list rotated image magician bursting - Temporary"
        #et si ça vous fait chier mes noms à rallonge, allez vous faire voir ok ?
        listRotatImgMagBurstTemp = []

        for shortFName in listShortFName:
            #chargement de l'image de la partie du corps qu'on doit faire rotater.
            imgMagPart = loadImg(prefixFNameImg + shortFName + ".png")
            #création d'une liste d'image rotatée à partir de cette image
            listRotatImg = makeRotatedImg(imgMagPart, stepAngle)
            #ajout dans la liste de deux éléments des images rotatées.
            listRotatImgMagBurstTemp.append(listRotatImg)

        #dictionnaire de tuple(2) de tuple(n) de Surface rotatay. faites pas chiay
        rotatImgMagBurst[idMagPart] = tuple(listRotatImgMagBurstTemp)

    #ajout du sous-dictionnaire dans le gros dictionnaire total. A la clé MAGBURST.
    dicImgInfoSpriteSimple[MAGBURST] = rotatImgMagBurst

    return dicImgInfoSpriteSimple



class SpriteSimpleGenerator():

    def __init__(self, spriteSimpleManager, dicImgInfoSpriteSimple):
        """
        constructeur (thx cap obvious)

        entrées :
          spriteSimpleManager : classe SpriteSimpleManager, dans laquelle
                                on ajoutera les sprites générés.
          dicImgInfoSpriteSimple : gros dictionnaire contenant un gros tas d'imgInfo
                                   au fait, ça devrait s'appeler des animInfo, et pas imgInfo
                                   trop tard...
        """

        self.spriteSimpleManager = spriteSimpleManager
        #je met pas le même nom, c'est pour en avoir un plus court.
        #parce que je m'en sers partout de ce truc et après c'est le bordel.
        self.dicAll = dicImgInfoSpriteSimple

    #Info applicable à toutes les fonctions generateXXXX contenues dans cette classe :
    #Ces fonctions permettent de générer un SpriteSimple et de le refiler au SpriteSimpleManager,
    #qui s'occupera de les faire évoluer, updater, et les supprimera quand ce sera nécessaire.
    #
    #param qu'on retrouvera tout le temps :
    #entrées : posStart. Rect. position de départ du sprite.
    #plat-dessert :
    #        le SpriteSimple, avec toute la config qui va bien dedans.
    #        (Ce SpriteSimple est envoyé au spriteSimpleManager, pour qu'il puisse
    #         s'en occuper. Cela va de soit)


    def generateFume(self, posStart):
        """
        Génération d'un sprite "Fioume". Un pet de magicien.
        """

        #Le sprite Fume contient deux petites images de fumée, qui défilent une fois.
        #Il bouge un peu vers le bas, et un peu à gauche ou à droite. Mais pas trop.
        #la direction exacte du mouvement est un peu randomizée.
        #il n'y a pas d'accélération.
        paramSprite = (self.dicAll[FUME], posStart, 1, END_ON_IMG_LOOP,
                       pyRect(centeredRandom(2), randRange(1, 5)), 5)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateFlame(self, posStart):
        """
        Génération d'un sprite Flame. Le coup de feu du flingue du héros.
        """

        #Le sprite Flame contient deux images de flamme, qui défilent une fois.
        #pas de mouvement ni d'accélération.
        paramSprite = (self.dicAll[FLAME], posStart, 1, END_ON_IMG_LOOP)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateLittleShell(self, posStart):
        """
        génération d'un sprite LittleShell. La douille qui sort du fusil du héros.
        """

        #la LittleShell contient 4 images d'une shell qui tournoie. Le mouvement est vers
        #la gauche, et vers le haut ou le bas. L'accélération est vers le bas.
        #la LittleShell est détruite quand elle quitte l'aire de jeu, ou quand elle
        #a fait 50 anims.
        paramSprite = (self.dicAll[LITTLE_SHELL], posStart, 50,
                       END_ON_IMG_LOOP | END_ON_OUT_GAME_AREA,
                       pyRect(randRange(-6, 0), randRange(-3, 2)), 2,
                       pyRect(0, randRange(1, 3)), 4)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateMagBurstSplat(self, posStart):
        """
        génération de la grosse tache de sang lorsqu'un magicien explose
        """

        #sprite statique, dont l'anim ne s'exécute qu'une fois
        paramSprite = (self.dicAll[MAGBURST_SPLAT], posStart,
                       1, END_ON_IMG_LOOP)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateMagDyingShit(self, posStart):
        """
        génération de la transformation du magicien en merde, qui se déliquesce ensuite.
        """

        #sprite statique, dont l'anim ne s'exécute qu'une fois
        paramSprite = (self.dicAll[MAGI_DYING_SHIT], posStart,
                       1, END_ON_IMG_LOOP)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateMagDyingRotate(self, posStart):
        """
        génération du sprite du magicien qui meurt en tournoyant.
        """

        #le sprite part vers la droite et vers le haut.
        #il y a une accélération vers le bas. Le sprite est détruit quand il
        #arrive en bas de l'aire de jeu.
        paramSprite = (self.dicAll[MAGI_DYING_ROT], posStart,
                       IMG_LOOP_ETERNAL, END_ON_OUT_DOWN,
                       pyRect(randRange(2, 7), randRange(-15, -8)), 2,
                       pyRect(0, 1), 2,
                       DECAL_ON_CENTER)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateMagAppearing(self, posStart):
        """
        génération du sprite du magicien qui apparaît.
        Au début, il a un peu une forme de bite. Et après ça devient le magicien.
        Ca se voit pas trop, mais lol quand même.
        """

        #sprite statique, dont l'anim ne s'exécute qu'une fois
        paramSprite = (self.dicAll[MAGI_APPEAR], posStart, 1, END_ON_IMG_LOOP)
        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateBulletSmoke(self, posStart):
        """
        Génération de la fumée dans le chargeur de cartouche, quand le héros tire un coup de feu.
        """

        #Le sprite BulletSmoke contient deux images de flamme, qui défilent une fois.
        #pas de mouvement ni d'accélération.
        paramSprite = (self.dicAll[BULLET_SMOKE], posStart, 1,END_ON_IMG_LOOP)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)


    def generateSomeBlood(self, posStart, nbrBlood):
        """
        génération de plusieurs sprite de taches de sang. Pour faire une giclure. spluirk !

        chaque tache de sang est un sprite avec une seule image. Le sprite est détruit
        si il sort de l'aire de jeu ou si son anim est finie. Mais le temps d'anim
        n'est pas le même pour chaque sprite.

        entrées : nbrBlood. int. nombre de taches de sang à générer.

        plat-dessert : contrairement au aux autres fonctions generateXXXX, celle-ci
                       ne renvoie que d'alle. Et osef.
        """

        #youpiii !! boucle avec un compteur qui sert à rien. J'adore ça !
        for _ in xrange(nbrBlood):

            #temps (nbre de cycles) pour ce sprite
            timeBlood = 30 + centeredRandom(30)
            #mouvement initial vers le haut ou le bas, et vers la gauche ou la droite. (c la fête)
            moveRect = pyRect(centeredRandom(3), randRange(-4, 2))
            moveCycle = randRange(2, 4)
            #accélération vers le bas. un peu ou pas beaucoup.
            accelRect = pyRect(0, randRange(1, 2))
            accelCycle = randRange(3, 6)

            #on récupère le seul élément de la listImgInfo, contenant la seule image de l'anim.
            #et on en fait une copie.
            imgInfoBloodUnique = list(self.dicAll[PARTICLE_BLOOD][0])
            #on change la période de temps de cette seule image. Pour mettre le temps
            #qu'on a choisi un peu plus haut.
            imgInfoBloodUnique[1] = timeBlood
            #tuplifiage de cet élément unique, et rangement de cet élément dans un "sur-tuple"
            #comme ça, on a une nouvelle listImgInfo (même si c'est une liste avec qu'un seul
            #element dedans)
            listImgInfo = ( tuple(imgInfoBloodUnique), )

            #création du sprite avec cette listImgInfo, et les params de move et d'acccel
            #calculés plus haut.
            #le sprite devra se terminer quand l'anim sera terminée. Et celle-ci n'est exécutée
            #qu'une seule fois. (Mais le temps de l'anim est variable, cc'est ça qu'est cool)
            paramSpr = (listImgInfo, posStart, 1,
                        END_ON_IMG_LOOP | END_ON_OUT_GAME_AREA,
                        moveRect, moveCycle, accelRect, accelCycle)

            self.spriteSimpleManager.addSpriteSimple(*paramSpr)


    def buildListIndexChoice(self, lenBaseList,
                             lenListIndexChoiceMin, lenListIndexChoiceMax):
        """
        fonction qui pourrait + ou - être mise dans le common. Mais pas forcément.
        Donc pour l'instant elle est là.

        fabrique une liste de tuple de 2 éléments int
         - le 1er elem c'est une alternance de O et de 1.
         - Le 2eme c'est une suite de chiffre qui monte et descend, sur une certaine
           quantité de valeur choisie au hasard. Cette suite de chiffre est bornée
           entre 0 et une autre valeur. Si on dépasse la borne, ça fait le tour et
           ça revient à 0

        A quoi ça sert ? A fabriquer une liste d'index pointant sur une liste d'images rotatées
        Comme la suite de chiffre monte puis descend, ça va faire une rotation d'oscillation
        (Ca tourne un peu dans un sens, puis dans l'autre, etc.)
        Et le 1er element (0 / 1), c'est pour pouvoir piocher alternativement dans une suite
        d'image rotatée ou dans une autre.
        Ca sert pour les MagBurst Arm (droit ou gauche), pour lesquels on a, à chaque fois,
        2 listes rotatées de 2 sprites un peu différent.

        entrées :
            lenBaseList : int. nombre d'élément des 2 listes rotatées.
                          Ca définit la borne supérieur pour les valeurs du 2eme elem

            lenListIndexChoiceMin,
            lenListIndexChoiceMax : int et int. Valeurs min et max pour la détermination
                                    en random de la longueur de la suite de chiffre.
                                    (la demi-longueur, en fait, car ça monte puis descend)

        plat-dessert :
            la liste de tuple de 2 elements, comme expliqué plus haut.
            (j'avais envie de l'expliquer plus haut. Na !!

        ex : lenBaseList = 10
             (lenListIndexChoiceMin, lenListIndexChoiceMax) = (3, 8)
             le random doit choisir un départ entre 0 et 10 -> 7
             le random doit choisir une demi-longueur entre 3 et 8 -> 5
             donc on fera monter-descendre à partir de 7, sur 5 valeurs.
             C'est à dire de 7 à 11.
             liste qui monte et descend: 7, 8, 9, 10, 11, 10, 9, 8
             (les valeurs min et max ne sont pas répétées dans le montage-descendage)
             bornage dans lenBaseList : 7, 8, 9, 0, 1, 0, 9, 8
             ajout du 0 / 1. (le random choisit si on commence à 1 ou 0)
             (7, 0), (8, 1), (9, 0), (0, 1), (1, 0), (0, 1), (9, 0), (8, 1)

        je suis un peu con, j'aurais peut-être du décomposer ça en 2 fonctions. boah osef.
        """

        #on détermine, totalement au hasard, l'index de départ dans la liste
        #des images rotatées.
        startIndexChoice = randRange(lenBaseList)

        #on détermine un peu au hasard, mais entre les val min et max, la demi-longueur
        #de la liste d'index d'images rotatées qui va monter et descendre.
        lenIndexChoice = randRange(lenListIndexChoiceMin,lenListIndexChoiceMax)

        #index de fin. Pour l'instant, il n'est pas bornée entre 0 et lenBaseList.
        #On le fera plus tard.
        endIndexChoice = startIndexChoice + lenIndexChoice

        #création de la 1ère demi-liste. (Les index montent, de start jusqu'à end)
        listIndexFirstHalf = range(startIndexChoice, endIndexChoice)

        #création de la 2eme demi-liste. (les index redescendent).

        #on commence par prendre la 1ere demi-liste, sans l'index de début ni celui de fin,
        #(cette instruction ne plante pas si la demi-liste de départ n'a que 0 ou 1 elem.
        #on se chope juste une liste vide qui ne sert à rien)
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
                                   #à partir de là, il suffit de faire compter de 1 en 1,
                                   #en partant de n'importe quelle valeur, osef.
                                   #(et on a ajouté le choiceImg pour avoir le hasard)
                                   (elem + choiceImg) & 1,
                                   #2eme elem. On lui met un modulo. Pour qu'il
                                   #reste dans la liste des images rotatées.
                                   elem % lenBaseList)
                               #on compte dans la liste précédemment calculée, qui monte-descend
                               for elem in listIndex
                             ]

        return tuple(listIndexAndChoice)


    def generateMagBurstArm(self, posStart, idMagArm, rectMove, rectAccel):
        """
        construit un SpriteSimple de type MagBurst, de type-type "bras coupé qui vole"

        entrées :
            posStart  : rect(X, Y). position initiale
            idMagArm  : choix du bras. ARM_RIGHT ou ARM_LEFT
            rectMove  : rect(X,Y). mouvement initial
            rectAccel : rect(X,Y). accélération

        la période de mouvement c'est 2. La période d'accélération c'est 4. Y'a pas le choix.
        J'ai décidé de les définir dans cette fonction, car c'est les mêmes quel que soit
        le type de bras (gauche ou droit)
        """

        #référence vers les 2 listes de sprites rotatés correspondant au bras coupé choisi
        listRotatedImgArm = self.dicAll[MAGBURST][idMagArm]

        #recup du nombre d'image dans les listes rotatées. (C'est le même nombre
        #dans les deux listes, on aurait pu foutre [1] ça aurait fait pareil.
        nbrImgRotated = len(listRotatedImgArm[0])

        #création à peu près random de la liste des index des images rotatées
        #les index vont pointer vers des images dans les 2 listes (voir fonc buildListIndexChoice)
        param = (nbrImgRotated,
                 MAGBURST_ARM_LIST_IMG_LEN_MIN, MAGBURST_ARM_LIST_IMG_LEN_MAX)

        listImgIndexAndChoice = self.buildListIndexChoice(*param)

        #construction de la liste des images pour l'anim. En utilisant la liste d'index
        #créées précédemment.
        #Le temps entre 2 img est le même.
        #Pas de décalage entre 2 img (on le gérera avec un décalage par rapport aux centres)
        listImgInfo = [ (listRotatedImgArm[elem[0]][elem[1]],
                         COUNTER_IMG_DYING_MAG_ARM,
                         pyRect()
                        ) for elem in listImgIndexAndChoice
                      ]

        #création du SpriteSimple, avec la liste d'images, et les pos, move et accel
        #indiqués en paramètre. on indique le décalage par rapport aux centres (DECAL_ON_CENTER).
        #le sprite sera détruit quand il arivera en bas de l'écran.
        paramSprit = (listImgInfo, posStart, IMG_LOOP_ETERNAL,
                      END_ON_OUT_DOWN,
                      rectMove, 2, rectAccel, 4,
                      DECAL_ON_CENTER)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprit)


    def generateMagBurstArmRight(self, posStart):
        """
        crée un SpriteSimple de type MagBurst, de type-type "bras coupé qui vole",
        de type-type-type "bras droit"
        """

        #random sur move et accel. Mouvement en cloche, qui part vers la droite.
        rectMove = pyRect(randRange(2, 7), randRange(-9, -4))
        rectAccel = pyRect(0, randRange(1, 3))

        return self.generateMagBurstArm(posStart, ARM_RIGHT,
                                        rectMove, rectAccel)


    def generateMagBurstArmLeft(self, posStart):
        """
        crée un SpriteSimple de type MagBurst, de type-type "bras coupé qui vole",
        de type-type-type "bras gauche"
        """

        #random sur move et accel. Mouvement en cloche, qui part vers la droite, mais pas trop.
        rectMove = pyRect(randRange(1, 4), randRange(-6, -3))
        rectAccel = pyRect(0, randRange(1, 3))

        return self.generateMagBurstArm(posStart, ARM_LEFT,
                                        rectMove, rectAccel)


    def generateMagBurstHead(self, posStart):
        """
        crée un SpriteSimple de type MagBurst, de type-type "tête coupée qui vole"
        """

        #La tête coupée tourne dans les airs. C'est pas un mouvement de rotation
        #oscillatoire comme les bras coupés. Du coup  c'est plus simple à faire.
        #On prend tout le temps toute la liste d'image rotatées. Le seul choix random
        #que y'a à faire, c'est l'alternance entre les 2 listes d'images.

        #référence vers les 2 listes de sprites rotatés correspondant à la tête coupée
        listRotatedImgArm = self.dicAll[MAGBURST][HEAD]

        #recup du nombre d'image dans les listes rotatées. (C'est le même nombre
        #dans les deux listes, on aurait pu foutre [1] ça aurait fait pareil.
        nbrImg = len(self.dicAll[MAGBURST][HEAD][0])

        #choix entre 0 ou 1. Pour que l'alternance 0/1 permettant de choisir entre l'une
        #ou l'autre des listes rotatées soit au hasard.
        choiceImg = randRange(2)

        #construction de la liste des index vers les images rotatées.
        #On prend toute la liste, et à chaque element, on ajoute une valeur 0/1
        listImgIndexAndChoice = [ ( (elem + choiceImg) & 1, elem )
                                  for elem in xrange(nbrImg)
                                ]

        #construction de la liste des images pour l'anim. En utilisant la liste d'index
        #créées précédemment.
        #Le temps entre 2 img est le même.
        #Pas de décalage entre 2 img (on le gérera avec un décalage par rapport aux centres)
        listImgInfo = [ (self.dicAll[MAGBURST][HEAD][elem[0]][elem[1]],
                         COUNTER_IMG_DYING_MAG_HEAD,
                         pyRect()
                        ) for elem in listImgIndexAndChoice
                      ]

        #création du SpriteSimple. Mouvement en cloche, qui part vers la droite, ou pas,
        #et qui vole vers le haut bien plus que les bras. (Comme ça c'est rigolo, la tête
        #elle peut faire une grande-grande courbe dans l'air. Youpi !!!)
        paramSprite = (listImgInfo, posStart, IMG_LOOP_ETERNAL,
                       END_ON_OUT_DOWN,
                       pyRect(randRange(0, 5), randRange(-12, -6)), 2,
                       pyRect(0, randRange(1, 3)), 4,
                       DECAL_ON_CENTER)

        return self.spriteSimpleManager.addSpriteSimple(*paramSprite)

