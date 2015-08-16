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

date de la derni�re relecture-commentage : 04/02/2011

Element de menu qui s'affiche �ventuellement quelque part, qui re�oit des stimuli
de click de souris et d'appuyage de touche, et qui fait eventuellement des trucs en fonction.

Mais l� c'est la classe g�n�rique, alors y'a pas grand chose dedans.

Vocabulaire et gestion d'interface : (bizarro�de, mais na!).

GetFocus, LoseFocus : l'�l�ment de menu est s�lectionn�/d�slectionn�, via les touches
du clavier (fl�che haut/bas, tab, ...) ou la souris. Les deux sont g�r�s,
mais c'est le dernier qui a parl� qui a raison.

*) Les �l�ments peuvent �ventuellement avoir un sensitiveRect. C'est une zone dans l'�cran
� laquelle l'�l�ment doit r�agir.
Les �l�ments peuvent �ventuellement avoir un drawRect. C'est une zone dans l'�cran
sur laquelle l'�l�ment se dessine.

*) On peut avoir un drawRect et ne pas avoir de sensitiveRect.
Exemple : les images et les textes statiques. (MenuText, MenuImage)

*) En g�n�ral, quand on a un sensitiveRect, y'a aussi un drawRect, et les deux Rects sont
� peu pr�s confondus. Mais th�oriquement rien ne l'oblige.

*) Si j'appuie sur une touche de cyclage d'�l�ment (tab, up, down),
je passe � l'�l�ment de menu suivant.
(La s�lection pr�c�dente avait �t� faite par la souris ou par l'appui d'une touche).
La touche tab fait cycler parmi tous les �l�ments focusables. ils sont ordonn�s dans une liste.

*) TRODO pour plus tard : shift+tab doit faire cycler parmi tous les �l�ments focusables,
mais dans l'autre sens.

*) On peut d�finir une sous-liste d'�l�ments focusable. (Par exemple, les
options du menu principal). Lorsqu'on fera up ou down, on naviguera dans cette sous-liste,
dans un sens ou dans l'autre.
Si on ne d�finit pas de sous-liste, up et down ne font rien.

*) Si il y a une sous-liste d'�l�ment focusable, que l'�l�ment actuellement focus�
n'est pas dans cette liste, et que j'appuie sur up ou down, alors on focus
sur le premier �l�ment de la sous-liste.

*) Si j'am�ne le curseur de souris sur le sensitiveRect d'un �l�ment, il est focus�.
Pas besoin de cliquer.

*) Si je focus sur un �l�ment avec la souris, et que j'appuie sur Tab, �a cycle.
Donc l'�l�ment focus� n'est plus celui point� par la souris. Tant que je ne bouge pas
la souris, �a reste comme �a.

*) D�s que je bouge ma souris, m�me un tout petit peu, je res�lectionne l'�l�ment
sur lequel se trouve la souris.
Si je bouge ma souris sur rien, je ne change pas le focus courant.

*) Si j'appuie sur l'une des touche Entr�e ou sur Espace. J'active l'�l�ment s�lectionn�.
(Quel que soit la fa�on dont il a �t� s�lectionn�, on s'en fout.)
Si y'a aucun �l�ment s�lectionn�, �a ne fait rien.

*) Si la souris ne se trouve pas sur l'�l�ment focus�, et que je clique,
alors je focus imm�diatement sur l'�l�ment point� (m�me si j'ai cliqu� sans bouger)
et j'active la fonction li�e � cet �l�ment (funcAction).

*) Si je clique avec ma souris sur rien, il ne se passe rien. L'�l�ment focus� reste
le m�me.

*) Certains �l�ments n'ont pas de sensitiveRect. On ne peut jamais les s�lectionner
avec la souris. (Je ne fais �a que pour les �l�ments non-interactifs. Sinon c'est cr�tin)

*) Certains �l�ments n'acceptent pas du tout le focus. Quand on passe la souris dessus, il
ne se passe rien, et quand on fait Tab, le cyclage de focus saute cet �l�ment.

*) En g�n�ral, on a la relation r�ciproque :
�l�ment n'ayant pas de sensitiveRect <=> �l�ments n'acceptant pas du tout le focus.
(Mais th�oriquement, rien ne l'interdit).

*) Il y a aussi des �l�ments sans focus, sans sensitiveRect, et qui ne s'affichent m�me pas.
Mais ils peuvent ex�cuter la fonction qui leur est li�e, quand on appuie sur une touche.
C'est juste un bind sur une touche en fait. Mais je l'ai foutu sous forme d'�l�ment,
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
    Fonction permettant de d�placer le focus d'un �l�ment vers le suivant.
    Cette fonction se trouve dans ce fichier de code, car je savais pas o� la foutre ailleurs.

    entr�es :
        focusedElem : r�f�rence vers le menuElem ayant actuellement le focus
                      On peut mettre ce param � None. Dans ce cas, pas de cyclage,
                      et on focusera sur le premier �l�ment de listMenuElemToCycle.
                      m�me si, euh... je suis pas sur d'avoir compl�tement test�

        listMenuElemToCycle : liste de menuElem dans laquelle on fait cycler le focus

        loopAuthorized : boolean. Indique si le cyclage de focus est autoris� �
                         faire des tours du compteurs.
                         Si il ne l'est pas et qu'on sort de la liste, alors
                         on d�placera pas le focus, et la fonction renverra None.

        delta : int (positif ou negatif). Indique de combien d'�l�ment on veut se
                d�placer dans la liste. En g�n�ral, on met juste +1 ou -1, pour
                indiquer dans quel sens on veut aller. Mais on pourrait mettre autre chose
                si on veut faire des trucs bizarres.
                (Moi j'en fais pas, je fais jamais de trucs bizarres moi).

    plat-dessert :

        Soit une r�f�rence vers le menuElem qui a pris le focus (donc le nouveau focusedElem)
        Soit une r�f�rence vers le m�me menuElem parce que �a a pas chang�,
        Soit None, si on n'a pas eu le droit de faire de tour du compteur alors qu'on devait.

        La fonction s'occupe elle-m�me de transf�rer le focus, en appelant les
        m�thodes LoseFocus et GetFocus des menuElem correspondants.

    Y'a des fois, on a besoin de faire un sous-cyclage de focus. Par exemple,
    l'�l�ment MenuSubMenu contient des �l�ments de Menu embarqu� dans lui-m�me.

    C'est pourquoi, avant de faire un cyclage principal, on pr�vient l'�l�ment
    actuellement focus�. Si l'elem focus� est simple, il r�pond qu'il accepte
    le cyclage, et on fait un cyclage principal.
    Si l'elem focus� est plus complexe, il se fait son sous-cyclage en interne. Et
    ensuite, il peut r�pondre deux choses diff�rente :
     - son sous-cyclage n'est pas fini, dans ce cas, il n'accepte pas le cyclage principal.
     - son sous-cyclage est fini (on �tait arriv� au dernier sous-�l�ment de menu),
    dans ce cas, il accepte le cyclage principal

    quand on cycle, on saute les �l�ments de la liste qui n'acceptent pas de prendre le focus.

    Si aucun �l�ment de la liste n'accepte de prendre le focus, la fonction va planter.
    Alors faut pas le faire, d'accord ?

    Le focusedElem pass� en param�tre peut �tre None, ou peut ne pas �tre dans listMenuElemToCycle,
    dans ce cas, on d�marrera � partir du premier �l�ment de la liste.

    Si on renvoie None, parce qu'on peut pas faire le tour du compteur, on ne fait pas perdre
    le focus � l'�l�ment focus�.
    TRODO : peut �tre qu'on devrait non ? faut que je regarde �a.
    """

    if focusedElem is not None:

        #on informe l'�l�ment focus� qu'on veut faire du cyclage de focus.
        #si c'est un �l�ment normal, il accepte de lacher le focus, et on va pouvoir cycler,
        #si c'est un subMenu, il va faire un cyclage en interne, et �ventuellement lacher
        #le focus si son cyclage est arriv� sur le dernier elem.
        ihmsgInfo = focusedElem.takeStimuliFocusCycling()
        acceptQuitFocus = IHMSG_CYCLE_FOCUS_OK in ihmsgInfo

    else:

        #Pas d'�l�ments focus�. Donc pas besoin de demander � qui que ce soit si il accepte
        #de lacher le focus.
        acceptQuitFocus = True

    if not acceptQuitFocus:
        #l'�l�ment focus� ne veut pas lacher le focus. On ne fait rien, on renvoie l'�l�m focus�.
        return focusedElem

    #liste des param�tres � passer � la fonction qui fait avancer un index entre deux bornes,
    #y'a pas le premier param, mais il change tout le temps, alors on le passera en live.
    param = (delta, 0, len(listMenuElemToCycle), loopAuthorized)

    # --- d�termination de l'index du premier menuElem qui pourrait (avoir le focus, ou pas) ---

    if focusedElem in listMenuElemToCycle:

        #l'�l�ment focus� est dans la liste. On commence par choper son index.

        #focusedElemIndex = listMenuElemToCycle.index(focusedElem)
        #l'instruction index n'existe pas dans le python 2.5.4. Allez zou, � la mimine.
        focusedElemIndex = -1
        menuElemCurrent = None

        #petite boucle un peu cheap, pour trouver l'index de focusedElem dans listMenuElemToCycle
        #la boucle va forc�ment fonctionner, puisqu'on a v�rifi� avant
        #que focusedElem est in listMenuElemToCycle
        while menuElemCurrent != focusedElem:
            focusedElemIndex += 1
            menuElemCurrent = listMenuElemToCycle[focusedElemIndex]

        #on fait avancer une premi�re fois l'index, c'est le cyclage effectif.
        #Mais que sur les index.
        newFocusedElemIndex = moveIndexInBounds(focusedElemIndex, *param)

        #Tour du compteur non autoris�. On se barre comme un voleur en renvoyant None.
        if newFocusedElemIndex is None:
            return None

    else:

        #l'�l�ment focus� n'est paz dans la liste. On prend arbitrairement le premier.
        newFocusedElemIndex = 0

    # --- d�termination de l'index du menuElem qui peut vraiment avoir le focus ---

    #on avance dans la liste jusqu'� trouver un menuElem qui accepte le focus.
    #Ca peut �ventuellement �tre l'�l�ment actuel (car on vient de faire un
    #cyclage juste ci-dessus, enfin ou pas si on a chop� le premier, bref...)
    #Mais il faut le v�rifier que �a "peut �ventuellement �tre l'�l�ment actuel"
    while not listMenuElemToCycle[newFocusedElemIndex].acceptFocus:

        #et un cyclage de plus.
        newFocusedElemIndex = moveIndexInBounds(newFocusedElemIndex, *param)

        #fail tour du compteur non autoris�. On se barre comme un voleur en renvoyant None.
        if newFocusedElemIndex is None:
            return None

        #fait chier parce que le bout de code ci-dessus, il est en doublon
        #avec le bout de code ci-ci-dessus. J'ai essay� de factoriser tant que je peux avec la
        #fonction moveIndexInBounds, mais �a fait pas tout. C'est � cause de ces putain de while
        #qu'on peut pas �crire � l'envers. Genre le repeat ... until du pascal. Pourquoi
        #y'a pas ce truc en python ? Ce serait putain de cool.

    # --- Ah y est ! on a chop� l'�l�ment qui veut bien du focus ! Donc : transfert du focus ---

    #on fait lacher le focus � l'�l�ment actuel qui l'a
    if focusedElem is not None:
        focusedElem.takeStimuliLoseFocus()

    #r�cup�ration de l'�l�ment � qui donner le focus, � partir de l'index.
    focusedElem = listMenuElemToCycle[newFocusedElemIndex]

    #don du focus � cet �l�ment. Oui je te dooo-ooonneeuuu !
    focusedElem.takeStimuliGetFocus()

    return focusedElem



class MenuElem():
    """
    menuElem super g�n�rique qu'on va d�cliner en plein de trucs.
    """

    def __init__(self):
        """
        constructeur. (thx captain obvious)
        """

        #indique dans quelle zone de son conteneur (menu ou submenu) est dessin� ce menuElem.
        #on peut mettre un Rect, ou None si ce menuElem ne se dessine pas.
        self.rectDrawZone = None

        #pour les menuElem qui se dessinent, indique si il faut redessiner � chaque cycle ou pas.
        #on peut bien evidemment changer cet attribut en live. Crac youpi.
        #attention, entre deux refresh, on ne r�affiche pas le background du menu. Donc
        #si on veut faire un menuelem anim�, faut tout le temps tripoter les m�mes pixels,
        #ou alors faut demander un redraw global avec IHMSG_REDRAW_MENU.
        #Y'a pas de juste milieu. TRODO : pour plus tard, essayer de pr�voir un juste milieu.
        self.mustBeRefreshed = False

        #r�f�rence vers la fonction � ex�cuter quand cet �l�ment de menu est activ�.
        #C'est � dire quand on clique dessus, o� quand le focus est dessus et
        #qu'on appuie sur entr�e ou espace, ou dans d'autres cas funny qu'on code soi-m�me
        #dans les classes h�rit�es
        self.funcAction = None

        #indique si le menuElem accepte le focus ou pas.
        self.acceptFocus = False

        #indique si le menuElem a le focus sur lui, ou pas. On n'est pas cens� avoir plusieurs
        #menuElem en m�me temps ayant le focus. Mais y'a rien de vraiment fait pour contr�ler �a.
        #Et en plus c'est pas tout � fait exact car on peut avoir un subMenu qui a le focus,
        #et l'un de ses sous-elem qui a un sous-focus. Bref : osef.
        self.focusOn = False


    def draw(self, surfaceDest):
        """
        dessine le menuElem.

        entr�es:
            surfaceDest :
                surface sur laquelle on doit dessiner le menuElem. Ca peut �tre
                le screen principal, la surface d'un submenu, ou n'importe quoi d'autre.
                On dessine tout comme on veut. Mais faut savoir que si on dessine
                dans un submenu, et qu'on met des pixels en noir,
                alors ces pixels seront transparents lors de l'affichage
                du subMenu dans le menu principal.
                TRODO : C'est peut �tre cr�tin. Pour ce jeu, �a me pose pas
                de probl�me. Mais faudra pas oublier �a par la suite.
        """
        pass


    def takeStimuliFocusCycling(self):
        """
        fonction ex�cut�e par le code ext�rieur, pour pr�venir que y'a un cyclage
        de focus � faire, alors que ce menuElem a pr�sentement le focus.

        sorties :
            un tuple ihmsgInfo.

        Y'a deux cas possibles :
         - le menuElem est "simple". Dans ce cas, il doit accepter de lacher son focus
           pour que le cyclage se fasse. Il faut donc mettre dans le ihmsgInfo renvoy� le
           message IHMSG_CYCLE_FOCUS_OK
         - le menuElem est "complexe" (il poss�de des sous-elements). Dans ce cas, on
           fait un sous-cyclage en interne, et si on arrive sur le dernier �l�ment,
           on acccepte de lacher le focus.
        """
        return (IHMSG_CYCLE_FOCUS_OK, )


    def takeStimuliGetFocus(self):
        """
        fonction ex�cut�e par le code ext�rieur, pour pr�venir que ce menuElem prend le focus
        """
        self.focusOn = True


    def takeStimuliLoseFocus(self):
        """
        fonction ex�cut�e par le code ext�rieur, pour pr�venir que ce menuElem perd le focus
        """
        self.focusOn = False


    def update(self):
        """
        r�actualise les trucs qu'on veut, � chaque cycle, quand ce menuElem est utilis�
        dans un menu.

        plat-dessert : soit IHMSG_VOID,
                       soit un tuple de message d'ihm, avec IHMSG_REDRAW_MENU dedans,
                       pour indiquer qu'on veut tout redrawer.

        On peut faire diff�rent truc dans cette fonction. (Sachant qu'elle est appel�e �
        chaque cycle :

         - Rien. Mettre self.mustBeRefreshed � False, et renvoyer IHMSG_VOID
           Cet �l�ment du menu ne sera pas redessin�.

         - Des petits trucs. mettre self.mustBeRefreshed � True, et renvoyer IHMSG_VOID.
           Cet �l�ment de menu sera redessin�. Mais le menu dans l'ensemble, ainsi que
           l'image de fond, ne le sera pas. Si on fait un truc comme �a, il faut
           donc faire attention que la fonction draw du menuElem tripote toujours
           les m�mes pixels. Sinon �a va laisser des traces.

         - Des gros trucs. mettre self.mustBeRefreshed � <osef>, et renvoyer un
           IHMSG_REDRAW_MENU. Dans ce cas, tout le menu (img de fond + tous les elems de
           menus) seront redessin�s. Et l� y'a plus de question � se poser. Mais c'est
           un peu bourrin. A ne faire que quand c'est n�cessaire.
        """
        return IHMSG_VOID


    def takeStimuliKeys(self, dictKeyPressed, keyCodeDown, keyCharDown):
        """
        prise en compte d'une touche appuy�e par le joueur.
        Le menuElem peut d�cider d'en avoir rien � foutre, ou pas.
        En g�n�ral, le menuElem ne r�agit au plus qu'� une seule touche. C'est �
        lui de la retrouver dans le bordel des param�tres en entr�e.
        Mais y'a aussi des menuElem qui r�agissent � n'importe quelle touche, tralala.

        entr�es :
            dictKeyPressed : dictionnaire (identifiant de touche) -> bool�en.
                             indique quelles touches sont appuy�es (elles sont peut-�tre
                             appuy�es depuis vachement longtemps, ou pas, on sait pas)

            keyCodeDown : identifiant de la touche qui vient d'�tre appuy�e.
                          l� tout de suite.

            keyCharDown : caract�re unicode correspondant � la touche qui vient d'�tre
                          appuy�. Ca peut �tre un caract�re vide si c'est une touche
                          � la con, genre F1, shift, ...
                          A priori, �a g�re automatiquement tous les trucs bizarres :
                          accents, majuscules, azerty/qwerty, "�", "�", ...

        plat-dessert :
            un tuple ihmsgInfo avec les messages qu'on veut dedans.
            En particulier IHMSG_REDRAW_MENU si le stimuli s'est modifi� des trucs
            et veut se redessiner.

        TRODO pour plus tard : cette fonction de prise en compte des stimulis n'est pas appel�e
        si on relache une touche. Alors que les menuElem auraient peut �tre besoin
        d'�tre au courant de cette info. Pour l'instant osef.
        """
        return IHMSG_VOID


    def takeStimuliMouse(self, mousePos, mouseDown, mousePressed):
        """
        prise en compte des mouvements et des clics de souris.
        Cette fonction est ex�cut�e par le code ext�rieur, m�me quand le joueur
        bouge la souris sans cliquer. Ca permet de faire des trucs cools genre mouseHover tout �a.
        Le menuElem peut d�cider d'en avoir rien � foutre, ou pas.

        entr�es:
            mousePos : tuple(X,Y). Coordonn�es du curseur de souris, dans ce menu/submenu
                       Si ce menuElem est dans un subMenu, mousePos contient
                       les coordonn�es locales � ce subMenu (c'est plus pratique).
                       Si le menuElem est dans un menu g�n�ral, c'est les coordonn�es
                       � l'�cran, tout simplement.
            mouseDown : bool�en. Indique si le bouton droit de la souris est appuy�e
                        (on sait pas depuis combien de temps)
            mousePressed : bool�en. Indique si le bouton droit de la souris vient
                           d'�tre appuy�, l� maintenant.

        Ca g�re que le bouton droit de la souris parce que je m'ai pas besoin des autres.
        TRODO pour plus tard : rajouter le reste.

        plat-dessert :
            un tuple ihmsgInfo avec les messages qu'on veut dedans.
            En particulier IHMSG_REDRAW_MENU si le stimuli s'est modifi� des trucs
            et veut se redessiner.
        """
        return IHMSG_VOID


    def changeLanguage(self):
        """
        Fonction ex�cut�e par le code ext�rieur, pour pr�venir les MenuElem qu'on change
        la langue (fran�ais/anglais). Si y'a du texte, ou d'autres trucs, faut les changer.

        on ne passe pas la nouvelle langue en param. Y'a pas besoin. Cette info se trouve
        dans l'objet txtStock, la classe contenant tous les textes de toutes les langues.

        dans cette fonction, on ne doit pas effectuer le redessinage de l'objet sur une surface
        de destination. Y'a la fonction draw, pour �a, qui est automatiquement appel�e
        par le code ext�rieur, quand on change la langue.
        Par contre, on a le droit de faire des redessinage en interne, pour pr�parer
        le futur redessinage vers autre part. (Genre le SubMenu)
        """
        pass

