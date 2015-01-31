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

date de la derni�re relecture-commentage : 25/02/2011

El�ment de menu qui poutre sa race, parce que c'est une case � cocher

quelques explications :

Bon, � la base, c'est un MenuElem comme un autre. focusable, sensible aux clics, bind�
avec une funcAction.
Le cochage/d�cochage doit �tre indiqu� explicitement, dans la funcAction. Il suffit
d'appeler la fonction toute faite "toggleTick" dans la funcAction. Si on le fait pas, �a
toggle pas. Haha.

Y'a une variable self.boolTickValue. Pas compliqu� : True=coch�. False=d�coch�.

Si on veut, on peut associer (via un dictionnaire), une literalValue � chaque valeur
coch�/d�coch�. La literalValue peut �tre de n'importe quel type, on s'en fout.
(Mais en th�orie, c'est des string, enfin plus exactement des globDataValue.)
La variable self.literTickValue stocke la valeur lit�rale actuelle.

Attention, trip total :
�a �a change plein de trucs. Je fais semblant de taper des trucs pour qu'elle me l�che
la gamine "au conseil th�orie". C'est Pas tout de suite. Pas le choix.
Gratuit. Non que d'alle. J'en sais rien depuis longtemps.  Bordel de merde. Faut que kje c
Je commence �.
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

#distance, en pixel, entre l'image de la case � cocher, et le texte.
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

        entr�e :

            rectPos, font, idTxtStock, text :
                voir description du contructeur de MenuText

            funcAction, clickType, inflateDist :
                voir description du contructeur de MenuSensitiveSquare

            dicTickImage : dictionnaire contenant 2 listes d'images,
                repr�sentant de la case � cochay.
                cl� : bool�en
                valeur : liste de pygame.Surface. Le premier �l�ment de la liste,
                         c'est l'image de la case, soit coch�, soit d�coch� (selon la cl�)
                         Les pygame.Surface suivantes, c'est la m�me image, mais de plus
                         en plus claires. Ca sert quand le MenuElem prend/perd le focus.
                         Il faut le m�me nombre d'images dans les deux listes. Sinon �a risque
                         de faire des trucs zarb parfois.

            dicLiteralFromBool : dictionnaire de correspondance pour les valeurs lit�rales.
                cl� : bool�en.
                valeur : n'importe quoi. Ce sera la valeur lit�rale correspondante.
                Si on passe un dictionnaire vide, ou un dictionnaire ne poss�dant pas les cl�s
                True et False, alors on peut pas utiliser les valeurs lit�rales.
                On n'a acc�s que aux valeurs bool�ennes (self.boolTickValue)

            literalValInit : param non utilis� si on ne d�finit pas dicLiteralFromBool
                Ce param doit valoir l'une des deux valeurs lit�rales.
                Il permet de d�finir, si, au d�part, la case est coch�e ou pas.
                on n'en tient pas compte si il n'est pas �gal � l'une des deux valeurs lit�rales
                d�finies dans le dico.

            boolTickValueInit : valeur bool�enne.
                param non utilis� si on d�finit correctement dicLiteralFromBool et literalValInit,
                Il d�finit la valeur initiale coch�/pas coch� de la case, tout b�tement.

        l'ordre des params est bordelique. C'est � cause des params optionnels.
        Et pis j'ai d�j� dis �a ailleurs, de toutes fa�ons.
        """

        MenuElem.__init__(self)

        #tentative d'activation des valeurs lit�rales, selon ce qui est fourni en param.
        param = (dicLiteralFromBool, literalValInit, boolTickValueInit)
        if not self.activateLiteralValue(*param):

            #�a a fail. On peut pas utiliser les valeurs lit�rales. On fout des valeurs
            #par d�faut dans les trucs qui sont li�s � la gestion de la lit�ralitude.
            #bon, �a c'est la valeur bool�enne en fait
            self.boolTickValue = boolTickValueInit
            #dictionnaire de correspondance val lit�rales <- val bool�ennes
            self.dicLiteralFromBool = {}
            #dictionnaire de correspondance val bool�ennes <- val lit�rales
            #oui j'ai besoin de ces deux dictionnaires, qui sont chacun dans un sens, et
            #je vous emmerde !
            self.dicBoolFromLiteral = {}
            #valeurs lit�rales. Donc du coup y'a rien dedans. Paf.
            self.literTickValue = None

        self.rectPosImg = rectPos
        self.dicTickImage = dicTickImage
        #r�cup�ration de la liste d'image repr�sentant la case coch�e, ou la case pas coch�e,
        #avec les diff�rents degr�s de luminosit�, pour g�rer le focusage.
        self.listImgWithLight = self.dicTickImage[self.boolTickValue]

        #index actuel de luminosit� sur l'image.
        #0 = aucune luminosit�, MenuElem pas focus�. Image normale.
        self.lightIndex = 0
        #direction d'incr�ment de l'index de luminosit�.
        # +1 : focusage en cours. l'image s'illumine.
        # -1 : perte du focus en cours. L'image redevient normale.
        self.lightIndexInc = 0
        #r�cup�ration de l'image en cours. (la normale, donc)
        self.theImg = self.listImgWithLight[self.lightIndex]

        #d�finition de la zone o� se dessine l'image (sans le texte) de la case � cocher.
        #vague incoh�rence mais osef : toutes les images de dicTickImage (quel que soit
        #le coch�/pas coch�, et la luminosit�) doivent avoir la m�me taille. Sinon �a
        #risque de faire des trucs bizarres.
        self.rectDrawZoneImg = getRectDrawZone(self.rectPosImg, self.theImg)

        #initialisation des infos concernant le texte de la case � cocher.
        MenuText.initTextInfo(self, rectPos, font, idTxtStock, text)

        #initialisation de la sensibilit� aux clics. Pour l'instant, la zone de sensibilit�
        #est le "rectangle z�ro" (taille = 0,0). C'est corrig� tout de suite apr�s.
        param = (self, funcAction, RECT_ZERO, clickType, inflateDist)
        MenuSensitiveSquare.initSensiInterface(*param)

        #Voil�. L�, on d�finit la zone compl�te de dessin (image + texte), et la zone
        #de sensibilit� aux clics qui en d�combe. (Blague sur "d�combe" d�j� faite ailleurs).
        self.refreshStimAndDrawZones()


    def refreshStimAndDrawZones(self):
        """
        donc, comme je viens de dire : d�finition des zones de dessins et de sensibilit�,
        en tenant compte de l'image et du texte de la case � cocher.

        On d�finit �galement self.rectPosText : position et taille du texte.

        Le texte est centr� verticalement par rapport au milieu vertical de l'image
        de la case � cocher.
        Le texte est plac� � droite de la case � cocher. Il y a un espace de X_SPACE_IMG_TEXT
        pixels entre le c�t� droit de la case � cocher et le c�t� gauche du texte.
        """

        #On chope la taille du rectangle englobant le texte. rectPosText = (0, 0, wText, hText)
        textSize = self.theLamoche.image.get_rect().size
        self.rectPosText = pyRectTuple(tupleSize=textSize)

        #on d�finit les coordonn�es du texte. pour que rectPosText = (x, y, wText, hText)
        #d�finition de Y. Centrage sur le centre de l'image de la case � cocher.
        self.rectPosText.centery = self.rectDrawZoneImg.centery
        #d�finition de X. Un peu � droite de l'image de la case � cocher
        self.rectPosText.left = self.rectDrawZoneImg.right + X_SPACE_IMG_TEXT

        #d�fitnion de self.rectDrawZone. Ca doit �tre un gros rectangle englobant
        #la zone de dessin du texte (self.rectPosText) et celle de l'image (self.rectDrawZoneImg)
        self.rectDrawZone = pygame.Rect(self.rectDrawZoneImg)
        self.rectDrawZone.union_ip(self.rectPosText)

        #d�finition de la zone de sensibilit� aux clics, en fonction de la zone de dessin globale,
        #(et de la marge self.inflateDist)
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self)


    def activateLiteralValue(self, dicLiteralFromBool, literalValInit,
                             boolTickValueInit):
        """
        fonction permettant d'activer (si c'est possible) les valeurs lit�rales associ�es
        aux valeurs bool�ennes de coch� / pas coch�.

        entr�es :
            dicLiteralFromBool, literalValInit, boolTickValueInit :
            voir fonction __init__. C'est les m�me params.

        plat-dessert : bool�en. Indique si on a r�ussi � activer les valeurs lit�rales ou pas.
        """

        #v�rification qu'il y a les bonnes cl�s dans le dictionnaire val lit�rales <- bool�en.
        #captain obvious : il faut donc avoir les cl�s True et False.

        if True not in dicLiteralFromBool:
            return False

        if False not in dicLiteralFromBool:
            return False

        #cr�ation du dico inverse bool�en <- val lit�rales. Yeaaaahh !!

        dicBoolFromLiteral = {}

        for boolTickVal, literalTickVal in dicLiteralFromBool.items():
            dicBoolFromLiteral[literalTickVal] = boolTickVal

        #enregistrement des deux dictionnaires dedans la classe.
        self.dicLiteralFromBool = dicLiteralFromBool
        self.dicBoolFromLiteral = dicBoolFromLiteral

        #initialiation de self.boolTickValue et self.literTickValue.
        if literalValInit not in dicBoolFromLiteral:
            #la valeur lit�rale indiqu�e comme valeur initiale n'est pas dans le dico
            #des valeurs lit�rales. Zut alors. On initialise les deux valeurs en se
            #basant sur boolTickValueInit
            self.boolTickValue = boolTickValueInit
            self.literTickValue = self.dicLiteralFromBool[self.boolTickValue]
        else:
            #la valeur lit�rale indiqu�e comme valeur initiale est dans le dico. Youpi.
            #On la prend, et on en d�duit la valeur bool�enne initiale.
            self.literTickValue = literalValInit
            self.boolTickValue = dicBoolFromLiteral[literalValInit]

        #C'est OK, on a pu activer les valeurs lit�rales.
        return True


    def toggleTick(self):
        """
        inverse l'�tat coch� / pas coch�.
        Met � jour l'image, la valeur bool�enne et la valeur lit�rale (si elles sont activ�es)

        plat-dessert : bool�en. Nouvel valeur bool�enne de la case � cocher.
                       (on s'en fout un peu de r�cup�rer �a, mais �a peut �tre cool).
        """

        self.boolTickValue = not self.boolTickValue
        #mise � jour de la liste d'images � afficher, en fonction du nouvel �tat.
        self.listImgWithLight = self.dicTickImage[self.boolTickValue]
        #mise � jour de l'image en cours que c'est celle qui s'affiche en ce moment m�me.
        self.theImg = self.listImgWithLight[self.lightIndex]

        #mise � jour de la valeur lit�rale, si elles sont activ�s.
        if self.dicBoolFromLiteral != {}:
            #on d�duit la nouvelle valeur lit�rale de la nouvelle valeur bool�ennne.
            self.literTickValue = self.dicLiteralFromBool[self.boolTickValue]

        return self.boolTickValue


    def draw(self, surfaceDest):
        """
        dessin de l'�l�ment de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #et hop, on blite l'image en cours, qui a �t� r�cup�r�e de la liste d'image en cours.
        surfaceDest.blit(self.theImg, self.rectPosImg)
        #et hop, on blite le texte.
        surfaceDest.blit(self.theLamoche.image, self.rectPosText)


    def changeLanguage(self):
        """
        changement du langage. (voir descrip dans MenuElem)

        c'est plus ou moins un copier-coller du MenuText.
        Je factorise pas, car �a vaut pas trop le coup.
        """
        if self.idTxtStock is None:
            #le texte ne d�pend pas du langage. Donc on se casse, y'a rien � faire.
            return

        #Sinon faut bosser un peu quand m�me. On r�actualise le texte du lamoche,
        #en r�cup�rant la cha�ne de caract�re dans le txtStock. (Il va en donner une diff�rente,
        #car il aura chang� sa valeur de langage en interne)
        newText = txtStock.getText(self.idTxtStock)
        self.theLamoche.updateAttrib(text=newText)

        #comme le texte a chang�, il faut red�finir la zone dans laquelle l'�l�ment s'affiche,
        #ainsi que la zone de sensibilit� aux clics. Sans oublier qu'il y a une image ET un texte.
        #Bon, y'a une fonction qui fait tout �a toute seule. Youpi.
        self.refreshStimAndDrawZones()