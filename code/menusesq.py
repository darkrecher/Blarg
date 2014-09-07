#/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Blarg version 1.0

    La page du jeu sur indieDB : http://www.indiedb.com/games/blarg
    Liens vers d'autres jeux sur mon blog : http://recher.wordpress.com/jeux
    Mon twitter : http://twitter.com/_Recher_

    Ce superbe jeu, son code source, ses images, et son euh... contenu sonore est disponible,
    au choix, sous la licence Art Libre ou la licence CC-BY-SA

    Copyright 2010 Réchèr
    Copyleft : cette oeuvre est libre, vous pouvez la redistribuer et/ou la modifier selon les
    termes de la Licence Art Libre. Vous trouverez un exemplaire de cette Licence sur le site
    Copyleft Attitude http://www.artlibre.org ainsi que sur d'autres sites.

    Creative Commons - Paternité - Partage des Conditions Initiales à l'Identique 2.0 France
    http://creativecommons.org/licenses/by-sa/2.0/fr/deed.fr

date de la dernière relecture-commentage : 21/02/2011

Elément de menu qui réagit quand on clique ou qu'on reste cliqué dans une certaine zone
rectangulaire de l'écran. Cet élément accepte le focus.
Cet élément ne s'affiche pas à l'écran. Si on veut un élément qui réagit à la souris et qui
s'affiche, voir les classe héritée de celle-ci (MenuSensitiveText, MenuSensitiveImg)
"""

#blabla déplacé du fichier zemain à ici. Parce que je raconte vraiment n'importe quoi et
#si on peut éviter de faire peur à d'éventuelles personnes qui hypothétiquement lirait mon code,
#ça peut être socialement intéressant.
#                  LE MOT "CHEVALS"  !!            voilà, merci. Ca va mieux.



import pygame

from common   import (pyRect, IHMSG_VOID,
                      IHMSG_ELEM_WANTFOCUS, IHMSG_ELEM_CLICKED)

from menuelem import MenuElem
import lamoche

#type de cliquage de souris auquel on peut réagir.

(MOUSE_DOWN,     #le joueur vient de cliquer sur la zone, juste là maintenant.
                 #l'activation n'est effectuée qu'une seul fois. Au moment du clic.

 MOUSE_PRESSED,  #le joueur a le bouton appuyé, sur la zone.
                 #l'activation est effectuée en continu, à chaque cycle, tant que le bouton
                 #de souris reste appuyé et que le curseur reste dans la zone.
                 #TRODO pour plus tard : je me sers jamais de ce type de cliquage.
                 #Et à mon avis il est buggé. Eh bien tant pis osef.

 MOUSE_HOVER,    #le joueur a pas besoin de cliquer. Faut juste qu'il soit sur la zone.
                 #L'activation est exécutée en continu, à chaque
                 #cycle, tant que le curseur de souris se trouve sur la zone.

 MOUSE_NONE,     #Ca réagit jamais. Mais ça chope le focus si jamais le curseur passe dessus.

 ) = range(4)

RECT_ZERO = pyRect()



class MenuSensitiveSquare(MenuElem):
    """
    element qu'on clique dessus.
    """

    def __init__(self, funcAction, rectStimZone=RECT_ZERO,
                 clickType=MOUSE_DOWN, inflateDist=0):
        """
        constructeur. (thx captain obvious)

        entrée :
            funcAction :   référence vers la fonction à exécuter quand cet élément de menu est
                activé. (Donc quand le joueur clique sur la zone rectangulaire sensible)

            rectStimZone : Rect. zone rectangulaire sensible qui fait s'activer cet élément.
                les coordonnées sont exprimées localement, en fonction de l'objet conteneur
                (menu ou submenu).
                Si c'est un menu, ça correspond aux coordonnées à l'écran.
                Si c'est un submenu, les décalages qui vont bien seront effectués
                Valeur par défaut : RECT_ZERO, un rectangle avec width=0 et height=0

            clickType : type de cliquage auquel il faut réagir. (valeur MOUSE_* définie au début)

            inflateDist : int. distance d'agrandissement de la zone de dessin, pour obtenir
                la zone de sensibilité. Car c'est cool de mettre une zone de sensibilité
                un peu plus grande. Ainsi, si on a un tout petit bouton, le joueur n'a pas besoin
                de viser pil poil bien comme un sniper avec sa souris.
                Cette inflateDist est appliquée sur les 4 côtés de la zone de dessin.
                Par contre, elle ne sert à rien du tout si on ne définit pas de rectDrawZone.
        """
        MenuElem.__init__(self)

        param = (funcAction, rectStimZone, clickType, inflateDist)
        self.initSensitiveInterface(*param)


    def initSensiInterface(self, funcAction, rectStimZone=RECT_ZERO,
                           clickType=MOUSE_DOWN, inflateDist=0):
        """
        initialisation des infos concernant la zone sensible.

        entrés : voir fonction __init__. C'est les mêmes.

        J'ai pas voulu mettre ce code directement dans l'__init__. Comme ça, on peut
        l'exécuter de manière plus explicite dans les classes héritées.
        (D'autant plus que je fais des héritages multiples car je suis un oufzor)
        """

        #ce menuElem peut être focusé.
        self.acceptFocus = True

        self.funcAction = funcAction
        self.clickType = clickType
        self.rectStimZone = rectStimZone
        self.inflateDist = inflateDist

        #booléen indiquant si le curseur de souris se trouve actuellement sur la zone
        #sensible, ou pas. J'en ai besoin pour le type de cliquage MOUSE_HOVER.
        #Et ça me simplifie un peu la vie pour les autres types, aussi.
        self.mouseHoverOn = False


    def defineStimZoneFromDrawZone(self, newInflateDist=None):
        """
        (re)définit la valeur self.rectStimZone = zone de sensibilité pour la souris,
        en fonction de la valeur self.rectDrawZone = zone sur laquelle on doit dessiner des trucs.

        entrées :
            newInflateDist : int, ou None.
                 Si None : ne sert à rien.
                 Si int : nouvelle valeur qui remplace la valeur actuelle de self.inflateDist

            il faut avoir préalablement défini self.rectDrawZone. (pygame.Rect)

        plat-dessert : rien, mais redéfinition interne de self.rectStimZone
        """

        #prise en compte de la nouvelle valeur de self.inflateDist, si nécessaire.
        if newInflateDist is not None:
            self.inflateDist = newInflateDist

        #redéfinition de self.rectStimZone, si on a bien un self.rectDrawZone.
        #Sinon, on ne peut rien faire.
        if self.rectDrawZone is not None:

            #on prend le rectangle de dessin (self.rectDrawZone), on le recopie,
            #et on l'étend. C'est à dire qu'on repousse chacun des 4 côtés du rectangle,
            #en ajoutant la marge de pixel inflateDist.
            self.rectStimZone = pygame.Rect(self.rectDrawZone)
            self.rectStimZone.inflate_ip(self.inflateDist, self.inflateDist)


    def treatStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        traite les stimulis lié la souris. Ca, c'est la fonction interne, qui
        est appelée par la fonction un peu plus externe takeStimuliMouse.

        Cette fonction n'exécute pas la fonction funcAction. Le but c'est qu'elle soit
        un peu à peu près générique. Comme ça je peux m'en servir pour les classes que
        j'hérite de celle-là.
        Et ça fait du gâteau au chocolat, et moi j'aime bien le gâteau au chocolat.

        entrées : voir menuElem.takeStimuliMouse. C'est les mêmes.

        plat-dessert :
            ihmsgInfoReturn : tuple avec des messages d'ihm. On peut renvoyer les suivants
             - IHMSG_ELEM_WANTFOCUS : l'élément veut le focus, car le curseur de souris
               est passé dessus.
             - IHMSG_ELEM_CLICKED : y'a eu cliquage.

        Et on met également à jour la variable self.mouseHoverOn.
        """

        #initialisation du tuple contenant les messages d'IHM à renvoyer
        ihmsgInfoReturn = IHMSG_VOID

        #on regarde si le pointeur de souris est dans le rectangle sensible.
        #Parce que sinon, on n'en a rien à foutre.
        if self.rectStimZone.collidepoint(mousePos):

            self.mouseHoverOn = True

            if not self.focusOn:
                #on est dans la zone sensible, et on n'a pas le focus.
                #on ajoute le message d'IHM indiquant que l'on veut le focus.
                #Le code extérieur devra se démerder pour donner le focus à cet élément
                #(sinon, il va être triste et il va pleurer, et ça il faut surtout pas)
                ihmsgInfoReturn += (IHMSG_ELEM_WANTFOCUS, )

            #on vérifie si y'a eu un appuyage de souris correspondant à celui qui
            #ferait réagir cet élément.
            if any((self.clickType == MOUSE_DOWN    and mouseDown,
                    self.clickType == MOUSE_PRESSED and mousePressed)):

                ihmsgInfoReturn += (IHMSG_ELEM_CLICKED, )

        else:

            #le pointeur est pas dans la zone sensible. On remet à jour le mouseHoverOn.
            self.mouseHoverOn = False

        return ihmsgInfoReturn


    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        prise en compte des mouvements et des clics de souris.
        (voir description dans la classe MenuElem)
        """
        ihmsgInfo = self.treatStimuliMouse(mousePos, mouseDown, mousePressed)

        if IHMSG_ELEM_CLICKED in ihmsgInfo:
            #yep. On exécute la fonction d'action bindée à cet élément,
            #et on récupère les messages d'IHM que ça renvoie, pour les ajouter au tuple
            #qui regroupe tout.
            ihmsgInfo += self.funcAction()

        return ihmsgInfo


    def update(self):
        """
        Mise à jour périodique de divers trucs. (voir description dans la classe MenuElem)
        """

        #Appel de la mother-class. ça ne sert à rien, car y'a rien dedans, mais ça fait cool.
        ihmsgInfo = MenuElem.update(self)

        #exécution de la funcAction de manière périodique, si c'est demandé, et si
        #le curseur de la souris est sur la zone sensible.
        if self.clickType == MOUSE_HOVER and self.mouseHoverOn:
            ihmsgInfo += self.funcAction()
            return ihmsgInfo

        #sinon, on branle rin.
        return ihmsgInfo
