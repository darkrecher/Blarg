#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blarg version 1.0

Démo du système de menu.
Lancement d'une démo avec des MenuElements standard :
 - des labels affichant du texte,
 - un élément réagissant à la touche Echap.
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
    # Ça ne marche pas forcément pour toutes les fonctions overridables
    # du MenuElement, mais là, ça marche.
    # La valeur IHMSG_TOTALQUIT sert à indiquer qu'on veut quitter
    # complètement l'application.
    return (common.IHMSG_TOTALQUIT, )

def launch_demo_menu_labels():

    # Init de pygame et du screen, comme d'hab'.
    pygame.init()
    SCREEN_RECT = pygame.Rect(0, 0, 400, 300)
    screen = pygame.display.set_mode(SCREEN_RECT.size, 0)
    # Chargement d'une police de caractère. On peut le faire soi-même via
    # les fonctions de pygame, ou récupérer ma police par défaut qui se charge
    # à l'aide de ma librairie "common".
    load_font_infos = common.loadFonts()
    fontDefault = load_font_infos[1]

    # Création de deux MenuElements, affichant un texte à l'écran.
    # Il faut indiquer les coordonnées à l'écran, la police et le texte.
    # Ces MenuElements ne sont pas interactifs.
    # (non cliquables, non focusables).
    label_1 = MenuText(
        pygame.Rect(10, 10, 0, 0),
        fontDefault,
        text="label_1 (j'aurais préféré label_5)")
    label_2 = MenuText(
        pygame.Rect(50, 110, 0, 0),
        fontDefault,
        text="appuyez sur Echap pour quitter.")
    # Création d'un dernier MenuElement, qui n'affiche rien à l'écran,
    # mais qui réagit à une touche particulière.
    # Ce MenuElement réagit à la touche Echap. Lorsqu'elle est appuyée,
    # la fonction mactCloseApp est exécutée.
    mkey_escape_quit = MenuSensitiveKey(
        mactCloseApp,
        pygl.K_ESCAPE)

    # Instanciation, comme d'hab'
    menu_main = MenuManager(screen)
    # On place les MenuElement dans le MenuManager qu'on vient de créer.
    # L'ordre est important, car il définit l'ordre de cyclage de focus.
    # (Quand l'utilisateur appuie sur Tab).
    menu_main.listMenuElem = [ label_1, label_2, mkey_escape_quit ]
    # Cette fonction doit obligatoirement être appelée après que listMenuElem
    # ait été modifiée. Ce n'est pas obligatoire, mais c'est mieux.
    # On peut l'appeler depuis du code extérieur, ou bien hériter un
    # MenuManager, et dans la fonction __init__, définir listMenuElem,
    # puis appeller initFocusCyclingInfo.
    menu_main.initFocusCyclingInfo()
    # Lancement du menu.
    menu_main.handleMenu()

    pygame.quit()

