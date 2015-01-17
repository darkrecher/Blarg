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


class MenuTextClearable(MenuText):
    """
    Monkey patching.
    La classe MenuTextClearable est un élément de menu qui affiche un texte.
    Mais le MenuText de base ne marche pas bien. Si on change le texte en live,
    ça se superpose.
    L'idéal serait de corriger ce bug directement dans la classe MenuText,
    mais j'ai pas envie de changer le code existant parce que j'ai plus
    envie de retoucher et retester tout ce bazar.
    """
    def redefineRectDrawZoneAfterAttribChange(self):
        if hasattr(self, "rectDrawZone"):
            self.rectDrawZone_previous = self.rectDrawZone
        else:
            self.rectDrawZone_previous = None
        MenuText.redefineRectDrawZoneAfterAttribChange(self)

    def draw(self, surfaceDest):
        """
        Dessine le texte à l'écran, comme un MenuText normal.
        Mais avant, dessine un carré noir, pour effacer le texte d'avant.
        """
        if self.rectDrawZone_previous is not None:
            img_clearing = pygame.Surface(self.rectDrawZone_previous.size).convert()
            img_clearing.fill((0, 0, 0))
            surfaceDest.blit(img_clearing, self.rectDrawZone_previous)
        MenuText.draw(self, surfaceDest)


def mactCloseApp():
    return (common.IHMSG_TOTALQUIT, )

def launch_demo_menu_event_teller():

    pygame.init()
    SCREEN_RECT = pygame.Rect(0, 0, 400, 300)
    screen = pygame.display.set_mode(SCREEN_RECT.size, 0)

    load_font_infos = common.loadFonts()
    fontDefault = load_font_infos[1]

    label_1 = MenuTextClearable(
        pygame.Rect(10, 10, 0, 0),
        fontDefault,
        text="bonjour !!")
    event_teller_1 = MenuElemEventTeller(
        pygame.rect.Rect(10, 50, 70, 70),
        label_1)
    label_2 = MenuTextClearable(
        pygame.Rect(210, 10, 0, 0),
        fontDefault,
        text="bonjour !!")
    event_teller_2 = MenuElemEventTeller(
        pygame.rect.Rect(210, 50, 70, 70),
        label_2)
    label_3 = MenuTextClearable(
        pygame.Rect(10, 160, 0, 0),
        fontDefault,
        text="bonjour !!")
    event_teller_3 = MenuElemEventTeller(
        pygame.rect.Rect(10, 200, 70, 70),
        label_3)
    mkey_escape_quit = MenuSensitiveKey(
        mactCloseApp,
        pygl.K_ESCAPE)

    menu_empty = MenuManager(screen)
    menu_empty.listMenuElem = [
        label_1, event_teller_1,
        label_2, event_teller_2,
        label_3, event_teller_3,
        mkey_escape_quit ]
    menu_empty.initFocusCyclingInfo()
    menu_empty.handleMenu()

    pygame.quit()