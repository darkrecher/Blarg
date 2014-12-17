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

date de la derni�re relecture-commentage : 22/09/2010

classe qui �labore les patterns pour faire une wave de magiciens, en fonction
du HardMana qu'il poss�de.

vocabulaire :

wave : une "vague" de magicien. C'est � dire un ensemble de magiciens, qui arrivent
tous plus ou moins en m�me temps. Le joueur dispose d'un temps limit� pour
tous les d�gommer. Pass� ce temps, la wave suivante est "�labor�e". une wave
est un ensemble de pattern.
(�laborer = g�n�rer, mais je trouve �a plus chouette "�laborer")

pattern : suite de magiciens � g�n�rer. pour chaque magicien, on associe les infos
n�cessaires � sa cr�ation (position, level, ...) et une valeur de "delay".
car tous les magiciens d'un pattern n'apparaissent pas tous d'un coup.
le delay est cumulatif. Ex : le premier magicien a un delay de 7, le suivant
a un delay de 10. Le premier appara�tra dans 7 cycles, le suivant dans 17 cycles.
On peut faire appara�tre plusieurs magiciens d'un coup en leur mettant des delay de 0

dans les infos du pattern, on trouve les coordonn�es de d�part des magiciens. Et eventuellement
les coordonn�es de fin. Elles ne sont utiles que pour les magiciens de type MAGI_LINE.
Elles d�finissent l� o� ils doivent se rendre.
(les MAGI_RAND bougent au hasard, et n'ont donc pas de coord de fin)

HardMana (HarM) : valeur num�rique. "Mana de difficult�". Le waveGenerator d�penses ce mana
pour acheter des patterns, les am�liorer, etc...
Entre deux waves, on redonne du HardMana au waveGenerator. Et on lui en redonne de plus
en plus.
Mais il faut racheter les patterns et les am�liorations de pattern entre chaque wave.

le waveGenerator d�pense le plus possible du HardMana qu'il poss�de � chaque wave.
Le petit reste qu'il n'a pas pu d�penser est report� � la wave suivante.
Ceci est �galement valable � l'int�rieur d'une wave. C'est � dire que quand le waveGen doit
acheter un certain truc, et qu'il ne d�pense pas tout le HarM allou� pour cela,
alors le reste est report� pour le prochain truc qu'il doit acheter.

Le HardMana est une classe � part enti�re. Car on a parfois besoin de le r�partir en
plusieurs petits bouts, de d�cider si on ach�te un truc ou pas en fonction du Mana qu'on a, ...
HardMana = harM : c'est la m�me chose mais en abr�g�

anti-HardMana (AntiHarM) : C'est du mana invers�. Du "mana de facilit�". Si le joueur termine
une wave en moins de temps que le temps pr�vu, il gagne de l'AntiHarM.
l'AntiHarM est d�pens� tout de suite, pour diminuer la quantit� de HarM allou�e � la prochaine
�laboration de wave. 1 HarM et 1 AntiHarM s'annulent.

a chaque wave, le waveGenerator fabrique deux sortes de patterns
 - 1 pattern principal : toujours constitu� de magiciens de type Rand (ils se d�placent au hasard)
 - 0, 1 ou plusieurs patterns suppl�mentaires. des magiciens Rand ou des magiciens Line.
TRODO : nommage un peu pourri. Dans le code, j'appelle le pattern principal PatRand,
et les patterns sup euh... Pat. Tout connement. C'est moche.

magiCoefCost : coefficient de co�t pour l'achat ou l'am�lioration d'un magicien. Ce coef varie
en fonction du type du magicien, et du pattern dans lequel on le place. pour les magi random,
il est tr�s haut. Car un magicien qui bouge au hasard est bien plus dangereux qu'un magicien
qui bouge dans une simple ligne droite.
Le magiCoefCost est utilis� pour :
 - acheter les magiciens d'un pattern
 - augmenter le level des magiciens d'un pattern
 - ... (ouais, c'est facile, de mettre des point-point-point. Eh bien fuck)
"""

from common import (randRange, SHIFT_PREC, NOT_FLOATING_PREC)

#moi j'importe des tonnes de trucs en les sp�cifiant un par un. Et c'est le bien de faire �a !!
#ma conne de chef qui me dit que quand y'en a beaucoup, faut mettre *. PAUV' CONNE ! Je te hais.
from maggenlc import (MagicianListCoordBuilder,
                      PAT_RAND,
                      PAT_CIRCLE,
                      PAT_DIAG,
                      PAT_LINE_VERTIC_TO_LEFT,
                      PAT_LINE_VERTIC_TO_RIGHT,
                      PAT_LINE_HORIZ_TO_UP,
                      PAT_LINE_HORIZ_TO_DOWN,
                      PAT_LINE_SWAP_VERTIC_TO_LEFT,
                      PAT_LINE_SWAP_VERTIC_TO_RIGHT,
                      PAT_LINE_SWAP_HORIZ_TO_UP,
                      PAT_LINE_SWAP_HORIZ_TO_DOWN)

from hardmana import HardMana

#liste des diff�rents types de magicien
(MAGI_BASE, #le magicien de base qui bouge pas. (en fait on en g�n�re jamais des comme �a)
 MAGI_RAND, #le magicien random, qui bouge n'importe comment
 MAGI_LINE, #le magicien line, qui bouge en ligne droite, puis s'arr�te.
) = range(3)

#HardMana allou� au d�part, pour cr�er la premi�re wave. (Oui, zero, oui)
HARM_FUNDS_INIT = 0

#delay (nbre de cycle) initiale entre la g�n�ration de deux magiciens d'un m�me pattern.
#le tout premier magicien d'un pattern n'est pas cr�� d�s le d�part. Il est cr�� au bout
#du temps de delay, le suivant : 2 fois le temps, etc.
#(un peu zarb' que le tout premei soit pas cr�� d�s le d�part, mais je trouve �a cool)
DELAY_MAGI_INIT = 40
#temps de diminution du d�lai, lorsque le waveGenerator d�cide d'acheter une diminution de delay,
#en payant du HardMana. (Chaque diminution coute plus cher que la pr�c�dente)
DELAY_MAGI_DECR = -5

#pour les patterns PAT_CIRCLE et PAT_DIAG : coefficient initial de la distance
#entre les magiciens et le joueur. (Utilisation de nombre � virgule pas-flottante)
#en fait, l� �a repr�sente un coefficient de 1.0
RAY_CIRCLE_INIT = NOT_FLOATING_PREC
#valeur de diminution du coef, � chaque fois que le waveGenerator d�cide d'acheter une
#diminution de coef. (en payant du HardMana, blablabla)
RAY_CIRCLE_DECR = -12

#quantit� de HarM allou� en plus � chaque nouvelle wave. C'est une valeur d'"acc�l�ration".
#� la 1ere wave on a 0. La 2eme : 20. La troisi�me 20*2, etc...
HARM_INCREMENTATION_OF_INCREMENTATION_PER_WAVE = 20

#magiCoefCost pour les magiciens de type MAGI_RAND.
#(pour les magiciens MAGI_LINE, le coefCost d�pend du pattern utilis� pour le g�n�rer)
MAGI_RAND_COEF_COST = 10

#liste de tuple, pour choisir le pattern principal (RAND, oui nommage fail, oui)
#chaque tuple contient 3 �l�ments :
#  - probabilit� de s�lection (parmi toutes les probas de s�lection
#    de tous les patterns dispos, et abordable)
#  - co�t, en HardMana
#  - identifiant du pattern
LIST_PATTERN_CHOICE_GEN_RAND = (
    (224,  0, PAT_RAND, ),
    ( 12, 10, PAT_CIRCLE, ),
    (  4, 10, PAT_DIAG, ),
    (  2,  1, PAT_LINE_VERTIC_TO_LEFT, ),
    (  2, 20, PAT_LINE_VERTIC_TO_RIGHT, ),
    (  2, 15, PAT_LINE_HORIZ_TO_UP, ),
    (  2, 15, PAT_LINE_HORIZ_TO_DOWN, ),
    (  2,  1, PAT_LINE_SWAP_VERTIC_TO_LEFT, ),
    (  2, 20, PAT_LINE_SWAP_VERTIC_TO_RIGHT, ),
    (  2, 15, PAT_LINE_SWAP_HORIZ_TO_UP, ),
    (  2, 15, PAT_LINE_SWAP_HORIZ_TO_DOWN),
)

#liste de tuple, pour choisir les pattern suppl�mentaires (PAT, oui nommage fail, oui)
#chaque tuple contient 3 �l�ments :
#  - probabilit� de s�lection (parmi toutes les probas de s�lection
#    de tous les patterns dispos, et abordable)
#  - co�t initail, en HardMana (plus on ach�te de pattern sup, plus les suivants sont chers)
#  - sous-tuple de 2 elem, avec :
#     *  magiCoefCost des magiciens de type MAGI_LINE g�n�r�s dans ce pattern.
#     *  identifiant du pattern
LIST_PATTERN_CHOICE_GEN_PAT = (
    ( 5, 15, (4, PAT_RAND)),
    (50, 20, (1, PAT_CIRCLE)),
    ( 5, 20, (4, PAT_DIAG)),
    (15, 15, (2, PAT_LINE_VERTIC_TO_LEFT)),
    ( 3, 40, (6, PAT_LINE_VERTIC_TO_RIGHT)),
    ( 8, 30, (3, PAT_LINE_HORIZ_TO_UP)),
    ( 8, 30, (3, PAT_LINE_HORIZ_TO_DOWN)),
    (20,  5, (2, PAT_LINE_SWAP_VERTIC_TO_LEFT)),
    ( 3, 30, (6, PAT_LINE_SWAP_VERTIC_TO_RIGHT)),
    ( 8, 12, (3, PAT_LINE_SWAP_HORIZ_TO_UP)),
    ( 8, 12, (3, PAT_LINE_SWAP_HORIZ_TO_DOWN)),
)

#augmentation appliqu�e au co�t de tous les patterns sup, � chaque fois qu'on en ach�te un
COST_PATTERN_SUP_INCR = 20

#d�calage � appliquer entre le magiCoefCost pour acheter un magicien, et le magiCoefCost pour
#configurer un magicien (diminuer son d�lai, augmenter son niveau, ...)
MAGI_COEF_COST_DECAL_NBR_CONF = 2

#temps "de baaaaase" donn� au joueur pour tuer tous les magiciens d'une wave
TIME_WAVE_BASE = 350
#coefficientde conversion entre la difficult� d'une wave et le temps donn� en plus
#(voir plus loin pour le calcul de la difficult� d'une wave, je me suis pas trop pris la t�te)
TIME_WAVE_COEF_DIFFICULTY = 10


def bla(*msg):
    """
    fonction � la con pour faire du debug
    """
    pass
    #ligne a commenter si on veut pas de debug.
    #et moi je suis pas un gros boulet ! Je fous pas un bool�en de merde DEBUG_ACTIVATED,
    #que personne n'utilise, et que �a va faire tout ralentir.
    #l�, quand y'a que l'instruction "pass" dans la fonction, on peut penser que le python
    #se d�merde pour l'optimiser, ou je sais pas quoi. bordel.
    #Ho et pis osef. De toutse fa�son je la virerais compl�tement � la fin. alors.
    ##print msg


class MagicianWaveGenerator():
    """
    classe qui g�re la cr�ation des vagues de magiciens. d�j� dit, oui.
    """

    def __init__(self, hero):
        """
        constructeur. (thx captain obvious)

        entr�e :
            hero : r�f�rence vers le h�ros. C'est juste pour pouvoir choper ses coordonn�es,
                   pour quand on cr�e des pattern PAT_CIRCLE ou PAT_DIAG.
        """

        #sous classe qui fabrique r�ellement les patterns,
        #en fonctions des infos de config qu'on lui donne
        self.magicianListCoordBuilder = MagicianListCoordBuilder(hero)

        #valeur courante de harM, qui va servir � acheter tout le bazar.
        self.harMTotal = HardMana(HARM_FUNDS_INIT)
        #quantit� de harM allou� � chaque nouvelle wave
        self.incrForHarM = 0
        #pas de AntiHarM au d�part.
        self.antiHarM = HardMana()
        #juste un compteur de wave � la con.
        self.indexCurrentWave = 0

        #alias � la con pour un nom plus court
        self.funcGenPat = self.magicianListCoordBuilder.generatePattern


    def receiveAntiHarMBonus(self, antiHarMBonus):
        """
        fonction � ex�cuter par des "stimulis ext�rieurs". Pour ajouter du AntiHarM,
        lorsque le joueur a r�ussi � faire des trucs skill�
        (genre buter tous les magi super rapidement, et genre c'est tout parce que c'est
        le seul moyen de choper de l'antiHarM)

        entr�e :
            antiHarMBonus : int. quantit� de antiHarM � rajouter.
        """
        self.antiHarM.addHarM(antiHarMBonus)
        bla("recevied antiHarM : ", antiHarMBonus, "  total : ", self.antiHarM)


    def addHarMForNextWave(self):
        """
        mise � jour de TotalHarM, et de incrForHarM, du fait qu'il faut g�n�rer une nouvelle wave.
        Ah c'est marrant de dire "du fait de". Faudrait que je le fasse plus souvent
        """
        bla("-------- more harM for newt wave --------")
        bla("harMTotal avant magouillerie : " + str(self.harMTotal))
        bla("antiHarm : " + str(self.antiHarM))

        #augmentation de harMTotal et incrForHarM
        self.harMTotal.addHarM(self.incrForHarM)
        self.incrForHarM += HARM_INCREMENTATION_OF_INCREMENTATION_PER_WAVE

        #d�cr�mentation du harM si on s'est pris de l'antiHarM
        self.harMTotal.antiHarMDebuff(self.antiHarM)


    def mergeGenPatInfo(self, magType,
                        listCoordStart, listCoordEnd=None,
                        magLevel=1, magLevelList=None,
                        delayValue=DELAY_MAGI_INIT, delayValueList=None):
        """
        wouhouuu, fonction qui rassemble un tas de trucs venant de n'importe o�,
        pour fabriquer toutes les infos n�cessaires � la cr�ation d'un pattern

        entr�es :
            magType        : type des magiciens � g�n�rer dans le pattern (RAND, LINE, ...)
            listCoordStart : liste de Rect. coordonn�es de d�part des magiciens
            listCoordEnd   : liste de Rect. coordonn�es de fin. utiles uniquement pour
                             les MAGI_LINE. Sinon, on peut mettre None.
            magLevel       : int. valeur de level de tous les magiciens du pattern.
                             (param�tre non utilis� si magLevelList is not None)
            magLevelList   : liste de int. valeur de level de chacun des magiciens du pattern
            delayValue     : int. d�lai d'attente (en nbre de cycle) entre la cr�ation de deux
                             magiciens du pattern.
                             (param�tre non utilis� si delayValueList is not None)
            delayValueList : liste de int. d�lai d'attente de chacun des magiciens du pattern

            listCoordStart doit �tre obligatoirement d�fini (pas de valeur None)
            la longueur de cette liste donne le nombre de magiciens � cr�er dans le pattern.

            listCoordEnd, magLevelList et delayValueList peuvent �tre non d�finie. (fix�e � None)
            Lorsqu'elles sont d�finies, ces 4 listes doivent toutes avoir le m�me nombre
            d'�l�ment. Sinon �a p�te.

        plat-dessert :
            genPattern : une liste. chaque �l�ment repr�sente un magicien � cr�er,
            ils sont constitu�s d'une sous-liste de 2 �l�ments.
             - temps de d�lai avant g�n�ration de ce magicien, (et passage au magi suivant)
             - infos concernant le magicien. C'est un sous-sous-tuple de 4 �l�ment :
                * type du magicien (LINE, RAND, ...)
                * rect. coordonn�e de d�part
                * rect ou None. coordonn�e d'arriv�e. (utile pour MAGI_LINE)
                * int. level.

            les deux premiers niveaux d'information doivent obligatoirement �tre une liste
            et une sous-liste (pas de tuple, sous-tuple). Car plus tard, on va avoir besoin
            de tripoter les donn�es que y'a dedans. (C'est le MagicianGenerator qui le fera)
        """
        nbrMagi = len(listCoordStart)

        #conversion valeur par d�faut -> liste de valeur par d�faut. (bourrin, mais bien)

        if listCoordEnd is None:
            listCoordEnd = (None, ) * nbrMagi

        if magLevelList is None:
            magLevelList = (magLevel, ) * nbrMagi

        if delayValueList is None:
            delayValueList = (delayValue, ) * nbrMagi

        magTypeList = (magType, ) * nbrMagi

        #et hop, on range tout �a dans l'autre sens pour avoir des tuples,
        #contenant chacun toutes les infos n�cessaires � la cr�ation d'un magicien du pattern
        magiParamList = zip(magTypeList, listCoordStart,
                            listCoordEnd, magLevelList)

        #et on re-range un coup pour ajouter le d�lai. (Le d�lai est pas compris dans le tuple
        #d'info, car �a ne concerne pas le magicien en lui-m�me,
        #mais le moment auquel on doit le cr�er)
        genPatternTuple = zip(delayValueList, magiParamList)

        #conversion tuple -> liste
        genPattern = [ list(elem) for elem in genPatternTuple ]

        return genPattern


    def buySthg(self, harMFunds, valueSthgInit, valueSthgStep,
                     costInit, costStep,
                     coefInit = None, coefStep = None):
        """
        buySthg = buySomething. Fonction utilis�e pour acheter
        les �tapes successives d'un truc (n'importe quoi : le nombre de magi,
        la diminution du temps de d�lai, ...)

        entr�es :
            harMFunds : objet HardMana. fonds de mana qui sera utilis� pour
            acheter le truc en question. plus y'a de mana dedans, plus qu'on pourra
            en acheter.
            valueSthgInit : int. valeur initiale du truc en question.
            valueSthgStep : int (pos ou neg). d�calage � appliquer � la valeur
                            � chaque fois qu'on ach�te une �tape du truc.
            costInit      : int. co�t initial, en harM, pour acheter une �tape du truc
            costStep      : int (positif). augmentation du co�t � chaque achat.
                            (c'est rigolo de dire "� chaque achat")

            si les deux params suivants sont None, on ach�te le plus possible
            d'�tapes du truc, jusqu'� ce que y'ait plus assez de harM dans harMFunds
            sinon, c'est un coefficient utilis� pour savoir si on va acheter ou pas
            selon que c'est trop cher ou pas. (voir fonction HardMana.payIfCheap)

            coefInit      : int (positif) coef initial de "pas-trop-cheritude" de l'achat
            coefStep      : int (begatif) diminution appliqu� au coef, � chaque achat.

        plat-dessert :
            int. valeur finale du truc. apr�s les �ventuelles �tapes d'achat.
            Ca vaut : valueSthgInit + X * valueSthgStep. Avec X, nombre d'�tapes achet�es.

            d'autre part, cette fonction modifie la quantit� de mana contenue dans harMFunds
        """

        #initialisations du bazar
        valueSthg = valueSthgInit
        cost = costInit
        coef = coefInit

        #on regarde si on a assez de mana pour acheter, et �ventuellement, on regarde
        #si c'est pas trop cher par rapport au coef indiqu�.
        while harMFunds.payGeneric(cost, coef):

            #et une �tape d'achat. une ! Le mana a d�j� �t� pay�, on modifie la valeur
            #du truc achet�, le co�t, et �ventuellement le coef de pas-trop-cheritude
            valueSthg += valueSthgStep
            cost += costStep

            if coef is not None:
                coef += coefStep

        return valueSthg


    def buyMagicians(self, harMFunds, magiCoefCost):
        """
        fonction utilis�e pour acheter des magiciens, pour un pattern.
        Le premier magi co�te toujours 0. donc on en ach�te syst�matiquement au moins 1.

        On ach�te le plus de magiciens qu'on peut, avec le mana contenu dans harMFunds
        Le prix du magicien augmente de magiCoefCost � chaque nouvel achat.

        entr�es :
            harMFunds :    objet HardMana. fonds de mana utilis� pour l'achat
            magiCoefCost : int. coefficient de co�t d'achat des magiciens.

        plat-dessert :
            int. Nbre de magiciens achet�s.
        """
        nbrMagi = self.buySthg(harMFunds,
                               valueSthgInit = 0, valueSthgStep = +1,
                               costInit = 0, costStep = magiCoefCost)

        bla("nbrMagi : ", nbrMagi)

        #comptage du nombre total de magi g�n�r� pour la wave en cours. (Y'en a besoin � la fin)
        self.nbrTotalMagiGenerated += nbrMagi
        return nbrMagi


    def buyLevelIndividually(self, harMFunds, magLevelList, magiCoefCost):
        """
        ach�te des mont�es de level, pour une liste de magicien.

        entr�es :
            harMFunds :    objet HardMana. fonds de mana utilis� pour le leveling
            magLevelList : liste de int. valeur des levels des magiciens, au d�part.
                           (la taille de la liste donne le nombre de magiciens)
                           En g�n�ral, on part d'une liste avec que des 1. Mais c'est pas oblig�.
            magiCoefCost : int. coefficient de co�t de mont�e de level des magiciens.

        plat-dessert :
            liste de int, de la m�me taille que magLevelList.
            valeur des levels des magiciens, apr�s les montages de levels.

        algorithme :
            voir code. HAHAHA hahaha !! (D�sol�, je m'amusais � parodier le code de merde que je
            fais dans mon boulot de merde). Bon, donc, cet algo :
            on choisit un magicien au hasard, et on calcule son cout de montage de level.
            Si on a assez de mana pour le monter, on le fait tout de suite. (pas de calcul de
            pas-trop-cheritude). Si on peut pas le monter, c'est �chou�. On re-choisit un magicien
            (on n'�limine pas le magicien de la liste, �a veur dire qu'on peut le rechoisir)
            Lorsqu'on a �chou� � un total de trois tentatives, on arr�te le montage de level.
        """
        #nombre de fois qu'on a �chou� � une tentative de montage de niveau.
        nbrFail = 0

        nbrMagi = len(magLevelList)

        while nbrFail < 3:

            #choix d'un magi au hasard, r�cup�ration de son level.
            selectedMagi = randRange(nbrMagi)
            level = magLevelList[selectedMagi]
            #calcul du cout du montage de level pour le magicien choisi.
            cost = level * magiCoefCost

            if harMFunds.payIfEnough(cost):
                #ok, on a pu payer le montage de level. on l'effectue, et on met � jour
                #la liste des levels
                level += 1
                magLevelList[selectedMagi] = level
            else:
                #on n'a pas pu payer le montage de niveau. �a fait un �chouage de plus
                nbrFail += 1

        return magLevelList


    def buyLevelCommonly(self, harMFunds, nbrMagi, magiCoefCost):
        """
        ach�te des mont�es de level de mani�re commune, pour plusieurs magiciens.

        Le 1er montage de niveau est gratuit. youpi !!! (car on a d�j�
        d�pens� du HardMana pour acheter la mise en commun du level up

        On ach�te le plus de level up qu'on peut, avec le mana contenu dans harMFunds
        Le prix du level up augmente de magiCoefCost * nbrMagi � chaque nouvel achat.

        entr�es :
            harMFunds :    objet HardMana. fonds de mana utilis� pour le leveling
            nbrMagi :      nombre de magiciens pour lesquels on doit acheter des levels communs.
            magiCoefCost : int. coefficient de co�t de mont�e de level des magiciens.

        plat-dessert :
            int. level final, � donner � tous les magiciens
        """
        magLevel = self.buySthg(harMFunds,
                                valueSthgInit = 1, valueSthgStep = +1,
                                costInit = 0, costStep = magiCoefCost*nbrMagi)

        bla("magLevel common : ", magLevel)
        return magLevel


    def buyDelayDecrementation(self, harMFunds, nbrMagi):
        """
        ach�te des d�cr�mentation de delay d'apparition entre magicien.
        Le co�t de d�part est �gal au nombre de magiciens, et �a augmente du nombre
        de magiciens � chaque fois.
        Il y'a un coefficient de pas-trop-cheritude. Car les decr de delay, c'est pas
        forc�ment un truc super indispensable. donc faut vraiment avoir du mana � perdre
        por acheter �a.
        Le coef de pas-trop-cheritude baisse � chaque achat.

        entr�es :
            harMFunds :    objet HardMana. fonds de mana utilis� pour le leveling
            nbrMagi :      nombre de magiciens pour lesquels on doit acheter des levels communs.

        plat-dessert :
            int. valeur finale du delay entre magiciens.
        """
        delay = self.buySthg(harMFunds,
                             valueSthgInit = DELAY_MAGI_INIT,
                             valueSthgStep = DELAY_MAGI_DECR,
                             costInit = nbrMagi, costStep = nbrMagi,
                             coefInit = 128, coefStep = -13)

        bla("delay : ", delay)
        return delay


    def buyRayCoefDecrementation(self, harMFunds, nbrMagi):
        """
        ach�te des d�cr�mentation du coef de distance entre le h�ros et les magiciens,
        pour les patterns PAT_CIRCLE et PAT_DIAG.
        Le co�t de d�part est �gal au nombre de magiciens, et �a augmente du nombre
        de magiciens � chaque fois.
        Il y'a un coefficient de pas-trop-cheritude. Car les decr de distance, c'est pas
        forc�ment un truc super indispensable. (mais d�j� un peu plus que les decr
        de delay)
        Le coef de pas-trop-cheritude baisse � chaque achat.

        entr�es :
            harMFunds :    objet HardMana. fonds de mana utilis� pour le leveling
            nbrMagi :      nombre de magiciens pour lesquels on doit acheter des levels communs.

        plat-dessert :
            int. valeur finale du coef de distance entre les magiciens et le h�ros.
        """
        rayCoef = self.buySthg(harMFunds,
                               valueSthgInit = RAY_CIRCLE_INIT,
                               valueSthgStep = RAY_CIRCLE_DECR,
                               costInit = nbrMagi, costStep = nbrMagi,
                               coefInit = 256, coefStep = -26)

        bla("rayCoef : ", rayCoef)
        return rayCoef


    def buyTimeWaveDecrementation(self, harMFunds, timeWaveInit):
        """
        ach�te des d�cr�mentation de timeWave (temps donn� au joueur pour buter tous
        les magis d'une wave.

        On en ach�te le plus qu'on peut avec le harMFunds donn�. Chaque achat diminue
        de 15 cycles le timeWave. Le premier co�te 1, le suivant 2, etc...

        entr�es :
            harMFunds    : objet HardMana. fonds de mana utilis� pour le leveling
            timeWaveInit : int. valeur initiale du timeWave

        plat-dessert :
            int. valeur finale du timeWave, apr�s d�cr�mentations.
        """
        timeWave = self.buySthg(harMFunds,
                                valueSthgInit = timeWaveInit,
                                valueSthgStep = -15,
                                costInit = 1, costStep = 1)

        return timeWave


    def magiCoefCostConfFromMagiCoefCostBuy(self, magiCoefCost):
        """
        conversion entre le magiCoefCost d'achat des magiciens, et le
        magiCoefCost de configuration des magiciens (utilis�s pour le montage de level,
        et d'autres trucs).

        entr�es :
            magiCoefCost : int. coefficient de co�t d'achat des magiciens.

        plat-dessert :
            int. coefficient de co�t de config des magiciens.
        """

        #conversion compl�tement � l'arrache. Je sais pas du tout si c'est �quilibr� ou pas,
        #en terme de jeu, gameplay, tout �a.

        magiCoefCost -= MAGI_COEF_COST_DECAL_NBR_CONF

        if magiCoefCost < 1:
            magiCoefCost = 1

        return magiCoefCost


    def elaborateNextWave(self):
        """
        Putain de grosse fonction qui g�n�re tous les patterns de magiciens d'une wave.

        entr�es : rin.

        plat-dessert :
            tuple de 2 �l�ments :
             - int. temps (nbre de cycle) avant la cr�ation de la prochaine wave.
             - liste de patterns : les patterns � cr�er. Avec les temps de d�lai et les infos
               de chaque magiciens. (voir le truc que renvoie la fonction mergeGenPatInfo)
        """

        # --- RECUPERATION ET REPARTITION DU HARD-MANA ---

        #rechargement du mana pour cette wave. prise en compte de l'antiHarM si y'en a.
        self.addHarMForNextWave()
        bla("  harmTotal for this wave :",str(self.harMTotal))

        #listes total des patterns qui seront g�n�r�s pour cette wave
        self.listOfGenPattern = []
        #nombre total de magiciens g�n�r�s pour cette wave.
        self.nbrTotalMagiGenerated = 0

        #r�partition du harM pour le pattern principal (harMRand), et les patterns sup (harMPat)
        #la tendance est de donner un peu plus au pattern principal
        (harMRand, harMPat) = self.harMTotal.dispatch(50, 100)

        #on prend le harM le plus grand parmi les deux, et on en retire un petit peu
        #pour avoir le harM de time wave (celui qui sera utilis� pour diminuer le timeWave
        #de cette wave. blablabla)
        if harMRand.getV() > harMPat.getV():
            (harMRand, harMTimeWave) = harMRand.dispatch(110, 128)
        else:
            (harMPat, harMTimeWave) = harMPat.dispatch(110, 128)

        bla("self.harMTotal", self.harMTotal, "harMRand ",harMRand,
            "harMPat ", harMPat, "harMTimeWave", harMTimeWave)

        # --- PATTERN PRINCIPAL "RAND" ---

        #   - CHOIX DU TYPE DE PATTERN, REPARTITION DU HARM, ACHAT DES MAGIS -

        #r�partition du harM entre celui utilis� pour acheter les magi (harMRandNbr),
        #et celui utilis� pour configurer les magiciens achet�s (harMRandConf)
        #on donne plus de harM � l'achat qu'� la conf
        (harMRandNbr, harMRandConf) = harMRand.dispatch(50, 100)
        bla("harMRandNbr : ", harMRandNbr, "harMRandConf : ", harMRandConf)

        #choix du type de pattern pour le pattern principal. En g�n�ral, on
        #prend le pattern de type rand (magicien cr�� n'importe o� au hasard)
        #mais y'a une petite probabilit� qu'on en prenne un autre, moyennant mana (lol consonance)
        patRand = harMRandNbr.chooseAndPay(LIST_PATTERN_CHOICE_GEN_RAND)[0]
        bla("harMRandNbr : ", harMRandNbr, "pattern : ", patRand)

        #les magiciens du pattern principal sont de type MAGI_RAND. Y'a pas le choix.
        #donc le magiCoefCost se d�termine tout de suite
        magiCoefCost = MAGI_RAND_COEF_COST

        #achat des magiciens du pattern principal.
        nbrMagi = self.buyMagicians(harMRandNbr, magiCoefCost)
        bla("bought magi. harMRandNbr : ", harMRandNbr)

        #on re-verse le harM restant (harMRandNbr) dans harMRandConf
        harMRandConf.grabAll(harMRandNbr)
        bla("harMRandNbr : ", harMRandNbr, "harMRandConf : ", harMRandConf)

        #   - CONFIGURATION DU PATTERN -

        #Comme on va faire de la config de pattern,
        #on passe du magiCoefCost d'achat de magi au magiCoefCost de config de magi
        magiCoefCost = self.magiCoefCostConfFromMagiCoefCostBuy(magiCoefCost)

        #achat de diminution du d�lay d'apparition des magiciens du pattern
        delayMagiRand = self.buyDelayDecrementation(harMRandConf, nbrMagi)
        bla("harMRandConf : ", harMRandConf)

        #init des level des magiciens, et achat de leur mont�e de level.
        #(dans le pattern principal, les level up sont individuels, y'a pas le choix
        magLevelList = [1, ] * nbrMagi
        param = (harMRandConf, magLevelList, magiCoefCost)
        magLevelList = self.buyLevelIndividually(*param)
        bla("magLevelList : ", magLevelList)
        bla("harMRandConf : ", harMRandConf)

        #construction des coordonn�es de d�part des magiciens, pour ce pattern.
        #les coordonn�es de fin, en fait ce sera toujours None, car on a
        #forc�ment des MAGI_RAND dans le pattern principal
        listCoordStart, listCoordEnd = self.funcGenPat(patRand, nbrMagi)

        #hop, on colle tout ce bordel ensemble, et �a nous fait un joli pattern principal !
        param = (MAGI_RAND, listCoordStart, None,
                 1, magLevelList, delayMagiRand)
        genPatternRand = self.mergeGenPatInfo(*param)

        #ajout du pattern principal dans la liste des patterns de cette wave
        self.listOfGenPattern.append(genPatternRand)

        #on re-verse le harM restant (harMRandConf) dans le harM des patterns sup. (harMPat)
        harMPat.grabAll(harMRandConf)

        bla("# --- AUTRES PATTERNS ---        ")
        # --- PATTERNS SUPPLEMENTAIRES. "PAT" ---

        #   - ACHAT DES PATTERNS SUP, ALLOCATION DE HARM A CHACUN -

        #r�partition du harM entre le harM pour acheter les patterns eux-m�mes (harMPatChoice),
        #et le harM pour acheter les magiciens et la config de tous les patters sup (harMPatMain)
        harMPatChoice, harMPatMain = harMPat.dispatch(32, 76)
        bla("harMPatChoice : ", harMPatChoice, "harMPatMain : ", harMPatMain)

        listPatChosen = []

        #on prend le gros tuple de d�part, listant les patterns sup avec leur co�t et
        #coef de proba, et on le clone en une liste, qu'on pourra modifier.
        currentListPatternChoice = [ list(elem) for elem
                                     in LIST_PATTERN_CHOICE_GEN_PAT ]

        #choix et achat d'un pattern parmi la liste disponible.
        #les patterns trop chers sont pr�alablement �limin�. et le pattern choisi
        #est apr�s-alablement �limin� aussi, pour pas prendre 2 fois le m�me.
        #si pas assez de harM pour choisir un pattern, on passera tout de suite
        #� la suite, et il n'y aura aucun pattern sup.
        patChosenInfo = harMPatChoice.chooseAndPay(currentListPatternChoice)

        while patChosenInfo is not None:

            # R�cup�ration des infos li�es au pattern choisi
            # (patChosenInfo = tuple de 2 �l�ments : magiCoefCost, patternId)
            # et de la liste de pattern sup restante, apr�s toutes les �liminations.
            patChosen, remainingList = patChosenInfo
            listPatChosen.append(patChosen)
            currentListPatternChoice = remainingList

            #augmentation du prix d'achat de tous les patterns restants.
            #(plus on ach�te de patterns, plus ils co�tent cher)
            for elem in currentListPatternChoice:
                elem[1] += COST_PATTERN_SUP_INCR

            #re-choisissage d'un nouveau pattern sup, ou pas si on n'a plus assez
            #de harM et qu'ils sont tous devenus trop chers.
            # Convention code fail :
            # Virage des espaces avant et apr�s le egal car ligne trop longue. (beurk)
            patChosenInfo=harMPatChoice.chooseAndPay(currentListPatternChoice)


        #on re-verse le harM restant (harMPatChoice) dans le harM qui va �tre utilis�
        #pour acheter les magiciens et faire la config des patterns sup. (harMPatMain)
        harMPatMain.grabAll(harMPatChoice)

        nbrPatChosen = len(listPatChosen)

        if nbrPatChosen > 0:

            #r�partition des harM pour chaque pattern sup. (De mani�re presque �quitable,
            #y'a juste le reste de la division qu'on claque dans le premier)
            #�a devrait se r��quilibrer par la suite, car � chaque fois, on re-verse
            #le harM du pattern sup pr�c�dent dans le pattern courant. Et de toutes fa�ons osef.
            listHarMPatMain = harMPatMain.divide(nbrPatChosen)

            #rassemblage de toutes les infos de chaque pattern sup.
            listPatWithHarM = zip(listPatChosen, listHarMPatMain)
            bla("liste des patterns avec les infos : ", listPatWithHarM)

            #�a c'est le HarMana pour faire le transfert du pat pr�c�dent au pat courant.
            harMRemainingPrecedentPat = HardMana()

            # --- ACHAT DSE MAGICIENS ET CONFIGURATION DE CHAQUE PATTERN SUP ---

            for patWithHarM in listPatWithHarM:

                #c'est un peu foutu en bordel, avec tout ce qu'on a fait avant.
                #donc je r�cup�re mes donn�es de mani�re un peu plus explicite
                magiCoefCost = patWithHarM[0][0]
                patternId = patWithHarM[0][1]
                harMCurrent = patWithHarM[1]

                param = (patternId, magiCoefCost,
                         harMCurrent, harMRemainingPrecedentPat)

                self.elaboratePatternSup(*param)

            #re-versage du harM du pattern prec dans le pattern courant
            harMPatMain.grabAll(harMRemainingPrecedentPat)

        #et finalement, on re-verse le harM restant � la fin dans la
        #grosse r�serve globale de harM. Ce sera utilis� pour la prochaine wave.
        #(on re-verse pas dans le harM utilis� pour diminuer le timeWave, parce
        #que �a aurait pas trop d'int�r�t. Faut pas claquer tout son harM dans
        #la diminution du temps.
        self.harMTotal.grabAll(harMPatMain)

        # --- CALCUL DE TIMEWAVE, ET DIMINUTION AVEC HARTIMEWAVE ---
        bla("   -------- diminution temps avec harMTimeWave  -----------")

        #calcul de la difficult� de la wave, et conversion pour avoir le timeWave.
        #(tout �a c'est calcul� � l'arrache. J'ai essay� de r�fl�chir � des formules et des
        #dosages pour que ce soit vaguement �quilibr�, mais je garantis rien.)
        #c'est marrant de dire "formules" et "dosages", �a fait alchimiste.
        waveDifficulty = self.nbrTotalMagiGenerated + self.indexCurrentWave
        timeWave = TIME_WAVE_BASE + waveDifficulty * TIME_WAVE_COEF_DIFFICULTY
        bla("timeWave : ", timeWave)

        #diminution du timeWave en d�pensant le harM de harMTimeWave
        timeWave = self.buyTimeWaveDecrementation(harMTimeWave, timeWave)
        bla("timeWave : ", timeWave)

        #youpiiii !!!
        if timeWave < 10:
            timeWave = 10

        #on re-verse le harM restant de harMTimeWave dans le gros harM global,
        #pour la prochaine wave
        self.harMTotal.grabAll(harMTimeWave)

        #augmentation du nombre total de wave g�n�r�
        self.indexCurrentWave += 1

        bla("harmTotal left after the wave : ", self.harMTotal)
        bla("------------- end of wave generation -------------")
        for _ in xrange(5): bla("")

        return timeWave, self.listOfGenPattern


    def elaboratePatternSup(self, patternId, magiCoefCost,
                            harMCurrent, harMRemainingPrecedentPat):
        """
        putain de grosse fonction  qui cr�e et configure un pattern sup.

        entr�es :
            patternId     : identifiant du type de pattern � g�n�rer
            magiCoefCost  : int. coef de co�t d'achat des magiciens de ce pattern
            harMCurrent   : objet HardMana. harM allou� pour ce pattern.
            harMRemainingPrecedentPat : objet HardMana. harM restant du pattern sup
               pr�c�dent. (A r�cup�rer, et � re-verser � la fin de l'�laboration)

        la fonction ajoute directement le pattern sup dans l'attribut listOfGenPattern
        """
        bla("   ***  pattern : ", patternId, "   ***")

        #on r�cup�re tout le harM du pattern sup pr�c�dent. (0 si c'est le 1er pattern sup)
        harMCurrent.grabAll(harMRemainingPrecedentPat)

        #d�cision si on fait des magiciens de type MAGI_RAND ou MAGI_LINE.
        #(y'a plus de chance de faire des MAGI_LINE)
        if randRange(128) < 16:
            magiType = MAGI_RAND
            #si on fait du MAGI_RAND, faut prendre le magiCoefCost qui correspond
            #(plus haut que les autres magiCoefCost, car un MAGI_RAND, c'est plus dur � buter)
            magiCoefCost = MAGI_RAND_COEF_COST
            #on n'aura pas besoin de la coordonn�e de fin, avec des MAGI_RAND.
            coordEnd = None
            bla("randomized magi !")
        else:
            magiType = MAGI_LINE
            #on garde le m�me magiCoefCost, et on dit que y'aura besoin de la coordEnd
            coordEnd = True

        #r�partition du harM entre l'achat des magiciens (harMCurNbr), et le reste (harMCurConf)
        (harMCurNbr, harMCurConf) = harMCurrent.dispatch(16, 96)
        bla("harMCurNbr : ", harMCurNbr, "harMCurConf : ", harMCurConf)

        #achat des magiciens du pattern. Hopla.
        nbrMagi = self.buyMagicians(harMCurNbr, magiCoefCost)

        #on re-verse le harM restant qui a servi � acheter les magiciens,
        #dans le harM utilis� pour tous le reste.
        harMCurConf.grabAll(harMCurNbr)
        bla("harMCurNbr : ", harMCurNbr, "harMCurConf : ", harMCurConf)

        #maintenant, on va faire de la config de pattern.
        #Donc on passe du magiCoefCost d'achat de magi au magiCoefCost de config de magi
        magiCoefCost = self.magiCoefCostConfFromMagiCoefCostBuy(magiCoefCost)

        #�ventuellement, achat de r�duction du coefficient de la distance entre le joueur
        #et les magiciens du pattern. (si le type de pattern s'y pr�te.)
        if patternId in (PAT_CIRCLE, PAT_DIAG):
            rayCoef = self.buyRayCoefDecrementation(harMCurConf, nbrMagi)
        else:
            rayCoef = None  #osef de ce param

        #d�cision de si on fait appara�tre tous les magiciens d'un seul coup,
        #(�a coute un peu de harM), ou si ils apparaissent un par un. (�a coute rien)
        #dans les deux cas, faudra quand m�me acheter les diminutions de d�lai, mais
        #on verra plus tard.
        costAppCommon = nbrMagi * magiCoefCost
        coefAppCommon = 100  #TRODO : je sais pas bien �quilibrer ce truc. is it la bonne m�thode?

        if harMCurConf.payIfCheap(costAppCommon, coefAppCommon):
            apparitionInCommon = True
            bla("apparition common !!")
        else:
            apparitionInCommon = False

        #achat de r�duction du d�lai d'apparition des magiciens.
        delayMagiRand = self.buyDelayDecrementation(harMCurConf, nbrMagi)

        #si ils n'apparaissent pas en m�me temps, le delay est plac� entre chaque
        #magicien, comme d'hab'.
        #si ils apparaissent en m�me temps, ils ont tous le m�me d�lai,
        #�gal � : <d�lai de d�part> * <nbrMagi> / 2. captain obvious c'est dit juste apr�s.

        if apparitionInCommon:

            #calcul du delay commun pour tous les magiciens.
            delayCommon = (delayMagiRand * nbrMagi) / 2

            #dans la delayList, les delay sont cumulatifs. Donc pour un d�lai commun,
            #on doit mettre le total de delay sur le premier magi, et tous les autres auront 0.

            #construction d'une liste avec le delayCommon en premier �l�ment, puis que des 0
            delayList = (delayCommon, ) + (0, ) * (nbrMagi - 1)

            delayMagiRand = None  #osef

        else:

            delayList = None  #osef

        bla("harMCurConf : ", harMCurConf)

        #d�cision de si on fait des mont�e de level commun, ou pas.
        #(le level up commun coute des sous. L'individuel ne co�te rien)
        costLvlUpCommon = nbrMagi * magiCoefCost
        coefLvlUpCommon = 512

        if harMCurConf.payIfCheap(costAppCommon, coefAppCommon):
            lvlUpInCommon = True
            bla("lvl up common !!")
        else:
            lvlUpInCommon = False

        if lvlUpInCommon:

            #achat des level up pour tous les magiciens.
            param = (harMCurConf, nbrMagi, magiCoefCost)
            magLevel = self.buyLevelCommonly(*param)
            magLevelList = None  #osef
            bla("magLevel : ", magLevel)

        else:

            #initialisation des level de d�part des magiciens. (tous au niveau 1)
            magLevelList = [1, ] * nbrMagi

            #achat des level up individuel.
            param = (harMCurConf, magLevelList, magiCoefCost)
            magLevelList = self.buyLevelIndividually(*param)
            magLevel = None  #osef
            bla("magLevelList : ", magLevelList)

        #construction des coordonn�es de d�part (et �ventuellement les coordonn�es de fin),
        #des magiciens du pattern.
        param = (patternId, nbrMagi, coordEnd, rayCoef)
        listCoordStart, listCoordEnd = self.funcGenPat(*param)

        #rassemblage de toutes les infos n�cessaires � la cr�ation du pattern,
        #et ajout dans listOfGenPattern

        param = (magiType, listCoordStart, listCoordEnd,
                 magLevel, magLevelList,
                 delayMagiRand, delayList)

        genPatternRand = self.mergeGenPatInfo(*param)

        self.listOfGenPattern.append(genPatternRand)

        bla("harMCurNbr : ", harMCurNbr, "harMCurConf : ", harMCurConf)

        #on re-verse le harM restant dans harMRemainingPrecedentPat, qui sera redonn� au
        #prochain pattern suppl�mentaire. (ou � la r�serve globale de harM si c'�tait
        #le dernier pattern sup).
        harMRemainingPrecedentPat.grabAll(harMCurConf)

