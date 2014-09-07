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

date de la derni�re relecture-commentage : 22/02/2011

El�ment de menu qui poutre sa race, parce que non seulement il affiche du texte comme un
ouf malade, mais en plus, il est focusable, et en plus-plus, il r�agit aux clics.
"""

import pygame

from common import pyRect
from menuelem import MenuElem
from lamoche  import ALIGN_LEFT, ALIGN_TOP
from menusesq import MenuSensitiveSquare, MOUSE_DOWN, RECT_ZERO
from menutxt  import MenuText


#liste d'une composante de couleur (R, V ou B, c'est comme on veut), permettant
#de faire un d�grad� : (composante max) -> (composante � 0) -> (re-composantee max)
#
#�a tombe pas tout � fait juste au niveau des valeurs des couleurs, mais osef.
#C'est � cause des range.
#On commence � 255, 239, 223, etc... on va � 0. Et quand on remonte vers le max, �a
#reprend pas les m�mes valeurs, c'est d�cal� de 1. On fait ..., 224, 240
#C'est bizarre, mais on s'en fout compl�tement. Ca a pas besoin d'�tre exact.
GLOW_TEXT_COMPONENT_LIST = tuple(range(255, 0, -16) + range(0, 255, 16))

#liste de tuple de couleur RVB utilis� pour faire le glow des menuElem de type Texte,
#quand ils ont le focus. C'est un d�grad� blanc -> bleu -> blanc
GLOW_TEXT_COLOR_LIST = tuple( [ (component, component, 255)
                                for component in GLOW_TEXT_COMPONENT_LIST
                              ]
                            )



#h�ritage multiple qu'on est oblig� de pr�ciser, pour brancher les fonctions
#qu'on veut. Mais sinon moi je fait pas de vrai h�ritage multiple. Car c'est zarb
class MenuSensitiveText(MenuSensitiveSquare, MenuText):
    """
    texte qu'on clique dessus, ou pas
    """

    def __init__(self, rectPos, font, funcAction, idTxtStock=None, text="",
                 clickType=MOUSE_DOWN, inflateDist=5,
                 antialias=False, color=(255, 255, 255), background=None,
                 alignX=ALIGN_LEFT, alignY=ALIGN_TOP):
        """
        constructeur. (thx captain obvious)

        Au niveau de l'ordre des params, j'ai essay� de faire de mon mieux pour avoir quelque
        chose de logique, homog�ne par rapport aux autres classes, et pratique au niveau
        des valeurs par d�faut. Eh bien je garantis pas que j'y suis arriv�. Et pis j'm'en fous.

        entr�e :
            rectPos, font, idTxtStock, text :
                voir description du contructeur de MenuText

            funcAction, clickType, inflateDist :
                voir description du contructeur de MenuSensitiveSquare

            antialias, color, background, alignX, alignY :
                voir description du constructeur de Lamoche
        """

        #l�, on peut appeler le constructeur du MenuText, car �a fait exactement la m�me
        #chose. (Et apr�s, on fait des trucs en plus. Mais faut faire gaffe quand on
        #fait �a. A la moindre diff�rence, vaut mieux factoriser le code avec des fonctions,
        #plut�t qu'avec des constructeurs.
        MenuText.__init__(self, rectPos, font, idTxtStock, text,
                          antialias, color, background, alignX, alignY)

        #initialisation de la zone sensible du menuElem, que la souris r�agit dessus.
        param = (self, funcAction, RECT_ZERO, clickType, inflateDist)
        MenuSensitiveSquare.initSensiInterface(*param)

        #et hop, apr�s l'initialisation, la vraie d�finition de la zone de o� qu'elle est.
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self)

        # -- d�finition des variables utilis�es pour faire glower le texte quand il a le focus --

        #index pointant sur la couleur courante du texte, dans la liste des couleurs du d�grad�
        #qui fait le glow. L'index 0 correspond � la couleur normale (blanche, comme dirait
        #Coluche). C'est cette couleur qui est utilis�e quand l'�l�ment n'est pas focus�.
        self.glowColorIndex = 0

        #step d'incr�mentaion dans la liste des couleurs. (C'est -1 ou +1, pour reculer
        #ou avancer dans la liste.
        self.glowColorIndexInc = +1

        self.glowColorList = GLOW_TEXT_COLOR_LIST


    def changeLanguage(self):
        """
        on est oblig� de linker explicitement la fonction vers le MenuText
        (l'une des deux mother-class de cette classe).

        J'ai bien indiqu� un h�ritage multiple. Mais �a suffit pas.
        Si j'ai bien compris d'o� vient le probl�me, c'est que le MenuSensitiveSquare
        (que j'h�rite en premier), a lui aussi sa fonction changeLanguage.
        (Elle est vide, et elle vient du MenuElem, mais elle existe).
        Et c'est cette fonction qui est prise en priorit�. Bon, �a se d�fend comme argument.

        Du coup, je transmet l'appel vers la fonction que je veux vraiment ex�cuter.
        C'est bof, mais je vois pas d'autres solution
        """
        MenuText.changeLanguage(self)

        #Alors l� on pourrait croire qu'il faut appeler la fonction defineStimZoneFromDrawZone,
        #Vu que le changeLanguage change le texte, donc faut modifier cascadalement la zone
        #de sensibilit� au clics. Mais en fait y'a pas besoin. Le changeLanguage du MenuText
        #appelle la fonction changeFontAndText. Et l'astuce, c'est que en vrai,
        #�a appelle la fonction changeFontAndText du MenuSensitiveText ! (Puisque l� on est
        #dedans le MenuSensitiveText). Et dans ce changeFontAndText, j'ai mis un appel
        #� defineStimZoneFromDrawZone. (Voir juste en dessous).
        #H�h� c'est quand m�me la classe ce truc.


    def changeFontAndText(self, newFont=None, newText=None):
        """
        Changer le texte et/ou la font, et modifier en cons�quence la zone rectangulaire dans
        laquelle cet �l�ment s'affiche, ainsi que la zone rectangulaire de sensibilit� aux clics.

        entr�es :
            (voir description de la fonction dans la classe MenuElem, c'est les m�mes)
        """
        MenuText.changeFontAndText(self, newFont, newText)

        #Modification de la zone de sensibilit� aux clics en fonction de la zone de dessin.
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self)


    def update(self):
        """
        (voir description de la fonction dans MenuElem)

        Si on est focus�, il faut redessiner � chaque cycle, pour faire glower le texte.
        Si on vient de paumer le focus, il faut continuer de redessiner, car on
        remet progressivement la couleur du texte � la couleur normale (celle d'index 0).
        Si on a pas le focus, et qu'on est sur la couleur normale, rien � faire.
        """

        ihmsgInfo = MenuSensitiveSquare.update(self)

        #Si on a pas le focus, et que le texte a la couleur normale, y'a rien � faire.
        #on fixe mustBeRefreshed � False, comme �a l'�l�ment ne se r�affichera pas.
        #Ca fonctionne comme il faut car l'update est fait avant le draw. Donc si, arriv�
        #� cet endroit du code, l'index de couleur est 0, c'est bien la couleur
        #r�ellement affich�e � l'�cran. (Y'a pas d'histoer � la con que il faudrait
        #r�afficher une derni�re petite fois avant d'arr�ter. Tralala)
        if not self.focusOn and self.glowColorIndex == 0:
            self.mustBeRefreshed = False
            return ihmsgInfo

        #on a le focus, ou pas. (osef en fait). Ce dont on est s�r, c'est qu'il faut
        #faire glower le texte. Donc on avance l'index dans la direction pr�d�finie.
        self.glowColorIndex += self.glowColorIndexInc

        #si l'index a d�pass� la taille de la liste, �a fait le tour du compteur et on
        #revient � 0.
        if self.glowColorIndex >= len(self.glowColorList):
            self.glowColorIndex = 0

        #pas la peine de faire le test du tour du compteur dans l'autre sens.
        #car si on avance � reculons dans la liste pour retomber sur le 0,
        #c'est pour s'y arr�ter. (voir plus loin, le lostFocus)

        return ihmsgInfo


    def draw(self, surfaceDest):
        """
        dessinage de l'�l�ment de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #il faut remettre � jour la couleur du texte dans le lamoche.
        #on chope la couleur courante dans la liste de d�grad�, en fonction de l'index
        #et on balance �a au lamoche

        #Y'a pas � r�fl�chir si il faut r�actualiser ou pas la couleur. Faut tout le temps
        #le faire quand on arrive � cet endroit du code.
        #Dans les moments o� y'a pas le focus, cette fonction n'est pas appel�e, car
        #mustBeRefreshed est revenu � False.
        currentColor = self.glowColorList[self.glowColorIndex]
        self.theLamoche.updateAttrib(color=currentColor)
        #et hop, plus qu'� rebliter l'image sur la surface de destination.
        surfaceDest.blit(self.theLamoche.image, self.rectDrawZone)


    def takeStimuliGetFocus(self):
        """
        fonction ex�cut�e par le code ext�rieur, pour pr�venir que ce menuElem prend le focus
        """

        #hop paf mother-class. (On choisit carr�ment la mother-motherclass. De toutes fa�ons
        #ni le MenuText ni le MenuSensitiveSquare ne surcharge cette fonction.
        #L'important, c'est que �a fixe self.focusOn � True
        MenuElem.takeStimuliGetFocus(self)

        #Quand on a le focus, on r�fl�chit pas. La direction de d�placement de l'index
        #de glow, c'est vers l'avant, et pis c'est tout.
        self.glowColorIndexInc = +1

        #et il faudra redessiner l'�l�ment � chaque cycle, et pis c'est tout aussi.
        self.mustBeRefreshed = True


    def takeStimuliLoseFocus(self):
        """
        fonction ex�cut�e par le code ext�rieur, pour pr�venir que ce menuElem perd le focus
        """

        #hop paf mother-class. Et �a fixe self.focusOn � False. Captbain obvious, oui.
        MenuElem.takeStimuliLoseFocus(self)

        #il faut faire revenir la couleur du texte � l'index 0. Mais on le fait en prenant
        #le chemin le plus court possible. C'est � dire que si on est dans la deuxi�me moiti�
        #de la liste de d�grad� de couleur, on reste dans la direction +1. (Et avec le tour
        #du compteur, on arrive � 0).
        #Si on est dans la premi�re moiti� de la liste, vaut mieux revenir en arri�re.
        #donc on change la direction pour -1.
        if self.glowColorIndex < (len(self.glowColorList) >> 1):
            self.glowColorIndexInc = -1

        #le mustBeRefreshed se remettra � False tout seul, gr�ce � la fonction update,
        #une fois que la couleur sera revenue � l'index 0.

