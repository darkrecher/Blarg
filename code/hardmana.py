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

date de la derni�re relecture-commentage : 23/09/2010

classe qui g�re le harM (Hard Mana)
HardMana = harM : c'est la m�me chose mais en abr�g�

lire le d�but de maggenwa.py pour plein de blabla super int�ressant.
"""

import pygame

from common import randRange, randWithListCoef, SHIFT_PREC, NOT_FLOATING_PREC

#valeur maximal d'antiHarm qu'on peut se prendre dans la gueule lors d'un
#debuff � l'antiHarM. (l'antiHarM restant sera gard� pour un prochain debuff)
ANTI_HARM_DECR_MAX = 40



class HardMana():
    """
    contient une valeur de HardMana. A utiliser pour acheter des trucs dans les waves.
    """
    def __init__(self, valInit=0):
        """
        constructeur. (thx captain obvious)

        entr�e :
            valInit : int. Quantit� initiale de HardMana dans l'objet.
        """
        self._val = valInit

        #d�finition de fonction avec des noms plus explicites
        #(en fait la seule diff�rence ce sera au niveau des param par d�faut)
        self.payIfCheap = self.payGeneric
        self.payIfEnough = self.payGeneric


    def getV(self):
        """
        captain obvious
        """
        return self._val


    def addHarM(self, harMToAdd):
        """
        ajoute du HardMana � la valeur courante.

        entr�es :
            harMToAdd : int. Quantit� de HardMana � rajouter.
        """
        self._val += harMToAdd


    def grabAll(self, harMToGrab):
        """
        r�cup�re tout le harM d'un autre objet HardMana

        entr�es :
            harMToGrab : objet HardMana, � qui on doit piquer tout le contenu
        """
        #on augmente sa propre quantit�.
        self._val += harMToGrab._val
        #et on met la quantit� de l'autre harM � 0, car on lui a tout piqu�
        harMToGrab._val = 0


    def payGeneric(self, cost, decisionCoef=None):
        """
        fonction g�n�rique pour payer un truc (quel qu'il soit).

        entr�es :
            cost : int. co�t en HardMana du truc � acheter
            decisionCoef : coefficient de "pas-trop-cheritude".

        plat-dessert :
            boolean. indique si on a d�cid� d'acheter le truc ou pas

        y'a deux cas possible :
         - decisionCoef = None : on paye obligatoirement, si on a assez de harM.
         - decisionCoef = (int donn� en 128eme). dans ce cas, on paye que si
           c'est pas trop cher par rapport � la quantit� de harM qu'on a.
           la prise de d�cision est un peu random : moins �a co�te, plus on a
           de harM, et plus le coefficient est haut -> plus on a de chance de l'acheter.
           Putain, �a pue le parfum dans ce bus bordel !
        """

        if self._val < cost:
            #trop cher. Pas la peine de r�fl�chir � une d�cision, on peut pas acheter.
            return False

        if decisionCoef is not None:

            #il y a un coef de pas-trop-cheritude. On l'utilise pour prendre la d�cision.

            #on shift-right la valeur car le coef est en 128eme
            decisionRandMax = (self._val * decisionCoef) >> SHIFT_PREC

            #c'est vraiment trop faible, de toutes fa�ons on d�cidera de pas acheter.
            #on se casse tout de suite
            if decisionRandMax == 0:
                return False

            #plus on a de mana et plus on a de coef,
            #plus on peut esp�rer avoir une valeur de decision haute
            decision = randRange(decisionRandMax)

            #si la decision est trop faible, par rapport au cost, on d�cide de pas acheter.
            if decision < cost:
                return False

        #tous les tests ont �t� pass�s. C'est bon, on ach�te.
        self._val -= cost
        return True


    def dispatch(self, coefMin, coefMax):
        """
        r�partit le harM dans deux autre objets HardMana.
        selon un ratio random, mais encadr� entre deux valeurs.

        entr�es:
            coefMin, coefMax : deux valeurs int, en 128eme.
            indique les valeurs min et max du ratio utilis� pour la r�partition.
            Le ratio indique combien on met de harM dans le premier objet,
            par rapport au harM total. le deuxi�me objet prend le reste du harM
            le ratio r�el est d�termin� en random entre coefMin et coefMax

        plat-dessert :
            tuple de 2 �l�ments.
             - le premier objet HardMana, contenant une partie du harM
             - le second objet HardMana

            (les deux objets HardMana sont cr��s pour l'occasion)
        """

        #calcul du ratio de r�partition du harM
        dispatchLimitCoef = randRange(coefMin, coefMax)
        #petite s�curit� � la con. Faut pas que �a d�passe 128
        if dispatchLimitCoef > NOT_FLOATING_PREC:
            dispatchLimitCoef = NOT_FLOATING_PREC

        #r�partition du harM en deux valeurs, selon le ratio calcul�.
        val_1 = (self._val * dispatchLimitCoef) >> SHIFT_PREC
        #hop, avec �a, on s'assure que y'a pas d'erreur d'arrondi pourri.
        #Et que y'a pas eu de harM cr��/perdu dans la r�partition. (oui c facile comme astuce)
        val_2 = self._val - val_1
        #on n'a plus de harM pour soi-m�me, vu qu'on vient de le donner.
        self._val = 0

        #cr�ation et renvoi des deux ibjets HardMana contenant le harM r�parti.
        harM_1 = HardMana(val_1)
        harM_2 = HardMana(val_2)
        return (harM_1, harM_2)


    def chooseAndPay(self, listCoefCost):
        """
        choisit un �l�ment parmi une liste de truc � acheter.
        (ne choisit rien si tous les trucs sont trop chers).

        entr�es :
            listCoefCost : liste de tuple de 3 �l�ments, repr�sentant les diff�rents choix
              - coefficient de ce choix, utilis� pour le random
              - prix � payer pour ce choix
              - n'importe quoi (c'est la valeur qui sera renvoy�e par la fonction,
                �a repr�sente le truc en lui-m�me)

        plat-dessert :
            None si on peut rien acheter dans la liste.
            sinon, un tuple de 2 elem :
             - le truc qu'on a choisi d'acheter. Un �l�ment de listCoefCost[][2]
             - la liste de choix listCoefCost, � laquelle on a supprim� les �l�ments trops chers,
               et celui qui a �t� choisi

            si listCoefCost contient au moins un �l�ment ayant un cost de 0, et un coef > 0 :
            alors on est s�r que la fonction ne renverra pas None.
            (Je le pr�cise, mais tout le monde le savait d�j� en fait).
        """

        #constrution d'une liste � partir de listCoefCost, en virant les �l�ments trops chers.
        affordableList = [ elem for elem in listCoefCost
                           if elem[1] <= self._val ]

        #Tout �tait trop cher. On se casse de la fonction et on renvoie None.
        if len(affordableList) == 0:
            return None

        #r�cup�ration des coefs de probabilit� de choix des �l�ments.
        listCoef = [ elem[0] for elem in affordableList ]

        #choix en random d'un �l�ment parmi la liste, en tenant compte des coefs de proba
        choiceIndex = randWithListCoef(listCoef)
        #recup des infos li�s � ce choix.
        (cost, dataChosen) = affordableList[choiceIndex][1:]
        #on a achet� l'elem, donc on diminue le harM.
        self._val -= cost

        #on vire l'�l�ment qui a �t� choisi de la liste de choix.
        affordableList.pop(choiceIndex)

        return dataChosen, affordableList


    def divide(self, nbr):
        """
        divise le harM en plusieurs objets HardMana, r�partis � peu pr�s �quitablement.
        chaque objet HardMana contient une part du harM, arrondi inf�rieur.
        on rajoute au premier objet HardMana le reste de la division. De cette mani�re,
        il n'y a pas de harM perdu ou cr�� dans cette r�partition.

        entr�es :
            nbr : int. nombre d'objets HardMana � cr�er pour faire la division de harM

        plat-dessert :
            liste de nbr objets HardMana, contenant chacun une partie du harM initial
            (les objets HardMana sont cr��s pour l'occasion)
        """

        #division enti�re du harM (donc arrondi inf�rieur)
        valDivide = self._val / nbr
        #r�cup�ration du reste du harM. (le reste de la division enti�re, voyez...)
        valRest = self._val % nbr

        #cr�ation du premier objet HardMana,
        #et ajout dans la liste qui contiendra tous les HardMana
        firstHarM = HardMana(valDivide + valRest)
        listHarM = [ firstHarM, ]

        #cr�ation de tous les autres objets HardMana, et ajout dans la liste.
        for _ in xrange(nbr-1):
            listHarM.append(HardMana(valDivide))

        #on n'a plus de harM pour soi-m�me, vu qu'on vient de le donner.
        self._val = 0

        return listHarM


    def antiHarMDebuff(self, antiHarM):
        """
        diminution du harM � cause d'un balan�age de antiHarM dans la gueule (debuff).
        1 point d'antiHarM et 1 point de harM s'annulent mutuellement.

        entr�es :
            antiHarM : objet HardMana contenant l'antiHarM du debuff

        plat-dessert :
            la valeur de harM de l'objet self est diminu�e. la valeur de l'antiHarM aussi.

        Y'a des contraintes pour ce debuff :
         - on peut pas virer plus de harM que ce qu'il y a dans l'objet.
           donc l'antiHarM ne sera peut �tre pas vir� enti�rement.
         - on ne peut pas virer plus de 70 points de harM d'un coup
           (valeur indiqu�e dans ANTI_HARM_DECR_MAX).
           donc l'antiHarM ne sera peut �tre pas vir� enti�rement.
           (D�j� dit juste au-dessus, mais pour une autre raison)
        """

        if antiHarM._val > self._val and self._val < ANTI_HARM_DECR_MAX:

            #il y a plus d'antiHarM que de harM. Et y'a tellement pas assez de harM
            #que y'en a moins que 70.
            #on debuffe le harM d'autant qu'on peut. l'antiHarM est diminu� d'autant.
            antiHarM._val -= self._val
            self._val = 0

        elif antiHarM._val > ANTI_HARM_DECR_MAX:

            #y'a beaucoup d'antiHarM, plus que la limite ANTI_HARM_DECR_MAX.
            #donc on ne debuff que ANTI_HARM_DECR_MAX, pas plus.
            #plus la peine de se poser la question si on a plus ou moins d'antiHarM que
            #de harM. Gr�ce au cas pr�c�dent, on ne peut pas enlever plus de harM
            #que ce qu'on en a. (Ca a pas l'air �vident, mais j'ai test�)
            self._val -= ANTI_HARM_DECR_MAX
            antiHarM._val -= ANTI_HARM_DECR_MAX

        elif antiHarM._val > 0:

            #il y a de l'antiHarM, mais moins que la limite. Donc on peut debuffer
            #tout le antiHarM sans probl�me. (une fois de plus, pas la peine de se
            #poser la question si on a plus ou moisn d'antiHarM que de harM, car blabla)
            self._val -= antiHarM._val
            antiHarM._val = 0


    def __repr__(self):
        """
        captain obvious.
        (le __repr__ est la fonction qui est appel�e quand on fait un print <objet HardMana>
        """
        return str(self._val)


