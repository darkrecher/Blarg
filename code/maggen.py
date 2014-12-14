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

date de la dernière relecture-commentage : 30/09/2010

Classe qui génère les magiciens. Chapeaute le maggenwa, maggenlc et hardmana.
Comme dirait Alexandre Astier : c'est moi qui chapeaute un peu tout le ...

La classe prend les patterns générés par le MagicianWaveGenerator, et s'occupe de
créer les instances de magiciens et de les placer dans le jeu.
La classe s'occupe également de demander une nouvelle Wave lorsque c'est le moment.
"""

import magician
import magiline
import magirand

from maggenwa import MagicianWaveGenerator, MAGI_BASE, MAGI_RAND, MAGI_LINE

from yargler import theSoundYargler, SND_MAG_APPEAR

#dico de correspondance entre le type de magicien, et la fonction constructeur pour le créer.
DIC_MAGIC_CONSTRUCTOR = {
  MAGI_BASE : magician.Magician,
  MAGI_RAND : magirand.MagiRand,
  MAGI_LINE : magiline.MagiLine,
}

#delay maximum entre deux wave. Même si le joueur a tué tous les monstres d'une wave,
#on attend ce temps (nbr de cycle) pour générer la prochaine.
#Par conséquent, ce temps ne sera pas utilisé pour alimenter le temps de bonus ou l'antiHarM
DELAY_MAX_BETWEEN_WAVE = 70

#coef de conversion entre le temps restant à la fin de la destruction d'une wave,
#et l'antiHarM offert pour ce temps. 3 cycles de temps donnent 1 point de antiHarM
COEF_CONVERSION_HARM_FROM_TIME = 3


class MagicianGenerator():
    """
    classe qui gère la création des magiciens (de tout poil) (hahaha).
    """

    def __init__(self, groupMagicianAppearing,
                 dicMagicienImg, spriteSimpleGenerator, hero):
        """
        constructeur. (thx captain obvious)

        entrée :
            groupMagicianAppearing : groupe de sprite, dans lequel on place les
                 magiciens nouvellement créés.

            dicMagicienImg : dictionnaire de correspondance entre les images et les
                identifiants d'image d'un magicien.
                Ce paramètre n'est pas réellement utilisé par cette classe.
                Il est juste transmis aux constructeurs des magicens.

            spriteSimpleGenerator : classe éponyme. Permet de générer des sprites simples
                Ce paramètre n'est pas réellement utilisé par cette classe.
                Il est juste transmis aux constructeurs des magicens.

            hero : référence vers le héros. C'est juste pour choper ses coordonnées.
                 le paramètre est transmis directement au waveGenerator lors de sa création.
        """

        self.groupMagicianAppearing = groupMagicianAppearing
        self.dicMagicienImg = dicMagicienImg
        self.spriteSimpleGenerator = spriteSimpleGenerator

        #liste des premiers paramètres à transmettre aux fonctions constructeurs de magi.
        #les param suivants ne sont pas fixes, donc on les fabriquera le moment venu.
        self.paramGeneration = (self.dicMagicienImg,
                                self.spriteSimpleGenerator)

        #liste des pattern de génération de magicien en cours. La classe dépile le
        #contenu de tous les patterns de la liste au fur à mesure du temps, et génère
        #les magiciens en fonction des infos indiquées dans le pattern.
        self.listGenPattern = []

        #numéro de la Wave en cours / Nombre de Wave déjà générée.
        self.indexCurrentWave = 0

        #classe permettant d'élaborer les différents patterns de magiciens,
        #à chaque nouvelle Wave, en fonction du HardMana qu'elle possède.
        self.magicianWaveGenerator = MagicianWaveGenerator(hero)

        #temps restant avant la prochaine Wave (nbre de cycle)
        self.counterNextWave = 0

        #temps de bonus, accumulé grâce au temps non utilisé par le joueur, lorsqu'il a
        #détruit tous les magiciens actifs d'une Wave avant le temps imparti.
        #Le temps de bonus est dépensé lorsqu'il n'y a plus de temps avant la prochaine
        #Wave. Pour obtenir une rallonge de temps.
        self.counterBonusTime = 0

        #Boolean. Indique si il y a encore des magiciens actifs dans le jeu.
        #magicien actif = un magicien vivant, et qui se déplace.
        #La prochaine Wave est lancée lorsqu'il n'y a plus de magicien actifs.
        self.presenceOfActiveMagi = False


    def generateOneMagician(self, magiType, posStart, posEnd=None, level=1):
        """
        génère un magicien et le place sur l'aire de jeu.

        entées :
            magiType : type du magicien : MAGI_BASE, MAGI_LINE, MAGI_RAND
            posStart : Rect. Coordonnées de départ du magicien.
            posEnd   : Rect. Utile seulement pour les MAGI_LINE.
                       Coordonnée d'arrivée du magicien.
                       (le MAGI_LINE se déplace de son départ jusqu'à son arrivée)
            level    : niveau du magicien
        """

        #rassemblement des paramètres, en fonction du type du magicien.
        #(pas besoin du posEnd si on doit faire un MAGI_LINE)
        if magiType == MAGI_LINE:
            param = self.paramGeneration + (posStart, posEnd, level)
        else:
            param = self.paramGeneration + (posStart, level, )

        #récupération de la fonction permettant de créer le magicien, selon son  type
        funcMagiConstructor = DIC_MAGIC_CONSTRUCTOR[magiType]

        #appel de la bonne fonction avec la bonne liste de param. Youpi.
        newMagician = funcMagiConstructor(*param)

        #son d'apparition de magicien : zwwwzzwwouuuww !!
        theSoundYargler.playSound(SND_MAG_APPEAR)

        #ajout du magicien dans le spriteGroup de magicien-qui-apparaissent.
        #Le code extérieur se démerde pour le transférer dans le spriteGroup des
        #vrais magiciens, le moment venu. Et pour gérer tout le reste du bordel.
        self.groupMagicianAppearing.add(newMagician)


    def takeStimuliNoMoreActiveMagi(self):
        """
        fonction exécutéee par le code extérieur. Permet d'indiquer à cette
        classe qu'il n'y a plus aucun magicien actifs dans l'aire de jeu.
        (voir bla-bla de la fonction Game.isMagicianActive pour une définition de "magicien actif")
        """

        #Le stimuli a déjà été pris en compte. On se casse tout de suite
        if self.presenceOfActiveMagi == False:
            return

        #enregistrement du stimuli
        self.presenceOfActiveMagi = False

        #On vérifie si le temps restant est suffisant pour accorder du bonus.
        #Dans le cas contraire, on ne fera rien, et on attendra la prochaine wave
        #comme normalement.
        if self.counterNextWave > DELAY_MAX_BETWEEN_WAVE:

            #le joueur a pu tuer les magiciens en beaucoup moins de temps que ce qui
            #lui était accordé. On calcule son bonus de temps
            waveTimeBonus = self.counterNextWave - DELAY_MAX_BETWEEN_WAVE

            #Maintenant qu'on a pris le bonus, on peut diminuer le temps avant
            #la prochaine wave, pour qu'il soit au strict minimum
            self.counterNextWave = DELAY_MAX_BETWEEN_WAVE

            #utilisation de ce temps de bonus pour obtenir de l'antiHarM, qui est
            #envoyé au WaveGenerator. L'antiHarM est un debuff, qui va rendre la/les
            #prochaines waves plus faciles que prévus (moins de magi, moins de pattern, ...)
            antiHarMBonus = waveTimeBonus / COEF_CONVERSION_HARM_FROM_TIME
            self.magicianWaveGenerator.receiveAntiHarMBonus(antiHarMBonus)

            #et en plus, utilisation de ce temps de bonnus pour alimenter le temps cumulé
            #de bonus. Ce temps est utilisé en dernier recours, lorsque le joueur n'a
            #pas tué tous les magiciens et qu'il faudrait lancer la prochaine wave.
            self.counterBonusTime += waveTimeBonus


    def updateGenPattern(self, genPattern):
        """
        mise à jour de l'un des pattern en cours.

        entrées :
            genPattern : pattern de génération de magicien dont duquel que l'on veut mettre à jour
                         Pour plus de précisions sur le contenu, voir description de "pattern",
                         dans le vocabulaire de maggenwa.py

        la fonction va modifier l'intérieur de genPattern.
        Tu veux que je te refasse l'intérieur, cochonne ? Et crac !! Ha ha haaa
        """

        #récupération du premier élément du pattern, contenant le prochain magicien à générer.
        #cet élément est un tuple de 2 sous-elem : le temps avant la génération,
        #et les infos nécessaires à la génération.
        nextMagiToGenerate = genPattern[0]

        #on diminue de 1 le premier élément de ce tuple (donc le temps avant la géné)
        nextMagiToGenerate[0] -= 1

        #bizarre. ce while 1, mais pourquoi pas ?
        while 1:

            #décomposition des deux éléments du tuple. (temps et infos)
            (nextMagiCounter, nextMagiparam) = nextMagiToGenerate

            #le temps avant la génération du prochain magicien n'est pas encore écoulé
            #(donc le temps pour les autres magi non plus, car c'est du temps cumulé)
            #on se casse, on n'a plus rien à faire.
            if nextMagiCounter > 0:
                return

            #on refile toutes les infos de générations à la fonction qui va bien.
            #Le magicien sera généré et placé dans le jeu.
            self.generateOneMagician(*nextMagiparam)

            #supression du pattern, de ce magicien généré.
            genPattern.pop(0)

            #si y'a plus de magiciens dans le pattern, on se casse.
            if len(genPattern) == 0:
                return

            #réactualisation du prochain magicien à générer.
            #ensuite, on va recommencer la boucle. On refait pas la diminution de
            #temps avant génération, pour ce magicien. Mais si son temps vaut initialement 0,
            #il sera tout de suite généré, et viré du pattern. Et le suivant aussi, etc...
            #Comme ça, si on a une suite de magicien avec un temps de 0, ils sont
            #tous générés dans le même cycle. Et c'est bien.
            nextMagiToGenerate = genPattern[0]


    def update(self):
        """
        mise à jour de tous les patterns en cours.
        Et génération des patterns de la prochaine Wave, si c'est le moment.
        """

        # --- génération des patterns de la nouvelle wave si c'est le moment. ---

        #si y'a encore du temps "normal" avant la prochaine Wave, on le diminue
        #(ce temps peut se faire diminuer d'un coup par la fonction takeStimuliNoMoreActiveMagi,
        #mais là on s'en fout, c'est pas le sujet.
        if self.counterNextWave > 0:

            self.counterNextWave -= 1

        else:

            #y'a plus de temps. (me fait penser à ma stupide chef : "on n'aaa pluuus de joouuurs")
            #bon, bref. on diminue le temps de bonus si il en reste.
            if self.presenceOfActiveMagi and self.counterBonusTime > 0:

                self.counterBonusTime -= 1

            else:

                #soit y'a plus de temps du tout, soit y'a plus de magiciens actifs.
                #dans tous les cas, faut balancer la prochaine Wave (que la précédente
                #ait été nettoyée ou pas, on s'en fout).

                #élaboration des patterns de la prochaine Wave, et du temps donné pour la nettoyer
                infoNextWave = self.magicianWaveGenerator.elaborateNextWave()
                (self.counterNextWave, listGenPatternNextWave) = infoNextWave

                #ajout des nouveaux patterns à ceux existants.
                self.listGenPattern += listGenPatternNextWave

                #du coup, maintenant, il y a des magiciens actifs
                self.presenceOfActiveMagi = True

        # --- gérage des patterns de génération de magicien ---

        #on vire les patterns de génération qui sont vides.
        self.listGenPattern = [ elem for elem in self.listGenPattern
                                if len(elem) > 0 ]

        #on parcourt la liste des patterns, pour les mettre à jour un par un.
        for genPattern in self.listGenPattern:
            self.updateGenPattern(genPattern)

