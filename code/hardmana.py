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

date de la dernière relecture-commentage : 23/09/2010

classe qui gère le harM (Hard Mana)
HardMana = harM : c'est la même chose mais en abrégé

lire le début de maggenwa.py pour plein de blabla super intéressant.
"""

import pygame

from common import randRange, randWithListCoef, SHIFT_PREC, NOT_FLOATING_PREC

#valeur maximal d'antiHarm qu'on peut se prendre dans la gueule lors d'un
#debuff à l'antiHarM. (l'antiHarM restant sera gardé pour un prochain debuff)
ANTI_HARM_DECR_MAX = 40



class HardMana():
    """
    contient une valeur de HardMana. A utiliser pour acheter des trucs dans les waves.
    """
    def __init__(self, valInit=0):
        """
        constructeur. (thx captain obvious)

        entrée :
            valInit : int. Quantité initiale de HardMana dans l'objet.
        """
        self._val = valInit

        #définition de fonction avec des noms plus explicites
        #(en fait la seule différence ce sera au niveau des param par défaut)
        self.payIfCheap = self.payGeneric
        self.payIfEnough = self.payGeneric


    def getV(self):
        """
        captain obvious
        """
        return self._val


    def addHarM(self, harMToAdd):
        """
        ajoute du HardMana à la valeur courante.

        entrées :
            harMToAdd : int. Quantité de HardMana à rajouter.
        """
        self._val += harMToAdd


    def grabAll(self, harMToGrab):
        """
        récupère tout le harM d'un autre objet HardMana

        entrées :
            harMToGrab : objet HardMana, à qui on doit piquer tout le contenu
        """
        #on augmente sa propre quantité.
        self._val += harMToGrab._val
        #et on met la quantité de l'autre harM à 0, car on lui a tout piqué
        harMToGrab._val = 0


    def payGeneric(self, cost, decisionCoef=None):
        """
        fonction générique pour payer un truc (quel qu'il soit).

        entrées :
            cost : int. coût en HardMana du truc à acheter
            decisionCoef : coefficient de "pas-trop-cheritude".

        plat-dessert :
            boolean. indique si on a décidé d'acheter le truc ou pas

        y'a deux cas possible :
         - decisionCoef = None : on paye obligatoirement, si on a assez de harM.
         - decisionCoef = (int donné en 128eme). dans ce cas, on paye que si
           c'est pas trop cher par rapport à la quantité de harM qu'on a.
           la prise de décision est un peu random : moins ça coûte, plus on a
           de harM, et plus le coefficient est haut -> plus on a de chance de l'acheter.
           Putain, ça pue le parfum dans ce bus bordel !
        """

        if self._val < cost:
            #trop cher. Pas la peine de réfléchir à une décision, on peut pas acheter.
            return False

        if decisionCoef is not None:

            #il y a un coef de pas-trop-cheritude. On l'utilise pour prendre la décision.

            #on shift-right la valeur car le coef est en 128eme
            decisionRandMax = (self._val * decisionCoef) >> SHIFT_PREC

            #c'est vraiment trop faible, de toutes façons on décidera de pas acheter.
            #on se casse tout de suite
            if decisionRandMax == 0:
                return False

            #plus on a de mana et plus on a de coef,
            #plus on peut espérer avoir une valeur de decision haute
            decision = randRange(decisionRandMax)

            #si la decision est trop faible, par rapport au cost, on décide de pas acheter.
            if decision < cost:
                return False

        #tous les tests ont été passés. C'est bon, on achète.
        self._val -= cost
        return True


    def dispatch(self, coefMin, coefMax):
        """
        répartit le harM dans deux autre objets HardMana.
        selon un ratio random, mais encadré entre deux valeurs.

        entrées:
            coefMin, coefMax : deux valeurs int, en 128eme.
            indique les valeurs min et max du ratio utilisé pour la répartition.
            Le ratio indique combien on met de harM dans le premier objet,
            par rapport au harM total. le deuxième objet prend le reste du harM
            le ratio réel est déterminé en random entre coefMin et coefMax

        plat-dessert :
            tuple de 2 éléments.
             - le premier objet HardMana, contenant une partie du harM
             - le second objet HardMana

            (les deux objets HardMana sont créés pour l'occasion)
        """

        #calcul du ratio de répartition du harM
        dispatchLimitCoef = randRange(coefMin, coefMax)
        #petite sécurité à la con. Faut pas que ça dépasse 128
        if dispatchLimitCoef > NOT_FLOATING_PREC:
            dispatchLimitCoef = NOT_FLOATING_PREC

        #répartition du harM en deux valeurs, selon le ratio calculé.
        val_1 = (self._val * dispatchLimitCoef) >> SHIFT_PREC
        #hop, avec ça, on s'assure que y'a pas d'erreur d'arrondi pourri.
        #Et que y'a pas eu de harM créé/perdu dans la répartition. (oui c facile comme astuce)
        val_2 = self._val - val_1
        #on n'a plus de harM pour soi-même, vu qu'on vient de le donner.
        self._val = 0

        #création et renvoi des deux ibjets HardMana contenant le harM réparti.
        harM_1 = HardMana(val_1)
        harM_2 = HardMana(val_2)
        return (harM_1, harM_2)


    def chooseAndPay(self, listCoefCost):
        """
        choisit un élément parmi une liste de truc à acheter.
        (ne choisit rien si tous les trucs sont trop chers).

        entrées :
            listCoefCost : liste de tuple de 3 éléments, représentant les différents choix
              - coefficient de ce choix, utilisé pour le random
              - prix à payer pour ce choix
              - n'importe quoi (c'est la valeur qui sera renvoyée par la fonction,
                ça représente le truc en lui-même)

        plat-dessert :
            None si on peut rien acheter dans la liste.
            sinon, un tuple de 2 elem :
             - le truc qu'on a choisi d'acheter. Un élément de listCoefCost[][2]
             - la liste de choix listCoefCost, à laquelle on a supprimé les éléments trops chers,
               et celui qui a été choisi

            si listCoefCost contient au moins un élément ayant un cost de 0, et un coef > 0 :
            alors on est sûr que la fonction ne renverra pas None.
            (Je le précise, mais tout le monde le savait déjà en fait).
        """

        #constrution d'une liste à partir de listCoefCost, en virant les éléments trops chers.
        affordableList = [ elem for elem in listCoefCost
                           if elem[1] <= self._val ]

        #Tout était trop cher. On se casse de la fonction et on renvoie None.
        if len(affordableList) == 0:
            return None

        #récupération des coefs de probabilité de choix des éléments.
        listCoef = [ elem[0] for elem in affordableList ]

        #choix en random d'un élément parmi la liste, en tenant compte des coefs de proba
        choiceIndex = randWithListCoef(listCoef)
        #recup des infos liés à ce choix.
        (cost, dataChosen) = affordableList[choiceIndex][1:]
        #on a acheté l'elem, donc on diminue le harM.
        self._val -= cost

        #on vire l'élément qui a été choisi de la liste de choix.
        affordableList.pop(choiceIndex)

        return dataChosen, affordableList


    def divide(self, nbr):
        """
        divise le harM en plusieurs objets HardMana, répartis à peu près équitablement.
        chaque objet HardMana contient une part du harM, arrondi inférieur.
        on rajoute au premier objet HardMana le reste de la division. De cette manière,
        il n'y a pas de harM perdu ou créé dans cette répartition.

        entrées :
            nbr : int. nombre d'objets HardMana à créer pour faire la division de harM

        plat-dessert :
            liste de nbr objets HardMana, contenant chacun une partie du harM initial
            (les objets HardMana sont créés pour l'occasion)
        """

        #division entière du harM (donc arrondi inférieur)
        valDivide = self._val / nbr
        #récupération du reste du harM. (le reste de la division entière, voyez...)
        valRest = self._val % nbr

        #création du premier objet HardMana,
        #et ajout dans la liste qui contiendra tous les HardMana
        firstHarM = HardMana(valDivide + valRest)
        listHarM = [ firstHarM, ]

        #création de tous les autres objets HardMana, et ajout dans la liste.
        for _ in xrange(nbr-1):
            listHarM.append(HardMana(valDivide))

        #on n'a plus de harM pour soi-même, vu qu'on vient de le donner.
        self._val = 0

        return listHarM


    def antiHarMDebuff(self, antiHarM):
        """
        diminution du harM à cause d'un balançage de antiHarM dans la gueule (debuff).
        1 point d'antiHarM et 1 point de harM s'annulent mutuellement.

        entrées :
            antiHarM : objet HardMana contenant l'antiHarM du debuff

        plat-dessert :
            la valeur de harM de l'objet self est diminuée. la valeur de l'antiHarM aussi.

        Y'a des contraintes pour ce debuff :
         - on peut pas virer plus de harM que ce qu'il y a dans l'objet.
           donc l'antiHarM ne sera peut être pas viré entièrement.
         - on ne peut pas virer plus de 70 points de harM d'un coup
           (valeur indiquée dans ANTI_HARM_DECR_MAX).
           donc l'antiHarM ne sera peut être pas viré entièrement.
           (Déjà dit juste au-dessus, mais pour une autre raison)
        """

        if antiHarM._val > self._val and self._val < ANTI_HARM_DECR_MAX:

            #il y a plus d'antiHarM que de harM. Et y'a tellement pas assez de harM
            #que y'en a moins que 70.
            #on debuffe le harM d'autant qu'on peut. l'antiHarM est diminué d'autant.
            antiHarM._val -= self._val
            self._val = 0

        elif antiHarM._val > ANTI_HARM_DECR_MAX:

            #y'a beaucoup d'antiHarM, plus que la limite ANTI_HARM_DECR_MAX.
            #donc on ne debuff que ANTI_HARM_DECR_MAX, pas plus.
            #plus la peine de se poser la question si on a plus ou moins d'antiHarM que
            #de harM. Grâce au cas précédent, on ne peut pas enlever plus de harM
            #que ce qu'on en a. (Ca a pas l'air évident, mais j'ai testé)
            self._val -= ANTI_HARM_DECR_MAX
            antiHarM._val -= ANTI_HARM_DECR_MAX

        elif antiHarM._val > 0:

            #il y a de l'antiHarM, mais moins que la limite. Donc on peut debuffer
            #tout le antiHarM sans problème. (une fois de plus, pas la peine de se
            #poser la question si on a plus ou moisn d'antiHarM que de harM, car blabla)
            self._val -= antiHarM._val
            antiHarM._val = 0


    def __repr__(self):
        """
        captain obvious.
        (le __repr__ est la fonction qui est appelée quand on fait un print <objet HardMana>
        """
        return str(self._val)


