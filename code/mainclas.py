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

date de la derni�re relecture-commentage : 17/02/2011

la classe que c'est la classe principale. Youpiiii !!!

BIG FUCCKING ENORMOUS TRODO : Certains trucs communs sont sans arr�t pass�s en param
entre les diff�rents objets, tel des patates chaudes. C'est chiant.
Vaut mieux cr�er le truc commun d�s le d�but, le foutre dans un module quelconque,
et l'importer quand y'a besoin.
Ce genre de connerie est applicable � : les fonts, peut-�tre les images,
la variable mainclas.nbrErreur, et surement encore plein d'autres conneries.
Si je l'ai pas fait, c'est parce que je voulais pas trop faire des modules de
code qui initialise des trucs d�s le d�but qu'on les importe. Mais en fait c'est pas
sp�cialement mal comme truc. Bref. Onn fera mieux la prochaine fois !
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

        entr�es :
            forceWindowed : bool�an.
                 True : le jeu se lance forc�ment en mode windowed (pas plein �cran).
                 False : le jeu se lance selon le mode d�fini dans le fichier de sauvegarde,
                         ou bien selon le mode par d�faut si pas de fichier de sauvegarde.
        """

        #nombre d'erreur total qui a eu lieu durant la totalit� de toute l'ex�cution du jeu
        #m�me si euh... y'a des fois j'oublie de r�cup�rer les erreurs renvoy�es.
        self.nbrErreur = 0

        #chargement de toutes les polices de caract�res utilis�es par le jeu.
        #BIG TRODO : faut que ce soit des var globales, ces font. d�j� dit, mais je le redis.
        (self.dictFont, self.fontDefault, fontLoadOK) = loadFonts()

        #si le load des fonts a fail, des erreurs ons d�j� �t� balanc�es.
        #Y'a juste � augmenter le compteur.
        if not fontLoadOK:
            self.nbrErreur += 1

        #cr�ation de la classe pour sauver/charger les donn�es dans un fichier
        self.archivist = Archivist()
        #cr�ation de la classe qui g�re les scores des parties jou�es, et met � jour les stats.
        self.scoreManager = ScoreManager(self.archivist)

        # ------ tentative de chargement du fichier contenant les sauvegardes et la config. ------

        if self.archivist.loadArchive():

            self.archivistLoadOK = True

        else:

            #erreur lors du chargement du fichier.
            #(des messages d'erreur d�taill�s ont d�j� �t� envoy�s sur la sortie standard)
            self.nbrErreur += 1
            securedPrint(u"donc fail loadage. Meme si c'est deja dit")
            self.archivistLoadOK = False

        # ------ Initialisation de tout le bordel ------

        #ici, on devrait charger tous les sons. Mais comme �a met un peu de temps,
        #je pr�f�re le faire juste avant de commencer l'animation de pr�sentation
        #Comme �a, le joueur patiente devant un d�but d'image, au lieu de devant rien.
        #Donc, voir la classe prezAnim pour l'ex�cution de la fonction loadAllSounds.

        #en attendant, on active/d�sactive le son selon ce qui est indiqu�
        #dans le fichier de sauvegarde
        soundConfig = self.archivist.dicGlobData[GLOB_DATA_ID_SOUND]
        theSoundYargler.changeSoundEnablation(soundConfig)

        if forceWindowed:
            #Au moment de lancer le jeu, on a indiqu� dans les param�tre qu'on veut
            #obligatoirement le mode fen�tre. Donc on le prend, et paf.
            screenGlobData = SCREEN_WINDOWED
        else:
            #r�cup�ration du choix fen�tre/plein �cran, en fonction de ce qui est indiqu�
            #dans le fichier de sauvegarde.
            screenGlobData = self.archivist.dicGlobData[GLOB_DATA_ID_SCREEN]

        #chargement et mise en place de l'ic�ne de l'application.
        #on met doConversion � False, pour dire qu'on veut pas faire le convert de l'image
        #dans le mode graphique actuel. (Car on l'a pas encore �t� d�fini, ce mode graphique
        #actuel, h�h�). Ca aurait pu poser des probl�mes d'optimisation si �a avait �t�
        #une image du jeu. Mais l� en fait c'est l'ic�ne de l'application, donc osef.
        #
        #Il para�t qu'il mettre en place l'ic�ne le plus t�t possible, en particulier avant de
        #d�finir le mode graphique. Car sur Mac, on risque de voir appara�tre fugitivement
        #l'ic�ne serpent de pygame, avant l'ic�ne qu'on veut. Je teste �a et je vous le dit
        #tr�s bient�t. Yi haa.
        gamIcon = loadImg("gam_icon.gif", doConversion=False)
        pygame.display.set_icon(gamIcon)

        #cr�ation de l'objet pygame.Surface, dans laquelle on affichera le jeu, les menus, tout.
        self.screen = theGraphModeChanger.setGraphMode(screenGlobData)

        #Si l'archivist indique que le mode doit �tre plein �cran, et qu'on a forc�
        #le mode windowed, alors il y a un d�saccord entre le jeu et le fichier de
        #sauvegarde. On pourrait r�gler �a en r�actualisant le fichier de sauvegarde.
        #Sauf qu'on va pas le faire. Le mode fen�tr� forc�, c'est un peu une sorte
        #de "mode sans �chec", donc il faut �viter de faire des trucs risqu�es.
        #Tenter d'�crire des trucs dans un fichier, c'est risqu�. Voil�.
        #Par contre, il faut que la case � cocher "plein �cran" du menu principal soit en
        #accord avec le mode actuel. Mais �a, le MenuManagerMain s'en occupe

        #d�finition du titre de la fen�tre de jeu. Ne sert ps � grand chose, mais �a fait cool.
        pygame.display.set_caption(GAME_CAPTION)

        #cr�ation de l'objet permettant de lancer des parties
        self.theGame = Game(self.screen, self.scoreManager, self.fontDefault)
        #chargement des sprites n�cessaires pour jouer une partie.
        self.theGame.loadGameStuff()


    def mactPlaySeveralGames(self, dogDom):
        """
        fonction s'activant quand on clique sur le MenuElem "JOUER".
        Permet de jouer plusieurs parties les unes apr�s les autres.

        entr�es :
         - dogDom : boolean. Indique si le h�ros perd des vies ou pas.
        """

        #tuple contenant les messages d'ihm de cette fonction courante. (cataclop et prout)
        ihmsgInfo = ()

        while IHMSG_QUIT not in ihmsgInfo:

            #on enl�ve le curseur de souris pendant une partie. Pour pas g�ner le joueur.
            pygame.mouse.set_visible(0)

            # --- lancement d'une partie. Tadzam !! ---
            #on r�cup�re les messages d'ihm, et �ventuellement un nombre d'erreurs.
            param = (self.archivist.dicKeyMapping, dogDom)
            (ihmsgInfo, errorInGame) = self.theGame.playOneGame(*param)

            #sauvegarde des stats du joueur, qui ont �t� remise � jour
            #par cette partie qui vient d'�tre jou�e. (blablablabla bla bla)
            if not self.scoreManager.saveScoreInArchive():
                self.nbrErreur += 1

            #on remet le curseur visible. Pour que le joueur puisse cliquouiller.
            pygame.mouse.set_visible(1)

            #Les erreurs, on les enregistre. (Mais je sais pas quoi en foutre en fait).
            self.nbrErreur += errorInGame

            if IHMSG_QUIT not in ihmsgInfo:

                #y'a pas de message IHMSG_QUIT dans le tuple des messages d'ihm.
                #Ca veut dire que le joueur a peut-�tre envie de rejouer.
                #(en tout cas il est mort, sinon la partie se serait pas arr�t�e)
                #Donc on affiche l'�cran de mort du h�ros, avec les scores et tout,
                #et on lui demande si il veut refaire une partie ou pas.

                #r�cup�ration des scores, pour les transmettre au menu de mort du h�ros
                param = (self.scoreManager.currentMagiBurst,
                         self.scoreManager.currentTotMagiKilled,
                         self.scoreManager.currentScore)

                self.menuHeroDead.updateMenuTextStat(*param)

                #affichage du menu de mort. Si le joueur veut rejouer,
                #on r�cup�rera IHMSG_PLAY_ONCE_MORE dans le tuple de message d'ihm renvoy�.
                ihmsgInfoOfHeroDeadMenu = self.menuHeroDead.handleMenu()

                if IHMSG_PLAY_ONCE_MORE not in ihmsgInfoOfHeroDeadMenu:
                    #le joueur veut pas rejouer. On s'auto-ajoute le QUIT dans
                    #le tuple des messages d'ihm courant. Ca va arr�ter la boucle.
                    ihmsgInfo += (IHMSG_QUIT, )

                if IHMSG_TOTALQUIT in ihmsgInfoOfHeroDeadMenu:
                    #Le joueur a fait Alt-F4 pendant le menu de mort,
                    #propagation du message TOTAL_QUIT.
                    ihmsgInfo += (IHMSG_TOTALQUIT, )

                #si le joueur veut rejouer, �a va refaire la boucle une fois de plus,
                #et relancer une autre partie.

        #le joueur a fait Alt-F4 pendant le jeu, ou pendant le menu de mort.
        #(on sait pas exactement d'o� �a vient mais on s'en fout).
        #propagation du TOTALQUIT vers la fonction appelante.
        if IHMSG_TOTALQUIT in ihmsgInfo:
            return (IHMSG_QUIT, IHMSG_TOTALQUIT)

        #On a donc fini la boucle permettant de jouer une ou plusieurs parties. Y'a juste �
        #envoyer l'info indiquant qu'on doit redessiner le menu principal.
        return (IHMSG_REDRAW_MENU, )


    def doFirstTimeLaunch(self, ihmsgInfo):
        """
        ex�cute les actions � faire lors du premier lancement du jeu. Y'a quelques menus
        en plus � afficher. Et d'autres trucs par rapport au nom que le joueur a saisi.

        entr�es :
            ihmsgInfo : tuple de message d'ihm en cours. (renvoy� par des menus
                        activ�s pr�c�demment).

        plat-dessert :
            ihmsgInfo : tuple de message d'ihm renvoy� par les menus qu'on active
                        dans cette fonction.

        C'est g�r� de mani�re un peu bancalaire, cet ihmsgInfo. A d'autre endroits du code, non.
        Mais l� si.
        """

        #on ex�cute les menus un par un. On fait un gros quittage de la fonction si
        #y'a eu un TOTALQUIT dans l'un des menus.
        #J'aurais pu faire une boucle avec tout �a. Mais l'activation d'un menu c'est
        #une fonction d'assez "haut niveau", alors j'ai pr�f�r� toutes les �crire explicitement.

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

        #si le joueur a fait echap, on quittera tout de suite. (zarb, mais �a se tient.)
        if IHMSG_CANCEL in ihmsgInfo:
            ihmsgInfo += (IHMSG_TOTALQUIT, )

        #quittage si le joueur a fait Alt-F4 pendant la saisie du nom.
        if IHMSG_TOTALQUIT in ihmsgInfo: return ihmsgInfo

        #r�cup�ration du nom saisi par le joueur. (c'est une cha�ne unicode)
        nameTyped = self.dicAllMenu[MENU_ENTER_NAME].nameTyped

        #cr�ation du fichier de sauvegarde, avec les valeurs initiales.
        #On y enregistre aussi le fait d'avoir activ� ou pas le edoMedoG
        if not self.archivist.initAndSaveNewArchive(nameTyped):
            #si la sauvegarde a fail, un message a �t� envoy�. On se rajoute une erreur.
            #On passe quand m�me � la suite, pour permettre de jouer.
            self.nbrErreur += 1

        #affichage d'un petit menu � la con avec un vague texte, si le joueur
        #a saisi un autre nom que le nom par d�faut.
        if nameTyped != NAME_HERO:
            #faut transmettre au menu le nom qu'a �t� saisi, car c'est pas le m�me texte selon.
            self.dicAllMenu[MENU_NAME_IS_A_LIE].setNameTyped(nameTyped)
            ihmsgInfo = self.dicAllMenu[MENU_NAME_IS_A_LIE].handleMenu()

            #quittage total si le joueur a fait Alt-F4 pendant ce menu � la con.
            if IHMSG_TOTALQUIT in ihmsgInfo: return ihmsgInfo

        #activation de l'option edoGedoM dans le menu principal, si le nom saisi correspond.
        if self.archivist.isDogDomEdocValid(nameTyped):
            self.dicAllMenu[MENU_MAIN].addDogDom()

        #on renvoie un tuple de message d'ihm avec rien dedans.
        #L'important c'est que y'ait pas le TOTAL_QUIT dedans.
        return IHMSG_VOID


    def main(self):
        """
        la fonction main, m�me si c'est pas la vraie fonction main, parce qu'elle est dans
        la classe zemain.py. Oh on s'en fout. C'est bizarre mais c'est comme �a. L� !
        """

        #classe effectuant l'animation � la con de pr�sentation du jeu.
        prezAnim = PresentationAnim(self.screen, self.fontDefault)
        #et lancement de cette superbe animation.
        prezAnim.launchAnim()

        #cr�ation du dictionnaire contenant tous les menus, que la fonction g�n�ratrice
        #de tous les menus a gentiment cr�� pour nous (enfin surtout moi, pas vous) (nawak).

        param = (self.dictFont, self.screen, self.mactPlaySeveralGames,
                 self.archivist, self.scoreManager,
                 prezAnim.imgBgMainMenu, prezAnim.imgTitle)

        self.dicAllMenu = generateAllMenuManager(*param)

        #ce menu-l�, je me l'enregistre avec un nom plus court et plus clair, car j'en ai besoin
        #pour plus tard.
        self.menuHeroDead = self.dicAllMenu[MENU_HERO_DEAD]

        #l'animation de pr�sentation est termin�e, mais son image finale est toujours
        #affich�e. On attend que le joueur appuie sur une touche, ou clique,
        #pour passer � la suite. (Au pire, �a passe � la suite tout seul au bout d'un moment)
        ihmsgInfo = self.dicAllMenu[MENU_PRESS_ANY_KEY].handleMenu()

        if not self.archivistLoadOK:

            #le chargement du fichier de sauvegarde a foir�, pour une raison ou une autre.
            #On tente d'en recr�er un avec des infos par d�faut, et de le sauvegarder,
            #histoire de se refoutre d'aplomb pour les prochaines ex�cutions du jeu.
            if not self.archivist.initAndSaveNewArchive():
                #Si le resauvegardage foire aussi, c'est vraiment la d�che.
                #(des messages d'erreur ont d�j� �t� balanc� � ce sujet).
                #on passe quand m�me � la suite. Ca permettra de jouer.
                self.nbrErreur += 1

        if self.archivist.firstTimeLaunch:

            #ex�cution de tous les trucs qu'il faut faire lors du premier lancement du jeu.
            ihmsgInfo = self.doFirstTimeLaunch(ihmsgInfo)

        else:

            #activation de l'option edoGedoM dans le menu principal,
            #si le nom stock� dans les globData correspond.
            if self.archivist.isDogDomEnabledFromGlobData():
                self.dicAllMenu[MENU_MAIN].addDogDom()

        #On v�rifie si y'a pas eu de demande de quittage durant tous le bazar pr�c�demment fait.
        if IHMSG_TOTALQUIT not in ihmsgInfo:

            #lancement du menu principal
            self.dicAllMenu[MENU_MAIN].handleMenu()

        #et apr�s on se barre. Voil�.

        #affichage d'un dernier message pour signaler les erreurs.
        #j'aimerais bien mettre un truc du genre "appuyez sur Entr�e pour quitter",
        #mais je suis pas sur de faire un truc qui marche comme il faut et multi-plateformes.
        #donc j'ai laiss� tomber. De toutes fa�on y'aura jamais d'erreur. Na !!
        #TRODO pour plus tard : les messages sur stdout + dans un fichier texte
        #Et � la fin, on ouvre le fichier texte avec l'appli par d�faut.
        if self.nbrErreur > 0:
            securedPrint(u"Il y a eu des erreurs durant le jeu.")

