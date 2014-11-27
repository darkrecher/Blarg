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

date de la derni�re relecture-commentage : 10/02/2011

classe qui fait la gestion du score, des hiscore, des stats, tout �a

vocab :

stat/playerStat : c'est les valeurs r�cup�r�es depuis l'archivist, qui les a
r�cup�r�es depuis le fichier de sauvegarde,pour un joueur en particulier.
Jouer une partie peut faire changer les stats.
Mais les stats ne refl�tent pas l'historique total des parties jou�es.

playerData : �quivalent des playerStat, mais c'est celles qui sont enregistr�es
dans l'archivist. Y'a une conversion playerStat <-> playerData � faire.
Mais en fait la conversion n'a pas grand chose � faire. On recopie tel quel.

score : score actuel de la partie en cours. Un magicien explos� vaut 2 points,
Un magicien tu� sans �tre explos� vaut 1 point. Ce score n'est pas
enregistr� dans les playerStats (sauf si c'est le hiscore de quelque chose)

gameData : ce sont les valeurs des playerStat qui se modifient en fonction de la
partie en cours. On trouve les trucs suivants :

 - nombre total de magicien explos�s, sur toutes les parties jou�es par le joueur,
   y compris la partie en cours. (augmente en m�me temps qu'on explose un magicien)

 - nombre total de magicien tu� (de mani�re normale, ou explos�s),
   sur toutes les parties jou�es par le joueur, y compris la partie en cours.
   (augmente en m�me temps qu'on tue un magicien)

 - couple de valeurs (nbr magi explos�s, nbr magi tu�s) si la partie
   en cours d�passe un ou plusieurs hiscore. Les gameData (et donc les playerStat)
   enregistrent trois hiscores, de trois parties (diff�rentes ou pas) :
    * la partie o� on a fait le plus gros score
    * la partie o� on a explos� le plus de magiciens
    * la partie o� on a tu� le plus de magiciens (explos�s ou pas)

   une m�me partie peut cr�er plusieurs hiscore parmi les trois.
   Dans ce cas, on enregistrera le m�me couple de valeurs (nbr magi explos�s, nbr magi tu�s)
   dans plusieurs hiscore diff�rents.

NDC (note du codeur) : voir NDC de archiv.py (Pas envie de me r�p�ter)

Rien � voir, mais �a me fait penser � l'expression "ton cahier est mal tenu." Haha quelle blague.
"""

#  --- liste des �l�ments de playerStat ---
(
 TOTAL_BURST,     #int : nombre total de magiciens burst (explos�s) sur toutes les parties jou�es
 TOTAL_KILL,      #int : nombre total de magiciens tu�s sur toutes les parties jou�es
 HISCORE_SCORE,   #tuple (kill, burst) de la partie avec le meilleur score
 HISCORE_BURST,   #tuple (kill, burst) de la partie avec le meilleur nbre de magicien burst
 HISCORE_KILL,    #tuple (kill, burst) de la partie avec le meilleur nbre de magicien tu�
) = range(5)

#valeurs des cl�s des dico "hiscore"
(BURST,        #burst. (nombre de magicien explos�s)
 KILL,         #total kill (burst + pas burst).
 CALC_SCORE,   #(c'est pas une vraie cl� pr�sente dans un dico "hiscore", mais �a servira �
               #indiquer qu'on veut r�cup�rer le calcul du score � partir des deux cl�s du dico.
) = range(3)


def scoreFromKillBurst(nbrTotalMagiKilled, nbrMagiBurst):
    """
    calcule la valeur du score � partir des trucidage effectu�es durant une partie

    je met cette fonction pas dans la classe. Car y'en a besoin pour l'affichage des scores,
    � un moment o� y'a pas de classe scoreManager instanci�e.
    Et pis de toute fa�ons elle est stand-alone, un peu, cette fonction.

    entr�es :
        nbrTotalMagiKilled : int. nombre total de magiciens tu�s (explos�s ou non)
        nbrMagiBurst : int. nombre de magiciens explos�s.

    plat-dessert :
        int. le score.
    """

    #on additionne les deux valeurs. Comme �a, les magiciens explos�s sont compt�s
    #deux fois, et les magiciens tu�s normalement sont compt�s une seule fois.
    #et c'est ce que je veux.
    return nbrMagiBurst + nbrTotalMagiKilled



class ScoreManager():
    """
    voir blabla en d�but de fichier
    """

    def __init__(self, archivist):
        """
        constructeur. (thx captain obvious)

        entr�e :
            archivist : r�f�rence vers un objet de la classe �ponyexpress.
                        sera utilis� pour enregistrer dans un fichier de sauvegarde
                        les nouvelles stats modifi�es par les parties jou�es avec ce scoreManager
        """
        self.archivist = archivist

        #nom du joueur en cours, s�lectionn� par le scoreManager
        self.selectedPlayerName = ""
        #stats du joueur en cours
        self.playerStat = {}


    def getPlayerStatFromArchivistPlayerData(self):
        """
        recopiage et conversion des playerData du joueur s�lectionn�,
        vers les player Stat du joueur s�lectionn� aussi, mais dans cette classe

        pr�-requis : faut que le jouer s�lectionn� de l'archivist et du scoreManager
        soit le m�me, sinon �a fout le bordel.
        """

        #Bon, en fait la conversion, on prend juste le truc tel quel. Rien de plus � faire.
        archPlayerStat = self.archivist.dicPlayerData[self.selectedPlayerName]
        #Par contre, il faut pas juste prendre une r�f�rence du dico playerStat.
        #Il faut recopier les donn�es, pour pas pourrir celle de l'archivist
        selectedPlayerStatClone = dict(archPlayerStat)
        self.playerStat = selectedPlayerStatClone


    def selectPlayer(self, selectedPlayerName):
        """
        s�lectionne un joueur en prenant l'un des joueurs enregistr�s dans l'archivist.

        entr�es :
            selectedPlayerName : nom du joueur � s�lectionner. doit �tre une cl� valide
                                 du dico archivist.dicPlayerData. Sinon �a p�te.
        """

        self.selectedPlayerName = selectedPlayerName

        #on r�cup�re les playerData de l'archivist, pour en faire les playerStat du ScoreManager.
        self.getPlayerStatFromArchivistPlayerData()


    def saveScoreInArchive(self):
        """
        demande � l'archivist de sauvegarder toutes les infos de tous les joueurs + les globData,
        en prenant en compte les nouvelles stats du joueur s�lectionn� par ce scoreManager.
        (qui ont, � priori chang�, avec la partie en cours / la partie qui vient d'�tre jou�e)

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a r�ussite.
                     (propag� depuis l'archivist)
        """

        #l'archiviste fait automatiquement une sauvegarde totale,
        #d�s qu'on lui modifie ses donn�es.
        param = (self.selectedPlayerName, self.playerStat)
        return self.archivist.modifyPlayerData(*param)


    def initCurrentGameData(self):
        """
        initalise le score et les gameData en vue de jouer une nouvelle partie.
        """

        #nombre de magiciens tu�s et nombre de magiciens explos�s de la partie en cours.
        self.currentTotMagiKilled = 0
        self.currentMagiBurst = 0

        #calcul initial du score.
        param = (self.currentTotMagiKilled, self.currentMagiBurst)
        self.currentScore = scoreFromKillBurst(*param)

        #calcul du hiscore � partir des playerStat.
        #( = le score de la partie dans laquelle on a fait le plus gros score. aha pl�noasme)
        #putain de nom � rallonge
        param = (self.playerStat[HISCORE_SCORE][KILL],
                 self.playerStat[HISCORE_SCORE][BURST])

        self.hiScore = scoreFromKillBurst(*param)

        #liste de boolean, indiquant les hiscores qui ont �t� d�pass� dans la partie en cours.
        self.dicHiScoreAttained = {
            HISCORE_SCORE : False,
            HISCORE_KILL  : False,
            HISCORE_BURST : False,
        }

        #boolean � la con. utilis� par le code ext�rieur. Pour savoir si faut r�actualiser
        #le label affichant le score
        #(c'est le code ext�rieur qui le met � False apr�s une r�actualisation.)
        #J'ai pas fait de fonction sp�cifique pour le code ext�rieur. Il met directos �
        #False le boolean, et osef. C'est du python bordayl !!
        self.scoreChanged = True


    def updateScore(self, addMagiBurst, addMagiKilledNotBurst):
        """
        met � jour le score et les gameData de la partie en cours, en fonction des
        nouveaux trucidages que vient de faire le h�ros.

        entr�es :
            addMagiBurst : nombre suppl�mentaire de magiciens explos�s, depuis le dernier update
            addMagiKilledNotBurst : nombre suppl�mentaire de magiciens tu�s,
                                    mais pas explos�s, depuis le dernier update.
                                    (attention, c'est pas le total de tu�s.
                                    C'est vraiment que les tu�s de mani�re "normale")
        """

        self.scoreChanged = True

        #conversion nbre de magi tu�s mais pas explos�s -> nbre total de magi tu�s.
        addTotalKill = addMagiBurst + addMagiKilledNotBurst

        #ajout des trucideries suppl�mentaires aux stats cumul�es sur toutes les parties
        self.playerStat[TOTAL_KILL]  += addTotalKill
        self.playerStat[TOTAL_BURST] += addMagiBurst

        #ajout des trucideries suppl�mentaires aux comptages de truciderie de la partie en cours.
        self.currentTotMagiKilled += addTotalKill
        self.currentMagiBurst += addMagiBurst

        #recalcul du score de la partie en cours.
        param = (self.currentTotMagiKilled, self.currentMagiBurst)
        self.currentScore = scoreFromKillBurst(*param)

        # --- mise � jour des high scores, si y'a besoin ---

        #Cette astuce � la con de garder dans un bool�en les atteignage de high score,
        #Ca marche que parce que les nombres de magi tu� et burst ne baissent jamais.
        #Sinon, faudrait r�fl�chir � un truc plus subtil. Mais l�, c'est cool.

        #le hi score score (hahaha)
        if self.currentScore > self.hiScore:
            self.dicHiScoreAttained[HISCORE_SCORE] = True

        #le hi score kills = partie dans laquelle on a tu�+explos� le plus de magiciens
        if self.currentTotMagiKilled > self.playerStat[HISCORE_KILL][KILL]:
            self.dicHiScoreAttained[HISCORE_KILL] = True

        #le hi score burst = partie dans laquelle on a explos� le plus de magiciens
        if self.currentMagiBurst > self.playerStat[HISCORE_BURST][BURST]:
            self.dicHiScoreAttained[HISCORE_BURST] = True

        #pour chaque hiScore d�pass� par la partie en cours, on r�actualise les valeurs kill
        #et burst du dictionnaire de playerStat correspondant.
        for hiScoreKey, hiScoreAttained in self.dicHiScoreAttained.items():
            if hiScoreAttained:
                self.playerStat[hiScoreKey][KILL] = self.currentTotMagiKilled
                self.playerStat[hiScoreKey][BURST] = self.currentMagiBurst

        #TRODO : si on a envie.
        #demander � l'archivist de faire un enregistrement "en live", si un/plusieurs hiScore
        #son atteints. Comme �a, si �a plante par la suite, pour une raison ou une autre,
        #les hiscore seront quand m�me un peu conserv�s.
        #par exemple, on pourrait faire une sauvegarde si currentScore > hiScore_enregistr� + 10

