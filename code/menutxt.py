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

date de la dernière relecture-commentage : 17/02/2011

élément de menu qui affiche du texte. Sur une seule ligne.
Cet élément de menu ne prend pas le focus et ne réagit pas aux clics de souris.
Mais y'en a un autre qui le fait.

pour changer la gueule du texte, y'a qu'à directement accéder au lamoche interne.
il faut appeler la fonction MenuText.theLamoche.updateAttrib( <param> )
Et ensuite, faut appeler la fonction redefineRectDrawZoneAfterAttribChange
pour réactualiser les infos du MenuText en fonction du lamoche.

Si on veut changer les attributs font (police de caractère), et text (le texte affiché),
on peut appeler directement la fonction changeFontAndText, qui s'occupe de tout.
(J'ai créé cette fonction parce que c'est les attributs qu'on change le plus souvent).
"""

import pygame

from common   import pyRect, getRectDrawZone
from menuelem import MenuElem
from lamoche  import Lamoche, ALIGN_LEFT, ALIGN_TOP
from txtstock import txtStock



class MenuText(MenuElem):
    """
    texte qu'on clique pas dessus, car ça sert à rien eud'cliquer dessus.
    """

    def __init__(self, rectPos, font, idTxtStock=None, text="",
                 antialias=False, color=(255, 255, 255), background=None,
                 alignX=ALIGN_LEFT, alignY=ALIGN_TOP):
        """
        constructeur. (thx captain obvious)

        entrée :
            rectPos : Rect(X, Y). Position du texte
                      (selon l'alignement défini dans les params alignX et alignY)
                      Comme d'hab', les coordonnées sont exprimées localement, par rapport au
                      conteneur de cet élément. Donc y'a des décalages qui s'appliquent, ou pas.

            font, text, antialias, color, background, alignX, alignY :
                      voir description du constructeur Lamoche.__init__. C'est les mêmes params.

            idTxtStock : None, ou identifiant de texte dans la classe txtStock.
                         Si on le définit, on affichera la chaîne de caractère contenue
                         dans txtStock, correspondant à cet identifiant.
                         Si on ne le définit pas, on affiche la chaîne du paramètre 'text'.
                         idTxtStock a la priorité sur text.

            text : string. Valeur de texte à afficher,
                   à condition d'avoir laissé idTxtStock à None
        """

        #constructeur de la mother-class. (Ce constructeur définit self.rectDrawZone à None,
        #et c'est pas ce qu'on veut. Mais on le redéfinit plus loin).
        MenuElem.__init__(self)

        #initialiation de tout un tas de bazar. En particulier le lamoche interne.

        param = (rectPos, font, idTxtStock, text,
                 antialias, color, background, alignX, alignY)

        self.initTextInfo(*param)

        #définition de la zone dans laquelle cet élément s'affiche, en fonction du texte
        # et de l'alignement que le lamoche vient de renderiser.
        self.redefineRectDrawZoneAfterAttribChange()


    def initTextInfo(self, rectPos, font, idTxtStock=None, text="",
                     antialias=False, color=(255, 255, 255), background=None,
                     alignX=ALIGN_LEFT, alignY=ALIGN_TOP):
        """
        initialise le lamoche interne, pour pouvoir afficher du texte.

        entrées : voir fonction __init__ de cette classe. C'est tout pareil.

        (J'ai créé cette mini-fonction pour factoriser un peu de code avec les classes
        que j'hérite de cette classe).
        """
        self.idTxtStock = idTxtStock

        #on prend le texte définit dans le txtStock, ou à défautn celui du param 'text'.
        if self.idTxtStock is not None:
            theText = txtStock.getText(self.idTxtStock)
        else:
            theText = text

        #création d'un lamoche, ce qui permet d'avoir une image représentant le texte à afficher.
        param = (rectPos, font, theText,
                 antialias, color, background, alignX, alignY)

        self.theLamoche = Lamoche(*param)


    def redefineRectDrawZoneAfterAttribChange(self):
        """
        fonction a exécuter après avoir modifié des attributs du lamoche.
        permet de redéfinir la rectDrawZone, en fonction des nouvelles infos dans le lamoche
        (le texte, l'alignement, etc...)
        """
        param = (self.theLamoche.rect, self.theLamoche.image)
        self.rectDrawZone = getRectDrawZone(*param)


    def draw(self, surfaceDest):
        """
        dessin de l'élément de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #y'a juste à blitter la surface du lamoche contenant le texte,
        #sur la surface de destination, et au bon endroit.
        surfaceDest.blit(self.theLamoche.image, self.rectDrawZone)


    def changeFontAndText(self, newFont=None, newText=None):
        """
        fonction pour changer le texte et/ou la font, et modifier en conséquence la zone
        rectangulaire dans laquelle cet élément s'affiche.

        C'est un peu petit comme fonction, y'a pas beaucoup de code dedans.
        Mais comme c'est un truc qu'on fait tout le temps, je me suis permis de le
        factoriser. (Pis en plus je l'override dans le MenuSensitiveText. Donc c'est cool).

        entrées :
          - newFont : objet pygame.font.Font, ou None. Si c'est None, on change pas la font.
            Si c'est pas None, on la change, avec cette nouvelle valeur.

          - newText : string unicode, ou None. Si c'est None, on change pas le texte.
            Si c'est pas None, on le change, avec cette nouvelle valeur.
            Si on avait défini un idTxtStock, le texte est changé, mais la valeur
            de idTxtStock reste quand même en mémoire dans la classe. Du coup, si on
            fait un changeLanguage après ça, on se retrouve avec le texte d'origine,
            selon la nouvelle langue spécifiée.
        """
        self.theLamoche.updateAttrib(font=newFont, text=newText)
        #Le texte a changé, faut redéfinir la zone de de dessin, dans laquelle cet elem s'affiche.
        self.redefineRectDrawZoneAfterAttribChange()


    def changeLanguage(self):
        """
        changement du langage. (voir descrip dans MenuElem)
        """

        if self.idTxtStock is None:
            #le texte ne dépend pas du langage. Donc on se casse, y'a rien à faire.
            return

        #Sinon faut bosser un peu. On réactualise le texte du lamoche,
        #en récupérant la chaîne de caractère dans le txtStock.
        #(Il va en donner une différente, car il aura changé sa valeur de langage en interne)
        newText = txtStock.getText(self.idTxtStock)

        #changement du texte et de la zone de dessin.
        self.changeFontAndText(newText=newText)

