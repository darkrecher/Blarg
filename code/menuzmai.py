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

date de la derni�re relecture-commentage : 27/03/2011

Menu principal avec la principalitude des choses eud'dans.

bon c'est le bordel l�. On va essayer de ranger un peu tout �a.

mact : menuAction : fonction de type funcAction, qu'on binde sur un �l�ment de menu
(par ex : un bouton)

mbutt :     MenuElem de type bouton text (MenuSensitiveText)
mbuttLink : MenuElem de type bouton text (MenuSensitiveText), qui fait un lien vers un site web.
mbuti : MenuElem de type bouton image (MenuSensitiveImage)
mkey :  MenuElem de type MenuSensitiveKey

En g�n�ral, on met le MenuElem et sa fonction bind�e ont le m�me nom.
Y'a que le pr�fixe qui change.

mtxt : MenuText

msub : MenuElem de type MenuSubMenu

menu : MenuManager

menuXXXListElem : liste de MenuElem qu'on place dans un MenuManager.
msubmXXXListElem : liste de MenuElem qu'on place dans un MenuSubMenu.

TRODO : est-ce que �a serait pas mieux ailleurs, tout le blabla de comm ci-dessus ?

BIG BIG TRODO : c'est chiant de se trainer cette r�f�rence � fontDefault partout.
La prochaine fois, importer la police d�s le d�but, et la foutre dans le common. PUTAIN !
"""

import pygame

from common import (pyRect, LANG_FRENCH, LANG_ENGL, NAME_DOGDOM, NAME_HERO,
                    SCREEN_WINDOWED, SCREEN_FULL,
                    IHMSG_QUIT, IHMSG_TOTALQUIT,
                    IHMSG_REDRAW_MENU, IHMSG_VOID)

from archiv   import GLOB_DATA_ID_LANG, GLOB_DATA_ID_SCREEN

from menutxt  import MenuText
from menusetx import MenuSensitiveText
from menulink import MenuLink
from menuimg  import MenuImage
from menuseim import MenuSensitiveImage
from menutick import MenuSensitiveTick
from menumng  import MenuManager
from yargler  import theSoundYargler, SND_MENU_SELECT
from txtstock import txtStock

from menucomn import (MENU_MAIN, MENU_CREDITS, MENU_STORY, MENU_MANUAL,
                      MENU_CONFIG, MENU_HISCORE,
                      IMG_TITLE_MAIN, IMG_DEDICACE,
                      IMG_FLAG_FRENCH, IMG_FLAG_ENGLISH,
                      mactQuit, mkeyQuitEsc, changeLanguageOnAllMenu,
                      theGraphModeChanger)

#dictionnaire de correspondance pour la case � cocher du plein �cran/windowed.
# - cl� : valeur bool�enne de la case � cocher. (True = coch�)
# - valeur : valeur litt�rale associ�e. Ce sont les valeurs possibles de la GLOB_DATA_ID_SCREEN,
#   stock�es dans l'archivist.
SCREEN_GLOB_DATA_FROM_TICK_VALUE = {
    False : SCREEN_WINDOWED,
    True  : SCREEN_FULL,
}

#position du coin sup gauche des options MenuSensitiveText (JOUER, CONFIG, ...)
POS_OPTION = pyRect(180, 80)
#d�calage (x, y) entre 2 options.
DECAL_OPTION = (0, 25)



class MenuManagerMain(MenuManager):
    """
    hohoho. La super mega classe avec le code du menu principal dedans.
    """

    def __init__(self, surfaceDest, dicImg, fontDefault, fontLittle,
                 dicTickImage, archivist, scoreManager,
                 funcMactPlaySeveralGames, dicAllMenu):
        """
        konztrukteuur. Ya !

        entr�es :
            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault, fontLittle : objets pygame.font.Font. les polices de caract�res.

            dicTickImage : dictionnaire contenant les images de la case � cocher.
                           voir constructeur de MenuSensitiveTick

            archivist : objet de la classe �poney-ime, qui g�re le fichier de sauvegarde.

            scoreManager : objet de la classe �poney-ime, qui g�re les scores.
                           Y'en a besoin pour fixer le nom du joueur en cours, en fonction du mode
                           de jeu. (Selon qu'on fait une partie en mode normale, ou en edoGedoM.

            funcMactPlaySeveralGames : r�f�rence vers la fonction permettant de lancer une partie.
                         (Elle est d�finie dans mainclas.py, ceci dit osef de �a)

            dicAllMenu : dictionnaire contenant tous les menus du jeu.
                         Y'en a besoin car le menu principal appelle les autres menus.
        """
        MenuManager.__init__(self, surfaceDest, dicImg)

        self.archivist = archivist
        self.funcMactPlaySeveralGames = funcMactPlaySeveralGames
        self.scoreManager = scoreManager
        self.fontDefault = fontDefault
        self.fontLittle = fontLittle
        self.dicAllMenu = dicAllMenu

        # --- Cr�ation des MenuSensitiveText d�finissant les options (JOUER, ...) ---

        #liste qui contiendra les MenuSensitiveText d'options. C'est une info que je stocke
        #en self. Car j'en ai besoin aussi dans la fonction addDogDom. (Voir fin de ce fichier)
        self.listMenuElemButtText = []

        #Infos pour cr�er les MenuSensitiveText d'option. C'est une liste de tuple de 2 �l�ments :
        # - r�f�rence vers la fonction � appeler quand l'option est activ�e.
        # - texte � afficher dans le MenuSensitiveText
        listMainMenuButtTextInfo = (
            (self.mactPlaySeveralGameNorm, txtStock.MAIN_PLAY),
            (self.mactConfig,              txtStock.MAIN_CONFIG),
            (self.mactHighScore,           txtStock.MAIN_HISCORE),
            (self.mactStory,               txtStock.MAIN_INTRO),
            (self.mactCredits,             txtStock.MAIN_CREDITS),
            (mactQuit,                     txtStock.MAIN_QUIT),
        )

        #position de l'option courante. Je la stocke aussi en self, because : voir addDogDom
        self.posCurrentMenuButtText = pygame.Rect(POS_OPTION)

        for funcOnClick, idTxtStock in listMainMenuButtTextInfo:

            #cr�ation du MenuSensitiveText d'option, avec le bon texte, la bonne fonction li�e,
            #et � la bonne position. (et avec la font par d�faut, mais osef)

            param = (self.posCurrentMenuButtText, self.fontDefault,
                     funcOnClick, idTxtStock)

            menuElemButtText = MenuSensitiveText(*param)

            #ajout dans la liste regroupant tous les MenuSensitiveText d'options.
            self.listMenuElemButtText.append(menuElemButtText)

            #r�actualisation de la position pour l'option suivante. (On d�cale un peu vers le bas)
            self.posCurrentMenuButtText.move_ip(DECAL_OPTION)

        # --- Cr�ation des autres MenuElem. Y'a un peu de tout ---

        #texte statique "cr�� par R�ch�r", en bas � gauche de l'�cran.
        param = (pyRect(5, 273), fontLittle, txtStock.MAIN_RECHER)
        mtxtRecher = MenuText(*param)

        #Lien vers mon blog recher.wordpress.com. en bas-bas � gauche.
        param = (pyRect(5, 285), fontLittle,
                 self.surfaceDest, txtStock.CREDL_BLOG)

        mbuttLinkRecher = MenuLink(*param)

        #image du titre "BLARG" en jaune orange. Cette image recouvre le titre d�j� dessin�
        #dans l'image de background principale. Pourquoi donc ? Car tout est assombri dans
        #l'image de background. Mais je voulais qu'on continue de voir le titre en clair. Alors je
        #r�affiche l'image originale, pil poil exactement par dessus. (J'utilise pas cette
        #astuce dans les autres menus. Du coup, on voit le titre
        #qui s'assombrit / se d�sassombrit. Mais je trouve �a cool).
        mimgTitle = MenuImage(pyRect(130, 4), dicImg[IMG_TITLE_MAIN])

        #image de la d�dicace, � gauche de l'�cran. En vrai, y'a pas forc�ment de d�dicace.
        #Une image est syst�matiquement affich�e, mais elle peut �tre vide
        #(C'est un carr� noir avec la keyTransparency sur le noir, justement.)
        mimgDedic = MenuImage(pyRect(10, 70), dicImg[IMG_DEDICACE])

        #cr�ation des deux petites images des drapeaux anglais et fran�ais,
        #qui font changer la langue quand on clique dessus.

        param = (pyRect(345, 280), dicImg[IMG_FLAG_FRENCH],
                 self.mactChangeLanguageFrench)

        mbutiFrench = MenuSensitiveImage(*param)

        param = (pyRect(370, 280), dicImg[IMG_FLAG_ENGLISH],
                 self.mactChangeLanguageEnglish)

        mbutiEnglish = MenuSensitiveImage(*param)

        #r�cup�ration du mode graphique actuel plein �cran / fen�tr�. On s'en sert pour
        #le transmettre � la case � cocher du mode graphique. Afin qu'elle soit en accord
        #avec la r�alit� actuelle des choses.
        screenGlobDataVal = theGraphModeChanger.getScreenGlobDataVal()

        #cr�ation de la case � cocher permettant de changer le mode graphique.
        #Putain c'est un bon tas de bordel ces param. Pas mieux.
        self.mtickVideoMode = MenuSensitiveTick(
            pyRect(210, 280), fontLittle, self.mactToggleFullScreen,
            dicTickImage, txtStock.MAIN_FULLSCR,
            dicLiteralFromBool=SCREEN_GLOB_DATA_FROM_TICK_VALUE,
            literalValInit=screenGlobDataVal)

        # --- Rangement de tous les MenuElem cr��s, dans la grande liste globale. ---

        #Cr�ation d'une liste contenant tous les MenuElem, except� les MenuSensitiveText d'option.
        #Je stocke cette liste en self, because voir addDogDom.
        self.listMenuElemOther = [
            mkeyQuitEsc, mimgTitle, mimgDedic, mtxtRecher, mbuttLinkRecher,
            self.mtickVideoMode, mbutiFrench, mbutiEnglish
        ]

        #Et hop, rassemblage des deux sous-listes dans la grande liste principale avec tout.
        #et au passage : tuplifiage pour acc�l�rer l'ex�cution du code.
        listMenuElemTotal = self.listMenuElemButtText + self.listMenuElemOther
        self.listMenuElem = tuple(listMenuElemTotal)

        #r�cup�ration du nombre de MenuSensitiveText d'options.
        nbrMenuButt = len(self.listMenuElemButtText)

        #d�finition du cyclage de focus. En plus du cyclage classique avec Tab, on peut
        #faire en cyclage restreint aux MenuSensitiveText d'options, avec les fl�ches
        #haut et bas. Ah et pis aussi on se focus par d�faut sur la premi�re option : JOUER.
        self.initFocusCyclingInfo(0, (0, nbrMenuButt))


    def addDogDom(self):
        """
        fonction ajoutant l'option pour jouer en mode edoMedoG

        J'aurais pu mettre l'ajout de cette option directement dans le __init__, (on aurait
        indiqu� avec un param bool�en si on en veut ou pas). et apr�s j'aurais
        modifi� un peu le code ext�rieur pour que la cr�ation du MenuManagerMain soit
        effectu�e apr�s qu'on ait d�termin� si faut ajouter cette option ou pas. Ca aurait �t� un
        peu plus simple, dans l'ensemble. Mais je le fais pas. Car j'aurais peut-�tre besoin,
        dans une hypoth�tique version 2, que cette option puisse s'ajouter en live.
        """

        #cr�ation de l'option � ajouter. On l'ajoute en bas des autres options d�j� cr��es.
        #On a stock� cette position dans la variable self.posCurrentMenuButtText.
        param = (self.posCurrentMenuButtText, self.fontDefault,
                 self.mactPlaySeveralGameNotNorm, txtStock.MAIN_DOGDOM)

        mbuttDogDom = MenuSensitiveText(*param)

        #ajout de cette nouvelle option dans la liste regroupant les MenuSensitiveText d'option.
        self.listMenuElemButtText += (mbuttDogDom, )

        #refabrication de la liste regroupant tous les MenuElem.
        self.listMenuElem = self.listMenuElemButtText + self.listMenuElemOther

        #r�cup�ration du nombre de MenuSensitiveText d'options. Vu qu'y en a un de plus.
        nbrMenuButt = len(self.listMenuElemButtText)

        #red�finition du cyclage de focus. (Voir le commentaire de cette m�me ligne de code
        #dans la fonction __init__ pour plus de d�tail).
        self.initFocusCyclingInfo(0, (0, nbrMenuButt))


    def mactChangeLanguage(self, newLanguage):
        """
        fonction g�n�rique pour changer de language. Elle est pr�fix�e par "mact", mais elle
        est pas directement link�e � un MenuElem. Elle est appel�e dans des fonctions "mact"
        link�e. (Voir ci-dessous).

        entr�e : identifiant de type GLOB_DATA_ID_LANG, indiquant la nouvelle langue.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        #son de s�lection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #changement du langage dans tous les menus. Tralala captain obvious oui.
        changeLanguageOnAllMenu(newLanguage, self.dicAllMenu)

        #enregistrement de la langue qu'on vient d'activer, dans l'archivist, et donc
        #par-l�-m�me-cons�cutivement dans le fichier de sauvegarde.
        self.archivist.modifyGlobData( {GLOB_DATA_ID_LANG : newLanguage} )

        #on demande un redessinage du menu principal (pour r��crire les textes qui auront chang�).
        return (IHMSG_REDRAW_MENU, )


    def mactChangeLanguageEnglish(self):
        """
        fonction qui s'ex�cute quand on appuie sur le drapal anglais.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        return self.mactChangeLanguage(LANG_ENGL)


    def mactChangeLanguageFrench(self):
        """
        fonction qui s'ex�cute quand on appuie sur le drapal fran�ais.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        return self.mactChangeLanguage(LANG_FRENCH)


    def activateSomeMenus(self, listIdMenu):
        """
        active plusieurs menus, les uns apr�s les autres.
        Si le joueur demande � quitter totalement le jeu, l'encha�nement de menus est
        interrompu, et on quitte la fonction tout de suite (avec le IHMSG_TOTALQUIT, of course).

        entr�es :
            listIdMenu : liste d'identifiant de menu (MENU_*) � activer.
                         on peut bien entendu indiquer une liste d'un seul �l�ment.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #son de s�lection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        ihmsgInfo = IHMSG_VOID

        for idMenu in listIdMenu:

            #r�cup�ration du menu � activer, et activation.
            menuToActivate = self.dicAllMenu[idMenu]
            ihmsgInfo += menuToActivate.handleMenu()

            if IHMSG_TOTALQUIT in ihmsgInfo:
                #durant le g�rage de ce menu, le joueur a demand� � quitter.
                #on interrompt tout, et on propage le message de TOTALQUIT au code ext�rieur,
                #qui est cens� s'en occuper.
                return (IHMSG_QUIT, IHMSG_TOTALQUIT)

        #on a activ� tous les menus demand�s. On demande un redessinage, pour redessiner
        #le menu principal. Youpi !
        return (IHMSG_REDRAW_MENU, )


    def mactStory(self):
        """
        fonction s'ex�cutant quand on appuie sur l'option "INTRO". (plat-dessert : tuple d'ihm)
        """
        #on active le menu affichant l'histoire du jeu, puis le menu affichant le manuel.
        return self.activateSomeMenus( (MENU_STORY, MENU_MANUAL) )


    def mactConfig(self):
        """
        fonction s'ex�cutant quand on appuie sur l'option "CONFIG". (plat-dessert : tuple d'ihm)
        """
        #on active un seul menu. Celui permettant de configurer le jeu.
        return self.activateSomeMenus( (MENU_CONFIG, ) )


    def mactHighScore(self):
        """
        fonction s'ex�cutant quand on appuie sur l'option "HISCORE". (plat-dessert : tuple d'ihm)
        """
        #oui bon, captain obvious. Ca va bien, ok ?
        return self.activateSomeMenus( (MENU_HISCORE, ) )


    def mactCredits(self):
        """
        fonction s'ex�cutant quand on appuie sur l'option "CREDITS". (plat-dessert : tuple d'ihm)
        """
        #bla blah yadah yadah yadaah. J'�coute le CD "mega ann�es 90 volume 2" et j'ai pas honte.
        return self.activateSomeMenus( (MENU_CREDITS, ) )


    def beforeDrawMenu(self):
        """
        fonction qui s'ex�cute avant chaque redessinage total du menu.
        (overrid� du MenuManager)
        """

        #il faut re-synchroniser la case � cocher affichant le mode plein-�cran/fen�tre avec
        #le mode graphique actuel. Car �a a peut �tre chang�, pour une raison ou une autre.

        #r�cup�ration du mode graphique indiqu� par la case � cocher.
        #(on r�cup�re un identifiant de type GLOB_DATA_ID_SCREEN)
        screenGlobDataValTick = self.mtickVideoMode.literTickValue
        #r�cup�ration du mode graphique affich� en r�alit�.
        screenGlobDataValReal = theGraphModeChanger.getScreenGlobDataVal()

        #si les deux identifiants de mode graphique sont en d�saccord, on inverse l'�tat de
        #la case � cocher, pour que �a devienne bon. Attention, ce genre d'astuce � l'arrache
        #fonctionne parce que la case � cocher n'a que deux �tats diff�rents. Sinon faudrait
        #lui transmettre explicitement l'�tat souhait�.
        if screenGlobDataValTick != screenGlobDataValReal:
            self.mtickVideoMode.toggleTick()


    def mactToggleFullScreen(self):
        """
        fonction qui s'ex�cute quand le joueur clique sur la case � cocher du mode graphique.

        fun fact : l'archivist est forc�ment synchro avec le contenu du fichier sauvegard�,
        la case � cocher du plein �cran est forc�ment synchro avec le fait d'�tre en
        plein �cran ou pas. Mais y'a pas forc�ment de synchro entre la case � cocher
        et le contenu du fichier. C'est � cause des clics sur les liens internet,
        qui d�sactivent le plein �cran sans le sauvegarder, ou du param�tre FORCE_WINDOWED

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #son de s�lection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #Le MenuTick ne toggle pas son �tat coch�/pas coch� de sa propre initiative.
        #Faut lui appeler sa fonction.
        self.mtickVideoMode.toggleTick()

        #maintenant qu'on l'a toggl�, on r�cup�re sa valeur lit�rale. Qui est un identifiant
        #GLOB_DATA_ID_SCREEN, et qui correspond au mode graphique souhait�.
        screenGlobDataVal = self.mtickVideoMode.literTickValue

        #Donc, on change le mode graphique, en sp�cifiant le nouveau qu'on veut.
        #C'est m�chamment bourrin de changer la surface principale d'affichage ici, � l'arrache.
        #Mais �a marche. Heureusement que les objets Surface sont pass�s par valeur. Du coup,
        #tout le monde a le m�me, et quand je le change ici, �a s'applique partout.
        self.surfaceDest = theGraphModeChanger.setGraphMode(screenGlobDataVal)

        #Enregistrement de la nouvelle valeur du mode graphique dans l'archivist
        #(Qui s'occupe de l'enregistrer dans le fichier de sauvegarde)
        newDicGlobData = { GLOB_DATA_ID_SCREEN : screenGlobDataVal }
        self.archivist.modifyGlobData(newDicGlobData)

        #Faut redessiner enti�rement le menu. Apr�s un changement de mode graphique,
        #c'est quand m�me la moindre des choses. Ah bah oui hein ma bonne dame.
        return (IHMSG_REDRAW_MENU, )


    def mactPlaySeveralGameNorm(self):
        """
        joue une ou plusieurs parties, en mode normal.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        #son de s�lection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #on dit au scoreManager de s�lectionner le joueur correspondant au mode normal.
        #Afin d'enregistrer les scores de cette/ces parties au bon endroit.
        self.scoreManager.selectPlayer(NAME_HERO)

        #on joue une ou plusieurs parties les unes apr�s les autres (c'est le joueur qui choisit).
        #On indique False en param pour pr�ciser que c'est le mode normal.
        #La fonction de jouage de partie peut renvoyer un message IHMSG_TOTALQUIT, qu'il faut
        #alors propager. Ou elle peut juste renvoyer un message IHMSG_REDRAW_MENU, mais faut le
        #propager aussi. Bref, on propage tout et voil�.
        return self.funcMactPlaySeveralGames(False)


    def mactPlaySeveralGameNotNorm(self):
        """
        joue une ou plusieurs parties, en mode edoMedoG.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        #son de s�lection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #voir fonction mactPlaySeveralGameNorm. C'est pareil sauf que c'est pas le m�me nom
        #s�lectionn� par le scoreManager, et pas le m�me param envoy� � la fonction pour jouer.
        self.scoreManager.selectPlayer(NAME_DOGDOM)
        return self.funcMactPlaySeveralGames(True)
