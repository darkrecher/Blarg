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

date de la dernière relecture-commentage : 15/10/2010

Classe de sprite tout simple. Trucs qu'on peut faire et pas faire avec :

 - une liste d'images qui défilent, avec les temps que l'on veut
   entre chaque image. Ca peut défiler en boucle ou un certain nombre de fois.

 - du mouvement en courbe. On indique une vitesse initiale et une
   accélération.

   - destruction automatique du sprite. Au choix : soit quand il est complètement sorti
   de l'écran, soit quand il a fini l'enchaînement d'images qu'on lui a indiqué

 * pas d'interaction, de gestion de collision... rien de tout ça.

 * pas de mouvement aléatoire. Et on peut pas changer les caractéristiques du mouvement
   une fois que le sprite est créé

 * il faut placer ces sprites dans le spriteSimpleManager,
   pour qu'ils soient gérés à chaque cycle de jeu.

Le SpriteSimple ne se détruit pas lui même lorsque c'est le moment. (Ha ha). Il met à jour
sa variable self.currentState à la valeur SPRITE_DEAD.
C'est le SpriteSimpleManager qui s'occupe de la destruction des sprites qui sont SPRITE_DEAD

TRODO : version 2 : la période de temps entre 2 images doit pouvoir être randomisable.
on indique une tuple min, max. Et ça calculera le random en live.
"""

import pygame

from common import GAME_RECT, pyRect, NONE_COUNT

#juste pour donner un nom plus adequat. (Sheila elle adequat)
IMG_LOOP_ETERNAL = NONE_COUNT

#conditions indiquant à quel moment le sprite sera DEAD. (on peut les "orer")
(END_ON_IMG_LOOP,       #on a fini de faire défiler les images (nbrImgLoop fois)
 END_ON_OUT_GAME_AREA,  #le sprite est sorti de l'aire de jeu, par n'importe quel côté
                        #attention, j'ai dit sorti de l'aire de jeu, pas sorti de l'écran.
 END_ON_OUT_DOWN,       #le sprite est sorti de l'écran par le bas
 #y'a pas les autres (END_ON_OUT_LEFT, ..., pas besoin pour l'instant.
 END_NEVER,             #le sprite n'est jamais DEAD
) = (1, 2, 4, 0)  #faut des puissances de 2, car on va orifier tout ça

#etat du sprite.
(SPRITE_ALIVE,  #Il est vivant.
 SPRITE_DEAD    #il est mort et le SpriteSimpleManager devra le détruire.
) = range(2)

#utilisé par le code extérieur. C'est juste pour définir de manière plus explicite
#la valeur du paramètre makeDecalCenter. Quand on veut que le sprite fasse ce décalage
#Y'a pas de NOT_DECAL_ON_CENTER = False. Car c'est la valeur par défaut du param.
DECAL_ON_CENTER = True



class SpriteSimple(pygame.sprite.Sprite):
    """
    le sprite qui est un objet au mouvement simple
    """

    def __init__(self, listImgInfo, posStart, nbrImgLoop=IMG_LOOP_ETERNAL,
                 endCondition=END_ON_OUT_GAME_AREA,
                 moveRect=pyRect(), movePeriod=NONE_COUNT,
                 accelRect=pyRect(), accelPeriod=NONE_COUNT,
                 makeDecalCenter=False):
        """
        constructeur. (thx captain obvious)

        entrée :
            listImgInfo : liste de tuple de 3 elements
               - Surface contenant une image du sprite
               - temps(nombre de cycle) avant de passer à l'image suivante
               - rect(X, Y) de décalage à appliquer lorsqu'on passe à l'image suivante
               (le tout premier décalage de listImgInfo sera appliqué dès la création du sprite)

            posStart : rect. position du coin superieur gauche du sprite, à l'écran.
                (enfin presque, because éventuel décalage initial)

            nbrImgLoop : int, ou valeur IMG_LOOP_ETERNAL. Nombre de fois qu'on fait
                défiler la liste d'image avant d'arrêter l'animation. (elle est moche cette phrase)
                si IMG_LOOP_ETERNAL : on arrête jamis l'anim.

            enfCondition : valeurs END_ON_XXX, indiquant à quel moment le sprite sera supprimé.
                Voir définition de ces valeurs au début de ce fichier. On peut les "orer".

            moveRect, movePeriod : rect et int. Mouvement du sprite, et sa période,
                en nombre de cycle. si movePeriod vaut NONE_COUNT : pas de mouvement

            accelRect, accelPeriod : rect et int. Accélération du sprite et sa période (pareil)
                si accelPeriod vaut NONE_COUNT : pas d'accélération

            makeDecalCenter : booléen. si true, à chaque changement d'image,
                on appplique un décalage automatique, de façon à
                ce que les centres des deux images soient confondus.
                (on peut en plus appliquer des décalages individuels avec
                les rects de listImgInfo)

            TRODO : c'est de la merde ce DecalCenter. Faut tout gérer avec des hotPoint,
                j'arrête pas de le dire depuis le début, putain de merde.
        """
        pygame.sprite.Sprite.__init__(self)

        #putain d'initialisations de merde. Y'a pas mieux ?
        self.listImgInfo = listImgInfo
        self.nbrImgLoop = nbrImgLoop
        self.endCondition = endCondition
        #vaut mieux recopier les Rect de position, move et accel.
        #même si c'est pas forcément utile.
        #Si les rect viennent d'une constante, on risque de tout niquer
        self.moveRect = pygame.Rect(moveRect)
        self.movePeriod = movePeriod
        self.accelRect = pygame.Rect(accelRect)
        self.accelPeriod = accelPeriod
        self.makeDecalCenter = makeDecalCenter
        self.rect = pygame.Rect(posStart)

        #curseur sur listImgInfo, indiquant l'image en cours, affiché à l'écran.
        self.imgCursor = 0

        #nombre de boucle déjà faite dans le défilement d'image.
        self.imgLoopMade = 0

        #It's ALIVE  !!! FFEEAAAAAARRRRR !!!!!
        self.currentState = SPRITE_ALIVE

        #on affiche la première image de listImgInfo, et on applique le décalage
        #ça définit également la variable self.changeImageCounter, qui indique le nombre
        #de cycle avant le prochain changement d'image.
        self.refreshImg()

        if self.endCondition & END_ON_OUT_GAME_AREA:

            #le sprite doit se détruire quand il sort de l'aire de jeu. Donc il faut pas se
            #contenter de le définir avec un point. Il lui faut aussi une taille de rectangle,
            #ce qui permettra de savoir quand le sprite est complètement hors de l'écran.
            #(on ne le détruit pas si il est en partie hors de l'écran)

            #du coup, pour déterminer la taille, je me fait pas chier. Je prends la
            #longueur et la largeur max de la liste d'image du sprite.
            #Y'aurait surement moyen de faire plus optimisé, mais KISS.

            #TRODO version 2 : précalculer ça, et donner la possibilité de passer la
            #taille précalculée en paramètre de l'__init__, pour qu'il soit pris tel quel.
            #C'est un gouffre à temps CPU, cette connerie. Bah, osef pour l'instant.

            listWidths  = [ imgInfo[0].get_width()
                            for imgInfo in listImgInfo
                          ]

            listHeights = [ imgInfo[0].get_height()
                            for imgInfo in listImgInfo
                          ]

            self.rect.size = (max(listWidths), max(listHeights))

        if self.movePeriod is not NONE_COUNT:
            #compteur pour les périodes de mouvement, si il y a du mouvement.
            self.moveCounter = self.movePeriod

        if self.accelPeriod is not NONE_COUNT:
            #pareil, mais accélération.
            self.accelCounter = self.accelPeriod


    def refreshImg(self):
        """
        fonction à lancer quand on a modifié self.imgCursor
        réactualise l'image en cours, en fonction de la nouvelle valeur de self.imgCursor
        ça réactualise aussi le compteur avant le prochain changement d'image.
        Et ça applique le décalage de sprite.
        """

        #chopage des infos en cours à partir de self.listImgInfo
        #ça change immédiatement l'image du sprite, because redef de self.image
        (self.image, self.changeImageCounter, rectDecalage
        ) = self.listImgInfo[self.imgCursor]

        if self.makeDecalCenter:
            #on  déplace un peu le rect du sprite, de façon à ce que le centre de
            #la nouvelle image et le centre de l'ancienne restent le même.
            #(code piqué à l'exemple "The Chimp", pour les images rotatées)
            self.rect = self.image.get_rect(center=self.rect.center)
            #atation, pour l'init au début, ça fout un peu le bronx. Mais pas trop.
            #ça veut dire que posStart indique la pos du centre, et non pas la pos
            #du coin supérieur gauche comme d'hab.
            #TRODO : d'ou l'intérêt des hotpoint et de ne plus se poser la question, bordel.

        #application du décalage lié à la nouvelle image.
        self.rect.move_ip(rectDecalage.topleft)


    def setCursorOnNextImage(self):
        """
        fonction qui détermine quelle est la prochaine image que le sprite doit afficher.
        Au passage, ça détermine aussi si le sprite doit arrêter de faire défiler ses images,
        et si il doit crever ou pas.
        """

        #On doit passer à l'image suivante, ou pas, ça dépendra des cas.
        #mais on part sur l'idée qu'il faudra le faire.
        mustChangeImage = True

        if self.imgCursor < len(self.listImgInfo)-1:

            #on n'est pas à la dernière image de self.listImgInfo
            #donc on peut avancer le curseur d'un cran, sans se poser de questions.
            self.imgCursor += 1

        else:

            #c'est la dernière image de self.listImgInfo. Ouatte is to be done ?

            if self.nbrImgLoop is IMG_LOOP_ETERNAL:
                #faut boucler éternellement. Donc on revient à la première image.
                self.imgCursor = 0

            else:

                #on a effectué une boucle d'image en plus.
                self.imgLoopMade += 1

                if self.imgLoopMade < self.nbrImgLoop:

                    #on n'a pas fini de faire le nombre de boucles d'images demandés.
                    #On revient à la première image.
                    self.imgCursor = 0

                else:

                    #on a fini de faire les boucles d'images. Donc on reste
                    #sur la dernière image.
                    self.imgCursor = len(self.listImgInfo) - 1
                    #on arrête le compteur. Maintenant on ne changera plus d'images.
                    self.changeImageCounter = NONE_COUNT
                    #on prévient que non non vraiment, il faut pas changer d'image
                    mustChangeImage = False

                    #et en plus, si le sprite doit crever à la fin de ses boucle d'image,
                    #on met à jour l'état, pour que le SpriteSimpleManager le fasse crever
                    if self.endCondition & END_ON_IMG_LOOP:
                        self.currentState = SPRITE_DEAD

        #rafraîchissement nouvel image si nécessaire.
        if mustChangeImage:
            self.refreshImg()


    def update(self):
        """
        grosse fonction de la mort qui gère tout :
        mouvement, accélération, changement d'image, alive/dead
        """

        # ---- gerage des changements d'images ----

        if self.changeImageCounter is not NONE_COUNT:
            self.changeImageCounter -= 1
            if self.changeImageCounter == 0:
                self.setCursorOnNextImage()

        # ---- gerage de l'accélération ----

        if self.accelPeriod is not NONE_COUNT:

            self.accelCounter -= 1

            if self.accelCounter == 0:

                self.accelCounter = self.accelPeriod
                #L'accélération reste tout le temps la même.
                #on l'applique sur le mouvement.
                self.moveRect.move_ip(self.accelRect.topleft)

        # ---- gerage du déplacement ----

        if self.movePeriod is not NONE_COUNT:

            self.moveCounter -= 1

            if self.moveCounter == 0:

                self.moveCounter = self.movePeriod
                #on applique le mouvement sur la position.
                self.rect.move_ip(self.moveRect.topleft)

        # ---- gerage de la mort du sprite si il est en dehors de l'écran ----

        if self.endCondition & END_ON_OUT_GAME_AREA:
            #on vérifie la collision entre le gros GAME_RECT et le petit self.rect.
            #Si ça se collisionne pas, c'est que le petit self.rect est complètement sorti
            #du gros GAME_RECT. Donc faut crever le sprite.
            if not GAME_RECT.colliderect(self.rect):
                self.currentState = SPRITE_DEAD

        if self.endCondition & END_ON_OUT_DOWN:
            #on vérifie si le haut du sprite n'est pas plus bas que le bas du GAME_RECT.
            #Si c'est le cas, le sprite est trop bas, on le voit plus du tout dans GAME_RECT.
            #Donc on le crève. Blarg.
            if  self.rect.top > GAME_RECT.bottom:
                self.currentState = SPRITE_DEAD

        #TRODO : rajouter les autres bords.

