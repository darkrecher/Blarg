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

date de la dern�re relecture-commentage : 11/10/2010

la classe pour g�rer le sprite qui affiche le corps du h�ros.
"""

import pygame

from common import pyRect

#BIG TRODO
#Pour l'instant on s'en sert pas de ces trucs, ici.
#Quand je rangerais les trucs comme il faut, c'est le heroBody
#qui g�rera les d�calages. Pour l'instant c'est le bordel
#DECAL_NORM_RAISE1   = (+3, -1)
#DECAL_RAISE1_RAISE2 = (+1, -5)
#DECAL_RAISE2_ARM    = ( 0, +1)
#pour la version 2

#meme d�calae mais oppos�
#DECAL_RAISE2_RAISE1 = (-DECAL_RAISE1_RAISE2[0], -DECAL_RAISE1_RAISE2[1])
#DECAL_RAISE1_NORM   = (-DECAL_NORM_RAISE1[0],   -DECAL_NORM_RAISE1[1])
#DECAL_ARM_RAISE2    = (-DECAL_RAISE2_ARM[0],    -DECAL_RAISE2_ARM[1])

#liste des identifieurs d'images du corps du h�ros.
(IMG_NORMAL,
 IMG_RAISE_A,
 IMG_RAISE_B,
 IMG_ARMINGE,
 IMG_RELOAD_A,
 IMG_RELOAD_B,
 IMG_HURT,
) = range(7)

#pr�fixe dans les noms de fichiers image du corps du h�ros.
IMG_FILENAME_PREFIX = "h"

#liste de tuple de 2 elements. Correspondance entre l'identifieur de l'image
#et le nom court du fichier contenant l'image.
#pour trouver le nom entier du fichier : "h" + <nom court> + ".png"
LIST_IMG_FILE_SHORT_NAME = (
 (IMG_NORMAL,      "norm"),
 (IMG_RAISE_A,     "leva"),
 (IMG_RAISE_B,     "levb"),
 (IMG_ARMINGE,     "arminge"),
 (IMG_RELOAD_A,    "rcharga"),
 (IMG_RELOAD_B,    "rchargb"),
 (IMG_HURT,        "hurt"),
)

#je partage pas moi. Je partage jamais rien. Parce que j'en ai pas envie.
#je fais ce que je veux.



class HeroBody(pygame.sprite.Sprite):
    """
    le sprite qui est le corps du heros
    """

    def __init__(self, dicHeroBodyImg, posStart):
        """
        constructeur. (thx captain obvious)

        entr�e :
            dicHeroBodyImg : dictionnaire de correspondance
                             identifiant d'image -> image
            posStart       : rect. position du coin superieur gauche du sprite, � l'�cran.
        """
        pygame.sprite.Sprite.__init__(self)
        self.dicHeroBodyImg = dicHeroBodyImg

        #initialisation de l'image du sprite, avec le corps normal.
        self.image = dicHeroBodyImg[IMG_NORMAL]

        #la taille du sprite (pour les collisions), c'est la taille de l'image
        #c'est pas syst�matiquement exact. par exemple si y'a un bout qui d�passe mais qu'est pas
        #cens� collisionner, genre un bout de fusil, faudrait le g�rer autrement. l�, osef.
        #De plus, la taille du sprite n'est pas r�actualis�e quand on change l'image.
        #osef une fois de plus, car toutes les images du corps ont � peu pr�s la m�me taille.
        spriteSize = self.image.get_size()
        self.rect = pygame.Rect(posStart.topleft + spriteSize)


    def changeImg(self, imgIdNew, rectOffset=None):
        """
        change l'image de la t�te du h�ros

        entr�e :
          imgIdNew   : identifiant de la nouvelle image � afficher.
          rectOffset : None, ou un rect.
                       Si rect : c'est le d�calage � appliquer au sprite
                       pour pas que le corps du h�ros bouge stupidement.
                       (gestion � l'arrache des hotPoint d'images de sprite)
        """

        self.image = self.dicHeroBodyImg[imgIdNew]

        if rectOffset is not None:
            self.rect.move_ip(rectOffset.topleft)

