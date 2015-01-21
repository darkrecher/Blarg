#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

Démo du système de menu.
Lancement d'une démo avec des MenuElements customisés :
des carrés qui réagissent aux événements, et qui les signalent dans un
MenuText associé.

L'utilisateur peut effectuer les actions suivantes :
 - cliquer sur un carré -> le carré prend le focus et s'active immédiatement.
 - touche Tab -> cyclage de focus entre les 3 carrés affichés.
 - touche Espace ou Entrée -> active l'élément ayant le focus.
 - touche Echap -> quitter.

Les clics et la touche Echap sont gérés par le MenuElement customisé, à l'aide
de fonction overridée.

Les touches Tab, Espace et Entrée sont gérées directement par le MenuManager.
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
    Cette classe est un élément de menu affichant un texte.
    Le MenuText de base ne marche pas bien. Si on change le texte en live,
    ça se superpose.
    L'idéal serait de corriger ce bug directement dans la classe MenuText,
    mais j'ai pas envie de changer le code existant parce que j'ai plus
    envie de retoucher et retester tout ce bazar.
    """

    def redefineRectDrawZoneAfterAttribChange(self):
        # self.rectDrawZone_previous permet de se souvenir de la position et
        # de la taille du texte précédent. Si pas de texte précédent,
        # il vaut None.
        if hasattr(self, "rectDrawZone"):
            self.rectDrawZone_previous = self.rectDrawZone
        else:
            self.rectDrawZone_previous = None
        MenuText.redefineRectDrawZoneAfterAttribChange(self)

    def draw(self, surfaceDest):
        """
        Dessine un carré noir, pour effacer le texte précédent.
        Puis dessine le texte à l'écran, comme un MenuText normal.
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
    # chargement d'une police de caractère.
    load_font_infos = common.loadFonts()
    fontDefault = load_font_infos[1]

    # Création d'un premier label. (Texte simple, non interactif)
    label_1 = MenuTextClearable(
        pygame.Rect(10, 10, 0, 0),
        fontDefault,
        text="bonjour !!")
    # Création d'un élément de menu customisé, réagissant aux événements.
    # On lui passe le label en paramètre. Il changera le texte de ce label,
    # afin de signaler les événements détectés.
    event_teller_1 = MenuElemEventTeller(
        pygame.rect.Rect(10, 50, 70, 70),
        "haut_gauche",
        label_1)

    # Création de deux autres couples label + MenuElemEventTeller.
    # Ça permet de bien comprendre ce qu'il se passe lors des cyclages
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
    # Élément qui fait quitter lorsqu'on appuie sur Echap.
    mkey_escape_quit = MenuSensitiveKey(
        mactCloseApp,
        pygl.K_ESCAPE)

    # création du menu, définition de ses éléments, init, lancement.
    menu_main = MenuManager(screen)
    menu_main.listMenuElem = [
        label_1, event_teller_1,
        label_2, event_teller_2,
        label_3, event_teller_3,
        mkey_escape_quit ]
    menu_main.initFocusCyclingInfo()
    menu_main.handleMenu()

    pygame.quit()
