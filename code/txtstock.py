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

date de la dernière relecture-commentage : 01/03/2011

classe de stockage de données, qui contient tous les textes, en anglais et en françay

dérogation spéciale pour ce fichier. Les lignes de code peuvent dépasser 79 caractères.
Car c'est que du texte, et ce serait super chiant de découper ça en plusieurs lignes.
C'est déjà assez moche comme ça à lire.
"""

from common import LANG_FRENCH, LANG_ENGL, LANG_DEFAULT, NAME_HERO



class TextStock():
    """
    tous les textes du jeu.
    """

    #Identifiants de tous les textes utilisés dans le jeu.
    #je les déclare tous à l'intérieur de la classe. Comme ça, le code extérieur pourra
    #les utiliser directement, sans les importer une par une. Parce que ce serait lourdingue.
    #Je détaille pas la signification de chacun de ces identifiants. Ca se devine plus ou moins
    #facilement en regardant à quelles chaînes de caractères ils sont associés. (Voir plus loin).

    (
     #menu principal
     MAIN_PLAY,
     MAIN_CREDITS,
     MAIN_QUIT,
     MAIN_RECHER,
     MAIN_INTRO,
     MAIN_CONFIG,
     MAIN_HISCORE,
     MAIN_DOGDOM,
     MAIN_FULLSCR,
     #menu affichant le héros mort, transformé en potion de mana.
     DEAD_PHRASE_1,
     DEAD_PHRASE_2,
     DEAD_BURST,
     DEAD_KILL,
     DEAD_SCORE,
     DEAD_KEYS,
     #menu avec tout le blabla des crédits.
     CRED_T_BLA,
     CRED_CLICK,
     CRED_INDIE,
     CREDL_INDIE,
     CRED_BLOG,
     CREDL_BLOG,
     CRED_42,
     CREDL_42,
     CRED_TWIT,
     CREDL_TWIT,
     CRED_T_DONAT,
     CRED_ST_DONAT1,
     CRED_DONAT_FK,
     CREDL_DONAT_FK,
     CRED_ST_DONAT2,
     CRED_DONAT_KA,
     CRED_ST_DONAT3,
     CRED_DONAT_CU,
     CRED_DONAT_CO,
     CRED_DONAT_CS,
     CREDL_DONAT_CS,
     CRED_DONAT_CM,
     CREDL_DONAT_CM,
     CRED_DONAT_LA,
     CREDL_DONAT_LA,
     CRED_PYG,
     CREDL_PYG,
     CRED_YOU,
     CRED_ULULE,
     CREDL_ULULE,
     CRED_T_OTHER,
     CRED_YUSU,
     CREDL_YUSU,
     CRED_LIC_1,
     CRED_LIC_2,
     CRED_LIC_3,
     CRED_LAL,
     CREDL_LAL,
     CRED_CC_1,
     CRED_CC_2,
     CREDL_CC,
     #menu demandant au joueur d'entrer son nom
     ENTER_NAME,
     #menu du ha ha ha scénario
     STORY_01,
     STORY_02,
     STORY_03,
     STORY_04,
     STORY_05,
     STORY_SURVIVE,
     STORY_SCRL_01,
     STORY_SCRL_02,
     STORY_SCRL_03,
     STORY_DO_STHG,
     #menu affichant le ha ha ha manuel du jeu
     MANUAL_MOVE,
     MANUAL_FIRE,
     MANUAL_RELOAD,
     #menu de configuration du jeu
     CONFIG_CLICK_1,
     CONFIG_CLICK_2,
     CONFIG_RESET,
     CONFIG_EXIT,
     CONFIG_SOUND,
     #menu des high scores et des statistiques.
     STAT_ALL_KILL,
     STAT_ALL_BURST,
     STAT_HI_SCORE,
     STAT_HI_KILL,
     STAT_HI_BURST,
     STAT_SEP,
     #animation de présentation du début.
     PREZ_LOADING,
     #menu qui vient juste après le choix du nom. Où on explique que le nom sert à rien.
     NAME_LIE_NORM_1,
     NAME_LIE_NORM_2,
     NAME_LIE_DOG_1,
     NAME_LIE_DOG_2,
    ) = range(86)

    #atation, l'ordre c'est français, puis anglais. Je me suis permis de l'écrire dans
    #une liste ordonnée, plutôt que de le déclarer sous forme de sous-dico,
    #car ça m'aurait fait répéter 10 000 fois les clés LANG_ENGL et LANG_FRENCH.
    #Si on met un seul elem, ça veut dire que l'anglais est pareil que le français
    DICT_LANGUAGE_LIST = {

     #menu principal

     MAIN_PLAY      : (u"JOUER",                      u"PLAY", ),
     MAIN_CREDITS   : (u"CREDITS",                    u"CREDITS", ),
     MAIN_QUIT      : (u"QUITTER",                    u"QUIT", ),
     MAIN_DOGDOM    : (u"EDOM EDOG"[::-1], ),
     MAIN_RECHER    : (u"Créé par Réchèr :",          u"Created by Réchèr :", ),
     MAIN_INTRO     : (u"INTRO",                      u"INTRO", ),
     MAIN_CONFIG    : (u"CONFIG",                     u"CONFIG", ),
     MAIN_HISCORE   : (u"HIGH SCORES",                u"HIGH SCORES", ),
     MAIN_FULLSCR   : (u"plein écran",                u"full screen", ),


     #menu affichant le héros mort, transformé en potion de mana.

     DEAD_PHRASE_1  : (u"Vous êtes mooorrrt !!",
                       u"You are deeeaaaad !!", ),

     DEAD_PHRASE_2  : (u"Vous avez été transformé en potion de mana.",
                       u"You were transformed in a mana potion.", ),

     DEAD_BURST     : (u"Nombre de magiciens explosés : ",
                       u"Number of magicians burst :", ),

     DEAD_KILL      : (u"Total de magiciens tués : ",
                       u"Total magicians killed :", ),

     DEAD_KEYS      : (u"Entrée : rejouer.   Esc : quitter",
                       u"Enter : play again.   Esc : quit", ),

     DEAD_SCORE     : (u"Score : ", ),

     #menu avec tout le blabla des crédits.

     CRED_T_BLA     : (u" --- MOI --- ",              u" --- ME --- ", ),

     CRED_CLICK     : (u"(Cliquez sur les liens pour augmentez mon ego)",
                       u"(Click on the links to increment my ego", ),

     CRED_INDIE     : (u"Moi et ce jeu dans IndieDb: ",
                       u"Me and that game in IndieDb:", ),

     CRED_ULULE     : (u"Moi et ce jeu dans Ulule:",
                       u"Me and that game in Ulule:"),

     CRED_BLOG      : (u"Moi et mon blog: ",
                       u"Me and my blog:", ),

     CRED_42        : (u"Moi et d'autres, dans un geekzine: ",
                       u"Me and others, in a geekzine:", ),

     CRED_TWIT      : (u"Moi en poudre instantanée: ",
                       u"Me, in instant powder:", ),

     CREDL_INDIE    : (u"http://indiedb.com/members/recher", ),
     CREDL_BLOG     : (u"http://recher.wordpress.com", ),
     CREDL_42       : (u"http://42lemag.fr", ),
     CREDL_TWIT     : (u"http://twitter.com/_Recher_", ),
     CREDL_ULULE    : (u"http://ulule.fr/blarg",            u"http://ulule.com/blarg", ),

     CRED_T_DONAT   : (u" --- PERSONNES DE QUALITE AYANT FAIT UN DON --- ",
                       u" ---   GREAT MAJESTIC PERSONS WHO DONATED   --- ", ),

     CRED_ST_DONAT1 : (u"--- assistant aux effets sonores ---",
                       u"--- sound effect assistant ---"),
     CRED_DONAT_FK  : (u"Ckyfran, qui vous conseille:",
                       u"Ckyfran, who recommends:"),
     CREDL_DONAT_FK : (u"http://jeanbamin.com", ),
     CRED_ST_DONAT2 : (u"--- super-donateuse ---",
                       u"--- super-donatorette ---"),
     CRED_DONAT_KA  : (u"Ceska2007", ),
     CRED_ST_DONAT3 : (u" --- joyeux mécènes ---",
                       u"--- joyesque donators ---"),
     CRED_DONAT_CU  : (u"Cuningham", ),
     CRED_DONAT_CO  : (u"Le Corse", ),
     CRED_DONAT_CS  : (u"Captive Studio", ),
     CREDL_DONAT_CS : (u"http://www.captive-studio.com/", ),
     CRED_DONAT_CM  : (u"cemonsieur", ),
     CREDL_DONAT_CM : (u"http://www.ulule.com", ),
     CRED_DONAT_LA  : (u"Platypus Creation", ),
     CREDL_DONAT_LA : (u"http://www.platypus-creation.com", ),

     CRED_YOU       : (u"Et vous bien sûr !! qui contribuerez à mes prochains jeux !!",
                       u"And you, of course !! Give me your money for my next game !", ),

     CRED_T_OTHER   : (u" --- AUTRES TRUCS SUPERS --- ",
                       u" ---  OTHER COOL THINGS  --- ", ),

     CRED_YUSU      : (u"Police de caractère youpi:",
                       u"yeepeeeh fonts:", ),

     CREDL_YUSU     : (u"http://p.yusukekamiyamane.com", ),

     CRED_PYG       : (u"Ce jeu a été créé avec pygame:",
                       u"Game created with pygame:", ),

     CREDL_PYG      : (u"http://pygame.org", ),

     CRED_LIC_1     : (u"Copyright 2010 Réchèr", ),

     CRED_LIC_2     : (u"Le code source, les sons et les images sont disponible, au choix,",
                       u"The source code, the images and the sounds are available", ),

     CRED_LIC_3     : (u"sous la licence Art Libre, ou la licence CC-BY-SA.",
                       u"under the Free Art License, or the CC-BY-SA", ),

     CRED_LAL       : (u"Copyleft Attitude:", ),

     CREDL_LAL      : (u"http://www.artlibre.org",
                       u"http://artlibre.org/licence/lal/en"),

     CRED_CC_1      : (u"Creative Commons - Paternité - ",
                       u"Creative Commons - Attribution - ", ),

     CRED_CC_2      : (u"Partage des Conditions Initiales à l'Identique 2.0 France",
                       u"              ShareAlike 2.0 France !!!", ),

     CREDL_CC       : (u"http://creativecommons.org/licenses/by-sa/2.0/fr/deed.fr",
                       u"http://creativecommons.org/licenses/by-sa/2.0/fr/deed.en", ),

     #menu demandant au joueur d'entrer son nom

     ENTER_NAME     : (u"Entrez votre nom :",         u"Enter your name :", ),

     #menu du ha ha ha scénario

     STORY_01       : (u"Vous êtes " + NAME_HERO + u", un vendeur de fusil à pompe",
                       u"You are " + NAME_HERO + u", a honest shotgun seller,", ),

     STORY_02       : (u"tout ce qu'il y a de plus honnête.",
                       u"the best in your county.", ),

     STORY_03       : (u"Un jour, vous êtes mystérieusement télétransportagé",
                       u"One day, you are mysteriously teletransportwhouffed", ),

     STORY_04       : (u"dans un univers parallèle remplis de magiciens dopés aux amphétamines,",
                       u"in a parallel universe full of steroized mad magicians,", ),

     STORY_05       : (u"qui veulent vous transformer en potion de mana.",
                       u"who want to transform you into a mana potion."),

     STORY_SURVIVE  : (u"Combien de temps pourrez-vous survivre ?",
                       u"How long will you survive ?"),

     STORY_SCRL_01  : (u"Note importante : ",
                       u"Important note :"),

     STORY_SCRL_02  : (u"Dans Star Wars, le scrolling de l'intro n'avait d'égal que la bande-son.",
                       u"In Star Wars, the intro scrolling was as cool as the musics."),

     STORY_SCRL_03  : (u"Pour ce jeu, c'est exactement pareil.",
                       u"In that game, it's exactly the same."),

     STORY_DO_STHG  : (u"Appuyez sur une touche ou cliquez pour continuer.",
                       u"To continue, press a key, or click."),

     #menu affichant le ha ha ha manuel du jeu

     MANUAL_MOVE    : (u"MOUVEMENT",                  u"MOVEMENT"),
     MANUAL_FIRE    : (u"PAN !!",                     u"FIRE"),
     MANUAL_RELOAD  : (u"RECHARGER",                  u"RELOAD"),

     #menu de configuration du jeu

     CONFIG_CLICK_1 : (u"Cliquez sur une touche à l'écran pour la modifier, ",
                       u"Click a key on the screen to modify it,", ),

     CONFIG_CLICK_2 : (u"puis appuyez sur la touche du clavier.",
                       u"then, press the corresponding key.", ),

     CONFIG_RESET   : (u"Remettre config par défaut",
                       u"Reset to default config", ),

     CONFIG_EXIT    : (u"Echap : sauver et quitter",
                       u"Esc : save and quit", ),

     CONFIG_SOUND   : (u"SON",                        u"SOUND", ),

     #menu des high scores et des statistiques.

     STAT_ALL_KILL  : (u"Total tués :",               u"Total kills :", ),
     STAT_ALL_BURST : (u"Total explosés :",           u"Total bursts :", ),
     STAT_HI_SCORE  : (u"Meilleur score :",           u"High score :", ),

     STAT_HI_KILL   : (u"Plus grand nombre de magiciens tués :",
                       u"Highest number of magiicians killed :", ),

     STAT_HI_BURST  : (u"Plus grand nombre de magiciens explosés :",
                       u"Highest number of magicians burst :", ),

     STAT_SEP       : (u"-" * 90, ),

     #animation de présentation du début.

     PREZ_LOADING   : (u"LOADINGE",                   u"LOADING"),

     #menu qui vient juste après le choix du nom. Où on explique que le nom sert à rien.
     #pas besoin de la traduction en anglais. Ce menu ne s'affiche qu'au début du jeu,
     #et au début, c'est en français, par défaut. Désolé pour nos amis rosbifs. Sorry, people.

     #mini-obfuscation. C'est écrit à l'envers. Hu hu hu.
     NAME_LIE_DOG_1 : (u"! edoM edoG el éuqolbéd zeva suoV ! snoitaticiléF"[::-1],),
     NAME_LIE_DOG_2 : (u"! uoy kcuf : noniS ! icrem : aç ruop éyap zeva suov iS"[::-1],),
     NAME_LIE_NORM_1: (u"En fait on s'en fout de votre nom à vous.",),
     NAME_LIE_NORM_2: (u"Le héros s'appelle " + NAME_HERO + u". C'est ça l'important.",),
    }


    def __init__(self):
        """
        constructeur. (thx captain obvious)
        """

        #initialisation du langage courant. Le langage par défaut c'est le français.
        self.language = LANG_DEFAULT

        #dictionnaire qui contiendra les textes du jeu, mais sous forme de dictionnaire, donc.
        #clé : identifiants de texte
        #valeur : sous-dictionnaire :
        #         clé : identifiants de langage. LANG_FRENCH ou LANG_ENGL
        #         valeur : chaîne de caractère unicode avec le texte dedans.
        self.DICT_LANGUAGE = {}

        #construction de self.DICT_LANGUAGE à partir de DICT_LANGUAGE_LIST
        #chaque élément de la liste crée un élément du dictionnaire.
        for idText, tupleTextLanguage in TextStock.DICT_LANGUAGE_LIST.items():

            if len(tupleTextLanguage) == 1:
                #le tuple de texte ne contient qu'une seul chaîne de caractère.
                #On l'utilise pour le français et l'anglais.
                frenchText = tupleTextLanguage[0]
                englishText = tupleTextLanguage[0]
            else:
                #le tuple contient deux chaînes de caractères, pour le français, et l'anglais.
                frenchText, englishText = tupleTextLanguage

            #création du sous-dictionnaire, et rangement dans le gros dico global.
            self.DICT_LANGUAGE[idText] = { LANG_FRENCH : frenchText,
                                           LANG_ENGL   : englishText }


    def changeLanguage(self, newLanguage):
        """
        change le langage courant.

        entrées :
            newLanguage. identifiants du nouveau langage. LANG_FRENCH ou LANG_ENGL.
        """
        self.language = newLanguage


    def getText(self, idText):
        """
        récupère un texte, selon l'identifiant donné, et le langage courant.

        entrées :
            idText. identifiant du texte à récupérer.

        plat-dessert :
            chaîne unicode, contenant le texte.
        """
        return self.DICT_LANGUAGE[idText][self.language]


#paf, instanciation à l'arrache. J'aime pas trop faire comme ça. Mais c'est quand même
#vachement plus simple que d'instancier la classe quelque part et de la passer en param
#à tout le monde qu'en a besoin. Et comme en plus tout les textes sont définis sur place
#(pas de chargement de fichier à faire), eh ben on a le droit.
txtStock = TextStock()
