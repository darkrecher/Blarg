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

date de la dernière relecture-commentage : 24/02/2011

Element de menu qui chope un appuyage de touche appuyée, et stocke le code de cette touche,
pour en faire ce qu'on veut après.
Pour que le MenuElem enregistre, faut activer son mode enregistrement. Sinon ça fait rien.
(C'est fait exprès, evidemment ! Car on n'a peut être pas tout le temps besoin d'enregistrer
les touches).
Il ne garde en mémoire qu'un seul appuyage de touche (le dernier effectué). Donc faut le
récupérer et en faire quelque chose immédiatement.
On peut activer/désactiver le mode enregistrement comme on veut.
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

        entrée :
            funcAction : référence vers la fonction à exécuter quand ce menuElem est activé.
                c'est à dire : quand le mode enregistrement est activé, et que le joueur
                appuie sur une touche.
        """

        MenuElem.__init__(self)

        self.funcAction = funcAction
        #booléean indiquant si le mode enregistrement est activé ou pas. Là : non
        self.recordingKey = False
        #code de la dernière touche appuyée. Là pour l'instant y'en a pas. On fout -1 par défaut.
        self.keyRecorded = -1


    def activateRecording(self):
        """
        Active le mode enregistrement. Bzzzuuuuuu !!! Rofl rofl rofl rofl rofl.
        """
        self.recordingKey = True


    def desactivateRecording(self):
        """
        Désactive le mode enregistrement. Kshhttzzmm ! wObble .. wObble ... wObble ... wOb
        """
        self.recordingKey = False


    def takeStimuliKeys(self, dictKeyPressed, keyCodeDown, keyCharDown):
        """
        prise en compte des touches appuyées par le joueur.
        (voir description dans la classe MenuElem)
        """

        if not self.recordingKey:
            #le mode enregistrement n'est pas activé. On s'en fout des appuyages de touches.
            #On fout rien, et on se casse.
            return IHMSG_VOID

        #bon, le mode enregistrement est activé. Faut bosser un peu.
        #on enregistre le code de la touche appuyée, ainsi que le caractère unicode qui va avec
        #(la valeur de ces deux variables est définie par pygame. C'est lui qui gère tout ça.
        #Moi je me contente de les récupérer)
        self.keyRecorded = keyCodeDown
        self.charKeyRecorded = keyCharDown
        #Exécution de la fonction d'action. Propagation du tuple de message d'ihm renvoyé.
        return self.funcAction()
