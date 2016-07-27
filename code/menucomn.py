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

date de la dernière relecture-commentage : 09/02/2011

fonction qui regroupe certains trucs commun à tous les menus du jeu.
"""

import pygame
import pygame.locals
pygl = pygame.locals

from common   import (IHMSG_QUIT, IHMSG_REDRAW_MENU, IHMSG_VOID,
                      SCREEN_RECT, SCREEN_DEFAULT,
                      SCREEN_FULL, SCREEN_WINDOWED)

from menukey  import MenuSensitiveKey
from menuanyk import MenuSensitiveAnyKeyButton
from txtstock import txtStock


#liste des identifiants de tous les menus du jeu
(MENU_MAIN,           #menu principal
 MENU_CREDITS,        #Crédits : affichage de Moi, mes liens, et les contributeurs
 MENU_HERO_DEAD,      #menu de fin de partie, avec l'image du héros mort.
 MENU_ENTER_NAME,     #menu demandant d'entrer le nom du joueur
 MENU_STORY,          #affichage de l'histoire du jeu, avec scrolling et tout.
 MENU_MANUAL,         #"manuel" du jeu. (C'est juste les touches, en fait)
 MENU_CONFIG,         #comme le manuel, mais on peut configurer les touches, et le son
 MENU_HISCORE,        #affichage des high scores.
 MENU_PRESS_ANY_KEY,  #menu qu'affiche rien. Il attend juste un clic ou un appui de touche
 MENU_NAME_IS_A_LIE,  #affichage du texte de 2 lignes expliquant qu'on s'en fout du nom du joueur.
) = range(10)

#liste des identifiants de toutes les images utilisées dans les menus du jeu.
(IMG_BG_MAIN,        #image de fond, avec héros et magicien, (en dark-foncé)
 IMG_TITLE_MAIN,     #le titre en jaune-orange : "BLARG"
 IMG_BG_BLARG,       #image du héros mort, pour la fin de la partie. (Nom mal choisi, on confond)
 IMG_FLAG_FRENCH,    #drapeau français
 IMG_FLAG_ENGLISH,   #drapeau rosbif
 IMG_TICK_TRUE,      #case à cocher coché
 IMG_TICK_FALSE,     #case à cocher pas coché
 IMG_CRED_SCRL_UP,   #bouton super-large (mais pas épais) de scrolling des crédits vers le haut.
 IMG_CRED_SCRL_DOWN, #bouton super-large (et épais) de scrolling des crédits vers le bas.
 IMG_BACK,           #bouton pour revenir en arrière quand on est dans les crédits
 IMG_FRAME_NAME,     #espèce de fenêtre pour demander le nom du joueur
 IMG_BUTT_OK,        #bouton OK. (utilisé dans la fenêtre de nom du joueur)
 IMG_MANUAL,         #grosse image montrant le manuel du jeu, avec les touches.
 IMG_BUTT_RESET,     #espèce de pseudo-bouton moche de remise à zero de la config
 IMG_DEDICACE,       #image avec la dédicace. Apparaît dans le menu principal, quand y'en a une.
) = range(15)
#TRODO : pour plus tard car j'ai la flemme : changer le nom de IMG_BG_BLARG

#options à filer à la fonction pygame.display.set_mode, pour initialiser le mode graphique.
#on peut faire en plein écran, ou en fenêtre.
#je préfère pas mettre le HWSURFACE et le DOUBLEBUF dans les options.
#Si on a une résolution qui correspond pas aux proportions de l'écran,
#ça me fait des vieux bugs d'affichage sur mon bidule.
#Donc tant pis, pas d'accélération matérielles de mes couilles. (pas besoin de toutes façons)
DISPLAY_OPT_FULLSCREEN = pygame.FULLSCREEN
DISPLAY_OPT_WINDOWED = 0

#dico de correspondance entre le type de screen, lu depuis le fichier de sauvegarde,
#et les options du set_mode.
DIC_DISPLAY_OPT = {
    SCREEN_WINDOWED : DISPLAY_OPT_WINDOWED,
    SCREEN_FULL     : DISPLAY_OPT_FULLSCREEN,
}



def changeLanguageOnAllMenu(newLanguage, dicAllMenu):
    """
    fonction pour propager le changement de langue anglais/français dans tous les menus du jeu.

    entrées :
        newLanguage : nouvelle lange à appliquer. LANG_FRENCH ou LANG_ENGL.

        dicAllMenu : dictionnaire contenant tous les menus du jeu.
                     (clé : identifiant MENU_*)

    Attention, ça change le langage, mais ça enregistre pas ce changement
    dans le fichier de config/sauvegarde. Il faut le faire manuellement, si nécessaire.
    """

    #si le nouveau langage à activer est le même que celui qui est en cours, on fait rien.
    if txtStock.language == newLanguage:
        return

    #on envoie le changement à l'objet qui stocke tous les textes de toutes les langues.
    txtStock.changeLanguage(newLanguage)

    #et on envoie le changement à tous les menus du jeu.
    for keyMenu, menu in dicAllMenu.items():
        menu.changeLanguage()


def mactQuit():
    """
    fonction qui fait quitter le menu en cours.

    plat-dessert : un tuple de message d'ihm, avec tout ce qu'il faut dedans
                   pour quitter le menu.
    """
    return (IHMSG_REDRAW_MENU, IHMSG_QUIT)


#ça c'est un élément de menu qui fait le bind entre la touche Echap,
#et le quittage du menu en cours. Y'en a besoin pour la plupart des menu.
mkeyQuitEsc = MenuSensitiveKey(mactQuit, pygl.K_ESCAPE)

#et ça, c'est un élément de menu qui fait le bind entre n'importe quelle touche/clic de souris,
#et le quittage du menu en cours. Y'en a besoin pour quelques menus
manyQuit = MenuSensitiveAnyKeyButton(mactQuit)


#TRODO pour plus tard : foutre cette classe ailleurs. Elle devrait pas vraiment être ici.
#(Elle est plus générique que les menus.)
class GraphModeChanger():
    """
    classe qui switche le mode plein écran / windowed. Et qui enregistre l'état actuel,
    pour le refiler à du code extérieur qui le demande (genre la case à cocher du MenuManagerMain)
    Y'a besoin de la stocker et de la ressortir cette putain de valeur, car elle est pas
    forcément en accord avec la GLOB_DATA_ID_SCREEN qui est dans l'archivist. Y'a des fois on
    change le mode graphique sans l'enregistrer. (Par exemple quand on force le mode fenêtré
    avec le param en ligne de commande. Ou quand on vire le plein écran car le joueur a
    cliqué sur un lien internet.)

    fun fact (même si je l'ai  peut-être déjà dit ailleurs). La case à cocher du menu principal
    est toujour en accord avec le mode graphique réel. La valeur GLOB_DATA_ID_SCREEN de
    l'archivist est toujours en accord avec le contenu du fichier de sauvegarde. Mais y'a
    pas forcément de cohérence entre ces deux trucs.
    """

    def __init__(self):
        """
        constructeur of ze obvious.
        """

        #état actuel du mode graphique. On utilise les mêmes valeurs que pour la
        #GLOB_DATA_ID_SCREEN, stockée dans l'archivist. Donc y'a SCREEN_FULL et SCREEN_WINDOWED.
        #Là je l'initialise à une valeur par défaut à la con. Osef en fait.
        self.currentScreenGlobDataVal = SCREEN_DEFAULT


    def setGraphMode(self, newScreenGlobDataVal):
        """
        change le mode graphique.

        entrées : newScreenGlobDataVal. valeur de type GLOB_DATA_ID_SCREEN, indiquant le nouveau
                  mode souhaité.

        plat-dessert : screen. objet pygame.surface.Surface, représentant la surface principale
                       sur laquelle on affiche le jeu. Forcément faut la renvoyer, puisque cette
                       fonction la redéfinit.

        Attention, la fonction ne vérifie pas que le mode graphique en cours soit différent
        du nouveau mode demandé. Du coup, on peut se retrouver à redéfinir le screen pour rien.
        Faut faire la vérif avant.
        """

        #réactualisation de la valeur courante du mode graphique.
        self.currentScreenGlobDataVal = newScreenGlobDataVal

        #conversion (mode fenêtre/plein écran) -> (options du mode graphique)
        displayOption = DIC_DISPLAY_OPT[self.currentScreenGlobDataVal]

        #création de l'objet pygame.Surface, dans laquelle on affichera le jeu, les menus, tout.
        #(cette action crée la fenêtre, ou met en plein écran, selon ce qui a été choisi)
        screen = pygame.display.set_mode(SCREEN_RECT.size, displayOption)

        return screen


    def getScreenGlobDataVal(self):
        """
        récupère la valeur courante du mode graphique.

        plat-dessert : donnée de type GLOB_DATA_ID_SCREEN.
        """
        return self.currentScreenGlobDataVal

#donc, comme déjà dit ailleurs, j'aime pas trop ce concept d'instancier à l'arrache un objet,
#pour pouvoir l'importer comme une putain de variable globale de mes couilles. En plus, ça
#fait exécuter du code lors du premier import, c'est à dire : on sait pas exactement quand.
#Mais va falloir que je m'y fasse à cette putain de technique, parce qu'elle est quand même
#bien pratique.
theGraphModeChanger = GraphModeChanger()
