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

date de la dernière relecture-commentage : 22/09/2010

classe qui élabore les patterns pour faire une wave de magiciens, en fonction
du HardMana qu'il possède.

vocabulaire :

wave : une "vague" de magicien. C'est à dire un ensemble de magiciens, qui arrivent
tous plus ou moins en même temps. Le joueur dispose d'un temps limité pour
tous les dégommer. Passé ce temps, la wave suivante est "élaborée". une wave
est un ensemble de pattern.
(élaborer = générer, mais je trouve ça plus chouette "élaborer")

pattern : suite de magiciens à générer. pour chaque magicien, on associe les infos
nécessaires à sa création (position, level, ...) et une valeur de "delay".
car tous les magiciens d'un pattern n'apparaissent pas tous d'un coup.
le delay est cumulatif. Ex : le premier magicien a un delay de 7, le suivant
a un delay de 10. Le premier apparaîtra dans 7 cycles, le suivant dans 17 cycles.
On peut faire apparaître plusieurs magiciens d'un coup en leur mettant des delay de 0

dans les infos du pattern, on trouve les coordonnées de départ des magiciens. Et eventuellement
les coordonnées de fin. Elles ne sont utiles que pour les magiciens de type MAGI_LINE.
Elles définissent là où ils doivent se rendre.
(les MAGI_RAND bougent au hasard, et n'ont donc pas de coord de fin)

HardMana (HarM) : valeur numérique. "Mana de difficulté". Le waveGenerator dépenses ce mana
pour acheter des patterns, les améliorer, etc...
Entre deux waves, on redonne du HardMana au waveGenerator. Et on lui en redonne de plus
en plus.
Mais il faut racheter les patterns et les améliorations de pattern entre chaque wave.

le waveGenerator dépense le plus possible du HardMana qu'il possède à chaque wave.
Le petit reste qu'il n'a pas pu dépenser est reporté à la wave suivante.
Ceci est également valable à l'intérieur d'une wave. C'est à dire que quand le waveGen doit
acheter un certain truc, et qu'il ne dépense pas tout le HarM alloué pour cela,
alors le reste est reporté pour le prochain truc qu'il doit acheter.

Le HardMana est une classe à part entière. Car on a parfois besoin de le répartir en
plusieurs petits bouts, de décider si on achète un truc ou pas en fonction du Mana qu'on a, ...
HardMana = harM : c'est la même chose mais en abrégé

anti-HardMana (AntiHarM) : C'est du mana inversé. Du "mana de facilité". Si le joueur termine
une wave en moins de temps que le temps prévu, il gagne de l'AntiHarM.
l'AntiHarM est dépensé tout de suite, pour diminuer la quantité de HarM allouée à la prochaine
élaboration de wave. 1 HarM et 1 AntiHarM s'annulent.

a chaque wave, le waveGenerator fabrique deux sortes de patterns
 - 1 pattern principal : toujours constitué de magiciens de type Rand (ils se déplacent au hasard)
 - 0, 1 ou plusieurs patterns supplémentaires. des magiciens Rand ou des magiciens Line.
TRODO : nommage un peu pourri. Dans le code, j'appelle le pattern principal PatRand,
et les patterns sup euh... Pat. Tout connement. C'est moche.

magiCoefCost : coefficient de coût pour l'achat ou l'amélioration d'un magicien. Ce coef varie
en fonction du type du magicien, et du pattern dans lequel on le place. pour les magi random,
il est très haut. Car un magicien qui bouge au hasard est bien plus dangereux qu'un magicien
qui bouge dans une simple ligne droite.
Le magiCoefCost est utilisé pour :
 - acheter les magiciens d'un pattern
 - augmenter le level des magiciens d'un pattern
 - ... (ouais, c'est facile, de mettre des point-point-point. Eh bien fuck)
"""

from common import (randRange, SHIFT_PREC, NOT_FLOATING_PREC)

#moi j'importe des tonnes de trucs en les spécifiant un par un. Et c'est le bien de faire ça !!
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

#liste des différents types de magicien
(MAGI_BASE, #le magicien de base qui bouge pas. (en fait on en génère jamais des comme ça)
 MAGI_RAND, #le magicien random, qui bouge n'importe comment
 MAGI_LINE, #le magicien line, qui bouge en ligne droite, puis s'arrête.
) = range(3)

#HardMana alloué au départ, pour créer la première wave. (Oui, zero, oui)
HARM_FUNDS_INIT = 0

#delay (nbre de cycle) initiale entre la génération de deux magiciens d'un même pattern.
#le tout premier magicien d'un pattern n'est pas créé dès le départ. Il est créé au bout
#du temps de delay, le suivant : 2 fois le temps, etc.
#(un peu zarb' que le tout premei soit pas créé dès le départ, mais je trouve ça cool)
DELAY_MAGI_INIT = 40
#temps de diminution du délai, lorsque le waveGenerator décide d'acheter une diminution de delay,
#en payant du HardMana. (Chaque diminution coute plus cher que la précédente)
DELAY_MAGI_DECR = -5

#pour les patterns PAT_CIRCLE et PAT_DIAG : coefficient initial de la distance
#entre les magiciens et le joueur. (Utilisation de nombre à virgule pas-flottante)
#en fait, là ça représente un coefficient de 1.0
RAY_CIRCLE_INIT = NOT_FLOATING_PREC
#valeur de diminution du coef, à chaque fois que le waveGenerator décide d'acheter une
#diminution de coef. (en payant du HardMana, blablabla)
RAY_CIRCLE_DECR = -12

#quantité de HarM alloué en plus à chaque nouvelle wave. C'est une valeur d'"accélération".
#à la 1ere wave on a 0. La 2eme : 20. La troisième 20*2, etc...
HARM_INCREMENTATION_OF_INCREMENTATION_PER_WAVE = 20

#magiCoefCost pour les magiciens de type MAGI_RAND.
#(pour les magiciens MAGI_LINE, le coefCost dépend du pattern utilisé pour le générer)
MAGI_RAND_COEF_COST = 10

#liste de tuple, pour choisir le pattern principal (RAND, oui nommage fail, oui)
#chaque tuple contient 3 éléments :
#  - probabilité de sélection (parmi toutes les probas de sélection
#    de tous les patterns dispos, et abordable)
#  - coût, en HardMana
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

#liste de tuple, pour choisir les pattern supplémentaires (PAT, oui nommage fail, oui)
#chaque tuple contient 3 éléments :
#  - probabilité de sélection (parmi toutes les probas de sélection
#    de tous les patterns dispos, et abordable)
#  - coût initail, en HardMana (plus on achète de pattern sup, plus les suivants sont chers)
#  - sous-tuple de 2 elem, avec :
#     *  magiCoefCost des magiciens de type MAGI_LINE générés dans ce pattern.
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

#augmentation appliquée au coût de tous les patterns sup, à chaque fois qu'on en achète un
COST_PATTERN_SUP_INCR = 20

#décalage à appliquer entre le magiCoefCost pour acheter un magicien, et le magiCoefCost pour
#configurer un magicien (diminuer son délai, augmenter son niveau, ...)
MAGI_COEF_COST_DECAL_NBR_CONF = 2

#temps "de baaaaase" donné au joueur pour tuer tous les magiciens d'une wave
TIME_WAVE_BASE = 350
#coefficientde conversion entre la difficulté d'une wave et le temps donné en plus
#(voir plus loin pour le calcul de la difficulté d'une wave, je me suis pas trop pris la tête)
TIME_WAVE_COEF_DIFFICULTY = 10


def bla(*msg):
    """
    fonction à la con pour faire du debug
    """
    pass
    #ligne a commenter si on veut pas de debug.
    #et moi je suis pas un gros boulet ! Je fous pas un booléen de merde DEBUG_ACTIVATED,
    #que personne n'utilise, et que ça va faire tout ralentir.
    #là, quand y'a que l'instruction "pass" dans la fonction, on peut penser que le python
    #se démerde pour l'optimiser, ou je sais pas quoi. bordel.
    #Ho et pis osef. De toutse façson je la virerais complètement à la fin. alors.
    ##print msg


class MagicianWaveGenerator():
    """
    classe qui gère la création des vagues de magiciens. déjà dit, oui.
    """

    def __init__(self, hero):
        """
        constructeur. (thx captain obvious)

        entrée :
            hero : référence vers le héros. C'est juste pour pouvoir choper ses coordonnées,
                   pour quand on crée des pattern PAT_CIRCLE ou PAT_DIAG.
        """

        #sous classe qui fabrique réellement les patterns,
        #en fonctions des infos de config qu'on lui donne
        self.magicianListCoordBuilder = MagicianListCoordBuilder(hero)

        #valeur courante de harM, qui va servir à acheter tout le bazar.
        self.harMTotal = HardMana(HARM_FUNDS_INIT)
        #quantité de harM alloué à chaque nouvelle wave
        self.incrForHarM = 0
        #pas de AntiHarM au départ.
        self.antiHarM = HardMana()
        #juste un compteur de wave à la con.
        self.indexCurrentWave = 0

        #alias à la con pour un nom plus court
        self.funcGenPat = self.magicianListCoordBuilder.generatePattern


    def receiveAntiHarMBonus(self, antiHarMBonus):
        """
        fonction à exécuter par des "stimulis extérieurs". Pour ajouter du AntiHarM,
        lorsque le joueur a réussi à faire des trucs skillé
        (genre buter tous les magi super rapidement, et genre c'est tout parce que c'est
        le seul moyen de choper de l'antiHarM)

        entrée :
            antiHarMBonus : int. quantité de antiHarM à rajouter.
        """
        self.antiHarM.addHarM(antiHarMBonus)
        bla("recevied antiHarM : ", antiHarMBonus, "  total : ", self.antiHarM)


    def addHarMForNextWave(self):
        """
        mise à jour de TotalHarM, et de incrForHarM, du fait qu'il faut générer une nouvelle wave.
        Ah c'est marrant de dire "du fait de". Faudrait que je le fasse plus souvent
        """
        bla("-------- more harM for newt wave --------")
        bla("harMTotal avant magouillerie : " + str(self.harMTotal))
        bla("antiHarm : " + str(self.antiHarM))

        #augmentation de harMTotal et incrForHarM
        self.harMTotal.addHarM(self.incrForHarM)
        self.incrForHarM += HARM_INCREMENTATION_OF_INCREMENTATION_PER_WAVE

        #décrémentation du harM si on s'est pris de l'antiHarM
        self.harMTotal.antiHarMDebuff(self.antiHarM)


    def mergeGenPatInfo(self, magType,
                        listCoordStart, listCoordEnd=None,
                        magLevel=1, magLevelList=None,
                        delayValue=DELAY_MAGI_INIT, delayValueList=None):
        """
        wouhouuu, fonction qui rassemble un tas de trucs venant de n'importe où,
        pour fabriquer toutes les infos nécessaires à la création d'un pattern

        entrées :
            magType        : type des magiciens à générer dans le pattern (RAND, LINE, ...)
            listCoordStart : liste de Rect. coordonnées de départ des magiciens
            listCoordEnd   : liste de Rect. coordonnées de fin. utiles uniquement pour
                             les MAGI_LINE. Sinon, on peut mettre None.
            magLevel       : int. valeur de level de tous les magiciens du pattern.
                             (paramètre non utilisé si magLevelList is not None)
            magLevelList   : liste de int. valeur de level de chacun des magiciens du pattern
            delayValue     : int. délai d'attente (en nbre de cycle) entre la création de deux
                             magiciens du pattern.
                             (paramètre non utilisé si delayValueList is not None)
            delayValueList : liste de int. délai d'attente de chacun des magiciens du pattern

            listCoordStart doit être obligatoirement défini (pas de valeur None)
            la longueur de cette liste donne le nombre de magiciens à créer dans le pattern.

            listCoordEnd, magLevelList et delayValueList peuvent être non définie. (fixée à None)
            Lorsqu'elles sont définies, ces 4 listes doivent toutes avoir le même nombre
            d'élément. Sinon ça pète.

        plat-dessert :
            genPattern : une liste. chaque élément représente un magicien à créer,
            ils sont constitués d'une sous-liste de 2 éléments.
             - temps de délai avant génération de ce magicien, (et passage au magi suivant)
             - infos concernant le magicien. C'est un sous-sous-tuple de 4 élément :
                * type du magicien (LINE, RAND, ...)
                * rect. coordonnée de départ
                * rect ou None. coordonnée d'arrivée. (utile pour MAGI_LINE)
                * int. level.

            les deux premiers niveaux d'information doivent obligatoirement être une liste
            et une sous-liste (pas de tuple, sous-tuple). Car plus tard, on va avoir besoin
            de tripoter les données que y'a dedans. (C'est le MagicianGenerator qui le fera)
        """
        nbrMagi = len(listCoordStart)

        #conversion valeur par défaut -> liste de valeur par défaut. (bourrin, mais bien)

        if listCoordEnd is None:
            listCoordEnd = (None, ) * nbrMagi

        if magLevelList is None:
            magLevelList = (magLevel, ) * nbrMagi

        if delayValueList is None:
            delayValueList = (delayValue, ) * nbrMagi

        magTypeList = (magType, ) * nbrMagi

        #et hop, on range tout ça dans l'autre sens pour avoir des tuples,
        #contenant chacun toutes les infos nécessaires à la création d'un magicien du pattern
        magiParamList = zip(magTypeList, listCoordStart,
                            listCoordEnd, magLevelList)

        #et on re-range un coup pour ajouter le délai. (Le délai est pas compris dans le tuple
        #d'info, car ça ne concerne pas le magicien en lui-même,
        #mais le moment auquel on doit le créer)
        genPatternTuple = zip(delayValueList, magiParamList)

        #conversion tuple -> liste
        genPattern = [ list(elem) for elem in genPatternTuple ]

        return genPattern


    def buySthg(self, harMFunds, valueSthgInit, valueSthgStep,
                     costInit, costStep,
                     coefInit = None, coefStep = None):
        """
        buySthg = buySomething. Fonction utilisée pour acheter
        les étapes successives d'un truc (n'importe quoi : le nombre de magi,
        la diminution du temps de délai, ...)

        entrées :
            harMFunds : objet HardMana. fonds de mana qui sera utilisé pour
            acheter le truc en question. plus y'a de mana dedans, plus qu'on pourra
            en acheter.
            valueSthgInit : int. valeur initiale du truc en question.
            valueSthgStep : int (pos ou neg). décalage à appliquer à la valeur
                            à chaque fois qu'on achète une étape du truc.
            costInit      : int. coût initial, en harM, pour acheter une étape du truc
            costStep      : int (positif). augmentation du coût à chaque achat.
                            (c'est rigolo de dire "à chaque achat")

            si les deux params suivants sont None, on achète le plus possible
            d'étapes du truc, jusqu'à ce que y'ait plus assez de harM dans harMFunds
            sinon, c'est un coefficient utilisé pour savoir si on va acheter ou pas
            selon que c'est trop cher ou pas. (voir fonction HardMana.payIfCheap)

            coefInit      : int (positif) coef initial de "pas-trop-cheritude" de l'achat
            coefStep      : int (begatif) diminution appliqué au coef, à chaque achat.

        plat-dessert :
            int. valeur finale du truc. après les éventuelles étapes d'achat.
            Ca vaut : valueSthgInit + X * valueSthgStep. Avec X, nombre d'étapes achetées.

            d'autre part, cette fonction modifie la quantité de mana contenue dans harMFunds
        """

        #initialisations du bazar
        valueSthg = valueSthgInit
        cost = costInit
        coef = coefInit

        #on regarde si on a assez de mana pour acheter, et éventuellement, on regarde
        #si c'est pas trop cher par rapport au coef indiqué.
        while harMFunds.payGeneric(cost, coef):

            #et une étape d'achat. une ! Le mana a déjà été payé, on modifie la valeur
            #du truc acheté, le coût, et éventuellement le coef de pas-trop-cheritude
            valueSthg += valueSthgStep
            cost += costStep

            if coef is not None:
                coef += coefStep

        return valueSthg


    def buyMagicians(self, harMFunds, magiCoefCost):
        """
        fonction utilisée pour acheter des magiciens, pour un pattern.
        Le premier magi coûte toujours 0. donc on en achète systématiquement au moins 1.

        On achète le plus de magiciens qu'on peut, avec le mana contenu dans harMFunds
        Le prix du magicien augmente de magiCoefCost à chaque nouvel achat.

        entrées :
            harMFunds :    objet HardMana. fonds de mana utilisé pour l'achat
            magiCoefCost : int. coefficient de coût d'achat des magiciens.

        plat-dessert :
            int. Nbre de magiciens achetés.
        """
        nbrMagi = self.buySthg(harMFunds,
                               valueSthgInit = 0, valueSthgStep = +1,
                               costInit = 0, costStep = magiCoefCost)

        bla("nbrMagi : ", nbrMagi)

        #comptage du nombre total de magi généré pour la wave en cours. (Y'en a besoin à la fin)
        self.nbrTotalMagiGenerated += nbrMagi
        return nbrMagi


    def buyLevelIndividually(self, harMFunds, magLevelList, magiCoefCost):
        """
        achète des montées de level, pour une liste de magicien.

        entrées :
            harMFunds :    objet HardMana. fonds de mana utilisé pour le leveling
            magLevelList : liste de int. valeur des levels des magiciens, au départ.
                           (la taille de la liste donne le nombre de magiciens)
                           En général, on part d'une liste avec que des 1. Mais c'est pas obligé.
            magiCoefCost : int. coefficient de coût de montée de level des magiciens.

        plat-dessert :
            liste de int, de la même taille que magLevelList.
            valeur des levels des magiciens, après les montages de levels.

        algorithme :
            voir code. HAHAHA hahaha !! (Désolé, je m'amusais à parodier le code de merde que je
            fais dans mon boulot de merde). Bon, donc, cet algo :
            on choisit un magicien au hasard, et on calcule son cout de montage de level.
            Si on a assez de mana pour le monter, on le fait tout de suite. (pas de calcul de
            pas-trop-cheritude). Si on peut pas le monter, c'est échoué. On re-choisit un magicien
            (on n'élimine pas le magicien de la liste, ça veur dire qu'on peut le rechoisir)
            Lorsqu'on a échoué à un total de trois tentatives, on arrête le montage de level.
        """
        #nombre de fois qu'on a échoué à une tentative de montage de niveau.
        nbrFail = 0

        nbrMagi = len(magLevelList)

        while nbrFail < 3:

            #choix d'un magi au hasard, récupération de son level.
            selectedMagi = randRange(nbrMagi)
            level = magLevelList[selectedMagi]
            #calcul du cout du montage de level pour le magicien choisi.
            cost = level * magiCoefCost

            if harMFunds.payIfEnough(cost):
                #ok, on a pu payer le montage de level. on l'effectue, et on met à jour
                #la liste des levels
                level += 1
                magLevelList[selectedMagi] = level
            else:
                #on n'a pas pu payer le montage de niveau. ça fait un échouage de plus
                nbrFail += 1

        return magLevelList


    def buyLevelCommonly(self, harMFunds, nbrMagi, magiCoefCost):
        """
        achète des montées de level de manière commune, pour plusieurs magiciens.

        Le 1er montage de niveau est gratuit. youpi !!! (car on a déjà
        dépensé du HardMana pour acheter la mise en commun du level up

        On achète le plus de level up qu'on peut, avec le mana contenu dans harMFunds
        Le prix du level up augmente de magiCoefCost * nbrMagi à chaque nouvel achat.

        entrées :
            harMFunds :    objet HardMana. fonds de mana utilisé pour le leveling
            nbrMagi :      nombre de magiciens pour lesquels on doit acheter des levels communs.
            magiCoefCost : int. coefficient de coût de montée de level des magiciens.

        plat-dessert :
            int. level final, à donner à tous les magiciens
        """
        magLevel = self.buySthg(harMFunds,
                                valueSthgInit = 1, valueSthgStep = +1,
                                costInit = 0, costStep = magiCoefCost*nbrMagi)

        bla("magLevel common : ", magLevel)
        return magLevel


    def buyDelayDecrementation(self, harMFunds, nbrMagi):
        """
        achète des décrémentation de delay d'apparition entre magicien.
        Le coût de départ est égal au nombre de magiciens, et ça augmente du nombre
        de magiciens à chaque fois.
        Il y'a un coefficient de pas-trop-cheritude. Car les decr de delay, c'est pas
        forcément un truc super indispensable. donc faut vraiment avoir du mana à perdre
        por acheter ça.
        Le coef de pas-trop-cheritude baisse à chaque achat.

        entrées :
            harMFunds :    objet HardMana. fonds de mana utilisé pour le leveling
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
        achète des décrémentation du coef de distance entre le héros et les magiciens,
        pour les patterns PAT_CIRCLE et PAT_DIAG.
        Le coût de départ est égal au nombre de magiciens, et ça augmente du nombre
        de magiciens à chaque fois.
        Il y'a un coefficient de pas-trop-cheritude. Car les decr de distance, c'est pas
        forcément un truc super indispensable. (mais déjà un peu plus que les decr
        de delay)
        Le coef de pas-trop-cheritude baisse à chaque achat.

        entrées :
            harMFunds :    objet HardMana. fonds de mana utilisé pour le leveling
            nbrMagi :      nombre de magiciens pour lesquels on doit acheter des levels communs.

        plat-dessert :
            int. valeur finale du coef de distance entre les magiciens et le héros.
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
        achète des décrémentation de timeWave (temps donné au joueur pour buter tous
        les magis d'une wave.

        On en achète le plus qu'on peut avec le harMFunds donné. Chaque achat diminue
        de 15 cycles le timeWave. Le premier coûte 1, le suivant 2, etc...

        entrées :
            harMFunds    : objet HardMana. fonds de mana utilisé pour le leveling
            timeWaveInit : int. valeur initiale du timeWave

        plat-dessert :
            int. valeur finale du timeWave, après décrémentations.
        """
        timeWave = self.buySthg(harMFunds,
                                valueSthgInit = timeWaveInit,
                                valueSthgStep = -15,
                                costInit = 1, costStep = 1)

        return timeWave


    def magiCoefCostConfFromMagiCoefCostBuy(self, magiCoefCost):
        """
        conversion entre le magiCoefCost d'achat des magiciens, et le
        magiCoefCost de configuration des magiciens (utilisés pour le montage de level,
        et d'autres trucs).

        entrées :
            magiCoefCost : int. coefficient de coût d'achat des magiciens.

        plat-dessert :
            int. coefficient de coût de config des magiciens.
        """

        #conversion complètement à l'arrache. Je sais pas du tout si c'est équilibré ou pas,
        #en terme de jeu, gameplay, tout ça.

        magiCoefCost -= MAGI_COEF_COST_DECAL_NBR_CONF

        if magiCoefCost < 1:
            magiCoefCost = 1

        return magiCoefCost


    def elaborateNextWave(self):
        """
        Putain de grosse fonction qui génère tous les patterns de magiciens d'une wave.

        entrées : rin.

        plat-dessert :
            tuple de 2 éléments :
             - int. temps (nbre de cycle) avant la création de la prochaine wave.
             - liste de patterns : les patterns à créer. Avec les temps de délai et les infos
               de chaque magiciens. (voir le truc que renvoie la fonction mergeGenPatInfo)
        """

        # --- RECUPERATION ET REPARTITION DU HARD-MANA ---

        #rechargement du mana pour cette wave. prise en compte de l'antiHarM si y'en a.
        self.addHarMForNextWave()
        bla("  harmTotal for this wave :",str(self.harMTotal))

        #listes total des patterns qui seront générés pour cette wave
        self.listOfGenPattern = []
        #nombre total de magiciens générés pour cette wave.
        self.nbrTotalMagiGenerated = 0

        #répartition du harM pour le pattern principal (harMRand), et les patterns sup (harMPat)
        #la tendance est de donner un peu plus au pattern principal
        (harMRand, harMPat) = self.harMTotal.dispatch(50, 100)

        #on prend le harM le plus grand parmi les deux, et on en retire un petit peu
        #pour avoir le harM de time wave (celui qui sera utilisé pour diminuer le timeWave
        #de cette wave. blablabla)
        if harMRand.getV() > harMPat.getV():
            (harMRand, harMTimeWave) = harMRand.dispatch(110, 128)
        else:
            (harMPat, harMTimeWave) = harMPat.dispatch(110, 128)

        bla("self.harMTotal", self.harMTotal, "harMRand ",harMRand,
            "harMPat ", harMPat, "harMTimeWave", harMTimeWave)

        # --- PATTERN PRINCIPAL "RAND" ---

        #   - CHOIX DU TYPE DE PATTERN, REPARTITION DU HARM, ACHAT DES MAGIS -

        #répartition du harM entre celui utilisé pour acheter les magi (harMRandNbr),
        #et celui utilisé pour configurer les magiciens achetés (harMRandConf)
        #on donne plus de harM à l'achat qu'à la conf
        (harMRandNbr, harMRandConf) = harMRand.dispatch(50, 100)
        bla("harMRandNbr : ", harMRandNbr, "harMRandConf : ", harMRandConf)

        #choix du type de pattern pour le pattern principal. En général, on
        #prend le pattern de type rand (magicien créé n'importe où au hasard)
        #mais y'a une petite probabilité qu'on en prenne un autre, moyennant mana (lol consonance)
        patRand = harMRandNbr.chooseAndPay(LIST_PATTERN_CHOICE_GEN_RAND)[0]
        bla("harMRandNbr : ", harMRandNbr, "pattern : ", patRand)

        #les magiciens du pattern principal sont de type MAGI_RAND. Y'a pas le choix.
        #donc le magiCoefCost se détermine tout de suite
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

        #achat de diminution du délay d'apparition des magiciens du pattern
        delayMagiRand = self.buyDelayDecrementation(harMRandConf, nbrMagi)
        bla("harMRandConf : ", harMRandConf)

        #init des level des magiciens, et achat de leur montée de level.
        #(dans le pattern principal, les level up sont individuels, y'a pas le choix
        magLevelList = [1, ] * nbrMagi
        param = (harMRandConf, magLevelList, magiCoefCost)
        magLevelList = self.buyLevelIndividually(*param)
        bla("magLevelList : ", magLevelList)
        bla("harMRandConf : ", harMRandConf)

        #construction des coordonnées de départ des magiciens, pour ce pattern.
        #les coordonnées de fin, en fait ce sera toujours None, car on a
        #forcément des MAGI_RAND dans le pattern principal
        listCoordStart, listCoordEnd = self.funcGenPat(patRand, nbrMagi)

        #hop, on colle tout ce bordel ensemble, et ça nous fait un joli pattern principal !
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

        #répartition du harM entre le harM pour acheter les patterns eux-mêmes (harMPatChoice),
        #et le harM pour acheter les magiciens et la config de tous les patters sup (harMPatMain)
        harMPatChoice, harMPatMain = harMPat.dispatch(32, 76)
        bla("harMPatChoice : ", harMPatChoice, "harMPatMain : ", harMPatMain)

        listPatChosen = []

        #on prend le gros tuple de départ, listant les patterns sup avec leur coût et
        #coef de proba, et on le clone en une liste, qu'on pourra modifier.
        currentListPatternChoice = [ list(elem) for elem
                                     in LIST_PATTERN_CHOICE_GEN_PAT ]

        #choix et achat d'un pattern parmi la liste disponible.
        #les patterns trop chers sont préalablement éliminé. et le pattern choisi
        #est après-alablement éliminé aussi, pour pas prendre 2 fois le même.
        #si pas assez de harM pour choisir un pattern, on passera tout de suite
        #à la suite, et il n'y aura aucun pattern sup.
        patChosenInfo = harMPatChoice.chooseAndPay(currentListPatternChoice)

        while patChosenInfo is not None:

            # Récupération des infos liées au pattern choisi
            # (patChosenInfo = tuple de 2 éléments : magiCoefCost, patternId)
            # et de la liste de pattern sup restante, après toutes les éliminations.
            patChosen, remainingList = patChosenInfo
            listPatChosen.append(patChosen)
            currentListPatternChoice = remainingList

            #augmentation du prix d'achat de tous les patterns restants.
            #(plus on achète de patterns, plus ils coûtent cher)
            for elem in currentListPatternChoice:
                elem[1] += COST_PATTERN_SUP_INCR

            #re-choisissage d'un nouveau pattern sup, ou pas si on n'a plus assez
            #de harM et qu'ils sont tous devenus trop chers.
            # Convention code fail :
            # Virage des espaces avant et après le egal car ligne trop longue. (beurk)
            patChosenInfo=harMPatChoice.chooseAndPay(currentListPatternChoice)


        #on re-verse le harM restant (harMPatChoice) dans le harM qui va être utilisé
        #pour acheter les magiciens et faire la config des patterns sup. (harMPatMain)
        harMPatMain.grabAll(harMPatChoice)

        nbrPatChosen = len(listPatChosen)

        if nbrPatChosen > 0:

            #répartition des harM pour chaque pattern sup. (De manière presque équitable,
            #y'a juste le reste de la division qu'on claque dans le premier)
            #ça devrait se rééquilibrer par la suite, car à chaque fois, on re-verse
            #le harM du pattern sup précédent dans le pattern courant. Et de toutes façons osef.
            listHarMPatMain = harMPatMain.divide(nbrPatChosen)

            #rassemblage de toutes les infos de chaque pattern sup.
            listPatWithHarM = zip(listPatChosen, listHarMPatMain)
            bla("liste des patterns avec les infos : ", listPatWithHarM)

            #ça c'est le HarMana pour faire le transfert du pat précédent au pat courant.
            harMRemainingPrecedentPat = HardMana()

            # --- ACHAT DSE MAGICIENS ET CONFIGURATION DE CHAQUE PATTERN SUP ---

            for patWithHarM in listPatWithHarM:

                #c'est un peu foutu en bordel, avec tout ce qu'on a fait avant.
                #donc je récupère mes données de manière un peu plus explicite
                magiCoefCost = patWithHarM[0][0]
                patternId = patWithHarM[0][1]
                harMCurrent = patWithHarM[1]

                param = (patternId, magiCoefCost,
                         harMCurrent, harMRemainingPrecedentPat)

                self.elaboratePatternSup(*param)

            #re-versage du harM du pattern prec dans le pattern courant
            harMPatMain.grabAll(harMRemainingPrecedentPat)

        #et finalement, on re-verse le harM restant à la fin dans la
        #grosse réserve globale de harM. Ce sera utilisé pour la prochaine wave.
        #(on re-verse pas dans le harM utilisé pour diminuer le timeWave, parce
        #que ça aurait pas trop d'intérêt. Faut pas claquer tout son harM dans
        #la diminution du temps.
        self.harMTotal.grabAll(harMPatMain)

        # --- CALCUL DE TIMEWAVE, ET DIMINUTION AVEC HARTIMEWAVE ---
        bla("   -------- diminution temps avec harMTimeWave  -----------")

        #calcul de la difficulté de la wave, et conversion pour avoir le timeWave.
        #(tout ça c'est calculé à l'arrache. J'ai essayé de réfléchir à des formules et des
        #dosages pour que ce soit vaguement équilibré, mais je garantis rien.)
        #c'est marrant de dire "formules" et "dosages", ça fait alchimiste.
        waveDifficulty = self.nbrTotalMagiGenerated + self.indexCurrentWave
        timeWave = TIME_WAVE_BASE + waveDifficulty * TIME_WAVE_COEF_DIFFICULTY
        bla("timeWave : ", timeWave)

        #diminution du timeWave en dépensant le harM de harMTimeWave
        timeWave = self.buyTimeWaveDecrementation(harMTimeWave, timeWave)
        bla("timeWave : ", timeWave)

        #youpiiii !!!
        if timeWave < 10:
            timeWave = 10

        #on re-verse le harM restant de harMTimeWave dans le gros harM global,
        #pour la prochaine wave
        self.harMTotal.grabAll(harMTimeWave)

        #augmentation du nombre total de wave généré
        self.indexCurrentWave += 1

        bla("harmTotal left after the wave : ", self.harMTotal)
        bla("------------- end of wave generation -------------")
        for _ in xrange(5): bla("")

        return timeWave, self.listOfGenPattern


    def elaboratePatternSup(self, patternId, magiCoefCost,
                            harMCurrent, harMRemainingPrecedentPat):
        """
        putain de grosse fonction  qui crée et configure un pattern sup.

        entrées :
            patternId     : identifiant du type de pattern à générer
            magiCoefCost  : int. coef de coût d'achat des magiciens de ce pattern
            harMCurrent   : objet HardMana. harM alloué pour ce pattern.
            harMRemainingPrecedentPat : objet HardMana. harM restant du pattern sup
               précédent. (A récupérer, et à re-verser à la fin de l'élaboration)

        la fonction ajoute directement le pattern sup dans l'attribut listOfGenPattern
        """
        bla("   ***  pattern : ", patternId, "   ***")

        #on récupère tout le harM du pattern sup précédent. (0 si c'est le 1er pattern sup)
        harMCurrent.grabAll(harMRemainingPrecedentPat)

        #décision si on fait des magiciens de type MAGI_RAND ou MAGI_LINE.
        #(y'a plus de chance de faire des MAGI_LINE)
        if randRange(128) < 16:
            magiType = MAGI_RAND
            #si on fait du MAGI_RAND, faut prendre le magiCoefCost qui correspond
            #(plus haut que les autres magiCoefCost, car un MAGI_RAND, c'est plus dur à buter)
            magiCoefCost = MAGI_RAND_COEF_COST
            #on n'aura pas besoin de la coordonnée de fin, avec des MAGI_RAND.
            coordEnd = None
            bla("randomized magi !")
        else:
            magiType = MAGI_LINE
            #on garde le même magiCoefCost, et on dit que y'aura besoin de la coordEnd
            coordEnd = True

        #répartition du harM entre l'achat des magiciens (harMCurNbr), et le reste (harMCurConf)
        (harMCurNbr, harMCurConf) = harMCurrent.dispatch(16, 96)
        bla("harMCurNbr : ", harMCurNbr, "harMCurConf : ", harMCurConf)

        #achat des magiciens du pattern. Hopla.
        nbrMagi = self.buyMagicians(harMCurNbr, magiCoefCost)

        #on re-verse le harM restant qui a servi à acheter les magiciens,
        #dans le harM utilisé pour tous le reste.
        harMCurConf.grabAll(harMCurNbr)
        bla("harMCurNbr : ", harMCurNbr, "harMCurConf : ", harMCurConf)

        #maintenant, on va faire de la config de pattern.
        #Donc on passe du magiCoefCost d'achat de magi au magiCoefCost de config de magi
        magiCoefCost = self.magiCoefCostConfFromMagiCoefCostBuy(magiCoefCost)

        #éventuellement, achat de réduction du coefficient de la distance entre le joueur
        #et les magiciens du pattern. (si le type de pattern s'y prête.)
        if patternId in (PAT_CIRCLE, PAT_DIAG):
            rayCoef = self.buyRayCoefDecrementation(harMCurConf, nbrMagi)
        else:
            rayCoef = None  #osef de ce param

        #décision de si on fait apparaître tous les magiciens d'un seul coup,
        #(ça coute un peu de harM), ou si ils apparaissent un par un. (ça coute rien)
        #dans les deux cas, faudra quand même acheter les diminutions de délai, mais
        #on verra plus tard.
        costAppCommon = nbrMagi * magiCoefCost
        coefAppCommon = 100  #TRODO : je sais pas bien équilibrer ce truc. is it la bonne méthode?

        if harMCurConf.payIfCheap(costAppCommon, coefAppCommon):
            apparitionInCommon = True
            bla("apparition common !!")
        else:
            apparitionInCommon = False

        #achat de réduction du délai d'apparition des magiciens.
        delayMagiRand = self.buyDelayDecrementation(harMCurConf, nbrMagi)

        #si ils n'apparaissent pas en même temps, le delay est placé entre chaque
        #magicien, comme d'hab'.
        #si ils apparaissent en même temps, ils ont tous le même délai,
        #égal à : <délai de départ> * <nbrMagi> / 2. captain obvious c'est dit juste après.

        if apparitionInCommon:

            #calcul du delay commun pour tous les magiciens.
            delayCommon = (delayMagiRand * nbrMagi) / 2

            #dans la delayList, les delay sont cumulatifs. Donc pour un délai commun,
            #on doit mettre le total de delay sur le premier magi, et tous les autres auront 0.

            #construction d'une liste avec le delayCommon en premier élément, puis que des 0
            delayList = (delayCommon, ) + (0, ) * (nbrMagi - 1)

            delayMagiRand = None  #osef

        else:

            delayList = None  #osef

        bla("harMCurConf : ", harMCurConf)

        #décision de si on fait des montée de level commun, ou pas.
        #(le level up commun coute des sous. L'individuel ne coûte rien)
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

            #initialisation des level de départ des magiciens. (tous au niveau 1)
            magLevelList = [1, ] * nbrMagi

            #achat des level up individuel.
            param = (harMCurConf, magLevelList, magiCoefCost)
            magLevelList = self.buyLevelIndividually(*param)
            magLevel = None  #osef
            bla("magLevelList : ", magLevelList)

        #construction des coordonnées de départ (et éventuellement les coordonnées de fin),
        #des magiciens du pattern.
        param = (patternId, nbrMagi, coordEnd, rayCoef)
        listCoordStart, listCoordEnd = self.funcGenPat(*param)

        #rassemblage de toutes les infos nécessaires à la création du pattern,
        #et ajout dans listOfGenPattern

        param = (magiType, listCoordStart, listCoordEnd,
                 magLevel, magLevelList,
                 delayMagiRand, delayList)

        genPatternRand = self.mergeGenPatInfo(*param)

        self.listOfGenPattern.append(genPatternRand)

        bla("harMCurNbr : ", harMCurNbr, "harMCurConf : ", harMCurConf)

        #on re-verse le harM restant dans harMRemainingPrecedentPat, qui sera redonné au
        #prochain pattern supplémentaire. (ou à la réserve globale de harM si c'était
        #le dernier pattern sup).
        harMRemainingPrecedentPat.grabAll(harMCurConf)

