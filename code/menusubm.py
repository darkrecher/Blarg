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

date de la dernière relecture-commentage : 10/02/2011

élément de menu qui contient, gère, et affiche d'autres trucs (une liste de menuElem)
on peut faire scroller horizontalement et verticalement ces trucs

BIG BIG TRODO : il y a du code commun entre le SubMenu et le MenuManager,
factoriser tout ça quand on aura envie.
Pas là. Là, j'en ai chié pour faire ce tas de merde, j'en ai marre.

BIG BIG TRODO ENCORE PIRE : peut être qu'en fait c'est complètement de la merde cette classe.
Et que je peux obtenir les mêmes "aspects fonctionnels" avec des menuElem mobiles,
et limités à une certaine zone d'affichage à l'écran.
Mais nous verrons cela une autre fois.

"""

import pygame
import pygame.locals
pygl = pygame.locals

from common import (pyRect, pyRectTuple, oppRect, COLOR_BLACK,
                    IHMSG_ELEM_WANTFOCUS, IHMSG_VOID, IHMSG_CYCLE_FOCUS_OK)

from menuelem import MenuElem, cycleFocus



class MenuSubMenu(MenuElem):
    """
    machin. (chai jamais quoi mettre ici.)
    """

    def __init__(self, rectDrawZone, listMenuElemInside, scrollLimit=(0, 0)):
        """
        constructeur. (thx captain obvious)

        entrée :
            rectDrawZone : Rect indiquant la zone dans laquelle on dessine les MenuElem
            contenus à l'intérieur du subMenu. Ce rect est relatif à la surface de destination
            du subMenu. C'est à dire, en général, le screen. Mais ça pourrait être autre chose.
            On le spécifie en param dans la méthode draw.
            Si y'a des MenuElem qui dépassent entièrement ou partiellement
            de cette zone, ils seront coupés. (Tu couperas ça au montage, Potard)
            (C'était une phrase qui date de 15 ans, de fun radio ou skyrock. Désolé).

            listMenuElemInside : liste de MenuElem à mettre dans ce subMenu.
            Les coordonnées de ces MenuElem sont définies par rapport
            aux coordonnées du SubMenu. Ce ne sont pas les coordonnées "absolues".
            Ne pas mettre de coordonnées négatives, ça va pas s'afficher.

            scrollLimit : tuple de deux entiers Y1 et Y2. Indique les limites hautes et basses
            du scrolling vertical. (Donc Y1 negatif ou nul, et Y2 positif ou nul).
            Enfin c'est pas obligé, mais si on fait autrement, ça fait bizarre et crétin.
            Par défaut : Y1 = Y2 = 0. C'est à dire qu'on peut pas scroller du tout.
        """

        #mother-class. ouech ouech.
        MenuElem.__init__(self)

        #ce MenuElem accepte le focus. youpi !
        self.acceptFocus = True

        #branchement de la fonction d'action vers une fonction interne.
        #Voir description de cette fonction, tout à la fin de ce fichier.
        #(Putain, je l'ai déjà dit, mais j'adore vraiment le mot "interne". Il fait trop bien)
        self.funcAction = self.funcTransmitActionOnFocus

        #définition du rectangle d'affichage et du rectangle de sensibilité à la souris.
        #(C'est le même. Ha !!!) Tiens en théorie je devrais peut être ajouter une petite
        #marge, pour être sur de ne pas couper la marge d'un éventuel SensitiveText
        #qui serait placée au bord du SubMenu. Ah. eh bien je m'en tamponne.
        self.rectDrawZone = rectDrawZone
        self.rectStimZone = rectDrawZone

        self.listMenuElemInside = listMenuElemInside

        #création de la surface interne contenant les dessins de tous les éléments internes.
        self.renderElemInside()

        #zone de départ, de la surface interne, qui sera blittée vers la surface de destination.
        #On part du coin haut-gauche de la surface interne, et on tronque à la taille de la zone
        #d'affichage du SubMenu.  Quand on scrolle vertical, la coord Y de ce rect change.
        self.sourceRectToBlit = pygame.Rect((0, 0), self.rectDrawZone.size)

        #Référence vers le MenuElem interne ayant le focus interne.
        #Quand le SubMenu prend le focus, il est censé donner un "sous-focus" à l'un de ses
        #MenuElem interne.
        #(Concrètement, ça sert à rien que le SubMenu en lui même ait le focus, il s'en tape)
        self.focusedElemInside = None

        self.scrollTop, self.scrollBottom = scrollLimit


    def renderElemInside(self):
        """
        on va foutre le dessin de tous les sous-MenuElem, dans une grosse
        surface "interne". Pour afficher le SubMenu, on se contentera de blitter cette surface.

        TRODO pour plus tard : MEGA BOURRIN. Si on a un subMenu de 10m de haut avec
        plein de blabla dedans (genre, les Credits), ça fait une surface de 10m de haut
        qui squatte toute la mémoire pour pas grand chose.
        Pour l'instant, je m'en tamponne la courge.

        Et donc ça, c'est la fonction pour pré-dessiner la surface interne.
        Son but, c'est de définir self.surfaceInside
        """

        #Il faut d'abord déterminer la taille de cette surface interne, de façon
        #à ce qu'elle puisse contenir tous les sous-MenuElem.
        #Il faut donc trouver :
        #la position du côté droit du sous-MenuElem le plus à droite, pour avoir la largeur,
        #et la position du bas du sous-MenuElem le plus en bas, pour avoir la hauteur.
        #(on considère que le haut-gauche c'est 0,0, même si y'a pas de sous-MenuElem à cet
        #endroit. Et c'est pour ça qu'il faut pas en mettre avec des coord négatives.
        #Car ils seront en partie ou totalement coupés.)

        #détermination de la largeur
        #on récupère la liste des coordonnées X des côtés droit des sous-MenuElem
        #(plus exactement, tous les MenuElem qui s'affichent, les autres osef)
        listXCoordRight = [ menuElem.rectDrawZone.right
                            for menuElem in self.listMenuElemInside
                            if menuElem.rectDrawZone is not None ]

        #récupération de la coord max, c'est à dire la plus à droite.
        XCoordMax = max(listXCoordRight)

        #détemrination de la longueur.
        #on récupère la liste des coordonnées Y des bas de tous les sous-MenuElem qui s'affichent.
        listYCoordBottom =[ menuElem.rectDrawZone.bottom
                            for menuElem in self.listMenuElemInside
                            if menuElem.rectDrawZone is not None ]

        #récupération de la coord max, c'est à dire la plus en bas
        YCoordMax = max(listYCoordBottom)

        #création de la surface interne, avec la largeur et la hauteur trouvée.
        self.surfaceInside = pygame.Surface( (XCoordMax, YCoordMax) )

        #couleur transparente = couleur noire. Ca veut dire que je pourrais jamais mettre
        #de noir quand je dessinerais mes MenuElem. Bon c'est zarb, mais j'y survivrais.
        #Sinon, je sais pas ce que c'est que ce RLEACCEL, mais ça doit être cool.
        self.surfaceInside.set_colorkey(COLOR_BLACK, pygl.RLEACCEL)

        #dessin des MenuElem sur la surface interne
        for menuElem in self.listMenuElemInside:
            menuElem.draw(self.surfaceInside)


    def scrollVertically(self, moveY):
        """
        fonction exécutée par le code extérieur. Elle permet de décaler les MenuElem,
        pour les afficher un peu plus haut ou un peu plus bas. Ca fait un scrolling.

        entrées :
            moveY : int (positif ou negatif). Nombre de pixel de déplacement vertical
                    positif : vers le bas. negatif : vers le haut.
        """

        #On bouge le rectangle définissant la zone de la surface interne à bliter.
        self.sourceRectToBlit.move_ip(0, moveY)

        #clamping vertical de ce rectangle.

        #si on est allé trop haut, on se remet à la limite haute.
        if self.sourceRectToBlit.top < self.scrollTop:
            self.sourceRectToBlit.top = self.scrollTop

        #si on est allé trop bas, blablabla. Le clamping est toujours sur le Rect.top,
        #parce que scrollLimit définit
        #la zone dans laquelle a le droit de se trouver le point sup-gauche de la zone à blitter,
        #et non pas la zone dans laquelle a le droit de se trouver toute la zone à blitter.
        elif self.sourceRectToBlit.top > self.scrollBottom:
            self.sourceRectToBlit.top = self.scrollBottom

        #on fait pas de redessinage, ni de refresh.
        #C'est le code extérieur qui doit s'occuper de ça.


    def scrollSetPosition(self, position=0):
        """
        fonction exécutée par le code extérieur. Elle permet de remettre à zero
        la position verticale des MenuElem.
        """

        #On réinitialise le rectangle définissant la zone de la surface interne à bliter.
        self.sourceRectToBlit.y = position

        #Pas de clamping. La position 0 est censée être comprise dans les limites autorisées,
        #si ça l'est pas, c'est bizarre. Et on s'en occupe pas.

        #et donc, comme pour scrollVertically, pas de redessinage, ni de refresh.


    def focusOnElem(self, elemAskingFocus):
        """
        Change le focus interne, pour le mettre sur un autre sous-MenuElem.

        entrées :
            elemAskingFocus : sous-MenuElem qui veut le focus.

        TRODO : putain de fonction pareil que le MenuManager. A factoriser
        """

        #si le focus était déjà sur un autre élément, on le lui enlève.
        if self.focusedElemInside is not None:
            self.focusedElemInside.takeStimuliLoseFocus()

        #modification de l'attribut pointant vers le sous-elem focusé.
        self.focusedElemInside = elemAskingFocus
        #on donne le focus au sous-elem qui n'en veut.
        self.focusedElemInside.takeStimuliGetFocus()


    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        prise en compte des mouvements et des clics de souris.
        (voir description dans la motheur-classe MenuElem)

        Il faut transmettre les stimulis de souris à tous les sous-menuElem
        """

        #tuple contenant les messages d'ihm, à renvoyer au code appelant.
        #il contiendra à peu près les messages d'ihm renvoyé par les sous-MenuElem.
        #voir plus loin pour l'explication du "à peu près".
        ihmsgInfoReturn = IHMSG_VOID

        if self.rectStimZone.collidepoint(mousePos):

            #le stimuli de la souris se trouve dans la zone du SubMenu.
            #Faut donc le prendre en compte.
            #
            #On doit transmettre ce stimuli de souris à tous les MenuElem interne.
            #Mais pour cela, il faut appliquer les décalages. On doit convertir
            #les coordonnées de la souris par rapport au code appelant, en
            #les coordonnées de la souris en local, par rapport à ce SubMenu

            #on part des coordonnées données par le code appelant. (A priori, c'est les
            #coordonnées de la souris à l'écran. Sauf si on a un SubMenu dans un SubMenu.
            #Mais ça on s'en fout).
            rectPosMouseInSubMenu = pyRectTuple(mousePos)

            #on applique le décalage lié au scrolling vertical du SubMenu
            rectPosMouseInSubMenu.move_ip(self.sourceRectToBlit.topleft)

            #et on applique le décalage par rapport à la position du SubMenu dans
            #l'objet qui le contient. Faut retirer la coordonnée du SubMenu, parce que euh...
            #Ouais là je saurais pas expliquer, mais faites un dessin, vous comprendrez.
            rectPosMouseInSubMenu.move_ip(oppRect(self.rectDrawZone).topleft)

            #Voilà, ça c'est les coordonnées de la souris, locales au SubMenu
            posMouseInSubMenu = rectPosMouseInSubMenu.topleft

            #on peut maintenant transmettre le stimuli à tous les sous-MenuElem, un par un.
            for menuElem in self.listMenuElemInside:

                #crac, transmission. Et récupération des messages d'ihm
                param = (posMouseInSubMenu, mouseDown, mousePressed)
                ihmsgInfoNew = menuElem.takeStimuliMouse(*param)

                #le sous-MenuElem a demandé le focus interne. On lui donne.
                if IHMSG_ELEM_WANTFOCUS in ihmsgInfoNew:
                    self.focusOnElem(menuElem)

                #ajout des messages d'ihm du sous-MenuElem au gros tuple cumulant tous les
                #message d'ihm.
                ihmsgInfoReturn += ihmsgInfoNew

        #on ne doit pas propager les demandes de focus des sous-MenuElem au code appelant.
        #Car on a déjà géré en interne ces demandes de focus.
        #Donc faut virer tous les messages IHMSG_ELEM_WANTFOCUS du tuple de message d'ihm.
        #TRODO? : Ces messages d'ihm, ce serait pas mieux sous forme d'un dico de booléen avec
        #tous les messages dedans ? Ou un set. Mais pas un tuple de merde avec du bordel.
        if self.focusOn:
            #TRODO : regardez moi ça, c'est dégueulasse. Mayrdeu !!!
            ihmsgInfoReturn = tuple( [ihmsg for ihmsg in ihmsgInfoReturn
                                      if ihmsg != IHMSG_ELEM_WANTFOCUS] )

        #C'est bon, on a filtré les WANTFOCUS. On renvoi le reste des messages d'ihm.
        return ihmsgInfoReturn


    def draw(self, surfaceDest):
        """
        dessinage de l'élément de menu, sur une surface de destination.
        (voir description de la fonction dans la mother-classe MenuElem)
        """

        #on redessine dans la surface interne tous les MenuElem qui doivent être refreshed.
        for menuElem in self.listMenuElemInside:

            if menuElem.mustBeRefreshed:
                menuElem.draw(self.surfaceInside)

        #on blitte la surfazce interne vers la surface de destination. On utilise le rect
        #définissant la zone à blitter. Cette zone a été éventuellement décalée pour le scrolling,
        #et éventuellement tronquée pour rentrer dans le RectDrawZone du SubMenu.
        #
        #petit rappel : le 2eme param du blit : self.rectDrawZone, sert uniquement à
        #indiquer le point de blittage sur la surface de destination. La taille
        #de self.rectDrawZone n'est pas utilisée. C'est la taille du 1er param qui définit
        #quelle est taille de la zone à blitter.
        param = (self.surfaceInside, self.rectDrawZone, self.sourceRectToBlit)
        surfaceDest.blit(*param)


    def update(self):
        """
        (voir description de la mother-fonction, dans MenuElem)
        """

        ihmsgInfo = IHMSG_VOID

        #y'a qu'à juste exécuter le update sur chaque MenuElem interne
        for menuElem in self.listMenuElemInside:

            ihmsgInfo += menuElem.update()

            #le SubMenu doit être refreshed si au moins un
            #de ces sous-MenuElem doit être refreshed. (Oh la jolie phrase !)
            if menuElem.mustBeRefreshed:
                self.mustBeRefreshed = True

        return ihmsgInfo


    def takeStimuliLoseFocus(self):
        """
        fonction exécutée par le code extérieur, pour prévenir que le SubMenu perd le focus
        """

        MenuElem.takeStimuliLoseFocus(self)

        #si l'un des MenuElem interne a le focus interne, on le lui fait perdre
        if self.focusedElemInside is not None:
            self.focusedElemInside.takeStimuliLoseFocus()
            #et on Nonifie la référence vers le sous-MenuElem ayant le focus interne.
            #Haha : "Nonifier". Non, ça veut pas dire transformer en nonne.
            self.focusedElemInside = None


    def takeStimuliGetFocus(self):
        """
        fonction exécutée par le code extérieur, pour prévenir que le SubMenu prend le focus
        """
        #paf mother-class.
        MenuElem.takeStimuliGetFocus(self)

        #Il n'y a rien de plus à faire. Du coup, on peut se avoir un SubMenu focusé,
        #avec un focus interne sur rien du tout (self.focusedElemInside = None)
        #Eh ben ça plantera pas.
        #Si on fait Tab, le SubMenu va focuser sur le premier sous-MenuElem de sa liste.
        #Si on fait Entrée ou Espace, le SubMenu ne fera rien.

        #TRODO pour plus tard : réfléchir philosophiquement si faudrait pas focuser
        #sur le premier sous-MenuElem. Au lieu de focuser sur rien.

    def takeStimuliFocusCycling(self):
        """
        fonction exécutée par le code extérieur, quand il veut prévenir que y'a un cyclage
        de focus à faire.
        (voir description de la fonction dans MenuElem)
        """

        #on fait d'abord le cyclage de focus interne. (On n'autorise pas le tour
        #du compteur dans ce cyclage)
        param = (self.focusedElemInside, self.listMenuElemInside, False)
        focusedElemNew = cycleFocus(*param)

        if focusedElemNew is None:
            #l'élément focusé en interne est None. Ca veut dire qu'on est arrivé à la
            #fin de la liste des éléments à focuser. Dans ce cas, on prévient
            #le code appelant que le cyclage de focus principal peut se faire.
            #(Le SubMenu va paumer le focus, et on passera au MenuElem "pas-interne" suivant.
            return (IHMSG_CYCLE_FOCUS_OK, )
        else:
            #l'élément focusé en interne est un sous-MenuElem. On met à jour la référence
            #pointant vers l'élément focusé.
            self.focusedElemInside = focusedElemNew
            #On renvoie un tuple avec aucun message d'ihm dedans.
            #Ca veut dire qu'on accepte pas de lacher son focus pour faire le cyclage de focus
            #principal. Car on n'a pas fini le cyclage interne.
            return IHMSG_VOID


    def funcTransmitActionOnFocus(self):
        """
        fonction permettant de transmettre un ordre d'exécution de funcAction
        vers l'élément focusé en interne. (Quand le joueur a appuyé sur Entrée ou Espace)
        Cette fonction est branché sur le funcAction du SubMenu, c'est à dire qu'elle
        s'exécute lorsqu'on active le SubMenu.
        Il faut exécuter la funcAction du sous-MenuElem, si c'est possible.
        """

        #on regarde si y'a un élément focusé, et si cet élément possède une funcAction.
        if self.focusedElemInside is not None:
            if self.focusedElemInside.funcAction is not None:

                #on peut exécuter cette funcAction, et renvoyer les messages d'ibm
                #qui en a résulté. (Décombé ? laul !!!)
                return self.focusedElemInside.funcAction()

        #Sinon : y'a rien à faire. On glande, et on renvoie un tuple d'ihmsg vide.
        return IHMSG_VOID


    def changeLanguage(self):
        """
        changement du language. (voir descrip dans MenuElem)
        """

        #il faut propager le changement du language à tous les sous-éléments.
        for elemInside in self.listMenuElemInside:
            elemInside.changeLanguage()

        #et il faut recréer la surface interne contenant ces éléments de menu.
        #on redétermine la taille, on redessine tout, etc.
        #TRODO pour plus tard : MEGA BOURRIN AUSSI. Cette fonction trashe la surface
        #de 10 m de haut pour en recréer une autre juste après. Et paf la mémoire !
        #Je le corrige pas. Vaut mieux corriger le problème à sa source. (pas de surface de 10 m)
        self.renderElemInside()

