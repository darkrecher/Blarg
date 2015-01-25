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
    label_1 = MenuText(
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
    label_2 = MenuText(
        pygame.Rect(210, 10, 0, 0),
        fontDefault,
        text="bonjour !!")
    event_teller_2 = MenuElemEventTeller(
        pygame.rect.Rect(210, 50, 70, 70),
        "haut_droite",
        label_2)
    label_3 = MenuText(
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

    # D�finition de l'image de fond du menu, et envoi au MenuManager.
    # Il y en a besoin, car le texte des MenuText change. Il faut donc
    # redessiner l'image de fond, puis dessiner le nouveau texte par-dessus.
    # Sinon, les diff�rents textes des MenuText vont se superposer au fur et
    # � mesure qu'ils changent.
    # L'image de fond est un rectangle noir qui prend tout l'�cran.
    img_background = pygame.Surface(SCREEN_RECT.size)
    img_background.fill((0, 0, 0))
    # On ne peut pas donner directement l'image de fond au MenuManager.
    # (C'est mal fichu mais c'est comme �a). Il faut la mettre dans un
    # dictionnaire (qui pourraient �ventuellemment contenir d'autres images
    # utiles pour le MenuManager). Ensuite, on envoie ce dictionnaire, ainsi
    # que la cl� correspondant � l'image de fond.
    img_background_key = 0
    dict_img_background = { img_background_key:img_background }

    # cr�ation du menu, d�finition de ses �l�ments, init, lancement.
    menu_main = MenuManager(screen, dict_img_background, img_background_key)
    menu_main.listMenuElem = [
        label_1, event_teller_1,
        label_2, event_teller_2,
        label_3, event_teller_3,
        mkey_escape_quit ]
    menu_main.initFocusCyclingInfo()
    menu_main.handleMenu()

    pygame.quit()
