#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

Démo du système de menu
TODO
"""


import pygame
import pygame.locals
pygl = pygame.locals
import common
from menumng import MenuManager
from menutxt  import MenuText
from menukey  import MenuSensitiveKey

def mactCloseApp():
    return (common.IHMSG_TOTALQUIT, )


def launch_demo_menu_labels():

    pygame.init()
    SCREEN_RECT = pygame.Rect(0, 0, 400, 300)
    screen = pygame.display.set_mode(SCREEN_RECT.size, 0)

    load_font_infos = common.loadFonts()
    fontDefault = load_font_infos[1]

    label_1 = MenuText(
        pygame.Rect(10, 10, 0, 0),
        fontDefault,
        text="label_1 (j'aurais préféré label_5)")
    label_2 = MenuText(
        pygame.Rect(50, 110, 0, 0),
        fontDefault,
        text="appuyez sur Echap pour quitter.")
    mkey_escape_quit = MenuSensitiveKey(
        mactCloseApp,
        pygl.K_ESCAPE)

    menu_empty = MenuManager(screen)
    menu_empty.listMenuElem = [ label_1, label_2, mkey_escape_quit ]
    menu_empty.initFocusCyclingInfo()
    menu_empty.handleMenu()

    pygame.quit()

