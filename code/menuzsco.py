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

date de la derni�re relecture-commentage : 18/03/2011

Menu affichant les scores des diff�rents joueur enregistr�s. Il y a 2 ou 3 joueurs enregistr�s.
(Voir description de ces joueurs de LIST_ORDERED_NAME)

Pour chaque joueur, on affiche un "bloc de score". Il s'agit d'un ensemble de MenuText, contenant
du blabla, et les statistiques du joueur.
Les blocs de score sont tous affich�s en m�me temps � l'�cran, les uns en dessous des autres.

Dans le fichier de sauuvegarde, on stocke 8 statistiques pour chaque joueur.
Dans ce menu, on n'affique que 4 statistiques dans un bloc de joueur. Y'en a donc 4 autres qui
servent � rien. Et je confirme, elles servent vraiment � rien. Elles ne sont jamais utilis�es
autre part.
(C'est parce que j'avais pr�vu plus de trucs au d�part, et apr�s j'ai simplifi�. Bon, pas grave)
"""

import pygame

from common   import pyRect, IHMSG_QUIT, NAME_HERO, NAME_RECHER, NAME_DOGDOM

from scoremn  import (scoreFromKillBurst,
                      TOTAL_KILL, TOTAL_BURST,
                      HISCORE_SCORE, HISCORE_KILL, HISCORE_BURST,
                      BURST, KILL, CALC_SCORE)

from menutxt  import MenuText
from txtstock import txtStock
from menucomn import manyQuit
from menumng  import MenuManager

#liste de tuple regroupant toutes les infos des MenuText statiques, � afficher dans les blocs
#de score. (c'est � dire tous les MenuText, sauf ceux affichant les valeurs des scores)
#Chaque tuple contient 2 �l�ments :
# - coordonn�es du MenuText dans le bloc de score du joueur en cours.
#   (on ajoute ces coordonn�es � la position du coin sup-gauche du bloc pour avoir les vraies
#   coordonn�es � l'�cran).
# - identifiant du texte � afficher, dans la classe txtStock.
LIST_MENU_TEXT_INFO_STATIC = (
    ((  40,  25), txtStock.STAT_HI_SCORE  ),
    ((  10,  40), txtStock.STAT_HI_KILL   ),
    ((  10,  50), txtStock.STAT_HI_BURST  ),
    ((  10,  70), txtStock.STAT_ALL_KILL  ),
    (( 210,  70), txtStock.STAT_ALL_BURST ),
    ((   0,  85), txtStock.STAT_SEP       ),
)

#liste de tuples regroupant les infos des MenuText affichant les valeurs des stats
#dans les blocs de score. Chaque tuple contient 2 �l�ments :
# - coordonn�es du MenuText dans le bloc de score du joueur en cours.
#   (gestion par bloc, comme pour les MenuText statiques)
# - sous-tuple de 1 ou 2 �l�ments, permettant de d�terminer quel stat on veut afficher.
#    * identifiant principal de la stat
#    * identifiant secondaire de la stat (si besoin)
LIST_MENU_TEXT_INFO_SCORE = (
    (( 125,  25), (HISCORE_SCORE, CALC_SCORE)),  #meilleur score
    (( 235,  40), (HISCORE_KILL,  KILL)),        #plus grand nombre de magi tu�s en 1 partie.
    (( 235,  50), (HISCORE_BURST, BURST)),       #plus grand nombre de magi explos�s en 1 partie.
    ((  75,  70), (TOTAL_KILL, )),               #nombre total de magiciens tu�s, en tout
    (( 295,  70), (TOTAL_BURST, )),              #nombre total de magiciens explos�s, en tout.
)

#position du coin sup-gauche du premier bloc de joueur.
POS_PLAYER_INIT = pyRect(10, 5)

#d�calage (X, Y) � appliquer pour passer d'un bloc de joueur au suivant.
POS_PLAYER_DECAL = (0, 100)

#nom des joueurs, pour lesquels ont doit afficher les blocs. L'ordre dans cette liste d�fini
#l'ordre des blocs � l'�cran.
#Si certains joueurs sont inexistants, on n'affiche pas leur bloc, et on passe au suivant.
LIST_ORDERED_NAME = (
    NAME_HERO,    #Le joueur principal. Qui correspond au mode de jeu normal
    NAME_DOGDOM,  #Le joueur correspondant au mode de jeu EdomEdog (pas forc�ment pr�sent)
    NAME_RECHER   #Moi-m�me. J'ai juste ajout� des stats statiques (haha), pour faire mon kakou.
)



class MenuManagerHighScore(MenuManager):
    """
    menu pour afficher les high scores, les stats et tout
    """

    def __init__(self, surfaceDest, dicImg,
                 fontDefault, fontLittle, archivist):
        """
        constructeur. (thx captain obvious)

        entr�e :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault, fontLittle : objets pygame.font.Font. les polices de caract�res.

            archivist : objet de la classe �poney-ime, qui g�re le fichier de sauvegarde
                C'est l� dedans que y'a les stats des joueurs
        """

        MenuManager.__init__(self, surfaceDest, dicImg)

        self.archivist = archivist
        self.fontDefault = fontDefault
        self.fontLittle = fontLittle

        # --- Cr�ation des MenuElem ---

        #cr�ation de tous les MenuText (statiques et scoriques) de tous les blocs de joueur.
        listMenuText = self.buildAllPlayerMenuText()

        # --- Rangement de tous les MenuElem cr��s, dans la grande liste globale. ---

        #y'a la liste des MenuText, et le MenuElem liant la touche Esc � la fonction de
        #quittage de menu
        self.listMenuElem = listMenuText + (manyQuit, )

        self.initFocusCyclingInfo()


    def buildAllPlayerMenuText(self):
        """
        Cr�e tous les MenuText (statiques et scoriques) de tous les blocs de joueur.

        plat-dessert : liste de MenuText, avec tout dedans.
        """
        listMenuText = []

        #position du bloc de score du joueur courant.
        rectPlayerPos = pygame.Rect(POS_PLAYER_INIT)

        for playerName in LIST_ORDERED_NAME:

            #on n'affiche le bloc de score de ce joueur que si il est mentionn� dans le
            #fichier de sauvegarde. Sinon, on passe directement au suivant.
            if playerName in self.archivist.dicPlayerData:

                #cr�ation des MenuText du bloc de score du joueur courant,
                #� la coordonn�e courante. (J'ai la courante, youpi !!)
                param = (playerName, rectPlayerPos)
                listMenuBlockScore = self.buildOnePlayerMenuText(*param)

                #ajout de ces MenuText dans la liste principale de tous les MenuText
                listMenuText += listMenuBlockScore

                #mise � jour de la coordonn�e du bloc de score. (on se d�cale vers le bas)
                rectPlayerPos.move_ip(POS_PLAYER_DECAL)

        return tuple(listMenuText)


    def buildOnePlayerMenuText(self, playerName, rectPlayerPos):
        """
        cr�e tous les MenuText (statiques et scoriques) pour un bloc de score de un joueur.

        entr�es :
            playerName : string � peu pr�s unicode. Identifiant du joueur dont on veut
                         cr�er le bloc de score
            rectPlayerPos : position du coin sup-gauche du bloc de score en cours.

        plat-dessert : liste des MenuText du bloc de score du joueur.
        """

        listMenuBlockScore = []

        #MenuText affichant le nom du joueur. (Il est directement dans le coin sup-gauche)
        menuElem = MenuText(rectPlayerPos, self.fontDefault, text=playerName)
        listMenuBlockScore.append(menuElem)

        #cr�ation des MenuText statique.
        for intRelativeCoord, idTxtStock in LIST_MENU_TEXT_INFO_STATIC:

            #d�finition de la position du MenuText � l'�cran
            #(position du bloc + d�calage dans le bloc, sp�cifique � ce MenuText)
            screenCoord = rectPlayerPos.move(intRelativeCoord)
            #cr�ation du MenuText, et ajout dans la liste.
            menuElem = MenuText(screenCoord, self.fontLittle, idTxtStock)
            listMenuBlockScore.append(menuElem)

        for intRelativeCoord, tupleStatKey in LIST_MENU_TEXT_INFO_SCORE:

            #d�finition de la position du MenuText � l'�cran
            #(position du bloc + d�calage dans le bloc, sp�cifique � ce MenuText)
            screenCoord = rectPlayerPos.move(intRelativeCoord)
            #r�cup�ration de la valeur de la statistique � afficher (score, ...)
            statValue = self.getHiScoreStat(playerName, tupleStatKey)
            #cr�ation du MenuText, et ajout dans la liste.
            menuElem = MenuText(screenCoord, self.fontLittle, text=statValue)
            listMenuBlockScore.append(menuElem)

        return listMenuBlockScore


    def getHiScoreStat(self, playerName, tupleStatKey):
        """
        r�cup�ration d'une statistique d'un joueur.

        entr�e :
            playerName : string � peu pr�s unicode. Identifiant du joueur dont on veut la stat.

            tupleStatKey : tuple de 1 ou 2, permettant d'indiquer la stat
                           qu'on veut afficher. Voir description de LIST_MENU_TEXT_INFO_SCORE
                           au d�but de ce fichier. C'est ces valeurs l�.

        plat-dessert :
            string. (Plus exactement : valeur num�rique sous forme de string), contenant
            la stat demand�e
        """

        #dictionnaire contenant les statistiques du joueur indiqu� en param�tre.
        #(r�cup�r� depuis la classe ayant r�cup�r� les infos du fichier de sauvegarde)
        dicCurrentPlayerData = self.archivist.dicPlayerData[playerName]

        #la suite est un peu crade, mais pas trop.

        if len(tupleStatKey) == 1:

            #on a juste un identifiant principal, sans identifiant secondaire.
            #Ca veut dire que l'identifiant principal sp�cifie une valeur num�rique simple,
            #qui se trouve dans le dictionnaire du joueur. Donc, on la chope directement.
            statKey = tupleStatKey[0]
            statValue = dicCurrentPlayerData[statKey]

        elif len(tupleStatKey) == 2:

            #y'a un identifiant principal, et un identifiant secondaire. Ca veut dire que
            #l'identifiant principal sp�cifie un sous-dictionnaire contenant divers trucs,
            #qui se trouve dans le dictionnaire du joueur. Pour l'instant, on sait
            #pas trop ce qu'on doit faire avec ce sous-dictionnaire. Ca d�pend de l'id secondaire.
            statKey = tupleStatKey[0]
            statSubKey = tupleStatKey[1]

            if statSubKey == CALC_SCORE:
                #la stat � r�cup�rer est une valeur de score. Il faut la recalculer, �
                #partir des valeurs KILL et BURST contenues dans le sous-dictionnaire
                #sp�cifi� par l'identifiant principal.

                #r�cup�ration des valeurs kill et burst.
                statValueKill = dicCurrentPlayerData[statKey][KILL]
                statValueBurst = dicCurrentPlayerData[statKey][BURST]
                #calcul du score, en fonction de ces deux valeurs.
                statValue = scoreFromKillBurst(statValueKill, statValueBurst)

            else:

                #la stat est � r�cup�rer dans le sous-dictionnaire. elle est identifi�e
                #directement par l'identifiant secondaire. On la chope directement.
                statValue = dicCurrentPlayerData[statKey][statSubKey]

        return str(statValue)


    def startMenu(self):
        """
        fonction qui s'ex�cute au d�but de l'activation du menu
        (voir description de la fonction dans la classe-m�re)
        """

        #C'est un peu bourrin, parce qu'on trashe tout les menuText (y compris ceux qui sont
        #statiques, et on les reconstruit tous juste apr�s. Alors que la seule chose qu'on
        #aurait besoin de faire, c'est r�actualiser le texte des MenuText affichant les stats.
        #TRODO pour plus tard : faire moins bourrin. (Mais �a veut dire qu'il faudra
        #identifier chaque MenuText affichant une stat, pour pouvoir les retrouver plus tard.
        #C'est un peu lourdingue).
        listMenuText = self.buildAllPlayerMenuText()
        #En plus, avec ces conneries, faut reconstituer la liste total des MenuElem du menu.
        self.listMenuElem = listMenuText + (manyQuit, )
