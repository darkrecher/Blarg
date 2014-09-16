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

TODO : Plus tard.

## Description du rôle de chaque classe ##

### game/Game ###

Classe principale gérant le jeu en lui-même. Contient la game loop.

### sprsimpl/SpriteSimple ###

Classe héritée de pygame.sprite.Sprite. Permet de gérer des sprites avec des mouvements simples (vitesse initiale + accélération), des enchaînements d'images simples (en boucle), et des conditions de "fin de vie" simples (au bout d'un certain temps, lorsqu'il est en dehors de l'écran). Il faut exécuter la méthode `update` à chaque cycle de jeu pour faire évoluer le sprite.

### sprsiman/SpriteSimpleManager ###

Contient une liste de `SpriteSimple`. Effectue leurs update, et les supprime de la liste lorsqu'ils sont arrivés en fin de vie.

### lamoche/Lamoche ###

Classe héritée de pygame.sprite.Sprite. Permet d'afficher un texte à l'écran. Je l'ai appelé "lamoche" pour faire une blague par rapport au mot "label". Voilà, c'est drôle.

### herobody/HeroBody ###

Héritée de pygame.sprite.Sprite. Affiche le corps du héros. Le choix de l'image à afficher se fait en appelant la méthode changeImg. C'est au code extérieur de décider quelle image afficher en fonction de ce qu'il se passe dans le jeu.

### herohead/HeroHead ###

Héritée de pygame.sprite.Sprite. Affiche la tête du héros. Gère un peu plus de choses que la classe HeroBody :

 - le tournage de tête à gauche et à droite : fonctions `turnHead`. (Appelée lorsque le héros meurt)
 - l'action de sourire : fonction `startSmiling` et `stopSmiling`. (Appelée lorsque le héros fait exploser un magicien en bouillie).
 - l'arrêt automatique du sourire au bout de quelques secondes : fonction `update`.

### cobulmag/CollHandlerBulletMagi ###

TODO : ce fichier contient plein d'explications sur les différents états du magicien, et comment il passe de l'un à l'autre.
Je ne sais pas si ça a sa place à cet endroit là. Le fait est que c'est à cet endroit là.

Exécute la fonction Magician.hitByBullet(Damage)

