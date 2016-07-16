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

date de la derni�re relecture-commentage : 09/02/2011

le putain de menu manager, avec des �l�ments de menu dedans. Que il les g�re,
leur passe les stimulis, et tout et tout.

Les fl�ches haut/bas cyclent le focus sur une liste pr�definie d'�l�ments (pas forc�ment tous).
La touche Tab cycle le focus sur tous les �l�ments focusables, c'est oblig�.
Ainsi, quel que soit les trucs bizarres d'IHM que je ferais, le pauvre joueur qu'a pas de
souris pourra toujours utiliser toutes les options, gr�ce � Tab. Ce sera chiant, mais faisable.

mini-vocab :
cr�ation du menu : Cr�ation de l'instance du menu, � partir de la classe.
(En g�n�ral, c'est des classes h�rit�es de celle-ci.

activation du menu : le menu est plac� � l'�cran. Et le joueur peut utiliser ses options.

BIG BIG TRODO : il y a du code commun entre le SubMenu et le MenuManager,
factoriser tout �a quand on aura envie.
Pas l�. L�, j'en ai chi� pour faire ce tas de merde, j'en ai marre.
"""

import pygame
import pygame.locals
pygl = pygame.locals

from common import (IHMSG_QUIT, IHMSG_TOTALQUIT, IHMSG_REDRAW_MENU,
                    IHMSG_ELEM_WANTFOCUS, IHMSG_VOID)

from menucomn import IMG_BG_MAIN
from menuelem import MenuElem, cycleFocus
from yargler  import theSoundYargler, SND_MENU_CYCLE

#Liste des touches provoquant une activation du MenuElem sur lequel y'a le focus.
#(activation = ex�cution de la fonction funcAction du MenuElem)
#TRODO : pour plus tard : tout stocker + le K_TAB, et mapper �a avec un niveau interm�diaire.
LIST_KEY_ACTIVATING_MENU = (
 pygl.K_SPACE,    #la touche espace
 pygl.K_RETURN,   #la touche entr�e
 pygl.K_KP_ENTER, #la touche entr�e du pav� num�rique.
)
#(Je rappelle aux gens qu'on dit "pav� num�rique", et non pas "clavier num�rique". Merci de pas
#tout confondre. Le clavier, c'est tout le bazar avec les touches. Et y'a des pav�s dedans. L�.



class MenuManager():
    """
    voyez, c'est un peu le bordel, mais pas trop, voyez.
    """

    def __init__(self, surfaceDest, dicImg=None, idImgBgMenu=None):
        """
        constructeur. (thx captain obvious)

        entr�e :

            surfaceDest : pygame.Surface, sur laquelle on veut afficher le menu.
                          En g�n�ral, on choisit la surface principale pointant sur l'�cran.
                          Mais �a pourrait �tre autre chose.

            dicImg      : dictionnaire {identifiant d'image -> image}, contenant
                          toutes les images utilis�es pour les menu.
                          (Le menuManager ne piochera que dans quelques images du dico)
                          En fait, on passe tout le temps le m�me dico, celui
                          cr�� dans la classe menucomn.py.
                          J'aurais du faire un import plut�t qu'un passage en param,
                          mais je suis un peu con. D'ailleurs j'ai fait cette connerie
                          pour plein d'autres trucs.
                          Si le param vaut None, le menuManager ne pourra pas utiliser d'image.

            idImgBgMenu : identifiant d'une image contenue dans dicImg.
                          indique l'image � utiliser comme image de fond pour ce menu.
                          Si on laisse � None, on prend par d�faut l'image IMG_BG_MAIN
                          Si dicImg vaut None, ce menu n'affiche pas d'image de fond.

        Normalement, on doit overrider cette fonction d'init.
        (En appelant celle du MenuManager au d�but),
        Et dans l'override, on doit d�finir self.listMenuElem.
        C'est la liste contenant tous les menuElem du menuManager.
        L'ordre de cette liste est important, il d�termine l'ordre d'affichage,
        et l'ordre du cyclage de focus.
        On peut plus ou moins modifier self.listMenuElem en live. Mais peut �tre pas trop
        (j'ai pas vraiment test�, j'en ai pas eu besoin).
        Dans l'init overrid�, c'est cool de finir par un appel � la fonction initFocusCyclingInfo.
        Si on oublie, �a fonctionne quand m�me, mais on peut pas cycler avec Tab.
        """

        self.surfaceDest = surfaceDest
        self.dicImg = dicImg

        #r�cup�ration de l'image de background, si c'est possible.
        if dicImg is not None:
            if idImgBgMenu is not None:
                #y'en a une, et elle est clairement sp�cifi�e
                self.imgBgMenu = dicImg[idImgBgMenu]
            else:
                #y'en a une, mais c'est celle par d�faut
                self.imgBgMenu = dicImg[IMG_BG_MAIN]
        else:
            #y'en a pas.
            self.imgBgMenu = None

        #donc, la liste contenant tous les �l�ments de ce MenuManager. L� y'a rien
        #dedans, et faut mettre des trucs.
        self.listMenuElem = ()

        #R�f�rence vers le MenuElem actuarialement focus�. (haha, "actuariat", c'est un vrai mot)
        self.focusedElem = None

        #Cette variable doit �tre une liste de menuElem. Tous les menuElem mentionn�s dans
        #cette liste doivent �tre pr�sent dans self.listMenuElem. Lorsque le joueur
        #appuiera sur haut et bas, �a fera un cyclage de focus dans cette "liste restreinte".
        #exemple : le main Menu, avec les commandes principales jouer, credits, etc...
        #On peut laisser la variable � None. Dans ce cas, il ne se passe rien quand on fait
        #haut et bas.
        #Le cyclage avec Tab n'est pas � d�finir explicitement. Mais j'en aid�j� parl� plus haut.
        self.listMenuElemArrows = None

        #indique si il y a au moins un �l�ment, dans self.listMenuElem, qui acccepte le focus.
        #C'est important de le savoir. Quand on fait Tab, ou haut/bas,
        #et que aucun �l�ment n'accepte le focus, alors il ne faut rien faire.
        #(Sinon on boucle-infinite en cherchant un elem focusable).
        #pour l'instant, self.listMenuElem est vide, donc on fixe la variable � False.
        self.isOneElemAcceptFocus = False

        #pointeur sur le menuElem qui est en train de traiter l'event courant (souris, clavier...)
        #C'est utile de retenir cette info, pour les menuElem qui ont la
        #m�me funcAction. (Genre les config de touches dans menuzcon.MenuManagerConfig).
        self.menuElemTakingEvent = None


    def initFocusCyclingInfo(self, indexFocusedElem=None,
                             indexMenuElemArrowBounds=None):
        """
        initialisation des infos li�es au cyclage de focus sur les MenuElem.

        indexFocusedElem : None ou int. si int : index du MenuElem qui prend
                           le focus, lors de l'activation du menu, au d�part.
                           Si None : personne n'a le focus.

        indexMenuElemArrowBounds : None ou tuple de 2 int. Index min et max des MenuElems,
                                   d�finissant une sous-liste, sur laquelle on fait
                                   le cyclage du focus avec les fl�ches haut et bas.

        Cette fonction est � ex�cuter une fois qu'on a d�finit listMenuElem.
        (Genre, � la fin de l'init overrid� de la classe-fille)
        """

        #donnage du focus � l'�l�ment qui doit le recevoir.
        #Pas de contr�le de indexFocusedElem  < taille de la liste.
        #On est grand, on ne fait pas n'importe quoi avec son propre code.
        if indexFocusedElem is not None:
            self.focusOnElem(self.listMenuElem[indexFocusedElem])

        #d�finition (ou pas) de la liste restreinte indexMenuElemArrowBounds.
        if indexMenuElemArrowBounds is not None:
            (min, max) = indexMenuElemArrowBounds
            self.listMenuElemArrows = self.listMenuElem[min:max]

        #d�finition de self.isOneElemAcceptFocus. boolean indiquant si il y a au moins un
        #MenuElem dans la liste qui accepte le focus.
        #construction d'une liste de bool�en : tous les menuElem.acceptFocus
        listAccepFocus = [ menuElem.acceptFocus
                           for menuElem in self.listMenuElem
                         ]

        #il suffit d'avoir un seul True dans cette liste, et c'est bon.
        self.isOneElemAcceptFocus = any(listAccepFocus)


    def showBackground(self):
        """
        fonction affichant le fond, derri�re le menu. Fonction � overrider, ou pas.
        """
        #On balance l'image de fond � l'�cran, (en haut � gauche), si elle existe.
        if self.imgBgMenu is not None:
            self.surfaceDest.blit(self.imgBgMenu, (0, 0))


    def beforeDrawMenu(self):
        """
        fonction � overrider. On met ce qu'on veut dedans.
        Elle s'ex�cute juste avant le redessinage total de menu
        """
        pass


    def drawMenu(self):
        """
        fonction affichant le fond et tous les �l�ments du menu.

        Attention, quand on ex�cute drawMenu, �a se voit pas encore � l'�cran.
        Faut faire un coup de flip, (ou pygame.display.update si j'avais g�r� des dirtyRects,
        mais il se trouve que je les ai pas g�r�s dans les menus, car je voulais pas me prendre
        la gueule.)

        """

        #ex�cution de code overrid�, si y'en a.
        self.beforeDrawMenu()

        #dessin du fond.
        self.showBackground()

        #appel de la m�thode draw de tous les MenuElem. (Y'en a qui dessineront rien, mais osef)
        for menuElem in self.listMenuElem:
            menuElem.draw(self.surfaceDest)


    def focusOnElem(self, elemAskingFocus):
        """
        change le focus pour le mettre sur un autre MenuElem.

        entr�es :
            elemAskingFocus : MenuElem qui veut choper le focus.
                              Il vaut mieux que ce soit un �l�ment appartenant � self.listMenuElem
                              Sinon c'est cr�tin, et je sais pas ce que �a donne.
        """

        #si le focus �tait d�j� sur un autre �l�ment, on le lui enl�ve.
        if self.focusedElem is not None:
            self.focusedElem.takeStimuliLoseFocus()

        #modification de l'attribut pointant vers l'�l�ment focus�.
        self.focusedElem = elemAskingFocus
        #on donne le focus � l'�l�ment qui le veut.
        self.focusedElem.takeStimuliGetFocus()


    def startMenu(self):
        """
        fonction � overrider. On met ce qu'on veut dedans.
        Elle s'ex�cute au d�but de l'activation d'un menu
        """
        pass


    def periodicAction(self):
        """
        fonction � overrider. On met ce qu'on veut dedans.
        Elle s'ex�cute au d�but de chaque cycle, durant la gestion du menu

        plat-dessert : tuple avec des messages d'ihm (genre IHMSG_REDRAW_MENU, ou autre)
        """
        return IHMSG_VOID


    def handleMenu(self):
        """
        fonction principale pour activer le menu, puis le g�rer, l'afficher,
        choper les events �mis par le joueur, et effectuer les actions qui en d�combent.
        (Non, qui lui incombent). Ha ha
        """

        self.startMenu()

        #Le rafra�chissement et la prise en compte des events se fait 30 fois par seconde.
        #Ca suffit bien, pour des menus merdiques.
        #(Sinon, on risque de piquer toute la CPU, ou je sais pas quoi).
        #D�sol�, j'avais envie de faire mon savant en disant "la CPU". Ca fait classe. Hey hey !
        waitingFPS = 30
        clock = pygame.time.Clock()

        #on traite tous les �v�nements en attente. Ca vide le buffer du clavier.
        pygame.event.pump()

        #initialisation du tuple de messages d'ihm. Lors d'un cycle, ce tuple contiendra
        #le cumul de tous les messages d'ihm renvoy�s par les MenuElem lors de leurs diverses
        #actions. C'est un peu bourrin de tout cumuler comme �a, mais �a marche.
        #L�, pour l'instant, y'a rien dedans.
        ihmsgInfo = IHMSG_VOID

        #premier gros dessin global de tout le menu, pour l'activation.
        self.drawMenu()

        #gros flip global pour tout rafra�chir.
        pygame.display.flip()

        #liste qui stockera les codes des touches qui viennent tout juste "paf" d'�tre appuy�es.
        #(la liste augmente quand on chope des events de KEY_DOWN. Elle diminue un par un,
        #au fur et � mesure qu'on traite ces appuyages.
        listKeyDown = []
        #liste contenant la valeur unicode renvoy� par les events d'appuyages de touches.
        #certains appuyages de touche ne corresponde � aucun caract�re. Dans ce cas,
        #on r�cup�rera une cha�ne vide.
        #Du coup, il y a autant d'�l�ment dans cette liste que dans celle ci-dessus.
        #C'est un peu idiot, j'aurais du faire une seule liste contenant des tuples de 2 �l�ments.
        #TRODO pour plus tard : changer �a.
        listKeyDownChar = []

        #r�cup�ration d'un dictionnaire {identifiant de touche -> boolean}, indiquant
        #quelles touches sont actuellement appuy�es (pas "paf")
        self.dictKeyPressed = pygame.key.get_pressed()

        # ---------- GROSSE BOUCLE DE GESTION DU MENU ------------

        while IHMSG_QUIT not in ihmsgInfo:

            #super classe clock, qui g�re toute seule le "30 fois par seconde"
            clock.tick(waitingFPS)

            #r�initialisation du tuple des messages d'ihm � : rien du tout.
            ihmsgInfo = IHMSG_VOID

            #ex�cution de la fonction p�riodique. Avec tout et n'importe quoi dedans, ou pas.
            #Cette fonction a le droit de v�rifier les touches d�j� appuy�s, en consultant
            #le dico self.dictKeyPressed. Car je l'ai initialis� juste avant. Youpi !
            ihmsgInfo += self.periodicAction()

            #boolean indiquant si il s'est pass� des trucs avec la souris (mouvement, bouton, ...)
            isEventAboutMouse = False
            #boolean indiquant si le bouton de la souris vient tout juste "paf" d'�tre appuy�.
            mouseDown = False

            # --- Scrutationnage des events.  ---

            for event in pygame.event.get():

                if event.type == pygl.QUIT:
                    #event de fermage de fen�tre
                    #(mais pas Alt-F4, qui ne semble pas �tre pris en compte).
                    #on se barre de la fonction avec le message d'ihm TOTALQUIT.
                    #Ce message doit �tre remont� vers tous les menus et les MenuElem
                    #en cours d'ex�cution, jusqu'� quitter le programme proprement.
                    #Et on se barre tout de suite, tel le bourrin. Car si on a demand�
                    #� quitter, autant le faire le plus vite possible. Sans fioritures-tralala.
                    return (IHMSG_QUIT, IHMSG_TOTALQUIT)

                elif event.type == pygl.MOUSEBUTTONDOWN:
                    #le joueur vient de "paf" appuyer sur le bouton de la souris.
                    isEventAboutMouse = True
                    mouseDown = True

                elif event.type == pygl.MOUSEMOTION:
                    #le joueur a boug� la souris
                    isEventAboutMouse = True

                elif event.type == pygl.KEYDOWN:
                    #le joueur vient de "paf" appuyer sur une touche.
                    #on ajoute l'identifiant de la touche et sa valeur unicode,
                    #aux listes contenant les appuyages de touches.
                    #comme dit ailleurs, l'unicode g�re tout seul les majuscules, �, �, ...
                    listKeyDown.append(event.key)
                    listKeyDownChar.append(event.unicode)

            #r�actualisation du dictionnaire {identifiant de touche -> boolean}
            self.dictKeyPressed = pygame.key.get_pressed()

            #recup du boolean indiquant si le bouton droit de la souris est appuy� ou pas
            mousePressed = pygame.mouse.get_pressed()[0]

            if mousePressed:
                isEventAboutMouse = True

            # --- d�pilage des events d'appuyage de touche ---

            #En fait, on prend que le premier appuyage.
            #Les autres seront g�r�s dans les cycles suivants

            if len(listKeyDown) > 0:
                keyCodeDown = listKeyDown.pop(0)
                keyCharDown = listKeyDownChar.pop(0)
            else:
                #Ah ben y'a plus d'appuyage de touches.
                keyCodeDown = None
                keyCharDown = None

            # --- Transmission de l'event d'appuyage de touche aux MenuElems ---

            if keyCodeDown is not None:
                for menuElem in self.listMenuElem:

                    #R�actualisation du menuElem qui est en cours de traitement d'event.
                    #voir explication � propos de cette variable dans self.__init
                    self.menuElemTakingEvent = menuElem

                    #on transmet les events, et on r�cup�re les messages d'ihm qu'on ajoute
                    #au tuple qui cumule tout.
                    param = (self.dictKeyPressed, keyCodeDown, keyCharDown)
                    ihmsgInfo += menuElem.takeStimuliKeys(*param)

            # --- Transmission des events de la souris aux MenuElems ---

            if isEventAboutMouse:

                #r�cup�r�ation des coordonn�es (X, Y) du curseur de la souris.
                mousePos = pygame.mouse.get_pos()

                for menuElem in self.listMenuElem:

                    #R�actualisation du menuElem qui est en cours de traitement d'event.
                    self.menuElemTakingEvent = menuElem

                    #on transmet les event, et on stocke les messages d'ihm dans un
                    #tuple provisoire. On met pas directement tout dans le tuple principal,
                    #car on doit retenir ce que renvoie chaque MenuElem s�par�ment,
                    #(voir juste apr�s)
                    param = (mousePos, mouseDown, mousePressed)
                    ihmsgInfoNew = menuElem.takeStimuliMouse(*param)

                    #Si le MenuElem a renvoy� un message de demande de focus, on le lui file tout
                    #de suite. (d'o� le besoin de pas cumuler tout de suite, mm'voyez)
                    #J'ai pas ajout� ce traitement sp�cifique dans les events d'appuyage
                    #de touches. Car les appuyage de touche ne font jamais changer le focus.
                    #Mais �a pourrait. TRODO pour plus tard : l'ajouter.
                    if IHMSG_ELEM_WANTFOCUS in ihmsgInfoNew:
                        self.focusOnElem(menuElem)

                    #et maintenant on peut ajouter au tuple principal
                    ihmsgInfo += ihmsgInfoNew

            # --- Prise en compte des events de touche pour la gestion interne du menu ---

            if keyCodeDown in LIST_KEY_ACTIVATING_MENU:
                #le joueur a appuy� sur l'une des touches Entr�e ou sur Espace.
                #Si y'a le focus sur un �l�ment, et que cet �l�ment a une fonction d'action,
                #alors il faut l'ex�cuter.
                #Et on ajoute les messages d'ihm r�cup�r�s au tuple ihmsgInfo.
                if self.focusedElem is not None:
                    if self.focusedElem.funcAction is not None:
                        #petite r�actualisation hopla de l'elem en train de traiter l'event.
                        self.menuElemTakingEvent = self.focusedElem
                        ihmsgInfo += self.focusedElem.funcAction()

            if keyCodeDown == pygl.K_TAB and self.isOneElemAcceptFocus:

                #Le joueur a appuy� sur Tab. Et il y a au moins un MenuElem qui accepte le focus
                #on fait un cyclage du focus sur toute la liste de MenuElem du menu
                param = (self.focusedElem, self.listMenuElem, True)
                self.focusedElem = cycleFocus(*param)

                #son du cyclage de focus : pop !!
                theSoundYargler.playSound(SND_MENU_CYCLE)

            if keyCodeDown in (pygl.K_UP, pygl.K_DOWN):

                #Le joueur a appuy� sur la fl�che du haut ou du bas.
                #Si on a une "liste restreinte" de menuElem, dans laquelle on a
                #pr�vu de faire un cyclage de focus, alors il faut le faire (le cyclage).
                if self.listMenuElemArrows is not None:

                    #d�but de la liste de param � transmettre � la fonction de cyclage de focus.
                    #Le "True" � la fin sert � indiquer qu'on a le droit
                    #de faire le tour du compteur dans la liste.
                    param = [self.focusedElem, self.listMenuElemArrows, True]

                    #ajout du dernier param : direction dans laquelle on cycle le focus,
                    #selon la touche appuy�e.
                    if keyCodeDown == pygl.K_UP:
                        param.append(-1)
                    else:
                        param.append(+1)

                    #cyclage du focus. En r�cup�rant le nouvel elem focus�.
                    self.focusedElem = cycleFocus(*param)

                    #son du cyclage de focus : pop !!
                    theSoundYargler.playSound(SND_MENU_CYCLE)

            # --- quittage immediat (sans redessiner), si faut quitter tout le jeu ---

            if IHMSG_TOTALQUIT in ihmsgInfo:
                return (IHMSG_QUIT, IHMSG_TOTALQUIT)

            # --- rafraichissement/redessinage du menu � l'�cran ---

            #update de tous les �l�ments de focus. (C'est une fonction avec tout et nimp dedans.)
            for menuElem in self.listMenuElem:
                ihmsgInfo += menuElem.update()

            #les update, ou bien les autres trucs fait avant, ont peut-�tre demand�
            #un gros redessinage g�n�ral du menu.
            if IHMSG_REDRAW_MENU in ihmsgInfo:

                #on dessine / redessine enti�rement le menu (ainsi que son fond)
                self.drawMenu()

            else:

                #pas besoin de redessiner tout le menu, ni l'image de fond.
                #On ne redessine que les �l�ments qui demandent � �tre refreshed.
                #(par exemple, du texte focus� qui glow, ou une image qui glow aussi)
                for menuElem in self.listMenuElem:
                    if menuElem.mustBeRefreshed:
                        menuElem.draw(self.surfaceDest)

            #gros flip global pour rafra�chir le dessin/refresh qu'on vient de faire.
            pygame.display.flip()

        # ---------- FIN DE LA PUTAIN DE GROSSE BOUCLE DE GESTION DU MENU ------------

        #On renvoie le tuple cumul� de messagesd'ihm qui a fait quitter la grosse boucle du menu.
        #Y'en a besoin pour propager certains messages d'IHM, en particulier le TOTALQUIT.
        return ihmsgInfo


    def changeLanguage(self):
        """
        changement du language. (voir description dans MenuElem) (m�me si cette classe
        n'est pas h�rit�e de MenuElem. La description va bien quand m�me. Na!)
        """

        #il faut propager le changement du language � tous les �l�ments internes, et c'est tout.
        for menuElem in self.listMenuElem:
            menuElem.changeLanguage()
