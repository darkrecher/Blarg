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

date de la dernière relecture-commentage : 27/03/2011

Menu principal avec la principalitude des choses eud'dans.

bon c'est le bordel là. On va essayer de ranger un peu tout ça.

mact : menuAction : fonction de type funcAction, qu'on binde sur un élément de menu
(par ex : un bouton)

mbutt :     MenuElem de type bouton text (MenuSensitiveText)
mbuttLink : MenuElem de type bouton text (MenuSensitiveText), qui fait un lien vers un site web.
mbuti : MenuElem de type bouton image (MenuSensitiveImage)
mkey :  MenuElem de type MenuSensitiveKey

En général, on met le MenuElem et sa fonction bindée ont le même nom.
Y'a que le préfixe qui change.

mtxt : MenuText

msub : MenuElem de type MenuSubMenu

menu : MenuManager

menuXXXListElem : liste de MenuElem qu'on place dans un MenuManager.
msubmXXXListElem : liste de MenuElem qu'on place dans un MenuSubMenu.

TRODO : est-ce que ça serait pas mieux ailleurs, tout le blabla de comm ci-dessus ?

BIG BIG TRODO : c'est chiant de se trainer cette référence à fontDefault partout.
La prochaine fois, importer la police dès le début, et la foutre dans le common. PUTAIN !
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

#dictionnaire de correspondance pour la case à cocher du plein écran/windowed.
# - clé : valeur booléenne de la case à cocher. (True = coché)
# - valeur : valeur littérale associée. Ce sont les valeurs possibles de la GLOB_DATA_ID_SCREEN,
#   stockées dans l'archivist.
SCREEN_GLOB_DATA_FROM_TICK_VALUE = {
    False : SCREEN_WINDOWED,
    True  : SCREEN_FULL,
}

#position du coin sup gauche des options MenuSensitiveText (JOUER, CONFIG, ...)
POS_OPTION = pyRect(180, 80)
#décalage (x, y) entre 2 options.
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

        entrées :
            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault, fontLittle : objets pygame.font.Font. les polices de caractères.

            dicTickImage : dictionnaire contenant les images de la case à cocher.
                           voir constructeur de MenuSensitiveTick

            archivist : objet de la classe époney-ime, qui gère le fichier de sauvegarde.

            scoreManager : objet de la classe époney-ime, qui gère les scores.
                           Y'en a besoin pour fixer le nom du joueur en cours, en fonction du mode
                           de jeu. (Selon qu'on fait une partie en mode normale, ou en edoGedoM.

            funcMactPlaySeveralGames : référence vers la fonction permettant de lancer une partie.
                         (Elle est définie dans mainclas.py, ceci dit osef de ça)

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

        # --- Création des MenuSensitiveText définissant les options (JOUER, ...) ---

        #liste qui contiendra les MenuSensitiveText d'options. C'est une info que je stocke
        #en self. Car j'en ai besoin aussi dans la fonction addDogDom. (Voir fin de ce fichier)
        self.listMenuElemButtText = []

        #Infos pour créer les MenuSensitiveText d'option. C'est une liste de tuple de 2 éléments :
        # - référence vers la fonction à appeler quand l'option est activée.
        # - texte à afficher dans le MenuSensitiveText
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

            #création du MenuSensitiveText d'option, avec le bon texte, la bonne fonction liée,
            #et à la bonne position. (et avec la font par défaut, mais osef)

            param = (self.posCurrentMenuButtText, self.fontDefault,
                     funcOnClick, idTxtStock)

            menuElemButtText = MenuSensitiveText(*param)

            #ajout dans la liste regroupant tous les MenuSensitiveText d'options.
            self.listMenuElemButtText.append(menuElemButtText)

            #réactualisation de la position pour l'option suivante. (On décale un peu vers le bas)
            self.posCurrentMenuButtText.move_ip(DECAL_OPTION)

        # --- Création des autres MenuElem. Y'a un peu de tout ---

        #texte statique "créé par Réchèr", en bas à gauche de l'écran.
        param = (pyRect(5, 273), fontLittle, txtStock.MAIN_RECHER)
        mtxtRecher = MenuText(*param)

        #Lien vers mon blog recher.wordpress.com. en bas-bas à gauche.
        param = (pyRect(5, 285), fontLittle,
                 self.surfaceDest, txtStock.CREDL_BLOG)

        mbuttLinkRecher = MenuLink(*param)

        #image du titre "BLARG" en jaune orange. Cette image recouvre le titre déjà dessiné
        #dans l'image de background principale. Pourquoi donc ? Car tout est assombri dans
        #l'image de background. Mais je voulais qu'on continue de voir le titre en clair. Alors je
        #réaffiche l'image originale, pil poil exactement par dessus. (J'utilise pas cette
        #astuce dans les autres menus. Du coup, on voit le titre
        #qui s'assombrit / se désassombrit. Mais je trouve ça cool).
        mimgTitle = MenuImage(pyRect(130, 4), dicImg[IMG_TITLE_MAIN])

        #image de la dédicace, à gauche de l'écran. En vrai, y'a pas forcément de dédicace.
        #Une image est systématiquement affichée, mais elle peut être vide
        #(C'est un carré noir avec la keyTransparency sur le noir, justement.)
        mimgDedic = MenuImage(pyRect(10, 70), dicImg[IMG_DEDICACE])

        #création des deux petites images des drapeaux anglais et français,
        #qui font changer la langue quand on clique dessus.

        param = (pyRect(345, 280), dicImg[IMG_FLAG_FRENCH],
                 self.mactChangeLanguageFrench)

        mbutiFrench = MenuSensitiveImage(*param)

        param = (pyRect(370, 280), dicImg[IMG_FLAG_ENGLISH],
                 self.mactChangeLanguageEnglish)

        mbutiEnglish = MenuSensitiveImage(*param)

        #récupération du mode graphique actuel plein écran / fenêtré. On s'en sert pour
        #le transmettre à la case à cocher du mode graphique. Afin qu'elle soit en accord
        #avec la réalité actuelle des choses.
        screenGlobDataVal = theGraphModeChanger.getScreenGlobDataVal()

        #création de la case à cocher permettant de changer le mode graphique.
        #Putain c'est un bon tas de bordel ces param. Pas mieux.
        self.mtickVideoMode = MenuSensitiveTick(
            pyRect(210, 280), fontLittle, self.mactToggleFullScreen,
            dicTickImage, txtStock.MAIN_FULLSCR,
            dicLiteralFromBool=SCREEN_GLOB_DATA_FROM_TICK_VALUE,
            literalValInit=screenGlobDataVal)

        # --- Rangement de tous les MenuElem créés, dans la grande liste globale. ---

        #Création d'une liste contenant tous les MenuElem, excepté les MenuSensitiveText d'option.
        #Je stocke cette liste en self, because voir addDogDom.
        self.listMenuElemOther = [
            mkeyQuitEsc, mimgTitle, mimgDedic, mtxtRecher, mbuttLinkRecher,
            self.mtickVideoMode, mbutiFrench, mbutiEnglish
        ]

        #Et hop, rassemblage des deux sous-listes dans la grande liste principale avec tout.
        #et au passage : tuplifiage pour accélérer l'exécution du code.
        listMenuElemTotal = self.listMenuElemButtText + self.listMenuElemOther
        self.listMenuElem = tuple(listMenuElemTotal)

        #récupération du nombre de MenuSensitiveText d'options.
        nbrMenuButt = len(self.listMenuElemButtText)

        #définition du cyclage de focus. En plus du cyclage classique avec Tab, on peut
        #faire en cyclage restreint aux MenuSensitiveText d'options, avec les flèches
        #haut et bas. Ah et pis aussi on se focus par défaut sur la première option : JOUER.
        self.initFocusCyclingInfo(0, (0, nbrMenuButt))


    def addDogDom(self):
        """
        fonction ajoutant l'option pour jouer en mode edoMedoG

        J'aurais pu mettre l'ajout de cette option directement dans le __init__, (on aurait
        indiqué avec un param booléen si on en veut ou pas). et après j'aurais
        modifié un peu le code extérieur pour que la création du MenuManagerMain soit
        effectuée après qu'on ait déterminé si faut ajouter cette option ou pas. Ca aurait été un
        peu plus simple, dans l'ensemble. Mais je le fais pas. Car j'aurais peut-être besoin,
        dans une hypothétique version 2, que cette option puisse s'ajouter en live.
        """

        #création de l'option à ajouter. On l'ajoute en bas des autres options déjà créées.
        #On a stocké cette position dans la variable self.posCurrentMenuButtText.
        param = (self.posCurrentMenuButtText, self.fontDefault,
                 self.mactPlaySeveralGameNotNorm, txtStock.MAIN_DOGDOM)

        mbuttDogDom = MenuSensitiveText(*param)

        #ajout de cette nouvelle option dans la liste regroupant les MenuSensitiveText d'option.
        self.listMenuElemButtText += (mbuttDogDom, )

        #refabrication de la liste regroupant tous les MenuElem.
        self.listMenuElem = self.listMenuElemButtText + self.listMenuElemOther

        #récupération du nombre de MenuSensitiveText d'options. Vu qu'y en a un de plus.
        nbrMenuButt = len(self.listMenuElemButtText)

        #redéfinition du cyclage de focus. (Voir le commentaire de cette même ligne de code
        #dans la fonction __init__ pour plus de détail).
        self.initFocusCyclingInfo(0, (0, nbrMenuButt))


    def mactChangeLanguage(self, newLanguage):
        """
        fonction générique pour changer de language. Elle est préfixée par "mact", mais elle
        est pas directement linkée à un MenuElem. Elle est appelée dans des fonctions "mact"
        linkée. (Voir ci-dessous).

        entrée : identifiant de type GLOB_DATA_ID_LANG, indiquant la nouvelle langue.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        #son de sélection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #changement du langage dans tous les menus. Tralala captain obvious oui.
        changeLanguageOnAllMenu(newLanguage, self.dicAllMenu)

        #enregistrement de la langue qu'on vient d'activer, dans l'archivist, et donc
        #par-là-même-consécutivement dans le fichier de sauvegarde.
        self.archivist.modifyGlobData( {GLOB_DATA_ID_LANG : newLanguage} )

        #on demande un redessinage du menu principal (pour réécrire les textes qui auront changé).
        return (IHMSG_REDRAW_MENU, )


    def mactChangeLanguageEnglish(self):
        """
        fonction qui s'exécute quand on appuie sur le drapal anglais.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        return self.mactChangeLanguage(LANG_ENGL)


    def mactChangeLanguageFrench(self):
        """
        fonction qui s'exécute quand on appuie sur le drapal français.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        return self.mactChangeLanguage(LANG_FRENCH)


    def activateSomeMenus(self, listIdMenu):
        """
        active plusieurs menus, les uns après les autres.
        Si le joueur demande à quitter totalement le jeu, l'enchaînement de menus est
        interrompu, et on quitte la fonction tout de suite (avec le IHMSG_TOTALQUIT, of course).

        entrées :
            listIdMenu : liste d'identifiant de menu (MENU_*) à activer.
                         on peut bien entendu indiquer une liste d'un seul élément.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #son de sélection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        ihmsgInfo = IHMSG_VOID

        for idMenu in listIdMenu:

            #récupération du menu à activer, et activation.
            menuToActivate = self.dicAllMenu[idMenu]
            ihmsgInfo += menuToActivate.handleMenu()

            if IHMSG_TOTALQUIT in ihmsgInfo:
                #durant le gérage de ce menu, le joueur a demandé à quitter.
                #on interrompt tout, et on propage le message de TOTALQUIT au code extérieur,
                #qui est censé s'en occuper.
                return (IHMSG_QUIT, IHMSG_TOTALQUIT)

        #on a activé tous les menus demandés. On demande un redessinage, pour redessiner
        #le menu principal. Youpi !
        return (IHMSG_REDRAW_MENU, )


    def mactStory(self):
        """
        fonction s'exécutant quand on appuie sur l'option "INTRO". (plat-dessert : tuple d'ihm)
        """
        #on active le menu affichant l'histoire du jeu, puis le menu affichant le manuel.
        return self.activateSomeMenus( (MENU_STORY, MENU_MANUAL) )


    def mactConfig(self):
        """
        fonction s'exécutant quand on appuie sur l'option "CONFIG". (plat-dessert : tuple d'ihm)
        """
        #on active un seul menu. Celui permettant de configurer le jeu.
        return self.activateSomeMenus( (MENU_CONFIG, ) )


    def mactHighScore(self):
        """
        fonction s'exécutant quand on appuie sur l'option "HISCORE". (plat-dessert : tuple d'ihm)
        """
        #oui bon, captain obvious. Ca va bien, ok ?
        return self.activateSomeMenus( (MENU_HISCORE, ) )


    def mactCredits(self):
        """
        fonction s'exécutant quand on appuie sur l'option "CREDITS". (plat-dessert : tuple d'ihm)
        """
        #bla blah yadah yadah yadaah. J'écoute le CD "mega années 90 volume 2" et j'ai pas honte.
        return self.activateSomeMenus( (MENU_CREDITS, ) )


    def beforeDrawMenu(self):
        """
        fonction qui s'exécute avant chaque redessinage total du menu.
        (overridé du MenuManager)
        """

        #il faut re-synchroniser la case à cocher affichant le mode plein-écran/fenêtre avec
        #le mode graphique actuel. Car ça a peut être changé, pour une raison ou une autre.

        #récupération du mode graphique indiqué par la case à cocher.
        #(on récupère un identifiant de type GLOB_DATA_ID_SCREEN)
        screenGlobDataValTick = self.mtickVideoMode.literTickValue
        #récupération du mode graphique affiché en réalité.
        screenGlobDataValReal = theGraphModeChanger.getScreenGlobDataVal()

        #si les deux identifiants de mode graphique sont en désaccord, on inverse l'état de
        #la case à cocher, pour que ça devienne bon. Attention, ce genre d'astuce à l'arrache
        #fonctionne parce que la case à cocher n'a que deux états différents. Sinon faudrait
        #lui transmettre explicitement l'état souhaité.
        if screenGlobDataValTick != screenGlobDataValReal:
            self.mtickVideoMode.toggleTick()


    def mactToggleFullScreen(self):
        """
        fonction qui s'exécute quand le joueur clique sur la case à cocher du mode graphique.

        fun fact : l'archivist est forcément synchro avec le contenu du fichier sauvegardé,
        la case à cocher du plein écran est forcément synchro avec le fait d'être en
        plein écran ou pas. Mais y'a pas forcément de synchro entre la case à cocher
        et le contenu du fichier. C'est à cause des clics sur les liens internet,
        qui désactivent le plein écran sans le sauvegarder, ou du paramètre FORCE_WINDOWED

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #son de sélection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #Le MenuTick ne toggle pas son état coché/pas coché de sa propre initiative.
        #Faut lui appeler sa fonction.
        self.mtickVideoMode.toggleTick()

        #maintenant qu'on l'a togglé, on récupère sa valeur litérale. Qui est un identifiant
        #GLOB_DATA_ID_SCREEN, et qui correspond au mode graphique souhaité.
        screenGlobDataVal = self.mtickVideoMode.literTickValue

        #Donc, on change le mode graphique, en spécifiant le nouveau qu'on veut.
        #C'est méchamment bourrin de changer la surface principale d'affichage ici, à l'arrache.
        #Mais ça marche. Heureusement que les objets Surface sont passés par valeur. Du coup,
        #tout le monde a le même, et quand je le change ici, ça s'applique partout.
        self.surfaceDest = theGraphModeChanger.setGraphMode(screenGlobDataVal)

        #Enregistrement de la nouvelle valeur du mode graphique dans l'archivist
        #(Qui s'occupe de l'enregistrer dans le fichier de sauvegarde)
        newDicGlobData = { GLOB_DATA_ID_SCREEN : screenGlobDataVal }
        self.archivist.modifyGlobData(newDicGlobData)

        #Faut redessiner entièrement le menu. Après un changement de mode graphique,
        #c'est quand même la moindre des choses. Ah bah oui hein ma bonne dame.
        return (IHMSG_REDRAW_MENU, )


    def mactPlaySeveralGameNorm(self):
        """
        joue une ou plusieurs parties, en mode normal.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        #son de sélection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #on dit au scoreManager de sélectionner le joueur correspondant au mode normal.
        #Afin d'enregistrer les scores de cette/ces parties au bon endroit.
        self.scoreManager.selectPlayer(NAME_HERO)

        #on joue une ou plusieurs parties les unes après les autres (c'est le joueur qui choisit).
        #On indique False en param pour préciser que c'est le mode normal.
        #La fonction de jouage de partie peut renvoyer un message IHMSG_TOTALQUIT, qu'il faut
        #alors propager. Ou elle peut juste renvoyer un message IHMSG_REDRAW_MENU, mais faut le
        #propager aussi. Bref, on propage tout et voilà.
        return self.funcMactPlaySeveralGames(False)


    def mactPlaySeveralGameNotNorm(self):
        """
        joue une ou plusieurs parties, en mode edoMedoG.
        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """
        #son de sélection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #voir fonction mactPlaySeveralGameNorm. C'est pareil sauf que c'est pas le même nom
        #sélectionné par le scoreManager, et pas le même param envoyé à la fonction pour jouer.
        self.scoreManager.selectPlayer(NAME_DOGDOM)
        return self.funcMactPlaySeveralGames(True)
