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

date de la derni�re relecture-commentage : 17/02/2011

�l�ment de menu qui affiche du texte. Sur une seule ligne.
Cet �l�ment de menu ne prend pas le focus et ne r�agit pas aux clics de souris.
Mais y'en a un autre qui le fait.

pour changer la gueule du texte, y'a qu'� directement acc�der au lamoche interne.
il faut appeler la fonction MenuText.theLamoche.updateAttrib( <param> )
Et ensuite, faut appeler la fonction redefineRectDrawZoneAfterAttribChange
pour r�actualiser les infos du MenuText en fonction du lamoche.

Si on veut changer les attributs font (police de caract�re), et text (le texte affich�),
on peut appeler directement la fonction changeFontAndText, qui s'occupe de tout.
(J'ai cr�� cette fonction parce que c'est les attributs qu'on change le plus souvent).
"""

import pygame

from common   import pyRect, getRectDrawZone
from menuelem import MenuElem
from lamoche  import Lamoche, ALIGN_LEFT, ALIGN_TOP
from txtstock import txtStock



class MenuText(MenuElem):
    """
    texte qu'on clique pas dessus, car �a sert � rien eud'cliquer dessus.
    """

    def __init__(self, rectPos, font, idTxtStock=None, text="",
                 antialias=False, color=(255, 255, 255), background=None,
                 alignX=ALIGN_LEFT, alignY=ALIGN_TOP):
        """
        constructeur. (thx captain obvious)

        entr�e :
            rectPos : Rect(X, Y). Position du texte
                      (selon l'alignement d�fini dans les params alignX et alignY)
                      Comme d'hab', les coordonn�es sont exprim�es localement, par rapport au
                      conteneur de cet �l�ment. Donc y'a des d�calages qui s'appliquent, ou pas.

            font, text, antialias, color, background, alignX, alignY :
                      voir description du constructeur Lamoche.__init__. C'est les m�mes params.

            idTxtStock : None, ou identifiant de texte dans la classe txtStock.
                         Si on le d�finit, on affichera la cha�ne de caract�re contenue
                         dans txtStock, correspondant � cet identifiant.
                         Si on ne le d�finit pas, on affiche la cha�ne du param�tre 'text'.
                         idTxtStock a la priorit� sur text.

            text : string. Valeur de texte � afficher,
                   � condition d'avoir laiss� idTxtStock � None
        """

        #constructeur de la mother-class. (Ce constructeur d�finit self.rectDrawZone � None,
        #et c'est pas ce qu'on veut. Mais on le red�finit plus loin).
        MenuElem.__init__(self)

        #initialiation de tout un tas de bazar. En particulier le lamoche interne.

        param = (rectPos, font, idTxtStock, text,
                 antialias, color, background, alignX, alignY)

        self.initTextInfo(*param)

        #d�finition de la zone dans laquelle cet �l�ment s'affiche, en fonction du texte
        # et de l'alignement que le lamoche vient de renderiser.
        self.redefineRectDrawZoneAfterAttribChange()


    def initTextInfo(self, rectPos, font, idTxtStock=None, text="",
                     antialias=False, color=(255, 255, 255), background=None,
                     alignX=ALIGN_LEFT, alignY=ALIGN_TOP):
        """
        initialise le lamoche interne, pour pouvoir afficher du texte.

        entr�es : voir fonction __init__ de cette classe. C'est tout pareil.

        (J'ai cr�� cette mini-fonction pour factoriser un peu de code avec les classes
        que j'h�rite de cette classe).
        """
        self.idTxtStock = idTxtStock

        #on prend le texte d�finit dans le txtStock, ou � d�fautn celui du param 'text'.
        if self.idTxtStock is not None:
            theText = txtStock.getText(self.idTxtStock)
        else:
            theText = text

        #cr�ation d'un lamoche, ce qui permet d'avoir une image repr�sentant le texte � afficher.
        param = (rectPos, font, theText,
                 antialias, color, background, alignX, alignY)

        self.theLamoche = Lamoche(*param)


    def redefineRectDrawZoneAfterAttribChange(self):
        """
        fonction a ex�cuter apr�s avoir modifi� des attributs du lamoche.
        permet de red�finir la rectDrawZone, en fonction des nouvelles infos dans le lamoche
        (le texte, l'alignement, etc...)
        """
        param = (self.theLamoche.rect, self.theLamoche.image)
        self.rectDrawZone = getRectDrawZone(*param)


    def draw(self, surfaceDest):
        """
        dessin de l'�l�ment de menu, sur une surface de destination.
        (voir description de la fonction dans la classe MenuElem)
        """

        #y'a juste � blitter la surface du lamoche contenant le texte,
        #sur la surface de destination, et au bon endroit.
        surfaceDest.blit(self.theLamoche.image, self.rectDrawZone)


    def changeFontAndText(self, newFont=None, newText=None):
        """
        fonction pour changer le texte et/ou la font, et modifier en cons�quence la zone
        rectangulaire dans laquelle cet �l�ment s'affiche.

        C'est un peu petit comme fonction, y'a pas beaucoup de code dedans.
        Mais comme c'est un truc qu'on fait tout le temps, je me suis permis de le
        factoriser. (Pis en plus je l'override dans le MenuSensitiveText. Donc c'est cool).

        entr�es :
          - newFont : objet pygame.font.Font, ou None. Si c'est None, on change pas la font.
            Si c'est pas None, on la change, avec cette nouvelle valeur.

          - newText : string unicode, ou None. Si c'est None, on change pas le texte.
            Si c'est pas None, on le change, avec cette nouvelle valeur.
            Si on avait d�fini un idTxtStock, le texte est chang�, mais la valeur
            de idTxtStock reste quand m�me en m�moire dans la classe. Du coup, si on
            fait un changeLanguage apr�s �a, on se retrouve avec le texte d'origine,
            selon la nouvelle langue sp�cifi�e.
        """
        self.theLamoche.updateAttrib(font=newFont, text=newText)
        #Le texte a chang�, faut red�finir la zone de de dessin, dans laquelle cet elem s'affiche.
        self.redefineRectDrawZoneAfterAttribChange()


    def changeLanguage(self):
        """
        changement du langage. (voir descrip dans MenuElem)
        """

        if self.idTxtStock is None:
            #le texte ne d�pend pas du langage. Donc on se casse, y'a rien � faire.
            return

        #Sinon faut bosser un peu. On r�actualise le texte du lamoche,
        #en r�cup�rant la cha�ne de caract�re dans le txtStock.
        #(Il va en donner une diff�rente, car il aura chang� sa valeur de langage en interne)
        newText = txtStock.getText(self.idTxtStock)

        #changement du texte et de la zone de dessin.
        self.changeFontAndText(newText=newText)

