# Document de conception de Blarg (système de menu) #

Ce document décrit la manière dont est organisé le système de menu de Blarg (menu principal, config des touches, affichage des scores, ...). Il ne décrit pas l'organisation du code du jeu en lui-même.

## Introduction ##

Le code est assez densément commenté. Ce document se bornera donc à décrire sommairement le but de chaque classe.

Durant la réalisation de ce jeu, le PEP8 a été foulé aux pieds, écartelé, équarri et humilié en place publique par des petits enfants jetant des cailloux. C'est la faute à l'entreprise dans laquelle je bossais à l'époque, qui m'a appris à coder en python avec les conventions de nommage du C++. Il va falloir faire avec !

Le système de menu se veut le plus générique et le plus réutilisable possible. Même si en réalité, euh... Bref.

Les noms des fichiers définissant le système de menu générique commencent tous par "menu". Les noms des fichiers définissant les menus spécifique à Blarg commencent tous par "menuz". J'aurais dû ranger tout ça correctement dans des répertoires, mais j'étais un vilain.

## Description du système de menu générique ##

### Menus d'exemple ###

Des exemples simples et indépendants du jeu ont été créés, afin de donner une première idée de ce que peut faire le système de menu.

Pour les exécuter, ouvrir une console, et utiliser les commandes suivantes :

    cd <emplacement_de_ce_repository>
    cd code
    python menudemo.py 1

Il y a 3 exemples de menus. Remplacer le "1" à la fin de la dernière commande par "2" ou "3" pour les lancer.

Il faut avoir installé python et les dépendances nécessaires. Si vous avez réussi à exécuter le jeu à partir du code source, les exemples s'exécuteront sans problème. L'aide à ce sujet est décrite dans un autre document, pas encore fait.

(TODO : https://github.com/darkrecher/Kawax/blob/master/doc_diverses/installation_et_exe_build.md)

Le code des exemples de menu contient des commentaires et des docstrings, qui sont à priori suffisants. Les fichiers sont à consulter dans l'ordre suivant :

 - code/menudemo.py
 - code/menudemo_files/launch_demo_menu_empty.py
 - code/menudemo_files/launch_demo_menu_label.py
 - code/menudemo_files/menuelem_event_teller.py
 - code/menudemo_files/launch_demo_menu_event_teller.py

### Diagramme de classe ###

![diagramme classe Blarg menu générique](https://raw.githubusercontent.com/darkrecher/Blarg/master/doc_diverses/diagramme_pas_UML_menu_generique.png)

#### Légende ####

Boîte avec un titre composé d'un seul mot : instance de classe.

Boîte avec un titre plus compliqué : instance de classe aussi. Format du titre : `nomDeLObjetInstancié = NomDeLaClasse()`.

Cadre bleu clair : zoom sur un endroit spécifique du diagramme, pour afficher plus de détails.

Flèche bleue pleine, de A vers B : Référence. L'objet A possède une référence vers l'objet B, qu'il garde tout le long de sa vie.

Flèche verte, de A vers B : héritage. L'objet B est dérivée de l'objet A.

### Modules définissant le fonctionnement des menus ###

#### common.py, valeurs IHMSG_* ####

"IHMSG" = "IHM Message".

Il s'agit de constantes permettant d'échanger des informations entre les `MenuElem` et le `MenuManager`. On peut en placer plusieurs dans un même message (par exemple, pour demander un redessin du menu et en même temps signaler qu'on accepte le focus).

Un message est constitué d'un tuple de 0, 1 ou plusieurs IHMSG. Ceux-ci sont définis dans `common.py`.

 - `IHMSG_QUIT` : on veut quitter le menu courant, pour revenir au truc qu'on faisait avant.
 - `IHMSG_TOTALQUIT` : on veut totalement quitter tout le jeu.
 - `IHMSG_REDRAW_MENU` : le menu doit être entièrement redessiné. (Le fond + tous les éléments).
 - `IHMSG_ELEM_CLICKED` : l'élément de menu s'est fait cliquer dessus.
 - `IHMSG_ELEM_WANTFOCUS` : l'élément de menu veut avoir le focus.
 - `IHMSG_CYCLE_FOCUS_OK` : lors d'un cyclage de focus (touche Tab), l'élément de menu actuellement focusé accepte de transmettre le focus à l'élément suivant.
 - `IHMSG_PLAY_ONCE_MORE` : message spécial utilisé dans un seul cas : quand on quitte le menu affichant que le héros est mort. Sert à indiquer que le joueur veut rejouer.
 - `IHMSG_CANCEL` : le joueur veut annuler le truc en cours.

Pour indiquer un message sans aucun IHMSG, il suffit d'utiliser un tuple vide. Comme je suis super malin, je me suis dit que j'allais créer une constante égale au tuple vide, afin d'exprimer explicitement la notion de message vide. (Une lubie s'apparentant à du typage spécifique). La constante s'appelle `IHMSG_VOID`.

Du coup, pour renvoyer un message vide, on écrit `IHMSG_VOID`, sans parenthèse. Pour renvoyer un message contenant un IHMSG, on écrit `(IHMSG_REDRAW_MENU, )`, avec parenthèses. Ça fait bizarre. Tant pis !

#### menucomn.py ####

Diverses fonctions et constantes communes au système de menu.

C'est principalement utilisé par la partie spécifique (menus du jeu Blarg). Mais la partie générique utilise parfois une ou deux constantes contenues dans ce fichier. D'ailleurs c'est pas très bien, il faudrait essayer de séparer.

<a class="mk-toclify" id="menuelempy"></a>
#### menuelem.py ####

Contient la classe `MenuElem` : définition générique d'un élément de menu.

La plupart des fonctions de cette classe sont vides. Pour créer un élément de menu effectuant des choses, il faut faire un héritage et overrider les fonctions nécessaires. Les commentaires de docstring détaillent le rôle de chaque fonction, ce qu'on peut mettre dedans, ce qu'elles doivent renvoyer, etc.

Un élément de menu peut être placé dans un `MenuManager` ou dans un `MenuSubMenu` (un élément de menu spécial stockant d'autres éléments de menu, [voir `MenuSubMenu`](#menusubmpy)).

Un élément de menu peut définir `funcAction()` : une fonction sans paramètre d'entrée, renvoyant un tuple de `IHMSG_*`, pouvant contenir tout ce qu'on veut. Cette fonction représente l'activation de l'élément. Elle est exécutée par le `MenuManager`, lorsque l'élément est focusé et que l'utilisateur appuie sur Espace ou Entrée. La fonction peut également être exécutée dans d'autres circonstances ([voir `MenuSensitiveSquare`](#menusesqpy)).

Si `funcAction()` vaut None, l'élément de menu n'est pas activable.

Le module `menuelem.py` contient également la fonction `cycleFocus()`, qui s'exécute lorsqu'il faut passer le focus à l'élément suivant d'une liste (par exemple, quand l'utilisateur appuie sur Tab). Un gros tas de commentaire au début du fichier décrit le fonctionnement des focus, ainsi que les différents "use cases".

La fonction `cycleFocus()` aurait méritée d'être dans un fichier de code à part, mais je l'ai mise là car elle y est plutôt bien. Elle est utilisée à la fois par le `MenuManager` et le `MenuSubMenu`, donc elle est assez générique.

#### menumng.py ####

Contient la classe `MenuManager` gérant un menu, qui comporte des `MenuElem`.

On peut créer un `MenuManager` de 2 manières différentes :

 - Utliser directement la classe de base. On l'instancie, on place dedans les `MenuElem` en redéfinissant la variable membre `listMenuElem`, puis on appelle la fonction `initFocusCyclingInfo()`. C'est ce qui est fait dans les codes d'exemple du chapitre précédent.

 - Dériver la classe. Dans l'`__init__`, on définit `listMenuElem`, puis on appelle `initFocusCyclingInfo()`. C'est ce qui est fait dans la plupart des menus de Blarg.

Dans les deux cas, l'activation du menu se fait en appelant la fonction `handleMenu()`.

Le terme "activation" est à peu près l'équivalent du "OnActivate" dans les menus Windows ou autre. Il désigne le fait d'afficher le menu, et de démarrer une boucle qui récupère et prend en compte les événements souris et clavier. La boucle s'arrête sur récupération d'un `IHMSG_QUIT` ou d'un `IHMSG_TOTALQUIT`.

Si on dérive, on peut également overrider les fonctions suivantes :

 - `showBackground()` : Fonction affichant l'image de fond, derrière le menu.

 - `beforeDrawMenu()` : Fonction vide. Elle est appelée à chaque fois qu'il faut (re)dessiner tout le menu, juste avant le dessin de l'image de fond et des éléments.

 - `startMenu()` : Fonction vide, s'exécute au début de l'activation d'un menu.

 - `periodicAction()` : Fonction vide, s'exécute au début de chaque cycle, tant que le menu est activé.

Le `MenuManager` envoie systématiquement tous les événements souris et clavier à tous ses éléments de menus, pas seulement à celui qui a le focus. C'est ensuite aux éléments de les gérer ou pas, en fonction de leur focus, ou d'autres choses.

Pour gérer les cyclages de focus, le `MenuManager` maintient 2 listes de `MenuElem`.

 - `listMenuElem` : liste contenant tous les éléments de menu. Utilisée pour cycler lorsque le joueur appuie sur Tab.

 - `listMenuElemArrows` : liste contenant une partie des éléments de menu. Utilisée pour cycler lorsque le joueur appuie sur les flèches haut et bas. (Par exemple, dans le menu principal de Blarg, cette liste contient les texte sélectionnables au milieu de l'écran, mais ne contient pas les mini-options tels que les choix de langue). Cette liste peut être None, dans ce cas, les flèches haut et bas ne font rien.

#### txtstock.py ####

Contient la classe `TextStock`, qui stocke tous les textes du jeu (menu, présentation, ...).

Les textes sont dans le dictionnaire `TextStock.DICT_LANGUAGE`.

 - clé : identifiant d'un texte. Ces identifiants sont définis comme des constantes statiques, au début de `TextStock`.
 - valeur : sous-dictionnaire :
    * clé : identifiants de langage. `LANG_FRENCH` ou `LANG_ENGL`
    * valeur : chaîne de caractère unicode avec le texte dedans.

La classe contient une variable membre `language`, qui indique la langue courante. Il est possible de changer sa valeur.

Le fichier `txtstock.py` effectue immédiatement une instanciation : `txtStock = TextStock()`. Lorsque les autres modules importent le fichier, ils utilisent cet objet instancié. Ça permet au code extérieur d'accéder à la valeur de langue courante sans se prendre la tête.

C'est pour ça que la fonction `MenuElem.changeLanguage` n'a pas de paramètres. Elle sert uniquement à prévenir les éléments de menu que la langue courante a changé. Pour avoir la nouvelle langue, il faut consulter `txtstock.TextStock.language`.

### Modules définissant les éléments de menu ###

Tous les classes définies dans les modules de ce chapitre sont dérivées de `MenuElem`.

#### menukey.py ####

Contient la classe `MenuSensitiveKey`. Élement de menu non focusable, et qui n'affiche rien.

Cet élément réagit à l'appui d'une touche spécifique. Lorsque celle-ci est appuyée, la fonction d'activation `funcAction()` est exécutée.

Ne réagit pas à un lâchage de touche ni à une touche déjà appuyée.

#### menuany.py ####

Contient la classe `MenuSensitiveAnyKeyButton`. Élement de menu non focusable, et qui n'affiche rien.

Cet élement réagit et exécute `funcAction()` sur un appui de touche (n'importe laquelle) et/ou sur un clic de souris. Il est utile pour des menus de transition, du style : "appuyer sur une touche pour passer à l'écran suivant".

#### menuimg.py ####

Contient la classe `MenuImage`. Élément de menu affichant une image.

Non focusable, non cliquable, non activable.

#### menutxt.py ####

Contient la classe `MenuText`. Affiche un texte non interactif.

Pour l'affichage et la config associée (alignement horizontal et vertical, police, couleur, ...), la classe utilise en interne un `Lamoche`, une classe également utilisée dans le jeu lui-même.

Le texte à afficher se définit à l'instanciation, on peut le faire de 2 manières différentes :

 - Indiquer directement une chaîne de caractère dans le paramètre `text`, qui sera affichée tel quelle. Ensuite, le texte peut être changé par un appel à la fonction `changeFontAndText()`.

 - Indiquer un identifiant de texte de `TextStock`. Le texte affichée sera celui défini dans `txtStock.DICT_LANGUAGE`, avec la langue courante. Ensuite, la langue peut être changée en appelant `txtStock.changeLanguage(newLanguage)` puis `MenuText.changeLanguage()`.

Le comportement du `MenuText` n'est pas vraiment prévu dans le cas où on s'amuse à panacher les 2 manières de définir le texte.

<a class="mk-toclify" id="menusesqpy"></a>
#### menusesq.py ####

Contient la classe `MenuSensitiveSquare`. Elément de menu qui n'affiche rien, mais qui est focusable et activable. Il réagit quand on clique ou qu'on passe la souris dans une zone rectangulaire prédéfinie.

On n'utilise jamais directement cette classe, mais on la fait dériver pour avoir des éléments de menu interactifs. (Héritage multiple ou simple).

Cette classe contient 3 variables membres importantes :

 - `rectStimZone` : rectangle définissant la zone sensible, dans l'écran. On peut la définir directement, ou à partir de la variable membre existante `rectDrawZone` (qui aurait été définie par un autre moyen, tel qu'un héritage mulitple).

 - `funcAction()` : [voir `MenuElem`](#menuelempy).

 - `clickType` : indique la manière dont est exécutée `funcAction()` en fonction des événements de la souris. Les différentes valeurs possibles sont les constantes `MOUSE_*`, définies au début du fichier. (Soit ça réagit aux clics, soit ça réagit périodiquement tant que le curseur est dans le rectangle sensible, soit ça réagit jamais).

Quel que soit la valeur de `clickType`, le `MenuSensitiveSquare` demande systématiquement à avoir le focus lorsque le curseur de souris passe sur le rectangle sensible. Pas besoin de cliquer pour prendre le focus.

TRIP: Désolé pour le nom de fonction `treatStimuliMouse`. Il faut bien évidemment lire `processStimuliMouse`. "Treat"... N'importe quoi. Même en français c'est moche, ce verbe "traiter".

#### menuseim.py ####

Contient la classe `MenuSensitiveImage`, héritée de `MenuSensitiveSquare`. Affiche une image.

Cette classe réagit aux clics ou aux mousehovers sur l'image. (Comportement défini dans `MenuSensitiveSquare`).

Lorsque l'élément prend le focus, l'image s'affiche progressivement en plus clair. Lorsqu'il perd le focus, l'image s'affiche progressivement du clair vers le normal.

Les transitions clair<->normal se font sur 8 images. La liste de ces images est stockée dans la variable membre `listImgWithLight`. Elle est précalculée à l'instanciation de la classe, à partir de l'image normale.

Les transitions sont effectuées par la fonction `update()`, exécutée une fois par cycle de jeu. Durant tout le temps de transition, le booléen membre `mustBeRefreshed` est fixé à True, c'est à dire qu'on ne réaffiche pas le menu en entier, mais uniquement cet élément.

#### menusetx.py ####

Contient la classe `MenuSensitiveText`, qui hérite à la fois de `MenuSensitiveSquare` et de `MenuText`.

Je ne sais pas trop comment est censé être géré l'héritage multiple en python. Dans le corps des fonctions, j'ai parfois besoin d'appeler explicitement une fonction de l'une ou l'autre des classes-mères. Ça fonctionne, c'est tout ce que j'attends.

Cette classe affiche un texte, comme `MenuText`. Elle réagit aux clics et aux mousehovers sur l'image, et exécute `funcAction()`, comme `MenuSensitiveSquare`.

Lorsque l'élément prend le focus, le texte se met en mode "glow". Il change de couleur pour aller du blanc vers le bleu vers le blanc vers le bleu, etc. Contrairement au `MenuSensitiveImage`, les changements de couleur se font en yo-yo continu, tant que l'élément possède le focus.

Lorsque l'élément perd le focus, le texte fait une dernière petite transition pour passer progressivement de la couleur en cours vers le blanc.

Les images de textes changeant de couleur ne sont pas pré-calculées. En interne, on change la couleur du `Lamoche` et on fait un `font.render()` à chaque fois.

La liste des couleurs pour le glow est définie dans la variable membre `glowColorList`.

Le glow et la transition "glow->normal" sont effectuées par la fonction `update()`, exécutée à chaque cycle de jeu. Pendant un glow/transition, on ne réaffiche pas le menu en entier, mais uniquement cet élément.

#### menulink.py ####

Contient la classe `MenuLink`, héritée de `MenuSensitiveText`.

Texte cliquable et focusable. La fonction `funcAction()` pointe vers la fonction `mactQuitFullScreenAndGoToDaInterWeb`. Cette fonction désactive le mode plein écran (si on est actuellement dans ce mode) et ouvre le navigateur internet par défaut en lui fournissant l'url correspondant au texte de l'élément de menu.

Pour ouvrir le navigateur par défaut vers une url, on utilise `webbrowser.open()` (présent dans la librairie standard). Comme on n'est pas sûr que cette librairie existe sur tous les systèmes, il y a un try-catch au moment de son import.

Si l'import a échoué, lorsque l'utilisateur clique sur l'élément, on se contente de logger l'url vers la sortie standard. Comme ça le jeu peut fonctionner sur des systèmes bizarres n'ayant pas de navigateur.

#### menutick.py ####

Contient la classe `MenuSensitiveTick`, qui hérite à la fois de `MenuSensitiveImage` et de `MenuText`.

Cet élément de menu affiche à la fois une image (case à cocher) et un texte. La variable membre `rectDrawZone` est égale à la fusion des deux rectangles de l'image et du texte. La variable membre `rectStimZone` est déduite de `rectDrawZone`, avec une petite marge à chaque bord, comme pour la plupart des autres éléments cliquables.

Lorsque cet élément a le focus, l'image de la case (cochée ou pas) s'affiche progressivement en plus clair (comme le `MenuSensitiveImage`). Cet élément a donc besoin de deux listes d'images différentes. Une liste de case cochée, de plus en plus claires. Et une liste de case pas cochée, de plus en plus claires. Tout cela doit être initialisé préalablement et transmis lors de l'instanciation, via le paramètre `dicTickImage`.

En l'état, la classe `MenuSensitiveTick` ne modifie pas la valeur de son cochage lorsqu'elle est activée. Pour cela, il faut overrider `funcAction()`, pour y appeler la méthode `toggleTick()`. J'ai fait exprès de rendre ça explicite, comme ça on peut désactiver le cochage/décochage si on a envie. Et on peut effectuer d'autres actions spécifiques dans `funcAction()`.

La valeur de cochage courante est stockée dans la variable membre `boolTickValue`.

On peut associer une valeur littérale à chacune des deux valeurs cochée/décochée. Pour cela, il faut passer les paramètres `dicLiteralFromBool` et `literalValInit` au moment de l'instanciation. Lorsque c'est défini, la variable membre `self.literTickValue` contient la valeur littérale courante.

#### menuedtx.py ####

Contient la classe `MenuEditableText`, héritée de `MenuSensitiveText`. Il s'agit d'une zone de texte éditable. L'élément est focusable, mais pas cliquable ni activable (`funcAction()` est None).

À priori, tous les caractères bizarres peuvent être écrits (accents, majuscules, trémas, ...). L'utilisateur peut appuyer sur backspace pour effacer la dernière lettre.

C'est malgré tout un peu rustique pour une zone de texte :

 - Le curseur reste toujours à la fin du texte.
 - Les flèches gauche et droite ne font rien.
 - On ne peut pas sélectionner tout ou partie du texte.
 - On ne peut pas faire de copier-coller.

La valeur courante du texte saisi est accessible par le `Lamoche` interne, c'est à dire : `self.theLamoche.text`.

La classe override la fonction `MenuElem.takeStimuliKeys()`, afin de récupérer les appuis de touche et d'en déduire les modifications à appliquer au texte saisi. Lorsqu'une modif est faite, on envoie le message `IHMSG_REDRAW_MENU`, afin de demander un redessin global du menu. On est obligé d'effacer entièrement le texte précédent puis de réafficher le texte courant, sinon ça fait des superpositions dégueulasses.

L'élément est un `MenuSensitiveSquare` (puisque c'est un `MenuSensitiveText`), mais avec `clickType = MOUSE_NONE`. Donc quand on clique dessus, il ne se passe rien. Cependant, le focus est attribué à cet élément lorsqu'on passe la souris dessus. Les saisies de texte ne sont prises en compte que quand l'élément a le focus.

Contrairement au `MenuSensitiveText`, le texte est toujours affiché en blanc, même lorsqu'il y a le focus. C'est le curseur qui change de couleur en continu : bleu -> blanc -> bleu -> blanc...

Lorsqu'il n'y a pas le focus, le curseur est bleu (et non pas blanc). C'est important que le curseur soit d'une couleur différente que le texte, sinon ça embrouille.

L'affichage du texte et du curseur est géré par la fonction `draw()`. La modification périodique de la couleur du curseur est effectuée par la fonction `MenuSensitiveText.update()` (cette classe n'override pas la fonction). Donc l'index de couleur évolue pareil que dans le `MenuSensitiveText`, mais la liste de couleur (`glowColorList`) n'est pas la même.

#### menukrec.py ####

Contient la classe `MenuOneKeyRecorder`. Élément de menu non focusable et qui ne s'affiche pas, mais qui peut quand même exécuter une `funcAction()`.

Cet élément possède deux fonctions spécifiques : `activateRecording()` et `desactivateRecording()`, permettant d'activer et désactiver l'enregistrement des touches.

Lorsque l'enregistrement est activé, les appuis de touches sont enregistrés. Seul le dernier appui est gardé en mémoire. Il est accessible par les variables membres `keyRecorded` (code numérique de la touche appuyée) et `charKeyRecorded` (caractère correspond à la touche appuyée).

De plus, lorsque l'enregistrement est activé, `funcAction()` est exécutée à chaque appui de touche.

Dans Blarg, c'est cet élément qui permet de configurer les touches du jeu.

<a class="mk-toclify" id="menusubmpy"></a>
#### menusubm.py ####

Contient la classe `MenuSubMenu`. Élément de menu top génial, dans lequel on met d'autres éléments de menu. Ces "sous-éléments" peuvent être de n'importe quel type.

Le sub-menu s'affiche dans un rectangle définie par `rectDrawZone` (transmis à l'instanciation). L'affichage ne déborde jamais de ce rectangle.

Les coordonnées des sous-éléments sont définies par rapport à une zone interne au sub-menu, et non pas par rapport à l'écran. C'est à dire qu'un sous-élément en coordonnée (0, 0) apparaîtra à la coordonnée `(MenuSubMenu.rectDrawZone.x, MenuSubMenu.rectDrawZone.y)` de l'écran.

La zone interne peut être plus grande que `rectDrawZone`, elle peut même être plus grande que l'écran. Sa taille est définie par la taille de la variable membre `surfaceInside` (objet `pygame.Surface`).

L'aspect graphique général du sub-menu est initialisé par la fonction `renderElemInside()`. Cette fonction détermine la taille de la zone interne à partir des sous-éléments et de leurs `rectDrawZone`, puis elle les dessine dans `surfaceInside`. Cette fonction est appelée à l'instanciation et lors d'un changement de langue.

La fonction `SubMenu.draw()` redessine les sous-éléments ayant leur valeur `mustBeRefreshed` à True, puis extrait un sous-rectangle de `surfaceInside` pour l'afficher à l'écran, à la position de `rectDrawZone`.

Le sous-rectangle est défini par la variable membre `sourceRectToBlit`. Si la zone interne est plus grande que l'écran, `sourceRectToBlit` n'en prend qu'une partie. On ne voit donc pas le sub-menu en entier.

Des fonctions spécifiques (`scrollVertically()` et `scrollSetPosition()`) permettent de déplacer verticalement `sourceRectToBlit`, afin de faire scroller la zone interne. On ne peut pas scroller horizontalement, car je n'en ai pas eu besoin pour Blarg.

À priori il y aurait un bug : si un quelconque élément de menu envoie `IHMSG_REDRAW_MENU`, on est censé redessiner tous les éléments (et sous-éléments) de menu. Mais au moment de redessiner le sub-menu, celui-ci inspecte ces sous-éléments et ne redessine que ceux ayant `mustBeRefreshed` à True.

Pour forcer un redessin complet, il faudrait appeler `renderElemInside()`. Le problème, c'est que quand le `MenuManager` exécute la fonction `draw()` d'un élément, il ne précise pas si c'est pour un redessin complet ou pour un rafraîchissement simple. Pour un élément simple, c'est indifférent, pour un sub-menu, ça a son importance. Je laisse comme ça, tant pis pour le bug.

Les événements souris sont transmis aux sous-éléments (en tenant compte des décalages de coordonnées dus au scrolling vertical et à la position du sub-menu à l'écran).

Les événements de touche ne sont pas transmis. Il faudrait le faire, mais je n'en ai pas eu besoin.

Les cyclages de focus sont transmis. C'est à dire que lorsque le sub-menu reçoit un événement de cyclage, il fait cycler le focus en interne, dans ses sous-éléments. Celui ayant le focus est indiqué par la variable membre `focusedElemInside`. Tant qu'on n'est pas arrivé au dernier sous-élément, le sub-menu répond qu'il ne veut pas lâcher le focus (il ne renvoie pas le message `IHMSG_CYCLE_FOCUS_OK`). Lorsqu'on est arrivé au dernier sous-élément et que l'utilisateur cycle une dernière fois, on accepte de lâcher le focus.

Le sub-menu possède une `funcAction()`, mais elle n'est pas censée être overridée. Cette `funcAction()` exécute la `funcAction()` du sous-élément ayant actuellement le focus interne. De cette manière, l'événement d'activation est propagé. Lorsque l'utilisateur appuie sur Espace ou Entrée, c'est le sous-élément actuellement focusé qui est activé.

Dans Blarg, le sub-menu permet d'afficher le texte scrollable des Credits (liens vers mes sites, noms des contributeurs, lien vers la licence, ...).

En théorie, on devrait pouvoir mettre un sub-menu dans un sub-menu dans un sub-menu etc. Mais je n'ai pas testé.

### mot-clé utilisés dans les noms de variables ###

`mact` : "menu action". Il s'agit d'une fonction, attribuée à une `funcAction()`.

`mbutt` : "menu button". Un élément de type `MenuSensitiveText` (texte cliquable).

`mbuttLink` : "menu button link". Un élément de type `MenuLink`, constituant un lien vers un site web.

`mbuti` : "menu button image". Un élément de type `MenuSensitiveImage` (image cliquable).

`mkey` : "menu key". Un élément de type `MenuSensitiveKey` (réaction à une touche spécifique).

`many` : "menu any key". Un élément de type `MenuSensitiveAnyKeyButton` (réaction à n'importe quelle touche ou clic).

"Création du menu" : Instanciation d'un `MenuManager`, ou d'une classe héritée.

"Activation du menu" : affichage et activation du `MenuManager` à l'écran, via la méthode `handleMenu()`.

## Description des menus spécifiques de Blarg ##

### Déroulement des actions lors du lancement du jeu ###

#### zemain.py ####

Il s'agit du point d'entrée du jeu. Ce fichier effectue les actions suivantes :

 - Récupération du paramètre optionnel passé en ligne de commande, pour forcer le lancement du jeu en mode fenêtré.

 - Initialisation de pygame, et fermeture de pygame à la fin.

 - Instanciation et activation de la classe principale, définie dans le fichier `mainclas.py`.

#### mainclas/MainClass ####

Les initialisations de tout le bazar sont effectuées en partie dans la fonction `__init__()` et en partie dans la fonction `main` (qui est appelée juste après l'init). Il n'y a pas vraiment de justification sur le fait que certaines actions sont dans l'init et d'autres sont dans le main. J'ai fait ça un peu au feeling.

En vrac, les actions effectuées sont les suivantes :

 - Chargement des polices de caractères (bon y'en a qu'une en fait).

 - Création d'un `Archivist`, permettant de charger/sauvegarder les données dans le fichier `dichmama.nil`.

 - Modification de l'icône de l'application, qui est censé apparaître dans la barre des tâches ou le dock.

 - Création d'une fenêtre, ou activation du mode plein écran (selon la config et les paramètres). Récupération de l'objet `pygame.Surface` correspondant à la zone de dessin à l'écran.

 - Initialisation de la classe `Game` permettant de jouer des parties. (voir DOC_CONCEPTION_jeu) TODO : link

 - Déroulement de la mini-animation de présentation, définie dans le fichier `prezanim.py`.

 - Chargement de tous les sons du jeu. Cette action peut prendre quelques secondes, elle est donc effectuée dans `prezanim.py`, après l'affichage de la première image (avec le texte "LOADINGE"), et avant le déroulement de l'animation.

 - Création de tous les menus du jeu, via le fichier `menugen.py`. Rangement de ces menus dans le dictionnaire `MainClass.dicAllMenu`.

 - Si le chargement du fichier de sauvegarde par l'`Archivist` a raté (fichier inexistant, ou une raison pllus grave) : création et sauvegarde d'un fichier contenant des informations par défaut. Si la sauvegarde échoue également, on garde les données par défaut et on continue l'exécution (un message d'erreur est émis sur stdout).

 - Si c'est le tout premier lancement du jeu (on le sait grâce à l'`Archivist`) : exécution de la fonction `MainClass.doFirstTimeLaunch()`.

 - Ajout de l'option "God Mode" (mode invincible) dans le menu principal, si le nom saisi lors du premier lancement correspond au nom secret.

 - Activation du menu principal, via cette ligne de code : `self.dicAllMenu[MENU_MAIN].handleMenu()`

 - Le joueur peut interagir avec le menu, démarrer une partie, changer la config, ...

 - Lorsque la fonction `handleMenu()` du menu principal se termine, c'est que le joueur a quitté (d'une manière ou d'une autre).

 - La fonction `MainClass.main()` se termine, ainsi que le code du fichier `zemain.py`.

La classe `MainClass` contient une variable `nbrErreur`, qui est incrémentée lors de la détection d'une erreur. En général, un incrément est toujours accompagné d'une description de l'erreur envoyée sur la sortie standard. Mais peut-être pas tout le temps.

Des erreurs peuvent survenir lors de l'initialisation (chargement des fichiers, etc.). Mais il n'y a pas de détection d'erreur pendant le `handleMenu()` du menu principal, ni des autres menus. Par contre, il peut y en avoir pendant le déroulement d'une partie. La fonction `theGame.playOneGame()`, renvoie, entre autres, une variable `errorInGame`.

##### fonction doFirstTimelaunch() #####

Exécute les actions à faire lors du premier lancement du jeu.

Il y a quelques menus supplémentaires à afficher avant le menu principal (l'histoire du jeu, la description des touches, la saisie du nom du joueur). Les fonctions `handleMenu()` sont exécutés les unes après les autres. Il y a, dans chacun de ces menus, un moyen simple pour le joueur de le quitter, et donc de passer au suivant. En général, il suffit juste d'appuyer sur une touche.

Le nom saisi est enregistré dans le fichier de sauvegarde. Ensuite, il est hashé avec du SHA-512, puis comparé avec le hash du nom magique permettant de débloquer le mode invincible.

##### fonction mactPlaySeveralGames() #####

Lance une ou plusieurs parties, les unes après les autres, et enregistre le score obtenu à chaque fin de partie.

Cette fonction est envoyée en paramètre au menu principal, ce qui lui permet de l'exécuter lorsque l'utilisateur clique sur l'option "Jouer".

Pour plus de détail : doc conception jeu. chapitre "Lancement d'une partie" (TODO : link)

#### prezanim/PresentationAnim ####

Cette classe effectue les actions suivantes :
 - Chargement des images nécessaires à la présentation.
 - Affichage d'une première image, avec le texte "LOADINGE". Cette action est effectuée le plus vite possible, afin de montrer au joueur qu'il se passe bien quelque chose.
 - Pré-calcul des différentes images du titre. Il apparaîtra agrandi au début puis se réduit petit à petit.
 - Chargement des sons.
 - Exécution de l'animation. Un objet `pygame.time.Clock` gère le FPS. À chaque cycle, on affiche les images en les déplaçant.
   * Le magicien se déplace de droite à gauche.
   * Morac se déplace de gauche à droite, en même temps le magicien recule un peu.
   * Le titre apparaît en gros, puis se réduit.

Lorsque l'animation est terminée, l'image finale est récupérée (fond + magicien + Morac + titre), elle est fortement assombrie, puis elle est stockée dans `imgBgMainMenu`. Le code extérieur (`MainClass`) récupérera cette image, qui sera utilisée comme fond pour le menu principal.

L'image du texte "Blarg" est également récupérée et réutilisée de la même manière (variable `imgTitle`). Aucun traitement n'est appliqué dessus. C'est juste pour éviter de charger deux fois la même image à deux endroits différents du code.

#### menugen.py ####

Contient une seule grosse fonction `generateAllMenuManager()`, qui effectue les actions suivantes :

 - Chargement de toutes les images nécessaires aux menus : boutons, pseudo-fenêtre, ...
 - Précalcul des images de tickBox (voir menutick.py TODO lien)
 - Création des menus, un par un, et rangement dans un dictionnaire `dicAllMenu`. Chaque menu est associé à une clé (valeur numérique). Les clés sont définis dans `menucomn.py`, il s'agit des variables commençant par `MENU_`, et elles sont utilisées un peu partout dans le code.
 - Récupération de la langue courante, stockée dans le fichier de sauvegarde, transmise par l'`Archivist`.
 - Application du changement de langue courante sur tous les menus, afin de les initialiser.
 - Renvoi de `dicAllMenu`.

#### menuzmai/MenuManagerMain ####

Classe définissant le menu principal du jeu. Il y a beaucoup de choses, mais c'est assez simple. Les commentaires dans le code sont suffisants.

Quelques détails :

Il y a un `MenuImage` affichant le titre "Blarg". Pourtant, ce titre est déjà présent dans l'image de background du menu principal. (Voir prezanim TODO : link). Mais dans l'image de background, il est assombri. On le réaffiche par dessus en pas-assombri, pour que ça ressorte bien.

L'élément `mkeyQuitEsc` est utilisé dans plusieurs menus. Il réagit à un appui sur la touche Esc, et envoie un message demandant à quitter le menu en cours. Dans le menu principal, le fait de quitter le menu en cours fait quitter complètement le jeu.

Les `MenuElem` sont rangés dans trois listes :
 - `listMenuElemButtText` : liste des options textes (jouer, high scores, ...)
 - `listMenuElemOther` : liste avec tous les autres éléments.
 - `listMenuElem` : tous les éléments (concaténation des deux listes précédentes).

Ça permet de définir plus facilement le cyclage de focus avec les flèches haut et bas. (voir menumng.py TODO lien). Ce cyclage se fait sur les éléments de `listMenuElemButtText`.

Ça permet aussi de rajouter plus facilement une option texte : on modifie `listMenuElemButtText` et on reconstruit `listMenuElem`. C'est ce qui est fait lorsqu'il faut rajouter l'option du mode invincible (fonction `MenuManagerMain.addDogDom`).

Pour rappel : "DogDom", "EdomEdog" et les termes de ce genre sont une façon stupidement obfusquée de mentionner le "god mode", le mode invincible.

#### menuzwak/MenuManagerWaitOrPressAnyKey ####

Menu utilisé pour la transition entre la présentation du jeu et le menu principal.

Ce menu attend que le joueur appuie sur une touche, puis il se quitte. (Le code extérieur s'occupe ensuite d'activer le menu principal). Il y a également un timer, qui fait quitter automatiquement le menu au bout de 100 cycles, si le joueur n'appuie pas sur une touche.

Ce menu n'affiche absolument rien. Le seul `MenuElem` qu'il possède ne dessine rien à l'écran, et il n'a pas d'image de background. Donc lorsqu'on l'active, ce qui était précédemment affiché reste à l'écran, à savoir : la dernière image de l'animation de présentation.

#### menuzsto/MenuManagerStory ####

Contient 3 éléments :
 - un `MenuSubMenu` contenant plusieurs textes, décrivant l'histoire du jeu. La `Surface` d'affichage de ce submenu est plus grande (en hauteur) que l'écran. Tous les textes sont placés dans la partie basse de la `Surface`, on ne les voit pas au début. La fonction `periodicAction` du menu décale progressivement la zone à afficher à l'écran, vers le bas. On voit donc le texte qui apparaît progressivement, à partir du bas de l'écran.
 - le `mkeyQuitEsc`
 - un `MenuSensitiveAnyKeyButton`. Si le joueur appuie sur une touche et que le décalage de la zone n'est pas fini, on applique un gros décalage qui termine immédiatement le scroll. Si le décalage est fini, l'appui de touche fait quitter le menu.

C'est donc un peu étrange, car on a deux éléments qui réagissent à des appuis de touche. Lorsque le joueur appuie sur Esc, il y a donc deux `funcAction` qui sont exécutées, et qui potentiellement peuvent demander tous les deux à quitter le menu en cours. Ça ne pose pas de problèmes.

#### menuzman/MenuManagerManual ####

Menu non interactif, affichant le manuel du jeu. L'élément `manyQuit` fait quitter sur un appui de touche ou un clic. Tous les autres éléments ne sont pas interactifs :

 - `self.mimgManual` : grosse image affichant le manuel.
 - `self.listMenuText` : Les `MenuText` décrivant les 3 actions du héros. "mouvement", "pan", "recharger".
 - `listMenuTextKey` (définis dans `__init__`) : Les `MenuText` affichant les noms des touches associées aux actions.

Les éléments de `listMenuTextKey` sont également stockés dans le dictionnaire `self.dicMenuElemKey`.
 - Clé : identifiant de touche permettant au héro d'effectuer une action. (KEY_DIR_UP, KEY_FIRE, KEY_RELOAD, ...)
 - Valeur : `MenuText`, affichant le nom de la touche mappée.

Ce menu sera hérité pour créer `MenuManagerConfig` (menu permettant de configurer les touches). Certaines fonctions sont utilisées dans les deux menus : `initCommonStuff()` et `determKeyNameFont()`.

#### menuznam/MenuManagerEnterName ####

Menu apparaissant uniquement au premier lancement du jeu, pour demander au joueur de saisir son nom.

Il contient les éléments suivants :

 - `mimgFrameName` : image de la fenêtre de saisie du nom. J'ai appelé ça "frame name", pour faire comme si c'était une fenêtre. Mais en fait c'est juste une image statique donnant l'impression que c'est une sorte de fenêtre.
 - `mtxtEnterName` : texte non interactif, indiquant au joueur qu'il doit entrer son nom.
 - `self.meditPlayerName` : instance de `MenuEditableText`. Zone de saisie du texte.
 - `mbutiOK` : instance de `MenuSensitiveImage`. Bouton OK.
 - `mkeyQuitCancel`, `mkeyEnterOK_1`, `mkeyEnterOK_2` : réactions à des touches du clavier. Echap pour quitter et les deux touches entrée pour valider.

Toute l'interface de saisie du texte est gérée directement par `self.meditPlayerName`. La valeur finale du texte saisi se trouve dans `self.nameTyped`. Ce menu ne s'en sert pas, mais le code extérieur peut la récupérer pour en faire ce qu'il veut.

#### menuzpof/MenuManagerNameIsALie ####

Menu apparaissant uniquement au premier lancement du jeu, après que le joueur ait saisi son nom.

Menu non interactif. L'élément `manyQuit` fait quitter sur un appui de touche ou un clic. Tous les autres éléments ne sont pas interactifs.

Le menu contient 4 `MenuText`, mais seuls deux sont affichés. Les deux premiers (`self.listMenuTextNorm`) dans le cas où le joueur a saisi un nom quelconque. Les deux derniers (`self.listMenuTextDogDom`) dans le cas où le joueur a saisi le nom secret permettant de débloquer le mode invincible.

Par défaut, c'est le texte normal qui est affiché. Pour passer au texte du nom secret, le code extérieur doit appeler la fonction `MenuManagerNameIsALie.setNameTyped(self, nameTyped)`, avant d'activer le menu.

#### menuzdea/MenuManagerHeroDead ####

Menu apparaissant à la fin d'une partie, lorsque le joueur est mort.

Contient des `MenuText` affichant le score et le nombre de magiciens tués/explosés lors de la partie. La mise à jour de ces valeurs est effectuée par la fonction `updateMenuTextStat()`, que le code extérieur doit appeler avant d'activer le menu.

Ce menu contient deux éléments interactifs :

 - `mkeyQuitEsc` : élément générique. Il réagit à l'appui sur la touche Echap, et renvoie le message `IHMSG_QUIT`, permettant d'indiquer qu'il faut quitter le menu.

 - `mkeyPlayOnceMore` : élément réagissant à l'appui sur la touche Entrée. Il renvoie un tuple de deux message : `IHMSG_QUIT` et `IHMSG_PLAY_ONCE_MORE`. Ce dernier message, contrairement à tous les autres, est spécifique au jeu Blarg. Le système de menu ne s'en sert jamais. Lorsque le menu se quitte, le code extérieur contrôle la présence de ce message pour déterminer si il faut jouer une nouvelle partie ou pas. (Voir fonction `mactPlaySeveralGames` TODO lien).

L'image de fond de ce menu est différente des autres. (Image du héros mort transformé en potion de mana).

#### menuzsco/MenuManagerHighScore ####

Menu affichant les scores. Menu non interactif. L'élément `manyQuit` fait quitter sur un appui de touche ou un clic. Tous les autres éléments ne sont pas interactifs.

Lors de l'instanciation, il faut lui passer un `Archivist` en paramètre. Le menu s'occupe de récupérer les valeurs de score et d'effectuer les calculs nécessaires pour afficher les scores.

L'`Archivist` ne stocke pas la valeur du meilleur score, uniquement les nombres de magiciens tués et explosés durant la partie ayant créé le meilleur score. (Il stocke d'autres statistiques, dont certaines ne servent à rien, mais c'est pas grave).

Il faut donc recalculer le meilleur score à partir des nombres de magiciens. C'est le menu qui s'occupe de cette tâche, en appelant la fonction `scoremn.scoreFromKillBurst()`. C'est la même fonction utilisée pour calculer le score pendant le jeu. Ça permet de garantir que le calcul effectué est le même dans tous les cas. (Certes, c'est un calcul super simple, mais ça me semblait important de le définir à un seul endroit, car ce n'est pas une opération anodine).

À chaque fois que le menu est activé, l'ensemble de ces `MenuText` est regénéré. Il y en a de 2 sortes. Les "statiques" affichant le texte statique, et les "scoriques", affichant les valeurs de score.

Les MenuText sont organisés par bloc. Un bloc = un joueur. La fonction `buildOnePlayerMenuText()` génère les `MenuText` d'un bloc.

La fonction `getHiScoreStat` récupère une stat de score à afficher.

Tout cela est un peu alambiqué, mais c'est pas grave. C'est de l'alambiqué local.

#### menuzcre/MenuManagerCredits ####

Menu affichant le texte des crédits. Il est constitué des éléments suivants :

 -

#### menuzcon/MenuManagerConfig ####









