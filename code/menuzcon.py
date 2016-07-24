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

date de la derni�re relecture-commentage : 10/03/2011

Menu permettant de configurer les touches et le son du jeu.

Putain, c'est un peu le bordel ce module. Y'a plein de cas tordus, de contournement du
fonctionnement standard de l'IHM, d'alambiquage, etc. J'ai pas trouv� plus simple.
En m�me temps, de la config de touche, c'est jamais super mega simple. Na.
"""

import pygame

import pygame.locals
pygl = pygame.locals

#wouh, y'a beaucoup de chose � importer. J'ai v�rifi�, tout est utile pour de vrai.

from common import (pyRect, addThings,
                    IHMSG_VOID, IHMSG_REDRAW_MENU, IHMSG_QUIT,
                    KEY_DIR_UP, KEY_DIR_DOWN, KEY_DIR_RIGHT, KEY_DIR_LEFT,
                    KEY_FIRE, KEY_RELOAD,
                    LIST_NO_PRINTABLE_KEY, SOUND_ENABLED, SOUND_DISABLED)

from menucomn import IMG_BUTT_RESET

from lamoche  import ALIGN_CENTER_X
from menukey  import MenuSensitiveKey
from menuimg  import MenuImage
from menusetx import MenuSensitiveText
from menutick import MenuSensitiveTick
from txtstock import txtStock
from menukrec import MenuOneKeyRecorder
from menumng  import MenuManager, LIST_KEY_ACTIVATING_MENU
from archiv   import DEFAULT_KEY_MAPPING, GLOB_DATA_ID_SOUND
from yargler  import theSoundYargler, SND_MENU_SELECT

from menuzman import (MenuManagerManual, POS_IMG_MANUAL,
                     LIST_MENU_TEXT_INFO_MANUAL, LIST_POS_KEY_NAME)

#liste des touches pour lesquels le nom de la touche ne doit pas �tre
#d�termin� � partir de la valeur event.unicode renvoy�e par pygame.
#Y'a toute la liste des touches renvoyant des caract�res non imprimables, ainsi que la touche
#espace. Ben oui, espace renvoie le caract�re " ". C'est tr�s bien. Sauf que " ", comme nom
#de touches, c'et vraiment pourri. Il faut utiliser le nom "space", renvoy� par pygame.key.name.
LIST_KEYCODE_IGNORE_CHAR = LIST_NO_PRINTABLE_KEY + (pygl.K_SPACE, )

#Liste de textes statiques � afficher. (Il y a ceux du MenuManagerManual + ceux l�).
#Cette liste a la m�me structure que menuzman.LIST_MENU_TEXT_INFO_MANUAL.
#L� aussi, les positions sont donn�es par rapport � la grande image du manuel,
#pas par rapport au haut-gauche de l'�cran. D'o� les valeurs n�gatives de mayrde.
LIST_MENU_TEXT_INFO_CONFIG = (
    (txtStock.CONFIG_CLICK_1, ( -35, -45)),
    (txtStock.CONFIG_CLICK_2, ( -35, -25)),
    (txtStock.CONFIG_EXIT,    ( -35, 230)),
)

#dictionnaire de correspondance literalValue <- boolValue, pour la checkbox d'activation du son.
GLOB_DATA_SOUND_FROM_TICK_VALUE = {
    False : SOUND_DISABLED,
    True  : SOUND_ENABLED,
}



class MenuManagerConfig(MenuManagerManual):
    """
    menu permettant au joueur de configurer des tas de trucs (les touches et le son, en fait).
    """

    #faudra passer la config des toucheu ...
    def __init__(self, surfaceDest, dicImg, fontDefault, fontLittle,
                 dicTickImage, archivist):
        """
        constructeur. (thx captain obvious)

        entr�e :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault, fontLittle : objets pygame.font.Font. les polices de caract�res.

            dicTickImage : dictionnaire contenant les images de la case � cocher.
                           voir constructeur de MenuSensitiveTick

            archivist : objet de la classe �poney-ime, qui g�re le fichier de sauvegarde
                de la config et des high scores. C'est l� dedans que y'a la config
                des touches.
        """

        MenuManager.__init__(self, surfaceDest, dicImg)

        #On rassemble les infos permettant de cr�er les MenuText statiques du
        #MenuManagerManual, et ceux sp�cifiques au MenuManagerConfig
        liMenuTxtInf = LIST_MENU_TEXT_INFO_MANUAL + LIST_MENU_TEXT_INFO_CONFIG

        #On balance tout �a � la fonction qui initialise les MenuElem commun � Manual et Config
        #Enfin pas tout � fait commun, vu que y'a des MenuText sp�cifique � la Config,
        #Mais justement, ils sont dans la liste pass� en param. Bon, me faites pas chier ok ?
        param = (fontDefault, fontLittle, archivist, liMenuTxtInf)
        self.initCommonStuff(*param)

        #dans cette classe, le dicMenuElemKey contient des MenuElem de type MenuSensitiveText.
        #A part �a, ce dico est structur� pareil que dans le MenuManagerManual
        self.dicMenuElemKey = {}
        #dictionnaire inverse de self.dicMenuElemKey. Ouais j'en ai besoin. C'est sale. D�sol� !
        #donc. Cl� : MenuSensitiveText affichant le nom d'une touche, et permettant de
        #reconfigurer cette touche. Valeur : identifiant de la touche en question.
        self.dicKeyMenuElem = {}
        #liste des MenuSensitiveText qu'on trouve dans le dico dicMenuElemKey.
        #J'en ai besoin juste vite fait provisoirement.
        listMenuTextKey = []

        # --- cr�ation des MenuSensitiveText permettant d'afficher et configurer les touches ---

        for idKey, coord in LIST_POS_KEY_NAME:

            #calcul des coordonn�es absolues du MenuText (par rapport au haut-gauche de l'�cran)
            rectCoord = POS_IMG_MANUAL.move(coord)

            #Comme avec le MenuManagerManual, je d�finis ni le param idTxtStock, ni le param text.
            #Et sinon, tous les MenuSensitiveText permettant de configurer les touches
            #utilise la m�me funcAction. (self.mactConfigKey). On fera la diff�rence gr�ce �
            #la variable self.menuElemTakingEvent, que d�fini le MenuManager juste avant
            #d'ex�cuter une funcAction.
            menuElem = MenuSensitiveText(
                rectCoord, fontDefault,
                self.mactConfigKey, alignX=ALIGN_CENTER_X)

            #ajout dans la liste, le dico dicMenuElemKey, et le dico inverse.
            listMenuTextKey.append(menuElem)
            self.dicMenuElemKey[idKey] = menuElem
            self.dicKeyMenuElem[menuElem] = idKey

        # --- cr�ation du MenuElem permettant d'enregistrer le code d'une touche appuy�e. ---

        #On n'a besoin de qu'un seul MenuElem enregistreur pour toutes les touches � configurer.
        #(On transmet le code de la touche enregistr�e � qui qu'on veut.)
        self.mOneKeyRecorder = MenuOneKeyRecorder(self.mactNewKeyTyped)

        # --- cr�ation du bouton permettant de remettre la config des touches par d�faut. ---

        #Alors c'est un peu fait � l'arrache. Le bouton, c'est un SensitiveText,
        #superpos� sur une image statique, qui ressemble vaguement � un cadre de bouton.

        #Le SensitiveText.
        param = (pyRect(60, 255), fontDefault,
                 self.mactResetDefaults, txtStock.CONFIG_RESET)

        mbuttResetDefaults = MenuSensitiveText(*param)

        #Et l'image statique.
        imgButton = dicImg[IMG_BUTT_RESET]
        mimgResetDefaults = MenuImage(pyRect(50, 254), imgButton)

        # --- cr�ation de la case � cocher permettant d'activer/d�sactiver le son.

        #r�cup�ration de la valeur actuelle de l'activitude du son
        globDataSound = self.archivist.dicGlobData[GLOB_DATA_ID_SOUND]

        #bon, y'a plein de param pour cr�er ce truc. Mais c'est pas compliqu�, hein ?
        self.mtickSound = MenuSensitiveTick(
            pyRect(310, 260), fontLittle, self.mactToggleSound,
            dicTickImage, txtStock.CONFIG_SOUND,
            dicLiteralFromBool=GLOB_DATA_SOUND_FROM_TICK_VALUE,
            literalValInit=globDataSound)

        # --- cr�ation du MenuElem qui bind la touche Esc � la fonction mactQuitOrCancel ---

        param = (self.mactQuitOrCancel, pygl.K_ESCAPE)
        mkeyQuitOrCancel = MenuSensitiveKey(*param)

        # --- rangement de tous les MenuElem cr��s, dans la grande liste globale. ---

        #on commence par faire une liste de sous-liste, parce qu'on fait avec ce qu'on a.
        #L'ordre semble un peu �trange. Y'a un bout de liste au d�but, et un autre bout � la fin.
        #C'est fait expr�s, carcet ordre d�termine l'ordre du cyclage de focus avec Tab, et
        #aussi l'ordre dans lequel les �l�ments sont affich�s. (Donc faut mettre les images
        #"en dessous" des textes.)
        #
        #truc important concernant l'ordre :
        #Le menuElem qui chope la touche Esc pour quitter / annuler la config en cours,
        #doit �tre plac� avant le menuElem qui enregistre la nouvelle touche.
        #(mkeyQuitOrCancel doit �tre avant self.mOneKeyRecorder).
        #Si on appuie sur Esc alors que y'a une config en cours, faut pas quitter.
        #Donc faut que l'objet mkeyQuitOrCancel sache que y'a une config en cours.
        #Pour le savoir, il regarde l'�tat de self.mOneKeyRecorder. Si cet objet est
        #en train d'enregistrer quelque chose, y'a une config en cours.
        #Si on place self.mOneKeyRecorder avant, il va se d�sactiver en voyant l'event d'appui
        #sur Esc, puis, lorsque cet event sera transmis � mkeyQuitOrCancel, il va faire
        #quitter tout le menu. Et faut pas. Voil�.
        lilistOfMenuElem = (
                                (self.mimgManual, mimgResetDefaults,
                                 mkeyQuitOrCancel, self.mOneKeyRecorder),

                                tuple(listMenuTextKey),

                                tuple(self.listMenuText),

                                (mbuttResetDefaults, self.mtickSound)
                            )

        #et maintenant, on fait une grande liste "aplatie", en concat�nant toutes les sous-liste.
        self.listMenuElem = addThings(*lilistOfMenuElem)

        #�a c'est un peu bancal. Mais �a marche. Ca indique si l'enregistreur de touche a
        #enregistr� une touche activant le MenuElem focus� (entr�e, espace, ...)
        #Y'a besoin de le savoir, car justement faut zapper cette activation si on �tait
        #en train d'enregistrer une touche pour la config, et que donc on a voulu l'enregistrer,
        #Et non pas activer un quelconque MenuElem.
        self.justRecordedIsAnActivationKey = False

        #pointeur sur le MenuSensitiveText focus�, activ�, et pour lequel on est en train
        #d'enregistrer une nouvelle touche. Si c'est None, c'est qu'on n'est pas en train
        #d'enregistrer une nouvelle touche.
        self.menuElemKeyActive = None

        self.initFocusCyclingInfo()


    def startMenu(self):
        """
        fonction qui s'ex�cute au d�but de l'activation du menu
        (voir description de la fonction dans la classe-m�re)
        """

        #Mise (ou remise) � jour des noms des touches en fonction du mapping en cours.
        self.initTextOfMenuElemKey()


    def stopKeyRecording(self, mustRefreshMenuElemKey):
        """
        Arr�te l'enregistrement de touche, si il y en a un en cours.
        Si y'en a pas en cours, cette fonction n'effectue que des trucs qui servent � rien.

        entr�es :
            mustRefreshMenuElemKey : bool�ean. Indique si on doit r�actualiser le texte
            du MenuSensitiveText affichant la touche pour laquelle on �tait en train de faire
            un enregistrement de touche. (bla bla bla, trop de blabla j'arr�te)

        Lorsque cette fonction est ex�cut�e, faut peut-�tre faire un redraw du menu,
        vu qu'on aura peut-�tre modifi� le texte d'un MenuSensitiveText.
        """

        if mustRefreshMenuElemKey and self.menuElemKeyActive is not None:

            #on �tait vraiment en train d'enregistrer une touche. Faut arr�ter �a.
            #rafra�chissement du texte du MenuSensitiveText pour lequel on est en train
            #d'enregistrer une nouvelle touche. Ca permet de virer les 3 points d'interrogation
            #affich� sur cette touche.
            self.refreshMenuElemKeyActive()

        #d�sactivation de l'enregistrement, pour le MenuElem qui enregistre.
        self.mOneKeyRecorder.desactivateRecording()

        #Supression de la r�f�rence au MenuSensitiveText pour lequel on est en train
        #d'enregistrer une nouvelle touche
        self.menuElemKeyActive = None


    def mactConfigKey(self):
        """
        Fonction qui s'ex�cute lorsqu'on active (avec un clic, ou une touche entr�e/espace),
        l'un des MenuSensitiveText utilis� pour changer une touche du jeu.

        Il faut lancer l'enregistrement de la prochaine touche, pour la prendre en compte
        dans la config.

        (Cette fonction est li�e � tous les MenuSensitiveText de config de touche.)

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #son de s�lection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        if self.justRecordedIsAnActivationKey:
            #On est arriv� dans l'ex�cution de cette fonction, alors qu'on avait rien � y faire.
            #Parce qu'on �tait en train d'enregistrer une nouvelle touche pour la config,
            #Et le joueur a appuy� sur Entr�e ou Espace. Du coup, le MenuManager de base
            #a activ� le MenuElem focus�, mais c'est pas ce qu'on veut. Donc on se barre
            #en catimini, sans oublier de remettre � False cette variable � la con.
            #(Ouais en fait on pourrait la remettre � False ailleurs, c'est � dire lorsqu'on
            #d�sactive l'enregistrement. Mais � ce moment l�, on la remettrait � False alors
            #que c'est pas absolument n�cessaire. Donc, paf, ici, et �a va tr�s bien.)
            self.justRecordedIsAnActivationKey = False
            #Et hop, au revoir. C'est pas moi, j'�tais pas l�, pis j'�tais bourr� en plus.
            return IHMSG_VOID

        if self.menuElemKeyActive is not None:
            #On �tait en train d'enregistrer une autre touche. Faut r�actualiser le nom de
            #cette touche, pour remettre celle du mapping. (On vire les points d'interrogation).
            self.refreshMenuElemKeyActive()

        #On r�cup�re la r�f�rence sur le MenuSensitiveText qui est actuellement activ�,
        #et pour lequel on est en train d'ex�cuter cette funcAction.
        self.menuElemKeyActive = self.menuElemTakingEvent

        #r�actualisation du texte de ce MenuSensitiveText. Pour indiquer que c'est celui-l�
        #pour lequel on est en train d'enregistrer une touche. (On met des points d'interrogation
        #� la place du nom de la touche).
        self.refreshMenuElemKeyActive(False, "???")

        #Lancement de l'enregistrement de la prochaine touche. Ouais ! Enfin !
        self.mOneKeyRecorder.activateRecording()
        return (IHMSG_REDRAW_MENU, )


    def refreshMenuElemKeyActive(self, refreshWithMapping=True, newText=""):
        """
        Rafra�chit le texte et la font du MenuSensitiveText actuellement en
        train d'enregistrer une nouvelle touche.

        entr�es :
            refreshWithMapping : bool�ean.
                True : le texte et la font doivent �tre rafra�chis en fonction
                de la touche actuellement d�finie dans le mapping self.dicKeyMapping.
                Dans ce cas, le param�tre newText ne sert � rien
                False : le texte doit �tre rafraichi avec le param�tre newText
                La font est rafraichie avec celle affichant les petits caract�res (pas le choix).

            newText : string
                nouvelle valeur du texte du MenuSensitiveText, ou pas. Ca d�pend de
                refreshWithMapping. Voir juste au-dessus.

        pr�-conditions :
            faut que self.menuElemKeyActive soit diff�rent de None, sinon �a p�te.
        """

        # -- (re)d�finition de newText et d�finition de font --

        if refreshWithMapping:

            #faut rafraichir selon le mapping de touche.

            #r�cup�ration de l'identifiant de touche dont on rafraichit le SensitiveText.
            idKeyActive = self.dicKeyMenuElem[self.menuElemKeyActive]
            #r�cup�ration du code et du event.unicode actuellement mapp� sur cette touche l�.
            (keyMapped, charKeyMapped) = self.dicKeyMapping[idKeyActive]
            #d�termination du vrai nom et de la font pour ce code de touche.
            (keyName, font) = self.determKeyNameFont(keyMapped, charKeyMapped)
            #red�finition de newText. C'est un peu brutal de changer comme �a la valeur
            #d'un param�tre d'entr�e. Mais on a le droit. Ce param est une string, donc
            #c'est modifi� localement. Pas de risque de modifier la valeur de l'�ventuelle
            #variable string pass� en param. (Enfin, � priori).
            newText = keyName

        else:

            #on prend la police de caract�re affichant le texte en petit.
            font = self.fontLittle

            #Y'a rien � faire de plus. On prendra directement la valeur du param�tre newText.

        #rafraichissement du texte et de la font du MenuSensitiveText
        self.menuElemKeyActive.changeFontAndText(font, newText)


    def mactNewKeyTyped(self):
        """
        fonction ex�cut�e par le MenuElem enregistreur de touche (self.mOneKeyRecorder),
        lorsque le joueur vient juste d'appuyer sur une touche, et si l'enregistreur
        est en mode enregistrement. Haha

        pr�-conditions :
            faut que self.menuElemKeyActive soit diff�rent de None, sinon �a p�te.
            Pas pour la m�me raison que pour la fonction refreshMenuElemKeyActive, mais
            �a p�terait quand m�me. Heureusement, commme je suis un super codeur trop fort,
            je suis sur que cette variable est pas � None au moment o� on ex�cute cette fonction.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #r�cup�ration du code et du caract�re de la touche, que l'enregistreur vient d'enregistrer
        newKey = self.mOneKeyRecorder.keyRecorded
        newCharKey = self.mOneKeyRecorder.charKeyRecorded

        #Filtrage de certains caract�res de touches pourris. (faudra d�terminer le nom de
        #la touche � partir du code, et pas du caract�re).
        #Voir d�but du fichier, la description de LIST_KEYCODE_IGNORE_CHAR
        if newKey in LIST_KEYCODE_IGNORE_CHAR:
            newCharKey = ""

        #Si le joueur a voulu enregistrer la touche Esc ou Tab pour le mapping,
        #alors on doit la refuser.
        #Pour la touche Esc, �a se justifie. Y'en a besoin pendant le jeu, pour indiquer qu'on
        #veut quitter le jeu, justement. (Et c'est pas configurable, car j'ai d�cid� ainsi)
        #Pour la touche Tab, �a se justifie un peu moins. Mais c'est juste moi, j'ai pas
        #envie que la touche de cyclage de focus puisse �tre utilis�e pendant le jeu. Na.
        if newKey not in (pygl.K_TAB, pygl.K_ESCAPE):

            #son de s�lection d'un truc : "blululup" !!
            theSoundYargler.playSound(SND_MENU_SELECT)

            #r�cup�ration de l'identifiant de la touche qu'on est en train de configurer.
            idKeyActive = self.dicKeyMenuElem[self.menuElemKeyActive]
            #mise � jour du dico de mapping des touches, avec le nouveau code et caract�re.
            self.dicKeyMapping[idKeyActive] = (newKey, newCharKey)

        #on arr�te l'enregistrement, et on r�affiche le nom de la touche en cours
        #(D'autant plus que ce nom vient peut-�tre d'�tre chang�)
        self.stopKeyRecording(True)

        #Le joueur a voulu enregistrer, pour le mapping, une touche d'activation de MenuElem
        #(entr�e, espace, ...). C'est acceptable. Mais il faut s'en souvenir, car �a veut
        #dire qu'on doit justement pas activer le MenuElem focus�. (voir mactConfigKey).
        if self.mOneKeyRecorder.keyRecorded in LIST_KEY_ACTIVATING_MENU:
            self.justRecordedIsAnActivationKey = True

        return (IHMSG_REDRAW_MENU, )


    def mactQuitOrCancel(self):
        """
        fonction ex�cut� lorsque le joueur appuie sur Echap.

        Faut, soit quitter le menu, soit d�sactiver l'enregistrement de touche en cours.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        if self.menuElemKeyActive is not None:

            #on arr�te l'enregistrement, et on r�affiche le nom de la touche en cours.
            #Du coup, on teste deux fois que self.menuElemKeyActive est pas None.
            #On vient de le tester juste avant, et on va le retester dans cette fonction.
            #C'est pas super classe, mais c'est pas un drame.
            self.stopKeyRecording(True)

            #on ne quitte pas le menu. On indique juste qu'il faut rafra�chir son affichage
            #sur l'�cran principal.
            return (IHMSG_REDRAW_MENU, )

        else:

            #y'a pas d'enregistrement de touche en cours. Faut quitter le menu. Sans oublier
            #de sauvegarder la nouvelle config.

            #L'activitude du son est indiqu� dans la valeur lit�rale de la case � cocher.
            globDataSound = self.mtickSound.literTickValue
            #On construit un dictionnaire de mise � jour des globData, avec une seule
            #valeur dedans. (l'activitude du son, donc)
            dicUpdateSound = { GLOB_DATA_ID_SOUND : globDataSound }

            #mise � jour du son et du nouveau mapping de touche, dans l'archivist.
            param = (self.dicKeyMapping, dicUpdateSound)
            self.archivist.modifyGlobDataAndKeyMapping(*param)

            #et paf, on quitte le menu.
            return (IHMSG_QUIT, )


    def mactResetDefaults(self):
        """
        fonction qui s'ex�cute quand on appuie sur le bouton pour remettre le mapping de touche
        par d�faut

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #son de s�lection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #on arr�te l'enregistrement des touches, (si y'en a un en cours)
        #On r�affiche pas le nom de la touche en cours. Car de toutes fa�ons, faut r�afficher
        #tous les noms de touches, et c'est fait juste apr�s.
        self.stopKeyRecording(False)

        #On reprend le mapping detouche par d�faut.
        self.dicKeyMapping = dict(DEFAULT_KEY_MAPPING)

        #faut rafra�chir tous les MenuSensitiveText affichant les noms des touches.
        #(une fois de plus, faut que y'ait les m�mes cl�s dans self.dicKeyMapping et dans
        #self.dicMenuElemKey. Mais �a c'est bon).
        for idKey, (keyMapped, charKeyMapped) in self.dicKeyMapping.items():

            #r�cup�ration du MenuSensitiveText affichant le nom de la touche concern�e
            menuElem = self.dicMenuElemKey[idKey]
            #d�termination du nom de la touche, et de la font � utiliser pour ce nom
            (keyName, font) = self.determKeyNameFont(keyMapped, charKeyMapped)

            #changement de la police de caract�re et du texte du MenuSensitiveText
            #TRODO pour plus tard : ordre des param pas homog�ne. Corriger determKeyNameFont.
            menuElem.changeFontAndText(font, keyName)

        return (IHMSG_REDRAW_MENU, )


    def mactToggleSound(self):
        """
        fonction qui s'ex�cute quand on clique sur la case � cocher du son on/off
        Faut inverser l'activation/d�sactivation du son.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        if self.menuElemKeyActive is not None:

            #on �tait en train d'enregistrer une touche. Faut arr�ter �a.

            #on arr�te l'enregistrement, et on r�affiche le nom de la touche en cours.
            #Du coup, on teste deux fois que self.menuElemKeyActive est pas None.
            #(Comme dans la fonction mactQuitOrCancel). H�h�, on teste deux fois un truc,
            #� deux endroits diff�rents. Ca fait plein de fois "deux" !! Super !!
            self.stopKeyRecording(True)

        #Le MenuTick ne fait pas le toggle de tick de sa propre initiative.
        #Faut appeler manuellement la fonction inversant le dessin de la case � cocher.
        self.mtickSound.toggleTick()

        #r�cup�ration de la globData indiquant l'activitude du son.
        globDataSoundCurrent = self.mtickSound.literTickValue
        #transmission de l'activitude du son � l'objet qu joue les sons
        theSoundYargler.changeSoundEnablation(globDataSoundCurrent)

        #son de s�lection d'un truc : "blululup" !! (le son n'est pas jou� si on vient
        #de d�sactiver les sons juste avant).
        theSoundYargler.playSound(SND_MENU_SELECT)

        return (IHMSG_REDRAW_MENU, )
