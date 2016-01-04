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

date de la derni�re relecture-commentage : 02/03/2011

classe qui joue les sons. Yaaaah !!! yargl.

Les sons sont organis�s par groupe.
Un groupe correspond � un �v�nement (ex : coup de feu, magicien qui se prend une balle, ...)
Il peut y avoir plusieurs sons dans un m�me groupe.
Lorsque l'�v�nement survient, on choisit un son au hasard parmi ceux du groupe, et on le joue.
"""

import os
import pygame
import random

from common import (securedPrint, SOUND_DIRECTORY_NAME,
                    SOUND_ENABLED, SOUND_DISABLED)

#liste des identifiants de sons. Chaque identifiant peut se rapporter � un son unique,
#ou � un groupe de sons.
(SND_MAG_BURST,         #magicien qui explose
 SND_MAG_DYING_ROTATE,  #magicien qui meurt en tournoyant dans les airs
 SND_MAG_DYING_SHIT,    #magicien qui meurt en se transformant en chiasse
 SND_GUN_REARM,         #r�armement du flingue
 SND_GUN_FIRE,          #coups de feu. Pan !
 SND_HERO_HURT,         #cri du h�ro quand il se fait toucher
 SND_GUN_RELOAD,        #rechargement du flingue
 SND_MAG_DYING_FART,    #pet du magicien, quand il meurt en s'envolant et en p�tant.
 SND_HERO_DIE,          #h�ros qui meurt
 SND_MAG_HURT,          #magicien qui se fait toucher (sans mourir)
 SND_MAG_APPEAR,        #magicien qui appara�t
 SND_PREZ_BLARG,        #le "Blarg" de la pr�sentation
 SND_STORY_MUSIC,       #la chanson que je chante moi-m�me pendant le scrolling du sc�nario
 SND_MENU_SELECT,       #"blolop" de s�lection d'une option du menu
 SND_MENU_CYCLE,        #"plop" de cyclage de focus d'un �l�ment de menu vers un autre
) = range(15)

#dictionnaire des infos permettant de charger tous les fichiers de sons.
#cl�    : identifiant du son ou du groupe de son
#valeur : tuple de 2 �l�ments
#         - noms de fichier son court.
#         - nombre de sons � charger pour ce groupe
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

#on a d�j�, autre part, un dico faisant la correspondance entre des bool�ens et
#le son activ� ou pas. C'est le menuzcon.GLOB_DATA_SOUND_FROM_TICK_VALUE.
#Mais les booleans n'on pas la m�me signification.
#Y'a le boolean de la case � cocher du son. Et le boolean de "doit-on jouer des sons ou pas".
#Moi je dis que c'est pas les m�me, que d'abord que m�me que ouais.
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

        #Indique si on a r�ussi le chargement des fichiers sons.
        self.loadSoundSucess = False


    def loadSound(self, filename):
        """
        charge un fichier son

        entr�es :
            filename : String indiquant le nom complet du fichier son � charger.
                       Les sons doivent toutes �tre dans le sous-r�pertoire SOUND_DIRECTORY_NAME.

        plat-dessert :
            l'objet pygame.mixer.Sound contenant le son charg�
        """

        pathname = os.path.join(SOUND_DIRECTORY_NAME, filename)

        #Tentative de chargement du son. On quitte totalement le jeu comme un voleur si �a fail.
        #TRODO pour plus tard : ouais en fait �a throw pas d'exception quand le chargement fail.
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
            rien du tout. Mais la fonction peut modifier self.loadSoundSucess si on r�ussit.
        """

        #Fail si le biniou pour balancer les sons n'est pas disponible.
        if not pygame.mixer or not pygame.mixer.get_init():
            securedPrint("Impossible initialising ze sounds. Yep. Too bad.")
            return

        #dictionnaire qui contiendra tous les sons et groupes de sons.
        #cl� : identifiant du son ou groupe de son
        #valeur : tuple de 2 �l�ments.
        #          - nombre de son dans le groupe. (Ca peut �tre 1)
        #          - tuple avec tous les sons du groupe.  (objet pygame.mixe.Sound)
        #le nombre de sons, on pourrait l'obtenir avec len(tuple_des_sons).
        #Mais comme j'en ai besoin tout le temps de cette valeur, je pr�f�re la "pr�-calculer".
        self.dictSoundGroups = {}

        for soundGroupId, soundGroupInfo in DICT_SND_FILENAME.items():

            shortFileName, nbrSound = soundGroupInfo
            #liste qui contiendra tous les sons du groupe, quand on les aura charg�s.
            listSound = []

            #chargement des sons du groupe
            for soundIndex in xrange(nbrSound):

                #les sons d'un groupe ont des noms de fichiers semblables :
                #"nomCourt00.ogg", "nomCourt01.ogg", "nomCourt02.ogg", ...
                #Donc faut construire le nom de fichier complet � partir du nom
                #de fichier court, du num�ro du son �crit sur 2 chiffres, et de ".ogg". Voil�.
                longFileName = "".join((shortFileName,
                                        str(soundIndex).rjust(2, "0"),
                                        ".ogg"))

                #chargement du son, et rangement dans la liste.
                soundLoaded = self.loadSound(longFileName)
                listSound.append(soundLoaded)

            #rangement du groupe de son (avec le nombre de son) dans le dictionnaire.
            self.dictSoundGroups[soundGroupId] = (nbrSound, tuple(listSound))

        #bon, si on est arriv� jusqu'ici, y'a qu'� dire que tout va bien. (M�me si
        #c'est pas forc�ment vrai, puisque pas d'exception g�n�r�e par la fonction loadSound.)
        self.loadSoundSucess = True


    def playSound(self, soundGroupId):
        """
        choisit au hasard un son, parmi ceux du groupe sp�cifi� en param�tre,
        et joue ce son. "Tut tut pouet pouet Arrrggll spflark!"

        entr�es :
            soundGroupId : identifiant du son ou du groupe de son � jouer.
        """

        #on ne joue pas de son si le chargement des sons a rat�.
        if not self.loadSoundSucess:
            return

        #on ne joue pas de son si ils ont �t� d�sactiv�s par le joueur, lors de la config.
        if not self.soundEnabled:
            return

        #r�cup�ration des infos li�es au groupe de son indiqu� par le param�tre.
        (nbrSound, listSound) = self.dictSoundGroups[soundGroupId]

        if nbrSound > 1:
            #il y a plusieurs sons dans le groupe. On en choisit un au hasard.
            soundChosen = random.choice(listSound)

        else:
            #Il n'y a qu'un seul son dans le groupe. Pas la peine de se prendre la t�te �
            #faire du random. On le prend directement.
            soundChosen = listSound[0]

        #on joue le son. Hop, y'a une fonction toute faite pour �a. Youpi.
        soundChosen.play()


    def changeSoundEnablation(self, globDataSound):
        """
        active/d�sactive le son. En fonction de la global Data, qui provient,
        soit du fichier de sauvegarde/config, soit de la case � cocher du menu de config.
        """

        #conversion bool�en <- globData
        soundEnablation = DIC_SOUND_ENABLED_FROM_GLOB_DATA[globDataSound]
        #enregistrement du bool�en.
        self.soundEnabled = soundEnablation


#Instanciation imm�diate de la classe stockant tous les sons.
#Je suis pas fan de ce genre de truc. Mais l� c'est un peu oblig�. Sinon faut que
#je le passe en param�tre � plein plein de classe.
#Le chargement de tous les sons n'est pas effectu� d�s l'instanciation de la classe.
#Il faut le faire explicitement, en ex�cutant loadAllSounds. Tout cela se passe ailleurs.
theSoundYargler = SoundYargler()
