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

date de la dernère relecture-commentage : 08/10/2010

la classe pour gérer les collisions entre les magiciens et les balles (bullets) du héros.

Cette classe calcule la trajectoire de chaque bullet, contrôle si elles collisionnent un
magicien, et transmet les infos nécessaires aux magiciens et au héros en fonction
des collisions trouvées.

---
Explication vaguement exacte du cycle de vie d'un enfoiré de magicien.
---

Les états d'un magicien évoluent dans cet ordre :

APPEARING   ->    ALIVE / HURT    ->   DYING / BURSTING    ->    DEAD

Le CollHandlerBulletMagi possède une référence vers la liste de tous les magiciens.

Le héros possède une référence vers le CollHandlerBulletMagi.
C'est le héros qui exécute la fonction CollHandlerBulletMagi.HeroFiresBullets, en spécifiant
les coordonnées d'où il tire.

Le héros tire trois bullets d'un coup,
 - une qui va horizontalement vers la droite,
 - une qui va vers la droite un peu en haut,
 - une qui va vers la droite un peu en bas.

La fonction HeroFiresBullets calcule ces trois trajectoires, et regarde quelles bullets
se collisionnent avec quelles magiciens. Si plusieurs bullets vont sur le même magicien,
la fonction doit le détecter et les additionner

Le déplacement des bullets est instantané. Dès qu'ils sont tirés, on regarde tout de
suite si ils se collisionnent. C'est pas des objets qui se déplacent au fur à mesure du temps.
(je trouve ça plus cool comme ça)

Ensuite, pour chaque magicien s'étant pris une/des bullets, la fonction exécute
Magician.hitByBullet(Damage)

Au départ, le magicien est APPRARING (animation à la con d'apparition du magicen),
puis au bout de quelques cycles, il est ALIVE

Quand il se fait toucher, le magicien va en déduire si il reste vivant (etat=HURT),
si il crève (etat=DYING), ou si il explose (etat=BURSTING).
Et il renvoie son état courant à la fonction HeroFiresBullets.

Quand un magicien est HURT, il peut faire certains trucs cools : s'immobiliser, bouger vers
la droite car il se prend du recul dans la gueule, ... Mais au bout d'un moment,
il revient à l'état ALIVE.

Un magicien est DYING quand il n'a plus de points de vie. (Il fait son anim de mourage)

Un magicien explose (BURSTING) quand il se prend trois bullets d'un coup.

La fonction HeroFiresBullets comptabilise le nombre de magiciens tués et le nombre explosés.
Elle renvoie tout ça au héros, qui l'additionne dans ses scores personnels.

Lorsqu'un magicien est DYING ou BURSTING, il se fait tout seul son animation de mourage.
Quand il a fini, il se met dans l'état DEAD.
La boucle principale du jeu (dans game.py), s'occupe de supprimer l'objet Magicien
et de l'effacer de la liste des sprites et de la liste des magiciens. Haha.

(putain de connard de gamin dans le car, ils vont me péter mon ordinateur.
C'est bon. Approche positive et donc il rigole et touche pas à ma machine chérie.
y'a juste qu'ils me déconcentrent ces petits cons.
Ah c'est bon ils se battent entre eux c'est nickel.)
"""

import pygame

from common import GAME_RECT, pyRect

from movpoint import (MOVE_ON_X, MOVE_ON_Y, MOVE_NONE,
                      calculateListTotalMove, MovingPoint)

import magician

#les trajectoire des bullets sont calculés avec des classes MovingPoint

#mouvement principal d'une bullet (vers la droite)
BULLET_MAIN_MOVE = pyRect(+1, 0)
#le mouvement secondaire est sur la coordonnée Y.
BULLET_INDEX_SEC_MOVE = MOVE_ON_Y

#les trois listes de mouvement secondaire de chacune des trois bullets
BULLET_LIST_SEC_MOVE_UP       = (0, 0, 0, 0, -1)  #un peu vers le haut
BULLET_LIST_SEC_MOVE_DOWN     = (0, 0, 0, 0, +1)  #un peu vers le bas
BULLET_LIST_SEC_MOVE_STRAIGHT = (0, )             #pas de sec move, donc la bullet ira tout droit.

#liste avec ces trois listes de mouvements secondaires.
LIST_BULLET_LIST_SEC_MOVE = (BULLET_LIST_SEC_MOVE_UP,
                             BULLET_LIST_SEC_MOVE_STRAIGHT,
                             BULLET_LIST_SEC_MOVE_DOWN
                            )

#précalcul des listTotalMove des trois bullets, à partir du mouvements primaire et des
#trois mouvements secondaires définis ci-dessus. (voir classe movpoint.py)
LIST_BULLET_LIST_TOTAL_MOVE = tuple(
    [
        calculateListTotalMove(BULLET_MAIN_MOVE, bulletListSecMove,
                               BULLET_INDEX_SEC_MOVE)

        for bulletListSecMove in LIST_BULLET_LIST_SEC_MOVE
    ])

#liste des états du magicien dans lesquels on le fera collisionner avec les bullets
#dans les autres états (APPEARING, DYING, BURSTING, ...) les bullets lui passent au travers.
LIST_MAGI_STATE_COLLIDES = ( magician.HURT, magician.ALIVE )


class CollHandlerBulletMagi():
    """
    la classe qui tralala. Voir début du fichier.
    """

    def __init__(self, listMagician):
        """
        constructeur. (thx captain obvious)

        entrée :
            listMagician : référence vers la liste des magiciens
                           dans le jeu. Le contenu de la liste évolue en live,
                           Le CollHandlerBulletMagi se contente de consulter cette liste.
        """
        self.listMagician = listMagician


    def heroFiresBullets(self, posFire):
        """
        fonction à exécuter lorsque le héros tire un coup de flingue.

        entrée :
          posFire : rect(X,Y) indiquant les coordonnées de départ du coup de feu
                    (c'est pas les coordonnées du héros, c'est les coordonnées du
                     bout du flingue du héros)

        plat-dessert :
          un tuple de deux int.
           - nombre de magiciens explosés par le tir
           - nombre de magiciens tués par le tir

        Cette fonction ne détermine pas directement le nombre de magicien tués et explosés.
        Ce sont les instances de magicien qui font cela.
        """

        #dictionnaire indiquant les magiciens touchés par une/des bullets.
        #clé : référence vers l'instance de magicien touché
        #valeur : nombre de bullets de ce tir qui l'ont touché en même temps.
        dicMagicianHit = {}

        # --- remplissage de dicMagicianHit ---

        for bulletListTotalMove in LIST_BULLET_LIST_TOTAL_MOVE:

            #on gère complètement la trajectoire de chaque bullet, l'une après l'autre.

            #création d'un movingPoint représentant la bullet, avec sa listTotalMove
            #qu'on a calculé précédemment
            bullet = MovingPoint(posFire, listTotalMove=bulletListTotalMove)

            isBulletActive = True

            while isBulletActive:

                #on fait avancer le movingPoint représentant la bullet. Dès que ça cogne dans
                #un truc ou que ça sort de l'écran, on la désactive.

                #on parcourt la liste des magiciens et on voit si y'a collision.
                #avec une boucle comme ça, une bullet peut toucher plusieurs magiciens
                #en même temps, si ils se trouvent pile poil à la même abscisse
                #moi ça me choque pas et je trouve ça cool. C'est fait exprès.
                for Magician in self.listMagician:

                    if Magician.currentState in LIST_MAGI_STATE_COLLIDES and \
                       Magician.rect.collidepoint(bullet.topleft):

                        #y'a une collision avec un magicien

                        #désactivation de la bullet. Elle ne fera pas plus de mouvement,
                        #mais on continue quand même de parcourir toute la liste des magiciens,
                        #pour détecter d'autres collisions.
                        isBulletActive = False

                        if Magician in dicMagicianHit:
                            #le magicien est déjà dans le dico dicMagicianHit.
                            #il est déjà touché par au moins une bullet.
                            #on le laisse dans le dico, et on ajoute une bullet de plus
                            #à la valeur.
                            dicMagicianHit[Magician] += 1
                        else:
                            #le magicien n'est pas dans le dico dicMagicianHit
                            #il n'a pas encore été touché par une bullet.
                            #on l'ajoute dans le dico, avec la valeur 1 (une bullet)
                            dicMagicianHit[Magician] = 1

                #pas de collision. On avance la bullet de un pas, selon sa direction prédefinie
                bullet.advanceOneStep()

                if not GAME_RECT.collidepoint(bullet.topleft):
                    #la bullet n'est plus en collision avec le gros rect
                    #représentant l'aire de jeu. Donc elle est sortie de l'écran.
                    #on la vire, et la boucle passera à la bullet suivante
                    isBulletActive = False

        #nombre de magicien burst par ce tir
        nbrMagicianBurst = 0
        #nombre de magicien tué (sans burst) par ce tir
        nbrMagicianKilledNotBurst = 0

        for Magician, Damage in dicMagicianHit.items():

            #pour chaque magicien touché, on le prévient qu'il s'est fait touché
            #en lui indiquant le nombre de bullet qui l'a atteint simultanément (c.a.d. : Damage)
            magicianState = Magician.hitByBullet(Damage)

            #le magicien prend en compte le Hit, et renvoie son état.
            #Si il s'est fait tué ou explosé, on augmente le compteur correspondant.
            if magicianState in [magician.DYING, magician.DEAD]:
                nbrMagicianKilledNotBurst += 1
            elif magicianState == magician.BURSTING:
                nbrMagicianBurst += 1

        #on renvoie les deux compteurs.
        #le héros récupère ces valeurs et les additionne à ses scores
        return (nbrMagicianBurst, nbrMagicianKilledNotBurst)


