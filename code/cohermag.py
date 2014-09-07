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

date de la derni�re relecture-commentage : 08/10/2010

gestion des collisions entre les magiciens et le h�ro.

La classe CollHandlerHeroMagi poss�de une r�f�rence vers la liste de tous les magiciens du jeu,
ainsi qu'une r�f�rence vers le h�ros.

Elle v�rifie si y'a une collision entre l'un des magiciens, et le h�ros,
Et si c'est le cas, elle envoie un stimuli de HURT au h�ros.
(qui g�rera la reste tout seul : recul, changement du sprite, perte de point de vie, ...)
et elle indique �galement au magicien concern� qu'il a touch� le h�ros.

le h�ros ne se prend qu'un seul stimuli de HURT, m�me si y'a plusieurs magiciens qui
le touche en m�me temps pil poil dans le m�me cycle.

On n'envoie aucun stimuli de HURT si le h�ros est d�j� HURT. Ce serait pas tr�s gentil sinon.

Je dois expliquer et justifier pourquoi le lien CollHandlerHeroMagi-Hero est pas le m�me
que le lien CollHandlerBulletMagi-Hero.
Pour cela, je dois utiliser le mot "idiosyncratique", m�me si on sait pas ce que �a veut dire.

justification 1 : je fais ce que je veux.

justification 2 :
le CollHandlerBulletMagi n'a pas de r�f�rence vers le h�ros, il ne
re�oit que la position (X,Y) du coup de feu tir� par le h�ros. Et il se contente
de renvoyer un tuple de valeur (nbre de magi tu�s/explos�s). Ca permettrait de faire
tirer des coups de feu par d'autres choses que le h�ros. La classe est ind�pendante.

le CollHandlerHeroMagi contient une r�f�rence vers le h�ros. J'ai d�cid� que cette classe
serait moins ind�pendante, mais plus "de haut niveau". Car elle envoie directement le stimuli
de HURT au h�ros.
Oh putain c'est de la merde ce que je dis et on s'en fout. idiosyncratique et go fuck yourself
"""

import pygame

import herobody
import herohead
import hero
import magician


class CollHandlerHeroMagi():
    """
    Collision Handler Hero-Magician
    """

    def __init__(self, listMagician):
        """
        constructeur. (thx captain obvious)

        entr�e :
            listMagician : r�f�rence vers la liste des magiciens dans le jeu.
                           La classe ne fait que consulter la liste.

        """
        self.listMagician = listMagician


    def testCollisionHeroMagi(self, theHero):
        """
        teste si un magicien est en collision avec le h�ros, ou pas.
        Si oui, envoie les stimulis n�cessaire au h�ros, et au magicien concern�.

        entr�e :
            hero         : r�f�rence vers l'instance du h�ros dont on g�re les collisions
                           cette classe ne modifie pas directement les caract�ristiques du h�ros.
                           mais elle appelle la fonction takeStimuliHurt. bong !!!
        """

        #on doit tester les collisions "corps du h�ros"<->magicien, et "t�te du h�ros"<->magicien
        rectHead = theHero.heroHead.rect
        rectBody = theHero.heroBody.rect

        for theMagician in self.listMagician:

            #pas de collision si le h�ros est d�j� HURT.
            #soit � cause d'une collision qui s'est pass� il y a quelques cycles,
            #soit � cause d'une collision dans le m�me cycle, mais avec un autre magicien
            if theHero.currentState == hero.HURT:
                #un peu crade car on return en plein milieu d'une boucle. Faites pas chier
                return

            #seul les magiciens ALIVE peuvent faire mal au h�ros.
            if theMagician.currentState == magician.ALIVE:

                #test de collision tout simple, avec des rectangles.
                #l'astuce c'est que mes sprites ont vaguement une forme rectangulaire,
                #donc �a se verra pas trop que je g�re �a compl�tement � l'arrache
                if theMagician.rect.colliderect(rectHead) or \
                   theMagician.rect.colliderect(rectBody):

                    #envoi du simuli HURT au h�ros. Cela va changer son currentState en HURT.
                    #faut lui passer la position du magicien, pour qu'il sache dans quel
                    #direction faire son mouvement de Hurt.
                    theHero.takeStimuliHurt(theMagician.rect)

                    #envoi du stimuli de touchage du h�ros au magicien.
                    #Ca va le faire revenir au level 1. (voir explication dans magician.py)
                    theMagician.TakeStimuliTouchedHero()
