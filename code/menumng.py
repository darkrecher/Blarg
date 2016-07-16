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

date de la dernière relecture-commentage : 09/02/2011

le putain de menu manager, avec des éléments de menu dedans. Que il les gère,
leur passe les stimulis, et tout et tout.

Les flèches haut/bas cyclent le focus sur une liste prédefinie d'éléments (pas forcément tous).
La touche Tab cycle le focus sur tous les éléments focusables, c'est obligé.
Ainsi, quel que soit les trucs bizarres d'IHM que je ferais, le pauvre joueur qu'a pas de
souris pourra toujours utiliser toutes les options, grâce à Tab. Ce sera chiant, mais faisable.

mini-vocab :
création du menu : Création de l'instance du menu, à partir de la classe.
(En général, c'est des classes héritées de celle-ci.

activation du menu : le menu est placé à l'écran. Et le joueur peut utiliser ses options.

BIG BIG TRODO : il y a du code commun entre le SubMenu et le MenuManager,
factoriser tout ça quand on aura envie.
Pas là. Là, j'en ai chié pour faire ce tas de merde, j'en ai marre.
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
#(activation = exécution de la fonction funcAction du MenuElem)
#TRODO : pour plus tard : tout stocker + le K_TAB, et mapper ça avec un niveau intermédiaire.
LIST_KEY_ACTIVATING_MENU = (
 pygl.K_SPACE,    #la touche espace
 pygl.K_RETURN,   #la touche entrée
 pygl.K_KP_ENTER, #la touche entrée du pavé numérique.
)
#(Je rappelle aux gens qu'on dit "pavé numérique", et non pas "clavier numérique". Merci de pas
#tout confondre. Le clavier, c'est tout le bazar avec les touches. Et y'a des pavés dedans. Là.



class MenuManager():
    """
    voyez, c'est un peu le bordel, mais pas trop, voyez.
    """

    def __init__(self, surfaceDest, dicImg=None, idImgBgMenu=None):
        """
        constructeur. (thx captain obvious)

        entrée :

            surfaceDest : pygame.Surface, sur laquelle on veut afficher le menu.
                          En général, on choisit la surface principale pointant sur l'écran.
                          Mais ça pourrait être autre chose.

            dicImg      : dictionnaire {identifiant d'image -> image}, contenant
                          toutes les images utilisées pour les menu.
                          (Le menuManager ne piochera que dans quelques images du dico)
                          En fait, on passe tout le temps le même dico, celui
                          créé dans la classe menucomn.py.
                          J'aurais du faire un import plutôt qu'un passage en param,
                          mais je suis un peu con. D'ailleurs j'ai fait cette connerie
                          pour plein d'autres trucs.
                          Si le param vaut None, le menuManager ne pourra pas utiliser d'image.

            idImgBgMenu : identifiant d'une image contenue dans dicImg.
                          indique l'image à utiliser comme image de fond pour ce menu.
                          Si on laisse à None, on prend par défaut l'image IMG_BG_MAIN
                          Si dicImg vaut None, ce menu n'affiche pas d'image de fond.

        Normalement, on doit overrider cette fonction d'init.
        (En appelant celle du MenuManager au début),
        Et dans l'override, on doit définir self.listMenuElem.
        C'est la liste contenant tous les menuElem du menuManager.
        L'ordre de cette liste est important, il détermine l'ordre d'affichage,
        et l'ordre du cyclage de focus.
        On peut plus ou moins modifier self.listMenuElem en live. Mais peut être pas trop
        (j'ai pas vraiment testé, j'en ai pas eu besoin).
        Dans l'init overridé, c'est cool de finir par un appel à la fonction initFocusCyclingInfo.
        Si on oublie, ça fonctionne quand même, mais on peut pas cycler avec Tab.
        """

        self.surfaceDest = surfaceDest
        self.dicImg = dicImg

        #récupération de l'image de background, si c'est possible.
        if dicImg is not None:
            if idImgBgMenu is not None:
                #y'en a une, et elle est clairement spécifiée
                self.imgBgMenu = dicImg[idImgBgMenu]
            else:
                #y'en a une, mais c'est celle par défaut
                self.imgBgMenu = dicImg[IMG_BG_MAIN]
        else:
            #y'en a pas.
            self.imgBgMenu = None

        #donc, la liste contenant tous les éléments de ce MenuManager. Là y'a rien
        #dedans, et faut mettre des trucs.
        self.listMenuElem = ()

        #Référence vers le MenuElem actuarialement focusé. (haha, "actuariat", c'est un vrai mot)
        self.focusedElem = None

        #Cette variable doit être une liste de menuElem. Tous les menuElem mentionnés dans
        #cette liste doivent être présent dans self.listMenuElem. Lorsque le joueur
        #appuiera sur haut et bas, ça fera un cyclage de focus dans cette "liste restreinte".
        #exemple : le main Menu, avec les commandes principales jouer, credits, etc...
        #On peut laisser la variable à None. Dans ce cas, il ne se passe rien quand on fait
        #haut et bas.
        #Le cyclage avec Tab n'est pas à définir explicitement. Mais j'en aidéjà parlé plus haut.
        self.listMenuElemArrows = None

        #indique si il y a au moins un élément, dans self.listMenuElem, qui acccepte le focus.
        #C'est important de le savoir. Quand on fait Tab, ou haut/bas,
        #et que aucun élément n'accepte le focus, alors il ne faut rien faire.
        #(Sinon on boucle-infinite en cherchant un elem focusable).
        #pour l'instant, self.listMenuElem est vide, donc on fixe la variable à False.
        self.isOneElemAcceptFocus = False

        #pointeur sur le menuElem qui est en train de traiter l'event courant (souris, clavier...)
        #C'est utile de retenir cette info, pour les menuElem qui ont la
        #même funcAction. (Genre les config de touches dans menuzcon.MenuManagerConfig).
        self.menuElemTakingEvent = None


    def initFocusCyclingInfo(self, indexFocusedElem=None,
                             indexMenuElemArrowBounds=None):
        """
        initialisation des infos liées au cyclage de focus sur les MenuElem.

        indexFocusedElem : None ou int. si int : index du MenuElem qui prend
                           le focus, lors de l'activation du menu, au départ.
                           Si None : personne n'a le focus.

        indexMenuElemArrowBounds : None ou tuple de 2 int. Index min et max des MenuElems,
                                   définissant une sous-liste, sur laquelle on fait
                                   le cyclage du focus avec les flèches haut et bas.

        Cette fonction est à exécuter une fois qu'on a définit listMenuElem.
        (Genre, à la fin de l'init overridé de la classe-fille)
        """

        #donnage du focus à l'élément qui doit le recevoir.
        #Pas de contrôle de indexFocusedElem  < taille de la liste.
        #On est grand, on ne fait pas n'importe quoi avec son propre code.
        if indexFocusedElem is not None:
            self.focusOnElem(self.listMenuElem[indexFocusedElem])

        #définition (ou pas) de la liste restreinte indexMenuElemArrowBounds.
        if indexMenuElemArrowBounds is not None:
            (min, max) = indexMenuElemArrowBounds
            self.listMenuElemArrows = self.listMenuElem[min:max]

        #définition de self.isOneElemAcceptFocus. boolean indiquant si il y a au moins un
        #MenuElem dans la liste qui accepte le focus.
        #construction d'une liste de booléen : tous les menuElem.acceptFocus
        listAccepFocus = [ menuElem.acceptFocus
                           for menuElem in self.listMenuElem
                         ]

        #il suffit d'avoir un seul True dans cette liste, et c'est bon.
        self.isOneElemAcceptFocus = any(listAccepFocus)


    def showBackground(self):
        """
        fonction affichant le fond, derrière le menu. Fonction à overrider, ou pas.
        """
        #On balance l'image de fond à l'écran, (en haut à gauche), si elle existe.
        if self.imgBgMenu is not None:
            self.surfaceDest.blit(self.imgBgMenu, (0, 0))


    def beforeDrawMenu(self):
        """
        fonction à overrider. On met ce qu'on veut dedans.
        Elle s'exécute juste avant le redessinage total de menu
        """
        pass


    def drawMenu(self):
        """
        fonction affichant le fond et tous les éléments du menu.

        Attention, quand on exécute drawMenu, ça se voit pas encore à l'écran.
        Faut faire un coup de flip, (ou pygame.display.update si j'avais géré des dirtyRects,
        mais il se trouve que je les ai pas gérés dans les menus, car je voulais pas me prendre
        la gueule.)

        """

        #exécution de code overridé, si y'en a.
        self.beforeDrawMenu()

        #dessin du fond.
        self.showBackground()

        #appel de la méthode draw de tous les MenuElem. (Y'en a qui dessineront rien, mais osef)
        for menuElem in self.listMenuElem:
            menuElem.draw(self.surfaceDest)


    def focusOnElem(self, elemAskingFocus):
        """
        change le focus pour le mettre sur un autre MenuElem.

        entrées :
            elemAskingFocus : MenuElem qui veut choper le focus.
                              Il vaut mieux que ce soit un élément appartenant à self.listMenuElem
                              Sinon c'est crétin, et je sais pas ce que ça donne.
        """

        #si le focus était déjà sur un autre élément, on le lui enlève.
        if self.focusedElem is not None:
            self.focusedElem.takeStimuliLoseFocus()

        #modification de l'attribut pointant vers l'élément focusé.
        self.focusedElem = elemAskingFocus
        #on donne le focus à l'élément qui le veut.
        self.focusedElem.takeStimuliGetFocus()


    def startMenu(self):
        """
        fonction à overrider. On met ce qu'on veut dedans.
        Elle s'exécute au début de l'activation d'un menu
        """
        pass


    def periodicAction(self):
        """
        fonction à overrider. On met ce qu'on veut dedans.
        Elle s'exécute au début de chaque cycle, durant la gestion du menu

        plat-dessert : tuple avec des messages d'ihm (genre IHMSG_REDRAW_MENU, ou autre)
        """
        return IHMSG_VOID


    def handleMenu(self):
        """
        fonction principale pour activer le menu, puis le gérer, l'afficher,
        choper les events émis par le joueur, et effectuer les actions qui en décombent.
        (Non, qui lui incombent). Ha ha
        """

        self.startMenu()

        #Le rafraîchissement et la prise en compte des events se fait 30 fois par seconde.
        #Ca suffit bien, pour des menus merdiques.
        #(Sinon, on risque de piquer toute la CPU, ou je sais pas quoi).
        #Désolé, j'avais envie de faire mon savant en disant "la CPU". Ca fait classe. Hey hey !
        waitingFPS = 30
        clock = pygame.time.Clock()

        #on traite tous les événements en attente. Ca vide le buffer du clavier.
        pygame.event.pump()

        #initialisation du tuple de messages d'ihm. Lors d'un cycle, ce tuple contiendra
        #le cumul de tous les messages d'ihm renvoyés par les MenuElem lors de leurs diverses
        #actions. C'est un peu bourrin de tout cumuler comme ça, mais ça marche.
        #Là, pour l'instant, y'a rien dedans.
        ihmsgInfo = IHMSG_VOID

        #premier gros dessin global de tout le menu, pour l'activation.
        self.drawMenu()

        #gros flip global pour tout rafraîchir.
        pygame.display.flip()

        #liste qui stockera les codes des touches qui viennent tout juste "paf" d'être appuyées.
        #(la liste augmente quand on chope des events de KEY_DOWN. Elle diminue un par un,
        #au fur et à mesure qu'on traite ces appuyages.
        listKeyDown = []
        #liste contenant la valeur unicode renvoyé par les events d'appuyages de touches.
        #certains appuyages de touche ne corresponde à aucun caractère. Dans ce cas,
        #on récupèrera une chaîne vide.
        #Du coup, il y a autant d'élément dans cette liste que dans celle ci-dessus.
        #C'est un peu idiot, j'aurais du faire une seule liste contenant des tuples de 2 éléments.
        #TRODO pour plus tard : changer ça.
        listKeyDownChar = []

        #récupération d'un dictionnaire {identifiant de touche -> boolean}, indiquant
        #quelles touches sont actuellement appuyées (pas "paf")
        self.dictKeyPressed = pygame.key.get_pressed()

        # ---------- GROSSE BOUCLE DE GESTION DU MENU ------------

        while IHMSG_QUIT not in ihmsgInfo:

            #super classe clock, qui gère toute seule le "30 fois par seconde"
            clock.tick(waitingFPS)

            #réinitialisation du tuple des messages d'ihm à : rien du tout.
            ihmsgInfo = IHMSG_VOID

            #exécution de la fonction périodique. Avec tout et n'importe quoi dedans, ou pas.
            #Cette fonction a le droit de vérifier les touches déjà appuyés, en consultant
            #le dico self.dictKeyPressed. Car je l'ai initialisé juste avant. Youpi !
            ihmsgInfo += self.periodicAction()

            #boolean indiquant si il s'est passé des trucs avec la souris (mouvement, bouton, ...)
            isEventAboutMouse = False
            #boolean indiquant si le bouton de la souris vient tout juste "paf" d'être appuyé.
            mouseDown = False

            # --- Scrutationnage des events.  ---

            for event in pygame.event.get():

                if event.type == pygl.QUIT:
                    #event de fermage de fenêtre
                    #(mais pas Alt-F4, qui ne semble pas être pris en compte).
                    #on se barre de la fonction avec le message d'ihm TOTALQUIT.
                    #Ce message doit être remonté vers tous les menus et les MenuElem
                    #en cours d'exécution, jusqu'à quitter le programme proprement.
                    #Et on se barre tout de suite, tel le bourrin. Car si on a demandé
                    #à quitter, autant le faire le plus vite possible. Sans fioritures-tralala.
                    return (IHMSG_QUIT, IHMSG_TOTALQUIT)

                elif event.type == pygl.MOUSEBUTTONDOWN:
                    #le joueur vient de "paf" appuyer sur le bouton de la souris.
                    isEventAboutMouse = True
                    mouseDown = True

                elif event.type == pygl.MOUSEMOTION:
                    #le joueur a bougé la souris
                    isEventAboutMouse = True

                elif event.type == pygl.KEYDOWN:
                    #le joueur vient de "paf" appuyer sur une touche.
                    #on ajoute l'identifiant de la touche et sa valeur unicode,
                    #aux listes contenant les appuyages de touches.
                    #comme dit ailleurs, l'unicode gère tout seul les majuscules, ô, Û, ...
                    listKeyDown.append(event.key)
                    listKeyDownChar.append(event.unicode)

            #réactualisation du dictionnaire {identifiant de touche -> boolean}
            self.dictKeyPressed = pygame.key.get_pressed()

            #recup du boolean indiquant si le bouton droit de la souris est appuyé ou pas
            mousePressed = pygame.mouse.get_pressed()[0]

            if mousePressed:
                isEventAboutMouse = True

            # --- dépilage des events d'appuyage de touche ---

            #En fait, on prend que le premier appuyage.
            #Les autres seront gérés dans les cycles suivants

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

                    #Réactualisation du menuElem qui est en cours de traitement d'event.
                    #voir explication à propos de cette variable dans self.__init
                    self.menuElemTakingEvent = menuElem

                    #on transmet les events, et on récupère les messages d'ihm qu'on ajoute
                    #au tuple qui cumule tout.
                    param = (self.dictKeyPressed, keyCodeDown, keyCharDown)
                    ihmsgInfo += menuElem.takeStimuliKeys(*param)

            # --- Transmission des events de la souris aux MenuElems ---

            if isEventAboutMouse:

                #récupéréation des coordonnées (X, Y) du curseur de la souris.
                mousePos = pygame.mouse.get_pos()

                for menuElem in self.listMenuElem:

                    #Réactualisation du menuElem qui est en cours de traitement d'event.
                    self.menuElemTakingEvent = menuElem

                    #on transmet les event, et on stocke les messages d'ihm dans un
                    #tuple provisoire. On met pas directement tout dans le tuple principal,
                    #car on doit retenir ce que renvoie chaque MenuElem séparément,
                    #(voir juste après)
                    param = (mousePos, mouseDown, mousePressed)
                    ihmsgInfoNew = menuElem.takeStimuliMouse(*param)

                    #Si le MenuElem a renvoyé un message de demande de focus, on le lui file tout
                    #de suite. (d'où le besoin de pas cumuler tout de suite, mm'voyez)
                    #J'ai pas ajouté ce traitement spécifique dans les events d'appuyage
                    #de touches. Car les appuyage de touche ne font jamais changer le focus.
                    #Mais ça pourrait. TRODO pour plus tard : l'ajouter.
                    if IHMSG_ELEM_WANTFOCUS in ihmsgInfoNew:
                        self.focusOnElem(menuElem)

                    #et maintenant on peut ajouter au tuple principal
                    ihmsgInfo += ihmsgInfoNew

            # --- Prise en compte des events de touche pour la gestion interne du menu ---

            if keyCodeDown in LIST_KEY_ACTIVATING_MENU:
                #le joueur a appuyé sur l'une des touches Entrée ou sur Espace.
                #Si y'a le focus sur un élément, et que cet élément a une fonction d'action,
                #alors il faut l'exécuter.
                #Et on ajoute les messages d'ihm récupérés au tuple ihmsgInfo.
                if self.focusedElem is not None:
                    if self.focusedElem.funcAction is not None:
                        #petite réactualisation hopla de l'elem en train de traiter l'event.
                        self.menuElemTakingEvent = self.focusedElem
                        ihmsgInfo += self.focusedElem.funcAction()

            if keyCodeDown == pygl.K_TAB and self.isOneElemAcceptFocus:

                #Le joueur a appuyé sur Tab. Et il y a au moins un MenuElem qui accepte le focus
                #on fait un cyclage du focus sur toute la liste de MenuElem du menu
                param = (self.focusedElem, self.listMenuElem, True)
                self.focusedElem = cycleFocus(*param)

                #son du cyclage de focus : pop !!
                theSoundYargler.playSound(SND_MENU_CYCLE)

            if keyCodeDown in (pygl.K_UP, pygl.K_DOWN):

                #Le joueur a appuyé sur la flèche du haut ou du bas.
                #Si on a une "liste restreinte" de menuElem, dans laquelle on a
                #prévu de faire un cyclage de focus, alors il faut le faire (le cyclage).
                if self.listMenuElemArrows is not None:

                    #début de la liste de param à transmettre à la fonction de cyclage de focus.
                    #Le "True" à la fin sert à indiquer qu'on a le droit
                    #de faire le tour du compteur dans la liste.
                    param = [self.focusedElem, self.listMenuElemArrows, True]

                    #ajout du dernier param : direction dans laquelle on cycle le focus,
                    #selon la touche appuyée.
                    if keyCodeDown == pygl.K_UP:
                        param.append(-1)
                    else:
                        param.append(+1)

                    #cyclage du focus. En récupérant le nouvel elem focusé.
                    self.focusedElem = cycleFocus(*param)

                    #son du cyclage de focus : pop !!
                    theSoundYargler.playSound(SND_MENU_CYCLE)

            # --- quittage immediat (sans redessiner), si faut quitter tout le jeu ---

            if IHMSG_TOTALQUIT in ihmsgInfo:
                return (IHMSG_QUIT, IHMSG_TOTALQUIT)

            # --- rafraichissement/redessinage du menu à l'écran ---

            #update de tous les éléments de focus. (C'est une fonction avec tout et nimp dedans.)
            for menuElem in self.listMenuElem:
                ihmsgInfo += menuElem.update()

            #les update, ou bien les autres trucs fait avant, ont peut-être demandé
            #un gros redessinage général du menu.
            if IHMSG_REDRAW_MENU in ihmsgInfo:

                #on dessine / redessine entièrement le menu (ainsi que son fond)
                self.drawMenu()

            else:

                #pas besoin de redessiner tout le menu, ni l'image de fond.
                #On ne redessine que les éléments qui demandent à être refreshed.
                #(par exemple, du texte focusé qui glow, ou une image qui glow aussi)
                for menuElem in self.listMenuElem:
                    if menuElem.mustBeRefreshed:
                        menuElem.draw(self.surfaceDest)

            #gros flip global pour rafraîchir le dessin/refresh qu'on vient de faire.
            pygame.display.flip()

        # ---------- FIN DE LA PUTAIN DE GROSSE BOUCLE DE GESTION DU MENU ------------

        #On renvoie le tuple cumulé de messagesd'ihm qui a fait quitter la grosse boucle du menu.
        #Y'en a besoin pour propager certains messages d'IHM, en particulier le TOTALQUIT.
        return ihmsgInfo


    def changeLanguage(self):
        """
        changement du language. (voir description dans MenuElem) (même si cette classe
        n'est pas héritée de MenuElem. La description va bien quand même. Na!)
        """

        #il faut propager le changement du language à tous les éléments internes, et c'est tout.
        for menuElem in self.listMenuElem:
            menuElem.changeLanguage()
