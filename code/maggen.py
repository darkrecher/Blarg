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

date de la derni�re relecture-commentage : 30/09/2010

Classe qui g�n�re les magiciens. Chapeaute le maggenwa, maggenlc et hardmana.
Comme dirait Alexandre Astier : c'est moi qui chapeaute un peu tout le ...

La classe prend les patterns g�n�r�s par le MagicianWaveGenerator, et s'occupe de
cr�er les instances de magiciens et de les placer dans le jeu.
La classe s'occupe �galement de demander une nouvelle Wave lorsque c'est le moment.
"""

import magician
import magiline
import magirand

from maggenwa import MagicianWaveGenerator, MAGI_BASE, MAGI_RAND, MAGI_LINE

from yargler import theSoundYargler, SND_MAG_APPEAR

#dico de correspondance entre le type de magicien, et la fonction constructeur pour le cr�er.
DIC_MAGIC_CONSTRUCTOR = {
  MAGI_BASE : magician.Magician,
  MAGI_RAND : magirand.MagiRand,
  MAGI_LINE : magiline.MagiLine,
}

#delay maximum entre deux wave. M�me si le joueur a tu� tous les monstres d'une wave,
#on attend ce temps (nbr de cycle) pour g�n�rer la prochaine.
#Par cons�quent, ce temps ne sera pas utilis� pour alimenter le temps de bonus ou l'antiHarM
DELAY_MAX_BETWEEN_WAVE = 70

#coef de conversion entre le temps restant � la fin de la destruction d'une wave,
#et l'antiHarM offert pour ce temps. 3 cycles de temps donnent 1 point de antiHarM
COEF_CONVERSION_HARM_FROM_TIME = 3


class MagicianGenerator():
    """
    classe qui g�re la cr�ation des magiciens (de tout poil) (hahaha).
    """

    def __init__(self, groupMagicianAppearing,
                 dicMagicienImg, spriteSimpleGenerator, hero):
        """
        constructeur. (thx captain obvious)

        entr�e :
            groupMagicianAppearing : groupe de sprite, dans lequel on place les
                 magiciens nouvellement cr��s.

            dicMagicienImg : dictionnaire de correspondance entre les images et les
                identifiants d'image d'un magicien.
                Ce param�tre n'est pas r�ellement utilis� par cette classe.
                Il est juste transmis aux constructeurs des magicens.

            spriteSimpleGenerator : classe �ponyme. Permet de g�n�rer des sprites simples
                Ce param�tre n'est pas r�ellement utilis� par cette classe.
                Il est juste transmis aux constructeurs des magicens.

            hero : r�f�rence vers le h�ros. C'est juste pour choper ses coordonn�es.
                 le param�tre est transmis directement au waveGenerator lors de sa cr�ation.
        """

        self.groupMagicianAppearing = groupMagicianAppearing
        self.dicMagicienImg = dicMagicienImg
        self.spriteSimpleGenerator = spriteSimpleGenerator

        #liste des premiers param�tres � transmettre aux fonctions constructeurs de magi.
        #les param suivants ne sont pas fixes, donc on les fabriquera le moment venu.
        self.paramGeneration = (self.dicMagicienImg,
                                self.spriteSimpleGenerator)

        #liste des pattern de g�n�ration de magicien en cours. La classe d�pile le
        #contenu de tous les patterns de la liste au fur � mesure du temps, et g�n�re
        #les magiciens en fonction des infos indiqu�es dans le pattern.
        self.listGenPattern = []

        #num�ro de la Wave en cours / Nombre de Wave d�j� g�n�r�e.
        self.indexCurrentWave = 0

        #classe permettant d'�laborer les diff�rents patterns de magiciens,
        #� chaque nouvelle Wave, en fonction du HardMana qu'elle poss�de.
        self.magicianWaveGenerator = MagicianWaveGenerator(hero)

        #temps restant avant la prochaine Wave (nbre de cycle)
        self.counterNextWave = 0

        #temps de bonus, accumul� gr�ce au temps non utilis� par le joueur, lorsqu'il a
        #d�truit tous les magiciens actifs d'une Wave avant le temps imparti.
        #Le temps de bonus est d�pens� lorsqu'il n'y a plus de temps avant la prochaine
        #Wave. Pour obtenir une rallonge de temps.
        self.counterBonusTime = 0

        #Boolean. Indique si il y a encore des magiciens actifs dans le jeu.
        #magicien actif = un magicien vivant, et qui se d�place.
        #La prochaine Wave est lanc�e lorsqu'il n'y a plus de magicien actifs.
        self.presenceOfActiveMagi = False


    def generateOneMagician(self, magiType, posStart, posEnd=None, level=1):
        """
        g�n�re un magicien et le place sur l'aire de jeu.

        ent�es :
            magiType : type du magicien : MAGI_BASE, MAGI_LINE, MAGI_RAND
            posStart : Rect. Coordonn�es de d�part du magicien.
            posEnd   : Rect. Utile seulement pour les MAGI_LINE.
                       Coordonn�e d'arriv�e du magicien.
                       (le MAGI_LINE se d�place de son d�part jusqu'� son arriv�e)
            level    : niveau du magicien
        """

        #rassemblement des param�tres, en fonction du type du magicien.
        #(pas besoin du posEnd si on doit faire un MAGI_LINE)
        if magiType == MAGI_LINE:
            param = self.paramGeneration + (posStart, posEnd, level)
        else:
            param = self.paramGeneration + (posStart, level, )

        #r�cup�ration de la fonction permettant de cr�er le magicien, selon son  type
        funcMagiConstructor = DIC_MAGIC_CONSTRUCTOR[magiType]

        #appel de la bonne fonction avec la bonne liste de param. Youpi.
        newMagician = funcMagiConstructor(*param)

        #son d'apparition de magicien : zwwwzzwwouuuww !!
        theSoundYargler.playSound(SND_MAG_APPEAR)

        #ajout du magicien dans le spriteGroup de magicien-qui-apparaissent.
        #Le code ext�rieur se d�merde pour le transf�rer dans le spriteGroup des
        #vrais magiciens, le moment venu. Et pour g�rer tout le reste du bordel.
        self.groupMagicianAppearing.add(newMagician)


    def takeStimuliNoMoreActiveMagi(self):
        """
        fonction ex�cut�ee par le code ext�rieur. Permet d'indiquer � cette
        classe qu'il n'y a plus aucun magicien actifs dans l'aire de jeu.
        (voir bla-bla de la fonction Game.isMagicianActive pour une d�finition de "magicien actif")
        """

        #Le stimuli a d�j� �t� pris en compte. On se casse tout de suite
        if self.presenceOfActiveMagi == False:
            return

        #enregistrement du stimuli
        self.presenceOfActiveMagi = False

        #On v�rifie si le temps restant est suffisant pour accorder du bonus.
        #Dans le cas contraire, on ne fera rien, et on attendra la prochaine wave
        #comme normalement.
        if self.counterNextWave > DELAY_MAX_BETWEEN_WAVE:

            #le joueur a pu tuer les magiciens en beaucoup moins de temps que ce qui
            #lui �tait accord�. On calcule son bonus de temps
            waveTimeBonus = self.counterNextWave - DELAY_MAX_BETWEEN_WAVE

            #Maintenant qu'on a pris le bonus, on peut diminuer le temps avant
            #la prochaine wave, pour qu'il soit au strict minimum
            self.counterNextWave = DELAY_MAX_BETWEEN_WAVE

            #utilisation de ce temps de bonus pour obtenir de l'antiHarM, qui est
            #envoy� au WaveGenerator. L'antiHarM est un debuff, qui va rendre la/les
            #prochaines waves plus faciles que pr�vus (moins de magi, moins de pattern, ...)
            antiHarMBonus = waveTimeBonus / COEF_CONVERSION_HARM_FROM_TIME
            self.magicianWaveGenerator.receiveAntiHarMBonus(antiHarMBonus)

            #et en plus, utilisation de ce temps de bonnus pour alimenter le temps cumul�
            #de bonus. Ce temps est utilis� en dernier recours, lorsque le joueur n'a
            #pas tu� tous les magiciens et qu'il faudrait lancer la prochaine wave.
            self.counterBonusTime += waveTimeBonus


    def updateGenPattern(self, genPattern):
        """
        mise � jour de l'un des pattern en cours.

        entr�es :
            genPattern : pattern de g�n�ration de magicien dont duquel que l'on veut mettre � jour
                         Pour plus de pr�cisions sur le contenu, voir description de "pattern",
                         dans le vocabulaire de maggenwa.py

        la fonction va modifier l'int�rieur de genPattern.
        Tu veux que je te refasse l'int�rieur, cochonne ? Et crac !! Ha ha haaa
        """

        #r�cup�ration du premier �l�ment du pattern, contenant le prochain magicien � g�n�rer.
        #cet �l�ment est un tuple de 2 sous-elem : le temps avant la g�n�ration,
        #et les infos n�cessaires � la g�n�ration.
        nextMagiToGenerate = genPattern[0]

        #on diminue de 1 le premier �l�ment de ce tuple (donc le temps avant la g�n�)
        nextMagiToGenerate[0] -= 1

        #bizarre. ce while 1, mais pourquoi pas ?
        while 1:

            #d�composition des deux �l�ments du tuple. (temps et infos)
            (nextMagiCounter, nextMagiparam) = nextMagiToGenerate

            #le temps avant la g�n�ration du prochain magicien n'est pas encore �coul�
            #(donc le temps pour les autres magi non plus, car c'est du temps cumul�)
            #on se casse, on n'a plus rien � faire.
            if nextMagiCounter > 0:
                return

            #on refile toutes les infos de g�n�rations � la fonction qui va bien.
            #Le magicien sera g�n�r� et plac� dans le jeu.
            self.generateOneMagician(*nextMagiparam)

            #supression du pattern, de ce magicien g�n�r�.
            genPattern.pop(0)

            #si y'a plus de magiciens dans le pattern, on se casse.
            if len(genPattern) == 0:
                return

            #r�actualisation du prochain magicien � g�n�rer.
            #ensuite, on va recommencer la boucle. On refait pas la diminution de
            #temps avant g�n�ration, pour ce magicien. Mais si son temps vaut initialement 0,
            #il sera tout de suite g�n�r�, et vir� du pattern. Et le suivant aussi, etc...
            #Comme �a, si on a une suite de magicien avec un temps de 0, ils sont
            #tous g�n�r�s dans le m�me cycle. Et c'est bien.
            nextMagiToGenerate = genPattern[0]


    def update(self):
        """
        mise � jour de tous les patterns en cours.
        Et g�n�ration des patterns de la prochaine Wave, si c'est le moment.
        """

        # --- g�n�ration des patterns de la nouvelle wave si c'est le moment. ---

        #si y'a encore du temps "normal" avant la prochaine Wave, on le diminue
        #(ce temps peut se faire diminuer d'un coup par la fonction takeStimuliNoMoreActiveMagi,
        #mais l� on s'en fout, c'est pas le sujet.
        if self.counterNextWave > 0:

            self.counterNextWave -= 1

        else:

            #y'a plus de temps. (me fait penser � ma stupide chef : "on n'aaa pluuus de joouuurs")
            #bon, bref. on diminue le temps de bonus si il en reste.
            if self.presenceOfActiveMagi and self.counterBonusTime > 0:

                self.counterBonusTime -= 1

            else:

                #soit y'a plus de temps du tout, soit y'a plus de magiciens actifs.
                #dans tous les cas, faut balancer la prochaine Wave (que la pr�c�dente
                #ait �t� nettoy�e ou pas, on s'en fout).

                #�laboration des patterns de la prochaine Wave, et du temps donn� pour la nettoyer
                infoNextWave = self.magicianWaveGenerator.elaborateNextWave()
                (self.counterNextWave, listGenPatternNextWave) = infoNextWave

                #ajout des nouveaux patterns � ceux existants.
                self.listGenPattern += listGenPatternNextWave

                #du coup, maintenant, il y a des magiciens actifs
                self.presenceOfActiveMagi = True

        # --- g�rage des patterns de g�n�ration de magicien ---

        #on vire les patterns de g�n�ration qui sont vides.
        self.listGenPattern = [ elem for elem in self.listGenPattern
                                if len(elem) > 0 ]

        #on parcourt la liste des patterns, pour les mettre � jour un par un.
        for genPattern in self.listGenPattern:
            self.updateGenPattern(genPattern)

