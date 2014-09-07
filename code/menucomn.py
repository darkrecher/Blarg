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

date de la derni�re relecture-commentage : 09/02/2011

fonction qui regroupe certains trucs commun � tous les menus du jeu.
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
 MENU_CREDITS,        #Cr�dits : affichage de Moi, mes liens, et les contributeurs
 MENU_HERO_DEAD,      #menu de fin de partie, avec l'image du h�ros mort.
 MENU_ENTER_NAME,     #menu demandant d'entrer le nom du joueur
 MENU_STORY,          #affichage de l'histoire du jeu, avec scrolling et tout.
 MENU_MANUAL,         #"manuel" du jeu. (C'est juste les touches, en fait)
 MENU_CONFIG,         #comme le manuel, mais on peut configurer les touches, et le son
 MENU_HISCORE,        #affichage des high scores.
 MENU_PRESS_ANY_KEY,  #menu qu'affiche rien. Il attend juste un clic ou un appui de touche
 MENU_NAME_IS_A_LIE,  #affichage du texte de 2 lignes expliquant qu'on s'en fout du nom du joueur.
) = range(10)

#liste des identifiants de toutes les images utilis�es dans les menus du jeu.
(IMG_BG_MAIN,        #image de fond, avec h�ros et magicien, (en dark-fonc�)
 IMG_TITLE_MAIN,     #le titre en jaune-orange : "BLARG"
 IMG_BG_BLARG,       #image du h�ros mort, pour la fin de la partie. (Nom mal choisi, on confond)
 IMG_FLAG_FRENCH,    #drapeau fran�ais
 IMG_FLAG_ENGLISH,   #drapeau rosbif
 IMG_TICK_TRUE,      #case � cocher coch�
 IMG_TICK_FALSE,     #case � cocher pas coch�
 IMG_CRED_SCRL_UP,   #bouton super-large (mais pas �pais) de scrolling des cr�dits vers le haut.
 IMG_CRED_SCRL_DOWN, #bouton super-large (et �pais) de scrolling des cr�dits vers le bas.
 IMG_BACK,           #bouton pour revenir en arri�re quand on est dans les cr�dits
 IMG_FRAME_NAME,     #esp�ce de fen�tre pour demander le nom du joueur
 IMG_BUTT_OK,        #bouton OK. (utilis� dans la fen�tre de nom du joueur)
 IMG_MANUAL,         #grosse image montrant le manuel du jeu, avec les touches.
 IMG_BUTT_RESET,     #esp�ce de pseudo-bouton moche de remise � zero de la config
 IMG_DEDICACE,       #image avec la d�dicace. Appara�t dans le menu principal, quand y'en a une.
) = range(15)
#TRODO : pour plus tard car j'ai la flemme : changer le nom de IMG_BG_BLARG

#options � filer � la fonction pygame.display.set_mode, pour initialiser le mode graphique.
#on peut faire en plein �cran, ou en fen�tre.
#je pr�f�re pas mettre le HWSURFACE et le DOUBLEBUF dans les options.
#Si on a une r�solution qui correspond pas aux proportions de l'�cran,
#�a me fait des vieux bugs d'affichage sur mon bidule.
#Donc tant pis, pas d'acc�l�ration mat�rielles de mes couilles. (pas besoin de toutes fa�ons)
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
    fonction pour propager le changement de langue anglais/fran�ais dans tous les menus du jeu.

    entr�es :
        newLanguage : nouvelle lange � appliquer. LANG_FRENCH ou LANG_ENGL.

        dicAllMenu : dictionnaire contenant tous les menus du jeu.
                     (cl� : identifiant MENU_*)

    Attention, �a change le langage, mais �a enregistre pas ce changement
    dans le fichier de config/sauvegarde. Il faut le faire manuellement, si n�cessaire.
    """

    #si le nouveau langage � activer est le m�me que celui qui est en cours, on fait rien.
    if txtStock.language == newLanguage:
        return

    #on envoie le changement � l'objet qui stocke tous les textes de toutes les langues.
    txtStock.changeLanguage(newLanguage)

    #et on envoie le changement � tous les menus du jeu.
    for keyMenu, menu in dicAllMenu.items():
        menu.changeLanguage()


def mactQuit():
    """
    fonction qui fait quitter le menu en cours.

    plat-dessert : un tuple de message d'ihm, avec tout ce qu'il faut dedans
                   pour quitter le menu.
    """
    return (IHMSG_REDRAW_MENU, IHMSG_QUIT)


#�a c'est un �l�ment de menu qui fait le bind entre la touche Echap,
#et le quittage du menu en cours. Y'en a besoin pour la plupart des menu.
mkeyQuitEsc = MenuSensitiveKey(mactQuit, pygl.K_ESCAPE)

#et �a, c'est un �l�ment de menu qui fait le bind entre n'importe quelle touche/clic de souris,
#et le quittage du menu en cours. Y'en a besoin pour quelques menus
manyQuit = MenuSensitiveAnyKeyButton(mactQuit)


#TRODO pour plus tard : foutre cette classe ailleurs. Elle devrait pas vraiment �tre ici.
#(Elle est plus g�n�rique que les menus.)
class GraphModeChanger():
    """
    classe qui switche le mode plein �cran / windowed. Et qui enregistre l'�tat actuel,
    pour le refiler � du code ext�rieur qui le demande (genre la case � cocher du MenuManagerMain)
    Y'a besoin de la stocker et de la ressortir cette putain de valeur, car elle est pas
    forc�ment en accord avec la GLOB_DATA_ID_SCREEN qui est dans l'archivist. Y'a des fois on
    change le mode graphique sans l'enregistrer. (Par exemple quand on force le mode fen�tr�
    avec le param en ligne de commande. Ou quand on vire le plein �cran car le joueur a
    cliqu� sur un lien internet.)

    fun fact (m�me si je l'ai  peut-�tre d�j� dit ailleurs). La case � cocher du menu principal
    est toujour en accord avec le mode graphique r�el. La valeur GLOB_DATA_ID_SCREEN de
    l'archivist est toujours en accord avec le contenu du fichier de sauvegarde. Mais y'a
    pas forc�ment de coh�rence entre ces deux trucs.
    """

    def __init__(self):
        """
        constructeur of ze obvious.
        """

        #�tat actuel du mode graphique. On utilise les m�mes valeurs que pour la
        #GLOB_DATA_ID_SCREEN, stock�e dans l'archivist. Donc y'a SCREEN_FULL et SCREEN_WINDOWED.
        #L� je l'initialise � une valeur par d�faut � la con. Osef en fait.
        self.currentScreenGlobDataVal = SCREEN_DEFAULT


    def setGraphMode(self, newScreenGlobDataVal):
        """
        change le mode graphique.

        entr�es : newScreenGlobDataVal. valeur de type GLOB_DATA_ID_SCREEN, indiquant le nouveau
                  mode souhait�.

        plat-dessert : screen. objet pygame.surface.Surface, repr�sentant la surface principale
                       sur laquelle on affiche le jeu. Forc�ment faut la renvoyer, puisque cette
                       fonction la red�finit.

        Attention, la fonction ne v�rifie pas que le mode graphique en cours soit diff�rent
        du nouveau mode demand�. Du coup, on peut se retrouver � red�finir le screen pour rien.
        Faut faire la v�rif avant.
        """

        #r�actualisation de la valeur courante du mode graphique.
        self.currentScreenGlobDataVal = newScreenGlobDataVal

        #conversion (mode fen�tre/plein �cran) -> (options du mode graphique)
        displayOption = DIC_DISPLAY_OPT[self.currentScreenGlobDataVal]

        #cr�ation de l'objet pygame.Surface, dans laquelle on affichera le jeu, les menus, tout.
        #(cette action cr�e la fen�tre, ou met en plein �cran, selon ce qui a �t� choisi)
        screen = pygame.display.set_mode(SCREEN_RECT.size, displayOption)

        return screen


    def getScreenGlobDataVal(self):
        """
        r�cup�re la valeur courante du mode graphique.

        plat-dessert : donn�e de type GLOB_DATA_ID_SCREEN.
        """
        return self.currentScreenGlobDataVal

#donc, comme d�j� dit ailleurs, j'aime pas trop ce concept d'instancier � l'arrache un objet,
#pour pouvoir l'importer comme une putain de variable globale de mes couilles. En plus, �a
#fait ex�cuter du code lors du premier import, c'est � dire : on sait pas exactement quand.
#Mais va falloir que je m'y fasse � cette putain de technique, parce qu'elle est quand m�me
#bien pratique.
theGraphModeChanger = GraphModeChanger()
