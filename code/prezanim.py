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

date de la derni�re relecture-commentage : 01/03/2011

classe qui g�re l'anim du d�but. (le magicien en gros plan appara�t � droite, et se d�place
un peu vers la gauche. En m�me temps le h�ros en gros plan appara�t � gauche, et se
d�place vers la droite. Puis le titre apparait en mega-zoom au milieu-haut de l'�cran.
Il se d�zomme progressivement pour arriver � sa taille normale.

Cette classe charge �galement tous les fichiers de sons.
Pourquoi qu'on charge les fichiers sons ici ? Voir explication dans le __init__ de mainclas.py

Autre truc important : l'image de fond utilis�e dans les diff�rents principal du jeu n'est
pas charg�e directement depuis un fichier. Elle est fabriqu�e lors de la pr�sentation.
C'est l'image finale de l'anim de pr�sentation, qu'il faut juste assombrir un peu.
Cette image finale est stock�e dans self.imgBgMainMenu. Le code ext�rieur pourra la r�cup�rer.
Le code ext�rieur a �galement besoin de l'image du titre "Blarg" (pour l'afficher en
pas-assombri, alors que tout le reste de l'image de background est assombrie).
Cette image est stock�e dans self.imgTitle. Le code ext�rieur peut �galement la r�cup�rer.

Du coup, avec toute cette histoire, on est oblig� de d�rouler toute l'animation de pr�sentation
au d�but du jeu. Sinon l'image de background n'est pas calcul�e, et self.imgBgMainMenu n'est
pas d�finie. Mais �a tombe bien, c'est ce qui est fait. (On peut pas skipper la pr�sentation).
"""

import pygame

from common   import (securedPrint, pyRect, SCREEN_RECT, COLOR_BLACK,
                      loadImg, loadImgInDict, pixTranspLight)

from txtstock import txtStock
from yargler  import theSoundYargler, SND_PREZ_BLARG


#identifiants des images de l'animation de pr�sentation.
#Chaque identifiant repr�sente l'une des images utilis� pendant la pr�sentation.
#Ca n'a rien � voir avec les sprites du h�ros, des magiciens, ... utilis�s pendant le jeu.
(IMG_HERO,       #image du h�ros, avec son flingue et ses dents serr�es.
 IMG_MAGI,       #image du magicien, avec ses boutons sur la gueule.
 IMG_TITLE,      #image du titre "Blarg", en jaune-orange vue un peu par en dessous wouhou.
 IMG_BACKGROUND, #image de fond de la pr�sentation. L'esp�ce de vortex bleu-violet-moche.
) = range(4)

#correspondance entre les identifiants d'images et leurs noms de fichiers. (.png,, comme d'hab')
LIST_FILENAME_IMG_PREZ = (
 (IMG_HERO,   "prezhero"),
 (IMG_MAGI,   "prezmagi"),
 (IMG_TITLE,  "preztitl"),
 #l'image de background n'est pas indiqu�e ici, car elle n'a pas de key Transparency.
 #Du coup, faudra la charger un peu plus "manuellement" que les autres images.
 #C'est g�r� � l'arrache, ce truc. Bon, c'est pas grave.
)

#et le voil� ! le nom du fichier pour l'image de fond.
FILENAME_IMG_BG_PREZ = "prezback.png"



class PresentationAnim():
    """
    classe qui g�re ce qui est l'exact contraire d'une carotte rose.
    C'est � dire l'animation de pr�sentation de mon jeu.
    """

    def __init__(self, screen, fontDefault):
        """
        constructeur. (thx captain obvious)

        entr�e :
            screen : Surface principale de l'�cran, sur laquelle s'affiche l'animation.
            fontDefault : pygame.font.Font. police de caract�re par d�faut.
                          Y'en a besoin pour afficher le "LOADINGE" au d�but.
        """

        self.screen = screen
        self.fontDefault = fontDefault

        #initialisation des deux variables qui contiendront les images r�cup�rables par le code
        #ext�rieur, une fois que l'animation sera termin�e. Car y'en aura besoin pour la suite.
        #image de background des menus. Elabor�es durant l'animation
        self.imgBgMainMenu = None
        #image du titre. Charg� telle quelle depuis un fichier image.
        self.imgTitle = None


    def launchAnim(self):
        """
         - effectue l'animation, et la montre � l'�cran devant les yeux subjugu�s du joueur.
         - charge tous les sons, � partir des fichiers .ogg (car c'est cool comme format)
         - construit les images self.imgBgMainMenu et self.imgTitle

        Comme j'ai pas voulu trop me faire chier pour cette petite animation, tout est g�r�
        avec des images, que je blitte l� o� il faut.
        C'est pas g�r� avec des sprites, que je met dans des groupes et que je d�place.
        Ca vaut pas le coup pour un truc aussi simple.
        """

        pygame.mouse.set_visible(0)

        #chargement de l'image de background, sans key transparency.
        imgBackground = loadImg(FILENAME_IMG_BG_PREZ, colorkey=None)
        self.screen.blit(imgBackground, (0, 0))

        #r�cup�ration du texte "LOADINGE"
        txtLoading = txtStock.getText(txtStock.PREZ_LOADING)
        colorWhite = (255, 255, 255)
        #cr�ation de l'image affichant le texte, et blittage. J'utilise pas le Lamoche,
        #car c'est un sprite. Et j'ai dit que je prenais pas les sprites pour cette anim.
        imgLoading = self.fontDefault.render(txtLoading, False, colorWhite)
        self.screen.blit(imgLoading, (180, 100))

        #gros flip global. Il faut, car c'est le tout premier flip du d�but du jeu.
        pygame.display.flip()

        #chargement de toute les autres images (avec key transparency).
        dicImg = loadImgInDict(LIST_FILENAME_IMG_PREZ)
        #rangement dans le dico de l'imagede background d�j� charg�e plus haut.
        dicImg[IMG_BACKGROUND] = imgBackground

        # -- construction de la liste d'images agrandies du titre "Blarg" --
        #on commence par une image tr�s tr�s agrandie, pour finir sur une image normale.

        #liste des tailles d'agrandissement relatives. On ira d'un agrandissement 7 fois
        #jusqu'� un agrandissement 1,4 fois
        listIntScaleRel = range(70, 10, -4)
        listScaleRel = [ scale / 10.0 for scale in listIntScaleRel ]
        #ajout, en fin de liste, de l'agrandissement 1 fois. C'est plus s�curitable de
        #l'ajouter comme �a plut�t que de l'avoir mis dans la liste de d�part, en
        #priant pour que les divers calculs matheux tombent juste et qu'on retombe sur 1.
        listScaleRel.append(1)

        titleWidth, titleHeight = dicImg[IMG_TITLE].get_size()

        #cr�ation de la liste des tailles absolues, sous forme de couple (width, height).
        listSizeScaled = [ (int(titleWidth * scale), int(titleHeight * scale))
                           for scale in listScaleRel
                         ]

        #cr�ation des image agrandies, � partir de la liste des tailles absolues.
        listImgTitleScaled = [ pygame.transform.scale(dicImg[IMG_TITLE], size)
                               for size in listSizeScaled ]

        #cr�ation de la liste des positions (X, Y) du coin sup�rieur-gauche es images agrandies.
        #les images doivent �tre centr�e horizontalement sur l'abscisse X = 210.
        #Le bas de la premi�re image se trouve � l'ordonn�e Y=30,
        #le bas des images suivantes descend de 2 en 2.
        listPosImgTitle = [ (210 - width/2, 30 + offsetY*2 - height)
                            for offsetY, (width, height)
                            in enumerate(listSizeScaled)
                          ]

        #nombre de Frame Par Seconde de l'animation
        animFPS = 55
        #classe pour g�rer toute seule le FPS.
        clock = pygame.time.Clock()

        #position de d�part du magicien. Il est � droite de l'�cran, mais pas compl�tement.
        #Le bas du magicien est en bas de l'�cran.
        posMagi = pyRect(SCREEN_RECT.width - 9,
                         SCREEN_RECT.height - dicImg[IMG_MAGI].get_height())

        #position de d�part du h�ros. Il est � gauche de l'�cran. Le bas est au bas de l'�cran.
        posHero = pyRect(-255,
                         SCREEN_RECT.height - dicImg[IMG_HERO].get_height())

        #curseur parcourant la liste des images et la liste des position du titre "Blarg".
        cursorImgTitle = 0

        #chargement de tous les sons. Paf, comme �a cash. Ouais, on le fait l�,
        #c'est un peu zarb. Voir explication dans le __init__ de mainclas.py
        #TRODO pour plus tard : charger maintenant les premiers sons utiles (ceux de la prez),
        #Et charger les suivants pendant la prez, petit � petit. Ca fera un loading moins long.
        theSoundYargler.loadAllSounds()

        # --- grosse boucle d�crivant tous les mouvements d'image de l'anim de pr�sentation ---

        for animCounter in xrange(40):

            #gestion du nombre de FPS, avec la classe toute faite "sur �tag�re". Haha.
            clock.tick(animFPS)

            #on y va bourrin. On reblitte l'image de fond int�gralement, � chaque fois.
            #C'est plus lent, mais osef. C'est une anim, il ne se passe rien d'autre que �a.
            self.screen.blit(dicImg[IMG_BACKGROUND], (0, 0))

            #blittage du magicien et du h�ros, � leur position courante.
            self.screen.blit(dicImg[IMG_MAGI], posMagi)
            self.screen.blit(dicImg[IMG_HERO], posHero)

            # -- gestion des divers mouvements des images. Un peu d�gueu, mais osef --

            #au d�but, le magicien bouge assez rapidement vers la gauche, (de 10 en 10),
            #et quand il voit arriver le h�ros, il se recule un peu (de 2 en 2)
            if animCounter < 13:
                posMagi.move_ip(-10, 0)
            elif 14 < animCounter < 17:
                posMagi.move_ip( +2, 0)

            #le h�ros avance rapidement vers la droite (de 15 en 15)
            if animCounter < 17:
                posHero.move_ip(+15, 0)

            #le titre n'est pas visible au d�but. Il appara�t apr�s 20 cycles.
            if animCounter > 20:

                #tant qu'on n'est pas � la fin de la liste, on avance le curseur.
                #Et on prend � chaque fois l'image agrandie courante, et la position qui va avec.
                if cursorImgTitle < len(listPosImgTitle):
                    imgTitle = listImgTitleScaled[cursorImgTitle]
                    postitle = listPosImgTitle[cursorImgTitle]
                    cursorImgTitle += 1

                #Affichage de l'image. Lorsque cursorImgTitle est arriv� au bout de la liste,
                #on se retrouve � afficher, � chaque cycle, la m�me image (non agrandie),
                #� la m�me position. Et c'est cool, c'est ce qu'on veut.
                self.screen.blit(imgTitle, postitle)

            if animCounter == 37:
                #son de pr�sentation : "blarg" !!
                theSoundYargler.playSound(SND_PREZ_BLARG)

            #gros flip global � chaque cycle. Bourrin et lent, mais osef, c'est qu'une anim.
            pygame.display.flip()


        # --- Voil�, c'est la fin de l'animation. Youpi ---

        #Cr�ation de l'image qui sera le background du menu principal.
        #Pour �a, on prend l'image actuellement affich�e � l'�cran, et on l'assombris fortement.
        #Ce qui fait que j'acc�de en lecture � self.screen, la Surface sp�ciale utilis�e
        #pour l'affichage � l'�cran. Est-ce bien ou mal ? Jusqu'ici, �a fonctionne.
        #(Y'a des risques de foirage si on utilise une acc�l�ration mat�rielle, ou je sais
        #pas quoi. Mais bon, je fais pas ce genre de chose.)
        self.imgBgMainMenu = pixTranspLight(self.screen, 0, 180)

        #conservation en m�moire de l'image du titre. Il suffit de l'enregistrer comme
        #membre de la classe. Et comme la classe est conserv�e en m�moire. C'est bon.
        #C'est une mani�re de faire un peu "hop hop � l'arrache", mais c'est pas grave.
        self.imgTitle = dicImg[IMG_TITLE]

        #re-affichage du curseur de souris. Que le joueur puisse cliquouiller dans les menus.
        pygame.mouse.set_visible(1)

        #Maintenant, on s'en va. Et donc le code ext�rieur pourra r�cup�rer self.imgBgMainMenu
        #et self.imgTitle. (Oui je l'ai d�j� dit 3 fois. Mais j'ai toujours peu de pas �tre
        #compr�hensible quand j'explique des trucs. Y compris pour moi m�me quand je me relis).
