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

from menuelem_event_teller import MenuElemEventTeller


def mactCloseApp():
    return (common.IHMSG_TOTALQUIT, )


def launch_demo_menu_event_teller():

    pygame.init()
    SCREEN_RECT = pygame.Rect(0, 0, 400, 300)
    screen = pygame.display.set_mode(SCREEN_RECT.size, 0)

    load_font_infos = common.loadFonts()
    fontDefault = load_font_infos[1]

    label_1 = MenuText(
        pygame.Rect(10, 10, 0, 0),
        fontDefault,
        text="bonjour !!")
    event_teller = MenuElemEventTeller(
        pygame.rect.Rect(150, 150, 70, 70),
        label_1)
    mkey_escape_quit = MenuSensitiveKey(
        mactCloseApp,
        pygl.K_ESCAPE)

    menu_empty = MenuManager(screen)
    menu_empty.listMenuElem = [ label_1, event_teller, mkey_escape_quit ]
    menu_empty.initFocusCyclingInfo()
    menu_empty.handleMenu()

    pygame.quit()