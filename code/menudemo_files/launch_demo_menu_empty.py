#/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blarg version 1.0

Démo du système de menu.
Lancement d'une démo avec un menu vide.

Crée un MenuManager, ne contenant aucun "MenuElement".
Pour quitter la démo, appuyer sur le bouton de fermage de fenêtre.
Alt-F4 ne marche pas.
"""


import pygame
from menumng import MenuManager


def launch_demo_menu_empty():

    # Init de pygame et création d'une surface correspondant à l'écran,
    # comme dans toute application pygame qui se respecte.
    pygame.init()
    SCREEN_RECT = pygame.Rect(0, 0, 400, 300)
    screen = pygame.display.set_mode(SCREEN_RECT.size, 0)

    # Instanciation d'un MenuManager.
    menu_empty = MenuManager(screen)
    # Lancement du menu. Il y a une boucle, dans handleMenu, qui :
    #  - dépile les événements de souris et de clavier,
    #  - les prend en compte pour lui-même ou bien
    #  - les transfère aux MenuElements contenus dans le menu.
    # Là, on a un menu sans MenuElements, donc il ne se passe pas grand-chose.
    menu_empty.handleMenu()

    pygame.quit()