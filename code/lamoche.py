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

date de la derni�re relecture-commentage : 18/02/2011

En fait c'est un "label", pas un "lamoche" mais je hahaha.
Je suis tout seul dans ma t�te, et �a me plait.
"""
import pygame

#valeurs possibles pour le param�tre alignX
(ALIGN_LEFT,       #texte align� � gauche
 ALIGN_CENTER_X,   #texte centr� horizontalement
 ALIGN_RIGHT,      #texte align� � droite
) = range(3)

#dico de correspondance (param alignX) -> (nom de l'attribut de l'objet Rect sur lequel agir)
DICT_ALIGN_X_ATTRIB = {
    ALIGN_LEFT     : "x",
    ALIGN_CENTER_X : "centerx",
    ALIGN_RIGHT    : "right",
}

#valeurs possibles pour le param�tre alignY
(ALIGN_TOP,       #texte align� en haut
 ALIGN_CENTER_Y,  #texte centr� verticalement
 ALIGN_BOTTOM,    #texte align� en banane. Oui, en banane.
) = range(3)

#dico de correspondance (param alignY) -> (nom de l'attribut de l'objet Rect sur lequel agir)
DICT_ALIGN_Y_ATTRIB = {
    ALIGN_TOP      : "y",
    ALIGN_CENTER_Y : "centery",
    ALIGN_BOTTOM   : "bottom",
}



class Lamoche(pygame.sprite.Sprite):
    """
    le Lamoche permettant d'afficher un texte est d�riv� d'un sprite.
    C'est peut �tre un peu bizarre, mais �a se tient, et je fais ce que je veux.
    """

    def __init__(self, rectPos, font, text="",
                 antialias=False, color=(255, 255, 255), background=None,
                 alignX=ALIGN_LEFT, alignY=ALIGN_TOP):
        """
        constructeur. (thx captain obvious)

        entr�e :
            rectPos : rect. coordonn�es X,Y du label. C'est les coordonn�es du point
                      haut/bas/milieu - gauche/droite/milieu du label. En fait �a d�pend
                      des alignements qu'on indique dans les param un peu plus loin.

            font : objet pygame.font.Font. police de caract�re utilis�e pour le texte.
                   (la taille est d�j� d�finie dans la font. Ca se fait au moment de la charger)

            text : string unicode ou pas. Ben c'est le texte quoi. (les accents et autres
                   caract�res zarb fonctionnent, si ils sont pr�sents dans la font utilis�e.)

            antialias : bool�en. indique si on veut faire le rendu du texte avec/sans antialiasing

            color : tuple de 3 elem RVB. couleur du texte.

            background : image de fond sur laquelle mettre le texte. chai plus trop comment
                         �a marche. Mais je crois que �a sert que si on fait de l'antialiasing.

            alignX : indique l'alignement horizontal du texte.
                     valeurs possibles : les trois d�finies au d�but de ce fichier de code

            alignY : indique l'alignement vertical du texte.
                     valeurs possibles : les trois d�finies au d�but de ce fichier de code
        """
        pygame.sprite.Sprite.__init__(self)

        #gros tas d'initialisations de merde.
        self.font = font
        self.text = text
        self.antialias = antialias
        self.color = color
        self.background = background
        self.alignX = alignX
        self.alignY = alignY

        #enregistrement des coordonn�es X,Y. pour l'instant, on tient pas compte des align X et Y
        self.rect = pygame.Rect(rectPos)

        #rendu du texte, avec les attributs qu'on vient d'enregistrer.
        #le self.rect sera red�plac�, pour tenir compte des aligns X et Y.
        self.render()


    def render(self):
        """
        cr�e une Surface contenant le rendu de texte, avec les attributs courants,
        et d�finit cette Surface comme l'image du Sprite.
        """

        #On ne passe pas le param�tre background si il est None
        #C'est un putain de bug dans pygame. Voir www.pygame.org/docs/ref/font.html#Font.render
        #ouvrir les commentaires, et lire ceux de July 19, 2007 4:32pm - Anonymous et
        #February 8, 2006 2:29am - Anonymous
        #bordayl !  je savais m�me pas qu'on pouvait faire la diff�rence entre
        #la valeur par d�faut d'un param facultatif et un param facultatif non sp�cifi�.
        #faudra nous corriger �a, les gens de pygame !!!
        if self.background is None:
            param = (self.text, self.antialias, self.color)
        else:
            param = (self.text, self.antialias, self.color, self.background)

        #cr�ation de la Surface avec le rendu de texte
        self.image = self.font.render(*param)

        #il faut repositionner le sprite, car la taille de l'image de rendu a surement chang�,
        #du coup, faut modifier les coordonn�es du rect, en tenant compte des aligns X et Y.
        self.setPos(self.rect)


    def updateAttrib(self, font=None, text=None, antialias=None, color=None,
                     background=None, updateBackground=False, refresh=True):
        """
        modifie un ou plusieurs attributs du Lamoche. Et refait le rendu, si on veut.

        entr�es :
            font, text, antialias, color : nouvelle valeur des attributs.
            voir description d�taill�e dans la fonction __init__
            mettre la valeur None pour les attributs qu'on ne veut pas changer.

            background : nouvelle valeur de l'attribut background.

            updateBackground : bool�en. indique si on veut changer la valeur
            du background avec celle sp�cifi�e en param, ou pas.

            je suis oblig� d'avoir recours � ce putain de param updateBackGround
            car 'None' a une signification pour background. Putain d'attribut background de merde.
            D�j� il fait chier avec le bug, et en plus il fait chier � se permettre
            de pouvoir �tre None.

            refresh : bool�en. Indique si on veut tout de suite refaire le rendu
                      avec les nouveaux attributs, ou pas.
        """

        #mise � jour des attributs, pour ceux qui ont �t� sp�cifi�s
        if font is not None: self.font = font
        if text is not None: self.text = text
        if color is not None: self.color = color
        if antialias is not None: self.antialias = antialias
        #fucking mise � jour de l'attribut background seulement si demand� par 'updateBackground'
        if updateBackground: self.background = background

        #re-r�alisation du rendu du texte, si demand� par 'refresh'
        if refresh:
            self.render()


    def setPos(self, rectNewPos):
        """
        modifie les coordonn�es du sprite (self.rect) avec de nouvelles valeurs,
        en tenant compte des alignement pr�alablement sp�cifi�, et de la taille du texte.

        entr�es :
            rectNewPos : rect. contient les nouvelles coordonn�es X,Y du Lamoche
                         vaut mieux que ce rect ait une width et une height de 0,
                         (seule les coord sont sp�cifi�). Sinon �a risque de faire
                         des trucs un peu bizarre.

        TRODO : J'ai rien pr�vu pour red�finir les align X et Y, apr�s la cr�ation de l'objet.
        Quand j'ajouterais cette fonctionnalit�, faudra le faire ici.
        Cette fonction prendra en param facultatif les nouvelles valeurs de alignX et Y.
        et du coup le rectNewPos serait aussi facultatif. Si il est None, on part de self.rect
        sinon, on part de rectNewPos
        Je ferais �a si j'en ai besoin, ou alors dans la version 2 du jeu
        """

        #dictionnaire qui sera utilis� dans l'appel d'une fonction.
        #cl� : nom du param�tre. valeur : valeur du param�tre.
        #on va l'utiliser pour la fonction constructeur d'un rect.
        dictParam = {}

        #je suis pas fan des dictionnaire de param, et encore moins des getattr.
        #Mais l� c'est la fa�on la plus �l�gante que j'ai trouv� pour faire du code
        #pas trop r�p�titif.

        #d'abord on chope le nom de l'attribut de l'objet Rect sur lequel on doit agir.
        #Il d�pend de l'alignement choisi.
        strParamName = DICT_ALIGN_X_ATTRIB[self.alignX]
        #cet attribut du self.rect devra prendre la valeur du m�me attribut du rectNewPos
        #si c'est pas clair, d�merdez-vous.
        dictParam[strParamName] = getattr(rectNewPos, strParamName)

        #tout pareil m�me code, mais pour la coordonn�e Y.
        strParamName = DICT_ALIGN_Y_ATTRIB[self.alignY]
        dictParam[strParamName] = getattr(rectNewPos, strParamName)

        #cr�ation d'un nouveau rect, en utilisant les width et height de l'image,
        #et la position X,Y d�finit par le dictionnaire d'attribut cr�� ci-dessus.
        self.rect = self.image.get_rect(**dictParam)

        #whoa, c'est zarb. Mais �a marche nickel !
