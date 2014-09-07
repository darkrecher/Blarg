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

date de la dernière relecture-commentage : 15/02/2011

Classe qui gère le chargement et le loadage des donnays dans un fichiay (config + score)

format du fichier de sauvegarde :

au début y'a les GlobData. L'ordre n'est pas imposé.
On s'y retrouve avec les clés (globDataId), qui identifient les données.

V<version. chaine de caractere ASCII quelconque>
L<langage F=francais. E=english>
S<SCREEN W=windowed F=fullscreen>
Y<yargl. Le son. E=Enabled. D=Disabled>

le premier caractère est la globDataId (identifiant de la globData)
la suite de la ligne est la globDataVal (valeur de la globData)

Ensuite on a la config des touches. Qui s'applique à tous les joueurs :
[dnipr] : tag à la con, pour identifier le début de la config de touche
<listKeyCode> : liste de valeurs numérique écrites en chaîne de caractère (décimal).
                séparé par des virgules. C'est les codes des touches pour le jeu.
                dans l'ordre : haut, bas, gauche, droite, feu, recharger
<listCharKey> : liste de chaîne de caractère. séparé par des octets à 0.
                noms des touches correspondant aux codes. Y'a autant d'élément et c'est dans
                le même ordre que les listKeyCode.
                Je suis obligé de stocker ces putains de noms. Car ils ne se déduisent pas
                automatiquement du code de la touche (Ca dépend de l'azert/qwerty/...)
                Ceci dit, y'a des fois, le nom c'est une chaîne vide. Parce qu'on peut
                le déduire automatiquement quand même. Enfin c'est un peu bizarre.
                Voir menuzcon.py

Bien Réchèr. T'as pété dans le bus. Ca sent le soufre. Tu vas tuer tout le monde avec tes
conneries. En plus les gens vont passer à côté de toi. Et pif et paf. Et pif et paf.
Baisse la tête. Reste concentré. Fais semblant de rien. Tout le monde n'y verra et
sentira que du fuego. FUEGO !!

Ensuite on a les infos détaillées pour chaque joueur

[knakes] : tag à la con, pour indiquer le début d'un joueur.
<nom du joueur> : unicode string (enfin on va essayer)
<playerStats> : liste de nombres écrit en chaîne de caractère décimale, séparé par des virgules.
                Ce sont les scores, et autres. L'ordre des valeurs est important>

[knakes]
<nom du joueur suivant>
etc...

La liste des joueurs n'a pas d'ordre précis.

les lignes vides sont pas autorisées. Faut pas déconner, mayrde.

ATTATION !! truc qu'il faut obligatoirement garder d'une version à l'autre du jeu :
le format des GlobData : concaténations <clé><valeur> avec la clé d'une seule lettre.
L'une de ces lignes doit avoir la clé "V", et indiquer la version du format du fichier.
Dans la suite du fichier, on peut faire n'importe quoi. On s'adaptera en fonction de la version.
Pour la version actuelle, c'est "V42".
Je n'en fait rien du tout. Mais c'est de la prévoyance pour la suite.

vocabulaire :

playerStat : les données de hiscore, et le nombres de magiciens tués/explosés du joueur.

playerData : toutes les données du joueur, equivalentes au contenu du fichier de sauvegarde,
             mais utilisables, placées dans un dico.
             playerData contient les playerStat. (Bon en fait, ça contient que ça,
             mais y'aurait pu y avoir d'autres trucs).
playerBytes : toutes les données du joueur (équivalente à playerData),
              mais sous forme d'une suite d'octets,
              à écrire tel quel dans le fichier de sauvegarde / lue tel quel depuis le fichier.

dans le code, il y a très souvent confusion entre les noms playerStat et playerData, car
les playerData sont constitués uniquement des playerStat, et de rien d'autre.
Si je voulais, je pourrais arranger ça. Mais c'est pas critique. Désolé pour la gêne occasionnée.

Archivist.dicPlayerData : dictionnaire. clé : nom du joueur. valeur : sa playerData
                          (ce qui fait que dicPlayerData est un dico de dico, youpi)

le Archivist.dicPlayerData est toujours rigoureusement égal au contenu du fichier de sauvegarde.
Quand on met à jour le dicPlayerData, pour une raison ou pour une autre,
on le sauvegarde en même temps dans le fichier, en totalité.
(On réécrit tout le fichier, j'ai pas trouvé mieux. Et osef)

Pareil pour les globData. On a toujours égalité entre Archivist.dicGlobData, et ce qu'il
y'a d'écrit dans le fichier de sauvegarde.

Et pareil pour la config des touches.

la classe ScoreManager contient un selectedPlayerStat. Mais c'est pas une
référence vers des données de l'archiviste. C'est une copie.
Le ScoreManager se modifie son playerStat dans son coin.
Lors d'une sauvegarde, le ScoreManager apporte son playerStat à l'Archivist, en indiquant
à quel playerName il se rapporte. l'archiviste le recopie pour lui, le place
dans le bon endroit de son self.dicPlayerData, et sauvegarde le tout.

L'archivist est conçu pour (à priori) ne pas tout faire planter si le fichier de sauvegarde
est pourri ou introuvable. Si ça arrive, on prend les valeurs par défaut et on regénère
un fichier correct.
Il est également conçu pour pas tout faire planter si on peut pas écrire dans le fichier.
On doit pouvoir jouer, et se faire la config qu'on veut, même dans ce cas.
Y'a juste que rien ne sera retenu. Ni les scores ni la config.

les fonctions modifyXXXX permettent de changer des données dans l'archivist, et de
sauvegarder le tout immédiatement après.
"le tout" : c'est à dire : globData, config et données de tous les joueurs
Cesfonctions renvoient un boolean, indiquant si la sauvegarde a réussie ou échouée.
Pour l'instant y'a 3 fonctions comme ça. (Voir vers la fin du fichier)

NDC (note du codeur) : Au départ, je voulais faire un truc de ouf avec ce jeu :
la gestion de différents joueurs. Avec chacun un nom, une config, des stats et tout.
Et on aurait pu en créer autant qu'on veut. Avec des chouettes menus. J'ai abandonné l'idée.
En fait y'a que un joueur et demi possible. (Le joueur normal, et celui du edoM edoG).
Du coup, il va peut être rester des bouts de code et des fonctions, qui étaient prévues
pour cette gestion de multi-profil, et qui servent à rien.
Cette NDC est valable pour les classes Archivist et ScoreManager
TRODO pour plus tard : config différente pour chaque joueur. Et plusieurs joueurs, donc, oui.
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
    securedPrint("Woups. Fail importation truc pour l'invincibilité. Désolé")


#indique l'ordre dans lequel écrire les playerStat dans le fichier, et leur type.
#TRODO pour plus tard : c'est une connerie un dico qui stocke des types différents.
#Jamais faut faire ça, après on se complique la vie.
#Enfin ce dico là, c'est pas une connerie. Il stocke des type. Et les types ont tous le même
#type. Mais le dico playerStat, dans l'archiviste, il stocke des tuples et des entiers.
#C'est très très con.
LIST_PLAYER_STAT_KEY_TYPE = (
    (TOTAL_BURST  , int),
    (TOTAL_KILL   , int),
    (HISCORE_SCORE, dict),
    (HISCORE_BURST, dict),
    (HISCORE_KILL , dict),
)

#dictionnaire de correspondance :
#clé d'un type de playerStat -> nombre de données numérique dans cette playerStat
DIC_NBR_DATA_FROM_PLAYER_STAT_TYPE = {
    dict : 2,
    int  : 1,
}
#pour les playerStat de type "dict" (les hiscores),
#indique l'ordre dans lequel écrire les valeurs de ce dict dans le fichier
HISCORE_KEYS_ORDERED = (BURST, KILL)

#longueur des globDataId
LEN_GLOB_DATA_ID = 1

#valeurs des globDataId
GLOB_DATA_ID_LANG    = "L"  #langue du jeu
GLOB_DATA_ID_VERSION = "V"  #version du format du fichier de sauvegarde
GLOB_DATA_ID_SCREEN  = "S"  #mode plein écran ou pas.
GLOB_DATA_ID_SOUND   = "Y"  #son activé ou pas. Y comme Yargler
GLOB_DATA_ID_DOGDOM  = "G"  #code qui activent le edog edom, ou pas.

#liste des globDataId
LIST_GLOB_DATA_ID = (GLOB_DATA_ID_VERSION,
                     GLOB_DATA_ID_LANG,
                     GLOB_DATA_ID_SCREEN,
                     GLOB_DATA_ID_SOUND,
                     GLOB_DATA_ID_DOGDOM,
                    )

#TRODO : pour plus tard. Une classe globData ? Ca déchargerait un peu l'archivist.
#liste des valeurs autorisés, pour les globData qui ont un domaine de valeur restreint.
#Pour les globData qui sont pas dans ce dico, y'a pas de restriction c'est la fête.
GLOB_DATA_AUTHORIZED_VALUE = {
    GLOB_DATA_ID_LANG   : LIST_LANG,
    GLOB_DATA_ID_SCREEN : LIST_SCREEN,
    GLOB_DATA_ID_SOUND  : LIST_SOUND,
}

#mouarf ! le séparator entre une globDataId et sa valeur est une chaîne vide. Hahaha !!! LAUL !!!
GLOB_DATA_ID_SEPARATOR = ""
#position du caractère dans une ligne de globData, à partir duquel on a la globDataVal
GLOB_DATA_VAL_POSITION = LEN_GLOB_DATA_ID + len(GLOB_DATA_ID_SEPARATOR)
#Tag du fichier, indiquant les données d'un joueur.
PLAYER_DATA_SEP = "[knakes]"
#caractère de séparation entre deux playerStat.
PLAYER_STAT_SEPARATOR = ","
#captain obvious
LINE_SEPARATOR = "\n"

#config de touche par défaut. dictionnaire :
# - clé : identifiant de l'action que peut faire le héros.
# - valeur : tuple de 2 elem :
#    * le code de la touche (valeur numérique)
#    * le nom de la touche. Mais on a le droit de foutre des chaînes vides en fait. Haha.
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

#tag du fichier, indiquant le début de la config des touches.
KEY_MAPPING_DATA_SEP = "[dnipr]"

#séparateur pour les éléments de listKeyCode
KEY_CODE_DATA_SEPARATOR = ","
#séparateur pour les éléments de listCharKey
KEY_CHAR_DATA_SEPARATOR = "\x01"

#valeur chiffré du edoMedoGedoC. Le nom bizarre, c'est pour faire une vague obfuscation.
#En fait il faut le lire à l'envers. (Je le dis que ici, même si j'utilise cette astuce
#pourrie un peu partout. Youpi, trop je suis un expert obfuscateur.)
HASHED_DOGDOMEDOC = "963f925fbb7bde454cf3e9ac1e37f30002a18b181f8999fd" + \
                    "00768c5ffbd3d69e50960befeda641eaf8cd30a45f0990d4" + \
                    "96d3cc249e55bfe5484f7b9b178ab530"



class Archivist():
    """
    voir tout le blabla au début de ce fichier de code
    """

    def __init__(self, filePathName=SAVE_FILE_PATHNAME):
        """
        constructeur. (thx captain obvious)

        entrée :
            filePathName : string. chemin et nom du fichier de sauvegarde.

        Pour l'init, on n'a pas encore chargé de données depuis un fichier. Alors
        on met toutes les valeurs par défaut.
        """

        self.filePathName = filePathName

        self.dicPlayerData = {}

        #initialisation des globData avec des valeurs par défaut.
        self.dicGlobData = {
            GLOB_DATA_ID_LANG    : LANG_DEFAULT,
            GLOB_DATA_ID_VERSION : SAVE_FILE_VERSION,
            GLOB_DATA_ID_SCREEN  : SCREEN_DEFAULT,
            GLOB_DATA_ID_SOUND   : SOUND_DEFAULT,
            GLOB_DATA_ID_DOGDOM  : "morceau de brennek",  #valeur qui sert à rien
        }

        #config des touches par défaut.
        self.dicKeyMapping = dict(DEFAULT_KEY_MAPPING)

        #calcul du nombre de données numériques constituant les playerStat
        #Y'en aura besoin pour faire des contrôles lors de la lecture du fichier.
        listNbrPlayerStat = [ DIC_NBR_DATA_FROM_PLAYER_STAT_TYPE[elem[1]]
                              for elem in LIST_PLAYER_STAT_KEY_TYPE
                            ]

        self.nbrPlayerStat = sum(listNbrPlayerStat)

        #handler vers le fichier de sauvegarde.
        self.loadedFile = None
        #booléen indiquant si c'est la toute première fois que le jeu est lancé, ou pas.
        #On part du principe que lorsqu'on ne trouve pas le fichier de sauvegarde,
        #c'est la toute première fois que le jeu est lancé. On garde les données par défaut,
        #et y'aura une sauvegarde du fichier peu de temps après le lancement du jeu.
        #Et pour les exécutions suivantes, tout ira bien.
        self.firstTimeLaunch = True

        #TRODO (osef, ce sera quand y'aura du multi-profil : voir si on peut pas stocker
        #sous forme de byteData toutes les infos des players non sélectionnés.
        #Pour pas avoir à tout recalculer lors des sauvegardes en live.


    def failToLoadArchive(self, errorMessage):
        """
        Balance un message à la gueule du joueur, si le fichier de sauvegarde est pourri.

        entrée :
            errorMessage : unicode string. Message d'erreur indiquant la raison
                           détaillée de pourquoi le fichier est pourri.
        """
        #emission sur stdout du message global, du nom du fichier et du message détaillé
        securedPrint(u"Chargement du fichier de sauvegarde fail.")
        securedPrint(self.filePathName)
        securedPrint(errorMessage)

        #on ferme le fichier de sauvegarde.
        if self.loadedFile is not None:
            self.loadedFile.close()


    def readNextLine(self):
        """
        pitite fonction toute simple pour lire la ligne suivante du fichier de sauvegarde,
        et la renvoyer, dans le plat-dessert. (Putain que je suis drôle avec ça !)
        """
        #et on vire le caractère de saut de ligne à la fin, car tout le monde s'en fout.
        return self.loadedFile.readline().strip(LINE_SEPARATOR)


    def playerBytesFromPlayerData(self, playerName, playerData):
        """
        conversion d'un playerData (tag de playerData + nom + playerStat
        en la suite d'octets à écrire tel quel dans le fichier de sauvegarde.

        entrées :
            playerName : string unicode. Nom du joueur
            playerData : dictionnaire playerData avec toutes les données du joueur.

        plat-dessert :
            playerBytes. string unicode, correspondant aux playerDatas.
        """
        playerStatFlat = []

        #récupération de toutes les playerStat, à partir des playerData
        #et rangement dans une liste "plate", dans un ordre prédefini.
        #(et au passage, conversion des valeur numériques en string, youpi)
        for playerStatKey, playerStatType in LIST_PLAYER_STAT_KEY_TYPE:
            if playerStatType is dict:
                #la playerStat est de type dictionnaire. Il faut donc prendre
                #toutes les valeurs de ce dico, dans un ordre précis
                for hiScoreKey in HISCORE_KEYS_ORDERED:
                    statVal = playerData[playerStatKey][hiScoreKey]
                    playerStatFlat.append(str(statVal))
            else:
                #la playerStat est un int tout simple. On le prend directos.
                statVal = playerData[playerStatKey]
                playerStatFlat.append(str(statVal))

        #création de la suite d'octets correspondant aux playerStat.
        #les valeurs numériques sont écrites en base 10, et séparées par une virgule.
        #Non, la taille du fichier de sauvegarde n'est pas optimisé. Eh bien osef.
        playerStatBytes = PLAYER_STAT_SEPARATOR.join(playerStatFlat)

        #on colle tout le bazar pour faire la suite d'octets total correspondant
        #à toutes les infos de ce joueur.
        playerAllBytes = "".join( (PLAYER_DATA_SEP, LINE_SEPARATOR,
                                   playerName, LINE_SEPARATOR,
                                   playerStatBytes, LINE_SEPARATOR)
                                )
        return playerAllBytes


    def playerStatFromPlayerBytes(self, line):
        """
        récupère les stats d'un joueur, à partir de la ligne d'octets lues depuis le fichier
        de sauvegarde. Les valeurs sont placées dans un dictionnaire, et renvoyées.
        Attention, c'est pas l'équivalent de la fonction ci-dessus : playerBytesFromPlayerData
        Dans cette fonction, on ne récupère que les Stat. Et non pas toutes les Data du player.
        TRODO pour plus tard : d'ailleurs c'est crétin que ce soit pas équivalent.

        entrées :
            line : string. Ligne contenant les playerStat, tel qu'elles ont été lues
                   depuis le fichier de sauvegarde. C'est censé être une suite de
                   valeurs numériques sous forme de string, séparées par des virgules.

        plat-dessert :
            si le format de line est correct : la fonction renvoie le dico playerStat

            si le format de line est pourri : la fonction renvoie None, balance un message
            d'erreur et ferme le fichier de sauvegarde.
        """

        #récupération de la liste des stats, sous forme de string.
        #en prenant en compte le fait qu'elles sont séparées par des virgules.
        listStrPlayerStat = line.split(PLAYER_STAT_SEPARATOR)

        #fail si pas le bon nombre de stats
        if len(listStrPlayerStat) != self.nbrPlayerStat:
            self.failToLoadArchive(u"nombre stat key beurk")
            return None

        #conversion string -> numériques de la liste des stats.
        #si y'en a qui sont pas convertibles, on ne les garde pas.
        #(normalement, elles le sont toutes)
        listIntPlayerStat = [ int(elem) for elem in listStrPlayerStat
                              if elem.isdigit()
                            ]

        #fail si les stats ont pas pu être toutes converties en valeurs numériques.
        if len(listIntPlayerStat) != self.nbrPlayerStat:
            self.failToLoadArchive(u"stat key pas int")
            return None

        playerStat = {}

        #rangement des stats dans le dictionnaire playerStat, en tenant compte de l'ordre
        #dans lequel elles ont été stockées dans le fichier de sauvegarde.
        #les instructions "pop(0)" permettent de récupérer la première stat de la liste,
        #et en même temps de la virer de cette même liste.
        for statKey, statKeyType in LIST_PLAYER_STAT_KEY_TYPE:

            if statKeyType is dict:
                #la stat est un sous-dictionnaire. il faut prendre plusieurs valeurs de la liste,
                #dans un ordre prédefini.
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
        (plus ou moins unicode, je sais pas, je suis pas sur d'avoir pigé le truc),
        à écrire tel quel dans le fichier de sauvegarde

        Il y a les codes des touches (valeurs numériques) et les noms des touches (unicode)

        plat-dessert :
            bytesKeyMapping : string unicode à écrire tel quel dans le fichier,
                              correspondant à la config de touche.

        """
        listKey = []
        listCharKey = []

        #création de la liste des codes de touches, et de la liste des noms, à partir
        #du dictionnaire de config. On prends ces infos dans un ordre bien déterminé.
        for idKey in LIST_KEY_ORDERED:

            (keyMapped, charKeyMapped) = self.dicKeyMapping[idKey]

            #keyMapped, c'est une valeur numérique. On peut la changer en str sans problèmes.
            listKey.append(str(keyMapped))

            #charKeyMapped, c'est de l'unicode. Surtout ne pas écrire str(charKeyMapped) !
            #Car si certains caractèrs sont pas ascii, ça pète. On laisse comme ça,
            #et à priori, quand on l'écrira tel quel dans le fichier, ça pètera pas à la gueule.
            #spoiler : en fait ça va pas péter car on définit un encodage, au moment
            #d'ouvrir le fichier pour écrire/lire dedans.
            listCharKey.append(charKeyMapped)

        #on rassemble ces listes en une grande chaîne de caractère (unicode ou pas),
        #en utilisant les séparateurs qui vont bien.
        strListKey = KEY_CODE_DATA_SEPARATOR.join(listKey)
        strListCharKey = KEY_CHAR_DATA_SEPARATOR.join(listCharKey)

        #et on colle tout ce bordel dans une grande-grande chaîne.
        #(sans oublier le tag qui annonce la config des touches)
        bytesKeyMapping = "".join( (KEY_MAPPING_DATA_SEP, LINE_SEPARATOR,
                                    strListKey, LINE_SEPARATOR,
                                    strListCharKey, LINE_SEPARATOR, )
                                 )

        return bytesKeyMapping


    def dicKeyMappingFromBytes(self, listLine):
        """
        convertit les octets lus depuis le fichier de sauvegarde, censé contenir la config
        des touches, en le dictionnaire de config des touches.

        C'est pas tout à fait équivalent à la fonction ci-dessus, (buildBytesKeyMapping),
        car on chope que les deux lignes contenant les codes et les noms. On ne chope
        pas le tag indiquant la config des touches.

        TRODO pour plus tard : faire que ça soye équivalent.

        entrées :
            listLine : liste de 2 éléments.
                        - string unicode, lue depuis le fichier, contenant les codes des touches
                        - string unicode, lue depuis le fichier, contenant les noms des touches

        plat-dessert :
            boolean. True : la conversion s'est déroulée sans problèmes.
                     False : la conversion a fail.

            De plus, cette fonction remplit l'attribut self.dicKeyMapping, avec les
            valeurs récupérées depuis listLine.

        TRODO pour plus tard : homogénéiser les sorties de cette fonction avec
        playerStatFromPlayerBytes. Là on sort un boolean, l'autre on sort le dico ou None.
        C'est nimp. Et pis ce serait mieux de faire des noms un peu plus explicites,
        qui commencent tous par load ou save. Là c'est vraiment le bordel toute cette classe.
        """

        #TRODO : si on a envie, un jour :  remplacer tous les "key" par des "keyCode"
        #et du coup : CharKey -> KeyChar
        strListKeyCode = listLine[0]
        strListCharKey = listLine[1]

        #récupération des codes et des noms des touches sous forme d'une liste,
        #en se basant sur les séparateurs adequats.
        listKeyCode = strListKeyCode.split(KEY_CODE_DATA_SEPARATOR)
        listCharKey = strListCharKey.split(KEY_CHAR_DATA_SEPARATOR)

        #si pas assez de valeurs dans la liste des codes de touches, ça fail.
        if len(listKeyCode) < len(LIST_KEY_ORDERED):
            self.failToLoadArchive(u"pas assez de valeur dans config touches")
            return False

        #conversion string -> numériques de la liste des KeyCode.
        #si y'en a qui sont pas convertibles, on ne les garde pas.
        #(normalement, ils le sont tous)
        listIntKeyCode = [ int(elem) for elem in listKeyCode
                           if elem.isdigit()
                         ]
        #si tous les codes de touches n'ont pas pu être convertis en int, ça fail.
        if len(listIntKeyCode) < len(LIST_KEY_ORDERED):
            self.failToLoadArchive(u"valeur pourrite dans config touches")
            return False

        #pas de contrôle sur listCharKey. (ce sont des strings unicode)

        #et pas vraiment de contrôle sur le nombre de valeurs de listCharKey.
        #Car il y a un risque que ça se soit mal splitté à cause de mon séparateur pourri : \x01.
        #Si ça arrive,  ça ne mérite pas de tout faire sauter. On balance juste un petit warning.
        #Toutes façons osef de ces noms de touches. c'est juste pour l'affichage dans la config.
        #J'ai mis "différent de", et non pas "inférieur à". Car l'éventuel couille de splittage
        #peut survenir aussi bien dans un sens que dans l'autre.
        if len(listCharKey) != len(LIST_KEY_ORDERED):
            securedPrint(u"WARNINGE LOAD : conf str keys un peu flappie")

        #on prend tous les éléments des deux listes (keyCode et charKey),
        #et on les range dans le dictionnaire de la config de touche, en respectant
        #le bon ordre.
        for idKey in LIST_KEY_ORDERED:

            keyCode = listIntKeyCode.pop(0)

            #si y'a pas assez d'élément dans charKey, à cause couille dans le splittage,
            #eh ben c'est pas grave, on complète la fin avec des chaînes vides.
            if len(listCharKey) > 0:
                charKey = listCharKey.pop(0)
            else:
                charKey = ""

            self.dicKeyMapping[idKey] = keyCode, charKey

        return True


    def loadArchive(self):
        """
        Charge toutes les données (globData + les playerData) depuis le fichier de
        sauvegarde. Et range le tout dans les attributs de la classe qui vont bien

        plat-dessert : boolean
            True : le fichier existe et a été chargé, ou bien
                   le fichier existe pas, et on a pris les valeurs par défaut.
                   (pas de fichier = fonctionnement normal, mais premier lancement du jeu)

            False : le fichier existe, mais il est pourri.
                    des messages d'erreurs ont été émis.

        si le fichier est pourri, on aura peut-être quand même réussi à lire quelques globData.
        On les garde. Et celles qu'on a pas lues, elles auront les valeurs par défaut.
        Pour la config de touches, c'est pareil. On les a lu entièrement, un peu, ou pas du tout.
        Ca ne dérange pas, car on les a initialisés avec des valeurs par défaut. (Au pire, y'a un
        peu de valeurs qui viennent du fichier, et un peu de valeurs par défaut)
        Par contre, pour les joueurs, on s'en fout des bouts d'infos éventuellement récupéré.
        On réinitialisera tout avec les valeurs par défaut. (Ca se passe pas ici, mais dans la
        fonction initAndSaveNewArchive.
        C'est un peu bizarre de faire comme ça. Mais là j'ai plus envie de changer. De toutes 
        façons, si jamais je fais une nouvelle version, y'aura vraiment du multi-profil. Et faudra
        repenser entièrement ce putain d'archivist.
        """

        #tentative de lecture du fichier. Si pas possible, on considère que c'est parce qu'il
        #existe pas. (On ne prend pas en compte d'éventuelles autres raisons bizarres).
        try:
            #encodage en utf-8. A priori, ça explose pas trop quand on prend les octets lus
            #pour en faire une chaîne unicode. (Les accents, tout ça, il s'y retrouve).
            #je pige pas exactement comment ça marche, mais ça marche.
            self.loadedFile = codecs.open(SAVE_FILE_PATHNAME,
                                          mode="r", encoding="utf-8")
        except:
            #pas de fichier. On renvoie True pour dire que tout est OK, mais on se barre direct.
            #la variable self.firstTimeLaunch, initalisée à True, n'a pas été modifiée.
            #il faudra donc créer un joueur par défaut.
            return True

        #autre try except. Celui-ci est bourrin. Mais si il foire, ce sera à cause d'une couille
        #totalement imprévue. Et on considèrera que le chargement du fichier a merdé.
        #Le but de ce try except géant, c'est qu'on puisse jouer même si on n'a pas pu
        #charger/sauver des fichiers, pour une raison qui me serait inconnue.
        try:
            line = self.readNextLine()

            # ------- LECTURE DES GLOBDATA -------

            #on arrête de les lire dès qu'on est à la fin du fichier, ou qu'on rencontre un
            #tag de données quelconque, indiquant qu'on doit passer à autre chose
            while line not in ("", PLAYER_DATA_SEP, KEY_MAPPING_DATA_SEP):

                #la ligne lue doit avoir une taille suffisante pour contenir au moins la globDataId
                #et le séparateur. (Mais la globDataVal peut être vide).
                if len(line) >= GLOB_DATA_VAL_POSITION:

                    #récupération de l'id et de la valeur de la globData
                    globDataId = line[:LEN_GLOB_DATA_ID]
                    globDataVal = line[GLOB_DATA_VAL_POSITION:]

                    #pas de message d'erreur si on trouve une globDataId qui ne correspond à rien.
                    #on la stocke, et on s'en servira pas, et c'est tout.
                    #ça permet de loader des versions plus récentes du fichier sans exploser

                    #vérification si la globData est restreinte à un domaine de valeur
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
                            #C'est pas bon. On laisse la globData a sa valeur par défaut.
                            securedPrint(u"WARNINGE loading:globdata erronay")

                else:
                    securedPrint(u"WARNINGE loading : glob data trop courte")

                line = self.readNextLine()

            # ------- LECTURE DE LA CONFIG DES TOUCHES -------

            if line == KEY_MAPPING_DATA_SEP:
                #y'a deux lignes de données pour le mapping de keys.
                #(Si c'est fait autrement, ça devrait pas, et na).
                line1 = self.readNextLine()
                line2 = self.readNextLine()

                #interprétation des deux lignes de données pour choper la config.
                if not self.dicKeyMappingFromBytes( (line1, line2) ):
                    #Lecture de la config fail. On renvoie pas de message. Ca a déjà été fait.
                    return False

                line = self.readNextLine()

            # ------- LECTURE DES STATS DES JOUEURS -------

            #lecture des données de chaque joueur. chaque itération de ce while lit toutes les
            #données d'un joueur. (C'est à dire qu'on lit plusieurs lignes du fichier)
            while line == PLAYER_DATA_SEP:

                # -- recup du nom du joueur. --
                #Ca fail si il n'y a plus de données dans le fichier.
                line = self.readNextLine()

                #Ca fail aussi si on a chopé une ligne vide.
                if line == "":
                    self.failToLoadArchive(u"nom joueur manquant")
                    return False

                #on prend directement la ligne, pour en faire le nom du joueur. A priori,
                #c'est déjà bien foutu en unicode comme il faut.
                playerName = line

                # -- lecture et contrôle des playerStat, et rangement dans le dictionnaire. --

                line = self.readNextLine()

                #conversion playerBytes -> playerStat.
                #et création de toutes les playerData, à partir de ... Ah ben en
                #fait dans les playerData y'a que les playerStat, et rien de plus.
                #Bon ben si c'est comme ça, alors voilà. J'ai plus rien à faire ici moi.
                playerData = self.playerStatFromPlayerBytes(line)

                if playerData is None:
                    #la lecture des playerStat a fail, mais on n'émet pas de message d'erreur,
                    #car déjà fait par la fonction playerStatFromPlayerBytes
                    return False

                #il faut créer un clone de playerData, faut pas juste donner une référence,
                #sinon ce sera effacé lors de la prochaine boucle. D'où le dict(  )
                self.dicPlayerData[playerName] = dict(playerData)

                line = self.readNextLine()

            # ------- DERNIERES PETITES VERIFS AVANT DE S'EN ALLER -------

            #Il faut avoir loadé le joueur qui a le nom du héros. Sinon on est mal
            #les autres on s'en fout (Le Réchèr et le EdomEdog)
            if NAME_HERO not in self.dicPlayerData:
                self.failToLoadArchive(u"joueur principal non defini. Zutre.")
                return False

            #On est censé être à la fin du fichier. Si c'est pas le cas, fail.
            if line != "":
                self.failToLoadArchive(u"unexpected not-end of file")
                return False

            self.loadedFile.close()

        except Exception, e:
            securedPrint(e)
            self.failToLoadArchive(u"impossible de charger les donnees.")
            return False

        #le fichier de sauvegarde existe, il a pu être lu entièrement, et aucune connerie
        #n'a été détectée. Donc on indique que c'est pas le premier lancement du jeu,
        #et que tout va bien youpi.
        self.firstTimeLaunch = False
        return True


    def saveArchive(self):
        """
        Sauvegarde dans le fichier le contenu de tout le bazar de l'archivist.
        Les infos en elle-même ne sont pas modifiés. On sauvegarde tout tel quel

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a réussite.
        """

        #on essaie d'ouvrir le fichier en écriture.
        #bloc try except géant. C'est un peu facile, mais au moins c'est sécurised
        #Le but de ce try except géant, c'est qu'on puisse jouer même si on peut pas sauver
        #des fichiers, pour une raison qui me serait inconnue.

        try:


            #crac boum encodage. (Voir fonction loadArchive, j'ai rien à dire de plus)
            saveFile = codecs.open(SAVE_FILE_PATHNAME,
                                   mode="w", encoding="utf-8")

            #formatage des globData. On en met une par ligne.
            # <clé> <separateur (qui est une chaîne vide, hahaha)> <valeur>
            #on n'enregistre dans le fichier de sauvegarde que les glob data qu'on connait
            #c'est à dire celles dont la clé est dans LIST_GLOB_DATA_ID.
            #si on en a trouvé d'autres lors du loadage du fichier, on considère
            #qu'elles servent à rien, donc on les sauve pas.
            listGlobData = [ "".join( (str(globDataKey),
                                       GLOB_DATA_ID_SEPARATOR,
                                       str(self.dicGlobData[globDataKey]),
                                       LINE_SEPARATOR)
                                    )
                             for globDataKey in LIST_GLOB_DATA_ID
                           ]

            #on met toute les lignes de globData bout à bout et on les écrit dans le fichier.
            bytesGlobData = "".join(listGlobData)
            saveFile.write(bytesGlobData)

            #conversion de la config des touches en une grosse chaîne unicode qu'on peut
            #écrire telle quelle dans le fichier.
            #TRODO pour plus tard : niveau de détail pas homogène entre l'écriture des globData
            #et l'écriture de la config des touches. C'est moche, mais c'est pas grave.
            bytesKeyMapping = self.buildBytesKeyMapping()

            saveFile.write(bytesKeyMapping)

            #parcours du dico des playerData. on les écrit toute, une par une.
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
        Prend en compte les nouvelles données du joueur spécifié en param,
        et sauvegarde toutes les données dans le fichier.

        entrées:
            PlayerName : nom du joueur pour lequel les playerData doivent être changées.
            newPlayerData : nouvelles données dudit joueur.

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a réussite.
        """

        #ajout du nouveau joueur dans dicPlayerData. ou mise à jour du joueur
        #déjà existant. (On sait pas si on ajoute ou si on modifie, et on s'en fout)
        #
        #Je clone les playerData pour les stocker dans les attributs, car au départ,
        #elles viennent des paramètres passés à la fonction.
        #Je dois m'en garder un exemplaire que pour moi.
        playerDataCloned = dict(newPlayerData)
        self.dicPlayerData[playerName] = playerDataCloned

        #sauvegarde du fichier et renvoi du boolean
        return self.saveArchive()


    def modifyGlobData(self, dicNewGlobData):
        """
        Prend en compte de nouvelles valeurs de globData, spécifiées dans un dictionnaire
        et sauvegarde toutes les données dans le fichier.

        entrées:
            dicNewGlobData : dictionnaire contenant une ou plusieurs valeurs de globData.
            Ces valeurs sont mises à jour avec un dict.update. Ca fait les actions suivantes :
             - si une clé est en même temps dans dicNewGlobData, et dans self.dicGlobData,
               alors la valeur dans self.dicGlobData est modifiée, avec celle de dicNewGlobData
             - si une clé n'est pas dans dicNewGlobData, mais qu'elle est dans self.dicGlobData,
               alors la valeur dans self.dicGlobData n'est pas modifiée
             - si une clé est dans dicNewGlobData, mais pas dans self.dicGlobData,
               alors une nouvelle clé est ajoutée dans self.dicGlobData, avec la valeur de
               dicNewGlobData. (Ce dernier cas ne me sert à rien. Comme j'ai déjà initialisée
               toutes mes globData avec es valeurs par défaut, si je m'en rajoute une autre,
               c'en est forcément une inutile. Mais c'est pas grave, on a le droit).

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a réussite.
        """

        #update du dictionnaire self.dicGlobData avec les données de dicNewGlobData
        self.dicGlobData.update(dicNewGlobData)

        #sauvegarde du fichier et renvoi du boolean
        return self.saveArchive()


    def modifyGlobDataAndKeyMapping(self, newKeyMapping, dicNewGlobData):
        """
        Prend en compte de nouvelles valeurs de globData, spécifiées dans un dictionnaire,
        ainsi qu'une nouvelle config de touches, et sauvegarde toutes les données dans le fichier.

        entrées:
            newKeyMapping : dictionnaire contenant la nouvelle config de touches.
                            il doit être structurée comme DEFAULT_KEY_MAPPING,
                            et contenir exactement les mêmes clés.
            dicNewGlobData : dictionnaire contenant une ou plusieurs valeurs de globData.
                             On met à jour les infos avec un dict.update (voir modifyGlobData)

        plat-dessert :
            boolean. Indique si la sauvegarde a fail, ou si elle a réussite.
        """

        #update du dictionnaire self.dicGlobData avec les données de dicNewGlobData
        self.dicGlobData.update(dicNewGlobData)
        #recupération de la config des touches. (on copie le dictionnaire, pour en
        #avoir une copie en interne dedans la classe, rien que pour soi)
        self.dicKeyMapping = dict(newKeyMapping)

        #sauvegarde du fichier et renvoi du boolean
        return self.saveArchive()


    def isDogDomEnabledFromGlobData(self):
        """
        consulte les globData en interne, et vérifie si elles contiennent la valeur permettant
        d'activer le edoMedoG.

        plat-dessert :
            boolean. indique si le edoMedoG est activé ou pas.
        """

        #récupération de la globData contenant la valeur d'activation.
        #Si y'a pas la globData, y'a pas à réfléchir, le edoMedoG n'est pas activé.
        dogDomEdoc = self.dicGlobData.get(GLOB_DATA_ID_DOGDOM)

        if dogDomEdoc is None:
            return False

        #tentative d'activation avec la valeur, et renvoi du résultat.
        return self.isDogDomEdocValid(dogDomEdoc)


    def isDogDomEdocValid(self, dogDomEdoc):
        """
        indique si un dogDomEdoc est valide ou pas.

        entrées :
            dogDomEdoc : string unicode. permettant de valider ou pas le edoMedoG

        plat-dessert :
            boolean. indique si le edoMedoG est activé ou pas.
        """

        #si y'a pas la bibliothèque permettant de faire du chiffrement SHA, on laisse tomber.
        #c'est bien dommage, et c'est totalement injuste, mais je peux pas faire autrement.
        #à priori, cette biblio est toujours présente dans le python, au moins dans la version
        #que j'utilise. Hein ? Ouais on va dire que ouais.
        if not hashlibEnabled:
            return False

        #conversion unicode -> ascii. Si y'a des caractères bizarres, on les remplaces par
        #des points d'interrogation. (Donc j'ai pas intérêt à avoir foutu de caractère
        #bizarre dans mon dogDomEdoc. Et justement, il se trouve que je l'ai pas fait. Youpi !)
        dogDomEdocAscii = dogDomEdoc.encode("ascii", "replace")
        #chiffrement SHA pour voir si ça correspond.
        hashedDogDomeEdocTry = hashlib.sha512(dogDomEdocAscii).hexdigest()
        #et si c'est bon, le dogDomEdoc permet d'activer le edoMedoG. Tadzam !!!
        return hashedDogDomeEdocTry == HASHED_DOGDOMEDOC


    def _addFixedDataOfRecher(self):
        """
        fonction interne. Ne doit pas être exécutée par le code extérieur,
        sinon y'a aura plus la synchro entre les données du disque dur et cette classe

        Cette fonction ajoute un joueur dans l'archivist, nommée Réchèr,
        avec des playerData déjà définie.
        Le joueur ne peut pas jouer avec ce "Réchèr", ses playerData resteront toujours les mêmes.
        Ca sert juste à l'affichage dans les scores. Je voulais faire mon mégalo, un petit peu.
        """

        #Vous avez vu mes scores ? C'est pas de la nioniotte ça ! Et tout est véridique.
        playerDataOfRecher = {
            TOTAL_BURST   :  5779,
            TOTAL_KILL    : 15925,
            HISCORE_SCORE : { BURST : 113, KILL : 304},
            HISCORE_BURST : { BURST : 113, KILL : 304},
            HISCORE_KILL  : { BURST :  20, KILL : 325},
        }

        #ajout de "Réchèr" dans le dictionnaire des données des joueurs.
        self.dicPlayerData[NAME_RECHER] = playerDataOfRecher


    def _addNewPlayerData(self, newPlayerName):
        """
        fonction interne. Ne doit pas être exécutée par le code extérieur,
        sinon y'a aura plus la synchro entre les données du disque dur et cette classe

        Ajoute un nouveau joueur, avec des playerData ayant les valeurs initiales
        (c'est à dire tout à zero).

        entrées :
            newPlayerName : string unicode. Nom du nouveau joueur à ajouter.
        """

        #dictionnaire contenant les playerStat initiales
        newPlayerStat = {
            TOTAL_KILL    : 0,
            TOTAL_BURST   : 0,
            HISCORE_SCORE : { BURST:0, KILL:0 },
            HISCORE_KILL  : { BURST:0, KILL:0 },
            HISCORE_BURST : { BURST:0, KILL:0 },
        }

        #ajout du nouveau joueur dans le dictionnaire des données des joueurs.
        self.dicPlayerData[newPlayerName] = newPlayerStat


    def initAndSaveNewArchive(self, nameEntered=""):
        """
        crée un tout nouveau fichier de sauvegarde. Par exemple, si c'est la première
        fois que le jeu est exécuté, ou si le fichier existant est tout pourri.

        entrées :
            nameEntered : string unicode. Nom que le joueur a tapé dans la zone
                          de texte au début du jeu. Comme le message débile de présentation
                          l'indique, ce nom n'est pas enregistré comme nom de joueur.
                          Mais il est utilisé pour l'activation éventuelle du edoGedoM

        plat-dessert :
            boolean. Indique si la création et la sauvegarde du fichier a fail,
                     ou si elle a réussite.
        """

        #ajout du joueur "Réchèr", qui sert à rien, et du joueur normal, qui contiendra
        #les playerStat des parties jouées normalement.
        self._addFixedDataOfRecher()
        self._addNewPlayerData(NAME_HERO)

        #tntative d'activation du edoGedoM, selon le nom saisi par le joueur.
        if self.isDogDomEdocValid(nameEntered):
            #C'est bon, on peut activer le edoGedoM. Dans ce cas, il faut stocker la
            #globData contenant le nom saisi (car ce nom est le doGedoMedoC, il faut
            #donc le garder précieusement.)
            self.dicGlobData[GLOB_DATA_ID_DOGDOM] = nameEntered
            #création du joueur spécifique, qui stockera les playerData des parties
            #jouées en edoGedoM.
            self._addNewPlayerData(NAME_DOGDOM)

        #si le nom saisi n'a pas permi de valider le edoGedoM, pas la peine de l'enregistrer,
        #on s'en fout complètement.

        #création et sauvegarde du fichier avec toutes ces nouvelles données dedans.
        return self.saveArchive()


