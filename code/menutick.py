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

date de la dernière relecture-commentage : 25/02/2011

Elément de menu qui poutre sa race, parce que c'est une case à cocher

quelques explications :

Bon, à la base, c'est un MenuElem comme un autre. focusable, sensible aux clics, bindé
avec une funcAction.
Le cochage/décochage doit être indiqué explicitement, dans la funcAction. Il suffit
d'appeler la fonction toute faite "toggleTick" dans la funcAction. Si on le fait pas, ça
toggle pas. Haha.

Y'a une variable self.boolTickValue. Pas compliqué : True=coché. False=décoché.

Si on veut, on peut associer (via un dictionnaire), une literalValue à chaque valeur
coché/décoché. La literalValue peut être de n'importe quel type, on s'en fout.
(Mais en théorie, c'est des string, enfin plus exactement des globDataValue.)
La variable self.literTickValue stocke la valeur litérale actuelle.

Attention, trip total :
ça ça change plein de trucs. Je fais semblant de taper des trucs pour qu'elle me lâche
la gamine "au conseil théorie". C'est Pas tout de suite. Pas le choix.
Gratuit. Non que d'alle. J'en sais rien depuis longtemps.  Bordel de merde. Faut que kje c
Je commence à.
end of trip total

"""

import pygame

from common import (pyRect, pyRectTuple, getRectDrawZone,
                    IHMSG_ELEM_CLICKED, IHMSG_REDRAW_MENU, IHMSG_VOID, )
# IHMSG_ELEM_CLICKED, IHMSG_REDRAW_MENU, IHMSG_VOID useless ?

from menuelem import MenuElem
from menusesq import MenuSensitiveSquare, MOUSE_DOWN, RECT_ZERO
from menuseim import MenuSensitiveImage
from menutxt  import MenuText
from txtstock import txtStock

#distance, en pixel, entre l'image de la case à cocher, et le texte.
X_SPACE_IMG_TEXT = 5



class MenuSensitiveTick(MenuSensitiveImage, MenuText):
    """
    texte qu'on clique dessus, ou pas
    """

    def __init__(self, rectPos, font, funcAction, dicTickImage,
                 idTxtStock=None, text="",
                 clickType=MOUSE_DOWN, inflateDist=5,
                 dicLiteralFromBool={}, literalValInit=None,
                 boolTickValueInit=False):
        """
        constructeur. (thx captain obvious)

        entrée :

            rectPos, font, idTxtStock, text :
                voir description du contructeur de MenuText

            funcAction, clickType, inflateDist :
                voir description du contructeur de MenuSensitiveSquare

            dicTickImage : dictionnaire contenant 2 listes d'images,
                représentant de la case à cochay.
                clé : booléen
                valeur : liste de pygame.Surface. Le premier élément de la liste,
                         c'est l'image de la case, soit coché, soit décoché (selon la clé)
                         Les pygame.Surface suivantes, c'est la même image, mais de plus
                         en plus claires. Ca sert quand le MenuElem prend/perd le focus.
                         Il faut le même nombre d'images dans les deux listes. Sinon ça risque
                         de faire des trucs zarb parfois.

            dicLiteralFromBool : dictionnaire de correspondance pour les valeurs litérales.
                clé : booléen.
                valeur : n'importe quoi. Ce sera la valeur litérale correspondante.
                Si on passe un dictionnaire vide, ou un dictionnaire ne possédant pas les clés
                True et False, alors on peut pas utiliser les valeurs litérales.
                On n'a accès que aux valeurs booléennes (self.boolTickValue)

            literalValInit : param non utilisé si on ne définit pas dicLiteralFromBool
                Ce param doit valoir l'une des deux valeurs litérales.
                Il permet de définir, si, au départ, la case est cochée ou pas.
                on n'en tient pas compte si il n'est pas égal à l'une des deux valeurs litérales
                définies dans le dico.

            boolTickValueInit : valeur booléenne.
                param non utilisé si on définit correctement dicLiteralFromBool et literalValInit,
                Il définit la valeur initiale coché/pas coché de la case, tout bêtement.

        l'ordre des params est bordelique. C'est à cause des params optionnels.
        Et pis j'ai déjà dis ça ailleurs, de toutes façons.
        """

        MenuElem.__init__(self)

        #tentative d'activation des valeurs litérales, selon ce qui est fourni en param.
        param = (dicLiteralFromBool, literalValInit, boolTickValueInit)
        if not self.activateLiteralValue(*param):

            #ça a fail. On peut pas utiliser les valeurs litérales. On fout des valeurs
            #par défaut dans les trucs qui sont liés à la gestion de la litéralitude.
            #bon, ça c'est la valeur booléenne en fait
            self.boolTickValue = boolTickValueInit
            #dictionnaire de correspondance val litérales <- val booléennes
            self.dicLiteralFromBool = {}
            #dictionnaire de correspondance val booléennes <- val litérales
            #oui j'ai besoin de ces deux dictionnaires, qui sont chacun dans un sens, et
            #je vous emmerde !
            self.dicBoolFromLiteral = {}
            #valeurs litérales. Donc du coup y'a rien dedans. Paf.
            self.literTickValue = None

        self.rectPosImg = rectPos
        self.dicTickImage = dicTickImage
        #récupération de la liste d'image représentant la case cochée, ou la case pas cochée,
        #avec les différents degrés de luminosité, pour gérer le focusage.
        self.listImgWithLight = self.dicTickImage[self.boolTickValue]

        #index actuel de luminosité sur l'image.
        #0 = aucune luminosité, MenuElem pas focusé. Image normale.
        self.lightIndex = 0
        #direction d'incrément de l'index de luminosité.
        # +1 : focusage en cours. l'image s'illumine.
        # -1 : perte du focus en cours. L'image redevient normale.
        self.lightIndexInc = 0
        #récupération de l'image en cours. (la normale, donc)
        self.theImg = self.listImgWithLight[self.lightIndex]

        #définition de la zone où se dessine l'image (sans le texte) de la case à cocher.
        #vague incohérence mais osef : toutes les images de dicTickImage (quel que soit
        #le coché/pas coché, et la luminosité) doivent avoir la même taille. Sinon ça
        #risque de faire des trucs bizarres.
        self.rectDrawZoneImg = getRectDrawZone(self.rectPosImg, self.theImg)

        #initialisation des infos concernant le texte de la case à cocher.
        MenuText.initTextInfo(self, rectPos, font, idTxtStock, text)

        #initialisation de la sensibilité aux clics. Pour l'instant, la zone de sensibilité
        #est le "rectangle zéro" (taille = 0,0). C'est corrigé tout de suite après.
        param = (self, funcAction, RECT_ZERO, clickType, inflateDist)
        MenuSensitiveSquare.initSensiInterface(*param)

        #Voilà. Là, on définit la zone complète de dessin (image + texte), et la zone
        #de sensibilité aux clics qui en décombe. (Blague sur "décombe" déjà faite ailleurs).
        self.refreshStimAndDrawZones()


    def refreshStimAndDrawZones(self):
        """
        donc, comme je viens de dire : définition des zones de dessins et de sensibilité,
        en tenant compte de l'image et du texte de la case à cocher.

        On définit également self.rectPosText : position et taille du texte.

        Le texte est centré verticalement par rapport au milieu vertical de l'image
        de la case à cocher.
        Le texte est placé à droite de la case à cocher. Il y a un espace de X_SPACE_IMG_TEXT
        pixels entre le côté droit de la case à cocher et le côté gauche du texte.
        """

        #On chope la taille du rectangle englobant le texte. rectPosText = (0, 0, wText, hText)
        textSize = self.theLamoche.image.get_rect().size
        self.rectPosText = pyRectTuple(tupleSize=textSize)

        #on définit les coordonnées du texte. pour que rectPosText = (x, y, wText, hText)
        #définition de Y. Centrage sur le centre de l'image de la case à cocher.
        self.rectPosText.centery = self.rectDrawZoneImg.centery
        #définition de X. Un peu à droite de l'image de la case à cocher
        self.rectPosText.left = self.rectDrawZoneImg.right + X_SPACE_IMG_TEXT

        #défitnion de self.rectDrawZone. Ca doit être un gros rectangle englobant
        #la zone de dessin du texte (self.rectPosText) et celle de l'image (self.rectDrawZoneImg)
        self.rectDrawZone = pygame.Rect(self.rectDrawZoneImg)
        self.rectDrawZone.union_ip(self.rectPosText)

        #définition de la zone de sensibilité aux clics, en fonction de la zone de dessin globale,
        #(et de la marge self.inflateDist)
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self)


    def activateLiteralValue(self, dicLiteralFromBool, literalValInit,
                             boolTickValueInit):
        """
        fonction permettant d'activer (si c'est possible) les valeurs litérales associées
        aux valeurs booléennes de coché / pas coché.

        entrées :
            dicLiteralFromBool, literalValInit, boolTickValueInit :
            voir fonction __init__. C'est les même params.

        plat-dessert : booléen. Indique si on a réussi à activer les valeurs litérales ou pas.
        """

        #vérification qu'il y a les bonnes clés dans le dictionnaire val litérales <- booléen.
        #captain obvious : il faut donc avoir les clés True et False.

        if True not in dicLiteralFromBool:
            return False

        if False not in dicLiteralFromBool:
            return False

        #création du dico inverse booléen <- val litérales. Yeaaaahh !!

        dicBoolFromLiteral = {}

        for boolTickVal, literalTickVal in dicLiteralFromBool.items():
            dicBoolFromLiteral[literalTickVal] = boolTickVal

        #enregistrement des deux dictionnaires dedans la classe.
        self.dicLiteralFromBool = dicLiteralFromBool
        self.dicBoolFromLiteral = dicBoolFromLiteral

        #initialiation de self.boolTickValue et self.literTickValue.
        if literalValInit not in dicBoolFromLiteral:
            #la valeur litérale indiquée comme valeur initiale n'est pas dans le dico
            #des valeurs litérales. Zut alors. On initialise les deux valeurs en se
            #basant sur boolTickValueInit
            self.boolTickValue = boolTickValueInit
            self.literTickValue = self.dicLiteralFromBool[self.boolTickValue]
        else:
            #la valeur litérale indiquée comme valeur initiale est dans le dico. Youpi.
            #On la prend, et on en déduit la valeur booléenne initiale.
            self.literTickValue = literalValInit
            self.boolTickValue = dicBoolFromLiteral[literalValInit]

        #C'est OK, on a pu activer les valeurs litérales.
        return True


    def toggleTick(self):
        """
        inverse l'état coché / pas coché.
        Met à jour l'image, la valeur booléenne et la valeur litérale (si elles sont activées)

        plat-dessert : booléen. Nouvel valeur booléenne de la case à cocher.
                       (on s'en fout un peu de récupérer ça, mais ça peut être cool).
        """

        self.boolTickValue = not self.boolTickValue
        #mise à jour de la liste d'images à afficher, en fonction du nouvel état.
        self.listImgWithLight = self.dicTickImage[self.boolTickValue]
        #mise à jour de l'image en cours que c'est celle qui s'affiche en ce moment même.
        self.theImg = self.listImgWithLight[self.lightIndex]

        #mise à jour de la valeur litérale, si elles sont activés.
        if self.dicBoolFromLiteral != {}:
            #on déduit la nouvelle valeur litérale de la nouvelle valeur booléennne.
            self.literTickValue = self.dicLiteralFromBool[self.boolTickValue]

        return self.boolTickValue


    def draw(self, surfaceDest):
        """
        dessin de l'élément de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #et hop, on blite l'image en cours, qui a été récupérée de la liste d'image en cours.
        surfaceDest.blit(self.theImg, self.rectPosImg)
        #et hop, on blite le texte.
        surfaceDest.blit(self.theLamoche.image, self.rectPosText)


    def changeLanguage(self):
        """
        changement du langage. (voir descrip dans MenuElem)

        c'est plus ou moins un copier-coller du MenuText.
        Je factorise pas, car ça vaut pas trop le coup.
        """
        if self.idTxtStock is None:
            #le texte ne dépend pas du langage. Donc on se casse, y'a rien à faire.
            return

        #Sinon faut bosser un peu quand même. On réactualise le texte du lamoche,
        #en récupérant la chaîne de caractère dans le txtStock. (Il va en donner une différente,
        #car il aura changé sa valeur de langage en interne)
        newText = txtStock.getText(self.idTxtStock)
        self.theLamoche.updateAttrib(text=newText)

        #comme le texte a changé, il faut redéfinir la zone dans laquelle l'élément s'affiche,
        #ainsi que la zone de sensibilité aux clics. Sans oublier qu'il y a une image ET un texte.
        #Bon, y'a une fonction qui fait tout ça toute seule. Youpi.
        self.refreshStimAndDrawZones()