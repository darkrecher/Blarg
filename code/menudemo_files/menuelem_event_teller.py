#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

Démo du système de menu
TODO

bon, il faudrait quoi ?

un label, à qui on change le texte.
un élément de menu spécial, qui réagit à des événements, et change le texte
d'un label (label = autre élément de menu générique)
"""



import pygame
import pygame.locals
pygl = pygame.locals

from common import IHMSG_VOID, IHMSG_REDRAW_MENU, IHMSG_CYCLE_FOCUS_OK
from menuelem import MenuElem


class MenuElemEventTeller(MenuElem):
    """
    TODO
    """

    def __init__(self, draw_zone, menu_elem_text):
        """
        constructeur. (thx captain obvious)
        """
        MenuElem.__init__(self)
        self.acceptFocus = True
        self.draw_zone = draw_zone
        self.carre_rouge = pygame.Surface(self.draw_zone.size).convert()
        self.carre_rouge.fill((200, 0, 0))
        self.menu_elem_text = menu_elem_text
        self.funcAction = self._funcAction

    def _funcAction(self):
        """
        overridé (plus ou moins)
        """
        print "J'ai été activé"
        self.menu_elem_text.changeFontAndText(newText="J'ai été activé")
        return (IHMSG_REDRAW_MENU, )

    def draw(self, surfaceDest):
        """
        overridé
        Dessine un carré rouge.
        """
        surfaceDest.blit(self.carre_rouge, self.draw_zone)

    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        TODO
        """
        #print "hailz"
        return IHMSG_VOID

    def takeStimuliFocusCycling(self):
        print "cyclage de focus"
        return (IHMSG_CYCLE_FOCUS_OK, )


    def takeStimuliGetFocus(self):
        print "je prends le focus"
        self.focusOn = True


    def takeStimuliLoseFocus(self):
        print "je perd le focus"
        self.focusOn = False


