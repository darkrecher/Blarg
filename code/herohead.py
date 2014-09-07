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

la classe pour g�rer le sprite qui affiche la t�te du h�ros.

BIG BIG TRODO : faire une classe commune aux sprites, avec tout �a dedans.
Lorsqu'on aura g�r� mieux que �a les changements d'image avec des hotpoint.
A faire pour la version 2. L�, pas envie.

pour l'instant, c'est du copier-coller de herobody avec moins de trucs dedans. C'est mal.
"""

import pygame

from common import NONE_COUNT, pyRect, oppRect

#liste des identifieurs d'images de la t�te du h�ros.
(IMG_NORMAL_RIGHT,
 IMG_SMILING,
 IMG_NORMAL_LEFT,
) = range(3)

#pr�fixe dans les noms de fichiers image de la tayte du h�ros.
IMG_FILENAME_PREFIX = "hhed"

#liste de tuple de 2 elements. Correspondance entre l'identifieur de l'image
#et le nom court du fichier contenant l'image.
#pour trouver le nom entier du fichier : "hhed" + <nom court> + ".png"
#y'a pas le IMG_NORMAL_LEFT. Car on cr�e cette image par sym�trie, � partir de IMG_NORMAL_RIGHT
LIST_IMG_FILE_SHORT_NAME = (
 (IMG_NORMAL_RIGHT,  "norm"),
 (IMG_SMILING, "smil"),
)

#temps (nombre de cycle) durant lequel le h�ros sourit, quand on lui envoie un stimuli
#de sourissage. (c'est � dire quand il a explos� un magicien)
TIME_SMILING = 150

DECAL_NORMRIGHT_NORMLEFT = pyRect(+5, 0)
DECAL_NORMLEFT_NORMRIGHT = oppRect(DECAL_NORMRIGHT_NORMLEFT)

#dictionnaire indiquant comment tourner la t�te.
# - cl� : identifiant de l'image initiale
# - valeur : tuple de 2 elem :
#            * identifiant de l'image correspondant � la t�te tourn�e
#            * rect (X, Y) de d�calage � appliquer suite au tournage de t�te.
DICT_TURNING_INFO = {
 IMG_NORMAL_RIGHT : (IMG_NORMAL_LEFT,  DECAL_NORMRIGHT_NORMLEFT),
 IMG_NORMAL_LEFT  : (IMG_NORMAL_RIGHT, DECAL_NORMLEFT_NORMRIGHT),
 #pas de tournage de tete quand le h�ros est en smiling. Pas pr�vu. Pas besoin. osef.
}

def preRenderFlippedHeadLeftRight(dicHeroHeadImg):
    """
    calcule l'image de la t�te tourn�e vers la gauche, en renversant l'image
    de la t�te tourn�e vers la droite, et la range dans le dico des images.

    entr�es :
        dicHeroHeadImg : dictionnaire (identifiant d'image -> image),
                         contenant au moins l'image IMG_NORMAL_RIGHT

    plat-dessert : rien du tout. La fonction modifie en place le dictionnaire.
                   Elle ajoute une image ayant l'identifiant IMG_NORMAL_LEFT
    """

    #G�n�ration d'une image renvers�e horizontalement, � partir de l'image IMG_NORMAL_RIGHT
    #WTF is this shit ? Si j'ex�cute la fonction flip en indiquant les param�tres
    #avec leur nom : xbool = True, ybool = False : je me prends un message d'erreur pourri :
    # TypeError: flip() takes no keyword arguments
    imgHeadLeft = pygame.transform.flip(dicHeroHeadImg[IMG_NORMAL_RIGHT],
                                        True, False)

    #rangement de l'image g�n�r�e dans le dictionnaire.
    dicHeroHeadImg[IMG_NORMAL_LEFT] = imgHeadLeft



class HeroHead(pygame.sprite.Sprite):
    """
    le sprite qui est la t�te du heros
    """

    def __init__(self, dicHeroHeadImg, posStart):
        """
        constructeur. (thx captain obvious)

        entr�e :
            dicHeroHeadImg : dictionnaire de correspondance
                             identifiant d'image -> image
                             il est cens� contenir toutes les images n�cessaires, y compris
                             l'image de la t�te tourn�e vers la gauche (IMG_NORMAL_LEFT)
            posStart       : rect. position du coin superieur gauche du sprite, � l'�cran.
        """
        pygame.sprite.Sprite.__init__(self)
        self.dicHeroHeadImg = dicHeroHeadImg

        #initialisation de l'image du sprite, avec la t�te normale, tourn�e vers la droite.
        self.changeImg(IMG_NORMAL_RIGHT)

        #la taille du sprite (pour les collisions) c'est la taille de son image
        #c'est pas syst�matiquement exact. par exemple si y'a un bout qui d�passe mais qu'est pas
        #cens� collisionner, genre une m�che de cheveux, faudrait le g�rer autrement. l�, osef.
        #De plus, la taille du sprite n'est pas r�actualis�e quand on change l'image.
        #osef une fois de plus, car toutes les images de la t�te ont la m�me taille.
        spriteSize = self.image.get_size()
        self.rect = pygame.Rect(posStart.topleft + spriteSize)

        #compteur utilis� lorsque le h�ros fait un sourire. L�, il sourit pas, donc on compte pas.
        self.counterSmiling = NONE_COUNT


    def changeImg(self, imgIdNew):
        """
        change l'image du corps du h�ros

        entr�e :
          imgIdNew   : identifiant de la nouvelle image � afficher.

        pas de d�calage. osef. en tout cas, pas dans cette fonction
        TRODO : C mal, je devrais factoriser ce bordel. d�j� dit.
        """
        self.currentImgId = imgIdNew
        self.image = self.dicHeroHeadImg[imgIdNew]


    def update(self):
        """
        Update du sprite. Fonction � ex�cuter � chaque cycle.

        Y'a qu'un seul truc � g�rer dans cette fonction : le comptage pour arr�ter
        de sourire, si le h�ros est en train de sourire.
        """

        if self.counterSmiling is not NONE_COUNT:

            #on est en cours de "smiling". Il faut d�compter le temps restant avant
            #le retour � la tronche normale
            self.counterSmiling -= 1

            if self.counterSmiling == 0:
                self.stopSmiling()


    def startSmiling(self):
        """
        d�marre un sourire. Cheeeeese !!!
        """

        #On change l'image de la t�te du h�ros pour mettre l'image qui sourit.
        self.changeImg(IMG_SMILING)
        #initialisation du compteur de sourissage
        self.counterSmiling = TIME_SMILING


    def stopSmiling(self):
        """
        arr�te de sourire. Chuuuuuse.
        """

        #on arr�te de sourire et on remet la t�te � l'image normale.
        self.changeImg(IMG_NORMAL_RIGHT)
        #arr�t du comptage de smiling.
        self.counterSmiling = NONE_COUNT


    def turnHead(self):
        """
        tourne la t�te du h�ros. Si le h�ros regarde vers la gauche, il regardera vers
        la droite, et vice-versa.

        D�j� dit, mais la t�te tourne pas si le h�ros est en train de sourire.
        C'est pas pr�vu de lancer la fonction turnHead pendant un smiling
        """

        #r�cup�ration de la nouvelle image de la t�te tourn�e, et du d�calage � appliquer
        #� la position du sprite, en fonction de l'image actuelle de la t�te.
        #On se chope des None si le dico ne contient pas ces infos pour l'img actuelle.
        (imgIdTurned, rectDecalage) = DICT_TURNING_INFO.get(self.currentImgId,
                                                            (None, None))

        if imgIdTurned is not None:
            #le dico de tournage de t�te contient bien la correspondance.
            #On peut faire tourner la t�te : Application du d�alage et changement de l'image.
            self.rect.move_ip(rectDecalage.topleft)
            self.changeImg(imgIdTurned)
