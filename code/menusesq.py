#/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Blarg version 1.0

    La page du jeu sur indieDB : http://www.indiedb.com/games/blarg
    Liens vers d'autres jeux sur mon blog : http://recher.wordpress.com/jeux
    Mon twitter : http://twitter.com/_Recher_

    Ce superbe jeu, son code source, ses images, et son euh... contenu sonore est disponible,
    au choix, sous la licence Art Libre ou la licence CC-BY-SA

    Copyright 2010 R�ch�r
    Copyleft : cette oeuvre est libre, vous pouvez la redistribuer et/ou la modifier selon les
    termes de la Licence Art Libre. Vous trouverez un exemplaire de cette Licence sur le site
    Copyleft Attitude http://www.artlibre.org ainsi que sur d'autres sites.

    Creative Commons - Paternit� - Partage des Conditions Initiales � l'Identique 2.0 France
    http://creativecommons.org/licenses/by-sa/2.0/fr/deed.fr

date de la derni�re relecture-commentage : 21/02/2011

El�ment de menu qui r�agit quand on clique ou qu'on reste cliqu� dans une certaine zone
rectangulaire de l'�cran. Cet �l�ment accepte le focus.
Cet �l�ment ne s'affiche pas � l'�cran. Si on veut un �l�ment qui r�agit � la souris et qui
s'affiche, voir les classe h�rit�e de celle-ci (MenuSensitiveText, MenuSensitiveImg)
"""

#blabla d�plac� du fichier zemain � ici. Parce que je raconte vraiment n'importe quoi et
#si on peut �viter de faire peur � d'�ventuelles personnes qui hypoth�tiquement lirait mon code,
#�a peut �tre socialement int�ressant.
#                  LE MOT "CHEVALS"  !!            voil�, merci. Ca va mieux.



import pygame

from common   import (pyRect, IHMSG_VOID,
                      IHMSG_ELEM_WANTFOCUS, IHMSG_ELEM_CLICKED)

from menuelem import MenuElem
import lamoche

#type de cliquage de souris auquel on peut r�agir.

(MOUSE_DOWN,     #le joueur vient de cliquer sur la zone, juste l� maintenant.
                 #l'activation n'est effectu�e qu'une seul fois. Au moment du clic.

 MOUSE_PRESSED,  #le joueur a le bouton appuy�, sur la zone.
                 #l'activation est effectu�e en continu, � chaque cycle, tant que le bouton
                 #de souris reste appuy� et que le curseur reste dans la zone.
                 #TRODO pour plus tard : je me sers jamais de ce type de cliquage.
                 #Et � mon avis il est bugg�. Eh bien tant pis osef.

 MOUSE_HOVER,    #le joueur a pas besoin de cliquer. Faut juste qu'il soit sur la zone.
                 #L'activation est ex�cut�e en continu, � chaque
                 #cycle, tant que le curseur de souris se trouve sur la zone.

 MOUSE_NONE,     #Ca r�agit jamais. Mais �a chope le focus si jamais le curseur passe dessus.

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

        entr�e :
            funcAction :   r�f�rence vers la fonction � ex�cuter quand cet �l�ment de menu est
                activ�. (Donc quand le joueur clique sur la zone rectangulaire sensible)

            rectStimZone : Rect. zone rectangulaire sensible qui fait s'activer cet �l�ment.
                les coordonn�es sont exprim�es localement, en fonction de l'objet conteneur
                (menu ou submenu).
                Si c'est un menu, �a correspond aux coordonn�es � l'�cran.
                Si c'est un submenu, les d�calages qui vont bien seront effectu�s
                Valeur par d�faut : RECT_ZERO, un rectangle avec width=0 et height=0

            clickType : type de cliquage auquel il faut r�agir. (valeur MOUSE_* d�finie au d�but)

            inflateDist : int. distance d'agrandissement de la zone de dessin, pour obtenir
                la zone de sensibilit�. Car c'est cool de mettre une zone de sensibilit�
                un peu plus grande. Ainsi, si on a un tout petit bouton, le joueur n'a pas besoin
                de viser pil poil bien comme un sniper avec sa souris.
                Cette inflateDist est appliqu�e sur les 4 c�t�s de la zone de dessin.
                Par contre, elle ne sert � rien du tout si on ne d�finit pas de rectDrawZone.
        """
        MenuElem.__init__(self)

        param = (funcAction, rectStimZone, clickType, inflateDist)
        self.initSensitiveInterface(*param)


    def initSensiInterface(self, funcAction, rectStimZone=RECT_ZERO,
                           clickType=MOUSE_DOWN, inflateDist=0):
        """
        initialisation des infos concernant la zone sensible.

        entr�s : voir fonction __init__. C'est les m�mes.

        J'ai pas voulu mettre ce code directement dans l'__init__. Comme �a, on peut
        l'ex�cuter de mani�re plus explicite dans les classes h�rit�es.
        (D'autant plus que je fais des h�ritages multiples car je suis un oufzor)
        """

        #ce menuElem peut �tre focus�.
        self.acceptFocus = True

        self.funcAction = funcAction
        self.clickType = clickType
        self.rectStimZone = rectStimZone
        self.inflateDist = inflateDist

        #bool�en indiquant si le curseur de souris se trouve actuellement sur la zone
        #sensible, ou pas. J'en ai besoin pour le type de cliquage MOUSE_HOVER.
        #Et �a me simplifie un peu la vie pour les autres types, aussi.
        self.mouseHoverOn = False


    def defineStimZoneFromDrawZone(self, newInflateDist=None):
        """
        (re)d�finit la valeur self.rectStimZone = zone de sensibilit� pour la souris,
        en fonction de la valeur self.rectDrawZone = zone sur laquelle on doit dessiner des trucs.

        entr�es :
            newInflateDist : int, ou None.
                 Si None : ne sert � rien.
                 Si int : nouvelle valeur qui remplace la valeur actuelle de self.inflateDist

            il faut avoir pr�alablement d�fini self.rectDrawZone. (pygame.Rect)

        plat-dessert : rien, mais red�finition interne de self.rectStimZone
        """

        #prise en compte de la nouvelle valeur de self.inflateDist, si n�cessaire.
        if newInflateDist is not None:
            self.inflateDist = newInflateDist

        #red�finition de self.rectStimZone, si on a bien un self.rectDrawZone.
        #Sinon, on ne peut rien faire.
        if self.rectDrawZone is not None:

            #on prend le rectangle de dessin (self.rectDrawZone), on le recopie,
            #et on l'�tend. C'est � dire qu'on repousse chacun des 4 c�t�s du rectangle,
            #en ajoutant la marge de pixel inflateDist.
            self.rectStimZone = pygame.Rect(self.rectDrawZone)
            self.rectStimZone.inflate_ip(self.inflateDist, self.inflateDist)


    def treatStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        traite les stimulis li� la souris. Ca, c'est la fonction interne, qui
        est appel�e par la fonction un peu plus externe takeStimuliMouse.

        Cette fonction n'ex�cute pas la fonction funcAction. Le but c'est qu'elle soit
        un peu � peu pr�s g�n�rique. Comme �a je peux m'en servir pour les classes que
        j'h�rite de celle-l�.
        Et �a fait du g�teau au chocolat, et moi j'aime bien le g�teau au chocolat.

        entr�es : voir menuElem.takeStimuliMouse. C'est les m�mes.

        plat-dessert :
            ihmsgInfoReturn : tuple avec des messages d'ihm. On peut renvoyer les suivants
             - IHMSG_ELEM_WANTFOCUS : l'�l�ment veut le focus, car le curseur de souris
               est pass� dessus.
             - IHMSG_ELEM_CLICKED : y'a eu cliquage.

        Et on met �galement � jour la variable self.mouseHoverOn.
        """

        #initialisation du tuple contenant les messages d'IHM � renvoyer
        ihmsgInfoReturn = IHMSG_VOID

        #on regarde si le pointeur de souris est dans le rectangle sensible.
        #Parce que sinon, on n'en a rien � foutre.
        if self.rectStimZone.collidepoint(mousePos):

            self.mouseHoverOn = True

            if not self.focusOn:
                #on est dans la zone sensible, et on n'a pas le focus.
                #on ajoute le message d'IHM indiquant que l'on veut le focus.
                #Le code ext�rieur devra se d�merder pour donner le focus � cet �l�ment
                #(sinon, il va �tre triste et il va pleurer, et �a il faut surtout pas)
                ihmsgInfoReturn += (IHMSG_ELEM_WANTFOCUS, )

            #on v�rifie si y'a eu un appuyage de souris correspondant � celui qui
            #ferait r�agir cet �l�ment.
            if any((self.clickType == MOUSE_DOWN    and mouseDown,
                    self.clickType == MOUSE_PRESSED and mousePressed)):

                ihmsgInfoReturn += (IHMSG_ELEM_CLICKED, )

        else:

            #le pointeur est pas dans la zone sensible. On remet � jour le mouseHoverOn.
            self.mouseHoverOn = False

        return ihmsgInfoReturn


    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        prise en compte des mouvements et des clics de souris.
        (voir description dans la classe MenuElem)
        """
        ihmsgInfo = self.treatStimuliMouse(mousePos, mouseDown, mousePressed)

        if IHMSG_ELEM_CLICKED in ihmsgInfo:
            #yep. On ex�cute la fonction d'action bind�e � cet �l�ment,
            #et on r�cup�re les messages d'IHM que �a renvoie, pour les ajouter au tuple
            #qui regroupe tout.
            ihmsgInfo += self.funcAction()

        return ihmsgInfo


    def update(self):
        """
        Mise � jour p�riodique de divers trucs. (voir description dans la classe MenuElem)
        """

        #Appel de la mother-class. �a ne sert � rien, car y'a rien dedans, mais �a fait cool.
        ihmsgInfo = MenuElem.update(self)

        #ex�cution de la funcAction de mani�re p�riodique, si c'est demand�, et si
        #le curseur de la souris est sur la zone sensible.
        if self.clickType == MOUSE_HOVER and self.mouseHoverOn:
            ihmsgInfo += self.funcAction()
            return ihmsgInfo

        #sinon, on branle rin.
        return ihmsgInfo
