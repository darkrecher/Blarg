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


## Rappel : fonctionnement des sprites avec pygame ##

Les sprites sont gérés par des objets `pygame.sprite.Sprite`. Durant un cycle de jeu, il faut effectuer les actions suivantes :

 - Pour chaque sprite :

    - Effacer à l'écran le rectangle englobant le sprite (selon sa position et la taille de son image). Si il y a une image de fond, il faut la redessiner par-dessus.

    - Exécuter la fonction `Sprite.update()` (qu'on a overridé). Cette fonction modifie la position et/ou l'image courante du sprite.

    - Exécuter la fonction `Sprite.draw()`. Dessine le sprite à l'écran.

- Exécuter la fonction `pygame.display.flip()`, afin de rafraîchir l'écran et d'afficher tous les changements d'un seul coup. (Double buffer, tout ça...)

Pygame permet de faciliter ce traitement, avec les groupes de sprite, en particulier, les `pygame.sprite.RenderUpdates`. On commence par mettre des sprites dans le groupe, avec la fonction `RenderUpdates.add()`. Ensuite, à chaque cycle de jeu, il faut effectuer les actions suivantes :

 - `RenderUpdates.clear()`, en indiquant en paramètre l'écran, et l'image de fond à redessiner. Cette fonction enregistre en interne une liste de "rectangle sales". C'est à dire les zones de l'écran sur lesquelles un sprite a été clearé.

 - Pour chaque sprite : exécuter sa fonction `update()`. On peut le faire individuellement, ou appeler la fonction `RenderUpdates.update()`, qui va updater tous les sprites du groupe.

 - `listDirtyRects = RenderUpdates.draw()`. Dessine à l'écran tous les sprites du groupe. Renvoie la liste de rectangle sales, correspondants à toutes les zones de l'écran sur laquelle quelque chose a changé (du clear, du draw, ou les deux, pour un ou plusieurs sprites).

 - Exécuter la fonction `pygame.display.flip()`, pour rafraîchir tout l'écran. Ou bien, si on veut être un peu plus subtil, exécuter `pygame.display.update(listDirtyRects)`. Cela rafraîchira uniquement les zones nécessaires.

Durant le jeu, on peut ajouter et enlever des sprites du groupe, avec les fonctions `add` et `remove`. Il faut le faire après le `clear`, et avant le `draw`.


## Description du rôle de chaque classe ##

### game/Game ###

Classe principale gérant le jeu en lui-même. Contient la game loop.

Cette classe contient un groupe `RenderUpdates`, appelé `allSprites`. Il contient tous les sprites du jeu à afficher actuellement. La game loop exécute la fonction `clear` et `draw` de `allSprites`.

Elle n'exécute pas la fonction `update`. Cette action est effectuée par divers autres modules du jeu. J'ai voulu faire comme ça car certains objets du jeu (en particulier le héros) sont représentés par plusieurs sprites. Il fallait donc mettre le code de gestion de ces objets dans des classes dédiées, et non pas dans un update d'un sprite quelconque qu'on n'aurait pas su exactement lequel.


### sprsimpl/SpriteSimple ###

Classe héritée de `pygame.sprite.Sprite`. Permet de gérer des sprites avec des mouvements simples (vitesse initiale + accélération), des enchaînements d'images simples (en boucle), et des conditions de destruction simples (après x boucles / en quittant l'écran).


### sprsiman/SpriteSimpleManager ###

Contient une groupe de `SpriteSimple`. Effectue leurs update, et les supprime de ce groupe lorsqu'ils sont arrivés en fin de vie.

À la création, on passe au manager le gros groupe `allSprites`. Le manager s'occupe d'updater, et d'ajouter/enlever de ce groupe les `SpriteSimple` dont il a la charge, au fur et à mesure de leur création/suppression.

Le manager ne s'occupe pas de dessiner ses sprites. C'est le code extérieur qui s'occupe de cette tâche, par le fait que ces sprites sont dans le groupe `allSprites`.


### sprsigen/SpriteSimpleGenerator ###

Générateur de `SpriteSimple` prédéfinis, correspondant à des éléments spécifiques du jeu (Le "prout" d'un magicien qui meurt en s'envolant, la flamme du fusil du héros, ...)

Le `SpriteSimpleGenerator` contient une référence vers un `SpriteSimpleManager`, dans lequel il ajoutera les sprites générés.

Cette classe est équivalente à un gros tas de constantes, permettant de générer des sprites avec des images, des mouvements et une configuration prédéfinies. La seule génération un peu plus complexe est celle des bras et des têtes coupées de magiciens. Ce sont des SpriteSimple comme les autres, mais il y a un petit traitement initial (avec du random) pour déterminer les images effectuant les gigotages et le tournoiement.


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

Pour le code extérieur, la seule chose intéressante à récupérer de cette classe est le groupe de sprite "groupLifePoints", contenant toutes les vestes en jean à afficher à un instant donné (tient compte des clignotements).

Cette classe ne gère pas la mort du héros. Elle ne prévient pas le code extérieur lorsque le héros n'a plus de points de vie. Elle ne fait pas du tout de "game logic". Elle indique juste des sprites à afficher.


### hero/Hero ###

Gère tout le bazar concernant le héros :

 - Affichage.

 - Récupération des stimulis (ordre envoyés par le joueur, collision avec les magiciens)

 - Mouvement, limitation de la position aux bords de l'aire de jeu.

 - Gestion des points de vie, animation de la mort du héros quand il n'a plus de points de vie.

 - Gestion du nombre de cartouche.

Lors de l'instanciation du héros, il faut lui envoyer les dictionnaires contenant les images du corps et de la tête. Il instancie de lui-même les deux objets `heroHead` et `heroBody`.

#### Fonctionnement global du héros ####

Le héros envoie directement ses ordres à deux objets `ammoViewer` et `lifePointViewer` (réarmement, perte d'un point de vie, ...). Cependant, la mise à jour de ces deux objets (fonction update) est effectuée dans la fonction principale `game.py/playOneGame`.

Il possède également un `spriteSimpleGenerator`, lui permettant de générer les sprites suivants, quand y'a besoin :

 - Douille qui s'envole et retombe à chaque réarmement.

 - Flamme sortant du fusil à chaque tir.

 - Sang qui gicle lorsque le héro se fait toucher.

La classe contient une super machine à état (variable membre `stateMachine`) permettant de gérer les comportements suivants :

 - Rechargements et réarmements.

 - Images du heroBody à afficher en fonction de l'action en cours. Enchaînement automatique de ces images.

 - Prise en compte des stimulis, ou stockage des stimulis si l'état actuel ne permet pas de le prendre immédiatement en compte.

 - Prise en compte des contraintes (par exemple : on recharge automatiquement après un tir si plus de cartouche)

 - Déclenchement d'un tir.

Les explications détaillées de chaque état, ainsi que les contraintes implémentées, sont décrites dans la fonction `definestateMachine`.

#### Tir ####

Le tir est déclenché après avoir vérifié qu'il y a au moins une cartouche, et que l'état actuel de la machine à état permet de tirer.

Détail des actions effectuée :

 - Changement d'état dans la machine à état.

 - Diminution du nombre de cartouche.

 - Envoi d'un son (bruit de coup de feu)

 - Indication qu'il faut réarmer. (La machine à état le prendra en compte le moment venu)

 - Détermination de la position exacte d'où partent les bullets.

 - Appel de la fonction `collHandlerBulletMagi.heroFiresBullets`

    - Calcul de la trajectoire des 3 bullets partant du fusil.

    - Détermination des collision entre les bullets et les magiciens.

    - Envoi des stimulis de dégâts aux magiciens touchés.

 - Récupération du nombre de magiciens tués et explosés par le tir.

 - Envoi de ces deux nombres au `scoreManager` (augmentation du score courant, des totaux, des high scores, ...)

 - Si au moins un magicien a été explosé, modification du sprite `heroHead` pour le faire sourire.

 - Génération d'un `simpleSprite` : la flamme au bout du fusil.

 - Remise à zéro du stimuli de FIRE, puisqu'il vient d'être effectué.

Toutes ces actions sont donc déclenchées automatiquement et instantanément. Les objets extérieurs sont directement contactés. On ne passe pas par le game.py pour envoyer des messages entre objets (par exemple, pour envoyer les points de dégâts aux magiciens).

#### Collision avec un magicien ####

Détail des actions déclenchées quand le héros se fait toucher (après avoir détecté une collision entre le héros et un magicien) :

 - Vérification que le héros n'est pas déjà dans un état où il a mal, ni où il est en train de mourir. (On est invincible pendant un petit temps juste après s'être fait toucher).

 - Diminution des points de vie de 1 (sauf si mode invincible)

 - Envoi d'un ordre au `lifePointViewer` pour afficher une veste en jean de moins (sauf si mode invincible).

 - Suppression du sourire sur le `heroHead`.

 - Annulation des stimulis stockées de tir et de rechargement. Le joueur n'aura qu'à réappuyer sur la touche correspondant. C'est comme ça, c'est le jeu.

 - Détermination du mouvement de Hurt, en fonction de la position relative du héros et du magicient qui l'a touché. (Lorsque le héro a mal, il recule pendant quelques cycles, dans la direction opposée au magicien)

 - Modification de l'image du `heroBody`. Gestion pourrie des décalages de sprite parce que j'ai pas implémenté de hotSpot.

 - Si il reste des points de vie :

    - Génération de Simple Sprite (gouttes de sang).

    - Changement de l'état actuel en l'état `HURT`.

    - Envoi d'un son ("argl !")

 - Sinon (le héros doit mourir)

    - Pas de génération de gouttes de sang, mais déclenchement du compteur de génération de gouttes de sang. (Le sang giclera en continu pendant quelques secondes).

    - Changement de l'état actuel en l'état `DYING`.

    - L'animation de mort (la tête qui se tourne de droite à gauche, les sons, ...) sont gérés par la machine à état, qui effectue toutes ces actions lorsque l'état est `DYING`.

    - Au bout de quelques secondes, la machine à état passera de `DYING` à `DEAD`.

#### Fin de partie ####

La classe `Hero` peut indirectement mettre fin à la partie, car la fonction `game.py/playOneGame` examine périodiquement l'état de la machine, et arrête la partie si cet état est `DEAD`.


### magician/Magician ###

Cette classe hérite de `pygame.sprite.Sprite`. Elle possède une machine à état, (plus simple que celle du héros). Lorsqu'on l'instancie, on lui passe un `spriteSimpleGenerator`, ce qui lui permet de créer des Simple Sprite lorsque c'est nécessaire.

#### cycle de vie ####

instanciation

création d'un Sprite Simple pour l'animation d'apparition


`currentState = APPEARING`

dans le groupe game.groupMagicianAppearing. updaté, mais pas drawé.

fonction magician.update exécute la fonction magician.updateAppearing : ne fait rien, à part attendre que l'animation du Simple Sprite se termine.


`currentState = ALIVE`

dans le groupe `game.groupMagician` et `game.allSprites`. updaté et drawé.

la fonction `magician.updateNormal` est exécutée. Elle est censé s'occuper des mouvements, de la montée de level du magicien, etc. Dans la classe de base, elle ne fait rien.


`currentState = DYING`

updaté et drawé.

Ça dépend du type de mort. Mais quand rotate et shit, le magicien ne reste pas plus d'un cycle dans cet état. Quand c'est dying naked, il y reste plus longtemps. (voir plus loin)


`currentState = DEAD`

retiré des deux groupes. ni updaté ni drawé. l'objet `magician` est garbage-collecté.


#### animation de mort ####

TODO

#### dérivation de la classe ####

TODO


### archiv/Archivist ###

TODO plus tard


## Vocabulaire ##

takeStimuli

dogDom

mact*

NONE_COUNT






