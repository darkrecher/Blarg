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

date de la dernière relecture-commentage : 08/10/2010

gestion des collisions entre les magiciens et le héro.

La classe CollHandlerHeroMagi possède une référence vers la liste de tous les magiciens du jeu,
ainsi qu'une référence vers le héros.

Elle vérifie si y'a une collision entre l'un des magiciens, et le héros,
Et si c'est le cas, elle envoie un stimuli de HURT au héros.
(qui gérera la reste tout seul : recul, changement du sprite, perte de point de vie, ...)
et elle indique également au magicien concerné qu'il a touché le héros.

le héros ne se prend qu'un seul stimuli de HURT, même si y'a plusieurs magiciens qui
le touche en même temps pil poil dans le même cycle.

On n'envoie aucun stimuli de HURT si le héros est déjà HURT. Ce serait pas très gentil sinon.

Je dois expliquer et justifier pourquoi le lien CollHandlerHeroMagi-Hero est pas le même
que le lien CollHandlerBulletMagi-Hero.
Pour cela, je dois utiliser le mot "idiosyncratique", même si on sait pas ce que ça veut dire.

justification 1 : je fais ce que je veux.

justification 2 :
le CollHandlerBulletMagi n'a pas de référence vers le héros, il ne
reçoit que la position (X,Y) du coup de feu tiré par le héros. Et il se contente
de renvoyer un tuple de valeur (nbre de magi tués/explosés). Ca permettrait de faire
tirer des coups de feu par d'autres choses que le héros. La classe est indépendante.

le CollHandlerHeroMagi contient une référence vers le héros. J'ai décidé que cette classe
serait moins indépendante, mais plus "de haut niveau". Car elle envoie directement le stimuli
de HURT au héros.
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

        entrée :
            listMagician : référence vers la liste des magiciens dans le jeu.
                           La classe ne fait que consulter la liste.

        """
        self.listMagician = listMagician


    def testCollisionHeroMagi(self, theHero):
        """
        teste si un magicien est en collision avec le héros, ou pas.
        Si oui, envoie les stimulis nécessaire au héros, et au magicien concerné.

        entrée :
            hero         : référence vers l'instance du héros dont on gère les collisions
                           cette classe ne modifie pas directement les caractéristiques du héros.
                           mais elle appelle la fonction takeStimuliHurt. bong !!!
        """

        #on doit tester les collisions "corps du héros"<->magicien, et "tête du héros"<->magicien
        rectHead = theHero.heroHead.rect
        rectBody = theHero.heroBody.rect

        for theMagician in self.listMagician:

            #pas de collision si le héros est déjà HURT.
            #soit à cause d'une collision qui s'est passé il y a quelques cycles,
            #soit à cause d'une collision dans le même cycle, mais avec un autre magicien
            if theHero.currentState == hero.HURT:
                #un peu crade car on return en plein milieu d'une boucle. Faites pas chier
                return

            #seul les magiciens ALIVE peuvent faire mal au héros.
            if theMagician.currentState == magician.ALIVE:

                #test de collision tout simple, avec des rectangles.
                #l'astuce c'est que mes sprites ont vaguement une forme rectangulaire,
                #donc ça se verra pas trop que je gère ça complètement à l'arrache
                if theMagician.rect.colliderect(rectHead) or \
                   theMagician.rect.colliderect(rectBody):

                    #envoi du simuli HURT au héros. Cela va changer son currentState en HURT.
                    #faut lui passer la position du magicien, pour qu'il sache dans quel
                    #direction faire son mouvement de Hurt.
                    theHero.takeStimuliHurt(theMagician.rect)

                    #envoi du stimuli de touchage du héros au magicien.
                    #Ca va le faire revenir au level 1. (voir explication dans magician.py)
                    theMagician.TakeStimuliTouchedHero()
