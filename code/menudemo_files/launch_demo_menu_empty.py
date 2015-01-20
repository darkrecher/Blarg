#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

D�mo du syst�me de menu.
Lancement d'une d�mo avec un menu vide.

Le MenuManager ne contient aucun "MenuElement".
Pour quitter la d�mo, appuyer sur le bouton de fermage de fen�tre.
Alt-F4 ne marche pas.
"""


import pygame
from menumng import MenuManager


def launch_demo_menu_empty():

    # Init de pygame et cr�ation d'une surface correspondant � l'�cran,
    # comme dans toute application pygame qui se respecte.
    pygame.init()
    SCREEN_RECT = pygame.Rect(0, 0, 400, 300)
    screen = pygame.display.set_mode(SCREEN_RECT.size, 0)

    # Instanciation d'un menumanager.
    menu_empty = MenuManager(screen)
    # Lancement du menu. Il y a une boucle, dans handleMenu, qui d�pile les
    # �v�nements de souris et de clavier, les prend en compte, et/ou les
    # transf�re aux MenuElements contenus dans le menu.
    # L�, on a un menu sans MenuElements, donc il ne se passe pas grand-chose.
    menu_empty.handleMenu()

    pygame.quit()