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

date de la derni�re relecture-commentage : 10/02/2011

�l�ment de menu qui contient, g�re, et affiche d'autres trucs (une liste de menuElem)
on peut faire scroller horizontalement et verticalement ces trucs

BIG BIG TRODO : il y a du code commun entre le SubMenu et le MenuManager,
factoriser tout �a quand on aura envie.
Pas l�. L�, j'en ai chi� pour faire ce tas de merde, j'en ai marre.

BIG BIG TRODO ENCORE PIRE : peut �tre qu'en fait c'est compl�tement de la merde cette classe.
Et que je peux obtenir les m�mes "aspects fonctionnels" avec des menuElem mobiles,
et limit�s � une certaine zone d'affichage � l'�cran.
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

        entr�e :
            rectDrawZone : Rect indiquant la zone dans laquelle on dessine les MenuElem
            contenus � l'int�rieur du subMenu. Ce rect est relatif � la surface de destination
            du subMenu. C'est � dire, en g�n�ral, le screen. Mais �a pourrait �tre autre chose.
            On le sp�cifie en param dans la m�thode draw.
            Si y'a des MenuElem qui d�passent enti�rement ou partiellement
            de cette zone, ils seront coup�s. (Tu couperas �a au montage, Potard)
            (C'�tait une phrase qui date de 15 ans, de fun radio ou skyrock. D�sol�).

            listMenuElemInside : liste de MenuElem � mettre dans ce subMenu.
            Les coordonn�es de ces MenuElem sont d�finies par rapport
            aux coordonn�es du SubMenu. Ce ne sont pas les coordonn�es "absolues".
            Ne pas mettre de coordonn�es n�gatives, �a va pas s'afficher.

            scrollLimit : tuple de deux entiers Y1 et Y2. Indique les limites hautes et basses
            du scrolling vertical. (Donc Y1 negatif ou nul, et Y2 positif ou nul).
            Enfin c'est pas oblig�, mais si on fait autrement, �a fait bizarre et cr�tin.
            Par d�faut : Y1 = Y2 = 0. C'est � dire qu'on peut pas scroller du tout.
        """

        #mother-class. ouech ouech.
        MenuElem.__init__(self)

        #ce MenuElem accepte le focus. youpi !
        self.acceptFocus = True

        #branchement de la fonction d'action vers une fonction interne.
        #Voir description de cette fonction, tout � la fin de ce fichier.
        #(Putain, je l'ai d�j� dit, mais j'adore vraiment le mot "interne". Il fait trop bien)
        self.funcAction = self.funcTransmitActionOnFocus

        #d�finition du rectangle d'affichage et du rectangle de sensibilit� � la souris.
        #(C'est le m�me. Ha !!!) Tiens en th�orie je devrais peut �tre ajouter une petite
        #marge, pour �tre sur de ne pas couper la marge d'un �ventuel SensitiveText
        #qui serait plac�e au bord du SubMenu. Ah. eh bien je m'en tamponne.
        self.rectDrawZone = rectDrawZone
        self.rectStimZone = rectDrawZone

        self.listMenuElemInside = listMenuElemInside

        #cr�ation de la surface interne contenant les dessins de tous les �l�ments internes.
        self.renderElemInside()

        #zone de d�part, de la surface interne, qui sera blitt�e vers la surface de destination.
        #On part du coin haut-gauche de la surface interne, et on tronque � la taille de la zone
        #d'affichage du SubMenu.  Quand on scrolle vertical, la coord Y de ce rect change.
        self.sourceRectToBlit = pygame.Rect((0, 0), self.rectDrawZone.size)

        #R�f�rence vers le MenuElem interne ayant le focus interne.
        #Quand le SubMenu prend le focus, il est cens� donner un "sous-focus" � l'un de ses
        #MenuElem interne.
        #(Concr�tement, �a sert � rien que le SubMenu en lui m�me ait le focus, il s'en tape)
        self.focusedElemInside = None

        self.scrollTop, self.scrollBottom = scrollLimit


    def renderElemInside(self):
        """
        on va foutre le dessin de tous les sous-MenuElem, dans une grosse
        surface "interne". Pour afficher le SubMenu, on se contentera de blitter cette surface.

        TRODO pour plus tard : MEGA BOURRIN. Si on a un subMenu de 10m de haut avec
        plein de blabla dedans (genre, les Credits), �a fait une surface de 10m de haut
        qui squatte toute la m�moire pour pas grand chose.
        Pour l'instant, je m'en tamponne la courge.

        Et donc �a, c'est la fonction pour pr�-dessiner la surface interne.
        Son but, c'est de d�finir self.surfaceInside
        """

        #Il faut d'abord d�terminer la taille de cette surface interne, de fa�on
        #� ce qu'elle puisse contenir tous les sous-MenuElem.
        #Il faut donc trouver :
        #la position du c�t� droit du sous-MenuElem le plus � droite, pour avoir la largeur,
        #et la position du bas du sous-MenuElem le plus en bas, pour avoir la hauteur.
        #(on consid�re que le haut-gauche c'est 0,0, m�me si y'a pas de sous-MenuElem � cet
        #endroit. Et c'est pour �a qu'il faut pas en mettre avec des coord n�gatives.
        #Car ils seront en partie ou totalement coup�s.)

        #d�termination de la largeur
        #on r�cup�re la liste des coordonn�es X des c�t�s droit des sous-MenuElem
        #(plus exactement, tous les MenuElem qui s'affichent, les autres osef)
        listXCoordRight = [ menuElem.rectDrawZone.right
                            for menuElem in self.listMenuElemInside
                            if menuElem.rectDrawZone is not None ]

        #r�cup�ration de la coord max, c'est � dire la plus � droite.
        XCoordMax = max(listXCoordRight)

        #d�temrination de la longueur.
        #on r�cup�re la liste des coordonn�es Y des bas de tous les sous-MenuElem qui s'affichent.
        listYCoordBottom =[ menuElem.rectDrawZone.bottom
                            for menuElem in self.listMenuElemInside
                            if menuElem.rectDrawZone is not None ]

        #r�cup�ration de la coord max, c'est � dire la plus en bas
        YCoordMax = max(listYCoordBottom)

        #cr�ation de la surface interne, avec la largeur et la hauteur trouv�e.
        self.surfaceInside = pygame.Surface( (XCoordMax, YCoordMax) )

        #couleur transparente = couleur noire. Ca veut dire que je pourrais jamais mettre
        #de noir quand je dessinerais mes MenuElem. Bon c'est zarb, mais j'y survivrais.
        #Sinon, je sais pas ce que c'est que ce RLEACCEL, mais �a doit �tre cool.
        self.surfaceInside.set_colorkey(COLOR_BLACK, pygl.RLEACCEL)

        #dessin des MenuElem sur la surface interne
        for menuElem in self.listMenuElemInside:
            menuElem.draw(self.surfaceInside)


    def scrollVertically(self, moveY):
        """
        fonction ex�cut�e par le code ext�rieur. Elle permet de d�caler les MenuElem,
        pour les afficher un peu plus haut ou un peu plus bas. Ca fait un scrolling.

        entr�es :
            moveY : int (positif ou negatif). Nombre de pixel de d�placement vertical
                    positif : vers le bas. negatif : vers le haut.
        """

        #On bouge le rectangle d�finissant la zone de la surface interne � bliter.
        self.sourceRectToBlit.move_ip(0, moveY)

        #clamping vertical de ce rectangle.

        #si on est all� trop haut, on se remet � la limite haute.
        if self.sourceRectToBlit.top < self.scrollTop:
            self.sourceRectToBlit.top = self.scrollTop

        #si on est all� trop bas, blablabla. Le clamping est toujours sur le Rect.top,
        #parce que scrollLimit d�finit
        #la zone dans laquelle a le droit de se trouver le point sup-gauche de la zone � blitter,
        #et non pas la zone dans laquelle a le droit de se trouver toute la zone � blitter.
        elif self.sourceRectToBlit.top > self.scrollBottom:
            self.sourceRectToBlit.top = self.scrollBottom

        #on fait pas de redessinage, ni de refresh.
        #C'est le code ext�rieur qui doit s'occuper de �a.


    def scrollSetPosition(self, position=0):
        """
        fonction ex�cut�e par le code ext�rieur. Elle permet de remettre � zero
        la position verticale des MenuElem.
        """

        #On r�initialise le rectangle d�finissant la zone de la surface interne � bliter.
        self.sourceRectToBlit.y = position

        #Pas de clamping. La position 0 est cens�e �tre comprise dans les limites autoris�es,
        #si �a l'est pas, c'est bizarre. Et on s'en occupe pas.

        #et donc, comme pour scrollVertically, pas de redessinage, ni de refresh.


    def focusOnElem(self, elemAskingFocus):
        """
        Change le focus interne, pour le mettre sur un autre sous-MenuElem.

        entr�es :
            elemAskingFocus : sous-MenuElem qui veut le focus.

        TRODO : putain de fonction pareil que le MenuManager. A factoriser
        """

        #si le focus �tait d�j� sur un autre �l�ment, on le lui enl�ve.
        if self.focusedElemInside is not None:
            self.focusedElemInside.takeStimuliLoseFocus()

        #modification de l'attribut pointant vers le sous-elem focus�.
        self.focusedElemInside = elemAskingFocus
        #on donne le focus au sous-elem qui n'en veut.
        self.focusedElemInside.takeStimuliGetFocus()


    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        prise en compte des mouvements et des clics de souris.
        (voir description dans la motheur-classe MenuElem)

        Il faut transmettre les stimulis de souris � tous les sous-menuElem
        """

        #tuple contenant les messages d'ihm, � renvoyer au code appelant.
        #il contiendra � peu pr�s les messages d'ihm renvoy� par les sous-MenuElem.
        #voir plus loin pour l'explication du "� peu pr�s".
        ihmsgInfoReturn = IHMSG_VOID

        if self.rectStimZone.collidepoint(mousePos):

            #le stimuli de la souris se trouve dans la zone du SubMenu.
            #Faut donc le prendre en compte.
            #
            #On doit transmettre ce stimuli de souris � tous les MenuElem interne.
            #Mais pour cela, il faut appliquer les d�calages. On doit convertir
            #les coordonn�es de la souris par rapport au code appelant, en
            #les coordonn�es de la souris en local, par rapport � ce SubMenu

            #on part des coordonn�es donn�es par le code appelant. (A priori, c'est les
            #coordonn�es de la souris � l'�cran. Sauf si on a un SubMenu dans un SubMenu.
            #Mais �a on s'en fout).
            rectPosMouseInSubMenu = pyRectTuple(mousePos)

            #on applique le d�calage li� au scrolling vertical du SubMenu
            rectPosMouseInSubMenu.move_ip(self.sourceRectToBlit.topleft)

            #et on applique le d�calage par rapport � la position du SubMenu dans
            #l'objet qui le contient. Faut retirer la coordonn�e du SubMenu, parce que euh...
            #Ouais l� je saurais pas expliquer, mais faites un dessin, vous comprendrez.
            rectPosMouseInSubMenu.move_ip(oppRect(self.rectDrawZone).topleft)

            #Voil�, �a c'est les coordonn�es de la souris, locales au SubMenu
            posMouseInSubMenu = rectPosMouseInSubMenu.topleft

            #on peut maintenant transmettre le stimuli � tous les sous-MenuElem, un par un.
            for menuElem in self.listMenuElemInside:

                #crac, transmission. Et r�cup�ration des messages d'ihm
                param = (posMouseInSubMenu, mouseDown, mousePressed)
                ihmsgInfoNew = menuElem.takeStimuliMouse(*param)

                #le sous-MenuElem a demand� le focus interne. On lui donne.
                if IHMSG_ELEM_WANTFOCUS in ihmsgInfoNew:
                    self.focusOnElem(menuElem)

                #ajout des messages d'ihm du sous-MenuElem au gros tuple cumulant tous les
                #message d'ihm.
                ihmsgInfoReturn += ihmsgInfoNew

        #on ne doit pas propager les demandes de focus des sous-MenuElem au code appelant.
        #Car on a d�j� g�r� en interne ces demandes de focus.
        #Donc faut virer tous les messages IHMSG_ELEM_WANTFOCUS du tuple de message d'ihm.
        #TRODO? : Ces messages d'ihm, ce serait pas mieux sous forme d'un dico de bool�en avec
        #tous les messages dedans ? Ou un set. Mais pas un tuple de merde avec du bordel.
        if self.focusOn:
            #TRODO : regardez moi �a, c'est d�gueulasse. Mayrdeu !!!
            ihmsgInfoReturn = tuple( [ihmsg for ihmsg in ihmsgInfoReturn
                                      if ihmsg != IHMSG_ELEM_WANTFOCUS] )

        #C'est bon, on a filtr� les WANTFOCUS. On renvoi le reste des messages d'ihm.
        return ihmsgInfoReturn


    def draw(self, surfaceDest):
        """
        dessinage de l'�l�ment de menu, sur une surface de destination.
        (voir description de la fonction dans la mother-classe MenuElem)
        """

        #on redessine dans la surface interne tous les MenuElem qui doivent �tre refreshed.
        for menuElem in self.listMenuElemInside:

            if menuElem.mustBeRefreshed:
                menuElem.draw(self.surfaceInside)

        #on blitte la surfazce interne vers la surface de destination. On utilise le rect
        #d�finissant la zone � blitter. Cette zone a �t� �ventuellement d�cal�e pour le scrolling,
        #et �ventuellement tronqu�e pour rentrer dans le RectDrawZone du SubMenu.
        #
        #petit rappel : le 2eme param du blit : self.rectDrawZone, sert uniquement �
        #indiquer le point de blittage sur la surface de destination. La taille
        #de self.rectDrawZone n'est pas utilis�e. C'est la taille du 1er param qui d�finit
        #quelle est taille de la zone � blitter.
        param = (self.surfaceInside, self.rectDrawZone, self.sourceRectToBlit)
        surfaceDest.blit(*param)


    def update(self):
        """
        (voir description de la mother-fonction, dans MenuElem)
        """

        ihmsgInfo = IHMSG_VOID

        #y'a qu'� juste ex�cuter le update sur chaque MenuElem interne
        for menuElem in self.listMenuElemInside:

            ihmsgInfo += menuElem.update()

            #le SubMenu doit �tre refreshed si au moins un
            #de ces sous-MenuElem doit �tre refreshed. (Oh la jolie phrase !)
            if menuElem.mustBeRefreshed:
                self.mustBeRefreshed = True

        return ihmsgInfo


    def takeStimuliLoseFocus(self):
        """
        fonction ex�cut�e par le code ext�rieur, pour pr�venir que le SubMenu perd le focus
        """

        MenuElem.takeStimuliLoseFocus(self)

        #si l'un des MenuElem interne a le focus interne, on le lui fait perdre
        if self.focusedElemInside is not None:
            self.focusedElemInside.takeStimuliLoseFocus()
            #et on Nonifie la r�f�rence vers le sous-MenuElem ayant le focus interne.
            #Haha : "Nonifier". Non, �a veut pas dire transformer en nonne.
            self.focusedElemInside = None


    def takeStimuliGetFocus(self):
        """
        fonction ex�cut�e par le code ext�rieur, pour pr�venir que le SubMenu prend le focus
        """
        #paf mother-class.
        MenuElem.takeStimuliGetFocus(self)

        #Il n'y a rien de plus � faire. Du coup, on peut se avoir un SubMenu focus�,
        #avec un focus interne sur rien du tout (self.focusedElemInside = None)
        #Eh ben �a plantera pas.
        #Si on fait Tab, le SubMenu va focuser sur le premier sous-MenuElem de sa liste.
        #Si on fait Entr�e ou Espace, le SubMenu ne fera rien.

        #TRODO pour plus tard : r�fl�chir philosophiquement si faudrait pas focuser
        #sur le premier sous-MenuElem. Au lieu de focuser sur rien.

    def takeStimuliFocusCycling(self):
        """
        fonction ex�cut�e par le code ext�rieur, quand il veut pr�venir que y'a un cyclage
        de focus � faire.
        (voir description de la fonction dans MenuElem)
        """

        #on fait d'abord le cyclage de focus interne. (On n'autorise pas le tour
        #du compteur dans ce cyclage)
        param = (self.focusedElemInside, self.listMenuElemInside, False)
        focusedElemNew = cycleFocus(*param)

        if focusedElemNew is None:
            #l'�l�ment focus� en interne est None. Ca veut dire qu'on est arriv� � la
            #fin de la liste des �l�ments � focuser. Dans ce cas, on pr�vient
            #le code appelant que le cyclage de focus principal peut se faire.
            #(Le SubMenu va paumer le focus, et on passera au MenuElem "pas-interne" suivant.
            return (IHMSG_CYCLE_FOCUS_OK, )
        else:
            #l'�l�ment focus� en interne est un sous-MenuElem. On met � jour la r�f�rence
            #pointant vers l'�l�ment focus�.
            self.focusedElemInside = focusedElemNew
            #On renvoie un tuple avec aucun message d'ihm dedans.
            #Ca veut dire qu'on accepte pas de lacher son focus pour faire le cyclage de focus
            #principal. Car on n'a pas fini le cyclage interne.
            return IHMSG_VOID


    def funcTransmitActionOnFocus(self):
        """
        fonction permettant de transmettre un ordre d'ex�cution de funcAction
        vers l'�l�ment focus� en interne. (Quand le joueur a appuy� sur Entr�e ou Espace)
        Cette fonction est branch� sur le funcAction du SubMenu, c'est � dire qu'elle
        s'ex�cute lorsqu'on active le SubMenu.
        Il faut ex�cuter la funcAction du sous-MenuElem, si c'est possible.
        """

        #on regarde si y'a un �l�ment focus�, et si cet �l�ment poss�de une funcAction.
        if self.focusedElemInside is not None:
            if self.focusedElemInside.funcAction is not None:

                #on peut ex�cuter cette funcAction, et renvoyer les messages d'ibm
                #qui en a r�sult�. (D�comb� ? laul !!!)
                return self.focusedElemInside.funcAction()

        #Sinon : y'a rien � faire. On glande, et on renvoie un tuple d'ihmsg vide.
        return IHMSG_VOID


    def changeLanguage(self):
        """
        changement du language. (voir descrip dans MenuElem)
        """

        #il faut propager le changement du language � tous les sous-�l�ments.
        for elemInside in self.listMenuElemInside:
            elemInside.changeLanguage()

        #et il faut recr�er la surface interne contenant ces �l�ments de menu.
        #on red�termine la taille, on redessine tout, etc.
        #TRODO pour plus tard : MEGA BOURRIN AUSSI. Cette fonction trashe la surface
        #de 10 m de haut pour en recr�er une autre juste apr�s. Et paf la m�moire !
        #Je le corrige pas. Vaut mieux corriger le probl�me � sa source. (pas de surface de 10 m)
        self.renderElemInside()

