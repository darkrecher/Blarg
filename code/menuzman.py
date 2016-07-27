#/usr/bin/env python
# -*- coding: utf-8 -*-
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

date de la dernière relecture-commentage : 06/03/2011

menu affichant le manuel du jeu.
"MMmmmhhh ... Manouel ! Tou aime é lé cochoné. Tou aime é lé contact !" (Désolé)
"""

import pygame

from common import (pyRect, addThings, IHMSG_REDRAW_MENU, IHMSG_QUIT,
                    KEY_DIR_UP, KEY_DIR_DOWN, KEY_DIR_RIGHT, KEY_DIR_LEFT,
                    KEY_FIRE, KEY_RELOAD)

from menucomn import IMG_MANUAL, manyQuit
from lamoche  import ALIGN_CENTER_X
from menutxt  import MenuText
from menuimg  import MenuImage
from txtstock import txtStock
from menumng  import MenuManager

#position de la grosse image affichant le manuel : les différentes actions possibles du héros,
#avec les dessins des touches.
POS_IMG_MANUAL = pyRect(50, 50)

#Identifiants et positions des textes du manuel (y'a les noms des actions du héros)
#les coordonnées sont par rapport à l'image du manuel. Pas par rapport au haut-gauche de l'écran.
LIST_MENU_TEXT_INFO_MANUAL = (
    (txtStock.MANUAL_MOVE,   ( 15,  35)  ),
    (txtStock.MANUAL_FIRE,   ( 15, 100)  ),
    (txtStock.MANUAL_RELOAD, ( 15, 160)  ),
)

#identifiants des touches, et positions du texte donnant le nom de la touche.
#Coordonnées définies par rapport à l'image du manuel, et indiquant le point milieu-haut
#du dessin de la touche. Ca veut dire qu'il faudra centrer horizontalement le texte.
LIST_POS_KEY_NAME = (
    (KEY_DIR_UP,    (235,  14)),
    (KEY_DIR_LEFT,  (200,  45)),
    (KEY_DIR_DOWN,  (235,  45)),
    (KEY_DIR_RIGHT, (269,  45)),
    (KEY_FIRE,      (234,  99)),
    (KEY_RELOAD,    (234, 158)),
)



class MenuManagerManual(MenuManager):
    """
    menu pour afficher le manuel du jeu.
    """

    def __init__(self, surfaceDest, dicImg, fontDefault, fontLittle,
                 archivist):
        """
        constructeur. (thx captain obvious)

        entrée :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault, fontLittle : objets pygame.font.Font. les polices de caractères
                pour afficher le texte. Y'a la font par défaut, qu'on utilise partout,
                et la font pour afficher du texte en petit.

            archivist : objet de la classe époney-ime, qui gère le fichier de sauvegarde
                de la config et des high scores. C'est là dedans que y'a la config
                des touches.

        Juste pour info : la classe MenuManagerManual ne demande pas de modif du fichier de
        sauvegarde. L'objet archivist passé en param lui sert uniquement à récupérer, en
        lecture, le mapping des touches actuels.
        """

        MenuManager.__init__(self, surfaceDest, dicImg)

        #initialisation d'un tas de trucs. J'ai mis tout ça dans la fonction initCommonStuff,
        #Pour pouvoir factoriser plus facilement le code avec celui du MenuManagerConfig.
        param = (fontDefault, fontLittle,
                 archivist, LIST_MENU_TEXT_INFO_MANUAL)

        self.initCommonStuff(*param)

        #dictionnaire des menuElem indiquant la config des touches.
        # clé : identifiant de touche. (KEY_DIR_UP, KEY_FIRE, KEY_RELOAD, ...)
        # valeur : menuElem de type MenuText, affichant le nom de la touche mappée.
        #Attention, c'est bien un MenuText. Dans la classe MenuManagerConfig, il y a aussi
        #un dictionnaire dicMenuElemKey. Mais il contient des objets MenuSensitiveText.
        self.dicMenuElemKey = {}

        #liste des MenuText qu'on trouve dans le dico dicMenuElemKey. J'en ai besoin juste
        #vite fait provisoirement. Sinon vous pensez bien que je m'amuserais pas à avoir
        #un dictionnaire et une liste stockant les mêmes choses.
        listMenuTextKey = []

        #création des MenuText et rangement dans self.dicMenuElemKey et listMenuTextKey
        for idKey, coord in LIST_POS_KEY_NAME:

            #calcul des coordonnées absolues du MenuText (par rapport au haut-gauche de l'écran)
            rectCoord = POS_IMG_MANUAL.move(coord)

            #Je ne définis ni le param idTxtStock, ni le param text.
            #ça fait un MenuText affichant un texte vide. On le définira correctement plus tard.
            menuElem = MenuText(rectCoord, fontDefault, alignX=ALIGN_CENTER_X)

            listMenuTextKey.append(menuElem)
            self.dicMenuElemKey[idKey] = menuElem

        #Rassemblement de tous les MenuElem du menu, pour les mettre dans une grosse liste.
        #on commence par faire une liste de sous-liste, parce qu'on fait avec ce qu'on a.
        #tiens c'est marrant y'a une parenthèse fermante à la fin des 3 lignes,
        #mais c'est jamais pour signifier la même chose. Woah, bizarre.
        lilistOfMenuElem = (
            (self.mimgManual, manyQuit),
            tuple(listMenuTextKey),
            tuple(self.listMenuText))

        #et maintenant, on fait une grande liste "aplatie", en concaténant toutes les sous-liste.
        self.listMenuElem = addThings(*lilistOfMenuElem)

        self.initFocusCyclingInfo()


    def initCommonStuff(self, fontDefault, fontLittle,
                        archivist, listMenuTextInfo):
        """
        Initialise les trucs communs au MenuManagerManual et MenuManagerConfig.
        Rien à voir : j'ai un prof qui disait : "toilettage initial" à propos
        d'un algo de calcul approché.

        entrées :
            fontDefault, fontLittle, archivist : voir constructeur de cette classe.

            listMenuTextInfo : liste contenant les infos pour créer les MenuText de ce menu.
                Y'a pas les MenuText affichant les noms des touches. Mais y'a tout les autres.
                La liste doit contenir des tuples de 2 éléments :
                 - identifiants du texte à afficher. (Ces identifiants sont dans txtStock.py)
                 - sous-tuple de 2 int. Coordonnées de la position du texte, par rapport à
                   la grosse image géante affichant le manuel.

        plat-dessert :
            Rien. Mais on initialise les variables self.listMenuText et self.mimgManual.
        """

        self.archivist = archivist
        self.fontDefault = fontDefault
        self.fontLittle = fontLittle

        # --- création des éléments MenuText statiques ---

        self.listMenuText = []

        for idTxtStock, coord in listMenuTextInfo:

            #calcul des coordonnées absolues (décalage image du manuel -> écran)
            rectCoord = POS_IMG_MANUAL.move(coord)
            menuElem = MenuText(rectCoord, fontDefault, idTxtStock)
            self.listMenuText.append(menuElem)

        # --- création des images du menu (bon y'en a qu'une) ---

        #C'est la grosse image géante affichant le manuel du jeu
        imgManual = self.dicImg[IMG_MANUAL]
        self.mimgManual = MenuImage(POS_IMG_MANUAL, imgManual)


    def determKeyNameFont(self, keyMapped, charKeyMapped):
        """
        détermine le nom de la touche à afficher, et la police de caractère à
        utiliser pour afficher ce nom.

        entrées :
            keyMapped : int. Code de la touche dont il faut afficher le nom.
            charKeyMapped : chaîne de caractère avec le nom de la touche,
                chopé de puis le event.unicode. Y'a déjà eu le filtrage sur le charKeyMapped,
                (les touches renvoyant un caractère non imprimables).
                Ce filtrage est effectuée au moment de la saisie des touches,
                dans la fonction MenuManagerConfig.mactNewKeyTyped
                A vérifier, mais sur Mac, le filtrage il risque de foirer.

        plat-dessert : tuple de 2 éléments.
             - keyName : string plus ou moins unicode. Le nom de la touche.
             - keyFont : font à utiliser pour afficher ce nom.
                         (le texte est plus petit si le nom est long.)
        """

        if charKeyMapped != "":
            #La touche a renvoyé un caractère, et il n'a pas été filtré. On peut donc
            #utiliser ce caractère pour définir le nom de la touche. Cette utilisation prioritaire
            #du caractère renvoyé permet de s'affranchir des conneries de différence
            #entre claviers qwerty, azerty, etc...
            keyName = charKeyMapped
        else:
            #la touche n'a pas de caractère. On utilise donc par défaut le nom de la touche
            keyName = pygame.key.name(keyMapped)

        if len(keyName) == 1:
            #Le nom de la touche n'a qu'un caractère. C'est peut être une lettre de l'alphabet.
            #Dans ce cas, on l'écrit en majuscule. C'est plus cool.
            #(Si c'est pas une lettre, la fonction upper() ne modifie pas la valeur.
            keyName = keyName.upper()
            #Comme y'a qu'un caractère à afficher (lettre ou pas lettre), on peut utiliser
            #la police de caractère par défaut. Qui affichera en assez gros.
            keyFont = self.fontDefault
        else:
            #Le nom de la touche a plusieurs caractères. On tronque un peu, sinon ça
            #dépasse vraiment de chaque côté du pauvre petit dessin de la touche.
            keyName = keyName[:10]
            #on utilise la police de caractère écrites en petits. Pour limiter ces dépassements.
            keyFont = self.fontLittle

        return keyName, keyFont


    def startMenu(self):
        """
        fonction qui s'exécute au début de l'activation du menu
        (voir description de la fonction dans la classe-mère)
        """

        #Il faut réinitialiser les textes des noms des touches à chaque activation du menu,
        #car si le joueur a modifié la config des touches, ces textes ont changés.
        self.initTextOfMenuElemKey()


    def initTextOfMenuElemKey(self):
        """
        modifie le texte et la font des MenuElem contenus dans self.dicMenuElemKey,
        afin qu'ils affichent les noms des touches en accord avec la config de touches actuelle.

        self.dicMenuElemKey peut contenir des MenuText, ou des MenuSensitiveText,
        cette fonction fonctionnera (haha) dans les deux cas.
        """

        #On récupère le mapping de touches depuis la "source". (l'archivist)
        #Comme ça on est sûr d'avoir le mapping actuel.
        self.dicKeyMapping = dict(self.archivist.dicKeyMapping)

        #on parcourt le dictionnaire des MenuElem affichant les noms des touches,
        #pour chacun d'eux, on récupère la config de la touche dans le mapping,
        #on en déduit le nom et on le réactualise dans le MenuElem.
        #
        #Faut donc que y'ait les mêmes clés entre self.dicMenuElemKey et dicKeyMapping,
        #sinon ça risque de péter. Mais moi je fais gaffe alors ça pète pas.
        #Les clés, c'est les identifiants de touches. (KEY_DIR_UP, KEY_FIRE, ...)
        for idKey, menuText in self.dicMenuElemKey.items():

            #récupération du code et du caractère de la touche.
            keyMapped, charKeyMapped = self.dicKeyMapping[idKey]
            #détermination du nom de la touche (et de la font à utiliser pour l'afficher)
            (keyName, font) = self.determKeyNameFont(keyMapped, charKeyMapped)

            #changement de la police de caractère et du texte du MenuElem
            menuText.changeFontAndText(font, keyName)
