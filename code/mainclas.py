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

date de la dernière relecture-commentage : 17/02/2011

la classe que c'est la classe principale. Youpiiii !!!

BIG FUCCKING ENORMOUS TRODO : Certains trucs communs sont sans arrêt passés en param
entre les différents objets, tel des patates chaudes. C'est chiant.
Vaut mieux créer le truc commun dès le début, le foutre dans un module quelconque,
et l'importer quand y'a besoin.
Ce genre de connerie est applicable à : les fonts, peut-être les images,
la variable mainclas.nbrErreur, et surement encore plein d'autres conneries.
Si je l'ai pas fait, c'est parce que je voulais pas trop faire des modules de
code qui initialise des trucs dès le début qu'on les importe. Mais en fait c'est pas
spécialement mal comme truc. Bref. Onn fera mieux la prochaine fois !
"""

import pygame

from common import (securedPrint, SCREEN_RECT, loadFonts, GAME_CAPTION,
                    loadImg, SCREEN_WINDOWED, NAME_HERO,
                    IHMSG_QUIT, IHMSG_TOTALQUIT, IHMSG_CANCEL, IHMSG_VOID,
                    IHMSG_REDRAW_MENU, IHMSG_PLAY_ONCE_MORE)

from menucomn import (MENU_MAIN, MENU_ENTER_NAME, MENU_STORY, MENU_MANUAL,
                      MENU_PRESS_ANY_KEY, MENU_NAME_IS_A_LIE, MENU_HERO_DEAD,
                      theGraphModeChanger)

from archiv   import Archivist, GLOB_DATA_ID_SCREEN, GLOB_DATA_ID_SOUND
from scoremn  import ScoreManager
from game     import Game
from menugen  import generateAllMenuManager
from prezanim import PresentationAnim
from yargler  import theSoundYargler



class MainClass():
    """
    hohoho. La super mega classe avec le code principal dedans
    """

    def __init__(self, forceWindowed):
        """
        constructeur. (thx captain obvious)

        entrées :
            forceWindowed : booléan.
                 True : le jeu se lance forcément en mode windowed (pas plein écran).
                 False : le jeu se lance selon le mode défini dans le fichier de sauvegarde,
                         ou bien selon le mode par défaut si pas de fichier de sauvegarde.
        """

        #nombre d'erreur total qui a eu lieu durant la totalité de toute l'exécution du jeu
        #même si euh... y'a des fois j'oublie de récupérer les erreurs renvoyées.
        self.nbrErreur = 0

        #chargement de toutes les polices de caractères utilisées par le jeu.
        #BIG TRODO : faut que ce soit des var globales, ces font. déjà dit, mais je le redis.
        (self.dictFont, self.fontDefault, fontLoadOK) = loadFonts()

        #si le load des fonts a fail, des erreurs ons déjà été balancées.
        #Y'a juste à augmenter le compteur.
        if not fontLoadOK:
            self.nbrErreur += 1

        #création de la classe pour sauver/charger les données dans un fichier
        self.archivist = Archivist()
        #création de la classe qui gère les scores des parties jouées, et met à jour les stats.
        self.scoreManager = ScoreManager(self.archivist)

        # ------ tentative de chargement du fichier contenant les sauvegardes et la config. ------

        if self.archivist.loadArchive():

            self.archivistLoadOK = True

        else:

            #erreur lors du chargement du fichier.
            #(des messages d'erreur détaillés ont déjà été envoyés sur la sortie standard)
            self.nbrErreur += 1
            securedPrint(u"donc fail loadage. Meme si c'est deja dit")
            self.archivistLoadOK = False

        # ------ Initialisation de tout le bordel ------

        #ici, on devrait charger tous les sons. Mais comme ça met un peu de temps,
        #je préfère le faire juste avant de commencer l'animation de présentation
        #Comme ça, le joueur patiente devant un début d'image, au lieu de devant rien.
        #Donc, voir la classe prezAnim pour l'exécution de la fonction loadAllSounds.

        #en attendant, on active/désactive le son selon ce qui est indiqué
        #dans le fichier de sauvegarde
        soundConfig = self.archivist.dicGlobData[GLOB_DATA_ID_SOUND]
        theSoundYargler.changeSoundEnablation(soundConfig)

        if forceWindowed:
            #Au moment de lancer le jeu, on a indiqué dans les paramètre qu'on veut
            #obligatoirement le mode fenêtre. Donc on le prend, et paf.
            screenGlobData = SCREEN_WINDOWED
        else:
            #récupération du choix fenêtre/plein écran, en fonction de ce qui est indiqué
            #dans le fichier de sauvegarde.
            screenGlobData = self.archivist.dicGlobData[GLOB_DATA_ID_SCREEN]

        #chargement et mise en place de l'icône de l'application.
        #on met doConversion à False, pour dire qu'on veut pas faire le convert de l'image
        #dans le mode graphique actuel. (Car on l'a pas encore été défini, ce mode graphique
        #actuel, héhé). Ca aurait pu poser des problèmes d'optimisation si ça avait été
        #une image du jeu. Mais là en fait c'est l'icône de l'application, donc osef.
        #
        #Il paraît qu'il faut mettre en place l'icône le plus tôt possible, en particulier
        #avant de définir le mode graphique. Car sur Mac, on risque de voir apparaître
        #fugitivement l'icône serpent de pygame, avant l'icône qu'on veut. Je teste ça et
        #je vous le dit très bientôt. Yi haa.
        gamIcon = loadImg("gam_icon.gif", doConversion=False)
        pygame.display.set_icon(gamIcon)

        #création de l'objet pygame.Surface, dans laquelle on affichera le jeu, les menus, tout.
        self.screen = theGraphModeChanger.setGraphMode(screenGlobData)

        #Si l'archivist indique que le mode doit être plein écran, et qu'on a forcé
        #le mode windowed, alors il y a un désaccord entre le jeu et le fichier de
        #sauvegarde. On pourrait régler ça en réactualisant le fichier de sauvegarde.
        #Sauf qu'on va pas le faire. Le mode fenêtré forcé, c'est un peu une sorte
        #de "mode sans échec", donc il faut éviter de faire des trucs risquées.
        #Tenter d'écrire des trucs dans un fichier, c'est risqué. Voilà.
        #Par contre, il faut que la case à cocher "plein écran" du menu principal soit en
        #accord avec le mode actuel. Mais ça, le MenuManagerMain s'en occupe

        #définition du titre de la fenêtre de jeu. Ne sert pas à grand chose, mais ça fait cool.
        pygame.display.set_caption(GAME_CAPTION)

        #création de l'objet permettant de lancer des parties
        self.theGame = Game(self.screen, self.scoreManager, self.fontDefault)
        #chargement des sprites nécessaires pour jouer une partie.
        self.theGame.loadGameStuff()


    def mactPlaySeveralGames(self, dogDom):
        """
        fonction s'activant quand on clique sur le MenuElem "JOUER".
        Permet de jouer plusieurs parties les unes après les autres.

        entrées :
         - dogDom : boolean. Indique si le héros perd des vies ou pas.
        """

        #tuple contenant les messages d'ihm de cette fonction courante. (cataclop et prout)
        ihmsgInfo = ()

        while IHMSG_QUIT not in ihmsgInfo:

            #on enlève le curseur de souris pendant une partie. Pour pas gêner le joueur.
            pygame.mouse.set_visible(0)

            # --- lancement d'une partie. Tadzam !! ---
            #on récupère les messages d'ihm, et éventuellement un nombre d'erreurs.
            param = (self.archivist.dicKeyMapping, dogDom)
            (ihmsgInfo, errorInGame) = self.theGame.playOneGame(*param)

            #sauvegarde des stats du joueur, qui ont été remise à jour
            #par cette partie qui vient d'être jouée. (blablablabla bla bla)
            if not self.scoreManager.saveScoreInArchive():
                self.nbrErreur += 1

            #on remet le curseur visible. Pour que le joueur puisse cliquouiller.
            pygame.mouse.set_visible(1)

            #Les erreurs, on les enregistre. (Mais je sais pas quoi en foutre en fait).
            self.nbrErreur += errorInGame

            if IHMSG_QUIT not in ihmsgInfo:

                #y'a pas de message IHMSG_QUIT dans le tuple des messages d'ihm.
                #Ca veut dire que le joueur a peut-être envie de rejouer.
                #(en tout cas il est mort, sinon la partie se serait pas arrêtée)
                #Donc on affiche l'écran de mort du héros, avec les scores et tout,
                #et on lui demande si il veut refaire une partie ou pas.

                #récupération des scores, pour les transmettre au menu de mort du héros
                param = (self.scoreManager.currentMagiBurst,
                         self.scoreManager.currentTotMagiKilled,
                         self.scoreManager.currentScore)

                self.menuHeroDead.updateMenuTextStat(*param)

                #affichage du menu de mort. Si le joueur veut rejouer,
                #on récupérera IHMSG_PLAY_ONCE_MORE dans le tuple de message d'ihm renvoyé.
                ihmsgInfoOfHeroDeadMenu = self.menuHeroDead.handleMenu()

                if IHMSG_PLAY_ONCE_MORE not in ihmsgInfoOfHeroDeadMenu:
                    #le joueur veut pas rejouer. On s'auto-ajoute le QUIT dans
                    #le tuple des messages d'ihm courant. Ca va arrêter la boucle.
                    ihmsgInfo += (IHMSG_QUIT, )

                if IHMSG_TOTALQUIT in ihmsgInfoOfHeroDeadMenu:
                    #Le joueur a fait Alt-F4 pendant le menu de mort,
                    #propagation du message TOTAL_QUIT.
                    ihmsgInfo += (IHMSG_TOTALQUIT, )

                #si le joueur veut rejouer, ça va refaire la boucle une fois de plus,
                #et relancer une autre partie.

        #le joueur a fait Alt-F4 pendant le jeu, ou pendant le menu de mort.
        #(on sait pas exactement d'où ça vient mais on s'en fout).
        #propagation du TOTALQUIT vers la fonction appelante.
        if IHMSG_TOTALQUIT in ihmsgInfo:
            return (IHMSG_QUIT, IHMSG_TOTALQUIT)

        #On a donc fini la boucle permettant de jouer une ou plusieurs parties. Y'a juste à
        #envoyer l'info indiquant qu'on doit redessiner le menu principal.
        return (IHMSG_REDRAW_MENU, )


    def doFirstTimeLaunch(self, ihmsgInfo):
        """
        exécute les actions à faire lors du premier lancement du jeu. Y'a quelques menus
        en plus à afficher. Et d'autres trucs par rapport au nom que le joueur a saisi.

        entrées :
            ihmsgInfo : tuple de message d'ihm en cours. (renvoyé par des menus
                        activés précédemment).

        plat-dessert :
            ihmsgInfo : tuple de message d'ihm renvoyé par les menus qu'on active
                        dans cette fonction.

        C'est géré de manière un peu bancalaire, cet ihmsgInfo. A d'autre endroits du code, non.
        Mais là si.
        """

        #on exécute les menus un par un. On fait un gros quittage de la fonction si
        #y'a eu un TOTALQUIT dans l'un des menus.
        #J'aurais pu faire une boucle avec tout ça. Mais l'activation d'un menu c'est
        #une fonction d'assez "haut niveau", alors j'ai préféré toutes les écrire explicitement.

        if IHMSG_TOTALQUIT in ihmsgInfo: return ihmsgInfo

        #l'histoire du jeu.
        ihmsgInfo = self.dicAllMenu[MENU_STORY].handleMenu()
        if IHMSG_TOTALQUIT in ihmsgInfo: return ihmsgInfo

        #les touches de clavier, pour jouer
        ihmsgInfo = self.dicAllMenu[MENU_MANUAL].handleMenu()
        if IHMSG_TOTALQUIT in ihmsgInfo: return ihmsgInfo

        #on demande au joueur de saisir un nom
        ihmsgInfo = self.dicAllMenu[MENU_ENTER_NAME].handleMenu()
        if IHMSG_TOTALQUIT in ihmsgInfo: return ihmsgInfo

        #si le joueur a fait echap, on quittera tout de suite. (zarb, mais ça se tient.)
        if IHMSG_CANCEL in ihmsgInfo:
            ihmsgInfo += (IHMSG_TOTALQUIT, )

        #quittage si le joueur a fait Alt-F4 pendant la saisie du nom.
        if IHMSG_TOTALQUIT in ihmsgInfo: return ihmsgInfo

        #récupération du nom saisi par le joueur. (c'est une chaîne unicode)
        nameTyped = self.dicAllMenu[MENU_ENTER_NAME].nameTyped

        #création du fichier de sauvegarde, avec les valeurs initiales.
        #On y enregistre aussi le fait d'avoir activé ou pas le edoMedoG
        if not self.archivist.initAndSaveNewArchive(nameTyped):
            #si la sauvegarde a fail, un message a été envoyé. On se rajoute une erreur.
            #On passe quand même à la suite, pour permettre de jouer.
            self.nbrErreur += 1

        #affichage d'un petit menu à la con avec un vague texte, si le joueur
        #a saisi un autre nom que le nom par défaut.
        if nameTyped != NAME_HERO:
            #faut transmettre au menu le nom qu'a été saisi, car c'est pas le même texte selon.
            self.dicAllMenu[MENU_NAME_IS_A_LIE].setNameTyped(nameTyped)
            ihmsgInfo = self.dicAllMenu[MENU_NAME_IS_A_LIE].handleMenu()

            #quittage total si le joueur a fait Alt-F4 pendant ce menu à la con.
            if IHMSG_TOTALQUIT in ihmsgInfo: return ihmsgInfo

        #activation de l'option edoGedoM dans le menu principal, si le nom saisi correspond.
        if self.archivist.isDogDomEdocValid(nameTyped):
            self.dicAllMenu[MENU_MAIN].addDogDom()

        #on renvoie un tuple de message d'ihm avec rien dedans.
        #L'important c'est que y'ait pas le TOTAL_QUIT dedans.
        return IHMSG_VOID


    def main(self):
        """
        la fonction main, même si la vraie fonction main est en fait dans la classe zemain.py.
        Oh on s'en fout. C'est bizarre mais c'est comme ça. Là !
        """

        #classe effectuant l'animation à la con de présentation du jeu.
        prezAnim = PresentationAnim(self.screen, self.fontDefault)
        #et lancement de cette superbe animation.
        prezAnim.launchAnim()

        #création du dictionnaire contenant tous les menus, que la fonction génératrice
        #de tous les menus a gentiment créé pour nous (enfin surtout moi, pas vous) (nawak).

        param = (self.dictFont, self.screen, self.mactPlaySeveralGames,
                 self.archivist, self.scoreManager,
                 prezAnim.imgBgMainMenu, prezAnim.imgTitle)

        self.dicAllMenu = generateAllMenuManager(*param)

        #ce menu-là, je me l'enregistre avec un nom plus court et plus clair, car j'en ai besoin
        #pour plus tard.
        self.menuHeroDead = self.dicAllMenu[MENU_HERO_DEAD]

        #l'animation de présentation est terminée, mais son image finale est toujours
        #affichée. On attend que le joueur appuie sur une touche, ou clique,
        #pour passer à la suite. (Au pire, ça passe à la suite tout seul au bout d'un moment)
        ihmsgInfo = self.dicAllMenu[MENU_PRESS_ANY_KEY].handleMenu()

        if not self.archivistLoadOK:

            #le chargement du fichier de sauvegarde a foiré, pour une raison ou une autre.
            #On tente d'en recréer un avec des infos par défaut, et de le sauvegarder,
            #histoire de se refoutre d'aplomb pour les prochaines exécutions du jeu.
            if not self.archivist.initAndSaveNewArchive():
                #Si le resauvegardage foire aussi, c'est vraiment la dèche.
                #(des messages d'erreur ont déjà été balancé à ce sujet).
                #on passe quand même à la suite. Ca permettra de jouer.
                self.nbrErreur += 1

        if self.archivist.firstTimeLaunch:

            #exécution de tous les trucs qu'il faut faire lors du premier lancement du jeu.
            ihmsgInfo = self.doFirstTimeLaunch(ihmsgInfo)

        else:

            #activation de l'option edoGedoM dans le menu principal,
            #si le nom stocké dans les globData correspond.
            if self.archivist.isDogDomEnabledFromGlobData():
                self.dicAllMenu[MENU_MAIN].addDogDom()

        #On vérifie si y'a pas eu de demande de quittage durant tous le bazar précédemment fait.
        if IHMSG_TOTALQUIT not in ihmsgInfo:

            #lancement du menu principal
            self.dicAllMenu[MENU_MAIN].handleMenu()

        #et après on se barre. Voilà.

        #affichage d'un dernier message pour signaler les erreurs.
        #j'aimerais bien mettre un truc du genre "appuyez sur Entrée pour quitter",
        #mais je suis pas sur de faire un truc qui marche comme il faut et multi-plateformes.
        #donc j'ai laissé tomber. De toutes façon y'aura jamais d'erreur. Na !!
        #TRODO pour plus tard : les messages sur stdout + dans un fichier texte
        #Et à la fin, on ouvre le fichier texte avec l'appli par défaut.
        if self.nbrErreur > 0:
            securedPrint(u"Il y a eu des erreurs durant le jeu.")

