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

date de la dern�re relecture-commentage : 08/10/2010

la classe pour g�rer les collisions entre les magiciens et les balles (bullets) du h�ros.

Cette classe calcule la trajectoire de chaque bullet, contr�le si elles collisionnent un
magicien, et transmet les infos n�cessaires aux magiciens et au h�ros en fonction
des collisions trouv�es.

---
Explication vaguement exacte du cycle de vie d'un enfoir� de magicien.
---

Les �tats d'un magicien �voluent dans cet ordre :

APPEARING   ->    ALIVE / HURT    ->   DYING / BURSTING    ->    DEAD

Le CollHandlerBulletMagi poss�de une r�f�rence vers la liste de tous les magiciens.

Le h�ros poss�de une r�f�rence vers le CollHandlerBulletMagi.
C'est le h�ros qui ex�cute la fonction CollHandlerBulletMagi.HeroFiresBullets, en sp�cifiant
les coordonn�es d'o� il tire.

Le h�ros tire trois bullets d'un coup,
 - une qui va horizontalement vers la droite,
 - une qui va vers la droite un peu en haut,
 - une qui va vers la droite un peu en bas.

La fonction HeroFiresBullets calcule ces trois trajectoires, et regarde quelles bullets
se collisionnent avec quelles magiciens. Si plusieurs bullets vont sur le m�me magicien,
la fonction doit le d�tecter et les additionner

Le d�placement des bullets est instantan�. D�s qu'ils sont tir�s, on regarde tout de
suite si ils se collisionnent. C'est pas des objets qui se d�placent au fur � mesure du temps.
(je trouve �a plus cool comme �a)

Ensuite, pour chaque magicien s'�tant pris une/des bullets, la fonction ex�cute
Magician.hitByBullet(Damage)

Au d�part, le magicien est APPRARING (animation � la con d'apparition du magicen),
puis au bout de quelques cycles, il est ALIVE

Quand il se fait toucher, le magicien va en d�duire si il reste vivant (etat=HURT),
si il cr�ve (etat=DYING), ou si il explose (etat=BURSTING).
Et il renvoie son �tat courant � la fonction HeroFiresBullets.

Quand un magicien est HURT, il peut faire certains trucs cools : s'immobiliser, bouger vers
la droite car il se prend du recul dans la gueule, ... Mais au bout d'un moment,
il revient � l'�tat ALIVE.

Un magicien est DYING quand il n'a plus de points de vie. (Il fait son anim de mourage)

Un magicien explose (BURSTING) quand il se prend trois bullets d'un coup.

La fonction HeroFiresBullets comptabilise le nombre de magiciens tu�s et le nombre explos�s.
Elle renvoie tout �a au h�ros, qui l'additionne dans ses scores personnels.

Lorsqu'un magicien est DYING ou BURSTING, il se fait tout seul son animation de mourage.
Quand il a fini, il se met dans l'�tat DEAD.
La boucle principale du jeu (dans game.py), s'occupe de supprimer l'objet Magicien
et de l'effacer de la liste des sprites et de la liste des magiciens. Haha.

(putain de connard de gamin dans le car, ils vont me p�ter mon ordinateur.
C'est bon. Approche positive et donc il rigole et touche pas � ma machine ch�rie.
y'a juste qu'ils me d�concentrent ces petits cons.
Ah c'est bon ils se battent entre eux c'est nickel.)
"""

import pygame

from common import GAME_RECT, pyRect

from movpoint import (MOVE_ON_X, MOVE_ON_Y, MOVE_NONE,
                      calculateListTotalMove, MovingPoint)

import magician

#les trajectoire des bullets sont calcul�s avec des classes MovingPoint

#mouvement principal d'une bullet (vers la droite)
BULLET_MAIN_MOVE = pyRect(+1, 0)
#le mouvement secondaire est sur la coordonn�e Y.
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

#pr�calcul des listTotalMove des trois bullets, � partir du mouvements primaire et des
#trois mouvements secondaires d�finis ci-dessus. (voir classe movpoint.py)
LIST_BULLET_LIST_TOTAL_MOVE = tuple(
    [
        calculateListTotalMove(BULLET_MAIN_MOVE, bulletListSecMove,
                               BULLET_INDEX_SEC_MOVE)

        for bulletListSecMove in LIST_BULLET_LIST_SEC_MOVE
    ])

#liste des �tats du magicien dans lesquels on le fera collisionner avec les bullets
#dans les autres �tats (APPEARING, DYING, BURSTING, ...) les bullets lui passent au travers.
LIST_MAGI_STATE_COLLIDES = ( magician.HURT, magician.ALIVE )


class CollHandlerBulletMagi():
    """
    la classe qui tralala. Voir d�but du fichier.
    """

    def __init__(self, listMagician):
        """
        constructeur. (thx captain obvious)

        entr�e :
            listMagician : r�f�rence vers la liste des magiciens
                           dans le jeu. Le contenu de la liste �volue en live,
                           Le CollHandlerBulletMagi se contente de consulter cette liste.
        """
        self.listMagician = listMagician


    def heroFiresBullets(self, posFire):
        """
        fonction � ex�cuter lorsque le h�ros tire un coup de flingue.

        entr�e :
          posFire : rect(X,Y) indiquant les coordonn�es de d�part du coup de feu
                    (c'est pas les coordonn�es du h�ros, c'est les coordonn�es du
                     bout du flingue du h�ros)

        plat-dessert :
          un tuple de deux int.
           - nombre de magiciens explos�s par le tir
           - nombre de magiciens tu�s par le tir

        Cette fonction ne d�termine pas directement le nombre de magicien tu�s et explos�s.
        Ce sont les instances de magicien qui font cela.
        """

        #dictionnaire indiquant les magiciens touch�s par une/des bullets.
        #cl� : r�f�rence vers l'instance de magicien touch�
        #valeur : nombre de bullets de ce tir qui l'ont touch� en m�me temps.
        dicMagicianHit = {}

        # --- remplissage de dicMagicianHit ---

        for bulletListTotalMove in LIST_BULLET_LIST_TOTAL_MOVE:

            #on g�re compl�tement la trajectoire de chaque bullet, l'une apr�s l'autre.

            #cr�ation d'un movingPoint repr�sentant la bullet, avec sa listTotalMove
            #qu'on a calcul� pr�c�demment
            bullet = MovingPoint(posFire, listTotalMove=bulletListTotalMove)

            isBulletActive = True

            while isBulletActive:

                #on fait avancer le movingPoint repr�sentant la bullet. D�s que �a cogne dans
                #un truc ou que �a sort de l'�cran, on la d�sactive.

                #on parcourt la liste des magiciens et on voit si y'a collision.
                #avec une boucle comme �a, une bullet peut toucher plusieurs magiciens
                #en m�me temps, si ils se trouvent pile poil � la m�me abscisse
                #moi �a me choque pas et je trouve �a cool. C'est fait expr�s.
                for Magician in self.listMagician:

                    if Magician.currentState in LIST_MAGI_STATE_COLLIDES and \
                       Magician.rect.collidepoint(bullet.topleft):

                        #y'a une collision avec un magicien

                        #d�sactivation de la bullet. Elle ne fera pas plus de mouvement,
                        #mais on continue quand m�me de parcourir toute la liste des magiciens,
                        #pour d�tecter d'autres collisions.
                        isBulletActive = False

                        if Magician in dicMagicianHit:
                            #le magicien est d�j� dans le dico dicMagicianHit.
                            #il est d�j� touch� par au moins une bullet.
                            #on le laisse dans le dico, et on ajoute une bullet de plus
                            #� la valeur.
                            dicMagicianHit[Magician] += 1
                        else:
                            #le magicien n'est pas dans le dico dicMagicianHit
                            #il n'a pas encore �t� touch� par une bullet.
                            #on l'ajoute dans le dico, avec la valeur 1 (une bullet)
                            dicMagicianHit[Magician] = 1

                #pas de collision. On avance la bullet de un pas, selon sa direction pr�definie
                bullet.advanceOneStep()

                if not GAME_RECT.collidepoint(bullet.topleft):
                    #la bullet n'est plus en collision avec le gros rect
                    #repr�sentant l'aire de jeu. Donc elle est sortie de l'�cran.
                    #on la vire, et la boucle passera � la bullet suivante
                    isBulletActive = False

        #nombre de magicien burst par ce tir
        nbrMagicianBurst = 0
        #nombre de magicien tu� (sans burst) par ce tir
        nbrMagicianKilledNotBurst = 0

        for Magician, Damage in dicMagicianHit.items():

            #pour chaque magicien touch�, on le pr�vient qu'il s'est fait touch�
            #en lui indiquant le nombre de bullet qui l'a atteint simultan�ment (c.a.d. : Damage)
            magicianState = Magician.hitByBullet(Damage)

            #le magicien prend en compte le Hit, et renvoie son �tat.
            #Si il s'est fait tu� ou explos�, on augmente le compteur correspondant.
            if magicianState in [magician.DYING, magician.DEAD]:
                nbrMagicianKilledNotBurst += 1
            elif magicianState == magician.BURSTING:
                nbrMagicianBurst += 1

        #on renvoie les deux compteurs.
        #le h�ros r�cup�re ces valeurs et les additionne � ses scores
        return (nbrMagicianBurst, nbrMagicianKilledNotBurst)


