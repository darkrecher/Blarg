#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

D�mo du syst�me de menu
Lancement d'une d�mo avec un menu vide, (la classe de base), ne contenant aucun "MenuElement".
Pour quitter la d�mo, appuyer sur le bouton de fermage de fen�tre. (Alt-F4 ne marche pas).
"""


import pygame
from menumng import MenuManager


def launch_demo_menu_empty():

    pygame.init()
    SCREEN_RECT = pygame.Rect(0, 0, 400, 300)
    screen = pygame.display.set_mode(SCREEN_RECT.size, 0)

    menu_empty = MenuManager(screen)
    menu_empty.handleMenu()

    pygame.quit()