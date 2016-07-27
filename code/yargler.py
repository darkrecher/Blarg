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

date de la dernière relecture-commentage : 02/03/2011

classe qui joue les sons. Yaaaah !!! yargl.

Les sons sont organisés par groupe.
Un groupe correspond à un événement (ex : coup de feu, magicien qui se prend une balle, ...)
Il peut y avoir plusieurs sons dans un même groupe.
Lorsque l'événement survient, on choisit un son au hasard parmi ceux du groupe, et on le joue.
"""

import os
import pygame
import random

from common import (securedPrint, SOUND_DIRECTORY_NAME,
                    SOUND_ENABLED, SOUND_DISABLED)

#liste des identifiants de sons. Chaque identifiant peut se rapporter à un son unique,
#ou à un groupe de sons.
(SND_MAG_BURST,         #magicien qui explose
 SND_MAG_DYING_ROTATE,  #magicien qui meurt en tournoyant dans les airs
 SND_MAG_DYING_SHIT,    #magicien qui meurt en se transformant en chiasse
 SND_GUN_REARM,         #réarmement du flingue
 SND_GUN_FIRE,          #coups de feu. Pan !
 SND_HERO_HURT,         #cri du héro quand il se fait toucher
 SND_GUN_RELOAD,        #rechargement du flingue
 SND_MAG_DYING_FART,    #pet du magicien, quand il meurt en s'envolant et en pétant.
 SND_HERO_DIE,          #héros qui meurt
 SND_MAG_HURT,          #magicien qui se fait toucher (sans mourir)
 SND_MAG_APPEAR,        #magicien qui apparaît
 SND_PREZ_BLARG,        #le "Blarg" de la présentation
 SND_STORY_MUSIC,       #la chanson que je chante moi-même pendant le scrolling du scénario
 SND_MENU_SELECT,       #"blolop" de sélection d'une option du menu
 SND_MENU_CYCLE,        #"plop" de cyclage de focus d'un élément de menu vers un autre
) = range(15)

#dictionnaire des infos permettant de charger tous les fichiers de sons.
#clé    : identifiant du son ou du groupe de son
#valeur : tuple de 2 éléments
#         - noms de fichier son court.
#         - nombre de sons à charger pour ce groupe
DICT_SND_FILENAME = {
    SND_MAG_BURST         : ("magbur", 12),
    SND_MAG_DYING_ROTATE  : ("magrot", 15),
    SND_MAG_DYING_SHIT    : ("magshi", 10),
    SND_GUN_REARM         : ("shlklk",  4),
    SND_GUN_FIRE          : ("pan",     8),
    SND_HERO_HURT         : ("herarg",  2),
    SND_GUN_RELOAD        : ("clicli",  1),
    SND_MAG_DYING_FART    : ("prout",  10),
    SND_HERO_DIE          : ("herdie",  1),
    SND_MAG_HURT          : ("magarg", 12), #magar11.ogg = son du Ckyfran
    SND_MAG_APPEAR        : ("zwouw",   9),
    SND_PREZ_BLARG        : ("blarg",   1),
    SND_STORY_MUSIC       : ("tuluu",   1),
    SND_MENU_SELECT       : ("bllb",    1),
    SND_MENU_CYCLE        : ("pop",     1),
}

#on a déjà, autre part, un dico faisant la correspondance entre des booléens et
#le son activé ou pas. C'est le menuzcon.GLOB_DATA_SOUND_FROM_TICK_VALUE.
#Mais les booleans n'on pas la même signification.
#Y'a le boolean de la case à cocher du son. Et le boolean de "doit-on jouer des sons ou pas".
#Moi je dis que c'est pas les même, que d'abord que même que ouais.
DIC_SOUND_ENABLED_FROM_GLOB_DATA = {
    SOUND_ENABLED   : True,
    SOUND_DISABLED  : False,
}

class SoundYargler():
    """
    Le machin qui joue les sons
    """

    def __init__(self):
        """
        constructeur. (thx captain obvious)
        """

        #Indique si on a réussi le chargement des fichiers sons.
        self.loadSoundSucess = False


    def loadSound(self, filename):
        """
        charge un fichier son

        entrées :
            filename : String indiquant le nom complet du fichier son à charger.
                       Les sons doivent toutes être dans le sous-répertoire SOUND_DIRECTORY_NAME.

        plat-dessert :
            l'objet pygame.mixer.Sound contenant le son chargé
        """

        pathname = os.path.join(SOUND_DIRECTORY_NAME, filename)

        #Tentative de chargement du son. On quitte totalement le jeu comme un voleur si ça fail.
        #TRODO pour plus tard : ouais en fait ça throw pas d'exception quand le chargement fail.
        #Va falloir trouver autre chose. Monde de merde.
        try:
            sound = pygame.mixer.Sound(pathname)
        except pygame.error, message:
            securedPrint(u"Fail. Impossible de charger le son : " + pathname)
            raise SystemExit, message

        return sound


    def loadAllSounds(self):
        """
        charge tous les fichiers sons, et les range comme il faut dans les groupes de son.

        plat-dessert :
            rien du tout. Mais la fonction peut modifier self.loadSoundSucess si on réussit.
        """

        #Fail si le biniou pour balancer les sons n'est pas disponible.
        if not pygame.mixer or not pygame.mixer.get_init():
            securedPrint("Impossible initialising ze sounds. Yep. Too bad.")
            return

        #dictionnaire qui contiendra tous les sons et groupes de sons.
        #clé : identifiant du son ou groupe de son
        #valeur : tuple de 2 éléments.
        #          - nombre de son dans le groupe. (Ca peut être 1)
        #          - tuple avec tous les sons du groupe.  (objet pygame.mixe.Sound)
        #le nombre de sons, on pourrait l'obtenir avec len(tuple_des_sons).
        #Mais comme j'en ai besoin tout le temps de cette valeur, je préfère la "pré-calculer".
        self.dictSoundGroups = {}

        for soundGroupId, soundGroupInfo in DICT_SND_FILENAME.items():

            shortFileName, nbrSound = soundGroupInfo
            #liste qui contiendra tous les sons du groupe, quand on les aura chargés.
            listSound = []

            #chargement des sons du groupe
            for soundIndex in xrange(nbrSound):

                #les sons d'un groupe ont des noms de fichiers semblables :
                #"nomCourt00.ogg", "nomCourt01.ogg", "nomCourt02.ogg", ...
                #Donc faut construire le nom de fichier complet à partir du nom
                #de fichier court, du numéro du son écrit sur 2 chiffres, et de ".ogg". Voilà.
                longFileName = "".join((shortFileName,
                                        str(soundIndex).rjust(2, "0"),
                                        ".ogg"))

                #chargement du son, et rangement dans la liste.
                soundLoaded = self.loadSound(longFileName)
                listSound.append(soundLoaded)

            #rangement du groupe de son (avec le nombre de son) dans le dictionnaire.
            self.dictSoundGroups[soundGroupId] = (nbrSound, tuple(listSound))

        #bon, si on est arrivé jusqu'ici, y'a qu'à dire que tout va bien. (Même si
        #c'est pas forcément vrai, puisque pas d'exception générée par la fonction loadSound.)
        self.loadSoundSucess = True


    def playSound(self, soundGroupId):
        """
        choisit au hasard un son, parmi ceux du groupe spécifié en paramètre,
        et joue ce son. "Tut tut pouet pouet Arrrggll spflark!"

        entrées :
            soundGroupId : identifiant du son ou du groupe de son à jouer.
        """

        #on ne joue pas de son si le chargement des sons a raté.
        if not self.loadSoundSucess:
            return

        #on ne joue pas de son si ils ont été désactivés par le joueur, lors de la config.
        if not self.soundEnabled:
            return

        #récupération des infos liées au groupe de son indiqué par le paramètre.
        (nbrSound, listSound) = self.dictSoundGroups[soundGroupId]

        if nbrSound > 1:
            #il y a plusieurs sons dans le groupe. On en choisit un au hasard.
            soundChosen = random.choice(listSound)

        else:
            #Il n'y a qu'un seul son dans le groupe. Pas la peine de se prendre la tête à
            #faire du random. On le prend directement.
            soundChosen = listSound[0]

        #on joue le son. Hop, y'a une fonction toute faite pour ça. Youpi.
        soundChosen.play()


    def changeSoundEnablation(self, globDataSound):
        """
        active/désactive le son. En fonction de la global Data, qui provient,
        soit du fichier de sauvegarde/config, soit de la case à cocher du menu de config.
        """

        #conversion booléen <- globData
        soundEnablation = DIC_SOUND_ENABLED_FROM_GLOB_DATA[globDataSound]
        #enregistrement du booléen.
        self.soundEnabled = soundEnablation


#Instanciation immédiate de la classe stockant tous les sons.
#Je suis pas fan de ce genre de truc. Mais là c'est un peu obligé. Sinon faut que
#je le passe en paramètre à plein plein de classe.
#Le chargement de tous les sons n'est pas effectué dès l'instanciation de la classe.
#Il faut le faire explicitement, en exécutant loadAllSounds. Tout cela se passe ailleurs.
theSoundYargler = SoundYargler()
