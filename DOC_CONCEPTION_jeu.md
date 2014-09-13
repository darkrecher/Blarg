# Document de conception de Blarg (jeu) #

Ce document décrit la manière dont est organisé le code du jeu. Il ne décrit pas l'organisation du code du système de menu. Ce sera l'objet d'un autre document (pas encore fait).

## Introduction ##

Le code est assez densément commenté. Ce document se bornera donc à décrire rapidement le but de chaque classe, et la façon dont elles s'organisent entre elles.

Durant la réalisation de ce jeu, le PEP8 a été foulé aux pieds, écartelé, équarri, et humilié en place publique par des petits enfants jetant des cailloux. C'est la faute à l'entreprise dans laquelle je bossais à l'époque, qui m'a appris à coder en python avec les conventions de nommage du C++. Il va falloir faire avec !

## Lancement d'une partie ##

Au démarrage du programme, le système de menu est initialisé. Ensuite, lors du clic sur l'option "jouer" du menu principal, la fonction `mainclas.py/MainClass/mactPlaySeveralGames` est exécutée. Cette fonction démarre une partie, puis affiche l'écran de fin de partie (avec l'image du mec transformé en potion de mana), puis redémarre éventuellement une partie, et ainsi de suite.

Le jeu en lui-même, sans le système de menu, est entièrement géré par la classe `game.py/Game`. Pour démarrer une partie, il faut exécuter les fonctions suivantes :

    # exécuté dans MainClass.__init__
    # instanciation
    self.theGame = Game(self.screen, self.scoreManager, self.fontDefault)
    # chargement des images, et autres trucs.
    self.theGame.loadGameStuff()

    # exécuté dans MaiClass.mactPlaySeveralGames
    self.theGame.playOneGame(self.archivist.dicKeyMapping, dogDom)

Les paramètres nécessaires sont les suivants :

 - `self.screen` : objet `pygame.surface.Surface`. Représente l'écran sur lequel s'affichera le jeu.

 - `self.scoreManager` : classe stockant le score de la partie en cours. Permet de récupérer le score final à la fin de la partie.

 - `self.fontDefault` : objet `pygame.font.Font`. Police de caractère utilisé pour afficher les textes durant le jeu. (principalement le score).

 - `self.archivist.dicKeyMapping` : dictionnaire effectuant la correspondance entre des touches du clavier, et les actions du joueur. (définissable par le joueur, via le menu de configuration).

 - `dogDom` : booléen indiquant si le mode invincible est activé ou pas.

## Diagramme de classe. ##

plus tard.