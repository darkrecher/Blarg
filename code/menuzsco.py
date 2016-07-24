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

date de la dernière relecture-commentage : 18/03/2011

Menu affichant les scores des différents joueur enregistrés. Il y a 2 ou 3 joueurs enregistrés.
(Voir description de ces joueurs de LIST_ORDERED_NAME)

Pour chaque joueur, on affiche un "bloc de score". Il s'agit d'un ensemble de MenuText, contenant
du blabla, et les statistiques du joueur.
Les blocs de score sont tous affichés en même temps à l'écran, les uns en dessous des autres.

Dans le fichier de sauuvegarde, on stocke 8 statistiques pour chaque joueur.
Dans ce menu, on n'affique que 4 statistiques dans un bloc de joueur. Y'en a donc 4 autres qui
servent à rien. Et je confirme, elles servent vraiment à rien. Elles ne sont jamais utilisées
autre part.
(C'est parce que j'avais prévu plus de trucs au départ, et après j'ai simplifié. Bon, pas grave)
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

#liste de tuple regroupant toutes les infos des MenuText statiques, à afficher dans les blocs
#de score. (c'est à dire tous les MenuText, sauf ceux affichant les valeurs des scores)
#Chaque tuple contient 2 éléments :
# - coordonnées du MenuText dans le bloc de score du joueur en cours.
#   (on ajoute ces coordonnées à la position du coin sup-gauche du bloc pour avoir les vraies
#   coordonnées à l'écran).
# - identifiant du texte à afficher, dans la classe txtStock.
LIST_MENU_TEXT_INFO_STATIC = (
    ((  40,  25), txtStock.STAT_HI_SCORE  ),
    ((  10,  40), txtStock.STAT_HI_KILL   ),
    ((  10,  50), txtStock.STAT_HI_BURST  ),
    ((  10,  70), txtStock.STAT_ALL_KILL  ),
    (( 210,  70), txtStock.STAT_ALL_BURST ),
    ((   0,  85), txtStock.STAT_SEP       ),
)

#liste de tuples regroupant les infos des MenuText affichant les valeurs des stats
#dans les blocs de score. Chaque tuple contient 2 éléments :
# - coordonnées du MenuText dans le bloc de score du joueur en cours.
#   (gestion par bloc, comme pour les MenuText statiques)
# - sous-tuple de 1 ou 2 éléments, permettant de déterminer quel stat on veut afficher.
#    * identifiant principal de la stat
#    * identifiant secondaire de la stat (si besoin)
LIST_MENU_TEXT_INFO_SCORE = (
    (( 125,  25), (HISCORE_SCORE, CALC_SCORE)),  #meilleur score
    (( 235,  40), (HISCORE_KILL,  KILL)),        #plus grand nombre de magi tués en 1 partie.
    (( 235,  50), (HISCORE_BURST, BURST)),       #plus grand nombre de magi explosés en 1 partie.
    ((  75,  70), (TOTAL_KILL, )),               #nombre total de magiciens tués, en tout
    (( 295,  70), (TOTAL_BURST, )),              #nombre total de magiciens explosés, en tout.
)

#position du coin sup-gauche du premier bloc de joueur.
POS_PLAYER_INIT = pyRect(10, 5)

#décalage (X, Y) à appliquer pour passer d'un bloc de joueur au suivant.
POS_PLAYER_DECAL = (0, 100)

#nom des joueurs, pour lesquels ont doit afficher les blocs. L'ordre dans cette liste défini
#l'ordre des blocs à l'écran.
#Si certains joueurs sont inexistants, on n'affiche pas leur bloc, et on passe au suivant.
LIST_ORDERED_NAME = (
    NAME_HERO,    #Le joueur principal. Qui correspond au mode de jeu normal
    NAME_DOGDOM,  #Le joueur correspondant au mode de jeu EdomEdog (pas forcément présent)
    NAME_RECHER   #Moi-même. J'ai juste ajouté des stats statiques (haha), pour faire mon kakou.
)



class MenuManagerHighScore(MenuManager):
    """
    menu pour afficher les high scores, les stats et tout
    """

    def __init__(self, surfaceDest, dicImg,
                 fontDefault, fontLittle, archivist):
        """
        constructeur. (thx captain obvious)

        entrée :

            surfaceDest, dicImg : voir constructeur de MenuManager

            fontDefault, fontLittle : objets pygame.font.Font. les polices de caractères.

            archivist : objet de la classe époney-ime, qui gère le fichier de sauvegarde
                C'est là dedans que y'a les stats des joueurs
        """

        MenuManager.__init__(self, surfaceDest, dicImg)

        self.archivist = archivist
        self.fontDefault = fontDefault
        self.fontLittle = fontLittle

        # --- Création des MenuElem ---

        #création de tous les MenuText (statiques et scoriques) de tous les blocs de joueur.
        listMenuText = self.buildAllPlayerMenuText()

        # --- Rangement de tous les MenuElem créés, dans la grande liste globale. ---

        #y'a la liste des MenuText, et le MenuElem liant la touche Esc à la fonction de
        #quittage de menu
        self.listMenuElem = listMenuText + (manyQuit, )

        self.initFocusCyclingInfo()


    def buildAllPlayerMenuText(self):
        """
        Crée tous les MenuText (statiques et scoriques) de tous les blocs de joueur.

        plat-dessert : liste de MenuText, avec tout dedans.
        """
        listMenuText = []

        #position du bloc de score du joueur courant.
        rectPlayerPos = pygame.Rect(POS_PLAYER_INIT)

        for playerName in LIST_ORDERED_NAME:

            #on n'affiche le bloc de score de ce joueur que si il est mentionné dans le
            #fichier de sauvegarde. Sinon, on passe directement au suivant.
            if playerName in self.archivist.dicPlayerData:

                #création des MenuText du bloc de score du joueur courant,
                #à la coordonnée courante. (J'ai la courante, youpi !!)
                param = (playerName, rectPlayerPos)
                listMenuBlockScore = self.buildOnePlayerMenuText(*param)

                #ajout de ces MenuText dans la liste principale de tous les MenuText
                listMenuText += listMenuBlockScore

                #mise à jour de la coordonnée du bloc de score. (on se décale vers le bas)
                rectPlayerPos.move_ip(POS_PLAYER_DECAL)

        return tuple(listMenuText)


    def buildOnePlayerMenuText(self, playerName, rectPlayerPos):
        """
        crée tous les MenuText (statiques et scoriques) pour un bloc de score de un joueur.

        entrées :
            playerName : string à peu près unicode. Identifiant du joueur dont on veut
                         créer le bloc de score
            rectPlayerPos : position du coin sup-gauche du bloc de score en cours.

        plat-dessert : liste des MenuText du bloc de score du joueur.
        """

        listMenuBlockScore = []

        #MenuText affichant le nom du joueur. (Il est directement dans le coin sup-gauche)
        menuElem = MenuText(rectPlayerPos, self.fontDefault, text=playerName)
        listMenuBlockScore.append(menuElem)

        #création des MenuText statique.
        for intRelativeCoord, idTxtStock in LIST_MENU_TEXT_INFO_STATIC:

            #définition de la position du MenuText à l'écran
            #(position du bloc + décalage dans le bloc, spécifique à ce MenuText)
            screenCoord = rectPlayerPos.move(intRelativeCoord)
            #création du MenuText, et ajout dans la liste.
            menuElem = MenuText(screenCoord, self.fontLittle, idTxtStock)
            listMenuBlockScore.append(menuElem)

        for intRelativeCoord, tupleStatKey in LIST_MENU_TEXT_INFO_SCORE:

            #définition de la position du MenuText à l'écran
            #(position du bloc + décalage dans le bloc, spécifique à ce MenuText)
            screenCoord = rectPlayerPos.move(intRelativeCoord)
            #récupération de la valeur de la statistique à afficher (score, ...)
            statValue = self.getHiScoreStat(playerName, tupleStatKey)
            #création du MenuText, et ajout dans la liste.
            menuElem = MenuText(screenCoord, self.fontLittle, text=statValue)
            listMenuBlockScore.append(menuElem)

        return listMenuBlockScore


    def getHiScoreStat(self, playerName, tupleStatKey):
        """
        récupération d'une statistique d'un joueur.

        entrée :
            playerName : string à peu près unicode. Identifiant du joueur dont on veut la stat.

            tupleStatKey : tuple de 1 ou 2, permettant d'indiquer la stat
                           qu'on veut afficher. Voir description de LIST_MENU_TEXT_INFO_SCORE
                           au début de ce fichier. C'est ces valeurs là.

        plat-dessert :
            string. (Plus exactement : valeur numérique sous forme de string), contenant
            la stat demandée
        """

        #dictionnaire contenant les statistiques du joueur indiqué en paramètre.
        #(récupéré depuis la classe ayant récupéré les infos du fichier de sauvegarde)
        dicCurrentPlayerData = self.archivist.dicPlayerData[playerName]

        #la suite est un peu crade, mais pas trop.

        if len(tupleStatKey) == 1:

            #on a juste un identifiant principal, sans identifiant secondaire.
            #Ca veut dire que l'identifiant principal spécifie une valeur numérique simple,
            #qui se trouve dans le dictionnaire du joueur. Donc, on la chope directement.
            statKey = tupleStatKey[0]
            statValue = dicCurrentPlayerData[statKey]

        elif len(tupleStatKey) == 2:

            #y'a un identifiant principal, et un identifiant secondaire. Ca veut dire que
            #l'identifiant principal spécifie un sous-dictionnaire contenant divers trucs,
            #qui se trouve dans le dictionnaire du joueur. Pour l'instant, on sait
            #pas trop ce qu'on doit faire avec ce sous-dictionnaire. Ca dépend de l'id secondaire.
            statKey = tupleStatKey[0]
            statSubKey = tupleStatKey[1]

            if statSubKey == CALC_SCORE:
                #la stat à récupérer est une valeur de score. Il faut la recalculer, à
                #partir des valeurs KILL et BURST contenues dans le sous-dictionnaire
                #spécifié par l'identifiant principal.

                #récupération des valeurs kill et burst.
                statValueKill = dicCurrentPlayerData[statKey][KILL]
                statValueBurst = dicCurrentPlayerData[statKey][BURST]
                #calcul du score, en fonction de ces deux valeurs.
                statValue = scoreFromKillBurst(statValueKill, statValueBurst)

            else:

                #la stat est à récupérer dans le sous-dictionnaire. elle est identifiée
                #directement par l'identifiant secondaire. On la chope directement.
                statValue = dicCurrentPlayerData[statKey][statSubKey]

        return str(statValue)


    def startMenu(self):
        """
        fonction qui s'exécute au début de l'activation du menu
        (voir description de la fonction dans la classe-mère)
        """

        #C'est un peu bourrin, parce qu'on trashe tout les menuText (y compris ceux qui sont
        #statiques, et on les reconstruit tous juste après. Alors que la seule chose qu'on
        #aurait besoin de faire, c'est réactualiser le texte des MenuText affichant les stats.
        #TRODO pour plus tard : faire moins bourrin. (Mais ça veut dire qu'il faudra
        #identifier chaque MenuText affichant une stat, pour pouvoir les retrouver plus tard.
        #C'est un peu lourdingue).
        listMenuText = self.buildAllPlayerMenuText()
        #En plus, avec ces conneries, faut reconstituer la liste total des MenuElem du menu.
        self.listMenuElem = listMenuText + (manyQuit, )
