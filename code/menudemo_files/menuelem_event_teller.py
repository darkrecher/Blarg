#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

D�mo du syst�me de menu
TODO

bon, il faudrait quoi ?

un label, � qui on change le texte.
un �l�ment de menu sp�cial, qui r�agit � des �v�nements, et change le texte
d'un label (label = autre �l�ment de menu g�n�rique)
"""



import pygame
import pygame.locals
pygl = pygame.locals

from common import (
    IHMSG_VOID, IHMSG_REDRAW_MENU, IHMSG_CYCLE_FOCUS_OK, IHMSG_ELEM_WANTFOCUS)
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
        self.color = (150, 50, 50)
        self.carre_rouge = pygame.Surface(self.draw_zone.size).convert()
        self.carre_rouge.fill(self.color)
        self.menu_elem_text = menu_elem_text
        self.funcAction = self._funcAction
        self.must_redraw = False
        self.got_focus_from_click = False
        self.nb_activation_chained = 0

    def _funcAction(self):
        """
        overrid� (plus ou moins)
        """
        print "J'ai ete actived"
        self.menu_elem_text.changeFontAndText(newText="activation")
        self.color = (0, 250, 0)
        self.carre_rouge.fill(self.color)
        return (IHMSG_REDRAW_MENU, )

    def draw(self, surfaceDest):
        """
        Dessine un carr� rouge.
        """
        surfaceDest.blit(self.carre_rouge, self.draw_zone)

    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        ihm_msg_result = IHMSG_VOID
        if mouseDown and self.draw_zone.collidepoint(mousePos):
            ihm_msg_result += self.funcAction()
            if not self.focusOn:
                # funcAction mettra la couleur verte.
                # mais comme on renvoie IHMSG_ELEM_WANTFOCUS, le menuManager
                # donnera le focus � l'�l�ment, qui ex�cutera takeStimuliGetFocus,
                # et �a risque de mettre la couleur rouge clair. Or on veut que �a
                # reste vert. Donc on stocke � l'arrache l'origine du focus dans
                # un bool�en.
                self.got_focus_from_click = True
                ihm_msg_result += (IHMSG_ELEM_WANTFOCUS, )
        return ihm_msg_result

    def takeStimuliFocusCycling(self):
        print "cyclage de focus"
        self.menu_elem_text.changeFontAndText(newText="cyclage de focus")
        return (IHMSG_REDRAW_MENU, IHMSG_CYCLE_FOCUS_OK, )

    def takeStimuliLoseFocus(self):
        self.focusOn = False
        self.nb_activation_chained = 0 # WIP TODO
        print "je perd le focus"
        self.menu_elem_text.changeFontAndText(newText="focus quit")
        self.color = (150, 50, 50)
        self.carre_rouge.fill(self.color)
        # Les fonctions takeStimuliGetFocus et takeStimuliLoseFocus ne peuvent
        # pas renvoyer des valeurs IHMSG. Donc on ne peut pas demander ici un
        # redraw global du menu.
        # Contournement � l'arrache, on utilise le bool�en must_redraw,
        # la fonction update (appel�e p�riodiquement) �mettra un
        # IHMSG_REDRAW_MENU lorsque ce sera n�cessaire.
        self.must_redraw = True

    def takeStimuliGetFocus(self):
        self.focusOn = True
        print "je prends le focus"
        if self.got_focus_from_click:
            print "mais je met pas la couleur rouge clair,"
            print "car c'est un focus qui vient d'un clic."
            self.got_focus_from_click = False
        else:
            self.menu_elem_text.changeFontAndText(newText="focus enter")
            self.color = (250, 0, 0)
            self.carre_rouge.fill(self.color)
            # voir commentaire de takeStimuliLoseFocus
            self.must_redraw = True

    def update(self):
        if self.must_redraw:
            self.must_redraw = False
            print "demande redessin global via la fonction update"
            return (IHMSG_REDRAW_MENU, )
        else:
            return IHMSG_VOID


