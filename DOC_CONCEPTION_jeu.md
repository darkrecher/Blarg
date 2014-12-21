# Document de conception de Blarg (jeu) #

Ce document décrit la manière dont est organisé le code du jeu. Le code du système d'interface (menu principal, config, ...) sera décrit dans un autre document, qui n'est pas encore fait.


## Introduction ##

Le code est assez densément commenté. Ce document se bornera donc à décrire sommairement le but de chaque classe.

Durant la réalisation de ce jeu, le PEP8 a été foulé aux pieds, écartelé, équarri et humilié en place publique par des petits enfants jetant des cailloux. C'est la faute à l'entreprise dans laquelle je bossais à l'époque, qui m'a appris à coder en python avec les conventions de nommage du C++. Il va falloir faire avec !


## Lancement d'une partie ##

Au démarrage du programme, le système d'interface est initialisé. Ensuite, lors du clic sur l'option "jouer" du menu principal, la fonction `mainclas.py/MainClass.mactPlaySeveralGames` est exécutée. Cette fonction effectue les actions suivantes :

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

 - `self.fontDefault` : objet `pygame.font.Font`. Police de caractère utilisée pour afficher les textes durant le jeu. (Le score).

 - `self.archivist.dicKeyMapping` : dictionnaire effectuant la correspondance entre des touches du clavier et les actions. Il est défini par le joueur, durant la configuration.

 - `dogDom` : booléen indiquant si le mode invincible est activé ou pas.


## Diagramme de classe. ##

![diagramme classe Blarg jeu](https://raw.githubusercontent.com/darkrecher/Blarg/master/doc_diverses/diagramme_pas_UML_jeu.png)

### Légende ###

Boîte avec un titre composé d'un seul mot : instance de classe. Le nom de l'objet instancié et le nom de la classe sont les mêmes, aux majuscules près.

Boîte avec un titre plus compliqué : instance de classe aussi. Format du titre : `nomDeLObjetInstancié = nomDeLaClasse()`.

Cadre bleu clair : zoom sur un endroit spécifique du diagramme, pour afficher plus de détails.

Flèche bleue pleine, de A vers B : Référence "forte". L'objet A possède une référence vers l'objet B, qu'il garde tout le long de sa vie.

Flèche bleue pointillée, de A vers B : Référence "faible". L'objet A n'a pas de référence vers l'objet B. Mais de temps en temps, on appelle une fonction de l'objet A en lui passant l'objet B en paramètre.

Petite flèche bleue vers "SpriteSiGen" : Référence vers l'objet `SpriteSimpleGenerator`. Ces références ne sont pas représentées comme les autres, car ça ferait une flèche qui traverse tout le diagramme et ça ferait fouilis.

Petite flèche bleue vers "SndYargl" : Référence vers l'objet `SoundYargler`.

Flèche verte, de A vers B : héritage. L'objet B est dérivée de l'objet A.

Grosse flèche grise pointillée : déplacement. À un moment de sa vie, l'objet est transféré d'un endroit à un autre.

Boîte avec un cadre pointillé : l'objet est instancié par l'objet englobant, puis il est tout de suite transféré ailleurs.


## Rappel : fonctionnement des sprites avec pygame ##

Les sprites sont gérés par des objets `pygame.sprite.Sprite`. Durant un cycle de jeu, il faut effectuer les actions suivantes :

 - Pour chaque sprite :

    - Effacer à l'écran le rectangle englobant (défini par la position et la taille de l'image courant du sprite). S'il y a une image de fond, il faut la redessiner par-dessus.

    - Exécuter la fonction (overridée) `Sprite.update()`. Cette fonction modifie la position et/ou l'image courante du sprite.

    - Exécuter la fonction `Sprite.draw()`. Dessine le sprite à l'écran.

- Exécuter la fonction `pygame.display.flip()`, afin de rafraîchir l'écran et d'afficher les changements. (Double buffer, tout ça...)

Pygame permet de faciliter ce traitement, avec les groupes de sprite, en particulier, les `pygame.sprite.RenderUpdates`. On commence par mettre des sprites dans le groupe, avec la fonction `RenderUpdates.add()`. Ensuite, à chaque cycle de jeu, il faut effectuer les actions suivantes :

 - `RenderUpdates.clear()`, en indiquant en paramètre l'écran, et l'image de fond à redessiner. Cette fonction enregistre en interne une liste de "rectangle sales". C'est à dire les zones de l'écran sur lesquelles un sprite a été clearé.

 - Pour chaque sprite : exécuter sa fonction `update()`. On peut le faire individuellement, ou appeler la fonction `RenderUpdates.update()`, qui va updater tous les sprites du groupe.

 - `listDirtyRects = RenderUpdates.draw()`. Dessine à l'écran tous les sprites du groupe. Renvoie la liste des rectangle sales, correspondant à toutes les zones de l'écran où quelque chose a changé (clear et/ou draw).

 - Exécuter la fonction `pygame.display.flip()`, pour rafraîchir tout l'écran. Si on veut être plus subtil, on peut exécuter à la place `pygame.display.update(listDirtyRects)`. Cela rafraîchira uniquement les zones nécessaires.

Durant le jeu, on peut ajouter et enlever des sprites du groupe, avec les fonctions `add` et `remove`. Il faut le faire après le `clear`, et avant le `draw`.


## Description du rôle de chaque classe ##

### game/Game ###

Classe principale gérant le jeu en lui-même. Contient la game loop.

Cette classe possède un `RenderUpdates`, appelé `allSprites`, contenant tous les sprites du jeu à afficher à l'instant T. La game loop exécute les fonctions `clear()` et `draw()` de `allSprites`.

Elle n'exécute pas `update()`. Cette action est effectuée par divers autres bouts de code. J'ai voulu faire comme ça car certains objets du jeu (en particulier le héros) sont représentés par plusieurs sprites. Il fallait donc mettre le code de gestion de ces objets dans des classes dédiées, et non pas dans un update d'un sprite quelconque qu'on n'aurait pas su à quel objet il se rapporte.


### common ###

Module contenant des petites fonctions et des constantes utiles un peu partout. Voir commentaire de chacun d'eux pour des infos détaillées.


### sprsimpl/SpriteSimple ###

Classe héritée de `pygame.sprite.Sprite`. Permet de gérer des sprites avec :
 - des mouvements simples (vitesse initiale, accélération),
 - des enchaînements d'images simples (en boucle),
 - des conditions de destruction simples (après x boucles / en quittant l'écran).


### sprsiman/SpriteSimpleManager ###

Contient une groupe de `SpriteSimple`. Effectue leurs updates, et les supprime lorsqu'ils sont arrivés en fin de vie.

Le manager possède une référence vers le gros groupe `allSprites`. Il s'occupe d'updater et d'ajouter/enlever les `SpriteSimple` dont il a la charge, au fur et à mesure de leur cycle de vie.

Le manager ne s'occupe pas de clearer et dessiner ses sprites. C'est le groupe `allSprites` qui effectue ces tâches, comme il le fait pour tous les autres sprites du jeu.


### sprsigen/SpriteSimpleGenerator ###

Générateur de `SpriteSimple` prédéfinis, correspondant à des éléments spécifiques du jeu (Le "prout" d'un magicien qui meurt en s'envolant, la flamme du fusil du héros, ...)

Le `SpriteSimpleGenerator` contient une référence vers un `SpriteSimpleManager`, dans lequel il ajoutera les sprites générés.

Cette classe est équivalente à un gros tas de constantes, permettant de générer des sprites avec des images, des mouvements et une configuration prédéfinis.

La seule génération plus complexe que les autres est celle des bras et têtes coupées de magiciens. Ce sont des `SpriteSimple` comme les autres, mais il y a un petit traitement initial (avec du random) pour déterminer les images effectuant les gigotages et le tournoiement.


### lamoche/Lamoche ###

Classe héritée de `pygame.sprite.Sprite`. Permet d'afficher un texte à l'écran. Je l'ai appelé "Lamoche" pour faire une blague par rapport au mot "Label". Voilà, c'est drôle.

Cette classe est également utilisée dans le système d'interface.


### herobody/HeroBody ###

Héritée de `pygame.sprite.Sprite`. Affiche le corps du héros. Le choix de l'image à afficher se fait en appelant la méthode `changeImg()`. C'est au code extérieur de décider quelle image afficher en fonction de ce qu'il se passe dans le jeu.


### herohead/HeroHead ###

Héritée de `pygame.sprite.Sprite`. Affiche la tête du héros. Cette classe est d'un niveau un peu plus haut que `HeroBody`, et gère donc un peu plus de choses :

 - Tournage de tête à gauche et à droite : fonction `turnHead()`. (Appelée lorsque le héros meurt)
 - Sourire : fonction `startSmiling()` et `stopSmiling()`. (Appelées lorsque le héros fait exploser un magicien en bouillie).
 - Arrêt automatique du sourire au bout de quelques secondes : fonction `update()`.


### movpoint/MovingPoint ###

classe héritée de `pygame.Rect`. Représente un point dans l'aire de jeu qui se déplace, la direction étant définie à l'instanciation. À chaque cycle, on exécute la fonction `advanceOneStep()`. La position courante est récupérée par le membre `Rect.topleft`.

Comme on définit un mouvement dans une direction donnée, sans limite, il ne se termine jamais. La fonction `isMoveFinished()` renvoie toujours false.

Cette classe est utilisée pour calculer la trajectoire des balles tirées par le héros.


### movline/MovingPointOnLine ###

classe héritée de `MovingPoint`. Représente un point dans l'aire de jeu se déplaçant le long d'un segment de droite. Les points d'arrivée et de départ sont donnés à l'instanciation.

À chaque exécution de `advanceOneStep()`, on se déplace d'un pixel (en diagonale ou pas, ça dépend de là où on est). La vitesse n'est donc pas constante entre deux cycles de jeu, mais on s'en fout.

La fonction `IsMoveFinished()` renvoie True lorsque le point courant a atteint le point d'arrivée.

Cette classe est utilisée pour calculer la trajectoire des magiciens se déplaçant le long d'une ligne (les `MagiLine`).


### cobulmag/CollHandlerBulletMagi ###

À chaque fois que le héros tire, cette classe effectue les actions suivantes :

 - Calcul des trajectoires. Un tir fait partir 3 balles : une un peu vers le haut, une tout droit, et une un peu vers le bas. Elles ont une vitesse instantanée.

 - Détection des collisions entre les balles et les magiciens.

 - Exécution de la fonction `Magician.hitByBullet(Damage)` chaque fois qu'une des balles touche un magicien. La valeur renvoyée indique son état (vivant/tué/explosé). Lorsque plusieurs magiciens sont exactement sur la même abscisse et qu'une balle leur arrive dessus, ils sont tous touchés en même temps.

 - Renvoi du nombre total de magiciens tués et explosés par le tir.

D'autre part, ce fichier de code contient des explications détaillées sur les différents états d'un magicien, et les passages d'un état à un autre. Ça n'a peut-être pas sa place ici, mais c'est ainsi. Tralalali.


### cohermag/CollHandlerHeroMagi ###

Gestion des collisions entre le héros (tête + corps) et les magiciens.

Lorsqu'une collision a lieu, on envoie le stimuli `takeStimuliHurt(theMagician.rect)` au héros, et le stimuli `TakeStimuliTouchedHero()` au magicien.

Lorsque le héros reçoit un stimuli de collision, il se met immédiatement dans l'état `HURT`. On ne fait pas d'autres détections de collision tant qu'il reste dans cet état. Cela permet d'éviter que le héros se fasse toucher plusieurs fois en peu de temps, ce qui ne serait pas très gentil envers le joueur.


### scoremn/ScoreManager ###

Récupère les stats d'un joueur à partir d'une classe `Archivist` (la classe qui gère le fichier de sauvegarde). Ces stats comprennent les high scores, ainsi que le nombre total de magiciens tués et explosés.

Au fur et à mesure de la partie, récupère le nombre de magiciens explosés, et le nombre de magiciens tués sans être explosé. Met à jour le score de la partie en cours, les high scores, et les totaux.

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

    - Calcul de la trajectoire des 3 bullets partant du fusil. (une tout droit, une un peu vers le haut, une un peu vers le bas).

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

Cette classe hérite de `pygame.sprite.Sprite`. Lorsqu'on l'instancie, on lui passe un `spriteSimpleGenerator`, ce qui lui permet de créer des Simple Sprite lorsque c'est nécessaire.

Il s'agit de la classe de base, définissant le comportement générique d'un magicien : apparition, gestion des collision avec le héros et les balles, animations de mort. Elle ne définit pas les mouvements. Ceux-ci sont définis dans les classes héritées.

Le magician possède une machine à état (plus simple que celle du héros). L'état courant est stocké dans le membre `currentState`.

Le magician possède un `level` (variable numérique entière). La classe de base ne fait rien de cette variable, elle est censée représenter le niveau de difficulté du magicien. Lorsque le magicien se collisionne avec le héros, son `level` retombe automatiquement à 1, et la fonction `resetToLevelOne` est exécutée. Cela permet de ne pas trop "punir" le joueur. Déjà qu'il se fait toucher et perd un point de vie, on ne va pas en plus lui laisser un magicien ayant un haut `level` à proximité de lui.

#### cycle de vie ####

 - Instanciation d'un `Magician`

    - création d'un `spriteSimple`, représentant l'animation d'apparition du magicien. (Que au début ça ressemble à une bite bleue, puis ça prend la forme du magicien). On conserve une référence vers ce sprite, afin de savoir quand l'animation se termine.

    - La game loop place le nouveau magicien dans le groupe de sprite `Game.groupMagicianAppearing`, mais pas dans `Game.allSprites`. C'est à dire que le magicien est updaté, mais pas dessiné.

 - `currentState = APPEARING`.

    - La fonction `Magician.update` exécute la fonction `Magician.updateAppearing`. Cette fonction ne fait rien, à part attendre que l'animation du SpriteSimple d'apparition se termine. Lorsque c'est le cas, on passe à l'état suivant.

 - `currentState = ALIVE`

    - La game loop sort le magicien du groupe `Game.groupMagicianAppearing`, pour le placer dans deux groupes à la fois : `game.groupMagician` et `game.allSprites`. Le magicien est donc updaté et dessiné à chaque cycle de jeu.

    - La fonction `Magician.update` exécute la fonction `magician.updateNormal`. Elle est censée s'occuper des mouvements, de la montée de level, etc. Dans la classe de base, cette fonction ne fait rien. Le magicien reste immobile.

 - `currentState = HURT`

    - (Cet état est facultatif, si le magicien perd tous ses points de vie d'un coup, il passe directement de l'état `ALIVE` à `DYING` ou `BURSTING`.)

    - Exécution de la fonction `updateHurt` à chaque cycle de jeu. Fonction à overrider. Au bout d'un moment, le magicien revient à l'état `ALIVE`.

 - `currentState = DYING / BURSTING`

    - Le magicien passe dans l'état `BURSTING` lorsqu'il se prend 3 bullets d'un seul coup. Ça arrive lorsque le héros lui tire dessus d'assez près, puisqu'un tir génère trois bullets, qui partent dans 3 directions un petit peu différentes. Dans ce cas, l'animation de mort est toujours la même : des membres coupés qui volent.

    - Il passe dans l'état `DYING` lorsqu'il n'a plus de points de vie (il en a 2 au départ). Dans ce cas, une animation de mort est sélectionnée au hasard parmi 3 différentes:

         * shit : le magicien se transforme en caca.
         * rotate : il tournoie dans les airs puis retombe.
         * naked : il s'envole tout nu, tout en faisant des prouts.

    - Pour les animations bursting, shit et rotate, le magicien génère immédiatement un ou plusieurs `simpleSprite` correspondant à l'animation. Puis, dès le cycle de jeu suivant, il passe directement à l'état `DEAD`. L'animation n'est pas gérée par la classe elle-même.

    - Pour l'animation naked, c'est un peu plus compliquée. Il faut effectuer des petits mouvements aléatoires gauche et droite, tout en allant vers le haut, et en générant de temps en temps des mini `spriteSimple` de fumée de prout, tout en émettant des mini-sons de prouts. Oui oui, tout cela est génial. Tout cela est effectué par le magician, avec la fonction `updateDyingNaked`.

 - `currentState = DEAD`

    - La game loop retire le magicien des deux groupes de sprites. Il n'est plus updaté ni drawé, et il finit par être garbage-collecté puisqu'il n'est plus référencé nul part.


### magiline/MagiLine ###

Classe dérivée de `Magician`. Définit un magicien qui se déplace sur une ligne droite. À l'instanciation, on indique (entre autres) la position de départ et la position d'arrivée.

Plus le `level` du magiline est haut plus il se déplace vite. Le level lui-même n'augmente pas.

Lorsque le magiline est arrivée à son point de destination, on vérifie s'il n'est pas trop à gauche de l'écran (la limite est définie par la constante `RESPECT_LINE_X`). Si c'est le cas, le joueur ne peut pas le tuer, car il n'a pas assez de place pour se placer à gauche du magiline et lui tirer dessus. (Vu que le héros ne peut pas se retourner, ha ha ha).

À la fin de son mouvement, si le magiline est à gauche de `RESPECT_LINE_X`, il se déplace vers la droite jusqu'à la dépasser. Ensuite, il ne bouge plus du tout.

La fonction `updateNormal`, exécutée à chaque cycle du jeu tant que le magiline est `ALIVE`, exécute la fonction référencée par `currentFuncupdateNorm`. Cette variable pointe sur une fonction d'update qui change selon l'action à faire. Elle peut prendre les valeurs suivantes :

 - updateNormMoveOnLine : mouvement le long de la ligne.
 - updateNormMoveRespectX : mouvement pour se placer à droite de `RESPECT_LINE_X`.
 - updateNormStayPut : pas de mouvement.

C'est un peu bizarre de faire comme ça, j'aurais peut-être dû faire un variable de sous-état, et un dictionnaire sous-état -> fonction, comme la classe de base qui a un dictionnaire état ->_fonction. Mais bon, je fais ce qu'on veut, j'ai le droit d'être bizarre.

Lorsque le magiline est touché, la fonction `updateHurt` est exécutée. Cette fonction immobilise le magiline pendant quelques cycles. Il n'a pas de mouvemement de recul, sinon ça le sortirait de la ligne sur laquelle il est censé se déplacer.


### magirand/MagiRand ###

Classe dérivée de `Magician`. Définit un magicien qui se déplace au hasard.

Les mouvements ont une inertie. On met du hasard dans les accélérations X et Y. Ces accélérations agissent sur les vitesses de déplacement X et Y, qui agissent sur les positions X et Y.

Le magirand possède une `respectLine` (variable numérique entière, différente pour chaque instance). Elle définit  la position d'une ligne verticale imaginaire. Lorsque le magirand se trouve à gauche de cette limite, on lui ajoute un petit mouvement vers la droite. Ça permet de mieux doser la difficulté. Le héros ayant tendance à rester du côté gauche, plus un magicien va vers la gauche, plus il rende le jeu difficile.

Plus le `level` du magirand est haut, plus ses accélérations et sa vitesse maximale sont haute, et plus la `respectLine` se décale vers la droite. Le `level` augmente avec le temps. Toutes ces valeurs sont réinitialisées si le magicrand retombe au niveau 1, lorsqu'il touche le héros.

Lorsque le magicrand est touché, la fonction `updateHurt` est exécutée. Cette fonction arrête les mouvements aléatoires pendant quelques cycles, et effectue un mouvement de recul, vers la droite. Les mouvements aléatoires reprennent avec une accélération et une vitesse nulle.


### maggen/MagicianGenerator ###

Cette classe génère les magiciens durant le jeu. Elle utilise un `MagicianWaveGenerator` pour savoir quoi générer, et quand. (Voir plus loin).

Le `MagicianGenerator` possède une référence vers le groupe de sprite `Game.groupMagicianAppearing`. La génération d'un magicien est effectuée par la fonction `MagicianGenerator.generateOneMagician`. Elle consiste à instancier un magicien, et à l'ajouter dans le groupe de sprite. (En même temps, on joue un son, pour faire cool).

La génération durant le jeu est définie par des "patterns". Il y en a de différents types : par exemple, une ligne de magicien en haut de l'écran, ou un cercle autour du héros, ou un certain nombre placés au hasard, ...

Un pattern, quel que soit son type, est une liste. Chaque élément est un tuple, représentant un magicien à générer. Le tuple contient deux sous-éléments :

 - "Delay" : nombre de cycle à attendre avant de générer ce magicien. Ce nombre est cumulatif. Par exemple, si le premier magicien du pattern à 4 cycles d'attente, et le second 2 cycles, alors le second devra attendre 6 cycles au total pour être généré. L'ordre des éléments du pattern est donc significatif. Si plusieurs magiciens à la suite ont un delay de 0, ils apparaîtront tous en même temps.

 - Un sous-tuple, contenant les caractéristiques du magicien à générer :

    - magiType : type du magicien : magiline (déplacement le long d'une ligne) ou magirand (déplacement au hasard).
    - position de départ.
    - position d'arrivée. (Utile seulement pour les magiline).
    - level de départ du magicien.

Le MagicianGenerator possède une liste de patterns. À chaque cycle, lors de l'appel de la fonction `MagicianGenerator.update`, les actions suivantes sont effectuées :

 - Diminution du compteur de temps  avant la prochaine vague de magicien.

 - Éventuellement, diminution du compteur de temps bonus (voir plus loin).

 - Si il n'y a plus de temps, on demande au `MagicianWaveGenerator` de générer une nouvelle vague. Cela créera de nouveaux patterns, qu'on ajoute à la liste.

 - Pour chaque pattern de la liste :

    - Diminution de 1 du delay du premier élément. Lorsqu'on atteint 0, on génère un magicien, et éventuellement les magiciens suivants, si ils ont aussi un delay de 0.
    - Suppression des patterns n'ayant plus d'éléments.

Lorsque la classe `Game` détecte qu'il n'y a plus de magiciens actifs dans le jeu, elle envoie un stimuli au `MagicianGenerator`, en exécutant la fonction `takeStimuliNoMoreActiveMagi`. Cette fonction modifie le temps de génération avant la prochaine vague de magicien, et éventuellement, elle augmente le temps de bonus et envoie de l'"antiHarM" au `MagicianWaveGenerator` (voir plus loin).


### maggenlc/MagicianListCoordBuilder ###

Classe contenant des fonctions "statiques", qui renvoient deux listes de coordonnées (coord de début, coord de fin), ou bien une liste de coord de début, et "None". Ces listes de coordonnées sont ensuite utilisées pour les patterns de génération de magicien.

Cette classe contient une référence vers le héros. Elle n'en fait rien de spécial, c'est uniquement pour récupérer la position courante du héros.

On ne transmet pas aux `MagicianListCoordBuilder` les autres infos liées au pattern : type de magicien à générer, délai entre magiciens, levels, ... Elle n'en n'a pas besoin, elle ne calcule que les coordonnées. Par contre elle a besoin du nombre de magiciens.

Ces fonctions sont les suivantes :

 - `generateLinePattern` : coordonnées en ligne, horizontale ou verticale. Les coordonnées de début sont d'un côté de l'écran, celles de fin sont de l'autre côtés. On peut avoir la liste des coordonnées de fin inversées par rapport à celles du début. C'est à dire que les magiciens, au lieu de tous avancer le long de lignes parallèles, vont avancer en se croisant au centre. (Le magicien en haut à gauche termine en bas à droite, etc.).

 - `generateDiagPattern` : coordonnées sur 4 diagonales, construites à partir d'un centre donné. On place un premier magicien sur une diagonale, un second sur la suivante, et ainsi de suite, puis on revient sur la première diagonale, et ainsi de suite-suite.

 - `generateRandPattern` : coordonnées complètement au hasard. Aussi bien le départ que l'arrivée.

 - `generateCirclePattern` : coordonnées le long d'un cercle. Le centre du cercle est la position courante du héros.

 - `generatePattern` : fonction générique. On lui passe un type de pattern, et elle appelle l'une des 4 fonctions ci-dessus, en fonction.

Pour chacune de ces fonctions, on précise si on veut la liste de coordonnées de fin, ou si on veut juste None. Lorsqu'on a prévu de générer des magirand, il n'y a pas besoin de déterminer les coordonnées de fin, puisque ce type de magicien se déplace au hasard.

Il y a parfois un peu de random dans la détermination des coordonnées (espacement entre les magiciens, ordre dans un sens ou dans l'autre, etc.). Rien de significatif pour la difficulté du jeu. Car la gestion de la difficulté est faite par le `MagicianWaveGenerator`.

Le `MagicianWaveGenerator` se crée une instance de `MagicianListCoordBuilder`, afin de l'assister dans la généreration des patterns qu'il renvoie. (C'est rigolo de lire qu'une classe assiste une autre. Ha ha ha).


### hardmana/HardMana ###

La génération des magiciens se fait par vagues. La difficulté des vagues doit être à peu près progressive, mais en même temps, il faut qu'il y ait du hasard. Afin de répondre à ces besoins, on met en place la notion de "hardMana".

Le hardMana est une valeur numérique entière. Il représente une quantité de "points", que le `MagicianWaveGenerator` peut dépenser pour augmenter la difficulté de la prochaine vague à générer. À chaque nouvelle vague, on redonne du hardMana au `MagicianWaveGenerator`. On lui en donne de plus en plus au fur et à mesure de la partie.

Lors de la génération d'une nouvelle vague, le hardMana disponible est réparti en plusieurs quantités, chacune attribué à un type de dépense spécifique. Les "achats" d'élément de la vague sont décidés en fonction de la quantité alloué.

De plus, lorsque le joueur élimine tous les magiciens d'une vague en peu de temps, on le récompense. On lui attribue de l'"antiHardMana". Un point d'antiHarM annule un point de hardMana.

Tout cela est un peu compliqué et j'ai donc créé la classe `HardMana`, qui sert à gérer une quantité de hardMana. Cette classe permet d'effectuer les opérations suivantes :

 - Lire la quantité actuelle de hardMana, en ajouter, en retirer.

 - `payGeneric` : décide de payer ou pas pour quelque chose (par exemple : un pattern en plus, un magicien en plus dans un pattern, une montée de niveau d'un magicien, ...). La décision se fait en fonction d'un coefficient, et de la quantité de hardMana actuelle. Plus la quantité et le coefs sont haut, plus on a de chances de le payer. (Il faut bien évidemment avoir suffisamment de hardMana).

 - `dispatch` : répartit la quantité actuelle dans deux classes hardMana, selon un coefficient de répartition déterminé plus ou moins au hasard.

 - `chooseAndPay` : choisit un élément (ou rien) parmi une liste de chose à payer, chacune ayant un coût et un coefficient de probabilité de payage. On choisit parmi ce qu'on peut permettre de s'acheter.

 - `divide` : répartit équitablement la quantité actuelle en plusieurs classes `HardMana`.

 - `antiHarMDebuff` : applique de l'antiHarm. Les quantités d'antiHarm sont également gérées par des classes `HardMana`. Sauf que quand on met ensemble du hardMana et de l'antiHarm, ça s'annule.

Tous les coefficients sont indiqués en 128ème. C'est un choix personnel d'implémentation, qui est peut-être discutable. Mais moi personnellement, je ne le discute pas, parce que je suis tout seul dans ma tête. (Je suis tout seul dans ma tête, n'est-ce pas ?).

### maggenwa/MagicianWaveGenerator ###

Gère la génération successive des vagues de magiciens.

#### déroulement de la génération des vagues, durant la partie ####

 - Au début de la partie, la classe `Game` instancie un `MagicianGenerator`, qui s'instancie pour lui-même un `MagicianWaveGenerator`.

 - Le `MagicianWaveGenerator` possède une quantité initiale de hardMana de 0 (dans la variable `harMTotal`). La quantité allouée à chaque nouvelle vague à créer est définie par `MagicianWaveGenerator.incrForHarM`. Cette quantité est de 0 également, mais elle augmente de 20 à chaque vague (`HARM_INCREMENTATION_OF_INCREMENTATION_PER_WAVE`).

 - La variable `MagicianGenerator.counterNextWave` est initialisé à 0. Donc on crée automatiquement une première vague, en exécutant la fonction `MagicianWaveGenerator.elaborateNextWave`.

 - Même avec un hardMana initiale de 0, cela crée un magicien. Car le premier pattern de generation d'une vague est gratuit, et le premier magicien d'un pattern est gratuit aussi. Donc la fonction `elaborateNextWave` renvoie toujours au moins un pattern. Elle renvoie également une variable numérique `timeWave` : nombre de cycle avant la génération de la prochaine vague. Ce temps est calculé par le `MagicianWaveGenerator` (voir plus loin pour plus de détails).

 - Le `MagicianGenerator` génère le ou les magiciens définis dans le ou les patterns. (Soit tous d'un coup, soit au fur et à mesure du temps, ça dépend des patterns).

 - `MagicianGenerator.counterNextWave` prend la valeur de `timeWave`.

 - exécution de `MagicianGenerator.update` à chaque cycle de jeu : `MagicianGenerator.counterNextWave` diminue de 1.

 - Le joueur doit tuer les tous les magiciens de la vague. On imagine qu'il parvient à le faire avant que `MagicianGenerator.counterNextWave` atteigne 0.

 - La fonction `Game.isMagicianActive` détecte qu'il n'y a plus de magiciens actifs. La classe `Game` exécute alors la fonction `MagicianGenerator.takeStimuliNoMoreActiveMagi`.

 - Si le temps restant avant la prochaine vague est inférieur à 70 cycles (`DELAY_MAX_BETWEEN_WAVE`), on récompense un peu le joueur : on ne fait rien jusqu'à la prochaine vague. Ça lui laisse le temps de se repositionner et de recharger son fusil.

 - Si le temps est supérieur à 70 cycles, on récompense plus le joueur. On récupère le temps au-delà des 70 cycles, et on l'utilise pour deux choses :

    - création d'antiHarM : 3 cycles de temps bonus créent un point d'antiHarM (`COEF_CONVERSION_HARM_FROM_TIME`). Envoi de cet antiHarM au `MagicianWaveGenerator`, qui le stocke dans sa variable interne `antiHarM`.

    - stockage du temps supplémentaire dans la variable `MagicianGenerator.counterBonusTime`.

 - Le temps avant la génération de la prochaine vague est ramené à 70 cycles, pour pas que le joueur s'ennuie.

 - `MagicianWaveGenerator.harMTotal` est augmenté, `MagicianWaveGenerator.incrForHarM` aussi.

 - Utilisation de l'antiHarM stocké pour diminuer `MagicianWaveGenerator.harMTotal`. On utilise au maximum 40 points d'antiHarM. Le reste est toujours stocké dans `MagicianWaveGenerator.antiHarM`, et sera utilisé pour les prochaines vagues.

 - Génération de la nouvelle vague de magicien, par la fonction `MagicianWaveGenerator.elaborateNextWave`, qui dépense le hardMana contenu dans `harMTotal`.

 - Le joueur doit tuer les tous les magiciens de la vague. On imagine que ça lui prend du temps, et que `MagicianGenerator.counterNextWave` atteint 0 alors qu'il reste encore des magiciens actifs.

 - On ne génère pas encore la vague suivante. On décrémente `MagicianGenerator.counterBonusTime`, de 1 à chaque cycle. Si le joueur parvient à tuer tous les magiciens actifs, on génère immédiatement la vague suivante, et on conserve le reste de `MagicianGenerator.counterBonusTime` pour plus tard.

 - Sinon, on vide tout le temps de bonus, et lorsqu'il atteint 0, on génère la vague suivante, même si il reste encore des magiciens actifs.

 - Et ainsi de suite, vague après vague ... (trip: peu à peu, vague à vague, goutte à goutte, miette à miette et cœur à cœur).

#### Actions effectuées pour générer une nouvelle vague. ####

Toutes ces actions sont effectuées par la fonction `MagicianWaveGenerator.elaborateNextWave`.

Voir commentaire dans le code. C'est assez détaillé.


### archiv/Archivist ###

Lit et écrit les données (config du jeu, config des touches, scores du joueur) dans le fichier de sauvegarde "dichmama.nil", créé dans le même répertoire que l'application.

Je l'ai appelé "dichmama.nil" parce que je suis quelqu'un de rigolo.

Le format de ce fichier et les interactions avec le code extérieur sont décrites dans le gros commentaire au début de `archiv.py`.


### yargler/SoundYargler ###

Joue les sons. Ceux du jeu, et ceux du système de menu.

Les sons sont organisés par groupe. Un groupe correspond à un événement (ex : coup de feu, magicien qui se prend une balle, ...)
Il peut y avoir plusieurs sons dans un même groupe. Lorsque l'événement survient, la fonction `playSound` doit être exécutée, en indiquant en paramètre l'identifiant de l'événement. La fonction on choisit un son au hasard parmi ceux du groupe correspondant à l'événement, et le joue.

Ça permet d'avoir un minimum de diversité dans les sons. Un magicien qui meurt fera parfois "Argl", parfois "Heuargl" ou parfois "Ayaaarrr". C'est important.

Le nom des fichiers sons reflète ce rangement par groupe. Le format des noms est le suivant :
(identifiant du groupe) (index sur 2 chiffres) ".ogg".

La liste des groupes et leurs identifiants sont décrits au début du fichiers (variables `SND_*` et `DICT_SND_FILENAME`).

Pour jouer les sons, on instancie une seule classe `SoundYargler`, dès l'importation du fichier `yargler.py`. L'objet instancié (`theSoundYargler`) n'est pas transmis en paramètre d'une fonction à l'autre. Ce serait lourdingue. On l'importe directement au moment d'importer le fichier. C'est une sorte de singleton à l'arrache.


## Vocabulaire ##

`takeStimuli*` : préfixe de nom de fonction. À appeler par du code extérieur, pour prévenire la classe possédant cette fonction qu'il s'est passé un truc. C'est pour exprimer que c'est une fonction "publique", et que c'est comme une sorte de "callback", mais pas vraiment. Et ça s'appelle "takeStimuli" et non pas "sendStimuli", car la fonction est nommé du point de vue de la classe, et non pas du point de vue du code extérieur. C'est pas très bien. Tant pis, on fera mieux la prochaine fois.

`dogDom` : annagramme plus ou moins obfusqué de "god mode". Je ne voulais pas que ce soit trop facile de se rajouter le mode invincible en bidouillant le code source. Une recherche des mots "god" et "invincible" dans tous les fichiers ne doit rien donner d'intéressant. J'utilise donc ce mot-clé toutes les fois où je parle de la validation du god mode avec le code secret, et de la sélection de ce mode dans le menu secret. Ha ha ha, je m'appelle Réchèr et j'obfusque du code python tout en le documentant par ailleurs. Oui je suis schizophrène, oui.

`mact*` : préfixe de nom de fonction. "mact" = "menu action". Fonction de callback à exécuter lorsque l'utilisateur clique un bouton, active un élément de l'IHM, ...

`NONE_COUNT` : Bon en fait c'est la valeur `None`. Je l'utilise pour les variables de compteur. Pour indiquer explicitement que c'est une variable de compteur, et que là, je lui demande de ne pas compter. C'est une sorte de typage spécifique du vide pour indiquer plus précisément qu'est-ce qui est vide. Au fait, vous avez lu mon article de blog sur l'expression du vide dans les langages de programmation ?

`HardMana`, `harM`, `antiHarM`, `wave`, `magiCoefCost` : voir début du fichier `maggenwa.py`.

`pat`, `pattern`, `genPattern` : pattern de génération d'une liste de magiciens, dans une vague. (en ligne, en diagonale, en cercle, au hasard), (avec tous les magiciens qui apparaissent d'un coup, qui apparaissent progressivement, ...) ...

`debuff` : action de diminuer le `HardMana` de la prochaine vague à créer avec de l'`antiHarM`. Le terme n'est pas très bien choisi mais c'est pas grave.
