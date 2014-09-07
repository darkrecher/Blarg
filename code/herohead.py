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

date de la dernère relecture-commentage : 11/10/2010

la classe pour gérer le sprite qui affiche la tête du héros.

BIG BIG TRODO : faire une classe commune aux sprites, avec tout ça dedans.
Lorsqu'on aura géré mieux que ça les changements d'image avec des hotpoint.
A faire pour la version 2. Là, pas envie.

pour l'instant, c'est du copier-coller de herobody avec moins de trucs dedans. C'est mal.
"""

import pygame

from common import NONE_COUNT, pyRect, oppRect

#liste des identifieurs d'images de la tête du héros.
(IMG_NORMAL_RIGHT,
 IMG_SMILING,
 IMG_NORMAL_LEFT,
) = range(3)

#préfixe dans les noms de fichiers image de la tayte du héros.
IMG_FILENAME_PREFIX = "hhed"

#liste de tuple de 2 elements. Correspondance entre l'identifieur de l'image
#et le nom court du fichier contenant l'image.
#pour trouver le nom entier du fichier : "hhed" + <nom court> + ".png"
#y'a pas le IMG_NORMAL_LEFT. Car on crée cette image par symétrie, à partir de IMG_NORMAL_RIGHT
LIST_IMG_FILE_SHORT_NAME = (
 (IMG_NORMAL_RIGHT,  "norm"),
 (IMG_SMILING, "smil"),
)

#temps (nombre de cycle) durant lequel le héros sourit, quand on lui envoie un stimuli
#de sourissage. (c'est à dire quand il a explosé un magicien)
TIME_SMILING = 150

DECAL_NORMRIGHT_NORMLEFT = pyRect(+5, 0)
DECAL_NORMLEFT_NORMRIGHT = oppRect(DECAL_NORMRIGHT_NORMLEFT)

#dictionnaire indiquant comment tourner la tête.
# - clé : identifiant de l'image initiale
# - valeur : tuple de 2 elem :
#            * identifiant de l'image correspondant à la tête tournée
#            * rect (X, Y) de décalage à appliquer suite au tournage de tête.
DICT_TURNING_INFO = {
 IMG_NORMAL_RIGHT : (IMG_NORMAL_LEFT,  DECAL_NORMRIGHT_NORMLEFT),
 IMG_NORMAL_LEFT  : (IMG_NORMAL_RIGHT, DECAL_NORMLEFT_NORMRIGHT),
 #pas de tournage de tete quand le héros est en smiling. Pas prévu. Pas besoin. osef.
}

def preRenderFlippedHeadLeftRight(dicHeroHeadImg):
    """
    calcule l'image de la tête tournée vers la gauche, en renversant l'image
    de la tête tournée vers la droite, et la range dans le dico des images.

    entrées :
        dicHeroHeadImg : dictionnaire (identifiant d'image -> image),
                         contenant au moins l'image IMG_NORMAL_RIGHT

    plat-dessert : rien du tout. La fonction modifie en place le dictionnaire.
                   Elle ajoute une image ayant l'identifiant IMG_NORMAL_LEFT
    """

    #Génération d'une image renversée horizontalement, à partir de l'image IMG_NORMAL_RIGHT
    #WTF is this shit ? Si j'exécute la fonction flip en indiquant les paramètres
    #avec leur nom : xbool = True, ybool = False : je me prends un message d'erreur pourri :
    # TypeError: flip() takes no keyword arguments
    imgHeadLeft = pygame.transform.flip(dicHeroHeadImg[IMG_NORMAL_RIGHT],
                                        True, False)

    #rangement de l'image générée dans le dictionnaire.
    dicHeroHeadImg[IMG_NORMAL_LEFT] = imgHeadLeft



class HeroHead(pygame.sprite.Sprite):
    """
    le sprite qui est la tête du heros
    """

    def __init__(self, dicHeroHeadImg, posStart):
        """
        constructeur. (thx captain obvious)

        entrée :
            dicHeroHeadImg : dictionnaire de correspondance
                             identifiant d'image -> image
                             il est censé contenir toutes les images nécessaires, y compris
                             l'image de la tête tournée vers la gauche (IMG_NORMAL_LEFT)
            posStart       : rect. position du coin superieur gauche du sprite, à l'écran.
        """
        pygame.sprite.Sprite.__init__(self)
        self.dicHeroHeadImg = dicHeroHeadImg

        #initialisation de l'image du sprite, avec la tête normale, tournée vers la droite.
        self.changeImg(IMG_NORMAL_RIGHT)

        #la taille du sprite (pour les collisions) c'est la taille de son image
        #c'est pas systématiquement exact. par exemple si y'a un bout qui dépasse mais qu'est pas
        #censé collisionner, genre une mèche de cheveux, faudrait le gérer autrement. là, osef.
        #De plus, la taille du sprite n'est pas réactualisée quand on change l'image.
        #osef une fois de plus, car toutes les images de la tête ont la même taille.
        spriteSize = self.image.get_size()
        self.rect = pygame.Rect(posStart.topleft + spriteSize)

        #compteur utilisé lorsque le héros fait un sourire. Là, il sourit pas, donc on compte pas.
        self.counterSmiling = NONE_COUNT


    def changeImg(self, imgIdNew):
        """
        change l'image du corps du héros

        entrée :
          imgIdNew   : identifiant de la nouvelle image à afficher.

        pas de décalage. osef. en tout cas, pas dans cette fonction
        TRODO : C mal, je devrais factoriser ce bordel. déjà dit.
        """
        self.currentImgId = imgIdNew
        self.image = self.dicHeroHeadImg[imgIdNew]


    def update(self):
        """
        Update du sprite. Fonction à exécuter à chaque cycle.

        Y'a qu'un seul truc à gérer dans cette fonction : le comptage pour arrêter
        de sourire, si le héros est en train de sourire.
        """

        if self.counterSmiling is not NONE_COUNT:

            #on est en cours de "smiling". Il faut décompter le temps restant avant
            #le retour à la tronche normale
            self.counterSmiling -= 1

            if self.counterSmiling == 0:
                self.stopSmiling()


    def startSmiling(self):
        """
        démarre un sourire. Cheeeeese !!!
        """

        #On change l'image de la tête du héros pour mettre l'image qui sourit.
        self.changeImg(IMG_SMILING)
        #initialisation du compteur de sourissage
        self.counterSmiling = TIME_SMILING


    def stopSmiling(self):
        """
        arrête de sourire. Chuuuuuse.
        """

        #on arrête de sourire et on remet la tête à l'image normale.
        self.changeImg(IMG_NORMAL_RIGHT)
        #arrêt du comptage de smiling.
        self.counterSmiling = NONE_COUNT


    def turnHead(self):
        """
        tourne la tête du héros. Si le héros regarde vers la gauche, il regardera vers
        la droite, et vice-versa.

        Déjà dit, mais la tête tourne pas si le héros est en train de sourire.
        C'est pas prévu de lancer la fonction turnHead pendant un smiling
        """

        #récupération de la nouvelle image de la tête tournée, et du décalage à appliquer
        #à la position du sprite, en fonction de l'image actuelle de la tête.
        #On se chope des None si le dico ne contient pas ces infos pour l'img actuelle.
        (imgIdTurned, rectDecalage) = DICT_TURNING_INFO.get(self.currentImgId,
                                                            (None, None))

        if imgIdTurned is not None:
            #le dico de tournage de tête contient bien la correspondance.
            #On peut faire tourner la tête : Application du déalage et changement de l'image.
            self.rect.move_ip(rectDecalage.topleft)
            self.changeImg(imgIdTurned)
