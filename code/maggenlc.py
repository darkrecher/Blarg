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

date de la derni�re relecture-commentage : 29/09/2010

classe qui g�n�re les coordonn�es des patterns de magiciens

vocabulaire :

semi-amplitude de random sur une variable X : valeur enti�re.
la variable X a une valeur de d�part, et on la modifie un peu au hasard, pour le fun.
X peut �tre modifi� dans l'intervalle suivant : [ X - semi-amplitude , X + semi-amplitude ]

amplitude de random n�gative sur une variable X. valeur enti�re.
comme la semii-amplitude, mais X est modifi� dans l'intervalle suivant : [ X - amplitude, X ]

amplitude de random positive : blabla [ X, X + amplitude ]

Pour tous les patterns, on s'autorise � placer les magiciens en dehors de l'�cran si ils sont
trop � droite ou trop en bas. (Ca donne l'impression qu'ils arrivent de plus loin, et c'est cool)
Mais on les place pas trop en haut ou trop � gauche. Sinon �a rentre dans le mur du haut, ou
dans les �l�ments du menu. Et �a ferait tout pourri.

TRODO : c'est pas clair entre ce qui est randomis� sur place (d�calage, point de d�part du cercle,
et ce qui est randomis� ailleurs (isClockWise, etc.)
Faudra r�gler �a quand on aura un peu plus de "mati�re". Hahahahah aaaa !!!!!! fuck.
Ou alors faut pas le r�gler du tout, on laisse comme �a et on s'en fout.
"""

import math  #yeaaahh !!! cosinus et sinus FTW !!
import pygame

from common import (GAME_RECT, pyRect, centeredRandom, randRange, randBoole,
                    SHIFT_PREC, NOT_FLOATING_PREC)

from magician import MAGICIAN_SIZE

# --- noms de tous les patterns existants

(PAT_RAND,                       #placement des magiciens au hasard
 PAT_CIRCLE,                     #un cercle de magicien autour du h�ros
 PAT_DIAG,                       #les 4 diagonales de magiciens autour du h�ros
 PAT_LINE_VERTIC_TO_LEFT,        #ligne verticale, magiciens allant de droite � gauche
 PAT_LINE_VERTIC_TO_RIGHT,       #ligne verticale, dans l'autre sens
 PAT_LINE_HORIZ_TO_UP,           #ligne horizontale, magicien allant de bas en haut
 PAT_LINE_HORIZ_TO_DOWN,         #bla
 PAT_LINE_SWAP_VERTIC_TO_LEFT,   #ligne verticale de droite � gauche,
                                 #mais les magiciens du haut vont en bas, et vice-et-versaaaaa
 PAT_LINE_SWAP_VERTIC_TO_RIGHT,  #pareil, mais de gauche � droite
 PAT_LINE_SWAP_HORIZ_TO_UP,      #ligne horizontale de bas en haut, mais les magiciens de droite
                                 #vont � gauche, et lyc�e-de-versailles (jeu de mot nul, merci)
 PAT_LINE_SWAP_HORIZ_TO_DOWN,    #bla
) = range(11)

# --- d�finition de trucs pour les patterns de LINE VERTIC.

#dans un pattern de ligne vertical, on donne une coordonn�e X, qui sera la m�me pour tous
#les magiciens. Cette coordonn�e X sera un peu randomiz�e, pour le fun.
#on ne donne pas de coordonn�es Y pour le pattern, juste le nombre de magiciens.
#les magiciens seront plac�s de fa�on � prendre toute la hauteur de l'aire de jeu.
#mais on randomisera un peu le Y du premier magicien de la ligne, et l'�cart Y
#entre chaque magicien.


#semi-amplitude du random sur la coordonn�e X du pattern.
PTN_VERTIC_X_RAND_SEMI_AMPL = 10
#amplitude (positive) du random sur la position Y du premier magicien du pattern
PTN_VERTIC_Y_RAND_AMPL_START = 15
#amplitude (n�gative) du random sur la taille Y de la ligne verticale
#sur laquelle se r�partiront les magiciens.
PTN_VERTIC_Y_RAND_AMPL_SIZE = 15

#A cause de cette randomisation, et de la taille des magiciens, il faut pr�voir
#une marge de s�curit�. on ne place pas les magiciens sur toute la hauteur de l'aire de jeu.
#il faut donc enlever la hauteur du magicien, et le d�calage maximum du random sur
#la coordonn�e Y du premier magicien.
#on ne retire pas PTN_VERTIC_Y_RAND_AMPL_SIZE. Car cette amplitude de random est n�gative
#(elle est retir�e � l'�cartement de base entre les magiciens. En fait �a ajoute de la marge)
LENGTH_TO_REMOVE = PTN_VERTIC_Y_RAND_AMPL_START + MAGICIAN_SIZE.height
PTN_VERTIC_HEIGHT = GAME_RECT.height - LENGTH_TO_REMOVE

# --- d�finition de trucs pour les patterns de LINE HORIZ.

#blabla, voir LINE VERTIC

#semi-amplitude du random sur la coordonn�e Y du pattern.
PTN_HORIZ_Y_RAND_SEMI_AMPL = 10
#amplitude (positive) du random sur la position X du premier magicien du pattern
PTN_HORIZ_X_RAND_AMPL_START = 20
#amplitude (n�gative) du random sur la taille X de la ligne horizontale
#sur laquelle se r�partiront les magiciens.
PTN_HORIZ_X_RAND_AMPL_SIZE = 20

#blabla pareil que VERTIC
LENGTH_TO_REMOVE = PTN_HORIZ_X_RAND_AMPL_START + MAGICIAN_SIZE.width
PTN_HORIZ_WIDTH = GAME_RECT.width - LENGTH_TO_REMOVE

# --- d�finition de trucs pour les patterns de LINE HORIZ et VERTIC.

# ces deux patterns ont une coordonn�e principale (coord 1 = X pour le vertic, Y pour le horiz)
# et une coordonn�e secondaire (coord 2 = Y pour le horiz, X pour le vertic)

#Indique si on inverse les positions d'arriv�e des magiciens (SWAP), ou pas (KEEP).
#Quand on est KEEP, les magiciens se d�placent en ligne horizontale ou verticale.
#Quand on est SWAP, les magiciens passent tous plus ou moins par le centre de l'�cran.
SWAP = True
KEEP = False

#d�finition des patterns de line, (verticale ou horizontale, haha)
(LINE_VERTIC,  #les magiciens seront g�n�r�s sur une ligne verticale
 LINE_HORIZ,   # blabla ligne horizontale
) = range(2)

#big dictionnaire de config des patterns de LINE.
# cl� : type du pattern.
# valeur : tuple de 5 �l�ments :
#          - semi-amplitude de random sur la coordonn�e 1
#          - amplitude sur le d�part de la coord 2
#          - amplitude sur l'�cartement entre magicien, de la coord 2
#          - valeur de d�part de la coordonn�e 2 (Sans aucun rand)
#          - taille de la ligne (coord 2) sur laquelle r�partir les magiciens du patterns)
DICT_LINE_INFO = {

  LINE_VERTIC : (PTN_VERTIC_X_RAND_SEMI_AMPL,
                 PTN_VERTIC_Y_RAND_AMPL_START,
                 PTN_VERTIC_Y_RAND_AMPL_SIZE,
                 GAME_RECT.y,
                 PTN_VERTIC_HEIGHT,
                ),

  LINE_HORIZ  : (PTN_HORIZ_Y_RAND_SEMI_AMPL,
                 PTN_HORIZ_X_RAND_AMPL_START,
                 PTN_HORIZ_X_RAND_AMPL_SIZE,
                 GAME_RECT.x,
                 PTN_HORIZ_WIDTH,
                ),
}

#Rect contenant les coordonn�es principale de d�part et de fin des Pattern de Line.
#on les mets aux bords de l'aire de jeu, mais � une distance de 15
# (donc on inflate de -15*2, oui faut suivre, oui.)
# PL = PAT_LINE = PATTERN DE LINE putain. Je l'avais dit qu'il fallait suivre
PL_RECT_START = GAME_RECT.inflate(-30, -30)

#coordonn�es principale de d�part. (On les sorts du Rect, c'est plus pratique)
#il faut retirer la taille du magicien aux coordonn�es dee bas et de droite. Car
#quand on positionne un magi, on donne son coin sup�rieur gauche. Du coup, faut se
#rajouter cette marge sinon les magi seront cr��s en dehors de l'�cran.
PL_UP    = PL_RECT_START.top
PL_DOWN  = PL_RECT_START.bottom - MAGICIAN_SIZE.height
PL_LEFT  = PL_RECT_START.left
PL_RIGHT = PL_RECT_START.right - MAGICIAN_SIZE.width

#encore un dictionnaire de config des patterns de LINE, mais un peu plus pr�cis cette fois-ci.
#cl� : identifiant du pattern
#valeur : tuple de 4 �l�ments :
#         - type du pattern (param whichCoord)
#         - coordonn�e 1 de d�part des magiciens du pattern (param c1Start)
#         - coordonn�e 1 de fin des magiciens du pattern (param c1End)
#         - SWAP / KEEP (voir plus haut)
#
#                                 whichCoord,  c1Start,  c1End,    swapPos
DIC_PAT_LINE_INFO = {
 PAT_LINE_VERTIC_TO_LEFT       : (LINE_VERTIC, PL_RIGHT, PL_LEFT,  KEEP) ,
 PAT_LINE_VERTIC_TO_RIGHT      : (LINE_VERTIC, PL_LEFT,  PL_RIGHT, KEEP) ,
 PAT_LINE_HORIZ_TO_UP          : (LINE_HORIZ , PL_DOWN,  PL_UP,    KEEP) ,
 PAT_LINE_HORIZ_TO_DOWN        : (LINE_HORIZ , PL_UP,    PL_DOWN,  KEEP) ,
 PAT_LINE_SWAP_VERTIC_TO_LEFT  : (LINE_VERTIC, PL_RIGHT, PL_LEFT,  SWAP) ,
 PAT_LINE_SWAP_VERTIC_TO_RIGHT : (LINE_VERTIC, PL_LEFT,  PL_RIGHT, SWAP) ,
 PAT_LINE_SWAP_HORIZ_TO_UP     : (LINE_HORIZ , PL_DOWN,  PL_UP,    SWAP) ,
 PAT_LINE_SWAP_HORIZ_TO_DOWN   : (LINE_HORIZ , PL_UP,    PL_DOWN,  SWAP) ,
}

# --- d�finition de trucs pour le pattern PAT_CIRCLE

#nombre maximal de points sur le cercle
NBR_POINT_CIRCLE = 256

#rayon de base (en pixel) du cercle
CIRCLE_RAY = 100

#liste des angles trignomom�trique des points du cercle.
#hahaha ! j'ai �crit trignomom�trique !!
ANGLE_LIST = tuple([ (indexPoint * 2 * math.pi) / NBR_POINT_CIRCLE
                      for indexPoint in range(NBR_POINT_CIRCLE)
                   ])

#liste de Rect. Les points du cercle.
CIRCLE_COORD_LIST = tuple([ pyRect(math.cos(angle) * CIRCLE_RAY,
                                   math.sin(angle) * CIRCLE_RAY)
                            for angle in ANGLE_LIST
                          ])

# --- d�finition de trucs pour le pattern PAT_DIAG

#distance initiale (en pixel) entre le magicien et le joueur
#enfin c'est pas exactement la distance. c'est la distance vertic ou horiz d'une diagonale
#pour avoir la vraie distance, faut faire DIAG_DIST_INIT * <racine de 2>, mtlmsf
DIAG_DIST_INIT = 60

#pixel vertic et horiz ajout�e � la distance de diag initiale, pour placer les autrse magiciens
#apr�s qu'on ait plac� les 4 premiers sur les 4 diago.
DIAG_DIST_STEP = 12

#les magiciens ne sont pas plac�s exactement sur les diagonales. on les bouge un peu en random,
#juste parce que c'est cool.
#semi-amplitude de random en X, sur les coordonn�es des magiciens.
DIAG_DIST_X_RAND_SEMI_AMPL = 10
#semi-amplitude Y
DIAG_DIST_Y_RAND_SEMI_AMPL =  8

#direction des diagonales. C'est dans l'ordre trigo. C'est pas si important que �a,
#mais un peu quand m�me
DIAG_LIST_DIR = (
 ( -1, -1),  #gauche haut. < ^
 ( -1, +1),  #gauche bas.  < V
 ( +1, +1),  #droite bas   > V
 ( +1, -1),  #droite haut  > ^
)

# --- d�finition de trucs pour les pattern PAT_CIRCLE et PAT_DIAG

#amplitude de migration en X et en Y.
#quand on cr�e un pattern de cercle ou de diagonale, si le h�ros est trop en haut et/ou trop
#� gauche de l'�cran, y'a des magiciens qu'on peut pas placer. Dans ce cas, on part
#des coordonn�es d'un magicien qu'on a pu placer, on migre un peu vers la droite et le bas
#(en random) et on place notre magicien. (Et ainsi de suite pour tous les magi qu'on pas
#pu �tre plac�s.
#amplitude positive de migration en X
MIGR_X_RAND_AMPL = 20
#amplitude positive de migration en Y
MIGR_Y_RAND_AMPL = 15


class MagicianListCoordBuilder():
    """
    classe qui g�re la cr�ation des magiciens (de tout poil) (hahaha).
    merde, j'ai d�j� dit �a dans le maggen.py. Du coup elle est plus dr�le du tout ma phrase.
    """

    def __init__(self, hero):
        """
        constructeur. (thx captain obvious)

        entr�e : hero : r�f�rence vers le h�ros. C'est juste pour choper
                        sa position, quand on veut faire un cercle ou un diag
                        autour de lui.
        """
        #dictionnaire de correspondance entre les types de pattern centr� sur un point,
        #et la fonction permettant de le g�n�rer. (beurkh, mal au ventre)
        #je suis oblig� de le foutre l�, le dico, car je dois pointer sur les fonctions
        #de cette classe. TRODO : voir si on peut pas le sortir d'ici quand m�me
        self.DIC_PAT_CENTER_FUNCTION = {
            PAT_CIRCLE : self.generateCirclePattern,
            PAT_DIAG   : self.generateDiagPattern,
        }

        self.hero = hero


    def generateLinePattern(self, nbrMagi, whichCoord, c1Start,
                            reverseStartSide, c1End=None, swapPos=None):
        """
        g�n�re les coordonn�ez pour un pattern de ligne (horiz on vertic)

        entr�es :
            nbrMagi : int. nombre de magicien � mettre dans le pattern.
            whichCoord : type de pattern. LINE_VERTIC ou LINE_HORIZ
            c1Start :  int. valeur de la coordonn�e principale (coord 1)
                       (X pour une vertic, Y pour une horiz)
            reverseStartSide : boolean. indique dans quel ordre ont range les magiciens
                (Ca aura une influence sur l'ordre dans lequels ils appara�tront, si jamais
                ils apparaissent un par un). si LINE_VERTIC :
                False : ordre de haut en bas, True : ordre de bas en haut.
                si LINE_HORIZ :
                False : ordre de gauche � droite, True : ordre de droite � gauche
            c1End : si None, on ne fabrique pas les coordonn�es de fin
                    si int, indique la valeur de la coordonn�e principale de fin (coord 1)
            swapPos : si c1 vaut None, ce param ne sert � rien. Sinon, c'est SWAP ou KEEP
                      indique si on �change les coordonn�es de fin entre les magiciens.

        plat-dessert :
            tuple de 2 �l�ments :
             - liste de Rect de nbrMagi �l�ments. coordonn�es de d�part pour les
               magis du pattern � cr�er.
             - soit None, soit liste de Rect de nbrMagi �l�ments (coordonn�e de fin).
               �a d�pend si on a demand� � cr�er les coordonn�es de fin ou pas, via le param c1End
        """

        #r�cup�ration de la config li� au type de pattern (VERTIC ou HORIZ)
        (c1RandSemiAmpl, c2RandAmplStart, c2RandAmplSize, c2Start, c2Size,
        ) = DICT_LINE_INFO[whichCoord]

        #ajout de la composante random sur la coordonn�e principale de d�part
        c1StartRand = c1Start + centeredRandom(c1RandSemiAmpl)

        #calcul de la taille de la ligne sur laquelle on va r�partir les magiciens
        #avec un petit coup de random � amplitude n�gative dessus)
        #on la met en n�gatif car �a permet  d'�tre s�r que �a d�passera pas l'�cran.
        c2sizeRand = c2Size - randRange(c2RandAmplSize)
        #calcul de la distance entre les magiciens.
        c2Step = c2sizeRand / nbrMagi
        #calcul de la coordonn�e secondaire de d�part du premier magicien de la ligne.
        #on ajoute c2Step/2, parce que on va faire comme �a en fait :
        #bord. 1/2 dist. magi.     dist.        magi.       dist.      magi. 1/2 dist. bord
        #   |   ---------  *  ------------------  *  ------------------  *  ---------   |
        #ha! le sch�ma de la mort! Ouais, finalement je vais me droguer, au lieu de coder des jeux
        c2StartRand = c2Start + c2Step / 2 + randRange(c2RandAmplStart)

        #cr�ation d'une liste allant de 0 � nbrMagi-1, pour apr�s, cr�er les coord 2
        if reverseStartSide:
            #la liste doit �tre mise � l'envers.
            #on compte de 0 � nbrMagi-1, et on inverse la liste. ( c'est ce que fait le [::-1] )
            #je veux pas directement compter de nbrMagi-1 � 0, car �a fait du code mega moche :
            # range(nbrMagi-1, -1, -1). Je l'aurais fait si c'�tait une grosse liste.
            c2ListMagi = range(nbrMagi)[::-1]
        else:
            #y'a juste � compter, sans inverser.
            c2ListMagi = range(nbrMagi)

        #cr�ation des valeurs de la coordonn�e secondaire, � partir de la liste.
        c2ListMagi = [ magi * c2Step + c2StartRand for magi in c2ListMagi ]

        #cr�ation des Rect rassemblant la liste des coord 1 et des coord 2,
        #en les mettant au bon endroit, (X ou Y), selon le type de ligne.
        if whichCoord == LINE_VERTIC:
            #c1 dans X, c2 dans Y. captain obvious
            listCoordStart = [ pyRect(c1StartRand, c2Magi)
                               for c2Magi in c2ListMagi ]
        else:
            #c1 dans Y, c2 dans X. captain obvious
            listCoordStart = [ pyRect(c2Magi, c1StartRand)
                               for c2Magi in c2ListMagi ]

        #si on n'a pas demand� les coordonn�es de fin, on peut se barrer tout de suite.
        if c1End is None:
            return listCoordStart, None

        #ajout de la composante random sur la coordonn�e principale de fin
        c1EndRand = c1End + centeredRandom(c1RandSemiAmpl)

        #la coordonn�e secondaire de d�but et la secondaire de fin sont les m�mes
        #cr�ation des Rect rassemblant les listes des coords de fin,
        if whichCoord == LINE_VERTIC:
            #c1 dans X, c2 dans Y. captain obvious
            listCoordEnd = [ pyRect(c1EndRand, c2Magi)
                             for c2Magi in c2ListMagi ]
        else:
            #c1 dans Y, c2 dans X. captain obvious
            listCoordEnd = [ pyRect(c2Magi, c1EndRand)
                             for c2Magi in c2ListMagi ]

        #on inverse les coordonn�es de fin si on est en SWAP (voir blabla au d�but du fichier)
        if swapPos == SWAP:
            listCoordEnd.reverse()

        return listCoordStart, listCoordEnd


    def rayCenterMigrCoords(self, listCoordStart,
                            center, isClockWise, rayCoef=NOT_FLOATING_PREC):
        """
        fonction qui fait plein de truc pour les patterns PAT_CIRCLE et PAT_DIAG :
         - applique le clockWise
         - le coef du rayon,
         - le d�calage vers le centre,
         - la migration � l'arrache des points qui sont pas dans l'�cran.

        entr�es :
            listCoordStart : liste de Rect, contenant les coordonn�es de d�part des magiciens.
                             Elles sont arrang�es selon le pattern qu'on veut, on s'en fout.
                             Mais �a doit �tre un pattern avec un centre, pour l'instant : (0, 0)
                             Certaines coord pourront se retrouver en dehors de l'�cran.
                             Ce sera corrig�.
            center : Rect. coordonn�es du vrai centre autour duquel on veut construire le pattern.
                     (� priori, autour du h�ros)
            isClockWise : boolean. indique si on range les coordonn�es des magiciens
                          dans le sens des aiguilles d'une montre, ou dans le sens inverse.
            rayCoef : int (en virgule pas flottante). coefficient d'agrandissement-retrecissement
                      de la distance entre les coordonn�es des magiciens et le centre.
                      NOT_FLOATING_PREC correspond � un coef de 1.

        plat-dessert :
            listCoordStart : liste de Rect, avec autant d'�l�ments que la liste pass�s en
                             param�tres. Mais le contenu a �t� arrang� comme il faut.
        """

        #inversion de l'ordre des coordonn�es d'arriv�e. Quand on les associera � des magiciens,
        #on les verra appara�tre dans un ordre ou un autre.
        if not isClockWise:
            listCoordStart.reverse()

        #application du coef sur la distance magicien-centre.
        if rayCoef != NOT_FLOATING_PREC:
            for circPoint in listCoordStart:
                #multiplication par le coef, qui est en virgule-pas-flottante
                circPoint.x = (circPoint.x * rayCoef) >> SHIFT_PREC
                circPoint.y = (circPoint.y * rayCoef) >> SHIFT_PREC

        #d�placement des points vers le vrai centre, indiqu� en param
        centerCoord = center.topleft
        for circPoint in listCoordStart:
            circPoint.move_ip(centerCoord)

        #r�cup�ration du nombre de point que y'a au d�part
        lenInitlistCoordStart =  len(listCoordStart)

        #supression des points qui d�passe en haut et � gauche.
        #on autorise le d�passement en bas et � droite, (voir blabla plus haut)
        listCoordStart = [ circPoint for circPoint in listCoordStart
                           if circPoint.x > GAME_RECT.left and
                              circPoint.y > GAME_RECT.top
                         ]

        #nombre de points qui ont �t� supprim�s, et que donc il faut remettre
        nbrPointRemoved = lenInitlistCoordStart - len(listCoordStart)

        #migration � l'arrache des points qui ont �t� vir�.

        for _ in xrange(nbrPointRemoved):

            #choix � l'arrache d'un point valide (toujours dans l'�cran)

            if len(listCoordStart) == 0:
                #il n'y a plus aucun point valide, on les a tous vir�s.
                #fabrication super � l'arrache d'un point valide. (� droite du centre)
                circPoint = pyRect(center.x + CIRCLE_RAY, center.y)
            else:
                #il y a un ou plusieurs points valides
                #on en prend un au hasard.
                circPoint = listCoordStart[randRange(len(listCoordStart))]

            #migration du point, vers le bas et la droite, afin de trouver � l'arrache
            #un autre point valide � partir du premier.(pas de limite sur les bords droit et bas)
            pointArrache = pyRect(circPoint.x + randRange(MIGR_X_RAND_AMPL),
                                  circPoint.y + randRange(MIGR_Y_RAND_AMPL))

            #et ajout � l'arrache dans la liste.
            #� l'it�ration suivante de la boucle, on risque de repartir ce point cr�� � l'arrache,
            #pour en refabriquer un autre, encore plus d�cal�. C'est zarb, mais je m'en cogne.
            listCoordStart.append(pointArrache)

        return listCoordStart


    def generateCirclePattern(self, nbrMagi, center, isClockWise,
                              coordEnd=None, rayCoef=NOT_FLOATING_PREC):
        """
        construit les coordonn�es d'un pattern PAT_CIRCLE. Les points sont
        r�partis plus ou moins r�guli�rement, en cercle, autour d'un centre donn�,
        et selon un rayon de base de CIRCLE_RAY (constante = 100), auquel on applique un coef.

        entr�es :
            nbrMagi : int. nombre de magicien � mettre dans le pattern.

            center,
            isClockWise,
            rayCoef : voir les params de la fonction rayCenterMigrCoords

            coordEnd : si None, on ne fabrique pas les coordonn�es de fin
                       si autre chose, on les fabrique.

        plat-dessert :
            tuple de 2 �l�ments :
             - liste de Rect de nbrMagi �l�ments. coordonn�es de d�part pour les
               magis du pattern � cr�er.
             - soit None, soit liste de Rect de nbrMagi �l�ments (coordonn�e de fin).
               �a d�pend si on a demand� � cr�er les coord de fin ou pas, via le param coordEnd
        """

        #on a d�j� tout pleins de coordonn�es pr�calcul�es, pour un cercle de centre(0, 0),
        #et de rayon CIRCLE_RAY. On commence par prendre des points de ce cercle,

        #on veut des points r�guli�rement r�parti sur le cercle. Donc on calcule tous les combien
        #de qu'on doit prendre un point. (fran�ais power !)
        stepPoint = NBR_POINT_CIRCLE / nbrMagi

        #si y'a plus de magi que de points de cercle, on se chope un 0. Or faut quand m�me
        #avancer un minimum dans la s�lection des points
        #c'est un truc � la con qui arrivera jamais, mais on fout quand m�me la s�curit�.
        if stepPoint == 0:
            stepPoint = 1

        #On d�marre de n'importe quel point du cercle. Osef.
        startPointIndex = randRange(NBR_POINT_CIRCLE)
        #index du point d'arriv�e du cercle (sans tenir compte du modulo-tour-du-compteur-fuck
        endPointIndex = startPointIndex + nbrMagi*stepPoint

        #r�cup�ration des index de points du cercle.
        listPointIndex = range(startPointIndex, endPointIndex, stepPoint)
        #pour les index trop grands, on leur fait faire un tour du compteur avec un modulo
        listPointIndex = [ pointIndex % NBR_POINT_CIRCLE
                           for pointIndex in listPointIndex ]

        #r�cup�ration des coordonn�es des points du cercle, � partir des index
        listCoordStart = [ pygame.rect.Rect(CIRCLE_COORD_LIST[pointIndex])
                           for pointIndex in listPointIndex ]

        #fonction qui arrange plein de trucs avec les coordonn�es du cercle
        #(voir description de la fonction)
        param = (listCoordStart, center, isClockWise, rayCoef)
        listCoordStart = self.rayCenterMigrCoords(*param)

        #si on n'a pas demand� les coordonn�es d'arriv�e des magiciens, on s'en va direct.
        if coordEnd is None:
            return listCoordStart, None

        #sinon, on les construit. C'est facile, c'est le centre du cercle.
        listCoordEnd = (center, ) * nbrMagi

        return listCoordStart, listCoordEnd


    def generateDiagPattern(self, nbrMagi, center, isClockWise,
                            coordEnd=None, rayCoef=NOT_FLOATING_PREC):
        """
        Construit les coordonn�es d'un PAT_DIAG. Les points sont r�partis �quitablement sur les
        4 diagonales partant d'un centre donn�. La distance initiale centre-point
        est de DIAG_DIST_INIT. Lorsqu'on a plac� 4 magiciens sur les 4 diag, on augmente
        cette distance de DIAG_DIST_STEP, et ainsi de suite.
        On peut appliquer un coef sur toutes ces distances.
        Les points sont un peu randomiz�s autour de la diagonale.

        entr�es :
            nbrMagi : int. nombre de magicien � mettre dans le pattern.

            center,
            isClockWise,
            rayCoef : voir les params de la fonction rayCenterMigrCoords

            coordEnd : si None, on ne fabrique pas les coordonn�es de fin
                       si autre chose, on les fabrique.

        plat-dessert :
            tuple de 2 �l�ments :
             - liste de Rect de nbrMagi �l�ments. coordonn�es de d�part pour les
               magis du pattern � cr�er.
             - soit None, soit liste de Rect de nbrMagi �l�ments (coordonn�e de fin).
               �a d�pend si on a demand� � cr�er les coord de fin ou pas, via le param coordEnd
        """

        #on commence d'abord par cr�er les points du pattern autour du centre (0, 0),
        #sans aucun coef.

        #init de l'index sur les diagonales, il varie de 0 � 3.
        #L�, on part de n'importe laquelle des 4 diagonales, osef.
        diagCursor = randRange(len(DIAG_LIST_DIR))
        #distance (juste sur le X ou le Y) entre le centre et le point
        currentDistance = DIAG_DIST_INIT
        #liste qu'on va rempliture au fur et � mesure (Liane Foly)
        listCoordStart = []

        for indexMagi in xrange(nbrMagi):

            #on chope le tuple avec des +1 / -1 correspondant � la diagonale courante
            currentDiag = DIAG_LIST_DIR[diagCursor]

            #d�termination des coordonn�es du point, en fonction de la diag choisi.
            #copier-coller pas bien. Eventuellement, factoriser ce tout petit bout de code
            if currentDiag[0] == -1:
                coordX = -currentDistance
            else:
                coordX = +currentDistance

            if currentDiag[1] == -1:
                coordY = -currentDistance
            else:
                coordY = +currentDistance

            #cr�ation du point et ajout dans la liste
            coordStart = pyRect(coordX, coordY)
            listCoordStart.append(coordStart)

            #mise � jour de l'index de la diagonale. On compte de 0 � 3 en faisant des tours
            diagCursor += 1
            if diagCursor >= len(DIAG_LIST_DIR):
                diagCursor = 0

            #Toutes les 4 fois, mais seulement � partir de la quatri�me fois,
            #on augmente la currentDistance. �a fait : 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, ...
            if indexMagi & 3 == 3:
                currentDistance += DIAG_DIST_STEP

        #ajout d'un petit peu de random sur tous les points. Comme �a, pour rire.
        for point in listCoordStart:
            point.x += centeredRandom(DIAG_DIST_X_RAND_SEMI_AMPL)
            point.y += centeredRandom(DIAG_DIST_Y_RAND_SEMI_AMPL)

        #fonction qui arrange plein de trucs avec les coordonn�es du cercle
        #(voir description de la fonction)
        param = (listCoordStart, center, isClockWise, rayCoef)
        listCoordStart = self.rayCenterMigrCoords(*param)

        #si on n'a pas demand� les coordonn�es d'arriv�e des magiciens, on s'en va direct.
        if coordEnd is None:
            return listCoordStart, None

        #sinon, on les construit. C'est facile, c'est le centre du pattern.
        listCoordEnd = (center, ) * nbrMagi

        return listCoordStart, listCoordEnd


    def generateRandPattern(self, nbrMagi, coordEnd=None):
        """
        g�n�re un pattern de magicien avec tout random : les positions de d�part et d'arriv�e

        entr�es :
            nbrMagi : int. nombre de magicien � mettre dans le pattern.
            coordEnd : si None, on ne fabrique pas les coordonn�es de fin
                       si autre chose, on les fabrique.

        plat-dessert :
            tuple de 2 �l�ments :
             d�j� blablat� dans les fonctions plus haut. S'y r�f�rer, bordel
        """

        #cr�ation d'une liste de Rect avec les coordonn�es compl�tement random,
        #mais comprises dans l'aire de jeu, quand m�me.
        listCoordStart = [ pyRect(randRange(GAME_RECT.width) + GAME_RECT.left,
                                  randRange(GAME_RECT.height) + GAME_RECT.top)
                           for _ in xrange(nbrMagi)
                         ]

        #si on n'a pas demand� les coordonn�es d'arriv�e des magiciens, on s'en va direct.
        if coordEnd is None:
            return listCoordStart, None

        #cr�ation d'une autre liste de Rect random, pour les coordonn�es d'arriv�e
        listCoordEnd = [ pyRect(randRange(GAME_RECT.width) + GAME_RECT.left,
                                randRange(GAME_RECT.height) + GAME_RECT.top)
                         for _ in xrange(nbrMagi)
                       ]

        return listCoordStart, listCoordEnd


    def generatePattern(self, patternType, nbrMagi,
                        coordEnd=None, rayCoef=NOT_FLOATING_PREC):
        """
        grosse fonction de la mort qui reprend toute les autres. Permet de cr�er un pattern
        comme il faut, juste � partir de son type, et d'un minimum de config

        entr�es :
            patternType : identifiant du type de pattern
            nbrMagi : int. nombre de magicien � mettre dans le pattern.
            coordEnd : si None, on ne fabrique pas les coordonn�es de fin
                       si autre chose, on les fabrique.
            rayCoef : int (en virgule pas flottante). utilis� uniquement si le type du pattern
                      est PAT_CIRCLE ou PAT_DIAG. indique le coefficient
                      d'agrandissement-retrecissement de la distance entre les coordonn�es
                      des magiciens et le centre. NOT_FLOATING_PREC correspond � un coef de 1.

        plat-dessert :
            un pattern, comme d'hab. Voir les fonctions ci-dessus.
        """

        #on teste si le pattern est de type LINE
        patternLineInfo = DIC_PAT_LINE_INFO.get(patternType)

        if patternLineInfo is not None:

            #il est de type LINE. On r�cup�re la config de ce pattern
            whichCoord, c1Start, c1End, swapPos = patternLineInfo

            #choix en random de l'ordre d'apparition des magiciens.
            #(�a a pas trop d'importance)
            reverseStartSide = randBoole()

            #propagation du fait qu'on veuille pas les coord d'arriv�e
            if coordEnd is None:
                c1End = None

            #rassemblement de tous les params de config permettant de cr�er le pattern,
            #et appel de la fonction qui va le cr�er.

            param = (nbrMagi, whichCoord, c1Start,
                     reverseStartSide, c1End, swapPos)

            return self.generateLinePattern(*param)

        elif patternType in self.DIC_PAT_CENTER_FUNCTION:

            #le pattern est de type "centr� autour d'un point".
            #on chope la fonction correspondante qui permettra de le cr�er.

            #Pas top car j'acc�de deux fois de suite � DIC_PAT_CENTER_FUNCTION.
            #mais la seule autre solution, c'est de faire un else tout simple,
            #puis un get, puis un test si None ou pas. Et j'ai pas envie d'une
            #imbrication de if en plus. L�. Voil�. L�. Llalaalalalala
            funcPat = self.DIC_PAT_CENTER_FUNCTION[patternType]

            #choix en random de l'ordre d'apparition des magiciens.
            #(�a a pas trop d'importance)
            isClockWise = randBoole()

            #rassemblement de tous les params de config permettant de cr�er le pattern,
            #et appel de la fonction qui va le cr�er.

            #ATTENTION, truc important ! On remarquera que j'indique, pour le param�tre center,
            #la valeur self.hero.rectPos, qui correspond au coordonn�es du h�ros.
            #Ce n'est pas la valeur directe de ses coordonn�es, c'est une r�f�rence
            #vers ses coordonn�es. Cette r�f�rence est transmise � chaque magicien.
            #Bon, et �a change quoi ?
            #les magiciens de type MAGI_LINE prennent en compte leur coordonn�e d'arriv�e au
            #moment de leur cr�ation. Si ils ne sont pas tous cr��s en m�me temps (il y a du
            #delay entre eux), et que le h�ros bouge pendance ce temps, ils ne vont pas tous
            #se rendre au m�me point.
            #Dans le jeu, quand on voit un cercle de magicien se cr�er petit � petit autour de
            #soi, les magiciens ne vont pas tous se rendre au milieu du cercle. Ils iront un peu
            #n'importe o�, selon la fa�on dont le h�ros a boug�.
            #En fait j'ai pas fait expr�s d'avoir fait comme �a au d�but. Et apr�s je me suis
            #dit que c'�tait plut�t cool. Ca augmente la difficult� de ces patterns.

            #Voil� j'ai fini de blablater, on peut reprendre.

            param = (nbrMagi, self.hero.rectPos, isClockWise,
                     coordEnd, rayCoef)

            return funcPat(*param)

        else:
            #le pattern n'est ni un LINE, ni centr� autour d'un point.
            #Par d�faut, on g�n�re un pattern total random, et crac.
            return self.generateRandPattern(nbrMagi, coordEnd)

