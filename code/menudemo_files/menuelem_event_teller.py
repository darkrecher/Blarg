#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

Démo du système de menu.
"""


import pygame
import pygame.locals
pygl = pygame.locals

from common import (
    # Les messages d'interface émis par des éléments de menu, à destination
    # du MenuManager. Voir module common pour une description détaillée
    # de la définition de chacun d'eux.
    IHMSG_VOID, IHMSG_REDRAW_MENU, IHMSG_CYCLE_FOCUS_OK, IHMSG_ELEM_WANTFOCUS)
from menuelem import MenuElem


class MenuElemEventTeller(MenuElem):
    """
    Un élément de menu customisé.

    Contient une référence vers un MenuText (élément de menu standard).
    Réagit à des événements, et change en conséquence le texte du MenuText
    référencé.

    Affichage : un carré de couleur.
     - rouge foncé lorsque le focus n'est pas dessus.
     - rouge clair lorsque le focus est dessus.
     - vert lorsqu'il a été activé. L'activation se perd à la perte du focus.

    Les fonctions définies dans cette classe sont des overrides de MenuElem,
    permettant de réagir à différents événements. Voir commentaires de
    MenuElem pour plus de précisions.
    """

    def __init__(self, draw_zone, name, menu_elem_text):
        """
        constructor.

        :param draw_zone: zone de l'écran (pos + taille)
            où sera placé l'élément de menu.
        :param name: nom de l'élément. N'est utilisé que pour le log stdout.
        :param menu_elem_text: référence vers un label. Cet élément modifiera
            le texte du label, lorsque certains événements surviennent.

        :type draw_zone: pygame.rect.Rect
        :type name: string
        :type menu_elem_text: instance de MenuText
        """
        MenuElem.__init__(self)
        self.acceptFocus = True
        self.draw_zone = draw_zone
        # Couleur courante du carré représentant le MenuElem.
        self.color = (150, 50, 50)
        self.colored_square = pygame.Surface(self.draw_zone.size).convert()
        self.colored_square.fill(self.color)
        self.name = name
        self.menu_elem_text = menu_elem_text
        # funcAction est un membre spécifique d'un élément de menu. Il peut
        # être appelé par le code extérieur (fonction contenant les actions à
        # faire lors d'une activation). Si je me contente de l'overrider, ça
        # ne marche pas, car le constructeur lui donne une valeur par défaut
        # (None). Donc je crée une fonction bidon à côté, et je l'attribue
        # au vrai functAction, après l'appel du constructeur père.
        self.funcAction = self._funcAction
        # Indique si les fonctions de perte et de récupération du focus ont
        # provoqué la nécessité d'un redessin global du menu. On demandera
        # ce redessin au code extérieur durant la fonction périodique update.
        # C'est un peu mal fichu, voir commentaire de takeStimuliLoseFocus.
        self.must_redraw = False
        # Indique si la prise de focus provient d'un clic ou d'autre chose.
        # Si ça vient d'un clic, l'élément de menu doit rester avec la couleur
        # verte, car on vient de l'activer. Sinon, il prend la couleur rouge
        # claire indiquant une prise de focus.
        # C'est super mal fichu de devoir gérer ça à la main dans les
        # fonctions overridées, mais j'ai pas mieux.
        # voir aussi : commentaire de takeStimuliMouse.
        self.got_focus_from_click = False
        self.nb_activation_chained = 0

    def _funcAction(self):
        """
         - Change le texte du label associé pour indiquer combien il y a eu
           d'activation de l'élément de menu à la suite.
         - Change la couleur pour le vert.
         - Demande un redessin global du menu pour que tout ce bazar soit pris
           en compte.
        """
        self.nb_activation_chained += 1
        print self.name + ". J'ai ete actived"
        self.menu_elem_text.changeFontAndText(
            newText="activation : " +
            str(self.nb_activation_chained))
        self.color = (0, 250, 0)
        self.colored_square.fill(self.color)
        return (IHMSG_REDRAW_MENU, )

    def draw(self, surfaceDest):
        """
        Dessine un carré avec la couleur courante.
        """
        surfaceDest.blit(self.colored_square, self.draw_zone)

    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        Si l'événement est un clic, et qu'il a lieu dans la zone de
        l'élément de menu : exécute funcAction et demande le focus.
        """
        ihm_msg_result = IHMSG_VOID
        if mouseDown and self.draw_zone.collidepoint(mousePos):
            ihm_msg_result += self.funcAction()
            if not self.focusOn:
                # funcAction mettra la couleur verte.
                # mais comme on renvoie IHMSG_ELEM_WANTFOCUS, le menuManager
                # donnera le focus à l'élément, qui exécutera takeStimuliGetFocus,
                # et ça risque de mettre la couleur rouge clair. Or on veut que ça
                # reste vert. Donc on stocke à l'arrache l'origine du focus dans
                # un booléen.
                self.got_focus_from_click = True
                ihm_msg_result += (IHMSG_ELEM_WANTFOCUS, )
        return ihm_msg_result

    def takeStimuliFocusCycling(self):
        """
        Change le texte du label associé pour indiquer le cyclage de focus.
        Mais on ne le voit jamais, car ce texte est immédiatement recouvert
        suite à un appel à takeStimuliLoseFocus ou à takeStimuliGetFocus,
        qui survient juste après.
        """
        print self.name + ". cyclage de focus"
        self.menu_elem_text.changeFontAndText(newText="cyclage de focus")
        return (IHMSG_REDRAW_MENU, IHMSG_CYCLE_FOCUS_OK, )

    def takeStimuliLoseFocus(self):
        """
         - Change le texte du label associé pour indiquer la perte de focus.
         - Change la couleur pour le rouge foncé.
         - Indique à la fonction update qu'il faudra demander un redessin
           global. (Cette fonction ne peut pas le demander directement).
        """
        self.focusOn = False
        self.nb_activation_chained = 0
        print self.name + ". je perd le focus"
        self.menu_elem_text.changeFontAndText(newText="focus quit")
        self.color = (150, 50, 50)
        self.colored_square.fill(self.color)
        # Les fonctions takeStimuliGetFocus et takeStimuliLoseFocus ne peuvent
        # pas renvoyer des valeurs IHMSG. Donc on ne peut pas demander ici un
        # redraw global du menu.
        # Contournement à l'arrache, on utilise le booléen must_redraw,
        # la fonction update (appelée périodiquement) émettra un
        # IHMSG_REDRAW_MENU lorsque ce sera nécessaire.
        self.must_redraw = True

    def takeStimuliGetFocus(self):
        """
        Si le gain du focus ne provient pas d'un clic :
         - Change le texte du label associé pour indiquer la perte de focus.
         - Change la couleur pour le rouge foncé.
         - Indique à la fonction update qu'il faudra demander un redessin
           global. (Cette fonction ne peut pas le demander directement).
        Si le gain du focus provient d'un clic : ne fait rien, à part un peu
        de log.
        """
        self.focusOn = True
        print self.name + ". je prends le focus"
        if self.got_focus_from_click:
            print self.name + ". mais je met pas la couleur rouge clair,"
            print self.name + ". car c'est un focus qui vient d'un clic."
            self.got_focus_from_click = False
        else:
            self.menu_elem_text.changeFontAndText(newText="focus enter")
            self.color = (250, 0, 0)
            self.colored_square.fill(self.color)
            # voir commentaire de takeStimuliLoseFocus
            self.must_redraw = True

    def update(self):
        """
        Demande (une seule fois) un redessin global du menu, si les fonctions
        de focus ont préalablement signalé qu'il fallait le demander.
        Sinon, ne fait rien et ne demande rien.
        """
        if self.must_redraw:
            self.must_redraw = False
            print self.name + ". demande redessin global via fonction update"
            return (IHMSG_REDRAW_MENU, )
        else:
            return IHMSG_VOID


