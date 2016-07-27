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

date de la dernière relecture-commentage : 08/10/2010

la classe pour gérer l'affichage des cartouches.

vocabulaire :

AmmoBox : le chargeur affichant le nombre de cartouches restantes.
Shell : la douille jaune de la cartouche. (je sais pas si c'est le vrai mot anglais. osef)
Bullet : la cartouche. Mais juste la cartouche sans la douille.
BulletShell, ou BulShel : la cartouche ET la douille.
BulletSmoke : fumée de la cartouche. C'est pas géré directement par l'ammoViewer.
              en fait c'est juste un spriteSimple affichant l'anim de fumée.
              l'ammoviewer crée le spriteSimple quand il faut. Le reste se fait tout seul.
Rearm, Reload : voir explication dans l'en-tête du fichier "hero.py"

comment on va gérer ça ? il faut que chaque BulletShell soit un minimum indépendant des autres.
 - nbrOfRearmToDo : nombre de rearming à faire. normalement ça dépasse pas 1, mais osef.
 - nbrOfReloadToDo : pareil.
 - nbrOfFireToDo : pareil pareil

bon je me pique de vouloir faire des bullets qui se réaffichent pas tout le temps.
Mais du coup, c'est un peu le bronsk.

J'utilise la variable AmmoViewer.isUpdatingSthg, qui permet d'indiquer au code extérieur
qu'il s'est passé un changement quelconque dans les bullets, et qu'il faut donc les rafraîchir.
(Les sprites à afficher se trouvent tous dans AmmoViewer.groupBulShell)
Donc à chaque cycle, le code extérieur doit faire les trucs suivants :

 - AmmoViewer.determineIsUpdatingSthg() pour remettre à jour la variable AmmoViewer.isUpdatingSthg
 - si cette variable est False, il n'y a rien à faire. Si elle est True, il faut faire tout ça :
    * AmmoViewer.groupBulShell.clear pour effacer les sprites
    * AmmoViewer.updateAmmoViewer pour remettre à jour les sprites (img, pos, ...)
    * AmmoViewer.groupBulShell.draw pour réafficher les sprites remis à jour.

J'ai pas prévu de sécurité si jamais on fait un reload
alors que y'a déjà toutes les BulletShell dans le chargeur,
ni si on fait un fire ou un rearm alors que y'a plus de BulletShell dans le chargeur.
Je suppose que ça plante. De toute façon c'est pas censé arriver. La classe Hero
contient les sécurités nécessaires pour éviter ces conneries.

et y'a un gosse qui fait "tic tic tic" et "ding !" dans le fond du car.
Euh... Moi j'suis pas là hein ! J'ai rien à voir là dedans moi !!
"""

import pygame

from common import pyRect, NONE_COUNT
from hero import NBR_MAX_CARTOUCHE

#position de l'ammoBox. En vrai c'est une image fixe. Mais faut placer
#correctement les cartouches par rapport à cette image fisc.
POS_AMMO_BOX = pyRect(4, 134)

#décalage entre une Shell et le Bullet correspondant
DECALAGE_SHELL_BULLET = pyRect(16, 3)
#espacement vertical entre deux BulletShell
SPACING_Y_BULLETS = 2

#liste des mouvements à appliquer aux cartouches restantes dans le flingue,
#lorsque le héros réarme. Ici, les cartouches montent, de 4 pix par 4 pix
MOVEMENT_REARMING = (pyRect(0, -4), ) * 5

#identifiant des images
(imgBullet,       #Bullet
 imgShell,        #Shell. Qui reste tel quel après le tir. Mais disparaît à la fin du rearm.
) = range(2)

#préfixes et noms des fichiers images
IMG_FILENAME_PREFIX = "bul"

LIST_IMG_FILE_SHORT_NAME = (
 (imgBullet,       "let"),
 (imgShell,        "shell"),
)

#on remarque que y'a pas les images de bulletSmoke. Normal, c'est géré par un SimpleSprite

#je l'avais balancé ce truc pourri. Et après on m'a dit que quelqu'un avait tué une chèvre
#c'était bizarre...


class AmmoViewer():
    """
    affichage du nombre de BulletShell restant dans le chargeur, avec anim et tout.

    Un BulletShell est un couple de deux sprites (sprShell, sprBullet)

    Lors de l'init de la classe,
    On fabrique autant de BulletShell qu'il y en a au max dans le chargeur.

    dans la suite, on ne fait pas de destruction/re-création de sprites.
    On fait simplement du cachage/affichage.
    Pour cacher un sprite, on l'enlève du groupe self.groupBulShell
    Pour réafficher, on le remet.

    il n'y a pas de grosse liste globale contenant tous les BulletShell. Il y en a deux petites :

    self.listBulShellLoaded : les BulletShell dans le chargeur. l'ordre dans la liste est le
    même que l'ordre dans le chargeur. Le premier élément de la liste est le BulletShell du
    haut. (Celui qui sortira au prochain coup de feu).

    self.listBulShellToLoad : les BulletShell à charger. Leur ordre n'est pas important.
    On prend le premier de la liste à l'arrache quand on en a besoin d'un.

    C'est un peu casse-gueule car si je paume un BulletShell lors du passage d'une liste
    à l'autre, je perds sa référence, et il se fait garbage collecté. Mais ça, ça m'arrive
    jamais car je suis pas un branquignol.
    """

    def __init__(self, dicAmmoViewerImg, spriteSimpleGenerator):
        """
        constructeur. (thx captain obvious)

        entrée :
            dicAmmoViewerImg : dictionnaire de correspondance
                               identifiant d'image -> image

            spriteSimpleGenerator : classe eponyme. Pour que l'ammoviewer génère
                                    des petits sprites si il a envie (les bulletSmoke)

        """
        self.dicAmmoViewerImg = dicAmmoViewerImg
        self.spriteSimpleGenerator = spriteSimpleGenerator

        #je voulais utiliser les dirtySprites, mais j'arrive pas à les faire
        #fonctionner comme il faut. Ca n'enregistre pas le rect de clear.
        #que celui de dessinage. (ou l'inverse ?). Voir mon article de blog à ce sujet.
        #http://recher.wordpress.com/2010/07/13/vulture-repellent-doesnt-work
        #bref. Ce groupe contient les sprites des Bullet et des Shell à afficher.
        self.groupBulShell = pygame.sprite.RenderUpdates()

        #calcul du décalage total entre 2 BulletShell
        heightBulletShell = self.dicAmmoViewerImg[imgShell].get_height()
        decalTwoBulletShell_Y = heightBulletShell + SPACING_Y_BULLETS
        self.decalTwoBulletShell = pyRect(0, decalTwoBulletShell_Y)

        #liste des BulletShell chargées (on les voit à l'écran)
        self.listBulShellLoaded = []
        #liste des BulletShell pas chargé (on les voit pas).
        self.listBulShellToLoad = []

        #céation des sprites de Bullet et de Shell
        #héhé, j'adore ce concept d'appeler une variable "_" parce qu'on n'en a pas besoin.
        for _ in xrange(NBR_MAX_CARTOUCHE):

            sprShell = pygame.sprite.Sprite()
            sprShell.image = self.dicAmmoViewerImg[imgShell]

            sprBullet = pygame.sprite.Sprite()
            sprBullet.image = self.dicAmmoViewerImg[imgBullet]

            #on ajoute le BulletShell dans la liste des "à charger"
            #donc là, elles vont pas encore s'afficher.
            self.listBulShellToLoad.append((sprShell, sprBullet))

        #position de la prochaine cartouche qui va se recharger.
        #(Ce sera la toute première cartouche, donc on la place au niveau
        #de l'ammoBox (chargeur contenant toutes les cartouches)
        self.posShellToReload = pygame.Rect(POS_AMMO_BOX)

        #variable indiquant au code principal si y'a eu des changements de sprites.
        #(image, pos, cachage/montrage, ...)
        self.isUpdatingSthg = True

        #nombre de coups de feu et de réarmement à faire.
        self.nbrOfFireToDo = 0
        self.nbrOfRearmToDo = 0

        #on indique qu'il faut charger toutes les cartouches, dès le départ.
        #Comme ça, ça exécute la fonction qui les affiche et les positionne bien comme il faut.
        #Pas besoin de doubloniser le code avec une boucle qui les positionnerait toute d'un coup.
        #factorisation power !!
        #Par contre, j'ai codé ça de façon à ce que y'ait qu'un seul reload par cycle. Même si il
        #faut en faire plein d'un coup. Du coup, au début de la partie, on voit les cartouches
        #qui apparaissent une par une, mais très vite. Eh bien moi je trouve ça cool et j'ai
        #décidé de le laisser comme ça.
        self.nbrOfReloadToDo = NBR_MAX_CARTOUCHE

        #curseur sur la liste MOVEMENT_REARMING. Permet de savoir où on en est
        #dans le déplacement des cartouches quand il y a un rearm
        self.cursorRearmMovement = NONE_COUNT


    #les fonctions de prise en compte des stimulis envoyé par le code extérieur.
    #(Plus exactement la classe Hero)

    def takeStimuliFire(self): self.nbrOfFireToDo += 1

    def takeStimuliRearm(self): self.nbrOfRearmToDo += 1

    def takeStimuliReload(self): self.nbrOfReloadToDo += 1


    def determineIsUpdatingSthg(self):
        """
        fonction qui met à jour la variable self.isUpdatingSthg,
        La variable devient True si y'a des trucs à faire. Elle devient False sinon.

        En même temps, la fonction démarre un rearm, un reload ou un fire, si ça a lieu d'être

        plat-dessert :
            boolean. self.isUpdatingSthg

        TRODO : c'est pas tout à fait optimisé comme truc. La variable isUpdatingSthg
        est utilisée par le code principal, pour savoir si faut updater à l'écran
        le groupe de sprite contenant les BulletShell.
        Je met cette variable à True dès qu'il y a un truc en cours. Mais c'est pas
        pour ça que des sprites ont bougé / changé d'image. Si on est en train de compter
        entre deux mouvements de rearm par exemple, on devrait pas mettre isUpdatingSthg à True.
        Mais je voulais pas me prendre la tête.
        (Me fait déjà assez chier comme ça pour l'optimisation)
        blablablabla blablabla qu'est-ce que je peux raconter comme connerie !!
        """

        #Vérifie si il faut démarrer une animation de réarmement.
        if self.nbrOfRearmToDo > 0:
            self.startRearm()

        #Vérifie si il y a une anim de rearm en cours.
        if self.cursorRearmMovement is not NONE_COUNT:
            self.isUpdatingSthg = True
        else:
            self.isUpdatingSthg = False

        #Vérifie si il faut faire un reload.
        #Le reload est instantané. On ajoute directement le BulletShell.
        #du coup y'a pas de test sur des compteur ou des curseurs. Mais on met
        #quand même la variable self.isUpdatingSthg à True, car un truc a changé.
        if self.nbrOfReloadToDo > 0:
            self.reload()
            self.isUpdatingSthg = True

        #Vérifie si il faut démarrer une animation de tirage d'un coup
        #Pareil, le fire est instantané. (Y'a juste à virer la cartouche).
        #La BulletSmoke n'influe pas sur self.isUpdatingSthg,
        #vu qu'elle est pas géré par l'ammoviewer
        if self.nbrOfFireToDo > 0:
            self.startFire()
            self.isUpdatingSthg = True

        return self.isUpdatingSthg


    def updateAmmoViewer(self):
        """
        code global d'update de l'AmmoViewer, à exécuter une fois à chaque cycle.
        """

        #avancement d'un cycle de l'anim de rearm, si il y en a une en cours.
        if self.cursorRearmMovement is not NONE_COUNT:
            self.doRearmMovement()

        #comme dit plus haut, pas de gestion de l'anim de reload, car instantanée.
        #et pas non plus de gestion de l'anim de fire, car géré par un spriteSimple


    def startRearm(self):
        """
        démarrage d'une animation de réarmement.
        (Mouvement de toutes les BulletShell vers le haut)
        """
        self.cursorRearmMovement = 0
        self.nbrOfRearmToDo -= 1


    def startFire(self):
        """
        démarrage d'une animation de coup de feu. (faut virer la Bullet du haut, et
        démarrer un SpriteSimpe de bulletSmoke)
        """

        #détermination du sprite de bullet qu'il faut tirer.
        #donc c'est le premier de la liste : [0]
        #et après il faut choisir entre le shell et le bullet : [1]
        sprBulletFiring = self.listBulShellLoaded[0][1]

        #détermination de la position de la BulletSmoke (c'est la même pos que sprBulletFiring)
        posBulletSmoke = pygame.rect.Rect(sprBulletFiring.rect)
        #Génération du SpriteSimple qui fera l'anim du BulletSmoke.
        self.spriteSimpleGenerator.generateBulletSmoke(posBulletSmoke)
        #cachage de la bullet. (on la supprime du groupe contenant tous les sprites affichés)
        self.groupBulShell.remove(sprBulletFiring)

        self.nbrOfFireToDo -= 1


    def doRearmMovement(self):
        """
        avance d'un pas le mouvement de rearming (un petit mouvement vers le haut)
        """

        #arrêt de la fin des mouvements de rearming, si on les a tous fait.
        if self.cursorRearmMovement >= len(MOVEMENT_REARMING):
            self.cursorRearmMovement = NONE_COUNT
            #réarrangement des BulletShell en tenant compte du réarming qu'on vient de faire.
            self.endRearm()
            return

        #conversion rect -> tuple de mouvement. (C'est chiant de devoir faire ça)
        moveRearming = MOVEMENT_REARMING[self.cursorRearmMovement].topleft

        #on applique le piti mouvement sur tous les BulletShell chargées
        for (sprShell, sprBullet) in self.listBulShellLoaded:
            sprShell.rect.move_ip(moveRearming)
            sprBullet.rect.move_ip(moveRearming)

        #il faut aussi appliquer ce mouvement sur
        #la position de la prochaine BulletShell à reloader
        self.posShellToReload.move_ip(moveRearming)

        #on avance le curseur vers le prochain piti mouvement de rearm à faire.
        self.cursorRearmMovement += 1


    def endRearm(self):
        """
        fonction effectuant les trucs à faire à la fin d'un réarmement.
        Il y a une BulletShell qui est sortie du chargeur.
        Donc il faut la transférer de la liste des BulShell loaded
        vers la liste des BulShell to load (sans la perdre en route).
        """

        #chopage de la BulletShell, et en même temps supression dans la liste des loaded
        (sprShell, sprBullet) = self.listBulShellLoaded.pop(0)

        #cachage du Shell, on n'a plus à l'afficher.
        #on cache pas le Bullet, car ça a déjà été fait avant.
        self.groupBulShell.remove(sprShell)

        #ajout du BulletShell dans la liste des BulShel to load
        self.listBulShellToLoad.append((sprShell, sprBullet))


    def reload(self):
        """
        chargement d'une nouvelle cartouche dans le chargeur.
        transfert d'une BulletShell de BulShell to load vers BulShell loaded
        affichage de cette BulletShell dans le chargeur
        """

        self.nbrOfReloadToDo -= 1

        #on chope la BulletShell à charger, et en même temps on la vire de la liste des to load.
        (sprShell, sprBullet) = self.listBulShellToLoad.pop(0)

        #détermination de la position du sprite de Shell.
        sprShell.rect = pygame.Rect(self.posShellToReload)
        #détermination de la position de la bullet, à partir de la position du shell
        #et redéfinition de l'image pour le Bullet.
        sprBullet.image = self.dicAmmoViewerImg[imgBullet]
        posBul = self.posShellToReload.move(DECALAGE_SHELL_BULLET.topleft)
        sprBullet.rect = pygame.Rect(posBul)

        #affichage des deux sprites. (on l'ajoute au groupe affichant tous les sprites)
        self.groupBulShell.add(sprShell)
        self.groupBulShell.add(sprBullet)

        #ajout du BulletShell dans la liste des loaded
        self.listBulShellLoaded.append((sprShell, sprBullet))

        #réactualisation de la position de la prochaine BulletShell à charger.
        #il faut décaler d'un espace de cartouche vers le bas
        self.posShellToReload.move_ip(self.decalTwoBulletShell.topleft)

