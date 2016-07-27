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

date de la dernière relecture-commentage : 27/02/2011

Elément de menu qui poutre sa race. C'est une zone de texte. On écrit dedans. Hell yeah !

A priori, tous les caractères bizarres fonctionnent (accents, majuscules, trémas, ...)
Le joueur peut appuyer sur backspace pour effacer la dernière lettre.
Les flèches gauche et droite ne font rien. On ne peut pas sélectionner tout ou une partie du
texte. On ne peut pas faire de copier-coller. Le curseur reste toujours en fin de texte.
Donc c'est un peu rustique comme zone de texte éditable, mais au moins, je le dis.

TRODO pour plus tard : y'a un bug sur Mac. Certaines touches, genre F1 F2 ... ne sont rien
censés écrire. Or, ça met un caractère vide. (je sais pas exactement lequel. J'ai pas regardé)
C'est la valeur event.unicode qu'est pas la même sur Mac et sur PC, pour certaines touches.
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

#liste de tuple de couleur RVB utilisé pour faire le glow du curseur,
#quand ils ont le focus. C'est un dégradé bleu -> blanc -> bleu
#Attention, c'est pas le même dégradé que le dégradé du SensitiveText.
#Ici, on commence par le bleu, alors que le SensitiveText commence par le blanc.
#A quoi ça sert ? Eh ben quand l'elem est pas focusé, il affiche la couleur d'index 0
#Pour du SensitiveText, faut que ce soit blanc. (Parce que j'avais envie de cette couleur là,
#et pis au moins c'est lisible)
#Pour le curseur de l'EditableText, faut que ce soit bleu. Car le texte de l'EditableText est
#tout le temps affiché en blanc. Et si le curseur est blanc aussi, ça fait bizarre.
#Ca donne l'impression que y'a un l minuscules qui traîne là qu'on sait pas pourquoi.
GLOW_CURSOR_COLOR_LIST = tuple( [ (component, component, 255)
                                  for component in GLOW_CURSOR_COMPONENT_LIST
                                ]
                              )



class MenuEditableText(MenuSensitiveText):
    """
    zone de texte qu'on peut éditay.
    """

    def __init__(self, rectDrawZone, font, text="",
                 maxNbrChar=-1, inflateDist=5):
        """
        constructeur. (thx captain obvious)

        entrée :
            rectDrawZone : rectangle de dessin du MenuElem. D'habitude, on peut se contenter
                de définir la position du point supérieur-gauche. La taille se déduit du
                truc qu'on a à afficher (image, texte, ...) Mais ici, c'est du texte qui
                change tout le temps. Donc on est obligé de définir explicitement la zone,
                avec la position et la taille du rectangle.

            font : objet pygame.font.Font. police de caractère utilisée pour le texte.
                   (la taille est déjà définie dans la font. Ca se fait au moment de la charger)

            text : string unicode. Valeur initiale du texte. Mais après, le joueur va le changer.

            maxNbrChar : int. Nombre maximal de caractères que le joueur peut saisir.
                         Si c'est -1 : pas de maximum (en théorie, haha).

            inflateDist : Marge ajouté au rectDrawZone pour définir rectStimZone.
                          voir description du contructeur de MenuSensitiveSquare.
        """

        #mother-mother-[...] class. Youpi !!
        MenuElem.__init__(self)

        #initialisation des trucs à propos du texte. (Cette fonction vient de MenuText).
        #Le param None est affecté à idTxtStock. Ca n'aurait pas de sens d'associer un
        #texte prédéfini à ce MenuElem, puisque le joueur va le changer. On peut lui associer
        #un texte initial, mais pas un texte prédéfini. Ouais c'est bizarre ce que je dis.
        #En fait c'est surtout par rapport à la fonction changeLanguage. Elle ne doit rien
        #faire. Et surtout pas se baser sur un idTxtStock pour changer la valeur du texte
        #si jamais on change la langue. Enfin on pourrait peut être en avoir besoin pour
        #définir le texte initial justement. Oh laissez tomber. Je commence vraiment à
        #raconter n'importe quoi. Ca suffit. Je suis chez le coiffeur. Héhé.
        self.initTextInfo(rectDrawZone, font, None, text)

        self.rectDrawZone = rectDrawZone
        self.maxNbrChar = maxNbrChar
        self.sizeLimited = (self.maxNbrChar != -1)

        #cet élément peut être focusé.
        self.acceptFocus = True
        #L'élément ne fait rien quand on clique dessus, mais si on passe la souris dessus,
        #il se focus.
        self.clickType = MOUSE_NONE

        #définition de la zone de sensibilité aux clics.
        MenuSensitiveSquare.defineStimZoneFromDrawZone(self, inflateDist)

        # - définition des variables utilisées pour faire glower le curseur quand il a le focus -
        #voir commentaire de MenuSensitiveText. C'est foutu exactement pareil, sauf que c'est pas
        #la même liste de couleur (déjà expliqué), et c'est pas le même truc qu'on fait glower.
        #Pour MenuSensitiveText, c'est tout le texte. Pour MenuEditableText, c'est que le curseur.
        self.glowColorIndex = 0
        self.glowColorIndexInc = +1
        self.glowColorList = GLOW_CURSOR_COLOR_LIST


    def draw(self, surfaceDest):
        """
        dessinage de l'élément de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #Le self.glowColorIndex se met à jour tout seul, avec la fonction update héritée
        #(voir MenuSensitiveText)
        currentColor = self.glowColorList[self.glowColorIndex]

        #On blite l'image du texte. Récupérée depuis le lamoche interne
        surfaceDest.blit(self.theLamoche.image, self.rectDrawZone)

        #Récupération de la position X du curseur. Il se trouve à droite du texte,
        #à une petite distance de marge de 2 pixel.
        cursorX = self.rectDrawZone.x + self.theLamoche.image.get_width() + 2

        #création du mini-rectangle représentant le curseur. Sa largeur est de 2 pixels.
        #Sa hauteur est celle de la hauteur de la zone de dessin.
        rectCursor = pyRect(cursorX, self.rectDrawZone.y,
                            2, self.rectDrawZone.height)

        #Maintenant qu'on a la position et la couleur du curseur, on le dessine.
        pygame.draw.rect(surfaceDest, currentColor, rectCursor)


    def canAddOneChar(self, key, unicodeChar):
        """
        vérifie si les infos indiquées par la touche de clavier que le joueur vient d'appuyer,
        correspondent à un caractère "imprimable" et correct, que l'on peut ajouter
        à la chaîne de caractère de la zone de texte. (Putain, ça c'est de la phrase à rallonge)

        entrées :
            key : int. Code de la touche appuyées
            unicodeChar : caractère unicode, correspondant à la touche appuyées.
                          (c'est la valeur de event.unicode de l'event pygame.locals.KEYDOWN)

        plat-dessert :
            Booléen. True : on peut ajouter le caractère unicodeChar au texte de la zone de texte.
                     False : Ay bien on peut pô. ("Eh ben c'est en cours. Haha job private joke).
        """

        #contrôle du nombre de caractère du texte. (Si ce nombre est limité)
        if self.sizeLimited and len(self.theLamoche.text) >= self.maxNbrChar:
            return False

        #contrôle du contenu de la chaîne de caractère unicode.
        if unicodeChar == "":
            return False

        #contrôle des caractères non imprimables. #TRODO pour plus tard : cette limite de 30,
        #c'est à verifier. Je fais comme si on était en Ascii. c'est peut être plus compliqué.
        if ord(unicodeChar) < 30:
            return False

        #contrôle des touches dont je suis sûr qu'elles génèrent des caractères non-imprimables.
        #TRODO pour plus tard : c'est ici qu'il faudrait agir pour corriger le bug que y'a sur Mac
        #(voir le premier trodo, au début de ce fichier.)
        if key in LIST_NO_PRINTABLE_KEY:
            return False

        #c'est bon, on a passé tous les tests. Le caractère unicode pourra être ajouté au texte.
        return True


    def takeStimuliKeys(self, dictKeyPressed, keyCodeDown, keyCharDown):
        """
        prise en compte des touches appuyées par le joueur.
        (voir description dans la classe MenuElem)
        """

        if not self.focusOn:
            #Y'a pas le focus. On n'a pas à prendre en compte les appuyages de touche.
            #On branle rien. Et on renvoie un ihmsgInfo vide.
            return IHMSG_VOID

        #y'a le focus. Faut branler queque chose.

        currentText = self.theLamoche.text
        #indique si le texte aura été modifié, et qu'il faudrera mettre à jour la modif.
        mustUpdate = False

        if keyCodeDown == pygl.K_BACKSPACE:

            #le joueur a appuyé sur backspace. On doit supprimer le dernier caractère du texte,
            #si il reste des caractères.
            if len(currentText) > 0:
                currentText = currentText[:-1]
                mustUpdate = True

        else:

            #le joueur a appuyé sur une touche, qui génère peut être un caractère imprimable,
            #et qu'on peut peut-être ajouter au texte. On vérifie tout ça.
            if self.canAddOneChar(keyCodeDown, keyCharDown):
                #C'est ok. On ajoute le caractère généré par la touche appuyée.
                currentText += keyCharDown
                mustUpdate = True

        if mustUpdate:

            #mise à jour du texte de la zone de texte, dans le lamoche interne.
            self.theLamoche.updateAttrib(text=currentText)
            #indication au code extérieur qu'il faut redessiner tout ce bordel.
            return (IHMSG_REDRAW_MENU, )

        else:

            #Le texte n'a pas changé. Rien à faire. (J'adore cette assertion : "Rien à faire").
            return IHMSG_VOID


    #pas besoin d'overrider la fonction takeStimuliMouse.
    #Comme j'ai mis MOUSE_NONE dans le clickType, la fonction treatStimuliMouse de
    #menuSensitiveSquare ne renvoie pas le message IHMSG_ELEM_CLICKED.
    #Et ça tombe bien. Parce que si ça le renvoyait, on essaierait d'exécuter funcAction
    #Or, j'ai pas défini de funcAction pour cette classe.
    #Donc ça devrait planter, mais ça plante pas grâce au MOUSE_NONE.
