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

date de la dernière relecture-commentage : 01/03/2011

classe qui gère l'anim du début. (le magicien en gros plan apparaît à droite, et se déplace
un peu vers la gauche. En même temps le héros en gros plan apparaît à gauche, et se
déplace vers la droite. Puis le titre apparait en mega-zoom au milieu-haut de l'écran.
Il se dézomme progressivement pour arriver à sa taille normale.

Cette classe charge également tous les fichiers de sons.
Pourquoi qu'on charge les fichiers sons ici ? Voir explication dans le __init__ de mainclas.py

Autre truc important : l'image de fond utilisée dans les différents principal du jeu n'est
pas chargée directement depuis un fichier. Elle est fabriquée lors de la présentation.
C'est l'image finale de l'anim de présentation, qu'il faut juste assombrir un peu.
Cette image finale est stockée dans self.imgBgMainMenu. Le code extérieur pourra la récupérer.
Le code extérieur a également besoin de l'image du titre "Blarg" (pour l'afficher en
pas-assombri, alors que tout le reste de l'image de background est assombrie).
Cette image est stockée dans self.imgTitle. Le code extérieur peut également la récupérer.

Du coup, avec toute cette histoire, on est obligé de dérouler toute l'animation de présentation
au début du jeu. Sinon l'image de background n'est pas calculée, et self.imgBgMainMenu n'est
pas définie. Mais ça tombe bien, c'est ce qui est fait. (On peut pas skipper la présentation).
"""

import pygame

from common   import (securedPrint, pyRect, SCREEN_RECT, COLOR_BLACK,
                      loadImg, loadImgInDict, pixTranspLight)

from txtstock import txtStock
from yargler  import theSoundYargler, SND_PREZ_BLARG


#identifiants des images de l'animation de présentation.
#Chaque identifiant représente l'une des images utilisé pendant la présentation.
#Ca n'a rien à voir avec les sprites du héros, des magiciens, ... utilisés pendant le jeu.
(IMG_HERO,       #image du héros, avec son flingue et ses dents serrées.
 IMG_MAGI,       #image du magicien, avec ses boutons sur la gueule.
 IMG_TITLE,      #image du titre "Blarg", en jaune-orange vue un peu par en dessous wouhou.
 IMG_BACKGROUND, #image de fond de la présentation. L'espèce de vortex bleu-violet-moche.
) = range(4)

#correspondance entre les identifiants d'images et leurs noms de fichiers. (.png,, comme d'hab')
LIST_FILENAME_IMG_PREZ = (
 (IMG_HERO,   "prezhero"),
 (IMG_MAGI,   "prezmagi"),
 (IMG_TITLE,  "preztitl"),
 #l'image de background n'est pas indiquée ici, car elle n'a pas de key Transparency.
 #Du coup, faudra la charger un peu plus "manuellement" que les autres images.
 #C'est géré à l'arrache, ce truc. Bon, c'est pas grave.
)

#et le voilà ! le nom du fichier pour l'image de fond.
FILENAME_IMG_BG_PREZ = "prezback.png"



class PresentationAnim():
    """
    classe qui gère ce qui est l'exact contraire d'une carotte rose.
    C'est à dire l'animation de présentation de mon jeu.
    """

    def __init__(self, screen, fontDefault):
        """
        constructeur. (thx captain obvious)

        entrée :
            screen : Surface principale de l'écran, sur laquelle s'affiche l'animation.
            fontDefault : pygame.font.Font. police de caractère par défaut.
                          Y'en a besoin pour afficher le "LOADINGE" au début.
        """

        self.screen = screen
        self.fontDefault = fontDefault

        #initialisation des deux variables qui contiendront les images récupérables par le code
        #extérieur, une fois que l'animation sera terminée. Car y'en aura besoin pour la suite.
        #image de background des menus. Elaborées durant l'animation
        self.imgBgMainMenu = None
        #image du titre. Chargé telle quelle depuis un fichier image.
        self.imgTitle = None


    def launchAnim(self):
        """
         - effectue l'animation, et la montre à l'écran devant les yeux subjugués du joueur.
         - charge tous les sons, à partir des fichiers .ogg (car c'est cool comme format)
         - construit les images self.imgBgMainMenu et self.imgTitle

        Comme j'ai pas voulu trop me faire chier pour cette petite animation, tout est géré
        avec des images, que je blitte là où il faut.
        C'est pas géré avec des sprites, que je met dans des groupes et que je déplace.
        Ca vaut pas le coup pour un truc aussi simple.
        """

        pygame.mouse.set_visible(0)

        #chargement de l'image de background, sans key transparency.
        imgBackground = loadImg(FILENAME_IMG_BG_PREZ, colorkey=None)
        self.screen.blit(imgBackground, (0, 0))

        #récupération du texte "LOADINGE"
        txtLoading = txtStock.getText(txtStock.PREZ_LOADING)
        colorWhite = (255, 255, 255)
        #création de l'image affichant le texte, et blittage. J'utilise pas le Lamoche,
        #car c'est un sprite. Et j'ai dit que je prenais pas les sprites pour cette anim.
        imgLoading = self.fontDefault.render(txtLoading, False, colorWhite)
        self.screen.blit(imgLoading, (180, 100))

        #gros flip global. Il faut, car c'est le tout premier flip du début du jeu.
        pygame.display.flip()

        #chargement de toute les autres images (avec key transparency).
        dicImg = loadImgInDict(LIST_FILENAME_IMG_PREZ)
        #rangement dans le dico de l'imagede background déjà chargée plus haut.
        dicImg[IMG_BACKGROUND] = imgBackground

        # -- construction de la liste d'images agrandies du titre "Blarg" --
        #on commence par une image très très agrandie, pour finir sur une image normale.

        #liste des tailles d'agrandissement relatives. On ira d'un agrandissement 7 fois
        #jusqu'à un agrandissement 1,4 fois
        listIntScaleRel = range(70, 10, -4)
        listScaleRel = [ scale / 10.0 for scale in listIntScaleRel ]
        #ajout, en fin de liste, de l'agrandissement 1 fois. C'est plus sécuritable de
        #l'ajouter comme ça plutôt que de l'avoir mis dans la liste de départ, en
        #priant pour que les divers calculs matheux tombent juste et qu'on retombe sur 1.
        listScaleRel.append(1)

        titleWidth, titleHeight = dicImg[IMG_TITLE].get_size()

        #création de la liste des tailles absolues, sous forme de couple (width, height).
        listSizeScaled = [ (int(titleWidth * scale), int(titleHeight * scale))
                           for scale in listScaleRel
                         ]

        #création des image agrandies, à partir de la liste des tailles absolues.
        listImgTitleScaled = [ pygame.transform.scale(dicImg[IMG_TITLE], size)
                               for size in listSizeScaled ]

        #création de la liste des positions (X, Y) du coin supérieur-gauche es images agrandies.
        #les images doivent être centrée horizontalement sur l'abscisse X = 210.
        #Le bas de la première image se trouve à l'ordonnée Y=30,
        #le bas des images suivantes descend de 2 en 2.
        listPosImgTitle = [ (210 - width/2, 30 + offsetY*2 - height)
                            for offsetY, (width, height)
                            in enumerate(listSizeScaled)
                          ]

        #nombre de Frame Par Seconde de l'animation
        animFPS = 55
        #classe pour gérer toute seule le FPS.
        clock = pygame.time.Clock()

        #position de départ du magicien. Il est à droite de l'écran, mais pas complètement.
        #Le bas du magicien est en bas de l'écran.
        posMagi = pyRect(SCREEN_RECT.width - 9,
                         SCREEN_RECT.height - dicImg[IMG_MAGI].get_height())

        #position de départ du héros. Il est à gauche de l'écran. Le bas est au bas de l'écran.
        posHero = pyRect(-255,
                         SCREEN_RECT.height - dicImg[IMG_HERO].get_height())

        #curseur parcourant la liste des images et la liste des position du titre "Blarg".
        cursorImgTitle = 0

        #chargement de tous les sons. Paf, comme ça cash. Ouais, on le fait là,
        #c'est un peu zarb. Voir explication dans le __init__ de mainclas.py
        #TRODO pour plus tard : charger maintenant les premiers sons utiles (ceux de la prez),
        #Et charger les suivants pendant la prez, petit à petit. Ca fera un loading moins long.
        theSoundYargler.loadAllSounds()

        # --- grosse boucle décrivant tous les mouvements d'image de l'anim de présentation ---

        for animCounter in xrange(40):

            #gestion du nombre de FPS, avec la classe toute faite "sur étagère". Haha.
            clock.tick(animFPS)

            #on y va bourrin. On reblitte l'image de fond intégralement, à chaque fois.
            #C'est plus lent, mais osef. C'est une anim, il ne se passe rien d'autre que ça.
            self.screen.blit(dicImg[IMG_BACKGROUND], (0, 0))

            #blittage du magicien et du héros, à leur position courante.
            self.screen.blit(dicImg[IMG_MAGI], posMagi)
            self.screen.blit(dicImg[IMG_HERO], posHero)

            # -- gestion des divers mouvements des images. Un peu dégueu, mais osef --

            #au début, le magicien bouge assez rapidement vers la gauche, (de 10 en 10),
            #et quand il voit arriver le héros, il se recule un peu (de 2 en 2)
            if animCounter < 13:
                posMagi.move_ip(-10, 0)
            elif 14 < animCounter < 17:
                posMagi.move_ip( +2, 0)

            #le héros avance rapidement vers la droite (de 15 en 15)
            if animCounter < 17:
                posHero.move_ip(+15, 0)

            #le titre n'est pas visible au début. Il apparaît après 20 cycles.
            if animCounter > 20:

                #tant qu'on n'est pas à la fin de la liste, on avance le curseur.
                #Et on prend à chaque fois l'image agrandie courante, et la position qui va avec.
                if cursorImgTitle < len(listPosImgTitle):
                    imgTitle = listImgTitleScaled[cursorImgTitle]
                    postitle = listPosImgTitle[cursorImgTitle]
                    cursorImgTitle += 1

                #Affichage de l'image. Lorsque cursorImgTitle est arrivé au bout de la liste,
                #on se retrouve à afficher, à chaque cycle, la même image (non agrandie),
                #à la même position. Et c'est cool, c'est ce qu'on veut.
                self.screen.blit(imgTitle, postitle)

            if animCounter == 37:
                #son de présentation : "blarg" !!
                theSoundYargler.playSound(SND_PREZ_BLARG)

            #gros flip global à chaque cycle. Bourrin et lent, mais osef, c'est qu'une anim.
            pygame.display.flip()


        # --- Voilà, c'est la fin de l'animation. Youpi ---

        #Création de l'image qui sera le background du menu principal.
        #Pour ça, on prend l'image actuellement affichée à l'écran, et on l'assombris fortement.
        #Ce qui fait que j'accède en lecture à self.screen, la Surface spéciale utilisée
        #pour l'affichage à l'écran. Est-ce bien ou mal ? Jusqu'ici, ça fonctionne.
        #(Y'a des risques de foirage si on utilise une accélération matérielle, ou je sais
        #pas quoi. Mais bon, je fais pas ce genre de chose.)
        self.imgBgMainMenu = pixTranspLight(self.screen, 0, 180)

        #conservation en mémoire de l'image du titre. Il suffit de l'enregistrer comme
        #membre de la classe. Et comme la classe est conservée en mémoire. C'est bon.
        #C'est une manière de faire un peu "hop hop à l'arrache", mais c'est pas grave.
        self.imgTitle = dicImg[IMG_TITLE]

        #re-affichage du curseur de souris. Que le joueur puisse cliquouiller dans les menus.
        pygame.mouse.set_visible(1)

        #Maintenant, on s'en va. Et donc le code extérieur pourra récupérer self.imgBgMainMenu
        #et self.imgTitle. (Oui je l'ai déjà dit 3 fois. Mais j'ai toujours peu de pas être
        #compréhensible quand j'explique des trucs. Y compris pour moi même quand je me relis).
