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

date de la dernière relecture-commentage : 10/03/2011

Menu permettant de configurer les touches et le son du jeu.

Putain, c'est un peu le bordel ce module. Y'a plein de cas tordus, de contournement du
fonctionnement standard de l'IHM, d'alambiquage, etc. J'ai pas trouvé plus simple.
En même temps, de la config de touche, c'est jamais super mega simple. Na.
"""

import pygame

import pygame.locals
pygl = pygame.locals

#wouh, y'a beaucoup de chose à importer. J'ai vérifié, tout est utile pour de vrai.

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

#liste des touches pour lesquels le nom de la touche ne doit pas être
#déterminé à partir de la valeur event.unicode renvoyée par pygame.
#Y'a toute la liste des touches renvoyant des caractères non imprimables, ainsi que la touche
#espace. Ben oui, espace renvoie le caractère " ". C'est très bien. Sauf que " ", comme nom
#de touches, c'et vraiment pourri. Il faut utiliser le nom "space", renvoyé par pygame.key.name.
LIST_KEYCODE_IGNORE_CHAR = LIST_NO_PRINTABLE_KEY + (pygl.K_SPACE, )

#Liste de textes statiques à afficher. (Il y a ceux du MenuManagerManual + ceux là).
#Cette liste a la même structure que menuzman.LIST_MENU_TEXT_INFO_MANUAL.
#Là aussi, les positions sont données par rapport à la grande image du manuel,
#pas par rapport au haut-gauche de l'écran. D'où les valeurs négatives de mayrde.
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

        entrée :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault, fontLittle : objets pygame.font.Font. les polices de caractères.

            dicTickImage : dictionnaire contenant les images de la case à cocher.
                           voir constructeur de MenuSensitiveTick

            archivist : objet de la classe époney-ime, qui gère le fichier de sauvegarde
                de la config et des high scores. C'est là dedans que y'a la config
                des touches.
        """

        MenuManager.__init__(self, surfaceDest, dicImg)

        #On rassemble les infos permettant de créer les MenuText statiques du
        #MenuManagerManual, et ceux spécifiques au MenuManagerConfig
        liMenuTxtInf = LIST_MENU_TEXT_INFO_MANUAL + LIST_MENU_TEXT_INFO_CONFIG

        #On balance tout ça à la fonction qui initialise les MenuElem commun à Manual et Config
        #Enfin pas tout à fait commun, vu que y'a des MenuText spécifique à la Config,
        #Mais justement, ils sont dans la liste passé en param. Bon, me faites pas chier ok ?
        param = (fontDefault, fontLittle, archivist, liMenuTxtInf)
        self.initCommonStuff(*param)

        #dans cette classe, le dicMenuElemKey contient des MenuElem de type MenuSensitiveText.
        #A part ça, ce dico est structuré pareil que dans le MenuManagerManual
        self.dicMenuElemKey = {}
        #dictionnaire inverse de self.dicMenuElemKey. Ouais j'en ai besoin. C'est sale. Désolé !
        #donc. Clé : MenuSensitiveText affichant le nom d'une touche, et permettant de
        #reconfigurer cette touche. Valeur : identifiant de la touche en question.
        self.dicKeyMenuElem = {}
        #liste des MenuSensitiveText qu'on trouve dans le dico dicMenuElemKey.
        #J'en ai besoin juste vite fait provisoirement.
        listMenuTextKey = []

        # --- création des MenuSensitiveText permettant d'afficher et configurer les touches ---

        for idKey, coord in LIST_POS_KEY_NAME:

            #calcul des coordonnées absolues du MenuText (par rapport au haut-gauche de l'écran)
            rectCoord = POS_IMG_MANUAL.move(coord)

            #Comme avec le MenuManagerManual, je définis ni le param idTxtStock, ni le param text.
            #Et sinon, tous les MenuSensitiveText permettant de configurer les touches
            #utilise la même funcAction. (self.mactConfigKey). On fera la différence grâce à
            #la variable self.menuElemTakingEvent, que défini le MenuManager juste avant
            #d'exécuter une funcAction.
            menuElem = MenuSensitiveText(
                rectCoord, fontDefault,
                self.mactConfigKey, alignX=ALIGN_CENTER_X)

            #ajout dans la liste, le dico dicMenuElemKey, et le dico inverse.
            listMenuTextKey.append(menuElem)
            self.dicMenuElemKey[idKey] = menuElem
            self.dicKeyMenuElem[menuElem] = idKey

        # --- création du MenuElem permettant d'enregistrer le code d'une touche appuyée. ---

        #On n'a besoin de qu'un seul MenuElem enregistreur pour toutes les touches à configurer.
        #(On transmet le code de la touche enregistrée à qui qu'on veut.)
        self.mOneKeyRecorder = MenuOneKeyRecorder(self.mactNewKeyTyped)

        # --- création du bouton permettant de remettre la config des touches par défaut. ---

        #Alors c'est un peu fait à l'arrache. Le bouton, c'est un SensitiveText,
        #superposé sur une image statique, qui ressemble vaguement à un cadre de bouton.

        #Le SensitiveText.
        param = (pyRect(60, 255), fontDefault,
                 self.mactResetDefaults, txtStock.CONFIG_RESET)

        mbuttResetDefaults = MenuSensitiveText(*param)

        #Et l'image statique.
        imgButton = dicImg[IMG_BUTT_RESET]
        mimgResetDefaults = MenuImage(pyRect(50, 254), imgButton)

        # --- création de la case à cocher permettant d'activer/désactiver le son.

        #récupération de la valeur actuelle de l'activitude du son
        globDataSound = self.archivist.dicGlobData[GLOB_DATA_ID_SOUND]

        #bon, y'a plein de param pour créer ce truc. Mais c'est pas compliqué, hein ?
        self.mtickSound = MenuSensitiveTick(
            pyRect(310, 260), fontLittle, self.mactToggleSound,
            dicTickImage, txtStock.CONFIG_SOUND,
            dicLiteralFromBool=GLOB_DATA_SOUND_FROM_TICK_VALUE,
            literalValInit=globDataSound)

        # --- création du MenuElem qui bind la touche Esc à la fonction mactQuitOrCancel ---

        param = (self.mactQuitOrCancel, pygl.K_ESCAPE)
        mkeyQuitOrCancel = MenuSensitiveKey(*param)

        # --- rangement de tous les MenuElem créés, dans la grande liste globale. ---

        #on commence par faire une liste de sous-liste, parce qu'on fait avec ce qu'on a.
        #L'ordre semble un peu étrange. Y'a un bout de liste au début, et un autre bout à la fin.
        #C'est fait exprès, carcet ordre détermine l'ordre du cyclage de focus avec Tab, et
        #aussi l'ordre dans lequel les éléments sont affichés. (Donc faut mettre les images
        #"en dessous" des textes.)
        #
        #truc important concernant l'ordre :
        #Le menuElem qui chope la touche Esc pour quitter / annuler la config en cours,
        #doit être placé avant le menuElem qui enregistre la nouvelle touche.
        #(mkeyQuitOrCancel doit être avant self.mOneKeyRecorder).
        #Si on appuie sur Esc alors que y'a une config en cours, faut pas quitter.
        #Donc faut que l'objet mkeyQuitOrCancel sache que y'a une config en cours.
        #Pour le savoir, il regarde l'état de self.mOneKeyRecorder. Si cet objet est
        #en train d'enregistrer quelque chose, y'a une config en cours.
        #Si on place self.mOneKeyRecorder avant, il va se désactiver en voyant l'event d'appui
        #sur Esc, puis, lorsque cet event sera transmis à mkeyQuitOrCancel, il va faire
        #quitter tout le menu. Et faut pas. Voilà.
        lilistOfMenuElem = (
                                (self.mimgManual, mimgResetDefaults,
                                 mkeyQuitOrCancel, self.mOneKeyRecorder),

                                tuple(listMenuTextKey),

                                tuple(self.listMenuText),

                                (mbuttResetDefaults, self.mtickSound)
                            )

        #et maintenant, on fait une grande liste "aplatie", en concaténant toutes les sous-liste.
        self.listMenuElem = addThings(*lilistOfMenuElem)

        #ça c'est un peu bancal. Mais ça marche. Ca indique si l'enregistreur de touche a
        #enregistré une touche activant le MenuElem focusé (entrée, espace, ...)
        #Y'a besoin de le savoir, car justement faut zapper cette activation si on était
        #en train d'enregistrer une touche pour la config, et que donc on a voulu l'enregistrer,
        #Et non pas activer un quelconque MenuElem.
        self.justRecordedIsAnActivationKey = False

        #pointeur sur le MenuSensitiveText focusé, activé, et pour lequel on est en train
        #d'enregistrer une nouvelle touche. Si c'est None, c'est qu'on n'est pas en train
        #d'enregistrer une nouvelle touche.
        self.menuElemKeyActive = None

        self.initFocusCyclingInfo()


    def startMenu(self):
        """
        fonction qui s'exécute au début de l'activation du menu
        (voir description de la fonction dans la classe-mère)
        """

        #Mise (ou remise) à jour des noms des touches en fonction du mapping en cours.
        self.initTextOfMenuElemKey()


    def stopKeyRecording(self, mustRefreshMenuElemKey):
        """
        Arrête l'enregistrement de touche, si il y en a un en cours.
        Si y'en a pas en cours, cette fonction n'effectue que des trucs qui servent à rien.

        entrées :
            mustRefreshMenuElemKey : booléean. Indique si on doit réactualiser le texte
            du MenuSensitiveText affichant la touche pour laquelle on était en train de faire
            un enregistrement de touche. (bla bla bla, trop de blabla j'arrête)

        Lorsque cette fonction est exécutée, faut peut-être faire un redraw du menu,
        vu qu'on aura peut-être modifié le texte d'un MenuSensitiveText.
        """

        if mustRefreshMenuElemKey and self.menuElemKeyActive is not None:

            #on était vraiment en train d'enregistrer une touche. Faut arrêter ça.
            #rafraîchissement du texte du MenuSensitiveText pour lequel on est en train
            #d'enregistrer une nouvelle touche. Ca permet de virer les 3 points d'interrogation
            #affiché sur cette touche.
            self.refreshMenuElemKeyActive()

        #désactivation de l'enregistrement, pour le MenuElem qui enregistre.
        self.mOneKeyRecorder.desactivateRecording()

        #Supression de la référence au MenuSensitiveText pour lequel on est en train
        #d'enregistrer une nouvelle touche
        self.menuElemKeyActive = None


    def mactConfigKey(self):
        """
        Fonction qui s'exécute lorsqu'on active (avec un clic, ou une touche entrée/espace),
        l'un des MenuSensitiveText utilisé pour changer une touche du jeu.

        Il faut lancer l'enregistrement de la prochaine touche, pour la prendre en compte
        dans la config.

        (Cette fonction est liée à tous les MenuSensitiveText de config de touche.)

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #son de sélection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        if self.justRecordedIsAnActivationKey:
            #On est arrivé dans l'exécution de cette fonction, alors qu'on avait rien à y faire.
            #Parce qu'on était en train d'enregistrer une nouvelle touche pour la config,
            #Et le joueur a appuyé sur Entrée ou Espace. Du coup, le MenuManager de base
            #a activé le MenuElem focusé, mais c'est pas ce qu'on veut. Donc on se barre
            #en catimini, sans oublier de remettre à False cette variable à la con.
            #(Ouais en fait on pourrait la remettre à False ailleurs, c'est à dire lorsqu'on
            #désactive l'enregistrement. Mais à ce moment là, on la remettrait à False alors
            #que c'est pas absolument nécessaire. Donc, paf, ici, et ça va très bien.)
            self.justRecordedIsAnActivationKey = False
            #Et hop, au revoir. C'est pas moi, j'étais pas là, pis j'étais bourré en plus.
            return IHMSG_VOID

        if self.menuElemKeyActive is not None:
            #On était en train d'enregistrer une autre touche. Faut réactualiser le nom de
            #cette touche, pour remettre celle du mapping. (On vire les points d'interrogation).
            self.refreshMenuElemKeyActive()

        #On récupère la référence sur le MenuSensitiveText qui est actuellement activé,
        #et pour lequel on est en train d'exécuter cette funcAction.
        self.menuElemKeyActive = self.menuElemTakingEvent

        #réactualisation du texte de ce MenuSensitiveText. Pour indiquer que c'est celui-là
        #pour lequel on est en train d'enregistrer une touche. (On met des points d'interrogation
        #à la place du nom de la touche).
        self.refreshMenuElemKeyActive(False, "???")

        #Lancement de l'enregistrement de la prochaine touche. Ouais ! Enfin !
        self.mOneKeyRecorder.activateRecording()
        return (IHMSG_REDRAW_MENU, )


    def refreshMenuElemKeyActive(self, refreshWithMapping=True, newText=""):
        """
        Rafraîchit le texte et la font du MenuSensitiveText actuellement en
        train d'enregistrer une nouvelle touche.

        entrées :
            refreshWithMapping : booléean.
                True : le texte et la font doivent être rafraîchis en fonction
                de la touche actuellement définie dans le mapping self.dicKeyMapping.
                Dans ce cas, le paramètre newText ne sert à rien
                False : le texte doit être rafraichi avec le paramètre newText
                La font est rafraichie avec celle affichant les petits caractères (pas le choix).

            newText : string
                nouvelle valeur du texte du MenuSensitiveText, ou pas. Ca dépend de
                refreshWithMapping. Voir juste au-dessus.

        pré-conditions :
            faut que self.menuElemKeyActive soit différent de None, sinon ça pète.
        """

        # -- (re)définition de newText et définition de font --

        if refreshWithMapping:

            #faut rafraichir selon le mapping de touche.

            #récupération de l'identifiant de touche dont on rafraichit le SensitiveText.
            idKeyActive = self.dicKeyMenuElem[self.menuElemKeyActive]
            #récupération du code et du event.unicode actuellement mappé sur cette touche là.
            (keyMapped, charKeyMapped) = self.dicKeyMapping[idKeyActive]
            #détermination du vrai nom et de la font pour ce code de touche.
            (keyName, font) = self.determKeyNameFont(keyMapped, charKeyMapped)
            #redéfinition de newText. C'est un peu brutal de changer comme ça la valeur
            #d'un paramètre d'entrée. Mais on a le droit. Ce param est une string, donc
            #c'est modifié localement. Pas de risque de modifier la valeur de l'éventuelle
            #variable string passé en param. (Enfin, à priori).
            newText = keyName

        else:

            #on prend la police de caractère affichant le texte en petit.
            font = self.fontLittle

            #Y'a rien à faire de plus. On prendra directement la valeur du paramètre newText.

        #rafraichissement du texte et de la font du MenuSensitiveText
        self.menuElemKeyActive.changeFontAndText(font, newText)


    def mactNewKeyTyped(self):
        """
        fonction exécutée par le MenuElem enregistreur de touche (self.mOneKeyRecorder),
        lorsque le joueur vient juste d'appuyer sur une touche, et si l'enregistreur
        est en mode enregistrement. Haha

        pré-conditions :
            faut que self.menuElemKeyActive soit différent de None, sinon ça pète.
            Pas pour la même raison que pour la fonction refreshMenuElemKeyActive, mais
            ça péterait quand même. Heureusement, commme je suis un super codeur trop fort,
            je suis sur que cette variable est pas à None au moment où on exécute cette fonction.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #récupération du code et du caractère de la touche, que l'enregistreur vient d'enregistrer
        newKey = self.mOneKeyRecorder.keyRecorded
        newCharKey = self.mOneKeyRecorder.charKeyRecorded

        #Filtrage de certains caractères de touches pourris. (faudra déterminer le nom de
        #la touche à partir du code, et pas du caractère).
        #Voir début du fichier, la description de LIST_KEYCODE_IGNORE_CHAR
        if newKey in LIST_KEYCODE_IGNORE_CHAR:
            newCharKey = ""

        #Si le joueur a voulu enregistrer la touche Esc ou Tab pour le mapping,
        #alors on doit la refuser.
        #Pour la touche Esc, ça se justifie. Y'en a besoin pendant le jeu, pour indiquer qu'on
        #veut quitter le jeu, justement. (Et c'est pas configurable, car j'ai décidé ainsi)
        #Pour la touche Tab, ça se justifie un peu moins. Mais c'est juste moi, j'ai pas
        #envie que la touche de cyclage de focus puisse être utilisée pendant le jeu. Na.
        if newKey not in (pygl.K_TAB, pygl.K_ESCAPE):

            #son de sélection d'un truc : "blululup" !!
            theSoundYargler.playSound(SND_MENU_SELECT)

            #récupération de l'identifiant de la touche qu'on est en train de configurer.
            idKeyActive = self.dicKeyMenuElem[self.menuElemKeyActive]
            #mise à jour du dico de mapping des touches, avec le nouveau code et caractère.
            self.dicKeyMapping[idKeyActive] = (newKey, newCharKey)

        #on arrête l'enregistrement, et on réaffiche le nom de la touche en cours
        #(D'autant plus que ce nom vient peut-être d'être changé)
        self.stopKeyRecording(True)

        #Le joueur a voulu enregistrer, pour le mapping, une touche d'activation de MenuElem
        #(entrée, espace, ...). C'est acceptable. Mais il faut s'en souvenir, car ça veut
        #dire qu'on doit justement pas activer le MenuElem focusé. (voir mactConfigKey).
        if self.mOneKeyRecorder.keyRecorded in LIST_KEY_ACTIVATING_MENU:
            self.justRecordedIsAnActivationKey = True

        return (IHMSG_REDRAW_MENU, )


    def mactQuitOrCancel(self):
        """
        fonction exécuté lorsque le joueur appuie sur Echap.

        Faut, soit quitter le menu, soit désactiver l'enregistrement de touche en cours.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        if self.menuElemKeyActive is not None:

            #on arrête l'enregistrement, et on réaffiche le nom de la touche en cours.
            #Du coup, on teste deux fois que self.menuElemKeyActive est pas None.
            #On vient de le tester juste avant, et on va le retester dans cette fonction.
            #C'est pas super classe, mais c'est pas un drame.
            self.stopKeyRecording(True)

            #on ne quitte pas le menu. On indique juste qu'il faut rafraîchir son affichage
            #sur l'écran principal.
            return (IHMSG_REDRAW_MENU, )

        else:

            #y'a pas d'enregistrement de touche en cours. Faut quitter le menu. Sans oublier
            #de sauvegarder la nouvelle config.

            #L'activitude du son est indiqué dans la valeur litérale de la case à cocher.
            globDataSound = self.mtickSound.literTickValue
            #On construit un dictionnaire de mise à jour des globData, avec une seule
            #valeur dedans. (l'activitude du son, donc)
            dicUpdateSound = { GLOB_DATA_ID_SOUND : globDataSound }

            #mise à jour du son et du nouveau mapping de touche, dans l'archivist.
            param = (self.dicKeyMapping, dicUpdateSound)
            self.archivist.modifyGlobDataAndKeyMapping(*param)

            #et paf, on quitte le menu.
            return (IHMSG_QUIT, )


    def mactResetDefaults(self):
        """
        fonction qui s'exécute quand on appuie sur le bouton pour remettre le mapping de touche
        par défaut

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        #son de sélection d'un truc : "blululup" !!
        theSoundYargler.playSound(SND_MENU_SELECT)

        #on arrête l'enregistrement des touches, (si y'en a un en cours)
        #On réaffiche pas le nom de la touche en cours. Car de toutes façons, faut réafficher
        #tous les noms de touches, et c'est fait juste après.
        self.stopKeyRecording(False)

        #On reprend le mapping detouche par défaut.
        self.dicKeyMapping = dict(DEFAULT_KEY_MAPPING)

        #faut rafraîchir tous les MenuSensitiveText affichant les noms des touches.
        #(une fois de plus, faut que y'ait les mêmes clés dans self.dicKeyMapping et dans
        #self.dicMenuElemKey. Mais ça c'est bon).
        for idKey, (keyMapped, charKeyMapped) in self.dicKeyMapping.items():

            #récupération du MenuSensitiveText affichant le nom de la touche concernée
            menuElem = self.dicMenuElemKey[idKey]
            #détermination du nom de la touche, et de la font à utiliser pour ce nom
            (keyName, font) = self.determKeyNameFont(keyMapped, charKeyMapped)

            #changement de la police de caractère et du texte du MenuSensitiveText
            #TRODO pour plus tard : ordre des param pas homogène. Corriger determKeyNameFont.
            menuElem.changeFontAndText(font, keyName)

        return (IHMSG_REDRAW_MENU, )


    def mactToggleSound(self):
        """
        fonction qui s'exécute quand on clique sur la case à cocher du son on/off
        Faut inverser l'activation/désactivation du son.

        plat-dessert : tuple de message d'ihm, comme d'hab'.
        """

        if self.menuElemKeyActive is not None:

            #on était en train d'enregistrer une touche. Faut arrêter ça.

            #on arrête l'enregistrement, et on réaffiche le nom de la touche en cours.
            #Du coup, on teste deux fois que self.menuElemKeyActive est pas None.
            #(Comme dans la fonction mactQuitOrCancel). Héhé, on teste deux fois un truc,
            #à deux endroits différents. Ca fait plein de fois "deux" !! Super !!
            self.stopKeyRecording(True)

        #Le MenuTick ne fait pas le toggle de tick de sa propre initiative.
        #Faut appeler manuellement la fonction inversant le dessin de la case à cocher.
        self.mtickSound.toggleTick()

        #récupération de la globData indiquant l'activitude du son.
        globDataSoundCurrent = self.mtickSound.literTickValue
        #transmission de l'activitude du son à l'objet qu joue les sons
        theSoundYargler.changeSoundEnablation(globDataSoundCurrent)

        #son de sélection d'un truc : "blululup" !! (le son n'est pas joué si on vient
        #de désactiver les sons juste avant).
        theSoundYargler.playSound(SND_MENU_SELECT)

        return (IHMSG_REDRAW_MENU, )
