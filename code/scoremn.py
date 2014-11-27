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

date de la dernière relecture-commentage : 10/02/2011

classe qui fait la gestion du score, des hiscore, des stats, tout ça

vocab :

stat/playerStat : c'est les valeurs récupérées depuis l'archivist, qui les a
récupérées depuis le fichier de sauvegarde,pour un joueur en particulier.
Jouer une partie peut faire changer les stats.
Mais les stats ne reflètent pas l'historique total des parties jouées.

playerData : équivalent des playerStat, mais c'est celles qui sont enregistrées
dans l'archivist. Y'a une conversion playerStat <-> playerData à faire.
Mais en fait la conversion n'a pas grand chose à faire. On recopie tel quel.

score : score actuel de la partie en cours. Un magicien explosé vaut 2 points,
Un magicien tué sans être explosé vaut 1 point. Ce score n'est pas
enregistré dans les playerStats (sauf si c'est le hiscore de quelque chose)

gameData : ce sont les valeurs des playerStat qui se modifient en fonction de la
partie en cours. On trouve les trucs suivants :

 - nombre total de magicien explosés, sur toutes les parties jouées par le joueur,
   y compris la partie en cours. (augmente en même temps qu'on explose un magicien)

 - nombre total de magicien tué (de manière normale, ou explosés),
   sur toutes les parties jouées par le joueur, y compris la partie en cours.
   (augmente en même temps qu'on tue un magicien)

 - couple de valeurs (nbr magi explosés, nbr magi tués) si la partie
   en cours dépasse un ou plusieurs hiscore. Les gameData (et donc les playerStat)
   enregistrent trois hiscores, de trois parties (différentes ou pas) :
    * la partie où on a fait le plus gros score
    * la partie où on a explosé le plus de magiciens
    * la partie où on a tué le plus de magiciens (explosés ou pas)

   une même partie peut créer plusieurs hiscore parmi les trois.
   Dans ce cas, on enregistrera le même couple de valeurs (nbr magi explosés, nbr magi tués)
   dans plusieurs hiscore différents.

NDC (note du codeur) : voir NDC de archiv.py (Pas envie de me répéter)

Rien à voir, mais ça me fait penser à l'expression "ton cahier est mal tenu." Haha quelle blague.
"""

#  --- liste des éléments de playerStat ---
(
 TOTAL_BURST,     #int : nombre total de magiciens burst (explosés) sur toutes les parties jouées
 TOTAL_KILL,      #int : nombre total de magiciens tués sur toutes les parties jouées
 HISCORE_SCORE,   #tuple (kill, burst) de la partie avec le meilleur score
 HISCORE_BURST,   #tuple (kill, burst) de la partie avec le meilleur nbre de magicien burst
 HISCORE_KILL,    #tuple (kill, burst) de la partie avec le meilleur nbre de magicien tué
) = range(5)

#valeurs des clés des dico "hiscore"
(BURST,        #burst. (nombre de magicien explosés)
 KILL,         #total kill (burst + pas burst).
 CALC_SCORE,   #(c'est pas une vraie clé présente dans un dico "hiscore", mais ça servira à
               #indiquer qu'on veut récupérer le calcul du score à partir des deux clés du dico.
) = range(3)


def scoreFromKillBurst(nbrTotalMagiKilled, nbrMagiBurst):
    """
    calcule la valeur du score à partir des trucidage effectuées durant une partie

    je met cette fonction pas dans la classe. Car y'en a besoin pour l'affichage des scores,
    à un moment où y'a pas de classe scoreManager instanciée.
    Et pis de toute façons elle est stand-alone, un peu, cette fonction.

    entrées :
        nbrTotalMagiKilled : int. nombre total de magiciens tués (explosés ou non)
        nbrMagiBurst : int. nombre de magiciens explosés.

    plat-dessert :
        int. le score.
    """

    #on additionne les deux valeurs. Comme ça, les magiciens explosés sont comptés
    #deux fois, et les magiciens tués normalement sont comptés une seule fois.
    #et c'est ce que je veux.
    return nbrMagiBurst + nbrTotalMagiKilled



class ScoreManager():
    """
    voir blabla en début de fichier
    """

    def __init__(self, archivist):
        """
        constructeur. (thx captain obvious)

        entrée :
            archivist : référence vers un objet de la classe éponyexpress.
                        sera utilisé pour enregistrer dans un fichier de sauvegarde
                        les nouvelles stats modifiées par les parties jouées avec ce scoreManager
        """
        self.archivist = archivist

        #nom du joueur en cours, sélectionné par le scoreManager
        self.selectedPlayerName = ""
        #stats du joueur en cours
        self.playerStat = {}


    def getPlayerStatFromArchivistPlayerData(self):
        """
        recopiage et conversion des playerData du joueur sélectionné,
        vers les player Stat du joueur sélectionné aussi, mais dans cette classe

        pré-requis : faut que le jouer sélectionné de l'archivist et du scoreManager
        soit le même, sinon ça fout le bordel.
        """

        #Bon, en fait la conversion, on prend juste le truc tel quel. Rien de plus à faire.
        archPlayerStat = self.archivist.dicPlayerData[self.selectedPlayerName]
        #Par contre, il faut pas juste prendre une référence du dico playerStat.
        #Il faut recopier les données, pour pas pourrir celle de l'archivist
        selectedPlayerStatClone = dict(archPlayerStat)
        self.playerStat = selectedPlayerStatClone


    def selectPlayer(self, selectedPlayerName):
        """
        sélectionne un joueur en prenant l'un des joueurs enregistrés dans l'archivist.

        entrées :
            selectedPlayerName : nom du joueur à sélectionner. doit être une clé valide
                                 du dico archivist.dicPlayerData. Sinon ça pète.
        """

        self.selectedPlayerName = selectedPlayerName

        #on récupère les playerData de l'archivist, pour en faire les playerStat du ScoreManager.
        self.getPlayerStatFromArchivistPlayerData()


    def saveScoreInArchive(self):
        """
        demande à l'archivist de sauvegarder toutes les infos de tous les joueurs + les globData,
        en prenant en compte les nouvelles stats du joueur sélectionné par ce scoreManager.
        (qui ont, à priori changé, avec la partie en cours / la partie qui vient d'être jouée)

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a réussite.
                     (propagé depuis l'archivist)
        """

        #l'archiviste fait automatiquement une sauvegarde totale,
        #dès qu'on lui modifie ses données.
        param = (self.selectedPlayerName, self.playerStat)
        return self.archivist.modifyPlayerData(*param)


    def initCurrentGameData(self):
        """
        initalise le score et les gameData en vue de jouer une nouvelle partie.
        """

        #nombre de magiciens tués et nombre de magiciens explosés de la partie en cours.
        self.currentTotMagiKilled = 0
        self.currentMagiBurst = 0

        #calcul initial du score.
        param = (self.currentTotMagiKilled, self.currentMagiBurst)
        self.currentScore = scoreFromKillBurst(*param)

        #calcul du hiscore à partir des playerStat.
        #( = le score de la partie dans laquelle on a fait le plus gros score. aha plénoasme)
        #putain de nom à rallonge
        param = (self.playerStat[HISCORE_SCORE][KILL],
                 self.playerStat[HISCORE_SCORE][BURST])

        self.hiScore = scoreFromKillBurst(*param)

        #liste de boolean, indiquant les hiscores qui ont été dépassé dans la partie en cours.
        self.dicHiScoreAttained = {
            HISCORE_SCORE : False,
            HISCORE_KILL  : False,
            HISCORE_BURST : False,
        }

        #boolean à la con. utilisé par le code extérieur. Pour savoir si faut réactualiser
        #le label affichant le score
        #(c'est le code extérieur qui le met à False après une réactualisation.)
        #J'ai pas fait de fonction spécifique pour le code extérieur. Il met directos à
        #False le boolean, et osef. C'est du python bordayl !!
        self.scoreChanged = True


    def updateScore(self, addMagiBurst, addMagiKilledNotBurst):
        """
        met à jour le score et les gameData de la partie en cours, en fonction des
        nouveaux trucidages que vient de faire le héros.

        entrées :
            addMagiBurst : nombre supplémentaire de magiciens explosés, depuis le dernier update
            addMagiKilledNotBurst : nombre supplémentaire de magiciens tués,
                                    mais pas explosés, depuis le dernier update.
                                    (attention, c'est pas le total de tués.
                                    C'est vraiment que les tués de manière "normale")
        """

        self.scoreChanged = True

        #conversion nbre de magi tués mais pas explosés -> nbre total de magi tués.
        addTotalKill = addMagiBurst + addMagiKilledNotBurst

        #ajout des trucideries supplémentaires aux stats cumulées sur toutes les parties
        self.playerStat[TOTAL_KILL]  += addTotalKill
        self.playerStat[TOTAL_BURST] += addMagiBurst

        #ajout des trucideries supplémentaires aux comptages de truciderie de la partie en cours.
        self.currentTotMagiKilled += addTotalKill
        self.currentMagiBurst += addMagiBurst

        #recalcul du score de la partie en cours.
        param = (self.currentTotMagiKilled, self.currentMagiBurst)
        self.currentScore = scoreFromKillBurst(*param)

        # --- mise à jour des high scores, si y'a besoin ---

        #Cette astuce à la con de garder dans un booléen les atteignage de high score,
        #Ca marche que parce que les nombres de magi tué et burst ne baissent jamais.
        #Sinon, faudrait réfléchir à un truc plus subtil. Mais là, c'est cool.

        #le hi score score (hahaha)
        if self.currentScore > self.hiScore:
            self.dicHiScoreAttained[HISCORE_SCORE] = True

        #le hi score kills = partie dans laquelle on a tué+explosé le plus de magiciens
        if self.currentTotMagiKilled > self.playerStat[HISCORE_KILL][KILL]:
            self.dicHiScoreAttained[HISCORE_KILL] = True

        #le hi score burst = partie dans laquelle on a explosé le plus de magiciens
        if self.currentMagiBurst > self.playerStat[HISCORE_BURST][BURST]:
            self.dicHiScoreAttained[HISCORE_BURST] = True

        #pour chaque hiScore dépassé par la partie en cours, on réactualise les valeurs kill
        #et burst du dictionnaire de playerStat correspondant.
        for hiScoreKey, hiScoreAttained in self.dicHiScoreAttained.items():
            if hiScoreAttained:
                self.playerStat[hiScoreKey][KILL] = self.currentTotMagiKilled
                self.playerStat[hiScoreKey][BURST] = self.currentMagiBurst

        #TRODO : si on a envie.
        #demander à l'archivist de faire un enregistrement "en live", si un/plusieurs hiScore
        #son atteints. Comme ça, si ça plante par la suite, pour une raison ou une autre,
        #les hiscore seront quand même un peu conservés.
        #par exemple, on pourrait faire une sauvegarde si currentScore > hiScore_enregistré + 10

