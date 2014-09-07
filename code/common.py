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

date de la dernière relecture-commentage : 29/03/2011

bibliothèque avec tous les trucs communs à plusieurs trucs

un peu de vocabulaire. C'est de l'obvious, mais ça prouve que moi, je suis clair dans
mes noms de variables. (Je dis absolument pas ça par rapport à la merde magmatesque qui se fait
dans mon boulot de merde) :
XXX_DIRECTORY_NAME : chemin vers un répertoire (relatif ou absolu, mais en général, relatif)
XXX_FILENAME : nom d'un fichier (que le nom, sans le chemin)
XXX_PATHNAME : chemin et nom d'un fichier (y'a tout dedans) (relatif ou absolu)
"""

import os
import random
import pygame

import pygame.locals
pygl = pygame.locals


def pyRect(top=0, left=0, width=0, height=0):
    """
    permet de générer un pygame.Rect, sans forcément donner la hauteur et la largeur.

    pourquoi ils ont pas mis eux-même des valeurs par défaut bordel !!
    (ou alors c'est moi qui suis à la masse et j'ai loupé une astuce.)
    """
    return pygame.Rect(top, left, width, height)


def pyRectTuple(tuplePos=(0, 0), tupleSize=(0, 0)):
    """
    permet de générer un pygame.Rect à partir de tuples,
    sans forcément donner la hauteur et la largeur.

    pourquoi ils ont pas mis eux-même des valeurs par défaut bordel !!
    (tiens, j'ai l'impression d'avoir déjà dit ça).
    """
    return pygame.Rect(tuplePos, tupleSize)


#texte écrit dans le titre de la fenêtre du jeu (si on joue en windowed)
GAME_CAPTION = "BLARG v1.0"

#taille de l'écran de jeu. pour info GROS FAIL !! NE PAS METTRE DES TAILLES POURRIES
#COMME CELLLE-CI. CA FAIT FOIRER LE MODE FULL SCREEN SUR CERTAINS PC. IL FAUT UTILISER DES
#TAILLES STANDARDS GENRE 640x480, OU 1024x768. A L'AVENIR, NE PAS FAIRE LE CON AVEC CA.
SCREEN_SIZE_X = 400
SCREEN_SIZE_Y = 300

#rect définissant l'aire de jeu totale.
SCREEN_RECT = pygame.Rect(0, 0, SCREEN_SIZE_X, SCREEN_SIZE_Y)

#youpi, la couleur noire.
COLOR_BLACK = (0, 0, 0)

#abscisse de la partie de l'écran de gauche réservée à l'affichage des infos du jeu
#(cartouches, scores, points de vie, ...) A GAAAUUUUCCHHE !!!! AAAA GAAAAUUUUCHE !!!!!!
GAME_INFO_LIMIT_X = 50

#taille et aire de la partie réservé au jeu en lui-même.
GAME_SIZE_X = SCREEN_SIZE_X - GAME_INFO_LIMIT_X
GAME_SIZE_Y = SCREEN_SIZE_Y
GAME_RECT = pyRect(GAME_INFO_LIMIT_X, 0, GAME_SIZE_X, GAME_SIZE_Y)

#rapidité du jeu (Frame Per Second)
#Sur mon Mac ça chie. En pas-plein-écran, il tient pas plus de 75 FPS.
#Même avec très peu de sprites. Ca doit être une histoire de conversion du mode graphique
#des images. Mais je vois pas comment faire mieux, j'ai fait le convert() pour toutes les images.
#osef. Personne n'utilise de Mac.
FRAME_PER_SECOND = 65

#nom du répertoire avec les images dedans
IMG_DIRECTORY_NAME = "img"

#nom du répertoire avec les sons dedans
SOUND_DIRECTORY_NAME = "sound"

#position X, Y du héros au départ. (cette info n'est utilisée que par game.py. Elle n'a donc
#pas trop lieu d'être dans le common. Mais c'est un gros truc assez important. Donc paf common.
COORD_HERO_START = pyRect(100, 100)

#allez, zou, 4 point de vie. C'est la fête !!!
HERO_LIFE_POINT_INITIAL = 4

#valeur à la con, utilisée pour les compteurs (de tout et n'importe quoi)
#indique que le compteur ne doit pas compter.
#du coup faut faire gaffe quand on l'utilise. Il faut mettre if machin is NONE_COUNT. Pas "="
NONE_COUNT = None

#la police de caractère tempesta.ttf vient du site : http://p.yusukekamiyamane.com
#voir le fichier fontzy/fonts_origin.txt de ce jeu pour plus de détail.

#nom du répertoire contenant toutes les fonts (police de caractère)
FONT_DIRECTORY_NAME = "fontzy"
#nom du fichier contenant la font par défaut
FONT_DEFAULT_NAME = "tempesta.ttf"
#taille par défaut de la font par défaut
FONT_DEFAULT_SIZE = 12
#taille du texte en petit de la font par défaut
FONT_LITTLE_SIZE = 8

#chemin et nom du fichier de sauvegarde. Il est trop bien ce nom. Je vais le garder comme ça.
SAVE_FILE_PATHNAME = "dichmama.nil"

#version du format du fichier de sauvegarde. Osef, mais ça pourra servir plus tard, imaginons
#que je fasse un blarg version 2. Ce sera bien qu'il puisse détecter et lire les anciennes
#version des fichiers de sauvegarde.
SAVE_FILE_VERSION = "42.0"

# --- liste des valeurs possibles des globData ---

#je n'utilise pas de dictionnaire qui ferait la correspondance entre
#un identidiant et la valeur string qui va avec. Quand c'est des string
#de une lettre, on a le droit. Et si je faisait un dico, il faudrait que
#je l'ai dans les deux sens. Car il faut pouvoir charger et enregistrer
#ces valeurs dans le fichier de sauvegarde. Donc pour éviter trop d'intermédiaires
#bordelique, j'utilise directement les valeurs comme identifiants. NA !
# --- valeurs possibles pour la globData GLOB_DATA_ID_SCREEN ---
SCREEN_WINDOWED = "W"  #mode fenêtre
SCREEN_FULL     = "F"  #plein écran
LIST_SCREEN     = (SCREEN_WINDOWED, SCREEN_FULL) #valeurs autorisées.
SCREEN_DEFAULT  = SCREEN_FULL

# --- valeurs possibles pour la globData GLOB_DATA_ID_LANG ---
LANG_FRENCH  = "F"  #français
LANG_ENGL    = "E"  #anglais
LIST_LANG    = (LANG_FRENCH, LANG_ENGL) #valeurs autorisées.
LANG_DEFAULT = LANG_FRENCH

# --- valeurs possibles pour la globData GLOB_DATA_ID_SOUND ---
SOUND_ENABLED  = "E"
SOUND_DISABLED = "D"
LIST_SOUND = (SOUND_ENABLED, SOUND_DISABLED) #valeurs autorisées.
SOUND_DEFAULT = SOUND_ENABLED

#nombre de bits de précision des valeurs en virgules pas-flottantes. (sur 128)
SHIFT_PREC = 7
#valeur de la précision
NOT_FLOATING_PREC = 2 ** SHIFT_PREC

#vitesse du héros, en nombre de pixel de déplacement par cycle de jeu
SPEED = 3

#liste des stimulis envoyable par le joueur, au héros. (quand le joueur appuie sur des touches)
(STIMULI_HERO_MOVE,   #mouvement (quel qu'il soit)
 STIMULI_HERO_FIRE,   #tirer un coup de feu
 STIMULI_HERO_RELOAD, #recharger
) = range(3)

#liste des identifiants de touches
(KEY_DIR_UP,
 KEY_DIR_DOWN,
 KEY_DIR_RIGHT,
 KEY_DIR_LEFT,
 KEY_FIRE,
 KEY_RELOAD,
) = range(6)

#mapping de touche par défaut. Pour le héros.
# - clé : identifiant d'une touche
# - valeur : tuple de 2 elements
#    * identifiant du stimuli à envoyer au héros.
#    * sous-tuple. liste de paramètres à envoyer en même temps que le stimuli.
#                  ça ne sers que pour le stimuli de mouvement, pour indiquer
#                  les coorodnnées X,Y de déplacemnt du héros.
KEY_MAPPING_DEFAULT_HERO = {
    pygl.K_UP    : (STIMULI_HERO_MOVE,   (pyRect( 0,      -SPEED), ) ),
    pygl.K_DOWN  : (STIMULI_HERO_MOVE,   (pyRect( 0,      +SPEED), ) ),
    pygl.K_RIGHT : (STIMULI_HERO_MOVE,   (pyRect(+SPEED,  0),      ) ),
    pygl.K_LEFT  : (STIMULI_HERO_MOVE,   (pyRect(-SPEED,  0),      ) ),
    pygl.K_e     : (STIMULI_HERO_FIRE,   (), ),
    pygl.K_r     : (STIMULI_HERO_RELOAD, (), ),
}

#liste des "ihmsg" (contraction de IHM Message = message d'interface homme-machine).
#les éléments d'interface des menus du jeu (bouton texte, sous-menu, ...)
#s'envoient des messages entre eux, "en interne" (haha, j'adore utiliser cette expression,
#ça fait trop le mec qu'a codé un truc de oufzor ultra complet et usine-à-gazesque).
#Bon bref, ces messages internes sont sous forme de tuple appelés "ihmsgInfo".
#Dans ce tuple, on peut mettre 0, 1 ou X valeurs de la liste ci-dessous, chacune ayant
#une signification spéciale.
(IHMSG_QUIT,           #on veut quitter le menu courant, pour revenir au truc qu'on faisait avant.

 IHMSG_TOTALQUIT,      #on veut totalement quitter tout le jeu (genre Alt-F4)

 IHMSG_REDRAW_MENU,    #Le menu doit être entièrement redessiné.
                       #(Le fond + tous les éléments du menu)

 IHMSG_ELEM_CLICKED,   #l'élément de menu s'est fait cliquer dessus.

 IHMSG_ELEM_WANTFOCUS, #l'élément de menu veut avoir le focus.

 IHMSG_CYCLE_FOCUS_OK, #on veut cycler le focus (Tab). L'élément de menu actuellement focusé
                       #accepte de lacher le focus pour qu'il soit transmis à l'élément suivant.

 IHMSG_PLAY_ONCE_MORE, #message spécial utilisé dans un seul cas : quand on quitte le menu
                       #affichant que le héros est mort, il faut pouvoir indiquer si
                       #le joueur veut rejouer. C'est à ça que ça sert.

 IHMSG_CANCEL,         #le joueur veut annuler le truc en cours.

) = range(8)

#tuple vide. Ca sert quand on veut renvoyer aucun message d'IHM.
IHMSG_VOID = ()

#liste des touches qui renvoient quelque chose dans la valeur event.unicode, mais qui corresponde
#pas à un caractère imprimable. (C'est bizarre, mais c'est ainsi)
#le event.unicode n'est pas le même sur Mac et sur PC, pour certaines touches
#par exemple : le backspace, le return du pavé numérique, et les flèches.
#sur Mac, les flèches renvoient ça : (u"\uf700", u"\uf701", u"\uf702", u"\uf703"). bizarre...
#TRODO : le signaler à pygame.org
#La touche espace n'est pas présente dans cette liste. Puisque c'est un caractère imprimable
#(il imprime rien, mais on peut l'imprimer)
LIST_NO_PRINTABLE_KEY = (pygl.K_RETURN, pygl.K_KP_ENTER,
                         pygl.K_TAB, pygl.K_BACKSPACE,
                         pygl.K_UP, pygl.K_DOWN, pygl.K_LEFT, pygl.K_RIGHT)

#nom du joueur par défaut, proposé lors du premier lancement du jeu.
#A cause de la prof d'anglais que j'ai jamais pu blairer : Colette Mora.
#A la fin de la partie, le héros meurt forcément. C'est cool. Je voulais qu'elle meurt celle-là
NAME_HERO = u"Morac"

#Ca, c'est moi.
NAME_RECHER = u"Réchèr"

#vague obfuscation à l'arrache
NAME_DOGDOM = u"edoM-edoG rueisnoM"[::-1]


def securedPrint(stringToWrite):
    """
    fonction pour balancer sur la sortie standard une string unicode, avec des accents et tout.
    C'est pas garanti que les accents sortent correctement.
    Mais c'est garanti que ça fasse jamais planter le programme.

    entrée :
        unicodeString : string (unicode ou pas) contenant le message à afficher.

    chui obligé de faire comme ça parce que le terminal du Mac est tellement merdique
    qu'il peut pas afficher des accents aigus unicode.
    Il peut en afficher que si ils viennent de l'encodage 'mac-roman'. Quelle daubasse !!!
    """

    try:
        print stringToWrite
    except:
        #fail ecrivage du unicode. Donc on convertit en ascii.
        #Ca fait des caractères pourri, mais l'ascii, ça marche partout.
        unicodeString = unicode(stringToWrite)
        print unicodeString.encode("ascii", "replace")


def loadImg(filename, colorkey=-1, doConversion=True):
    """
    fonction piquée au tutorial chimp de pygame. Permet de charger une image.
    Si l'image ne peut pas être chargée, envoie une message sur stdout et balance une exception

    entrées :
        filename : string indiquant le nom du fichier image à charger.
                   les images doivent toutes être dans le sous-répertoire
                   défini par IMG_DIRECTORY_NAME

        colorkey : définition de la key transparency de l'image
                   None :        pas de transparence
                   une couleur : la transparence est sur cette couleur
                   -1 :          on prend la couleur du pixel
                                 en haut à gauche de l'écran

        doConversion : boolean. Indique si on doit faire la conversion de l'image dans le mode
                       graphique actuel. (Normalement, faut le faire tout le temps, pour
                       optimiser). Sauf que si le mode graphique actuel n'a pas encore été
                       déterminé, eh ben on peut pô faire de convert. Donc faudra mettre False.
                                 
    plat-dessert :
        la Surface contenant l'image chargée
    """

    pathname = os.path.join(IMG_DIRECTORY_NAME, filename)

    #tentative de chargement de l'image. On sort comme un voleur si ça fail
    try:
        image = pygame.image.load(pathname)
    except pygame.error, message:
        securedPrint(u"Fail. Impossible de charger l'image : " + pathname)
        #On peut mettre "raise" sans rien après. Ca recrache la dernière exception en cours.
        raise

    #conversion dans le mode graphique actuel. On le fait qu'une fois au début
    #et après c'est plus rapide pour les blits. Enfin... normalement, parce que sur Mac...
    #Si on switche plein-ecran/windowed, je sais pas ce que ça donne.
    #Si ça se trouve faudrait refaire le convert sur toutes les images.
    #Bon, ça marce quand même. C'est pas un drame si c'est pas hyper optimisé.
    if doConversion:
        image = image.convert()

    #ajout de la transparence en fonction du paramètre colorkey
    if colorkey is not None:

        if colorkey == -1:
            #la couleur de transparence est celle du 1er pixel
            #en haut à gauche de l'image
            colorkey = image.get_at((0,0))

        #je sais pas ce que c'est que ce RLEACCEL, mais ça doit être cool.
        image.set_colorkey(colorkey, pygl.RLEACCEL)

    #on balance l'image
    return image


def loadImgInDict(listImgIdWithFileName, prefixFileName="", colorkey=-1,
                  extension=".png"):
    """
    fonction permettant de charger tout plein d'images, et les ranger dans un dictionnaire.
    pas de gestion d'erreur si les chargement fails.
    C'est à peu près géré dans la fonction LoadImg

    entrée :
        listImgIdWithFileName : tuple de tuple de 2 elem, avec :
         - identifiant de l'image (int, ou autre chose)
         - nom de fichier court de l'image à charger (string)
        TRODO : pourquoi c'est déclaré sous forme de tuple et ça se finit en dict ?
        pourquoi pas déclarer un dict dès le début ? et en sortir un autre dict ?
        réponse : osef. C'est pas grave si c'est foutu comme ça.

        prefixFileName : string. Préfixe des noms de fichier pour les images à charger.

        colorkey : voir fonction LoadImg

        extension : string. extension des noms de fichier image.

    plat-dessert : un dictionnaire
        clé : identifiant de l'image (les mêmes que dans listImgIdWithFileName)
        valeur : Surface contenant l'image correspondante
    """

    dicImg = {}

    for imgIdentifier, shortFileName in listImgIdWithFileName:
        #création du nom entier à partir du nom court
        longFileName = prefixFileName + shortFileName + extension
        #chargementde l'image
        imgLoaded = loadImg(longFileName, colorkey)
        #rangement dans le dico
        dicImg[imgIdentifier] = imgLoaded

    return dicImg


def makeRotatedImg(imgToRotate, stepAngle):
    """
    crée un tuple contenant des Surface d'une image rotatée.

    entrées :
        imgToRotate : Surface contenant l'image de départ à rotater
        stepAngle : int. angle, en degré, indiquant le pas de degré à avancer pour chaque image
                    on peut mettre un pas négatif, ça tournera dans le sens anti-trigo
                    C'est pas obligé de tomber pil poil sur un multiple de 360 degrés.
                    La dernière image aura la valeur de l'angle de rotation du pas,
                    juste avant d'arriver au 360

    plat-dessert :
        tuple de X element (X = 360 / stepAngle arrondi inférieur), contenant les
        Surface des images rotatées.
    """
    #const à la con
    NBR_DEGRE = 360

    #création de la liste des angles de rotation de chaque image. (avec pas negatif ou positif)
    if stepAngle > 0:
        listAngles = range(0, NBR_DEGRE, stepAngle)
    else:
        listAngles = range(NBR_DEGRE, 0, stepAngle)

    #on construit la liste en rotatant les images.
    listImgRotated = [ pygame.transform.rotate(imgToRotate, angle)
                       for angle in listAngles
                     ]

    #tuplifiage de la liste avant de la renvoyer, car elle ne va pas bouger.
    return tuple(listImgRotated)

#bizarre ce caillou ...


def centeredRandom(maximumRay):
    """
    génère un nombre entier aléatoire, à distribution égale (enfin à priori)
    compris entre -maximumRay inclus et +maximumRay inclus

    un peu useless, mais pas trop.
    """
    return random.randrange(-maximumRay, +maximumRay+1)


#TRODO pour plus tard : A l'avenir, éviter de faire le con à importer le random que dans common.
#random on peut bien l'avoir partout. et l'alias randRange, on le recrée sur place à chaque fois.
#c'est juste un putain d'alias
randRange = random.randrange


def oppRect(rectToOpp):
    """
    construit un pygame.Rect avec les coordonnées X et Y opposées.

    entrées : rectToOpp : pygame.Rect (X, Y, width, height) dont auquel il faut
              oppositionner les coordonnées. Oui ça veut rien dire ma phrase.

    plat-dessert : pygame.Rect (-X, -Y, width, height)
    """

    return pygame.Rect(-rectToOpp.left, -rectToOpp.top,
                       rectToOpp.width, rectToOpp.height)


def loadFonts():
    """
    charge toutes les fonts (polices de caractère) nécessaires au jeu.

    De ce que j'ai compris dans la doc, lorsqu'on charge une font,
    on doit immédiatement spécifier sa taille. Et on ne peut pas la changer après.
    Si on veut plusieurs tailles, faut charger plusieurs fois la font.

    Si des fonts ne peuvent pas être chargée, la fonction écrit un message sur stdout,
    et tente de créer une font de secours, avec la font par défaut du système.
    si cette seconde étape foire aussi, tout plante complètement. (Je l'ai pas géré, osef)

    plat-dessert :
        un tuple de 3 elem : (dictFont, fontDefault, boolean)

         - dictFont : dictionnaire :
            * clé : le nom de la font
            * valeur : un autre dictionnaire :
                . clé : la taille de la font
                . valeur : la font en elle-même. L'objet. Enfin !!!!

         - fontDefault : encore une font. celle par défaut, avec une taille par défaut

         - boolean. Indique si le chargement des font s'est fait totalement bien, ou pas.
    """

    #bon en fait mon mega-dictionnaire dictFont n'a que 2 elem :
    #la font par défaut, avec 2 tailles. Hahahaha LOL !!!!
    #et du coup, je me permet un chargement à l'envers.
    #au lieu de remplir mon dictionnaire, puis de piocher l'un des elem dedans
    #pour en faire ma font par défaut. Je charge les fonts, dont la font par défaut
    #puis je remplis mon dico à l'arrache avec tout ça.
    #TRODO : faire ça mieux si on a besoin et envie.

    loadingOK = False

    #vague gestion du cas où le pygame n'a pas les fonts.
    #ça plante pas dans cette fonction, mais y'a tout qui va planter après. osef.
    if not pygame.font:
        securedPrint(u"Atation, impossible d'afficher du texte")
        return (None, None, loadingOK)

    #chemin et nom du fichier indiquant la font à charger
    fontDefaultPathName = os.path.join(FONT_DIRECTORY_NAME, FONT_DEFAULT_NAME)

    try:

        #tentative de chargement des fonts.
        fontDefault = pygame.font.Font(fontDefaultPathName, FONT_DEFAULT_SIZE)
        fontLittle = pygame.font.Font(fontDefaultPathName, FONT_LITTLE_SIZE)
        loadingOK = True

    except IOError, e:

        #ça a fail. On envoie un message, et on charge une font par défaut.
        securedPrint(u"Font loadage fail. fichier : " + fontDefaultPathName)
        securedPrint(e)
        #la font par défaut de pygame est illisible. Donc je la charge avec une taille
        #un peu plus grosse. C'est bancal, mais c'est du fonctionnement dégradé. On a le droit.
        fontDefault = pygame.font.Font(None, FONT_DEFAULT_SIZE+6)
        fontLittle = pygame.font.Font(None, FONT_LITTLE_SIZE+6)

    #création du dictionnaire contenant toutes les font. Même si y'en a que 2 dedans.
    dictFont = {}
    dictFont[FONT_DEFAULT_NAME] = {}
    dictFont[FONT_DEFAULT_NAME][FONT_DEFAULT_SIZE] = fontDefault
    dictFont[FONT_DEFAULT_NAME][FONT_LITTLE_SIZE] = fontLittle

    return (dictFont, fontDefault, loadingOK)


def sign(X):
    """
    fonction à la con pour avoir le signe de X. renvoie -1, 0 ou 1
    TRODO : y'en a pas une toute faite ? C'est con comme fonction
    """
    if X < 0:
        return -1
    if X == 0:
        return 0

    return +1


def randWithListCoef(listCoef):
    """
    génère un nombre au hasard, entre 0 et N,
    avec des coefficient de proba différent pour chaque nombre

    entrée :
        listCoef : liste de int (positif ou nul), indiquant les coefs pour chaque valeur
                   possible. On peut avoir des coef de 0. Dans ce cas, ce nombre ne sera
                   jamais choisi.
                   La somme des coefs peut valoir n'importe quoi, on fait avec.

    plat-dessert
        int. nombre aléatoire générée, compris entre 0 et len(listCoef)-1
    """

    #détermination de la plage de random ( = somme de tous les coefs,
    #et génération d'un nombre au hasard, dans cette plage.
    randMax = sum(listCoef)
    choiceValue = randRange(randMax)

    choiceIndex = 0

    #il faut trouver à quelle choix correspond le nombre qu'on a généré au hasard.
    #on avance dans la liste des coefs. A chaque fois, on retire le coef du choix
    #en cours. Quand on arrive à un choix, alors que le nombre est descendu en dessous
    #de son coef, alors c'est ce choix qui est le bon.
    #Et ça marche, bon c'est tout simple. Pas besoin de plus d'explication, bordel.
    while choiceValue >= listCoef[choiceIndex]:

        choiceValue -= listCoef[choiceIndex]
        choiceIndex += 1

    #voili voilà, on a trouvé le choix qu'a été fait.
    return choiceIndex


def randBoole():
    """
    génère un boolean aléatoire. Avec distribution égale.

    plat-dessert : booléean. True ou False. Le choix se fait au hasard.
    """
    if randRange(2) == 0:
        return True
    else:
        return False


def addListRectOrNot(listRectSource, listRectToAddOrNot):
    """
    ajoute une liste de Rect à une autre liste de Rect existante. Ou pas.
    Si la liste de Rect à ajouter est None, on l'ajoute pas.

    Je suis obligé de créer cette fonction de merde, parce que quand on fait listRect += None,
    Ca plante complètement, au lieu de ne rien faire. Ah bravo !!

    entrée :
        listRectSource : liste de Rect.
        listRectToAddOrNot : liste de Rect, ou bien valeur None.

    plat-dessert :
        rien du tout. Mais le contenu de listRectSource est modifié en live.
    """
    if listRectToAddOrNot is not None:
        listRectSource += listRectToAddOrNot


def moveIndexInBounds(indexInit, delta, min, max, loopAuthorized):
    """
    déplace un index entre deux limites, selon un delta.
    Si l'index dépasse les limites, et qu'on autorise le loop, on renvoie min, ou max,
    en faisant un tour du compteur. Si on n'autorise pas le loop, on renvoie None.

    La fonction ne fait pas de calcul savant, que si on a un delta supérieur à 1, il faut
    avancer un peu, puis faire le tour, puis re-avancer un peu. Si y'a un tour de compteur,
    on renvoie min, ou max, et pis c'est tout.

    entrée :
        indexInit : int. valeur initiale de l'index

        delta : int. valeur de déplacement (positif ou negatif) à appliquer à l'index

        min, max : int. avec min <= max. Valeurs limites entre lesquelles l'index doit rester.
                   c'est dans la philosophie python. C'est à dire que c'est min inclu, max exclu.
                   (je trouve ça ridicule de dire "philosophie" python, mais j'aime bien être
                   ridicule. Ouh putain, ça vibre ce camion-bus.)

        loopAuthorized : boolean. Si on sort des limites et que c'est False, on renverra None.
                         Si on sort des limites et que c'est True,
                         on renverra min ou max, selon où on a dépassé.

    plat-dessert :
        int, compris entre min inclu et max exclu, ou None.
    """

    #application du delta
    indexNew = indexInit + delta

    #j'ais pas voulu écrire cette condition sous la forme A <= B < C. Parce que y'a un
    #inférieur strict, et un inférieur ou égal. Ca m'embêtait de les mettre dans le même sac,
    #alors que c'est pas tout à fait le même type de condition.
    if (min <= indexNew) and (indexNew < max):
        #on est entre les limites. on peut renvoyer l'index delta-ifié.
        return indexNew

    #on n'est pas entre les limite.
    if not loopAuthorized:
        #interdit de faire des tours du compteur. donc on renvoie None.
        return None

    if indexNew >= max:
        #on a dépassé les limites par la borne supérieure. comme on fait le tour du compteur,
        #on renvoie la valeur de la borne inférieure.
        return min

    #dans l'autre cas, ben c'estle contraire. Faut renvoyer la borne supérieure.
    #Comme les limites, c'est min inclu et max exclu, la borne sup, c'est max-1.
    return max-1


def colorCompAdd(colorComp, delta):
    """
    ajoute ou soustrait une valeur à une composante de couleur RGB.
    La valeur résultat reste comprise entre les bornes des composantes de couleur,
    C'est à dire entre 0 et 255.

    Hemmm.... Cette fonction ne sert à rien. Je l'utilise jamais. Merci au revoir.
    Allez, y'a qu'à dire qu'on la garde pour plus tard si jamais y'a besoin.

    entrée :
        colorComp : int. (à priori compris entre 0 et 255, mais si ça l'est pas c'est pas grave
                    Valeur initiale de la composante RGB.

        delta : int positif ou négatif, pas de bornes limites. Valeur à ajouter à la composante.

    plat-dessert :
        La composante et le delta ajouté. int compris entre 0 et 255
    """

    #putain, il peut pas faire ça tout seul ce putain de python ?
    #Paye ton code pas optimisé. Heureusement que j'en ai besoin que pour des conneries.
    colorCompRes = colorComp + delta

    if colorCompRes > 255: return 255
    if colorCompRes < 0:   return 0
    return colorCompRes


def pixTranspColor(surfaceSource, tupleRVBColor, transparency):
    """
    ajoute un filtre de couleur transparent à une image.

    entrées :
        surfaceSource : pygame.Surface. Image de départ sur laquelle on veut mettre le filtre.

        tupleRVBColor : tuple de 3 octets. composantes RGB de la couleur du filtre

        transparency : int (entre 0 et 255, c'est mieux). Transparence du filtre.
                       0 = totalement transparent. 255 = totalement opaque.

    plat-dessert :
        objet pygame.Surface, de la même taille que l'image source.
        C'est l'image avec le filtre.
        (On crée une nouvelle surface, on ne modifie pas le contenu de surfaceSource.)
    """

    #création de la nouvelle surface, et copie-collage de l'image d'origine sur cette surface.
    (width, height) = surfaceSource.get_size()
    surfaceDest = pygame.surface.Surface((width, height))
    #Le convert, faut le faire systématiquement pour optimiser les utilisations ultérieures.
    #(Je l'ai toujours trouvé bizarre ce mot : "ultérieur". Ca fait : "cul-terreux").
    surfaceDest.convert()
    surfaceDest.blit(surfaceSource, (0, 0))

    #création d'une surface représentant le filtre. Même taille que l'image, mais on la colorie
    #entièrement avec la couleur du filtre.
    surfaceTransp = pygame.surface.Surface((width, height))
    surfaceTransp.fill(tupleRVBColor)
    #définition du degré de transparence du filtre.
    surfaceTransp.set_alpha(transparency)

    #on copie-colle le filtre sur la surface de destination. Comme on a défini sa transparence,
    #ça fait pas un vrai copier-coller-paf-comme-ça. Ca mélange les couleurs, comme dirait
    #Francis Cabrèleu.
    surfaceDest.blit(surfaceTransp, (0, 0))

    #TRODO pour plus tard : Bizarre qu'il faille créer toute une surface de filtre juste pour
    #faire ça. Y'a pas moyen d'appliquer direct une couleur avec une transparence ? A chercher.

    return surfaceDest


def pixTranspLight(surfaceSource, light, transparency):
    """
    applique un filtre de lumière ou de sombritude sur une image.
    (voir fonction pixTranspColor. Un filtre de lumière/sombritude, c'est comme un filtre
     de couleur, mais avec toutes les composantes égales).

    entrées :
        surfaceSource, transparency : voir param de pixTranspColor. C'est les mêmes.

        light : int (compris entre 0 et 255, c'est mieux). intensité de la lumière/sombritude.

    plat-dessert : voir pixTranspColor
    """

    #création du tuple de composante RGB du filtre, à partir de l'intensité de lumière du filtre.
    #(On répète trois fois la même valeur, pour les trois couleurs RGB).
    tupleRVBColor = (light, ) * 3

    #Et paf, application du filtre de couleur qu'est un filtre lumineux.
    return pixTranspColor(surfaceSource, tupleRVBColor, transparency)

#Valeurs utilisées pour les éléments de menu "image cliquable" (MenuSensitiveImage), et
#"case à cocher" (MenuTick). C'est la liste des valeurs d'intensité lumineuse des filtres à
#appliquer à l'image d'origine, pour faire les images plus claires.
#On affiche successivement ces images quand le MenuElem prend le focus. Et wouw ! il s'illumine !
#(Ca nous y fait : 10, 30, 50, ... jusqu'à 130)
LIST_TRANSP_FOCUS = range(10, 150, 20)

def buildListImgLight(theImg, listTransp):
    """
    construit une liste d'image à partir d'une seule image, en appliquant des filtres
    d'intensité de luminosité maximales, avec des degrés de transparence différents.

    entrées :
        surfaceSource : pygame.Surface. Image de départ sur laquelle on veut mettre les filtres.

        listTransp : liste de int (tous compris entre 0 et 255, c'est mieux).
                     degré de transparence des filtres lummineux pour chaque images

    plat-dessert :
        Liste de pygame.Surface. (Autant d'élément qu'il y a d'élément dans listTransp) + 1
        Ouais, y'a +1 parce qu'on ajoute l'image d'origine au début de la liste. Car tel
        est mon bon vouloir.
        Les images résultante de l'application des filtres sur l'image d'origine.
    """

    #création de la liste d'image avec l'application des filtres ultra-luminique
    #(intensité de lumière = 255)
    listImgWithLight = [ pixTranspLight(theImg, 255, transparency)
                         for transparency in listTransp ]

    #ajout de l'image d'origine au début de la liste.
    listImgWithLight.insert(0, theImg)

    #tuplifiage de la liste pour accélérer les accès ultérieurs (cul-terrieurs).
    listImgWithLight = tuple(listImgWithLight)

    return listImgWithLight


def boundJustAttained(value, inc, limitDown, limitUp):
    """
    indique si une valeur a atteint/dépassé les bornes dans lesquelles elle est censée rester,
    selon la direction dans laquelle cette valeur évolue. Wouaw !

    Tous les paramètres de cette fonction sont des int qui peuvent être positif ou négatif.
    (ouais, même le inc. Surtout le inc en fait)

    value : Valeur dont on vérifie qu'elle a dépassé les bornes ou pas

    inc : pas d'incrémentation (ou de décrémentation) de la valeur

    limitDown, limitUp : bornes inf et sup dans lesquelles la valeur devrait rester.
                         il vaut mieux que limitDown < limitUp, mais ce n'est pas vérifié,
                         donc faites comme vous voulez.

    plat-dessert :
        booléen : True : la valeur a atteint ou dépassé la limite vers laquelle elle avance.
                  False : la valeur n'a ni atteint, ni dépassé la limite.

    Si la valeur évolue de manière croissante (inc > 0), on ne vérifie pas si elle est en
    dessous de LimitDown. (osef, car c'est ainsi)
    Si la valeur évolue de manière décroissante (inc < 0), on ne vérifie pas si elle est
    au dessus de LimitUp. (osef aussi)
    Les limites de vérification sont limitDown inclue, et limitUp exclue. Comme d'hab' en python.
    """

    #vérification, lorsque la valeur est croissante, qu'elle ait atteint ou dépassé la limite.
    #y'a -1 donc, parce qu'on fait tout le temps comme ça en python.
    if inc > 0 and value >= limitUp-1:
        return True

    #vérification, lorsque la valeur est décroissante, qu'elle ait atteint ou dépassé la limite.
    if inc < 0 and value <= limitDown:
        return True

    #pas de dépassement ni d'atteignage. Ou alors, la valeur n'évolue pas (inc == 0)
    return False


def getRectDrawZone(rectPos, img):
    """
    Récupère la zone dans laquelle va se dessiner un MenuElem (self.rectDrawZone),
    en fonction de la taille et la position de l'image qu'il affiche.

    entrées :
        rectPos : objet pygame.Rect indiquant la position du coin sup-gauche de l'image.
                  (la taille de ce rect, on s'en fout)

        img : objet pygame.Surface. L'image que le MenuElem va afficher.

    plat-dessert :
        objet pygame.Rect. zone de dessin du MenuElem, sur sa surface de destination.
    """

    #on récupère la position.
    rectDrawZonePos = rectPos.topleft
    #on récupère la taille (en pixel). C'est la taille de l'image, m'voyez.
    rectDrawZoneSize = img.get_rect().size
    #rassemblement de la position et de la taille pour obtenir la zone dans laquelle
    #cet élément de menu va s'afficher.
    return pygame.Rect(rectDrawZonePos, rectDrawZoneSize)


def addThings(*listOfThings):
    """
    ajoute des trucs entre eux.

    entrées :
        liste de trucs (n'importe quoi, mais faut qu'on puisse les additionner ensemble)

    plat-dessert :
        trucs (n'importe quoi) correspondant à la somme de tous les trucs de la liste.

    A partir d'une liste [ truc1, truc2, ... trucN ], la fonction renvoie la valeur unique
    truc1 + truc2 + ... + trucN

    la fonction sum() déjà toute faite du python ne marche que pour les int. Fay chiay.
    """

    #paf. Voir fonction reduce du python pour les clampins qui connaîtraient pas.
    return reduce(lambda x,y : x+y, listOfThings)
