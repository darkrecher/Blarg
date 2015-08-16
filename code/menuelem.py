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

date de la dernière relecture-commentage : 04/02/2011

Element de menu qui s'affiche éventuellement quelque part, qui reçoit des stimuli
de click de souris et d'appuyage de touche, et qui fait eventuellement des trucs en fonction.

Mais là c'est la classe générique, alors y'a pas grand chose dedans.

Vocabulaire et gestion d'interface : (bizarroïde, mais na!).

GetFocus, LoseFocus : l'élément de menu est sélectionné/déslectionné, via les touches
du clavier (flèche haut/bas, tab, ...) ou la souris. Les deux sont gérés,
mais c'est le dernier qui a parlé qui a raison.

*) Les éléments peuvent éventuellement avoir un sensitiveRect. C'est une zone dans l'écran
à laquelle l'élément doit réagir.
Les éléments peuvent éventuellement avoir un drawRect. C'est une zone dans l'écran
sur laquelle l'élément se dessine.

*) On peut avoir un drawRect et ne pas avoir de sensitiveRect.
Exemple : les images et les textes statiques. (MenuText, MenuImage)

*) En général, quand on a un sensitiveRect, y'a aussi un drawRect, et les deux Rects sont
à peu près confondus. Mais théoriquement rien ne l'oblige.

*) Si j'appuie sur une touche de cyclage d'élément (tab, up, down),
je passe à l'élément de menu suivant.
(La sélection précédente avait été faite par la souris ou par l'appui d'une touche).
La touche tab fait cycler parmi tous les éléments focusables. ils sont ordonnés dans une liste.

*) TRODO pour plus tard : shift+tab doit faire cycler parmi tous les éléments focusables,
mais dans l'autre sens.

*) On peut définir une sous-liste d'éléments focusable. (Par exemple, les
options du menu principal). Lorsqu'on fera up ou down, on naviguera dans cette sous-liste,
dans un sens ou dans l'autre.
Si on ne définit pas de sous-liste, up et down ne font rien.

*) Si il y a une sous-liste d'élément focusable, que l'élément actuellement focusé
n'est pas dans cette liste, et que j'appuie sur up ou down, alors on focus
sur le premier élément de la sous-liste.

*) Si j'amène le curseur de souris sur le sensitiveRect d'un élément, il est focusé.
Pas besoin de cliquer.

*) Si je focus sur un élément avec la souris, et que j'appuie sur Tab, ça cycle.
Donc l'élément focusé n'est plus celui pointé par la souris. Tant que je ne bouge pas
la souris, ça reste comme ça.

*) Dès que je bouge ma souris, même un tout petit peu, je resélectionne l'élément
sur lequel se trouve la souris.
Si je bouge ma souris sur rien, je ne change pas le focus courant.

*) Si j'appuie sur l'une des touche Entrée ou sur Espace. J'active l'élément sélectionné.
(Quel que soit la façon dont il a été sélectionné, on s'en fout.)
Si y'a aucun élément sélectionné, ça ne fait rien.

*) Si la souris ne se trouve pas sur l'élément focusé, et que je clique,
alors je focus immédiatement sur l'élément pointé (même si j'ai cliqué sans bouger)
et j'active la fonction liée à cet élément (funcAction).

*) Si je clique avec ma souris sur rien, il ne se passe rien. L'élément focusé reste
le même.

*) Certains éléments n'ont pas de sensitiveRect. On ne peut jamais les sélectionner
avec la souris. (Je ne fais ça que pour les éléments non-interactifs. Sinon c'est crétin)

*) Certains éléments n'acceptent pas du tout le focus. Quand on passe la souris dessus, il
ne se passe rien, et quand on fait Tab, le cyclage de focus saute cet élément.

*) En général, on a la relation réciproque :
élément n'ayant pas de sensitiveRect <=> éléments n'acceptant pas du tout le focus.
(Mais théoriquement, rien ne l'interdit).

*) Il y a aussi des éléments sans focus, sans sensitiveRect, et qui ne s'affichent même pas.
Mais ils peuvent exécuter la fonction qui leur est liée, quand on appuie sur une touche.
C'est juste un bind sur une touche en fait. Mais je l'ai foutu sous forme d'élément,
et pis c'est tout.

*) Pour communiquer tout ces trucs, on utilise les IHMSG (IHM Message).
Voir la librairie common. Ils sont tous dedans.

"""
import pygame
import pygame.locals
pygl = pygame.locals

from common import moveIndexInBounds, IHMSG_CYCLE_FOCUS_OK, IHMSG_VOID


def cycleFocus(focusedElem, listMenuElemToCycle, loopAuthorized, delta=+1):
    """
    Fonction permettant de déplacer le focus d'un élément vers le suivant.
    Cette fonction se trouve dans ce fichier de code, car je savais pas où la foutre ailleurs.

    entrées :
        focusedElem : référence vers le menuElem ayant actuellement le focus
                      On peut mettre ce param à None. Dans ce cas, pas de cyclage,
                      et on focusera sur le premier élément de listMenuElemToCycle.
                      même si, euh... je suis pas sur d'avoir complètement testé

        listMenuElemToCycle : liste de menuElem dans laquelle on fait cycler le focus

        loopAuthorized : boolean. Indique si le cyclage de focus est autorisé à
                         faire des tours du compteurs.
                         Si il ne l'est pas et qu'on sort de la liste, alors
                         on déplacera pas le focus, et la fonction renverra None.

        delta : int (positif ou negatif). Indique de combien d'élément on veut se
                déplacer dans la liste. En général, on met juste +1 ou -1, pour
                indiquer dans quel sens on veut aller. Mais on pourrait mettre autre chose
                si on veut faire des trucs bizarres.
                (Moi j'en fais pas, je fais jamais de trucs bizarres moi).

    plat-dessert :

        Soit une référence vers le menuElem qui a pris le focus (donc le nouveau focusedElem)
        Soit une référence vers le même menuElem parce que ça a pas changé,
        Soit None, si on n'a pas eu le droit de faire de tour du compteur alors qu'on devait.

        La fonction s'occupe elle-même de transférer le focus, en appelant les
        méthodes LoseFocus et GetFocus des menuElem correspondants.

    Y'a des fois, on a besoin de faire un sous-cyclage de focus. Par exemple,
    l'élément MenuSubMenu contient des éléments de Menu embarqué dans lui-même.

    C'est pourquoi, avant de faire un cyclage principal, on prévient l'élément
    actuellement focusé. Si l'elem focusé est simple, il répond qu'il accepte
    le cyclage, et on fait un cyclage principal.
    Si l'elem focusé est plus complexe, il se fait son sous-cyclage en interne. Et
    ensuite, il peut répondre deux choses différente :
     - son sous-cyclage n'est pas fini, dans ce cas, il n'accepte pas le cyclage principal.
     - son sous-cyclage est fini (on était arrivé au dernier sous-élément de menu),
    dans ce cas, il accepte le cyclage principal

    quand on cycle, on saute les éléments de la liste qui n'acceptent pas de prendre le focus.

    Si aucun élément de la liste n'accepte de prendre le focus, la fonction va planter.
    Alors faut pas le faire, d'accord ?

    Le focusedElem passé en paramètre peut être None, ou peut ne pas être dans listMenuElemToCycle,
    dans ce cas, on démarrera à partir du premier élément de la liste.

    Si on renvoie None, parce qu'on peut pas faire le tour du compteur, on ne fait pas perdre
    le focus à l'élément focusé.
    TRODO : peut être qu'on devrait non ? faut que je regarde ça.
    """

    if focusedElem is not None:

        #on informe l'élément focusé qu'on veut faire du cyclage de focus.
        #si c'est un élément normal, il accepte de lacher le focus, et on va pouvoir cycler,
        #si c'est un subMenu, il va faire un cyclage en interne, et éventuellement lacher
        #le focus si son cyclage est arrivé sur le dernier elem.
        ihmsgInfo = focusedElem.takeStimuliFocusCycling()
        acceptQuitFocus = IHMSG_CYCLE_FOCUS_OK in ihmsgInfo

    else:

        #Pas d'éléments focusé. Donc pas besoin de demander à qui que ce soit si il accepte
        #de lacher le focus.
        acceptQuitFocus = True

    if not acceptQuitFocus:
        #l'élément focusé ne veut pas lacher le focus. On ne fait rien, on renvoie l'élém focusé.
        return focusedElem

    #liste des paramètres à passer à la fonction qui fait avancer un index entre deux bornes,
    #y'a pas le premier param, mais il change tout le temps, alors on le passera en live.
    param = (delta, 0, len(listMenuElemToCycle), loopAuthorized)

    # --- détermination de l'index du premier menuElem qui pourrait (avoir le focus, ou pas) ---

    if focusedElem in listMenuElemToCycle:

        #l'élément focusé est dans la liste. On commence par choper son index.

        #focusedElemIndex = listMenuElemToCycle.index(focusedElem)
        #l'instruction index n'existe pas dans le python 2.5.4. Allez zou, à la mimine.
        focusedElemIndex = -1
        menuElemCurrent = None

        #petite boucle un peu cheap, pour trouver l'index de focusedElem dans listMenuElemToCycle
        #la boucle va forcément fonctionner, puisqu'on a vérifié avant
        #que focusedElem est in listMenuElemToCycle
        while menuElemCurrent != focusedElem:
            focusedElemIndex += 1
            menuElemCurrent = listMenuElemToCycle[focusedElemIndex]

        #on fait avancer une première fois l'index, c'est le cyclage effectif.
        #Mais que sur les index.
        newFocusedElemIndex = moveIndexInBounds(focusedElemIndex, *param)

        #Tour du compteur non autorisé. On se barre comme un voleur en renvoyant None.
        if newFocusedElemIndex is None:
            return None

    else:

        #l'élément focusé n'est paz dans la liste. On prend arbitrairement le premier.
        newFocusedElemIndex = 0

    # --- détermination de l'index du menuElem qui peut vraiment avoir le focus ---

    #on avance dans la liste jusqu'à trouver un menuElem qui accepte le focus.
    #Ca peut éventuellement être l'élément actuel (car on vient de faire un
    #cyclage juste ci-dessus, enfin ou pas si on a chopé le premier, bref...)
    #Mais il faut le vérifier que ça "peut éventuellement être l'élément actuel"
    while not listMenuElemToCycle[newFocusedElemIndex].acceptFocus:

        #et un cyclage de plus.
        newFocusedElemIndex = moveIndexInBounds(newFocusedElemIndex, *param)

        #fail tour du compteur non autorisé. On se barre comme un voleur en renvoyant None.
        if newFocusedElemIndex is None:
            return None

        #fait chier parce que le bout de code ci-dessus, il est en doublon
        #avec le bout de code ci-ci-dessus. J'ai essayé de factoriser tant que je peux avec la
        #fonction moveIndexInBounds, mais ça fait pas tout. C'est à cause de ces putain de while
        #qu'on peut pas écrire à l'envers. Genre le repeat ... until du pascal. Pourquoi
        #y'a pas ce truc en python ? Ce serait putain de cool.

    # --- Ah y est ! on a chopé l'élément qui veut bien du focus ! Donc : transfert du focus ---

    #on fait lacher le focus à l'élément actuel qui l'a
    if focusedElem is not None:
        focusedElem.takeStimuliLoseFocus()

    #récupération de l'élément à qui donner le focus, à partir de l'index.
    focusedElem = listMenuElemToCycle[newFocusedElemIndex]

    #don du focus à cet élément. Oui je te dooo-ooonneeuuu !
    focusedElem.takeStimuliGetFocus()

    return focusedElem



class MenuElem():
    """
    menuElem super générique qu'on va décliner en plein de trucs.
    """

    def __init__(self):
        """
        constructeur. (thx captain obvious)
        """

        #indique dans quelle zone de son conteneur (menu ou submenu) est dessiné ce menuElem.
        #on peut mettre un Rect, ou None si ce menuElem ne se dessine pas.
        self.rectDrawZone = None

        #pour les menuElem qui se dessinent, indique si il faut redessiner à chaque cycle ou pas.
        #on peut bien evidemment changer cet attribut en live. Crac youpi.
        #attention, entre deux refresh, on ne réaffiche pas le background du menu. Donc
        #si on veut faire un menuelem animé, faut tout le temps tripoter les mêmes pixels,
        #ou alors faut demander un redraw global avec IHMSG_REDRAW_MENU.
        #Y'a pas de juste milieu. TRODO : pour plus tard, essayer de prévoir un juste milieu.
        self.mustBeRefreshed = False

        #référence vers la fonction à exécuter quand cet élément de menu est activé.
        #C'est à dire quand on clique dessus, où quand le focus est dessus et
        #qu'on appuie sur entrée ou espace, ou dans d'autres cas funny qu'on code soi-même
        #dans les classes héritées
        self.funcAction = None

        #indique si le menuElem accepte le focus ou pas.
        self.acceptFocus = False

        #indique si le menuElem a le focus sur lui, ou pas. On n'est pas censé avoir plusieurs
        #menuElem en même temps ayant le focus. Mais y'a rien de vraiment fait pour contrôler ça.
        #Et en plus c'est pas tout à fait exact car on peut avoir un subMenu qui a le focus,
        #et l'un de ses sous-elem qui a un sous-focus. Bref : osef.
        self.focusOn = False


    def draw(self, surfaceDest):
        """
        dessine le menuElem.

        entrées:
            surfaceDest :
                surface sur laquelle on doit dessiner le menuElem. Ca peut être
                le screen principal, la surface d'un submenu, ou n'importe quoi d'autre.
                On dessine tout comme on veut. Mais faut savoir que si on dessine
                dans un submenu, et qu'on met des pixels en noir,
                alors ces pixels seront transparents lors de l'affichage
                du subMenu dans le menu principal.
                TRODO : C'est peut être crétin. Pour ce jeu, ça me pose pas
                de problème. Mais faudra pas oublier ça par la suite.
        """
        pass


    def takeStimuliFocusCycling(self):
        """
        fonction exécutée par le code extérieur, pour prévenir que y'a un cyclage
        de focus à faire, alors que ce menuElem a présentement le focus.

        sorties :
            un tuple ihmsgInfo.

        Y'a deux cas possibles :
         - le menuElem est "simple". Dans ce cas, il doit accepter de lacher son focus
           pour que le cyclage se fasse. Il faut donc mettre dans le ihmsgInfo renvoyé le
           message IHMSG_CYCLE_FOCUS_OK
         - le menuElem est "complexe" (il possède des sous-elements). Dans ce cas, on
           fait un sous-cyclage en interne, et si on arrive sur le dernier élément,
           on acccepte de lacher le focus.
        """
        return (IHMSG_CYCLE_FOCUS_OK, )


    def takeStimuliGetFocus(self):
        """
        fonction exécutée par le code extérieur, pour prévenir que ce menuElem prend le focus
        """
        self.focusOn = True


    def takeStimuliLoseFocus(self):
        """
        fonction exécutée par le code extérieur, pour prévenir que ce menuElem perd le focus
        """
        self.focusOn = False


    def update(self):
        """
        réactualise les trucs qu'on veut, à chaque cycle, quand ce menuElem est utilisé
        dans un menu.

        plat-dessert : soit IHMSG_VOID,
                       soit un tuple de message d'ihm, avec IHMSG_REDRAW_MENU dedans,
                       pour indiquer qu'on veut tout redrawer.

        On peut faire différent truc dans cette fonction. (Sachant qu'elle est appelée à
        chaque cycle :

         - Rien. Mettre self.mustBeRefreshed à False, et renvoyer IHMSG_VOID
           Cet élément du menu ne sera pas redessiné.

         - Des petits trucs. mettre self.mustBeRefreshed à True, et renvoyer IHMSG_VOID.
           Cet élément de menu sera redessiné. Mais le menu dans l'ensemble, ainsi que
           l'image de fond, ne le sera pas. Si on fait un truc comme ça, il faut
           donc faire attention que la fonction draw du menuElem tripote toujours
           les mêmes pixels. Sinon ça va laisser des traces.

         - Des gros trucs. mettre self.mustBeRefreshed à <osef>, et renvoyer un
           IHMSG_REDRAW_MENU. Dans ce cas, tout le menu (img de fond + tous les elems de
           menus) seront redessinés. Et là y'a plus de question à se poser. Mais c'est
           un peu bourrin. A ne faire que quand c'est nécessaire.
        """
        return IHMSG_VOID


    def takeStimuliKeys(self, dictKeyPressed, keyCodeDown, keyCharDown):
        """
        prise en compte d'une touche appuyée par le joueur.
        Le menuElem peut décider d'en avoir rien à foutre, ou pas.
        En général, le menuElem ne réagit au plus qu'à une seule touche. C'est à
        lui de la retrouver dans le bordel des paramètres en entrée.
        Mais y'a aussi des menuElem qui réagissent à n'importe quelle touche, tralala.

        entrées :
            dictKeyPressed : dictionnaire (identifiant de touche) -> booléen.
                             indique quelles touches sont appuyées (elles sont peut-être
                             appuyées depuis vachement longtemps, ou pas, on sait pas)

            keyCodeDown : identifiant de la touche qui vient d'être appuyée.
                          là tout de suite.

            keyCharDown : caractère unicode correspondant à la touche qui vient d'être
                          appuyé. Ca peut être un caractère vide si c'est une touche
                          à la con, genre F1, shift, ...
                          A priori, ça gère automatiquement tous les trucs bizarres :
                          accents, majuscules, azerty/qwerty, "ô", "ö", ...

        plat-dessert :
            un tuple ihmsgInfo avec les messages qu'on veut dedans.
            En particulier IHMSG_REDRAW_MENU si le stimuli s'est modifié des trucs
            et veut se redessiner.

        TRODO pour plus tard : cette fonction de prise en compte des stimulis n'est pas appelée
        si on relache une touche. Alors que les menuElem auraient peut être besoin
        d'être au courant de cette info. Pour l'instant osef.
        """
        return IHMSG_VOID


    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        prise en compte des mouvements et des clics de souris.
        Cette fonction est exécutée par le code extérieur, même quand le joueur
        bouge la souris sans cliquer. Ca permet de faire des trucs cools genre mouseHover tout ça.
        Le menuElem peut décider d'en avoir rien à foutre, ou pas.

        entrées:
            mousePos : tuple(X,Y). Coordonnées du curseur de souris, dans ce menu/submenu
                       Si ce menuElem est dans un subMenu, mousePos contient
                       les coordonnées locales à ce subMenu (c'est plus pratique).
                       Si le menuElem est dans un menu général, c'est les coordonnées
                       à l'écran, tout simplement.
            mouseDown : booléen. Indique si le bouton droit de la souris est appuyée
                        (on sait pas depuis combien de temps)
            mousePressed : booléen. Indique si le bouton droit de la souris vient
                           d'être appuyé, là maintenant.

        Ca gère que le bouton droit de la souris parce que je m'ai pas besoin des autres.
        TRODO pour plus tard : rajouter le reste.

        plat-dessert :
            un tuple ihmsgInfo avec les messages qu'on veut dedans.
            En particulier IHMSG_REDRAW_MENU si le stimuli s'est modifié des trucs
            et veut se redessiner.
        """
        return IHMSG_VOID


    def changeLanguage(self):
        """
        Fonction exécutée par le code extérieur, pour prévenir les MenuElem qu'on change
        la langue (français/anglais). Si y'a du texte, ou d'autres trucs, faut les changer.

        on ne passe pas la nouvelle langue en param. Y'a pas besoin. Cette info se trouve
        dans l'objet txtStock, la classe contenant tous les textes de toutes les langues.

        dans cette fonction, on ne doit pas effectuer le redessinage de l'objet sur une surface
        de destination. Y'a la fonction draw, pour ça, qui est automatiquement appelée
        par le code extérieur, quand on change la langue.
        Par contre, on a le droit de faire des redessinage en interne, pour préparer
        le futur redessinage vers autre part. (Genre le SubMenu)
        """
        pass

