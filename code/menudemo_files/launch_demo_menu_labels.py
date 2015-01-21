#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

D�mo du syst�me de menu.
Lancement d'une d�mo avec un menu contenant des MenuElements standard :
des labels affichant du texte, et un �l�ment r�agissant � la touche Echap.
"""


import pygame
import pygame.locals
pygl = pygame.locals
import common
from menumng import MenuManager
from menutxt  import MenuText
from menukey  import MenuSensitiveKey


def mactCloseApp():
    """ Quitte l'application. """
    # Un MenuElement peut communiquer avec le MenuManager en renvoyant
    # un tuple contenant des valeurs "IHMSG_xxx".
    # La liste de ces valeurs et leur signification sont dans common.py.
    # �a ne marche pas forc�ment pour toutes les fonctions overridable
    # dans un MenuElement, mais l�, �a marche.
    # la valeur IHMSG_TOTALQUIT sert � indiquer qu'on veut quitter
    # compl�tement l'application.
    return (common.IHMSG_TOTALQUIT, )

def launch_demo_menu_labels():

    # Init de pygame et du screen, comme d'hab'.
    pygame.init()
    SCREEN_RECT = pygame.Rect(0, 0, 400, 300)
    screen = pygame.display.set_mode(SCREEN_RECT.size, 0)
    # Chargement d'une police de caract�re. On peut le faire soi-m�me via
    # les fonctions de pygame, ou r�cup�rer ma police par d�faut qui se charge
    # � l'aide de ma librairie "common".
    load_font_infos = common.loadFonts()
    fontDefault = load_font_infos[1]

    # Cr�ation de deux MenuElements, affichant un texte � l'�cran.
    # Il faut indiquer les coordonn�es � l'�cran, la police et le texte.
    # Ces MenuElements ne sont pas interactifs :
    # non cliquables, non focusables.
    label_1 = MenuText(
        pygame.Rect(10, 10, 0, 0),
        fontDefault,
        text="label_1 (j'aurais pr�f�r� label_5)")
    label_2 = MenuText(
        pygame.Rect(50, 110, 0, 0),
        fontDefault,
        text="appuyez sur Echap pour quitter.")
    # Cr�ation d'un dernier MenuElement, qui n'affiche rien � l'�cran,
    # mais qui r�agit � une touche particuli�re.
    # Ce MenuElement r�agit � la touche Echap. Lorsqu'elle est appuy�e,
    # la fonction mactCloseApp est ex�cut�e.
    mkey_escape_quit = MenuSensitiveKey(
        mactCloseApp,
        pygl.K_ESCAPE)

    # Instanciation, comme d'hab'
    menu_main = MenuManager(screen)
    # On place les MenuElement dans le menu qu'on vient de cr�er. L'ordre
    # est important, car il d�finit l'ordre de focus (quand l'utilisateur
    # appuie sur Tab).
    menu_main.listMenuElem = [ label_1, label_2, mkey_escape_quit ]
    # Cette fonction doit obligatoirement �tre appel�e apr�s une red�finition
    # du contenu de listMenuElem. Ce n'est pas obligatoire, mais c'est mieux.
    # On peut l'appeler depuis du code ext�rieur, ou bien h�riter un
    # MenuManager, et dans la fonction __init__, on d�finit directement
    # listMenuElem, puis on appelle initFocusCyclingInfo.
    menu_main.initFocusCyclingInfo()
    # Lancement du menu.
    menu_main.handleMenu()

    pygame.quit()

