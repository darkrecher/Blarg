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

date de la derni�re relecture-commentage : 15/10/2010

Classe de sprite tout simple. Trucs qu'on peut faire et pas faire avec :

 - une liste d'images qui d�filent, avec les temps que l'on veut
   entre chaque image. Ca peut d�filer en boucle ou un certain nombre de fois.

 - du mouvement en courbe. On indique une vitesse initiale et une
   acc�l�ration.

   - destruction automatique du sprite. Au choix : soit quand il est compl�tement sorti
   de l'�cran, soit quand il a fini l'encha�nement d'images qu'on lui a indiqu�

 * pas d'interaction, de gestion de collision... rien de tout �a.

 * pas de mouvement al�atoire. Et on peut pas changer les caract�ristiques du mouvement
   une fois que le sprite est cr��

 * il faut placer ces sprites dans le spriteSimpleManager,
   pour qu'ils soient g�r�s � chaque cycle de jeu.

Le SpriteSimple ne se d�truit pas lui m�me lorsque c'est le moment. (Ha ha). Il met � jour
sa variable self.currentState � la valeur SPRITE_DEAD.
C'est le SpriteSimpleManager qui s'occupe de la destruction des sprites qui sont SPRITE_DEAD

TRODO : version 2 : la p�riode de temps entre 2 images doit pouvoir �tre randomisable.
on indique une tuple min, max. Et �a calculera le random en live.
"""

import pygame

from common import GAME_RECT, pyRect, NONE_COUNT

#juste pour donner un nom plus adequat. (Sheila elle adequat)
IMG_LOOP_ETERNAL = NONE_COUNT

#conditions indiquant � quel moment le sprite sera DEAD. (on peut les "orer")
(END_ON_IMG_LOOP,       #on a fini de faire d�filer les images (nbrImgLoop fois)
 END_ON_OUT_GAME_AREA,  #le sprite est sorti de l'aire de jeu, par n'importe quel c�t�
                        #attention, j'ai dit sorti de l'aire de jeu, pas sorti de l'�cran.
 END_ON_OUT_DOWN,       #le sprite est sorti de l'�cran par le bas
 #y'a pas les autres (END_ON_OUT_LEFT, ..., pas besoin pour l'instant.
 END_NEVER,             #le sprite n'est jamais DEAD
) = (1, 2, 4, 0)  #faut des puissances de 2, car on va orifier tout �a

#etat du sprite.
(SPRITE_ALIVE,  #Il est vivant.
 SPRITE_DEAD    #il est mort et le SpriteSimpleManager devra le d�truire.
) = range(2)

#utilis� par le code ext�rieur. C'est juste pour d�finir de mani�re plus explicite
#la valeur du param�tre makeDecalCenter. Quand on veut que le sprite fasse ce d�calage
#Y'a pas de NOT_DECAL_ON_CENTER = False. Car c'est la valeur par d�faut du param.
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

        entr�e :
            listImgInfo : liste de tuple de 3 elements
               - Surface contenant une image du sprite
               - temps(nombre de cycle) avant de passer � l'image suivante
               - rect(X, Y) de d�calage � appliquer lorsqu'on passe � l'image suivante
               (le tout premier d�calage de listImgInfo sera appliqu� d�s la cr�ation du sprite)

            posStart : rect. position du coin superieur gauche du sprite, � l'�cran.
                (enfin presque, because �ventuel d�calage initial)

            nbrImgLoop : int, ou valeur IMG_LOOP_ETERNAL. Nombre de fois qu'on fait
                d�filer la liste d'image avant d'arr�ter l'animation. (elle est moche cette phrase)
                si IMG_LOOP_ETERNAL : on arr�te jamis l'anim.

            enfCondition : valeurs END_ON_XXX, indiquant � quel moment le sprite sera supprim�.
                Voir d�finition de ces valeurs au d�but de ce fichier. On peut les "orer".

            moveRect, movePeriod : rect et int. Mouvement du sprite, et sa p�riode,
                en nombre de cycle. si movePeriod vaut NONE_COUNT : pas de mouvement

            accelRect, accelPeriod : rect et int. Acc�l�ration du sprite et sa p�riode (pareil)
                si accelPeriod vaut NONE_COUNT : pas d'acc�l�ration

            makeDecalCenter : bool�en. si true, � chaque changement d'image,
                on appplique un d�calage automatique, de fa�on �
                ce que les centres des deux images soient confondus.
                (on peut en plus appliquer des d�calages individuels avec
                les rects de listImgInfo)

            TRODO : c'est de la merde ce DecalCenter. Faut tout g�rer avec des hotPoint,
                j'arr�te pas de le dire depuis le d�but, putain de merde.
        """
        pygame.sprite.Sprite.__init__(self)

        #putain d'initialisations de merde. Y'a pas mieux ?
        self.listImgInfo = listImgInfo
        self.nbrImgLoop = nbrImgLoop
        self.endCondition = endCondition
        #vaut mieux recopier les Rect de position, move et accel.
        #m�me si c'est pas forc�ment utile.
        #Si les rect viennent d'une constante, on risque de tout niquer
        self.moveRect = pygame.Rect(moveRect)
        self.movePeriod = movePeriod
        self.accelRect = pygame.Rect(accelRect)
        self.accelPeriod = accelPeriod
        self.makeDecalCenter = makeDecalCenter
        self.rect = pygame.Rect(posStart)

        #curseur sur listImgInfo, indiquant l'image en cours, affich� � l'�cran.
        self.imgCursor = 0

        #nombre de boucle d�j� faite dans le d�filement d'image.
        self.imgLoopMade = 0

        #It's ALIVE  !!! FFEEAAAAAARRRRR !!!!!
        self.currentState = SPRITE_ALIVE

        #on affiche la premi�re image de listImgInfo, et on applique le d�calage
        #�a d�finit �galement la variable self.changeImageCounter, qui indique le nombre
        #de cycle avant le prochain changement d'image.
        self.refreshImg()

        if self.endCondition & END_ON_OUT_GAME_AREA:

            #le sprite doit se d�truire quand il sort de l'aire de jeu. Donc il faut pas se
            #contenter de le d�finir avec un point. Il lui faut aussi une taille de rectangle,
            #ce qui permettra de savoir quand le sprite est compl�tement hors de l'�cran.
            #(on ne le d�truit pas si il est en partie hors de l'�cran)

            #du coup, pour d�terminer la taille, je me fait pas chier. Je prends la
            #longueur et la largeur max de la liste d'image du sprite.
            #Y'aurait surement moyen de faire plus optimis�, mais KISS.

            #TRODO version 2 : pr�calculer �a, et donner la possibilit� de passer la
            #taille pr�calcul�e en param�tre de l'__init__, pour qu'il soit pris tel quel.
            #C'est un gouffre � temps CPU, cette connerie. Bah, osef pour l'instant.

            listWidths  = [ imgInfo[0].get_width()
                            for imgInfo in listImgInfo
                          ]

            listHeights = [ imgInfo[0].get_height()
                            for imgInfo in listImgInfo
                          ]

            self.rect.size = (max(listWidths), max(listHeights))

        if self.movePeriod is not NONE_COUNT:
            #compteur pour les p�riodes de mouvement, si il y a du mouvement.
            self.moveCounter = self.movePeriod

        if self.accelPeriod is not NONE_COUNT:
            #pareil, mais acc�l�ration.
            self.accelCounter = self.accelPeriod


    def refreshImg(self):
        """
        fonction � lancer quand on a modifi� self.imgCursor
        r�actualise l'image en cours, en fonction de la nouvelle valeur de self.imgCursor
        �a r�actualise aussi le compteur avant le prochain changement d'image.
        Et �a applique le d�calage de sprite.
        """

        #chopage des infos en cours � partir de self.listImgInfo
        #�a change imm�diatement l'image du sprite, because redef de self.image
        (self.image, self.changeImageCounter, rectDecalage
        ) = self.listImgInfo[self.imgCursor]

        if self.makeDecalCenter:
            #on  d�place un peu le rect du sprite, de fa�on � ce que le centre de
            #la nouvelle image et le centre de l'ancienne restent le m�me.
            #(code piqu� � l'exemple "The Chimp", pour les images rotat�es)
            self.rect = self.image.get_rect(center=self.rect.center)
            #atation, pour l'init au d�but, �a fout un peu le bronx. Mais pas trop.
            #�a veut dire que posStart indique la pos du centre, et non pas la pos
            #du coin sup�rieur gauche comme d'hab.
            #TRODO : d'ou l'int�r�t des hotpoint et de ne plus se poser la question, bordel.

        #application du d�calage li� � la nouvelle image.
        self.rect.move_ip(rectDecalage.topleft)


    def setCursorOnNextImage(self):
        """
        fonction qui d�termine quelle est la prochaine image que le sprite doit afficher.
        Au passage, �a d�termine aussi si le sprite doit arr�ter de faire d�filer ses images,
        et si il doit crever ou pas.
        """

        #On doit passer � l'image suivante, ou pas, �a d�pendra des cas.
        #mais on part sur l'id�e qu'il faudra le faire.
        mustChangeImage = True

        if self.imgCursor < len(self.listImgInfo)-1:

            #on n'est pas � la derni�re image de self.listImgInfo
            #donc on peut avancer le curseur d'un cran, sans se poser de questions.
            self.imgCursor += 1

        else:

            #c'est la derni�re image de self.listImgInfo. Ouatte is to be done ?

            if self.nbrImgLoop is IMG_LOOP_ETERNAL:
                #faut boucler �ternellement. Donc on revient � la premi�re image.
                self.imgCursor = 0

            else:

                #on a effectu� une boucle d'image en plus.
                self.imgLoopMade += 1

                if self.imgLoopMade < self.nbrImgLoop:

                    #on n'a pas fini de faire le nombre de boucles d'images demand�s.
                    #On revient � la premi�re image.
                    self.imgCursor = 0

                else:

                    #on a fini de faire les boucles d'images. Donc on reste
                    #sur la derni�re image.
                    self.imgCursor = len(self.listImgInfo) - 1
                    #on arr�te le compteur. Maintenant on ne changera plus d'images.
                    self.changeImageCounter = NONE_COUNT
                    #on pr�vient que non non vraiment, il faut pas changer d'image
                    mustChangeImage = False

                    #et en plus, si le sprite doit crever � la fin de ses boucle d'image,
                    #on met � jour l'�tat, pour que le SpriteSimpleManager le fasse crever
                    if self.endCondition & END_ON_IMG_LOOP:
                        self.currentState = SPRITE_DEAD

        #rafra�chissement nouvel image si n�cessaire.
        if mustChangeImage:
            self.refreshImg()


    def update(self):
        """
        grosse fonction de la mort qui g�re tout :
        mouvement, acc�l�ration, changement d'image, alive/dead
        """

        # ---- gerage des changements d'images ----

        if self.changeImageCounter is not NONE_COUNT:
            self.changeImageCounter -= 1
            if self.changeImageCounter == 0:
                self.setCursorOnNextImage()

        # ---- gerage de l'acc�l�ration ----

        if self.accelPeriod is not NONE_COUNT:

            self.accelCounter -= 1

            if self.accelCounter == 0:

                self.accelCounter = self.accelPeriod
                #L'acc�l�ration reste tout le temps la m�me.
                #on l'applique sur le mouvement.
                self.moveRect.move_ip(self.accelRect.topleft)

        # ---- gerage du d�placement ----

        if self.movePeriod is not NONE_COUNT:

            self.moveCounter -= 1

            if self.moveCounter == 0:

                self.moveCounter = self.movePeriod
                #on applique le mouvement sur la position.
                self.rect.move_ip(self.moveRect.topleft)

        # ---- gerage de la mort du sprite si il est en dehors de l'�cran ----

        if self.endCondition & END_ON_OUT_GAME_AREA:
            #on v�rifie la collision entre le gros GAME_RECT et le petit self.rect.
            #Si �a se collisionne pas, c'est que le petit self.rect est compl�tement sorti
            #du gros GAME_RECT. Donc faut crever le sprite.
            if not GAME_RECT.colliderect(self.rect):
                self.currentState = SPRITE_DEAD

        if self.endCondition & END_ON_OUT_DOWN:
            #on v�rifie si le haut du sprite n'est pas plus bas que le bas du GAME_RECT.
            #Si c'est le cas, le sprite est trop bas, on le voit plus du tout dans GAME_RECT.
            #Donc on le cr�ve. Blarg.
            if  self.rect.top > GAME_RECT.bottom:
                self.currentState = SPRITE_DEAD

        #TRODO : rajouter les autres bords.

