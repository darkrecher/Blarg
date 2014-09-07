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

date de la derni�re relecture-commentage : 28/03/2011

grosse fonction qui cr�e tous les menus.
"""

import pygame

from common   import (loadImg, loadImgInDict, LANG_DEFAULT,
                      FONT_DEFAULT_NAME, FONT_LITTLE_SIZE, FONT_DEFAULT_SIZE,
                      LIST_TRANSP_FOCUS, buildListImgLight)

from archiv   import GLOB_DATA_ID_LANG
from menuzwak import MenuManagerWaitOrPressAnyKey
from menuzdea import MenuManagerHeroDead
from menuzcre import MenuManagerCredits
from menuznam import MenuManagerEnterName
from menuzsto import MenuManagerStory
from menuzman import MenuManagerManual
from menuzcon import MenuManagerConfig
from menuzsco import MenuManagerHighScore
from menuzpof import MenuManagerNameIsALie
from menuzmai import MenuManagerMain

#moi j'aime bien importer plein de trucs, je trouve �a cool.
from menucomn import (MENU_MAIN, MENU_CREDITS, MENU_HERO_DEAD, MENU_ENTER_NAME,
                      MENU_STORY, MENU_MANUAL, MENU_CONFIG, MENU_HISCORE,
                      MENU_PRESS_ANY_KEY, MENU_NAME_IS_A_LIE,
                      IMG_BG_MAIN, IMG_TITLE_MAIN, IMG_BG_BLARG,
                      IMG_FLAG_FRENCH, IMG_FLAG_ENGLISH, IMG_TICK_TRUE,
                      IMG_TICK_FALSE, IMG_CRED_SCRL_UP, IMG_CRED_SCRL_DOWN,
                      IMG_BACK, IMG_FRAME_NAME, IMG_BUTT_OK, IMG_MANUAL,
                      IMG_BUTT_RESET, IMG_DEDICACE,
                      changeLanguageOnAllMenu)

#liste de correspondance entre l'identifiant d'une image utilis�e pour les menus et l'ihm,
#et le nom du fichier image correspondant � charger (au format PNG).
#liste de tuple de 2 �l�ments :
# - identifiant de l'image. ils sont tous d�finis et d�crits dans menucomn.py
# - nom du fichier court � charger. (Pour avoir le nom long, ajouter ".png").
#Toutes ces images sont � charger sans key transparency.
LIST_IMG_MENU_FILENAMES = (
 #IMG_BG_MAIN    : cette image n'est pas charg� par la classe. Elle a �t� fabriqu�e avant
 #IMG_TITLE_MAIN : cette image, pareil (pis en plus elle a une key transparency celle l�.
 (IMG_BG_BLARG,       "bgdeath"),
 (IMG_FLAG_FRENCH,    "drapalfr"),
 (IMG_FLAG_ENGLISH,   "drapalen"),
 (IMG_TICK_TRUE,      "tickboxb"),
 (IMG_TICK_FALSE,     "tickboxa"),
 (IMG_CRED_SCRL_UP,   "txtscrup"),
 (IMG_CRED_SCRL_DOWN, "txtscrdo"),
 (IMG_BACK,           "back"),
 (IMG_FRAME_NAME,     "framname"),
 (IMG_BUTT_OK,        "buttok"),
 (IMG_MANUAL,         "manual"),
 (IMG_BUTT_RESET,     "buttconf"),
)

#Lui il est pas avec les autres, parce que faut charger l'image avec une key transparency � noir.
IMG_DEDICACE_LONG_FILENAME = "dedicace.png"

#I hate my "real" job !



def generateAllMenuManager(dictFont, screen, funcMactPlaySeveralGames,
                           archivist, scoreManager, imgBgMainMenu, imgTitle):
    """
    Cration de tous les menus. (Oui, j'ai �crit "cration", also sprach ma proffe d'histoire g�o.

    entr�es :

        dictFont : dictionnaire contenant toutes les polices de caract�re du jeu.
                   (m�me si en vrai y'en a que deux. (Enfin une avec 2 tailles)).

        screen : objet pygame.Surface. Surface principale sur laquelle s'affiche le jeu
                 (en plein �cran ou en fen�tre).

        funcMactPlaySeveralGames : r�f�rence vers la fonction permettant de lancer
                                   une ou plusieurs parties du jeu. (Faut la refiler
                                   au menu principal, vu que c'est lui qui lance les parties).

        archivist : classe �poneyime, permettant d'enregistrer et recharger le fichier
                    de sauvegarde et de config.

        scoreManager : classe �poneyime, qui g�re les scores.

        imgBgMainMenu : pygame.Surface. Image de background des menus. D�j� assembl�e durant
                        l'animation de pr�sentation, et assombrie.

        imgTitle : pygame.Surface. Image du titre "Blarg" en jaune-orange.

    plat-dessert :

        dicAllMenu. dictionnaire contenant tous les menus.
         - cl� : identifiant du menu (variable de type MENU_*)
         - valeur : instance d'une classe h�rit�e de MenuManager. Ah que c'est le menu quoi.
    """

    #r�cup�ration des 2 fonts, � partir du dictionnaire. (C'est vraiment g�r� n'importe
    #comment ce truc. On fera mieux la prochaine fois).
    fontDefault = dictFont[FONT_DEFAULT_NAME][FONT_DEFAULT_SIZE]
    fontLittle = dictFont[FONT_DEFAULT_NAME][FONT_LITTLE_SIZE]

    #chargement des fichiers images utilis�s pour les menus, et remplissage
    #du dictionnaire contenant justement les images des menus.
    dicImg = loadImgInDict(LIST_IMG_MENU_FILENAMES, colorkey=None)

    #compl�ment de remplissage du dico des images des menus, avec ce qu'on a mis en param.
    dicImg[IMG_BG_MAIN] = imgBgMainMenu
    dicImg[IMG_TITLE_MAIN] = imgTitle

    #Et encore compl�ment de dico, avec encore une image charg�e depuis un fichier.
    #Je pouvais pas l'inclure dans le loadImgInDict ci-dessus, car la transparency est pas la
    #m�me. (cette image a une key transparency sur le noir. Les autres n'en ont pas du tout.)
    dicImg[IMG_DEDICACE] = loadImg(IMG_DEDICACE_LONG_FILENAME)

    #construction du dictionnaire de liste d'images utilis�es pour les cases � cocher.
    #voir constructeur MenuSensitiveTick.__init__ pour la structure de ce dico.
    dicTickImage = {
        False : buildListImgLight(dicImg[IMG_TICK_FALSE], LIST_TRANSP_FOCUS),
        True  : buildListImgLight(dicImg[IMG_TICK_TRUE],  LIST_TRANSP_FOCUS),
    }

    #dictionnaire qui contiendra tous les menus.
    dicAllMenu = {}

    #pour tous les blocs de code � venir (jusqu'� "Menu principal"), on effectue les
    #actions suivantes :
    # - construction de la liste des param�tres � passer au constructeur du MenuManager
    # - appel du constructeur du MenuManager, pour cr�er l'instance de la classe.
    # - rangement de cette instance dans dicAllMenu, avec pour cl� l'identifiant de menu
    #   correspondant
    #
    #De cette mani�re, on va cr�er une instance pour chaque classe h�rit�e de MenuManager.

    # --- menu Credits ---

    param = (screen, dicImg, fontDefault, fontLittle)

    menuCredits = MenuManagerCredits(*param)
    dicAllMenu[MENU_CREDITS] = menuCredits

    # --- menu affichant le h�ros mort transform� en potion de mana ---

    param = (screen, dicImg, fontDefault)

    menuHeroDead = MenuManagerHeroDead(*param)
    dicAllMenu[MENU_HERO_DEAD] = menuHeroDead

    # --- menu Frame Name (saisie du nom du joueur au d�but) ---

    param = (screen, dicImg, fontDefault)

    menuEnterName = MenuManagerEnterName(*param)
    dicAllMenu[MENU_ENTER_NAME] = menuEnterName

    # --- menu qu'affiche le scrolling de l'histoire. (Wouu, y'a un vrai sc�nario) ---

    param = (screen, dicImg, fontLittle)

    menuStory = MenuManagerStory(*param)
    dicAllMenu[MENU_STORY] = menuStory

    # --- menu affichant le manuel du jeu (m�me si en vrai c'est qu'une image � l'arrache) ---

    param = (screen, dicImg, fontDefault, fontLittle, archivist)

    menuManual = MenuManagerManual(*param)
    dicAllMenu[MENU_MANUAL] = menuManual

    # --- menu permettant de configurer les touches et le son ---

    param = (screen, dicImg, fontDefault, fontLittle,
             dicTickImage, archivist)

    menuConfig = MenuManagerConfig(*param)
    dicAllMenu[MENU_CONFIG] = menuConfig

    # --- menu affichant les high scores ---

    param = (screen, dicImg, fontDefault, fontLittle, archivist)

    menuHighScore = MenuManagerHighScore(*param)
    dicAllMenu[MENU_HISCORE] = menuHighScore

    # --- menu affichant un vague blabla apr�s que le joueur ait saisi son nom. ---

    param = (screen, dicImg, fontLittle, archivist)

    menuNameIsALie = MenuManagerNameIsALie(*param)
    dicAllMenu[MENU_NAME_IS_A_LIE] = menuNameIsALie

    # --- menu qu'affiche rien et qu'attend juste qu'on appuyasse sur une touchasse ---

    param = (screen, 100)

    menuPressAnyKey = MenuManagerWaitOrPressAnyKey(*param)
    dicAllMenu[MENU_PRESS_ANY_KEY] = menuPressAnyKey

    # --- menu principal ---

    param = (screen, dicImg, fontDefault, fontLittle, dicTickImage,
             archivist, scoreManager, funcMactPlaySeveralGames,
             dicAllMenu)

    menuManagerMain = MenuManagerMain(*param)
    dicAllMenu[MENU_MAIN] = menuManagerMain

    # --- Voil�, c'est fini. On a cr�� tous les menus existants.

    #r�cup�ration du langage courant, indiqu� dans le fichier de sauvegarde de la config.
    currentLang = archivist.dicGlobData[GLOB_DATA_ID_LANG]

    if currentLang != LANG_DEFAULT:
        #le langage courant n'est pas le langage par d�faut (celui avec lequel tous les
        #menus ont �t� cr��s). Il faut donc pr�venir tous les menus existants qu'ils
        #doivent faire changer leur langue � tous leurs MenuElem. Et on indique le bon
        #langage, celui qu'on a trouv� dans le fichier de sauvegarde. Of course.
        changeLanguageOnAllMenu(currentLang, dicAllMenu)

    return dicAllMenu
