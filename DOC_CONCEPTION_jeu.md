# Document de conception de Blarg (jeu) #

Ce document décrit la manière dont est organisé le code du jeu. Le code du système d'interface (menu principal, config, ...) sera décrit dans un autre document, qui n'est pas encore fait.

## Introduction ##

Le code est assez densément commenté. Ce document se bornera donc à décrire sommairement le but de chaque classe.

Durant la réalisation de ce jeu, le PEP8 a été foulé aux pieds, écartelé, équarri et humilié en place publique par des petits enfants jetant des cailloux. C'est la faute à l'entreprise dans laquelle je bossais à l'époque, qui m'a appris à coder en python avec les conventions de nommage du C++. Il va falloir faire avec !

## Lancement d'une partie ##

Au démarrage du programme, le système d'interface est initialisé. Ensuite, lors du clic sur l'option "jouer" du menu principal, la fonction `MainClass.mactPlaySeveralGames` du fichier `mainclas.py` est exécutée. Cette fonction effectue les actions suivantes :

 - Jouer une partie.
 - Afficher l'écran de fin de partie (avec le héros transformé en potion de mana)
 - Éventuellement, redémarrer une partie, et ainsi de suite.

Le jeu en lui-même, sans l'interface, est géré par la classe `game.py/Game`. Pour démarrer une partie, les fonctions suivantes sont exécutées :

    # Instanciation (appelée par MainClass.__init__)
    self.theGame = Game(self.screen, self.scoreManager, self.fontDefault)
    # Chargement des images et d'autres trucs.
    self.theGame.loadGameStuff()
    # Démarrage (appelé par MainClass.mactPlaySeveralGames)
    self.theGame.playOneGame(self.archivist.dicKeyMapping, dogDom)

Les paramètres nécessaires sont les suivants :

 - `self.screen` : objet `pygame.surface.Surface`. Représente l'écran sur lequel s'affichera le jeu.

 - `self.scoreManager` : classe stockant le score de la partie en cours. Permet de récupérer le score final à la fin de la partie.

 - `self.fontDefault` : objet `pygame.font.Font`. Police de caractère utilisé pour afficher tous les textes durant le jeu. (en fait, il n'y a que le score à afficher).

 - `self.archivist.dicKeyMapping` : dictionnaire effectuant la correspondance entre des touches du clavier et les actions. Il est défini par le joueur, dans le menu de configuration.

 - `dogDom` : booléen indiquant si le mode invincible est activé ou pas.

## Diagramme de classe. ##

TODO : Plus tard.
(le scoreManager et l'archivist sont liés)

## Description du rôle de chaque classe ##

### game/Game ###

Classe principale gérant le jeu en lui-même. Contient la game loop.

### sprsimpl/SpriteSimple ###

Classe héritée de `pygame.sprite.Sprite`. Permet de gérer des sprites avec des mouvements simples (vitesse initiale + accélération), des enchaînements d'images simples (en boucle), et des conditions de destruction simples (après x boucles / en quittant l'écran). Il faut exécuter la méthode `update` à chaque cycle de jeu pour faire évoluer le sprite.

### sprsiman/SpriteSimpleManager ###

Contient une liste de `SpriteSimple`. Effectue leurs update, et les supprime de la liste lorsqu'ils sont arrivés en fin de vie.

### lamoche/Lamoche ###

Classe héritée de `pygame.sprite.Sprite`. Permet d'afficher un texte à l'écran. Je l'ai appelé "lamoche" pour faire une blague par rapport au mot "label". Voilà, c'est drôle.

Cette classe est également utilisée dans le système d'interface.

### herobody/HeroBody ###

Héritée de `pygame.sprite.Sprite`. Affiche le corps du héros. Le choix de l'image à afficher se fait en appelant la méthode `changeImg`. C'est au code extérieur de décider quelle image afficher en fonction de ce qu'il se passe dans le jeu.

### herohead/HeroHead ###

Héritée de `pygame.sprite.Sprite`. Affiche la tête du héros. Elle est d'un niveau un peu plus haut que la classe `HeroBody`, et gère donc un peu plus de choses :

 - Tournage de tête à gauche et à droite : fonction `turnHead`. (Appelée lorsque le héros meurt)
 - Sourire : fonction `startSmiling` et `stopSmiling`. (Appelées lorsque le héros fait exploser un magicien en bouillie).
 - Arrêt automatique du sourire au bout de quelques secondes : fonction `update`.

### cobulmag/CollHandlerBulletMagi ###

 - Calcul de la trajectoire des balles tirées par le héros. À chaque tir, il y en a 3 qui partent : une un peu vers le haut, une tout droit, et une un peu vers le bas. Elles ont une vitesse instantanée.

 - Gestion des collisons entre les balles et les magiciens.

Lorsqu'une balle touche un magicien, cette classe exécute la fonction `Magician.hitByBullet(Damage)`. La valeur renvoyée indique l'état du magicien  (vivant/tué/explosé). La classe renvoie le nombre total de magiciens tués et explosés par le tir.

D'autre part, ce fichier de code contient des explications détaillées sur les différents états d'un magicien, et les passages d'un état à un autre.
Je ne sais pas si ça a sa place à cet endroit, mais c'est ainsi. Tralalali.

### cohermag/CollHandlerHeroMagi ###

Gestion des collisions entre le héros (tête + corps) et les magiciens.

Lorsqu'une collision a lieu, on envoie le stimuli `takeStimuliHurt(theMagician.rect)` au héros, et le stimuli `TakeStimuliTouchedHero()` au magicien.

Lorsque le héros reçoit un stimuli de collision, il se met immédiatement dans l'état `HURT`. On ne lui envoie pas d'autres stimuli de collision tant qu'il reste dans cet état. Cela permet d'éviter que le héros se fasse toucher plusieurs fois en peu de temps, ce qui ne serait pas très gentil pour le joueur.

### scoremn/ScoreManager ###

Récupère les stats d'un joueur à partir d'une classe `Archivist` (la classe qui gère le fichier de sauvegarde). Ces stats comprennent les high scores, ainsi que le nombre total de magiciens tués et explosés.

Au fur et à mesure de la partie, récupère le nombre de magiciens explosés, et le nombre de magiciens tués sans être explosé. Met à jour le score de la partie en cours, les high scores, et les nombres totaux en fonction.

À la fin de la partie, renvoie à l'archivist les stats mises à jour, qui les enregistrera dans le fichier.

### ammoview/AmmoViewer ###

Affiche les cartouches à gauche de l'écran, et gère leurs animations :

 - reload : le héros vient de recharger. Une cartouche supplémentaire est affichée en bas de la pile.
 - fire : la balle la plus haute disparaît, et un nuage de fumée est dessiné. La douille reste.
 - rearm : la douille tout en haut, ainsi que toutes les autres cartouches de la pile, sont déplacées progressivement vers le haut. À la fin, la douille du haut disparaît.

Ces événements sont provoqués par le code extérieur, qui appelle les fonctions correspondantes. (`takeStimuliFire`, `takeStimuliRearm`, `takeStimuliReload`).

La classe contient des fonctions à appeler à chaque cycle, pour faire jouer les animations des cartouches, ajouter/enlever celles qui se rechargent, celles qui sont tirées, etc. Le blabla en début de fichier me semble suffisamment clair à ce sujet.

### lifeview/LifePointViewer ###

Affiche les points de vie du joueur, en haut à gauche de l'écran (sous forme d'image représentant des vestes en jean, parce que c'est rigolo).

Reçoit un stimuli lorsque le héros perd un point de vie, et fait clignoter une veste en jean, pour la faire disparaître progressivement. Le "progressivement" étant un peu aléatoire, pour faire quelque chose de joli et classe. Le fonctionnement détaillé du clignotement est expliqué au début du fichier.

Le code extérieur doit donc appeler, à chaque cycle, une fonction determineIsUpdatingSthg, pour savoir si il y a un clignotement en cours, et appeler update, pour gérer cedit clignotement.

Cette classe ne gère pas la mort du héros, lorsqu'il n'a plus de point de vie. Elle ne prévient pas le code extérieur le héros n'a plus de points de vie. En gros, elle ne fait pas du tout de "game logic", juste de l'affichage.





### archiv/Archivist ###

plus tard


## Vocabulaire ##

takeStimuli

dogDom

mact*
