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

date de la derni�re relecture-commentage : 29/03/2011

biblioth�que avec tous les trucs communs � plusieurs trucs

un peu de vocabulaire. C'est de l'obvious, mais �a prouve que moi, je suis clair dans
mes noms de variables. (Je dis absolument pas �a par rapport � la merde magmatesque qui se fait
dans mon boulot de merde) :
XXX_DIRECTORY_NAME : chemin vers un r�pertoire (relatif ou absolu, mais en g�n�ral, relatif)
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
    permet de g�n�rer un pygame.Rect, sans forc�ment donner la hauteur et la largeur.

    pourquoi ils ont pas mis eux-m�me des valeurs par d�faut bordel !!
    (ou alors c'est moi qui suis � la masse et j'ai loup� une astuce.)
    """
    return pygame.Rect(top, left, width, height)


def pyRectTuple(tuplePos=(0, 0), tupleSize=(0, 0)):
    """
    permet de g�n�rer un pygame.Rect � partir de tuples,
    sans forc�ment donner la hauteur et la largeur.

    pourquoi ils ont pas mis eux-m�me des valeurs par d�faut bordel !!
    (tiens, j'ai l'impression d'avoir d�j� dit �a).
    """
    return pygame.Rect(tuplePos, tupleSize)


#texte �crit dans le titre de la fen�tre du jeu (si on joue en windowed)
GAME_CAPTION = "BLARG v1.0"

#taille de l'�cran de jeu. pour info GROS FAIL !! NE PAS METTRE DES TAILLES POURRIES
#COMME CELLLE-CI. CA FAIT FOIRER LE MODE FULL SCREEN SUR CERTAINS PC. IL FAUT UTILISER DES
#TAILLES STANDARDS GENRE 640x480, OU 1024x768. A L'AVENIR, NE PAS FAIRE LE CON AVEC CA.
SCREEN_SIZE_X = 400
SCREEN_SIZE_Y = 300

#rect d�finissant l'aire de jeu totale.
SCREEN_RECT = pygame.Rect(0, 0, SCREEN_SIZE_X, SCREEN_SIZE_Y)

#youpi, la couleur noire.
COLOR_BLACK = (0, 0, 0)

#abscisse de la partie de l'�cran de gauche r�serv�e � l'affichage des infos du jeu
#(cartouches, scores, points de vie, ...) A GAAAUUUUCCHHE !!!! AAAA GAAAAUUUUCHE !!!!!!
GAME_INFO_LIMIT_X = 50

#taille et aire de la partie r�serv� au jeu en lui-m�me.
GAME_SIZE_X = SCREEN_SIZE_X - GAME_INFO_LIMIT_X
GAME_SIZE_Y = SCREEN_SIZE_Y
GAME_RECT = pyRect(GAME_INFO_LIMIT_X, 0, GAME_SIZE_X, GAME_SIZE_Y)

#rapidit� du jeu (Frame Per Second)
#Sur mon Mac �a chie. En pas-plein-�cran, il tient pas plus de 75 FPS.
#M�me avec tr�s peu de sprites. Ca doit �tre une histoire de conversion du mode graphique
#des images. Mais je vois pas comment faire mieux, j'ai fait le convert() pour toutes les images.
#osef. Personne n'utilise de Mac.
FRAME_PER_SECOND = 65

#nom du r�pertoire avec les images dedans
IMG_DIRECTORY_NAME = "img"

#nom du r�pertoire avec les sons dedans
SOUND_DIRECTORY_NAME = "sound"

#position X, Y du h�ros au d�part. (cette info n'est utilis�e que par game.py. Elle n'a donc
#pas trop lieu d'�tre dans le common. Mais c'est un gros truc assez important. Donc paf common.
COORD_HERO_START = pyRect(100, 100)

#allez, zou, 4 point de vie. C'est la f�te !!!
HERO_LIFE_POINT_INITIAL = 4

#valeur � la con, utilis�e pour les compteurs (de tout et n'importe quoi)
#indique que le compteur ne doit pas compter.
#du coup faut faire gaffe quand on l'utilise. Il faut mettre if machin is NONE_COUNT. Pas "="
NONE_COUNT = None

#la police de caract�re tempesta.ttf vient du site : http://p.yusukekamiyamane.com
#voir le fichier fontzy/fonts_origin.txt de ce jeu pour plus de d�tail.

#nom du r�pertoire contenant toutes les fonts (police de caract�re)
FONT_DIRECTORY_NAME = "fontzy"
#nom du fichier contenant la font par d�faut
FONT_DEFAULT_NAME = "tempesta.ttf"
#taille par d�faut de la font par d�faut
FONT_DEFAULT_SIZE = 12
#taille du texte en petit de la font par d�faut
FONT_LITTLE_SIZE = 8

#chemin et nom du fichier de sauvegarde. Il est trop bien ce nom. Je vais le garder comme �a.
SAVE_FILE_PATHNAME = "dichmama.nil"

#version du format du fichier de sauvegarde. Osef, mais �a pourra servir plus tard, imaginons
#que je fasse un blarg version 2. Ce sera bien qu'il puisse d�tecter et lire les anciennes
#version des fichiers de sauvegarde.
SAVE_FILE_VERSION = "42.0"

# --- liste des valeurs possibles des globData ---

#je n'utilise pas de dictionnaire qui ferait la correspondance entre
#un identidiant et la valeur string qui va avec. Quand c'est des string
#de une lettre, on a le droit. Et si je faisait un dico, il faudrait que
#je l'ai dans les deux sens. Car il faut pouvoir charger et enregistrer
#ces valeurs dans le fichier de sauvegarde. Donc pour �viter trop d'interm�diaires
#bordelique, j'utilise directement les valeurs comme identifiants. NA !
# --- valeurs possibles pour la globData GLOB_DATA_ID_SCREEN ---
SCREEN_WINDOWED = "W"  #mode fen�tre
SCREEN_FULL     = "F"  #plein �cran
LIST_SCREEN     = (SCREEN_WINDOWED, SCREEN_FULL) #valeurs autoris�es.
SCREEN_DEFAULT  = SCREEN_FULL

# --- valeurs possibles pour la globData GLOB_DATA_ID_LANG ---
LANG_FRENCH  = "F"  #fran�ais
LANG_ENGL    = "E"  #anglais
LIST_LANG    = (LANG_FRENCH, LANG_ENGL) #valeurs autoris�es.
LANG_DEFAULT = LANG_FRENCH

# --- valeurs possibles pour la globData GLOB_DATA_ID_SOUND ---
SOUND_ENABLED  = "E"
SOUND_DISABLED = "D"
LIST_SOUND = (SOUND_ENABLED, SOUND_DISABLED) #valeurs autoris�es.
SOUND_DEFAULT = SOUND_ENABLED

#nombre de bits de pr�cision des valeurs en virgules pas-flottantes. (sur 128)
SHIFT_PREC = 7
#valeur de la pr�cision
NOT_FLOATING_PREC = 2 ** SHIFT_PREC

#vitesse du h�ros, en nombre de pixel de d�placement par cycle de jeu
SPEED = 3

#liste des stimulis envoyable par le joueur, au h�ros. (quand le joueur appuie sur des touches)
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

#mapping de touche par d�faut. Pour le h�ros.
# - cl� : identifiant d'une touche
# - valeur : tuple de 2 elements
#    * identifiant du stimuli � envoyer au h�ros.
#    * sous-tuple. liste de param�tres � envoyer en m�me temps que le stimuli.
#                  �a ne sers que pour le stimuli de mouvement, pour indiquer
#                  les coorodnn�es X,Y de d�placemnt du h�ros.
KEY_MAPPING_DEFAULT_HERO = {
    pygl.K_UP    : (STIMULI_HERO_MOVE,   (pyRect( 0,      -SPEED), ) ),
    pygl.K_DOWN  : (STIMULI_HERO_MOVE,   (pyRect( 0,      +SPEED), ) ),
    pygl.K_RIGHT : (STIMULI_HERO_MOVE,   (pyRect(+SPEED,  0),      ) ),
    pygl.K_LEFT  : (STIMULI_HERO_MOVE,   (pyRect(-SPEED,  0),      ) ),
    pygl.K_e     : (STIMULI_HERO_FIRE,   (), ),
    pygl.K_r     : (STIMULI_HERO_RELOAD, (), ),
}

#liste des "ihmsg" (contraction de IHM Message = message d'interface homme-machine).
#les �l�ments d'interface des menus du jeu (bouton texte, sous-menu, ...)
#s'envoient des messages entre eux, "en interne" (haha, j'adore utiliser cette expression,
#�a fait trop le mec qu'a cod� un truc de oufzor ultra complet et usine-�-gazesque).
#Bon bref, ces messages internes sont sous forme de tuple appel�s "ihmsgInfo".
#Dans ce tuple, on peut mettre 0, 1 ou X valeurs de la liste ci-dessous, chacune ayant
#une signification sp�ciale.
(IHMSG_QUIT,           #on veut quitter le menu courant, pour revenir au truc qu'on faisait avant.

 IHMSG_TOTALQUIT,      #on veut totalement quitter tout le jeu (genre Alt-F4)

 IHMSG_REDRAW_MENU,    #Le menu doit �tre enti�rement redessin�.
                       #(Le fond + tous les �l�ments du menu)

 IHMSG_ELEM_CLICKED,   #l'�l�ment de menu s'est fait cliquer dessus.

 IHMSG_ELEM_WANTFOCUS, #l'�l�ment de menu veut avoir le focus.

 IHMSG_CYCLE_FOCUS_OK, #on veut cycler le focus (Tab). L'�l�ment de menu actuellement focus�
                       #accepte de lacher le focus pour qu'il soit transmis � l'�l�ment suivant.

 IHMSG_PLAY_ONCE_MORE, #message sp�cial utilis� dans un seul cas : quand on quitte le menu
                       #affichant que le h�ros est mort, il faut pouvoir indiquer si
                       #le joueur veut rejouer. C'est � �a que �a sert.

 IHMSG_CANCEL,         #le joueur veut annuler le truc en cours.

) = range(8)

#tuple vide. Ca sert quand on veut renvoyer aucun message d'IHM.
IHMSG_VOID = ()

#liste des touches qui renvoient quelque chose dans la valeur event.unicode, mais qui corresponde
#pas � un caract�re imprimable. (C'est bizarre, mais c'est ainsi)
#le event.unicode n'est pas le m�me sur Mac et sur PC, pour certaines touches
#par exemple : le backspace, le return du pav� num�rique, et les fl�ches.
#sur Mac, les fl�ches renvoient �a : (u"\uf700", u"\uf701", u"\uf702", u"\uf703"). bizarre...
#TRODO : le signaler � pygame.org
#La touche espace n'est pas pr�sente dans cette liste. Puisque c'est un caract�re imprimable
#(il imprime rien, mais on peut l'imprimer)
LIST_NO_PRINTABLE_KEY = (pygl.K_RETURN, pygl.K_KP_ENTER,
                         pygl.K_TAB, pygl.K_BACKSPACE,
                         pygl.K_UP, pygl.K_DOWN, pygl.K_LEFT, pygl.K_RIGHT)

#nom du joueur par d�faut, propos� lors du premier lancement du jeu.
#A cause de la prof d'anglais que j'ai jamais pu blairer : Colette Mora.
#A la fin de la partie, le h�ros meurt forc�ment. C'est cool. Je voulais qu'elle meurt celle-l�
NAME_HERO = u"Morac"

#Ca, c'est moi.
NAME_RECHER = u"R�ch�r"

#vague obfuscation � l'arrache
NAME_DOGDOM = u"edoM-edoG rueisnoM"[::-1]


def securedPrint(stringToWrite):
    """
    fonction pour balancer sur la sortie standard une string unicode, avec des accents et tout.
    C'est pas garanti que les accents sortent correctement.
    Mais c'est garanti que �a fasse jamais planter le programme.

    entr�e :
        unicodeString : string (unicode ou pas) contenant le message � afficher.

    chui oblig� de faire comme �a parce que le terminal du Mac est tellement merdique
    qu'il peut pas afficher des accents aigus unicode.
    Il peut en afficher que si ils viennent de l'encodage 'mac-roman'. Quelle daubasse !!!
    """

    try:
        print stringToWrite
    except:
        #fail ecrivage du unicode. Donc on convertit en ascii.
        #Ca fait des caract�res pourri, mais l'ascii, �a marche partout.
        unicodeString = unicode(stringToWrite)
        print unicodeString.encode("ascii", "replace")


def loadImg(filename, colorkey=-1, doConversion=True):
    """
    fonction piqu�e au tutorial chimp de pygame. Permet de charger une image.
    Si l'image ne peut pas �tre charg�e, envoie une message sur stdout et balance une exception

    entr�es :
        filename : string indiquant le nom du fichier image � charger.
                   les images doivent toutes �tre dans le sous-r�pertoire
                   d�fini par IMG_DIRECTORY_NAME

        colorkey : d�finition de la key transparency de l'image
                   None :        pas de transparence
                   une couleur : la transparence est sur cette couleur
                   -1 :          on prend la couleur du pixel
                                 en haut � gauche de l'�cran

        doConversion : boolean. Indique si on doit faire la conversion de l'image dans le mode
                       graphique actuel. (Normalement, faut le faire tout le temps, pour
                       optimiser). Sauf que si le mode graphique actuel n'a pas encore �t�
                       d�termin�, eh ben on peut p� faire de convert. Donc faudra mettre False.
                                 
    plat-dessert :
        la Surface contenant l'image charg�e
    """

    pathname = os.path.join(IMG_DIRECTORY_NAME, filename)

    #tentative de chargement de l'image. On sort comme un voleur si �a fail
    try:
        image = pygame.image.load(pathname)
    except pygame.error, message:
        securedPrint(u"Fail. Impossible de charger l'image : " + pathname)
        #On peut mettre "raise" sans rien apr�s. Ca recrache la derni�re exception en cours.
        raise

    #conversion dans le mode graphique actuel. On le fait qu'une fois au d�but
    #et apr�s c'est plus rapide pour les blits. Enfin... normalement, parce que sur Mac...
    #Si on switche plein-ecran/windowed, je sais pas ce que �a donne.
    #Si �a se trouve faudrait refaire le convert sur toutes les images.
    #Bon, �a marce quand m�me. C'est pas un drame si c'est pas hyper optimis�.
    if doConversion:
        image = image.convert()

    #ajout de la transparence en fonction du param�tre colorkey
    if colorkey is not None:

        if colorkey == -1:
            #la couleur de transparence est celle du 1er pixel
            #en haut � gauche de l'image
            colorkey = image.get_at((0,0))

        #je sais pas ce que c'est que ce RLEACCEL, mais �a doit �tre cool.
        image.set_colorkey(colorkey, pygl.RLEACCEL)

    #on balance l'image
    return image


def loadImgInDict(listImgIdWithFileName, prefixFileName="", colorkey=-1,
                  extension=".png"):
    """
    fonction permettant de charger tout plein d'images, et les ranger dans un dictionnaire.
    pas de gestion d'erreur si les chargement fails.
    C'est � peu pr�s g�r� dans la fonction LoadImg

    entr�e :
        listImgIdWithFileName : tuple de tuple de 2 elem, avec :
         - identifiant de l'image (int, ou autre chose)
         - nom de fichier court de l'image � charger (string)
        TRODO : pourquoi c'est d�clar� sous forme de tuple et �a se finit en dict ?
        pourquoi pas d�clarer un dict d�s le d�but ? et en sortir un autre dict ?
        r�ponse : osef. C'est pas grave si c'est foutu comme �a.

        prefixFileName : string. Pr�fixe des noms de fichier pour les images � charger.

        colorkey : voir fonction LoadImg

        extension : string. extension des noms de fichier image.

    plat-dessert : un dictionnaire
        cl� : identifiant de l'image (les m�mes que dans listImgIdWithFileName)
        valeur : Surface contenant l'image correspondante
    """

    dicImg = {}

    for imgIdentifier, shortFileName in listImgIdWithFileName:
        #cr�ation du nom entier � partir du nom court
        longFileName = prefixFileName + shortFileName + extension
        #chargementde l'image
        imgLoaded = loadImg(longFileName, colorkey)
        #rangement dans le dico
        dicImg[imgIdentifier] = imgLoaded

    return dicImg


def makeRotatedImg(imgToRotate, stepAngle):
    """
    cr�e un tuple contenant des Surface d'une image rotat�e.

    entr�es :
        imgToRotate : Surface contenant l'image de d�part � rotater
        stepAngle : int. angle, en degr�, indiquant le pas de degr� � avancer pour chaque image
                    on peut mettre un pas n�gatif, �a tournera dans le sens anti-trigo
                    C'est pas oblig� de tomber pil poil sur un multiple de 360 degr�s.
                    La derni�re image aura la valeur de l'angle de rotation du pas,
                    juste avant d'arriver au 360

    plat-dessert :
        tuple de X element (X = 360 / stepAngle arrondi inf�rieur), contenant les
        Surface des images rotat�es.
    """
    #const � la con
    NBR_DEGRE = 360

    #cr�ation de la liste des angles de rotation de chaque image. (avec pas negatif ou positif)
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
    g�n�re un nombre entier al�atoire, � distribution �gale (enfin � priori)
    compris entre -maximumRay inclus et +maximumRay inclus

    un peu useless, mais pas trop.
    """
    return random.randrange(-maximumRay, +maximumRay+1)


#TRODO pour plus tard : A l'avenir, �viter de faire le con � importer le random que dans common.
#random on peut bien l'avoir partout. et l'alias randRange, on le recr�e sur place � chaque fois.
#c'est juste un putain d'alias
randRange = random.randrange


def oppRect(rectToOpp):
    """
    construit un pygame.Rect avec les coordonn�es X et Y oppos�es.

    entr�es : rectToOpp : pygame.Rect (X, Y, width, height) dont auquel il faut
              oppositionner les coordonn�es. Oui �a veut rien dire ma phrase.

    plat-dessert : pygame.Rect (-X, -Y, width, height)
    """

    return pygame.Rect(-rectToOpp.left, -rectToOpp.top,
                       rectToOpp.width, rectToOpp.height)


def loadFonts():
    """
    charge toutes les fonts (polices de caract�re) n�cessaires au jeu.

    De ce que j'ai compris dans la doc, lorsqu'on charge une font,
    on doit imm�diatement sp�cifier sa taille. Et on ne peut pas la changer apr�s.
    Si on veut plusieurs tailles, faut charger plusieurs fois la font.

    Si des fonts ne peuvent pas �tre charg�e, la fonction �crit un message sur stdout,
    et tente de cr�er une font de secours, avec la font par d�faut du syst�me.
    si cette seconde �tape foire aussi, tout plante compl�tement. (Je l'ai pas g�r�, osef)

    plat-dessert :
        un tuple de 3 elem : (dictFont, fontDefault, boolean)

         - dictFont : dictionnaire :
            * cl� : le nom de la font
            * valeur : un autre dictionnaire :
                . cl� : la taille de la font
                . valeur : la font en elle-m�me. L'objet. Enfin !!!!

         - fontDefault : encore une font. celle par d�faut, avec une taille par d�faut

         - boolean. Indique si le chargement des font s'est fait totalement bien, ou pas.
    """

    #bon en fait mon mega-dictionnaire dictFont n'a que 2 elem :
    #la font par d�faut, avec 2 tailles. Hahahaha LOL !!!!
    #et du coup, je me permet un chargement � l'envers.
    #au lieu de remplir mon dictionnaire, puis de piocher l'un des elem dedans
    #pour en faire ma font par d�faut. Je charge les fonts, dont la font par d�faut
    #puis je remplis mon dico � l'arrache avec tout �a.
    #TRODO : faire �a mieux si on a besoin et envie.

    loadingOK = False

    #vague gestion du cas o� le pygame n'a pas les fonts.
    #�a plante pas dans cette fonction, mais y'a tout qui va planter apr�s. osef.
    if not pygame.font:
        securedPrint(u"Atation, impossible d'afficher du texte")
        return (None, None, loadingOK)

    #chemin et nom du fichier indiquant la font � charger
    fontDefaultPathName = os.path.join(FONT_DIRECTORY_NAME, FONT_DEFAULT_NAME)

    try:

        #tentative de chargement des fonts.
        fontDefault = pygame.font.Font(fontDefaultPathName, FONT_DEFAULT_SIZE)
        fontLittle = pygame.font.Font(fontDefaultPathName, FONT_LITTLE_SIZE)
        loadingOK = True

    except IOError, e:

        #�a a fail. On envoie un message, et on charge une font par d�faut.
        securedPrint(u"Font loadage fail. fichier : " + fontDefaultPathName)
        securedPrint(e)
        #la font par d�faut de pygame est illisible. Donc je la charge avec une taille
        #un peu plus grosse. C'est bancal, mais c'est du fonctionnement d�grad�. On a le droit.
        fontDefault = pygame.font.Font(None, FONT_DEFAULT_SIZE+6)
        fontLittle = pygame.font.Font(None, FONT_LITTLE_SIZE+6)

    #cr�ation du dictionnaire contenant toutes les font. M�me si y'en a que 2 dedans.
    dictFont = {}
    dictFont[FONT_DEFAULT_NAME] = {}
    dictFont[FONT_DEFAULT_NAME][FONT_DEFAULT_SIZE] = fontDefault
    dictFont[FONT_DEFAULT_NAME][FONT_LITTLE_SIZE] = fontLittle

    return (dictFont, fontDefault, loadingOK)


def sign(X):
    """
    fonction � la con pour avoir le signe de X. renvoie -1, 0 ou 1
    TRODO : y'en a pas une toute faite ? C'est con comme fonction
    """
    if X < 0:
        return -1
    if X == 0:
        return 0

    return +1


def randWithListCoef(listCoef):
    """
    g�n�re un nombre au hasard, entre 0 et N,
    avec des coefficient de proba diff�rent pour chaque nombre

    entr�e :
        listCoef : liste de int (positif ou nul), indiquant les coefs pour chaque valeur
                   possible. On peut avoir des coef de 0. Dans ce cas, ce nombre ne sera
                   jamais choisi.
                   La somme des coefs peut valoir n'importe quoi, on fait avec.

    plat-dessert
        int. nombre al�atoire g�n�r�e, compris entre 0 et len(listCoef)-1
    """

    #d�termination de la plage de random ( = somme de tous les coefs,
    #et g�n�ration d'un nombre au hasard, dans cette plage.
    randMax = sum(listCoef)
    choiceValue = randRange(randMax)

    choiceIndex = 0

    #il faut trouver � quelle choix correspond le nombre qu'on a g�n�r� au hasard.
    #on avance dans la liste des coefs. A chaque fois, on retire le coef du choix
    #en cours. Quand on arrive � un choix, alors que le nombre est descendu en dessous
    #de son coef, alors c'est ce choix qui est le bon.
    #Et �a marche, bon c'est tout simple. Pas besoin de plus d'explication, bordel.
    while choiceValue >= listCoef[choiceIndex]:

        choiceValue -= listCoef[choiceIndex]
        choiceIndex += 1

    #voili voil�, on a trouv� le choix qu'a �t� fait.
    return choiceIndex


def randBoole():
    """
    g�n�re un boolean al�atoire. Avec distribution �gale.

    plat-dessert : bool�ean. True ou False. Le choix se fait au hasard.
    """
    if randRange(2) == 0:
        return True
    else:
        return False


def addListRectOrNot(listRectSource, listRectToAddOrNot):
    """
    ajoute une liste de Rect � une autre liste de Rect existante. Ou pas.
    Si la liste de Rect � ajouter est None, on l'ajoute pas.

    Je suis oblig� de cr�er cette fonction de merde, parce que quand on fait listRect += None,
    Ca plante compl�tement, au lieu de ne rien faire. Ah bravo !!

    entr�e :
        listRectSource : liste de Rect.
        listRectToAddOrNot : liste de Rect, ou bien valeur None.

    plat-dessert :
        rien du tout. Mais le contenu de listRectSource est modifi� en live.
    """
    if listRectToAddOrNot is not None:
        listRectSource += listRectToAddOrNot


def moveIndexInBounds(indexInit, delta, min, max, loopAuthorized):
    """
    d�place un index entre deux limites, selon un delta.
    Si l'index d�passe les limites, et qu'on autorise le loop, on renvoie min, ou max,
    en faisant un tour du compteur. Si on n'autorise pas le loop, on renvoie None.

    La fonction ne fait pas de calcul savant, que si on a un delta sup�rieur � 1, il faut
    avancer un peu, puis faire le tour, puis re-avancer un peu. Si y'a un tour de compteur,
    on renvoie min, ou max, et pis c'est tout.

    entr�e :
        indexInit : int. valeur initiale de l'index

        delta : int. valeur de d�placement (positif ou negatif) � appliquer � l'index

        min, max : int. avec min <= max. Valeurs limites entre lesquelles l'index doit rester.
                   c'est dans la philosophie python. C'est � dire que c'est min inclu, max exclu.
                   (je trouve �a ridicule de dire "philosophie" python, mais j'aime bien �tre
                   ridicule. Ouh putain, �a vibre ce camion-bus.)

        loopAuthorized : boolean. Si on sort des limites et que c'est False, on renverra None.
                         Si on sort des limites et que c'est True,
                         on renverra min ou max, selon o� on a d�pass�.

    plat-dessert :
        int, compris entre min inclu et max exclu, ou None.
    """

    #application du delta
    indexNew = indexInit + delta

    #j'ais pas voulu �crire cette condition sous la forme A <= B < C. Parce que y'a un
    #inf�rieur strict, et un inf�rieur ou �gal. Ca m'emb�tait de les mettre dans le m�me sac,
    #alors que c'est pas tout � fait le m�me type de condition.
    if (min <= indexNew) and (indexNew < max):
        #on est entre les limites. on peut renvoyer l'index delta-ifi�.
        return indexNew

    #on n'est pas entre les limite.
    if not loopAuthorized:
        #interdit de faire des tours du compteur. donc on renvoie None.
        return None

    if indexNew >= max:
        #on a d�pass� les limites par la borne sup�rieure. comme on fait le tour du compteur,
        #on renvoie la valeur de la borne inf�rieure.
        return min

    #dans l'autre cas, ben c'estle contraire. Faut renvoyer la borne sup�rieure.
    #Comme les limites, c'est min inclu et max exclu, la borne sup, c'est max-1.
    return max-1


def colorCompAdd(colorComp, delta):
    """
    ajoute ou soustrait une valeur � une composante de couleur RGB.
    La valeur r�sultat reste comprise entre les bornes des composantes de couleur,
    C'est � dire entre 0 et 255.

    Hemmm.... Cette fonction ne sert � rien. Je l'utilise jamais. Merci au revoir.
    Allez, y'a qu'� dire qu'on la garde pour plus tard si jamais y'a besoin.

    entr�e :
        colorComp : int. (� priori compris entre 0 et 255, mais si �a l'est pas c'est pas grave
                    Valeur initiale de la composante RGB.

        delta : int positif ou n�gatif, pas de bornes limites. Valeur � ajouter � la composante.

    plat-dessert :
        La composante et le delta ajout�. int compris entre 0 et 255
    """

    #putain, il peut pas faire �a tout seul ce putain de python ?
    #Paye ton code pas optimis�. Heureusement que j'en ai besoin que pour des conneries.
    colorCompRes = colorComp + delta

    if colorCompRes > 255: return 255
    if colorCompRes < 0:   return 0
    return colorCompRes


def pixTranspColor(surfaceSource, tupleRVBColor, transparency):
    """
    ajoute un filtre de couleur transparent � une image.

    entr�es :
        surfaceSource : pygame.Surface. Image de d�part sur laquelle on veut mettre le filtre.

        tupleRVBColor : tuple de 3 octets. composantes RGB de la couleur du filtre

        transparency : int (entre 0 et 255, c'est mieux). Transparence du filtre.
                       0 = totalement transparent. 255 = totalement opaque.

    plat-dessert :
        objet pygame.Surface, de la m�me taille que l'image source.
        C'est l'image avec le filtre.
        (On cr�e une nouvelle surface, on ne modifie pas le contenu de surfaceSource.)
    """

    #cr�ation de la nouvelle surface, et copie-collage de l'image d'origine sur cette surface.
    (width, height) = surfaceSource.get_size()
    surfaceDest = pygame.surface.Surface((width, height))
    #Le convert, faut le faire syst�matiquement pour optimiser les utilisations ult�rieures.
    #(Je l'ai toujours trouv� bizarre ce mot : "ult�rieur". Ca fait : "cul-terreux").
    surfaceDest.convert()
    surfaceDest.blit(surfaceSource, (0, 0))

    #cr�ation d'une surface repr�sentant le filtre. M�me taille que l'image, mais on la colorie
    #enti�rement avec la couleur du filtre.
    surfaceTransp = pygame.surface.Surface((width, height))
    surfaceTransp.fill(tupleRVBColor)
    #d�finition du degr� de transparence du filtre.
    surfaceTransp.set_alpha(transparency)

    #on copie-colle le filtre sur la surface de destination. Comme on a d�fini sa transparence,
    #�a fait pas un vrai copier-coller-paf-comme-�a. Ca m�lange les couleurs, comme dirait
    #Francis Cabr�leu.
    surfaceDest.blit(surfaceTransp, (0, 0))

    #TRODO pour plus tard : Bizarre qu'il faille cr�er toute une surface de filtre juste pour
    #faire �a. Y'a pas moyen d'appliquer direct une couleur avec une transparence ? A chercher.

    return surfaceDest


def pixTranspLight(surfaceSource, light, transparency):
    """
    applique un filtre de lumi�re ou de sombritude sur une image.
    (voir fonction pixTranspColor. Un filtre de lumi�re/sombritude, c'est comme un filtre
     de couleur, mais avec toutes les composantes �gales).

    entr�es :
        surfaceSource, transparency : voir param de pixTranspColor. C'est les m�mes.

        light : int (compris entre 0 et 255, c'est mieux). intensit� de la lumi�re/sombritude.

    plat-dessert : voir pixTranspColor
    """

    #cr�ation du tuple de composante RGB du filtre, � partir de l'intensit� de lumi�re du filtre.
    #(On r�p�te trois fois la m�me valeur, pour les trois couleurs RGB).
    tupleRVBColor = (light, ) * 3

    #Et paf, application du filtre de couleur qu'est un filtre lumineux.
    return pixTranspColor(surfaceSource, tupleRVBColor, transparency)

#Valeurs utilis�es pour les �l�ments de menu "image cliquable" (MenuSensitiveImage), et
#"case � cocher" (MenuTick). C'est la liste des valeurs d'intensit� lumineuse des filtres �
#appliquer � l'image d'origine, pour faire les images plus claires.
#On affiche successivement ces images quand le MenuElem prend le focus. Et wouw ! il s'illumine !
#(Ca nous y fait : 10, 30, 50, ... jusqu'� 130)
LIST_TRANSP_FOCUS = range(10, 150, 20)

def buildListImgLight(theImg, listTransp):
    """
    construit une liste d'image � partir d'une seule image, en appliquant des filtres
    d'intensit� de luminosit� maximales, avec des degr�s de transparence diff�rents.

    entr�es :
        surfaceSource : pygame.Surface. Image de d�part sur laquelle on veut mettre les filtres.

        listTransp : liste de int (tous compris entre 0 et 255, c'est mieux).
                     degr� de transparence des filtres lummineux pour chaque images

    plat-dessert :
        Liste de pygame.Surface. (Autant d'�l�ment qu'il y a d'�l�ment dans listTransp) + 1
        Ouais, y'a +1 parce qu'on ajoute l'image d'origine au d�but de la liste. Car tel
        est mon bon vouloir.
        Les images r�sultante de l'application des filtres sur l'image d'origine.
    """

    #cr�ation de la liste d'image avec l'application des filtres ultra-luminique
    #(intensit� de lumi�re = 255)
    listImgWithLight = [ pixTranspLight(theImg, 255, transparency)
                         for transparency in listTransp ]

    #ajout de l'image d'origine au d�but de la liste.
    listImgWithLight.insert(0, theImg)

    #tuplifiage de la liste pour acc�l�rer les acc�s ult�rieurs (cul-terrieurs).
    listImgWithLight = tuple(listImgWithLight)

    return listImgWithLight


def boundJustAttained(value, inc, limitDown, limitUp):
    """
    indique si une valeur a atteint/d�pass� les bornes dans lesquelles elle est cens�e rester,
    selon la direction dans laquelle cette valeur �volue. Wouaw !

    Tous les param�tres de cette fonction sont des int qui peuvent �tre positif ou n�gatif.
    (ouais, m�me le inc. Surtout le inc en fait)

    value : Valeur dont on v�rifie qu'elle a d�pass� les bornes ou pas

    inc : pas d'incr�mentation (ou de d�cr�mentation) de la valeur

    limitDown, limitUp : bornes inf et sup dans lesquelles la valeur devrait rester.
                         il vaut mieux que limitDown < limitUp, mais ce n'est pas v�rifi�,
                         donc faites comme vous voulez.

    plat-dessert :
        bool�en : True : la valeur a atteint ou d�pass� la limite vers laquelle elle avance.
                  False : la valeur n'a ni atteint, ni d�pass� la limite.

    Si la valeur �volue de mani�re croissante (inc > 0), on ne v�rifie pas si elle est en
    dessous de LimitDown. (osef, car c'est ainsi)
    Si la valeur �volue de mani�re d�croissante (inc < 0), on ne v�rifie pas si elle est
    au dessus de LimitUp. (osef aussi)
    Les limites de v�rification sont limitDown inclue, et limitUp exclue. Comme d'hab' en python.
    """

    #v�rification, lorsque la valeur est croissante, qu'elle ait atteint ou d�pass� la limite.
    #y'a -1 donc, parce qu'on fait tout le temps comme �a en python.
    if inc > 0 and value >= limitUp-1:
        return True

    #v�rification, lorsque la valeur est d�croissante, qu'elle ait atteint ou d�pass� la limite.
    if inc < 0 and value <= limitDown:
        return True

    #pas de d�passement ni d'atteignage. Ou alors, la valeur n'�volue pas (inc == 0)
    return False


def getRectDrawZone(rectPos, img):
    """
    R�cup�re la zone dans laquelle va se dessiner un MenuElem (self.rectDrawZone),
    en fonction de la taille et la position de l'image qu'il affiche.

    entr�es :
        rectPos : objet pygame.Rect indiquant la position du coin sup-gauche de l'image.
                  (la taille de ce rect, on s'en fout)

        img : objet pygame.Surface. L'image que le MenuElem va afficher.

    plat-dessert :
        objet pygame.Rect. zone de dessin du MenuElem, sur sa surface de destination.
    """

    #on r�cup�re la position.
    rectDrawZonePos = rectPos.topleft
    #on r�cup�re la taille (en pixel). C'est la taille de l'image, m'voyez.
    rectDrawZoneSize = img.get_rect().size
    #rassemblement de la position et de la taille pour obtenir la zone dans laquelle
    #cet �l�ment de menu va s'afficher.
    return pygame.Rect(rectDrawZonePos, rectDrawZoneSize)


def addThings(*listOfThings):
    """
    ajoute des trucs entre eux.

    entr�es :
        liste de trucs (n'importe quoi, mais faut qu'on puisse les additionner ensemble)

    plat-dessert :
        trucs (n'importe quoi) correspondant � la somme de tous les trucs de la liste.

    A partir d'une liste [ truc1, truc2, ... trucN ], la fonction renvoie la valeur unique
    truc1 + truc2 + ... + trucN

    la fonction sum() d�j� toute faite du python ne marche que pour les int. Fay chiay.
    """

    #paf. Voir fonction reduce du python pour les clampins qui conna�traient pas.
    return reduce(lambda x,y : x+y, listOfThings)
