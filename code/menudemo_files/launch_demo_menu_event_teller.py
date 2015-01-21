#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

D�mo du syst�me de menu.
Lancement d'une d�mo avec des MenuElements customis�s :
des carr�s qui r�agissent aux �v�nements, et qui les signalent dans un
MenuText associ�.

L'utilisateur peut effectuer les actions suivantes :
 - cliquer sur un carr� -> le carr� prend le focus et s'active imm�diatement.
 - touche Tab -> cyclage de focus entre les 3 carr�s affich�s.
 - touche Espace ou Entr�e -> active l'�l�ment ayant le focus.
 - touche Echap -> quitter.

Les clics et la touche Echap sont g�r�s par le MenuElement customis�, � l'aide
de fonction overrid�e.

Les touches Tab, Espace et Entr�e sont g�r�es directement par le MenuManager.
"""


import pygame
import pygame.locals
pygl = pygame.locals
import common
from menumng import MenuManager
from menutxt import MenuText
from menukey import MenuSensitiveKey

from menuelem_event_teller import MenuElemEventTeller


class MenuTextClearable(MenuText):
    """
    Monkey patching.
    Cette classe est un �l�ment de menu affichant un texte.
    Le MenuText de base ne marche pas bien. Si on change le texte en live,
    �a se superpose.
    L'id�al serait de corriger ce bug directement dans la classe MenuText,
    mais j'ai pas envie de changer le code existant parce que j'ai plus
    envie de retoucher et retester tout ce bazar.
    """

    def redefineRectDrawZoneAfterAttribChange(self):
        # self.rectDrawZone_previous permet de se souvenir de la position et
        # de la taille du texte pr�c�dent. Si pas de texte pr�c�dent,
        # il vaut None.
        if hasattr(self, "rectDrawZone"):
            self.rectDrawZone_previous = self.rectDrawZone
        else:
            self.rectDrawZone_previous = None
        MenuText.redefineRectDrawZoneAfterAttribChange(self)

    def draw(self, surfaceDest):
        """
        Dessine un carr� noir, pour effacer le texte pr�c�dent.
        Puis dessine le texte � l'�cran, comme un MenuText normal.
        """
        if self.rectDrawZone_previous is not None:
            img_clearing = pygame.Surface(self.rectDrawZone_previous.size)
            img_clearing = img_clearing.convert()
            img_clearing.fill((0, 0, 0))
            surfaceDest.blit(img_clearing, self.rectDrawZone_previous)
        MenuText.draw(self, surfaceDest)


def mactCloseApp():
    """ Quitte l'application. """
    return (common.IHMSG_TOTALQUIT, )

def launch_demo_menu_event_teller():

    # Init de pygame et du screen, comme d'hab'.
    pygame.init()
    SCREEN_RECT = pygame.Rect(0, 0, 400, 300)
    screen = pygame.display.set_mode(SCREEN_RECT.size, 0)
    # chargement d'une police de caract�re.
    load_font_infos = common.loadFonts()
    fontDefault = load_font_infos[1]

    # Cr�ation d'un premier label. (Texte simple, non interactif)
    label_1 = MenuTextClearable(
        pygame.Rect(10, 10, 0, 0),
        fontDefault,
        text="bonjour !!")
    # Cr�ation d'un �l�ment de menu customis�, r�agissant aux �v�nements.
    # On lui passe le label en param�tre. Il changera le texte de ce label,
    # afin de signaler les �v�nements d�tect�s.
    event_teller_1 = MenuElemEventTeller(
        pygame.rect.Rect(10, 50, 70, 70),
        "haut_gauche",
        label_1)

    # Cr�ation de deux autres couples label + MenuElemEventTeller.
    # �a permet de bien comprendre ce qu'il se passe lors des cyclages
    # de focus avec Tab.
    label_2 = MenuTextClearable(
        pygame.Rect(210, 10, 0, 0),
        fontDefault,
        text="bonjour !!")
    event_teller_2 = MenuElemEventTeller(
        pygame.rect.Rect(210, 50, 70, 70),
        "haut_droite",
        label_2)
    label_3 = MenuTextClearable(
        pygame.Rect(10, 160, 0, 0),
        fontDefault,
        text="bonjour !!")
    event_teller_3 = MenuElemEventTeller(
        pygame.rect.Rect(10, 200, 70, 70),
        "bas_gauche",
        label_3)
    # �l�ment qui fait quitter lorsqu'on appuie sur Echap.
    mkey_escape_quit = MenuSensitiveKey(
        mactCloseApp,
        pygl.K_ESCAPE)

    # cr�ation du menu, d�finition de ses �l�ments, init, lancement.
    menu_main = MenuManager(screen)
    menu_main.listMenuElem = [
        label_1, event_teller_1,
        label_2, event_teller_2,
        label_3, event_teller_3,
        mkey_escape_quit ]
    menu_main.initFocusCyclingInfo()
    menu_main.handleMenu()

    pygame.quit()
