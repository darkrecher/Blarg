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

date de la derni�re relecture-commentage : 15/02/2011

Classe qui g�re le chargement et le loadage des donnays dans un fichiay (config + score)

format du fichier de sauvegarde :

au d�but y'a les GlobData. L'ordre n'est pas impos�.
On s'y retrouve avec les cl�s (globDataId), qui identifient les donn�es.

V<version. chaine de caractere ASCII quelconque>
L<langage F=francais. E=english>
S<SCREEN W=windowed F=fullscreen>
Y<yargl. Le son. E=Enabled. D=Disabled>

le premier caract�re est la globDataId (identifiant de la globData)
la suite de la ligne est la globDataVal (valeur de la globData)

Ensuite on a la config des touches. Qui s'applique � tous les joueurs :
[dnipr] : tag � la con, pour identifier le d�but de la config de touche
<listKeyCode> : liste de valeurs num�rique �crites en cha�ne de caract�re (d�cimal).
                s�par� par des virgules. C'est les codes des touches pour le jeu.
                dans l'ordre : haut, bas, gauche, droite, feu, recharger
<listCharKey> : liste de cha�ne de caract�re. s�par� par des octets � 0.
                noms des touches correspondant aux codes. Y'a autant d'�l�ment et c'est dans
                le m�me ordre que les listKeyCode.
                Je suis oblig� de stocker ces putains de noms. Car ils ne se d�duisent pas
                automatiquement du code de la touche (Ca d�pend de l'azert/qwerty/...)
                Ceci dit, y'a des fois, le nom c'est une cha�ne vide. Parce qu'on peut
                le d�duire automatiquement quand m�me. Enfin c'est un peu bizarre.
                Voir menuzcon.py

Bien R�ch�r. T'as p�t� dans le bus. Ca sent le soufre. Tu vas tuer tout le monde avec tes
conneries. En plus les gens vont passer � c�t� de toi. Et pif et paf. Et pif et paf.
Baisse la t�te. Reste concentr�. Fais semblant de rien. Tout le monde n'y verra et
sentira que du fuego. FUEGO !!

Ensuite on a les infos d�taill�es pour chaque joueur

[knakes] : tag � la con, pour indiquer le d�but d'un joueur.
<nom du joueur> : unicode string (enfin on va essayer)
<playerStats> : liste de nombres �crit en cha�ne de caract�re d�cimale, s�par� par des virgules.
                Ce sont les scores, et autres. L'ordre des valeurs est important>

[knakes]
<nom du joueur suivant>
etc...

La liste des joueurs n'a pas d'ordre pr�cis.

les lignes vides sont pas autoris�es. Faut pas d�conner, mayrde.

ATTATION !! truc qu'il faut obligatoirement garder d'une version � l'autre du jeu :
le format des GlobData : concat�nations <cl�><valeur> avec la cl� d'une seule lettre.
L'une de ces lignes doit avoir la cl� "V", et indiquer la version du format du fichier.
Dans la suite du fichier, on peut faire n'importe quoi. On s'adaptera en fonction de la version.
Pour la version actuelle, c'est "V42".
Je n'en fait rien du tout. Mais c'est de la pr�voyance pour la suite.

vocabulaire :

playerStat : les donn�es de hiscore, et le nombres de magiciens tu�s/explos�s du joueur.

playerData : toutes les donn�es du joueur, equivalentes au contenu du fichier de sauvegarde,
             mais utilisables, plac�es dans un dico.
             playerData contient les playerStat. (Bon en fait, �a contient que �a,
             mais y'aurait pu y avoir d'autres trucs).
playerBytes : toutes les donn�es du joueur (�quivalente � playerData),
              mais sous forme d'une suite d'octets,
              � �crire tel quel dans le fichier de sauvegarde / lue tel quel depuis le fichier.

dans le code, il y a tr�s souvent confusion entre les noms playerStat et playerData, car
les playerData sont constitu�s uniquement des playerStat, et de rien d'autre.
Si je voulais, je pourrais arranger �a. Mais c'est pas critique. D�sol� pour la g�ne occasionn�e.

Archivist.dicPlayerData : dictionnaire. cl� : nom du joueur. valeur : sa playerData
                          (ce qui fait que dicPlayerData est un dico de dico, youpi)

le Archivist.dicPlayerData est toujours rigoureusement �gal au contenu du fichier de sauvegarde.
Quand on met � jour le dicPlayerData, pour une raison ou pour une autre,
on le sauvegarde en m�me temps dans le fichier, en totalit�.
(On r��crit tout le fichier, j'ai pas trouv� mieux. Et osef)

Pareil pour les globData. On a toujours �galit� entre Archivist.dicGlobData, et ce qu'il
y'a d'�crit dans le fichier de sauvegarde.

Et pareil pour la config des touches.

la classe ScoreManager contient un selectedPlayerStat. Mais c'est pas une
r�f�rence vers des donn�es de l'archiviste. C'est une copie.
Le ScoreManager se modifie son playerStat dans son coin.
Lors d'une sauvegarde, le ScoreManager apporte son playerStat � l'Archivist, en indiquant
� quel playerName il se rapporte. l'archiviste le recopie pour lui, le place
dans le bon endroit de son self.dicPlayerData, et sauvegarde le tout.

L'archivist est con�u pour (� priori) ne pas tout faire planter si le fichier de sauvegarde
est pourri ou introuvable. Si �a arrive, on prend les valeurs par d�faut et on reg�n�re
un fichier correct.
Il est �galement con�u pour pas tout faire planter si on peut pas �crire dans le fichier.
On doit pouvoir jouer, et se faire la config qu'on veut, m�me dans ce cas.
Y'a juste que rien ne sera retenu. Ni les scores ni la config.

les fonctions modifyXXXX permettent de changer des donn�es dans l'archivist, et de
sauvegarder le tout imm�diatement apr�s.
"le tout" : c'est � dire : globData, config et donn�es de tous les joueurs
Cesfonctions renvoient un boolean, indiquant si la sauvegarde a r�ussie ou �chou�e.
Pour l'instant y'a 3 fonctions comme �a. (Voir vers la fin du fichier)

NDC (note du codeur) : Au d�part, je voulais faire un truc de ouf avec ce jeu :
la gestion de diff�rents joueurs. Avec chacun un nom, une config, des stats et tout.
Et on aurait pu en cr�er autant qu'on veut. Avec des chouettes menus. J'ai abandonn� l'id�e.
En fait y'a que un joueur et demi possible. (Le joueur normal, et celui du edoM edoG).
Du coup, il va peut �tre rester des bouts de code et des fonctions, qui �taient pr�vues
pour cette gestion de multi-profil, et qui servent � rien.
Cette NDC est valable pour les classes Archivist et ScoreManager
TRODO pour plus tard : config diff�rente pour chaque joueur. Et plusieurs joueurs, donc, oui.
"""

import codecs

import pygame.locals
pygl = pygame.locals

from common import (SAVE_FILE_PATHNAME, SAVE_FILE_VERSION,
                    SCREEN_WINDOWED, SCREEN_FULL, LIST_SCREEN, SCREEN_DEFAULT,
                    LANG_FRENCH, LANG_ENGL, LIST_LANG, LANG_DEFAULT,
                    SOUND_ENABLED, SOUND_DISABLED, LIST_SOUND, SOUND_DEFAULT,
                    KEY_DIR_UP, KEY_DIR_DOWN, KEY_DIR_RIGHT, KEY_DIR_LEFT,
                    KEY_FIRE, KEY_RELOAD,
                    securedPrint,
                    NAME_RECHER, NAME_HERO, NAME_DOGDOM)

from scoremn import (TOTAL_KILL, TOTAL_BURST,
                     HISCORE_SCORE, HISCORE_KILL, HISCORE_BURST,
                     BURST, KILL)

hashlibEnabled = True

try:
    import hashlib
except:
    hashlibEnabled = False
    securedPrint("Woups. Fail importation truc pour l'invincibilit�. D�sol�")


#indique l'ordre dans lequel �crire les playerStat dans le fichier, et leur type.
#TRODO pour plus tard : c'est une connerie un dico qui stocke des types diff�rents.
#Jamais faut faire �a, apr�s on se complique la vie.
#Enfin ce dico l�, c'est pas une connerie. Il stocke des type. Et les types ont tous le m�me
#type. Mais le dico playerStat, dans l'archiviste, il stocke des tuples et des entiers.
#C'est tr�s tr�s con.
LIST_PLAYER_STAT_KEY_TYPE = (
    (TOTAL_BURST  , int),
    (TOTAL_KILL   , int),
    (HISCORE_SCORE, dict),
    (HISCORE_BURST, dict),
    (HISCORE_KILL , dict),
)

#dictionnaire de correspondance :
#cl� d'un type de playerStat -> nombre de donn�es num�rique dans cette playerStat
DIC_NBR_DATA_FROM_PLAYER_STAT_TYPE = {
    dict : 2,
    int  : 1,
}
#pour les playerStat de type "dict" (les hiscores),
#indique l'ordre dans lequel �crire les valeurs de ce dict dans le fichier
HISCORE_KEYS_ORDERED = (BURST, KILL)

#longueur des globDataId
LEN_GLOB_DATA_ID = 1

#valeurs des globDataId
GLOB_DATA_ID_LANG    = "L"  #langue du jeu
GLOB_DATA_ID_VERSION = "V"  #version du format du fichier de sauvegarde
GLOB_DATA_ID_SCREEN  = "S"  #mode plein �cran ou pas.
GLOB_DATA_ID_SOUND   = "Y"  #son activ� ou pas. Y comme Yargler
GLOB_DATA_ID_DOGDOM  = "G"  #code qui activent le edog edom, ou pas.

#liste des globDataId
LIST_GLOB_DATA_ID = (GLOB_DATA_ID_VERSION,
                     GLOB_DATA_ID_LANG,
                     GLOB_DATA_ID_SCREEN,
                     GLOB_DATA_ID_SOUND,
                     GLOB_DATA_ID_DOGDOM,
                    )

#TRODO : pour plus tard. Une classe globData ? Ca d�chargerait un peu l'archivist.
#liste des valeurs autoris�s, pour les globData qui ont un domaine de valeur restreint.
#Pour les globData qui sont pas dans ce dico, y'a pas de restriction c'est la f�te.
GLOB_DATA_AUTHORIZED_VALUE = {
    GLOB_DATA_ID_LANG   : LIST_LANG,
    GLOB_DATA_ID_SCREEN : LIST_SCREEN,
    GLOB_DATA_ID_SOUND  : LIST_SOUND,
}

#mouarf ! le s�parator entre une globDataId et sa valeur est une cha�ne vide. Hahaha !!! LAUL !!!
GLOB_DATA_ID_SEPARATOR = ""
#position du caract�re dans une ligne de globData, � partir duquel on a la globDataVal
GLOB_DATA_VAL_POSITION = LEN_GLOB_DATA_ID + len(GLOB_DATA_ID_SEPARATOR)
#Tag du fichier, indiquant les donn�es d'un joueur.
PLAYER_DATA_SEP = "[knakes]"
#caract�re de s�paration entre deux playerStat.
PLAYER_STAT_SEPARATOR = ","
#captain obvious
LINE_SEPARATOR = "\n"

#config de touche par d�faut. dictionnaire :
# - cl� : identifiant de l'action que peut faire le h�ros.
# - valeur : tuple de 2 elem :
#    * le code de la touche (valeur num�rique)
#    * le nom de la touche. Mais on a le droit de foutre des cha�nes vides en fait. Haha.
DEFAULT_KEY_MAPPING = {
    KEY_DIR_UP    : (pygl.K_UP,    "",),
    KEY_DIR_DOWN  : (pygl.K_DOWN,  "",),
    KEY_DIR_RIGHT : (pygl.K_RIGHT, "",),
    KEY_DIR_LEFT  : (pygl.K_LEFT,  "",),
    KEY_FIRE      : (pygl.K_e,     "",),
    KEY_RELOAD    : (pygl.K_r,     "",),
}

#ordre dans lequel on doit ranger les touches, pour faire les listes listKeyCode et listCharKey.
LIST_KEY_ORDERED = (KEY_DIR_UP, KEY_DIR_DOWN,
                    KEY_DIR_RIGHT, KEY_DIR_LEFT,
                    KEY_FIRE, KEY_RELOAD)

#tag du fichier, indiquant le d�but de la config des touches.
KEY_MAPPING_DATA_SEP = "[dnipr]"

#s�parateur pour les �l�ments de listKeyCode
KEY_CODE_DATA_SEPARATOR = ","
#s�parateur pour les �l�ments de listCharKey
KEY_CHAR_DATA_SEPARATOR = "\x01"

#valeur chiffr� du edoMedoGedoC. Le nom bizarre, c'est pour faire une vague obfuscation.
#En fait il faut le lire � l'envers. (Je le dis que ici, m�me si j'utilise cette astuce
#pourrie un peu partout. Youpi, trop je suis un expert obfuscateur.)
HASHED_DOGDOMEDOC = "963f925fbb7bde454cf3e9ac1e37f30002a18b181f8999fd" + \
                    "00768c5ffbd3d69e50960befeda641eaf8cd30a45f0990d4" + \
                    "96d3cc249e55bfe5484f7b9b178ab530"



class Archivist():
    """
    voir tout le blabla au d�but de ce fichier de code
    """

    def __init__(self, filePathName=SAVE_FILE_PATHNAME):
        """
        constructeur. (thx captain obvious)

        entr�e :
            filePathName : string. chemin et nom du fichier de sauvegarde.

        Pour l'init, on n'a pas encore charg� de donn�es depuis un fichier. Alors
        on met toutes les valeurs par d�faut.
        """

        self.filePathName = filePathName

        self.dicPlayerData = {}

        #initialisation des globData avec des valeurs par d�faut.
        self.dicGlobData = {
            GLOB_DATA_ID_LANG    : LANG_DEFAULT,
            GLOB_DATA_ID_VERSION : SAVE_FILE_VERSION,
            GLOB_DATA_ID_SCREEN  : SCREEN_DEFAULT,
            GLOB_DATA_ID_SOUND   : SOUND_DEFAULT,
            GLOB_DATA_ID_DOGDOM  : "morceau de brennek",  #valeur qui sert � rien
        }

        #config des touches par d�faut.
        self.dicKeyMapping = dict(DEFAULT_KEY_MAPPING)

        #calcul du nombre de donn�es num�riques constituant les playerStat
        #Y'en aura besoin pour faire des contr�les lors de la lecture du fichier.
        listNbrPlayerStat = [ DIC_NBR_DATA_FROM_PLAYER_STAT_TYPE[elem[1]]
                              for elem in LIST_PLAYER_STAT_KEY_TYPE
                            ]

        self.nbrPlayerStat = sum(listNbrPlayerStat)

        #handler vers le fichier de sauvegarde.
        self.loadedFile = None
        #bool�en indiquant si c'est la toute premi�re fois que le jeu est lanc�, ou pas.
        #On part du principe que lorsqu'on ne trouve pas le fichier de sauvegarde,
        #c'est la toute premi�re fois que le jeu est lanc�. On garde les donn�es par d�faut,
        #et y'aura une sauvegarde du fichier peu de temps apr�s le lancement du jeu.
        #Et pour les ex�cutions suivantes, tout ira bien.
        self.firstTimeLaunch = True

        #TRODO (osef, ce sera quand y'aura du multi-profil : voir si on peut pas stocker
        #sous forme de byteData toutes les infos des players non s�lectionn�s.
        #Pour pas avoir � tout recalculer lors des sauvegardes en live.


    def failToLoadArchive(self, errorMessage):
        """
        Balance un message � la gueule du joueur, si le fichier de sauvegarde est pourri.

        entr�e :
            errorMessage : unicode string. Message d'erreur indiquant la raison
                           d�taill�e de pourquoi le fichier est pourri.
        """
        #emission sur stdout du message global, du nom du fichier et du message d�taill�
        securedPrint(u"Chargement du fichier de sauvegarde fail.")
        securedPrint(self.filePathName)
        securedPrint(errorMessage)

        #on ferme le fichier de sauvegarde.
        if self.loadedFile is not None:
            self.loadedFile.close()


    def readNextLine(self):
        """
        pitite fonction toute simple pour lire la ligne suivante du fichier de sauvegarde,
        et la renvoyer, dans le plat-dessert. (Putain que je suis dr�le avec �a !)
        """
        #et on vire le caract�re de saut de ligne � la fin, car tout le monde s'en fout.
        return self.loadedFile.readline().strip(LINE_SEPARATOR)


    def playerBytesFromPlayerData(self, playerName, playerData):
        """
        conversion d'un playerData (tag de playerData + nom + playerStat
        en la suite d'octets � �crire tel quel dans le fichier de sauvegarde.

        entr�es :
            playerName : string unicode. Nom du joueur
            playerData : dictionnaire playerData avec toutes les donn�es du joueur.

        plat-dessert :
            playerBytes. string unicode, correspondant aux playerDatas.
        """
        playerStatFlat = []

        #r�cup�ration de toutes les playerStat, � partir des playerData
        #et rangement dans une liste "plate", dans un ordre pr�defini.
        #(et au passage, conversion des valeur num�riques en string, youpi)
        for playerStatKey, playerStatType in LIST_PLAYER_STAT_KEY_TYPE:
            if playerStatType is dict:
                #la playerStat est de type dictionnaire. Il faut donc prendre
                #toutes les valeurs de ce dico, dans un ordre pr�cis
                for hiScoreKey in HISCORE_KEYS_ORDERED:
                    statVal = playerData[playerStatKey][hiScoreKey]
                    playerStatFlat.append(str(statVal))
            else:
                #la playerStat est un int tout simple. On le prend directos.
                statVal = playerData[playerStatKey]
                playerStatFlat.append(str(statVal))

        #cr�ation de la suite d'octets correspondant aux playerStat.
        #les valeurs num�riques sont �crites en base 10, et s�par�es par une virgule.
        #Non, la taille du fichier de sauvegarde n'est pas optimis�. Eh bien osef.
        playerStatBytes = PLAYER_STAT_SEPARATOR.join(playerStatFlat)

        #on colle tout le bazar pour faire la suite d'octets total correspondant
        #� toutes les infos de ce joueur.
        playerAllBytes = "".join( (PLAYER_DATA_SEP, LINE_SEPARATOR,
                                   playerName, LINE_SEPARATOR,
                                   playerStatBytes, LINE_SEPARATOR)
                                )
        return playerAllBytes


    def playerStatFromPlayerBytes(self, line):
        """
        r�cup�re les stats d'un joueur, � partir de la ligne d'octets lues depuis le fichier
        de sauvegarde. Les valeurs sont plac�es dans un dictionnaire, et renvoy�es.
        Attention, c'est pas l'�quivalent de la fonction ci-dessus : playerBytesFromPlayerData
        Dans cette fonction, on ne r�cup�re que les Stat. Et non pas toutes les Data du player.
        TRODO pour plus tard : d'ailleurs c'est cr�tin que ce soit pas �quivalent.

        entr�es :
            line : string. Ligne contenant les playerStat, tel qu'elles ont �t� lues
                   depuis le fichier de sauvegarde. C'est cens� �tre une suite de
                   valeurs num�riques sous forme de string, s�par�es par des virgules.

        plat-dessert :
            si le format de line est correct : la fonction renvoie le dico playerStat

            si le format de line est pourri : la fonction renvoie None, balance un message
            d'erreur et ferme le fichier de sauvegarde.
        """

        #r�cup�ration de la liste des stats, sous forme de string.
        #en prenant en compte le fait qu'elles sont s�par�es par des virgules.
        listStrPlayerStat = line.split(PLAYER_STAT_SEPARATOR)

        #fail si pas le bon nombre de stats
        if len(listStrPlayerStat) != self.nbrPlayerStat:
            self.failToLoadArchive(u"nombre stat key beurk")
            return None

        #conversion string -> num�riques de la liste des stats.
        #si y'en a qui sont pas convertibles, on ne les garde pas.
        #(normalement, elles le sont toutes)
        listIntPlayerStat = [ int(elem) for elem in listStrPlayerStat
                              if elem.isdigit()
                            ]

        #fail si les stats ont pas pu �tre toutes converties en valeurs num�riques.
        if len(listIntPlayerStat) != self.nbrPlayerStat:
            self.failToLoadArchive(u"stat key pas int")
            return None

        playerStat = {}

        #rangement des stats dans le dictionnaire playerStat, en tenant compte de l'ordre
        #dans lequel elles ont �t� stock�es dans le fichier de sauvegarde.
        #les instructions "pop(0)" permettent de r�cup�rer la premi�re stat de la liste,
        #et en m�me temps de la virer de cette m�me liste.
        for statKey, statKeyType in LIST_PLAYER_STAT_KEY_TYPE:

            if statKeyType is dict:
                #la stat est un sous-dictionnaire. il faut prendre plusieurs valeurs de la liste,
                #dans un ordre pr�defini.
                playerStat[statKey] = {}
                for hiScoreKey in HISCORE_KEYS_ORDERED:
                    playerStat[statKey][hiScoreKey] = listIntPlayerStat.pop(0)
            else:
                #la stat est une valeur simple. On la prend tel quel.
                playerStat[statKey] = listIntPlayerStat.pop(0)

        return playerStat


    def buildBytesKeyMapping(self):
        """
        A partir de la conguration des touches, construit une liste d'octet
        (plus ou moins unicode, je sais pas, je suis pas sur d'avoir pig� le truc),
        � �crire tel quel dans le fichier de sauvegarde

        Il y a les codes des touches (valeurs num�riques) et les noms des touches (unicode)

        plat-dessert :
            bytesKeyMapping : string unicode � �crire tel quel dans le fichier,
                              correspondant � la config de touche.

        """
        listKey = []
        listCharKey = []

        #cr�ation de la liste des codes de touches, et de la liste des noms, � partir
        #du dictionnaire de config. On prends ces infos dans un ordre bien d�termin�.
        for idKey in LIST_KEY_ORDERED:

            (keyMapped, charKeyMapped) = self.dicKeyMapping[idKey]

            #keyMapped, c'est une valeur num�rique. On peut la changer en str sans probl�mes.
            listKey.append(str(keyMapped))

            #charKeyMapped, c'est de l'unicode. Surtout ne pas �crire str(charKeyMapped) !
            #Car si certains caract�rs sont pas ascii, �a p�te. On laisse comme �a,
            #et � priori, quand on l'�crira tel quel dans le fichier, �a p�tera pas � la gueule.
            #spoiler : en fait �a va pas p�ter car on d�finit un encodage, au moment
            #d'ouvrir le fichier pour �crire/lire dedans.
            listCharKey.append(charKeyMapped)

        #on rassemble ces listes en une grande cha�ne de caract�re (unicode ou pas),
        #en utilisant les s�parateurs qui vont bien.
        strListKey = KEY_CODE_DATA_SEPARATOR.join(listKey)
        strListCharKey = KEY_CHAR_DATA_SEPARATOR.join(listCharKey)

        #et on colle tout ce bordel dans une grande-grande cha�ne.
        #(sans oublier le tag qui annonce la config des touches)
        bytesKeyMapping = "".join( (KEY_MAPPING_DATA_SEP, LINE_SEPARATOR,
                                    strListKey, LINE_SEPARATOR,
                                    strListCharKey, LINE_SEPARATOR, )
                                 )

        return bytesKeyMapping


    def dicKeyMappingFromBytes(self, listLine):
        """
        convertit les octets lus depuis le fichier de sauvegarde, cens� contenir la config
        des touches, en le dictionnaire de config des touches.

        C'est pas tout � fait �quivalent � la fonction ci-dessus, (buildBytesKeyMapping),
        car on chope que les deux lignes contenant les codes et les noms. On ne chope
        pas le tag indiquant la config des touches.

        TRODO pour plus tard : faire que �a soye �quivalent.

        entr�es :
            listLine : liste de 2 �l�ments.
                        - string unicode, lue depuis le fichier, contenant les codes des touches
                        - string unicode, lue depuis le fichier, contenant les noms des touches

        plat-dessert :
            boolean. True : la conversion s'est d�roul�e sans probl�mes.
                     False : la conversion a fail.

            De plus, cette fonction remplit l'attribut self.dicKeyMapping, avec les
            valeurs r�cup�r�es depuis listLine.

        TRODO pour plus tard : homog�n�iser les sorties de cette fonction avec
        playerStatFromPlayerBytes. L� on sort un boolean, l'autre on sort le dico ou None.
        C'est nimp. Et pis ce serait mieux de faire des noms un peu plus explicites,
        qui commencent tous par load ou save. L� c'est vraiment le bordel toute cette classe.
        """

        #TRODO : si on a envie, un jour :  remplacer tous les "key" par des "keyCode"
        #et du coup : CharKey -> KeyChar
        strListKeyCode = listLine[0]
        strListCharKey = listLine[1]

        #r�cup�ration des codes et des noms des touches sous forme d'une liste,
        #en se basant sur les s�parateurs adequats.
        listKeyCode = strListKeyCode.split(KEY_CODE_DATA_SEPARATOR)
        listCharKey = strListCharKey.split(KEY_CHAR_DATA_SEPARATOR)

        #si pas assez de valeurs dans la liste des codes de touches, �a fail.
        if len(listKeyCode) < len(LIST_KEY_ORDERED):
            self.failToLoadArchive(u"pas assez de valeur dans config touches")
            return False

        #conversion string -> num�riques de la liste des KeyCode.
        #si y'en a qui sont pas convertibles, on ne les garde pas.
        #(normalement, ils le sont tous)
        listIntKeyCode = [ int(elem) for elem in listKeyCode
                           if elem.isdigit()
                         ]
        #si tous les codes de touches n'ont pas pu �tre convertis en int, �a fail.
        if len(listIntKeyCode) < len(LIST_KEY_ORDERED):
            self.failToLoadArchive(u"valeur pourrite dans config touches")
            return False

        #pas de contr�le sur listCharKey. (ce sont des strings unicode)

        #et pas vraiment de contr�le sur le nombre de valeurs de listCharKey.
        #Car il y a un risque que �a se soit mal splitt� � cause de mon s�parateur pourri : \x01.
        #Si �a arrive,  �a ne m�rite pas de tout faire sauter. On balance juste un petit warning.
        #Toutes fa�ons osef de ces noms de touches. c'est juste pour l'affichage dans la config.
        #J'ai mis "diff�rent de", et non pas "inf�rieur �". Car l'�ventuel couille de splittage
        #peut survenir aussi bien dans un sens que dans l'autre.
        if len(listCharKey) != len(LIST_KEY_ORDERED):
            securedPrint(u"WARNINGE LOAD : conf str keys un peu flappie")

        #on prend tous les �l�ments des deux listes (keyCode et charKey),
        #et on les range dans le dictionnaire de la config de touche, en respectant
        #le bon ordre.
        for idKey in LIST_KEY_ORDERED:

            keyCode = listIntKeyCode.pop(0)

            #si y'a pas assez d'�l�ment dans charKey, � cause couille dans le splittage,
            #eh ben c'est pas grave, on compl�te la fin avec des cha�nes vides.
            if len(listCharKey) > 0:
                charKey = listCharKey.pop(0)
            else:
                charKey = ""

            self.dicKeyMapping[idKey] = keyCode, charKey

        return True


    def loadArchive(self):
        """
        Charge toutes les donn�es (globData + les playerData) depuis le fichier de
        sauvegarde. Et range le tout dans les attributs de la classe qui vont bien

        plat-dessert : boolean
            True : le fichier existe et a �t� charg�, ou bien
                   le fichier existe pas, et on a pris les valeurs par d�faut.
                   (pas de fichier = fonctionnement normal, mais premier lancement du jeu)

            False : le fichier existe, mais il est pourri.
                    des messages d'erreurs ont �t� �mis.

        si le fichier est pourri, on aura peut-�tre quand m�me r�ussi � lire quelques globData.
        On les garde. Et celles qu'on a pas lues, elles auront les valeurs par d�faut.
        Pour la config de touches, c'est pareil. On les a lu enti�rement, un peu, ou pas du tout.
        Ca ne d�range pas, car on les a initialis�s avec des valeurs par d�faut. (Au pire, y'a un
        peu de valeurs qui viennent du fichier, et un peu de valeurs par d�faut)
        Par contre, pour les joueurs, on s'en fout des bouts d'infos �ventuellement r�cup�r�.
        On r�initialisera tout avec les valeurs par d�faut. (Ca se passe pas ici, mais dans la
        fonction initAndSaveNewArchive.
        C'est un peu bizarre de faire comme �a. Mais l� j'ai plus envie de changer. De toutes 
        fa�ons, si jamais je fais une nouvelle version, y'aura vraiment du multi-profil. Et faudra
        repenser enti�rement ce putain d'archivist.
        """

        #tentative de lecture du fichier. Si pas possible, on consid�re que c'est parce qu'il
        #existe pas. (On ne prend pas en compte d'�ventuelles autres raisons bizarres).
        try:
            #encodage en utf-8. A priori, �a explose pas trop quand on prend les octets lus
            #pour en faire une cha�ne unicode. (Les accents, tout �a, il s'y retrouve).
            #je pige pas exactement comment �a marche, mais �a marche.
            self.loadedFile = codecs.open(SAVE_FILE_PATHNAME,
                                          mode="r", encoding="utf-8")
        except:
            #pas de fichier. On renvoie True pour dire que tout est OK, mais on se barre direct.
            #la variable self.firstTimeLaunch, initalis�e � True, n'a pas �t� modifi�e.
            #il faudra donc cr�er un joueur par d�faut.
            return True

        #autre try except. Celui-ci est bourrin. Mais si il foire, ce sera � cause d'une couille
        #totalement impr�vue. Et on consid�rera que le chargement du fichier a merd�.
        #Le but de ce try except g�ant, c'est qu'on puisse jouer m�me si on n'a pas pu
        #charger/sauver des fichiers, pour une raison qui me serait inconnue.
        try:
            line = self.readNextLine()

            # ------- LECTURE DES GLOBDATA -------

            #on arr�te de les lire d�s qu'on est � la fin du fichier, ou qu'on rencontre un
            #tag de donn�es quelconque, indiquant qu'on doit passer � autre chose
            while line not in ("", PLAYER_DATA_SEP, KEY_MAPPING_DATA_SEP):

                #la ligne lue doit avoir une taille suffisante pour contenir au moins la globDataId
                #et le s�parateur. (Mais la globDataVal peut �tre vide).
                if len(line) >= GLOB_DATA_VAL_POSITION:

                    #r�cup�ration de l'id et de la valeur de la globData
                    globDataId = line[:LEN_GLOB_DATA_ID]
                    globDataVal = line[GLOB_DATA_VAL_POSITION:]

                    #pas de message d'erreur si on trouve une globDataId qui ne correspond � rien.
                    #on la stocke, et on s'en servira pas, et c'est tout.
                    #�a permet de loader des versions plus r�centes du fichier sans exploser

                    #v�rification si la globData est restreinte � un domaine de valeur
                    #nom trop long. Fuck
                    globi = GLOB_DATA_AUTHORIZED_VALUE
                    listAuthorizedValues = globi.get(globDataId)

                    if listAuthorizedValues is None:
                        #pas de restricition. On prend directement la valeur, et youpi.
                        self.dicGlobData[globDataId] = globDataVal
                    else:
                        #il y a une restriction.
                        if globDataVal in listAuthorizedValues:
                            #c'est bon, c'est dans le domaine de valeur. On prend la globData
                            self.dicGlobData[globDataId] = globDataVal
                        else:
                            #C'est pas bon. On laisse la globData a sa valeur par d�faut.
                            securedPrint(u"WARNINGE loading:globdata erronay")

                else:
                    securedPrint(u"WARNINGE loading : glob data trop courte")

                line = self.readNextLine()

            # ------- LECTURE DE LA CONFIG DES TOUCHES -------

            if line == KEY_MAPPING_DATA_SEP:
                #y'a deux lignes de donn�es pour le mapping de keys.
                #(Si c'est fait autrement, �a devrait pas, et na).
                line1 = self.readNextLine()
                line2 = self.readNextLine()

                #interpr�tation des deux lignes de donn�es pour choper la config.
                if not self.dicKeyMappingFromBytes( (line1, line2) ):
                    #Lecture de la config fail. On renvoie pas de message. Ca a d�j� �t� fait.
                    return False

                line = self.readNextLine()

            # ------- LECTURE DES STATS DES JOUEURS -------

            #lecture des donn�es de chaque joueur. chaque it�ration de ce while lit toutes les
            #donn�es d'un joueur. (C'est � dire qu'on lit plusieurs lignes du fichier)
            while line == PLAYER_DATA_SEP:

                # -- recup du nom du joueur. --
                #Ca fail si il n'y a plus de donn�es dans le fichier.
                line = self.readNextLine()

                #Ca fail aussi si on a chop� une ligne vide.
                if line == "":
                    self.failToLoadArchive(u"nom joueur manquant")
                    return False

                #on prend directement la ligne, pour en faire le nom du joueur. A priori,
                #c'est d�j� bien foutu en unicode comme il faut.
                playerName = line

                # -- lecture et contr�le des playerStat, et rangement dans le dictionnaire. --

                line = self.readNextLine()

                #conversion playerBytes -> playerStat.
                #et cr�ation de toutes les playerData, � partir de ... Ah ben en
                #fait dans les playerData y'a que les playerStat, et rien de plus.
                #Bon ben si c'est comme �a, alors voil�. J'ai plus rien � faire ici moi.
                playerData = self.playerStatFromPlayerBytes(line)

                if playerData is None:
                    #la lecture des playerStat a fail, mais on n'�met pas de message d'erreur,
                    #car d�j� fait par la fonction playerStatFromPlayerBytes
                    return False

                #il faut cr�er un clone de playerData, faut pas juste donner une r�f�rence,
                #sinon ce sera effac� lors de la prochaine boucle. D'o� le dict(  )
                self.dicPlayerData[playerName] = dict(playerData)

                line = self.readNextLine()

            # ------- DERNIERES PETITES VERIFS AVANT DE S'EN ALLER -------

            #Il faut avoir load� le joueur qui a le nom du h�ros. Sinon on est mal
            #les autres on s'en fout (Le R�ch�r et le EdomEdog)
            if NAME_HERO not in self.dicPlayerData:
                self.failToLoadArchive(u"joueur principal non defini. Zutre.")
                return False

            #On est cens� �tre � la fin du fichier. Si c'est pas le cas, fail.
            if line != "":
                self.failToLoadArchive(u"unexpected not-end of file")
                return False

            self.loadedFile.close()

        except Exception, e:
            securedPrint(e)
            self.failToLoadArchive(u"impossible de charger les donnees.")
            return False

        #le fichier de sauvegarde existe, il a pu �tre lu enti�rement, et aucune connerie
        #n'a �t� d�tect�e. Donc on indique que c'est pas le premier lancement du jeu,
        #et que tout va bien youpi.
        self.firstTimeLaunch = False
        return True


    def saveArchive(self):
        """
        Sauvegarde dans le fichier le contenu de tout le bazar de l'archivist.
        Les infos en elle-m�me ne sont pas modifi�s. On sauvegarde tout tel quel

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a r�ussite.
        """

        #on essaie d'ouvrir le fichier en �criture.
        #bloc try except g�ant. C'est un peu facile, mais au moins c'est s�curised
        #Le but de ce try except g�ant, c'est qu'on puisse jouer m�me si on peut pas sauver
        #des fichiers, pour une raison qui me serait inconnue.

        try:


            #crac boum encodage. (Voir fonction loadArchive, j'ai rien � dire de plus)
            saveFile = codecs.open(SAVE_FILE_PATHNAME,
                                   mode="w", encoding="utf-8")

            #formatage des globData. On en met une par ligne.
            # <cl�> <separateur (qui est une cha�ne vide, hahaha)> <valeur>
            #on n'enregistre dans le fichier de sauvegarde que les glob data qu'on connait
            #c'est � dire celles dont la cl� est dans LIST_GLOB_DATA_ID.
            #si on en a trouv� d'autres lors du loadage du fichier, on consid�re
            #qu'elles servent � rien, donc on les sauve pas.
            listGlobData = [ "".join( (str(globDataKey),
                                       GLOB_DATA_ID_SEPARATOR,
                                       str(self.dicGlobData[globDataKey]),
                                       LINE_SEPARATOR)
                                    )
                             for globDataKey in LIST_GLOB_DATA_ID
                           ]

            #on met toute les lignes de globData bout � bout et on les �crit dans le fichier.
            bytesGlobData = "".join(listGlobData)
            saveFile.write(bytesGlobData)

            #conversion de la config des touches en une grosse cha�ne unicode qu'on peut
            #�crire telle quelle dans le fichier.
            #TRODO pour plus tard : niveau de d�tail pas homog�ne entre l'�criture des globData
            #et l'�criture de la config des touches. C'est moche, mais c'est pas grave.
            bytesKeyMapping = self.buildBytesKeyMapping()

            saveFile.write(bytesKeyMapping)

            #parcours du dico des playerData. on les �crit toute, une par une.
            for playerName, playerData in self.dicPlayerData.items():
                param = (playerName, playerData)
                playerBytes = self.playerBytesFromPlayerData(*param)
                saveFile.write(playerBytes)

            saveFile.close()

        except Exception, e:
            securedPrint(u"impossible de sauvegarder les donnees.")
            securedPrint(u"el fichieto der safegardskeit failed. Nyi pen.")
            securedPrint(e)
            return False

        return True


    def modifyPlayerData(self, playerName, newPlayerData):
        """
        Prend en compte les nouvelles donn�es du joueur sp�cifi� en param,
        et sauvegarde toutes les donn�es dans le fichier.

        entr�es:
            PlayerName : nom du joueur pour lequel les playerData doivent �tre chang�es.
            newPlayerData : nouvelles donn�es dudit joueur.

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a r�ussite.
        """

        #ajout du nouveau joueur dans dicPlayerData. ou mise � jour du joueur
        #d�j� existant. (On sait pas si on ajoute ou si on modifie, et on s'en fout)
        #
        #Je clone les playerData pour les stocker dans les attributs, car au d�part,
        #elles viennent des param�tres pass�s � la fonction.
        #Je dois m'en garder un exemplaire que pour moi.
        playerDataCloned = dict(newPlayerData)
        self.dicPlayerData[playerName] = playerDataCloned

        #sauvegarde du fichier et renvoi du boolean
        return self.saveArchive()


    def modifyGlobData(self, dicNewGlobData):
        """
        Prend en compte de nouvelles valeurs de globData, sp�cifi�es dans un dictionnaire
        et sauvegarde toutes les donn�es dans le fichier.

        entr�es:
            dicNewGlobData : dictionnaire contenant une ou plusieurs valeurs de globData.
            Ces valeurs sont mises � jour avec un dict.update. Ca fait les actions suivantes :
             - si une cl� est en m�me temps dans dicNewGlobData, et dans self.dicGlobData,
               alors la valeur dans self.dicGlobData est modifi�e, avec celle de dicNewGlobData
             - si une cl� n'est pas dans dicNewGlobData, mais qu'elle est dans self.dicGlobData,
               alors la valeur dans self.dicGlobData n'est pas modifi�e
             - si une cl� est dans dicNewGlobData, mais pas dans self.dicGlobData,
               alors une nouvelle cl� est ajout�e dans self.dicGlobData, avec la valeur de
               dicNewGlobData. (Ce dernier cas ne me sert � rien. Comme j'ai d�j� initialis�e
               toutes mes globData avec es valeurs par d�faut, si je m'en rajoute une autre,
               c'en est forc�ment une inutile. Mais c'est pas grave, on a le droit).

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a r�ussite.
        """

        #update du dictionnaire self.dicGlobData avec les donn�es de dicNewGlobData
        self.dicGlobData.update(dicNewGlobData)

        #sauvegarde du fichier et renvoi du boolean
        return self.saveArchive()


    def modifyGlobDataAndKeyMapping(self, newKeyMapping, dicNewGlobData):
        """
        Prend en compte de nouvelles valeurs de globData, sp�cifi�es dans un dictionnaire,
        ainsi qu'une nouvelle config de touches, et sauvegarde toutes les donn�es dans le fichier.

        entr�es:
            newKeyMapping : dictionnaire contenant la nouvelle config de touches.
                            il doit �tre structur�e comme DEFAULT_KEY_MAPPING,
                            et contenir exactement les m�mes cl�s.
            dicNewGlobData : dictionnaire contenant une ou plusieurs valeurs de globData.
                             On met � jour les infos avec un dict.update (voir modifyGlobData)

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a r�ussite.
        """

        #update du dictionnaire self.dicGlobData avec les donn�es de dicNewGlobData
        self.dicGlobData.update(dicNewGlobData)
        #recup�ration de la config des touches. (on copie le dictionnaire, pour en
        #avoir une copie en interne dedans la classe, rien que pour soi)
        self.dicKeyMapping = dict(newKeyMapping)

        #sauvegarde du fichier et renvoi du boolean
        return self.saveArchive()


    def isDogDomEnabledFromGlobData(self):
        """
        consulte les globData en interne, et v�rifie si elles contiennent la valeur permettant
        d'activer le edoMedoG.

        plat-dessert :
            boolean. indique si le edoMedoG est activ� ou pas.
        """

        #r�cup�ration de la globData contenant la valeur d'activation.
        #Si y'a pas la globData, y'a pas � r�fl�chir, le edoMedoG n'est pas activ�.
        dogDomEdoc = self.dicGlobData.get(GLOB_DATA_ID_DOGDOM)

        if dogDomEdoc is None:
            return False

        #tentative d'activation avec la valeur, et renvoi du r�sultat.
        return self.isDogDomEdocValid(dogDomEdoc)


    def isDogDomEdocValid(self, dogDomEdoc):
        """
        indique si un dogDomEdoc est valide ou pas.

        entr�es :
            dogDomEdoc : string unicode. permettant de valider ou pas le edoMedoG

        plat-dessert :
            boolean. indique si le edoMedoG est activ� ou pas.
        """

        #si y'a pas la biblioth�que permettant de faire du chiffrement SHA, on laisse tomber.
        #c'est bien dommage, et c'est totalement injuste, mais je peux pas faire autrement.
        #� priori, cette biblio est toujours pr�sente dans le python, au moins dans la version
        #que j'utilise. Hein ? Ouais on va dire que ouais.
        if not hashlibEnabled:
            return False

        #conversion unicode -> ascii. Si y'a des caract�res bizarres, on les remplaces par
        #des points d'interrogation. (Donc j'ai pas int�r�t � avoir foutu de caract�re
        #bizarre dans mon dogDomEdoc. Et justement, il se trouve que je l'ai pas fait. Youpi !)
        dogDomEdocAscii = dogDomEdoc.encode("ascii", "replace")
        #chiffrement SHA pour voir si �a correspond.
        hashedDogDomeEdocTry = hashlib.sha512(dogDomEdocAscii).hexdigest()
        #et si c'est bon, le dogDomEdoc permet d'activer le edoMedoG. Tadzam !!!
        return hashedDogDomeEdocTry == HASHED_DOGDOMEDOC


    def _addFixedDataOfRecher(self):
        """
        fonction interne. Ne doit pas �tre ex�cut�e par le code ext�rieur,
        sinon y'a aura plus la synchro entre les donn�es du disque dur et cette classe

        Cette fonction ajoute un joueur dans l'archivist, nomm�e R�ch�r,
        avec des playerData d�j� d�finie.
        Le joueur ne peut pas jouer avec ce "R�ch�r", ses playerData resteront toujours les m�mes.
        Ca sert juste � l'affichage dans les scores. Je voulais faire mon m�galo, un petit peu.
        """

        #Vous avez vu mes scores ? C'est pas de la nioniotte �a ! Et tout est v�ridique.
        playerDataOfRecher = {
            TOTAL_BURST   :  5779,
            TOTAL_KILL    : 15925,
            HISCORE_SCORE : { BURST : 113, KILL : 304},
            HISCORE_BURST : { BURST : 113, KILL : 304},
            HISCORE_KILL  : { BURST :  20, KILL : 325},
        }

        #ajout de "R�ch�r" dans le dictionnaire des donn�es des joueurs.
        self.dicPlayerData[NAME_RECHER] = playerDataOfRecher


    def _addNewPlayerData(self, newPlayerName):
        """
        fonction interne. Ne doit pas �tre ex�cut�e par le code ext�rieur,
        sinon y'a aura plus la synchro entre les donn�es du disque dur et cette classe

        Ajoute un nouveau joueur, avec des playerData ayant les valeurs initiales
        (c'est � dire tout � zero).

        entr�es :
            newPlayerName : string unicode. Nom du nouveau joueur � ajouter.
        """

        #dictionnaire contenant les playerStat initiales
        newPlayerStat = {
            TOTAL_KILL    : 0,
            TOTAL_BURST   : 0,
            HISCORE_SCORE : { BURST:0, KILL:0 },
            HISCORE_KILL  : { BURST:0, KILL:0 },
            HISCORE_BURST : { BURST:0, KILL:0 },
        }

        #ajout du nouveau joueur dans le dictionnaire des donn�es des joueurs.
        self.dicPlayerData[newPlayerName] = newPlayerStat


    def initAndSaveNewArchive(self, nameEntered=""):
        """
        cr�e un tout nouveau fichier de sauvegarde. Par exemple, si c'est la premi�re
        fois que le jeu est ex�cut�, ou si le fichier existant est tout pourri.

        entr�es :
            nameEntered : string unicode. Nom que le joueur a tap� dans la zone
                          de texte au d�but du jeu. Comme le message d�bile de pr�sentation
                          l'indique, ce nom n'est pas enregistr� comme nom de joueur.
                          Mais il est utilis� pour l'activation �ventuelle du edoGedoM

        plat-dessert :
            boolean. Indique si la cr�ation et la sauvegarde du fichier a fail,
                     ou si elle a r�ussite.
        """

        #ajout du joueur "R�ch�r", qui sert � rien, et du joueur normal, qui contiendra
        #les playerStat des parties jou�es normalement.
        self._addFixedDataOfRecher()
        self._addNewPlayerData(NAME_HERO)

        #tntative d'activation du edoGedoM, selon le nom saisi par le joueur.
        if self.isDogDomEdocValid(nameEntered):
            #C'est bon, on peut activer le edoGedoM. Dans ce cas, il faut stocker la
            #globData contenant le nom saisi (car ce nom est le doGedoMedoC, il faut
            #donc le garder pr�cieusement.)
            self.dicGlobData[GLOB_DATA_ID_DOGDOM] = nameEntered
            #cr�ation du joueur sp�cifique, qui stockera les playerData des parties
            #jou�es en edoGedoM.
            self._addNewPlayerData(NAME_DOGDOM)

        #si le nom saisi n'a pas permi de valider le edoGedoM, pas la peine de l'enregistrer,
        #on s'en fout compl�tement.

        #cr�ation et sauvegarde du fichier avec toutes ces nouvelles donn�es dedans.
        return self.saveArchive()


