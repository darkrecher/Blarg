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

date de la dernière relecture-commentage : 18/02/2011

En fait c'est un "label", pas un "lamoche" mais je hahaha.
Je suis tout seul dans ma tête, et ça me plait.
"""
import pygame

#valeurs possibles pour le paramètre alignX
(ALIGN_LEFT,       #texte aligné à gauche
 ALIGN_CENTER_X,   #texte centré horizontalement
 ALIGN_RIGHT,      #texte aligné à droite
) = range(3)

#dico de correspondance (param alignX) -> (nom de l'attribut de l'objet Rect sur lequel agir)
DICT_ALIGN_X_ATTRIB = {
    ALIGN_LEFT     : "x",
    ALIGN_CENTER_X : "centerx",
    ALIGN_RIGHT    : "right",
}

#valeurs possibles pour le paramètre alignY
(ALIGN_TOP,       #texte aligné en haut
 ALIGN_CENTER_Y,  #texte centré verticalement
 ALIGN_BOTTOM,    #texte aligné en banane. Oui, en banane.
) = range(3)

#dico de correspondance (param alignY) -> (nom de l'attribut de l'objet Rect sur lequel agir)
DICT_ALIGN_Y_ATTRIB = {
    ALIGN_TOP      : "y",
    ALIGN_CENTER_Y : "centery",
    ALIGN_BOTTOM   : "bottom",
}



class Lamoche(pygame.sprite.Sprite):
    """
    le Lamoche permettant d'afficher un texte est dérivé d'un sprite.
    C'est peut être un peu bizarre, mais ça se tient, et je fais ce que je veux.
    """

    def __init__(self, rectPos, font, text="",
                 antialias=False, color=(255, 255, 255), background=None,
                 alignX=ALIGN_LEFT, alignY=ALIGN_TOP):
        """
        constructeur. (thx captain obvious)

        entrée :
            rectPos : rect. coordonnées X,Y du label. C'est les coordonnées du point
                      haut/bas/milieu - gauche/droite/milieu du label. En fait ça dépend
                      des alignements qu'on indique dans les param un peu plus loin.

            font : objet pygame.font.Font. police de caractère utilisée pour le texte.
                   (la taille est déjà définie dans la font. Ca se fait au moment de la charger)

            text : string unicode ou pas. Ben c'est le texte quoi. (les accents et autres
                   caractères zarb fonctionnent, si ils sont présents dans la font utilisée.)

            antialias : booléen. indique si on veut faire le rendu du texte avec/sans antialiasing

            color : tuple de 3 elem RVB. couleur du texte.

            background : image de fond sur laquelle mettre le texte. chai plus trop comment
                         ça marche. Mais je crois que ça sert que si on fait de l'antialiasing.

            alignX : indique l'alignement horizontal du texte.
                     valeurs possibles : les trois définies au début de ce fichier de code

            alignY : indique l'alignement vertical du texte.
                     valeurs possibles : les trois définies au début de ce fichier de code
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

        #enregistrement des coordonnées X,Y. pour l'instant, on tient pas compte des align X et Y
        self.rect = pygame.Rect(rectPos)

        #rendu du texte, avec les attributs qu'on vient d'enregistrer.
        #le self.rect sera redéplacé, pour tenir compte des aligns X et Y.
        self.render()


    def render(self):
        """
        crée une Surface contenant le rendu de texte, avec les attributs courants,
        et définit cette Surface comme l'image du Sprite.
        """

        #On ne passe pas le paramètre background si il est None
        #C'est un putain de bug dans pygame. Voir www.pygame.org/docs/ref/font.html#Font.render
        #ouvrir les commentaires, et lire ceux de July 19, 2007 4:32pm - Anonymous et
        #February 8, 2006 2:29am - Anonymous
        #bordayl !  je savais même pas qu'on pouvait faire la différence entre
        #la valeur par défaut d'un param facultatif et un param facultatif non spécifié.
        #faudra nous corriger ça, les gens de pygame !!!
        if self.background is None:
            param = (self.text, self.antialias, self.color)
        else:
            param = (self.text, self.antialias, self.color, self.background)

        #création de la Surface avec le rendu de texte
        self.image = self.font.render(*param)

        #il faut repositionner le sprite, car la taille de l'image de rendu a surement changé,
        #du coup, faut modifier les coordonnées du rect, en tenant compte des aligns X et Y.
        self.setPos(self.rect)


    def updateAttrib(self, font=None, text=None, antialias=None, color=None,
                     background=None, updateBackground=False, refresh=True):
        """
        modifie un ou plusieurs attributs du Lamoche. Et refait le rendu, si on veut.

        entrées :
            font, text, antialias, color : nouvelle valeur des attributs.
            voir description détaillée dans la fonction __init__
            mettre la valeur None pour les attributs qu'on ne veut pas changer.

            background : nouvelle valeur de l'attribut background.

            updateBackground : booléen. indique si on veut changer la valeur
            du background avec celle spécifiée en param, ou pas.

            je suis obligé d'avoir recours à ce putain de param updateBackGround
            car 'None' a une signification pour background. Putain d'attribut background de merde.
            Déjà il fait chier avec le bug, et en plus il fait chier à se permettre
            de pouvoir être None.

            refresh : booléen. Indique si on veut tout de suite refaire le rendu
                      avec les nouveaux attributs, ou pas.
        """

        #mise à jour des attributs, pour ceux qui ont été spécifiés
        if font is not None: self.font = font
        if text is not None: self.text = text
        if color is not None: self.color = color
        if antialias is not None: self.antialias = antialias
        #fucking mise à jour de l'attribut background seulement si demandé par 'updateBackground'
        if updateBackground: self.background = background

        #re-réalisation du rendu du texte, si demandé par 'refresh'
        if refresh:
            self.render()


    def setPos(self, rectNewPos):
        """
        modifie les coordonnées du sprite (self.rect) avec de nouvelles valeurs,
        en tenant compte des alignement préalablement spécifié, et de la taille du texte.

        entrées :
            rectNewPos : rect. contient les nouvelles coordonnées X,Y du Lamoche
                         vaut mieux que ce rect ait une width et une height de 0,
                         (seule les coord sont spécifié). Sinon ça risque de faire
                         des trucs un peu bizarre.

        TRODO : J'ai rien prévu pour redéfinir les align X et Y, après la création de l'objet.
        Quand j'ajouterais cette fonctionnalité, faudra le faire ici.
        Cette fonction prendra en param facultatif les nouvelles valeurs de alignX et Y.
        et du coup le rectNewPos serait aussi facultatif. Si il est None, on part de self.rect
        sinon, on part de rectNewPos
        Je ferais ça si j'en ai besoin, ou alors dans la version 2 du jeu
        """

        #dictionnaire qui sera utilisé dans l'appel d'une fonction.
        #clé : nom du paramètre. valeur : valeur du paramètre.
        #on va l'utiliser pour la fonction constructeur d'un rect.
        dictParam = {}

        #je suis pas fan des dictionnaire de param, et encore moins des getattr.
        #Mais là c'est la façon la plus élégante que j'ai trouvé pour faire du code
        #pas trop répétitif.

        #d'abord on chope le nom de l'attribut de l'objet Rect sur lequel on doit agir.
        #Il dépend de l'alignement choisi.
        strParamName = DICT_ALIGN_X_ATTRIB[self.alignX]
        #cet attribut du self.rect devra prendre la valeur du même attribut du rectNewPos
        #si c'est pas clair, démerdez-vous.
        dictParam[strParamName] = getattr(rectNewPos, strParamName)

        #tout pareil même code, mais pour la coordonnée Y.
        strParamName = DICT_ALIGN_Y_ATTRIB[self.alignY]
        dictParam[strParamName] = getattr(rectNewPos, strParamName)

        #création d'un nouveau rect, en utilisant les width et height de l'image,
        #et la position X,Y définit par le dictionnaire d'attribut créé ci-dessus.
        self.rect = self.image.get_rect(**dictParam)

        #whoa, c'est zarb. Mais ça marche nickel !
