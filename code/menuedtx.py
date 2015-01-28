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

date de la derni�re relecture-commentage : 27/02/2011

El�ment de menu qui poutre sa race. C'est une zone de texte. On �crit dedans. Hell yeah !

A priori, tous les caract�res bizarres fonctionnent (accents, majuscules, tr�mas, ...)
Le joueur peut appuyer sur backspace pour effacer la derni�re lettre.
Les fl�ches gauche et droite ne font rien. On ne peut pas s�lectionner tout ou une partie du
texte. On ne peut pas faire de copier-coller. Le curseur reste toujours en fin de texte.
Donc c'est un peu rustique comme zone de texte �ditable, mais au moins, je le dis.

TRODO pour plus tard : y'a un bug sur Mac. Certaines touches, genre F1 F2 ... ne sont rien
cens�s �crire. Or, �a met un caract�re vide. (je sais pas exactement lequel. J'ai pas regard�)
C'est la valeur event.unicode qu'est pas la m�me sur Mac et sur PC, pour certaines touches.
"""

import pygame
import pygame.locals
pygl = pygame.locals

from common   import (pyRect, IHMSG_REDRAW_MENU, IHMSG_VOID,
                      LIST_NO_PRINTABLE_KEY)

from menuelem import MenuElem
from menusesq import MenuSensitiveSquare, MOUSE_NONE
from menusetx import MenuSensitiveText

GLOW_CURSOR_COMPONENT_LIST = tuple(range(0, 255, 16) + range(255, 0, -16))

#liste de tuple de couleur RVB utilis� pour faire le glow du curseur,
#quand ils ont le focus. C'est un d�grad� bleu -> blanc -> bleu
#Attention, c'est pas le m�me d�grad� que le d�grad� du SensitiveText.
#Ici, on commence par le bleu, alors que le SensitiveText commence par le blanc.
#A quoi �a sert ? Eh ben quand l'elem est pas focus�, il affiche la couleur d'index 0
#Pour du SensitiveText, faut que ce soit blanc. (Parce que j'avais envie de cette couleur l�,
#et pis au moins c'est lisible)
#Pour le curseur de l'EditableText, faut que ce soit bleu. Car le texte de l'EditableText est
#tout le temps affich� en blanc. Et si le curseur est blanc aussi, �a fait bizarre.
#Ca donne l'impression que y'a un l minuscules qui tra�ne l� qu'on sait pas pourquoi.
GLOW_CURSOR_COLOR_LIST = tuple( [ (component, component, 255)
                                  for component in GLOW_CURSOR_COMPONENT_LIST
                                ]
                              )



class MenuEditableText(MenuSensitiveText):
    """
    zone de texte qu'on peut �ditay.
    """

    def __init__(self, rectDrawZone, font, text="",
                 maxNbrChar=-1, inflateDist=5):
        """
        constructeur. (thx captain obvious)

        entr�e :
            rectDrawZone : rectangle de dessin du MenuElem. D'habitude, on peut se contenter
                de d�finir la position du point sup�rieur-gauche. La taille se d�duit du
                truc qu'on a � afficher (image, texte, ...) Mais ici, c'est du texte qui
                change tout le temps. Donc on est oblig� de d�finir explicitement la zone,
                avec la position et la taille du rectangle.

            font : objet pygame.font.Font. police de caract�re utilis�e pour le texte.
                   (la taille est d�j� d�finie dans la font. Ca se fait au moment de la charger)

            text : string unicode. Valeur initiale du texte. Mais apr�s, le joueur va le changer.

            maxNbrChar : int. Nombre maximal de caract�res que le joueur peut saisir.
                         Si c'est -1 : pas de maximum (en th�orie, haha).

            inflateDist : Marge ajout� au rectDrawZone pour d�finir rectStimZone.
                          voir description du contructeur de MenuSensitiveSquare.
        """

        #mother-mother-[...] class. Youpi !!
        MenuElem.__init__(self)

        #initialisation des trucs � propos du texte. (Cette fonction vient de MenuText).
        #Le param None est affect� � idTxtStock. Ca n'aurait pas de sens d'associer un
        #texte pr�d�fini � ce MenuElem, puisque le joueur va le changer. On peut lui associer
        #un texte initial, mais pas un texte pr�d�fini. Ouais c'est bizarre ce que je dis.
        #En fait c'est surtout par rapport � la fonction changeLanguage. Elle ne doit rien
        #faire. Et surtout pas se baser sur un idTxtStock pour changer la valeur du texte
        #si jamais on change la langue. Enfin on pourrait peut �tre en avoir besoin pour
        #d�finir le texte initial justement. Oh laissez tomber. Je commence vraiment �
        #raconter n'importe quoi. Ca suffit. Je suis chez le coiffeur. H�h�.
        self.initTextInfo(rectDrawZone, font, None, text)

        self.rectDrawZone = rectDrawZone
        self.maxNbrChar = maxNbrChar
        self.sizeLimited = (self.maxNbrChar != -1)

        #cet �l�ment peut �tre focus�.
        self.acceptFocus = True
        #L'�l�ment ne fait rien quand on clique dessus, mais si on passe la souris dessus,
        #il se focus.
        self.clickType = MOUSE_NONE

        #d�finition de la zone de sensibilit� aux clics.
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self, inflateDist)

        # - d�finition des variables utilis�es pour faire glower le curseur quand il a le focus -
        #voir commentaire de MenuSensitiveText. C'est foutu exactement pareil, sauf que c'est pas
        #la m�me liste de couleur (d�j� expliqu�), et c'est pas le m�me truc qu'on fait glower.
        #Pour MenuSensitiveText, c'est tout le texte. Pour MenuEditableText, c'est que le curseur.
        self.glowColorIndex = 0
        self.glowColorIndexInc = +1
        self.glowColorList = GLOW_CURSOR_COLOR_LIST


    def draw(self, surfaceDest):
        """
        dessinage de l'�l�ment de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #Le self.glowColorIndex se met � jour tout seul, avec la fonction update h�rit�e
        #(voir MenuSensitiveText)
        currentColor = self.glowColorList[self.glowColorIndex]

        #On blite l'image du texte. R�cup�r�e depuis le lamoche interne
        surfaceDest.blit(self.theLamoche.image, self.rectDrawZone)

        #R�cup�ration de la position X du curseur. Il se trouve � droite du texte,
        #� une petite distance de marge de 2 pixel.
        cursorX = self.rectDrawZone.x + self.theLamoche.image.get_width() + 2

        #cr�ation du mini-rectangle repr�sentant le curseur. Sa largeur est de 2 pixels.
        #Sa hauteur est celle de la hauteur de la zone de dessin.
        rectCursor = pyRect(cursorX, self.rectDrawZone.y,
                            2, self.rectDrawZone.height)

        #Maintenant qu'on a la position et la couleur du curseur, on le dessine.
        pygame.draw.rect(surfaceDest, currentColor, rectCursor)


    def canAddOneChar(self, key, unicodeChar):
        """
        v�rifie si les infos indiqu�es par la touche de clavier que le joueur vient d'appuyer,
        correspondent � un caract�re "imprimable" et correct, que l'on peut ajouter
        � la cha�ne de caract�re de la zone de texte. (Putain, �a c'est de la phrase � rallonge)

        entr�es :
            key : int. Code de la touche appuy�es
            unicodeChar : caract�re unicode, correspondant � la touche appuy�es.
                          (c'est la valeur de event.unicode de l'event pygame.locals.KEYDOWN)

        plat-dessert :
            Bool�en. True : on peut ajouter le caract�re unicodeChar au texte de la zone de texte.
                     False : Ay bien on peut p�. ("Eh ben c'est en cours. Haha job private joke).
        """

        #contr�le du nombre de caract�re du texte. (Si ce nombre est limit�)
        if self.sizeLimited and len(self.theLamoche.text) >= self.maxNbrChar:
            return False

        #contr�le du contenu de la cha�ne de caract�re unicode.
        if unicodeChar == "":
            return False

        #contr�le des caract�res non imprimables. #TRODO pour plus tard : cette limite de 30,
        #c'est � verifier. Je fais comme si on �tait en Ascii. c'est peut �tre plus compliqu�.
        if ord(unicodeChar) < 30:
            return False

        #contr�le des touches dont je suis s�r qu'elles g�n�rent des caract�res non-imprimables.
        #TRODO pour plus tard : c'est ici qu'il faudrait agir pour corriger le bug que y'a sur Mac
        #(voir le premier trodo, au d�but de ce fichier.)
        if key in LIST_NO_PRINTABLE_KEY:
            return False

        #c'est bon, on a pass� tous les tests. Le caract�re unicode pourra �tre ajout� au texte.
        return True


    def takeStimuliKeys(self, dictKeyPressed, keyCodeDown, keyCharDown):
        """
        prise en compte des touches appuy�es par le joueur.
        (voir description dans la classe MenuElem)
        """

        if not self.focusOn:
            #Y'a pas le focus. On n'a pas � prendre en compte les appuyages de touche.
            #On branle rien. Et on renvoie un ihmsgInfo vide.
            return IHMSG_VOID

        #y'a le focus. Faut branler queque chose.

        currentText = self.theLamoche.text
        #indique si le texte aura �t� modifi�, et qu'il faudrera mettre � jour la modif.
        mustUpdate = False

        if keyCodeDown == pygl.K_BACKSPACE:

            #le joueur a appuy� sur backspace. On doit supprimer le dernier caract�re du texte,
            #si il reste des caract�res.
            if len(currentText) > 0:
                currentText = currentText[:-1]
                mustUpdate = True

        else:

            #le joueur a appuy� sur une touche, qui g�n�re peut �tre un caract�re imprimable,
            #et qu'on peut peut-�tre ajouter au texte. On v�rifie tout �a.
            if self.canAddOneChar(keyCodeDown, keyCharDown):
                #C'est ok. On ajoute le caract�re g�n�r� par la touche appuy�e.
                currentText += keyCharDown
                mustUpdate = True

        if mustUpdate:

            #mise � jour du texte de la zone de texte, dans le lamoche interne.
            self.theLamoche.updateAttrib(text=currentText)
            #indication au code ext�rieur qu'il faut redessiner tout ce bordel.
            return (IHMSG_REDRAW_MENU, )

        else:

            #Le texte n'a pas chang�. Rien � faire. (J'adore cette assertion : "Rien � faire").
            return IHMSG_VOID


    #pas besoin d'overrider la fonction takeStimuliMouse.
    #Comme j'ai mis MOUSE_NONE dans le clickType, la fonction treatStimuliMouse de
    #menuSensitiveSquare ne renvoie pas le message IHMSG_ELEM_CLICKED.
    #Et �a tombe bien. Parce que si �a le renvoyait, on essaierait d'ex�cuter funcAction
    #Or, j'ai pas d�fini de funcAction pour cette classe.
    #Donc �a devrait planter, mais �a plante pas gr�ce au MOUSE_NONE.
