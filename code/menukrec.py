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

date de la derni�re relecture-commentage : 24/02/2011

Element de menu qui chope un appuyage de touche appuy�e, et stocke le code de cette touche,
pour en faire ce qu'on veut apr�s.
Pour que le MenuElem enregistre, faut activer son mode enregistrement. Sinon �a fait rien.
(C'est fait expr�s, evidemment ! Car on n'a peut �tre pas tout le temps besoin d'enregistrer
les touches).
Il ne garde en m�moire qu'un seul appuyage de touche (le dernier effectu�). Donc faut le
r�cup�rer et en faire quelque chose imm�diatement.
On peut activer/d�sactiver le mode enregistrement comme on veut.
"""

import pygame
from common   import IHMSG_VOID
from menuelem import MenuElem



class MenuOneKeyRecorder(MenuElem):
    """
    enregistreur d'appuyage de touche. (mais que une par une)
    """

    def __init__(self, funcAction):
        """
        constructeur. (thx captain obvious)

        entr�e :
            funcAction : r�f�rence vers la fonction � ex�cuter quand ce menuElem est activ�.
                c'est � dire : quand le mode enregistrement est activ�, et que le joueur
                appuie sur une touche.
        """

        MenuElem.__init__(self)

        self.funcAction = funcAction
        #bool�ean indiquant si le mode enregistrement est activ� ou pas. L� : non
        self.recordingKey = False
        #code de la derni�re touche appuy�e. L� pour l'instant y'en a pas. On fout -1 par d�faut.
        self.keyRecorded = -1


    def activateRecording(self):
        """
        Active le mode enregistrement. Bzzzuuuuuu !!! Rofl rofl rofl rofl rofl.
        """
        self.recordingKey = True


    def desactivateRecording(self):
        """
        D�sactive le mode enregistrement. Kshhttzzmm ! wObble .. wObble ... wObble ... wOb
        """
        self.recordingKey = False


    def takeStimuliKeys(self, dictKeyPressed, keyCodeDown, keyCharDown):
        """
        prise en compte des touches appuy�es par le joueur.
        (voir description dans la classe MenuElem)
        """

        if not self.recordingKey:
            #le mode enregistrement n'est pas activ�. On s'en fout des appuyages de touches.
            #On fout rien, et on se casse.
            return IHMSG_VOID

        #bon, le mode enregistrement est activ�. Faut bosser un peu.
        #on enregistre le code de la touche appuy�e, ainsi que le caract�re unicode qui va avec
        #(la valeur de ces deux variables est d�finie par pygame. C'est lui qui g�re tout �a.
        #Moi je me contente de les r�cup�rer)
        self.keyRecorded = keyCodeDown
        self.charKeyRecorded = keyCharDown
        #Ex�cution de la fonction d'action. Propagation du tuple de message d'ihm renvoy�.
        return self.funcAction()
