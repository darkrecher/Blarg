#/usr/bin/env python
# -*- coding: utf-8 -*-

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
    label_1 = MenuText(
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
    # Élément qui fait quitter lorsqu'on appuie sur Echap.
    mkey_escape_quit = MenuSensitiveKey(
        mactCloseApp,
        pygl.K_ESCAPE)

    # Définition de l'image de fond du menu, et envoi au MenuManager.
    # Il y en a besoin, car le texte des MenuText change. Il faut donc
    # redessiner l'image de fond, puis dessiner le nouveau texte par-dessus.
    # Sinon, les différents textes des MenuText vont se superposer au fur et
    # à mesure qu'ils changent.
    # L'image de fond est un rectangle noir qui prend tout l'écran.
    img_background = pygame.Surface(SCREEN_RECT.size)
    img_background.fill((0, 0, 0))
    # On ne peut pas donner directement l'image de fond au MenuManager.
    # (C'est mal fichu mais c'est comme ça). Il faut la mettre dans un
    # dictionnaire (qui pourraient éventuellemment contenir d'autres images
    # utiles pour le MenuManager). Ensuite, on envoie ce dictionnaire, ainsi
    # que la clé correspondant à l'image de fond.
    img_background_key = 0
    dict_img_background = { img_background_key:img_background }

    # création du menu, définition de ses éléments, init, lancement.
    menu_main = MenuManager(screen, dict_img_background, img_background_key)
    menu_main.listMenuElem = [
        label_1, event_teller_1,
        label_2, event_teller_2,
        label_3, event_teller_3,
        mkey_escape_quit ]
    menu_main.initFocusCyclingInfo()
    menu_main.handleMenu()

    pygame.quit()
