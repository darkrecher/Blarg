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

date de la dernière relecture-commentage : 22/02/2011

Elément de menu qui poutre sa race, parce que non seulement il affiche du texte comme un
ouf malade, mais en plus, il est focusable, et en plus-plus, il réagit aux clics.
"""

import pygame

from common import pyRect
from menuelem import MenuElem
from lamoche  import ALIGN_LEFT, ALIGN_TOP
from menusesq import MenuSensitiveSquare, MOUSE_DOWN, RECT_ZERO
from menutxt  import MenuText


#liste d'une composante de couleur (R, V ou B, c'est comme on veut), permettant
#de faire un dégradé : (composante max) -> (composante à 0) -> (re-composantee max)
#
#ça tombe pas tout à fait juste au niveau des valeurs des couleurs, mais osef.
#C'est à cause des range.
#On commence à 255, 239, 223, etc... on va à 0. Et quand on remonte vers le max, ça
#reprend pas les mêmes valeurs, c'est décalé de 1. On fait ..., 224, 240
#C'est bizarre, mais on s'en fout complètement. Ca a pas besoin d'être exact.
GLOW_TEXT_COMPONENT_LIST = tuple(range(255, 0, -16) + range(0, 255, 16))

#liste de tuple de couleur RVB utilisé pour faire le glow des menuElem de type Texte,
#quand ils ont le focus. C'est un dégradé blanc -> bleu -> blanc
GLOW_TEXT_COLOR_LIST = tuple( [ (component, component, 255)
                                for component in GLOW_TEXT_COMPONENT_LIST
                              ]
                            )



#héritage multiple qu'on est obligé de préciser, pour brancher les fonctions
#qu'on veut. Mais sinon moi je fait pas de vrai héritage multiple. Car c'est zarb
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

        Au niveau de l'ordre des params, j'ai essayé de faire de mon mieux pour avoir quelque
        chose de logique, homogène par rapport aux autres classes, et pratique au niveau
        des valeurs par défaut. Eh bien je garantis pas que j'y suis arrivé. Et pis j'm'en fous.

        entrée :
            rectPos, font, idTxtStock, text :
                voir description du contructeur de MenuText

            funcAction, clickType, inflateDist :
                voir description du contructeur de MenuSensitiveSquare

            antialias, color, background, alignX, alignY :
                voir description du constructeur de Lamoche
        """

        #là, on peut appeler le constructeur du MenuText, car ça fait exactement la même
        #chose. (Et après, on fait des trucs en plus. Mais faut faire gaffe quand on
        #fait ça. A la moindre différence, vaut mieux factoriser le code avec des fonctions,
        #plutôt qu'avec des constructeurs.
        MenuText.__init__(self, rectPos, font, idTxtStock, text,
                          antialias, color, background, alignX, alignY)

        #initialisation de la zone sensible du menuElem, que la souris réagit dessus.
        param = (self, funcAction, RECT_ZERO, clickType, inflateDist)
        MenuSensitiveSquare.initSensiInterface(*param)

        #et hop, après l'initialisation, la vraie définition de la zone de où qu'elle est.
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self)

        # -- définition des variables utilisées pour faire glower le texte quand il a le focus --

        #index pointant sur la couleur courante du texte, dans la liste des couleurs du dégradé
        #qui fait le glow. L'index 0 correspond à la couleur normale (blanche, comme dirait
        #Coluche). C'est cette couleur qui est utilisée quand l'élément n'est pas focusé.
        self.glowColorIndex = 0

        #step d'incrémentaion dans la liste des couleurs. (C'est -1 ou +1, pour reculer
        #ou avancer dans la liste.
        self.glowColorIndexInc = +1

        self.glowColorList = GLOW_TEXT_COLOR_LIST


    def changeLanguage(self):
        """
        on est obligé de linker explicitement la fonction vers le MenuText
        (l'une des deux mother-class de cette classe).

        J'ai bien indiqué un héritage multiple. Mais ça suffit pas.
        Si j'ai bien compris d'où vient le problème, c'est que le MenuSensitiveSquare
        (que j'hérite en premier), a lui aussi sa fonction changeLanguage.
        (Elle est vide, et elle vient du MenuElem, mais elle existe).
        Et c'est cette fonction qui est prise en priorité. Bon, ça se défend comme argument.

        Du coup, je transmet l'appel vers la fonction que je veux vraiment exécuter.
        C'est bof, mais je vois pas d'autres solution
        """
        MenuText.changeLanguage(self)

        #Alors là on pourrait croire qu'il faut appeler la fonction defineStimZoneFromDrawZone,
        #Vu que le changeLanguage change le texte, donc faut modifier cascadalement la zone
        #de sensibilité au clics. Mais en fait y'a pas besoin. Le changeLanguage du MenuText
        #appelle la fonction changeFontAndText. Et l'astuce, c'est que en vrai,
        #ça appelle la fonction changeFontAndText du MenuSensitiveText ! (Puisque là on est
        #dedans le MenuSensitiveText). Et dans ce changeFontAndText, j'ai mis un appel
        #à defineStimZoneFromDrawZone. (Voir juste en dessous).
        #Héhé c'est quand même la classe ce truc.


    def changeFontAndText(self, newFont=None, newText=None):
        """
        Changer le texte et/ou la font, et modifier en conséquence la zone rectangulaire dans
        laquelle cet élément s'affiche, ainsi que la zone rectangulaire de sensibilité aux clics.

        entrées :
            (voir description de la fonction dans la classe MenuElem, c'est les mêmes)
        """
        MenuText.changeFontAndText(self, newFont, newText)

        #Modification de la zone de sensibilité aux clics en fonction de la zone de dessin.
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self)


    def update(self):
        """
        (voir description de la fonction dans MenuElem)

        Si on est focusé, il faut redessiner à chaque cycle, pour faire glower le texte.
        Si on vient de paumer le focus, il faut continuer de redessiner, car on
        remet progressivement la couleur du texte à la couleur normale (celle d'index 0).
        Si on a pas le focus, et qu'on est sur la couleur normale, rien à faire.
        """

        ihmsgInfo = MenuSensitiveSquare.update(self)

        #Si on a pas le focus, et que le texte a la couleur normale, y'a rien à faire.
        #on fixe mustBeRefreshed à False, comme ça l'élément ne se réaffichera pas.
        #Ca fonctionne comme il faut car l'update est fait avant le draw. Donc si, arrivé
        #à cet endroit du code, l'index de couleur est 0, c'est bien la couleur
        #réellement affichée à l'écran. (Y'a pas d'histoer à la con que il faudrait
        #réafficher une dernière petite fois avant d'arrêter. Tralala)
        if not self.focusOn and self.glowColorIndex == 0:
            self.mustBeRefreshed = False
            return ihmsgInfo

        #on a le focus, ou pas. (osef en fait). Ce dont on est sûr, c'est qu'il faut
        #faire glower le texte. Donc on avance l'index dans la direction prédéfinie.
        self.glowColorIndex += self.glowColorIndexInc

        #si l'index a dépassé la taille de la liste, ça fait le tour du compteur et on
        #revient à 0.
        if self.glowColorIndex >= len(self.glowColorList):
            self.glowColorIndex = 0

        #pas la peine de faire le test du tour du compteur dans l'autre sens.
        #car si on avance à reculons dans la liste pour retomber sur le 0,
        #c'est pour s'y arrêter. (voir plus loin, le lostFocus)

        return ihmsgInfo


    def draw(self, surfaceDest):
        """
        dessinage de l'élément de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #il faut remettre à jour la couleur du texte dans le lamoche.
        #on chope la couleur courante dans la liste de dégradé, en fonction de l'index
        #et on balance ça au lamoche

        #Y'a pas à réfléchir si il faut réactualiser ou pas la couleur. Faut tout le temps
        #le faire quand on arrive à cet endroit du code.
        #Dans les moments où y'a pas le focus, cette fonction n'est pas appelée, car
        #mustBeRefreshed est revenu à False.
        currentColor = self.glowColorList[self.glowColorIndex]
        self.theLamoche.updateAttrib(color=currentColor)
        #et hop, plus qu'à rebliter l'image sur la surface de destination.
        surfaceDest.blit(self.theLamoche.image, self.rectDrawZone)


    def takeStimuliGetFocus(self):
        """
        fonction exécutée par le code extérieur, pour prévenir que ce menuElem prend le focus
        """

        #hop paf mother-class. (On choisit carrément la mother-motherclass. De toutes façons
        #ni le MenuText ni le MenuSensitiveSquare ne surcharge cette fonction.
        #L'important, c'est que ça fixe self.focusOn à True
        MenuElem.takeStimuliGetFocus(self)

        #Quand on a le focus, on réfléchit pas. La direction de déplacement de l'index
        #de glow, c'est vers l'avant, et pis c'est tout.
        self.glowColorIndexInc = +1

        #et il faudra redessiner l'élément à chaque cycle, et pis c'est tout aussi.
        self.mustBeRefreshed = True


    def takeStimuliLoseFocus(self):
        """
        fonction exécutée par le code extérieur, pour prévenir que ce menuElem perd le focus
        """

        #hop paf mother-class. Et ça fixe self.focusOn à False. Captbain obvious, oui.
        MenuElem.takeStimuliLoseFocus(self)

        #il faut faire revenir la couleur du texte à l'index 0. Mais on le fait en prenant
        #le chemin le plus court possible. C'est à dire que si on est dans la deuxième moitié
        #de la liste de dégradé de couleur, on reste dans la direction +1. (Et avec le tour
        #du compteur, on arrive à 0).
        #Si on est dans la première moitié de la liste, vaut mieux revenir en arrière.
        #donc on change la direction pour -1.
        if self.glowColorIndex < (len(self.glowColorList) >> 1):
            self.glowColorIndexInc = -1

        #le mustBeRefreshed se remettra à False tout seul, grâce à la fonction update,
        #une fois que la couleur sera revenue à l'index 0.

