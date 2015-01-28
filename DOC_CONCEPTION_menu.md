# Document de conception de Blarg (système de menu) #

Ce document décrit la manière dont est organisé le système de menu de Blarg (menu principal, config des touches, affichage des scores, ...). Il ne décrit pas comment le code du jeu en lui-même est organisé.

## Introduction ##

Le code est assez densément commenté. Ce document se bornera donc à décrire sommairement le but de chaque classe.

Durant la réalisation de ce jeu, le PEP8 a été foulé aux pieds, écartelé, équarri et humilié en place publique par des petits enfants jetant des cailloux. C'est la faute à l'entreprise dans laquelle je bossais à l'époque, qui m'a appris à coder en python avec les conventions de nommage du C++. Il va falloir faire avec !

Le système de menu se veut le plus générique et le plus réutilisable possible. Même si en réalité, euh... Bref.

Les noms des fichiers de code définissant le système de menu générique commencent tous par "menu". Les noms des fichiers de code définissant les menus spécifique à Blarg commencent tous par "menuz". J'aurais dû ranger tout ça correctement dans des répertoires, mais j'étais un vilain.

## Description du système de menu générique ##

### Menus d'exemple ###

Des exemples simples, indépendants du jeu, ont été créés, afin de donner une première idée de ce que peut faire le système de menu.

Pour les exécuter, ouvrir une console, et utiliser les commandes suivantes :

    cd <emplacement_de_ce_repository>
    cd code
    python menudemo.py 1

Il y a 3 exemples de menus. Remplacer le "1" à la fin de la dernière commande par "2" ou "3" pour les lancer.

Il faut avoir installé python et les dépendances nécessaires. Si vous avez réussi à exécuter le jeu à partir de son code source, les exemples de menus s'exécuteront sans problème. Pour installer le jeu à partir du code source, voir autre document pas encore fait.

(TODO : https://github.com/darkrecher/Kawax/blob/master/doc_diverses/installation_et_exe_build.md)

Le code de ces exemples de menu contiennent des commentaires et des docstrings, qui sont à priori suffisants. Pour une meilleure compréhension, les fichiers sont à consulter dans l'ordre suivant :
 - code/menudemo.py
 - code/menudemo_files/launch_demo_menu_empty.py
 - code/menudemo_files/launch_demo_menu_label.py
 - code/menudemo_files/menuelem_event_teller.py
 - code/menudemo_files/launch_demo_menu_event_teller.py

### Diagramme de classe ###

TODO.

### Modules définissant le fonctionnement des menus ###

#### Valeurs IHMSG_* ####

IHMSG = "IHM Message".

Il s'agit de constantes permettant d'échanger des informations entre les `MenuElem` et le `MenuManager`. On peut en placer plusieurs dans un même message (par exemple, pour demander un redessin du menu, et en même temps signaler qu'on accepte le focus). Un message est constitué d'un tuple de 0, 1 ou plusieurs IHMSG.

La liste des IHMSG est définie dans `common.py`

 - `IHMSG_QUIT` : on veut quitter le menu courant, pour revenir au truc qu'on faisait avant.
 - `IHMSG_TOTALQUIT` : on veut totalement quitter tout le jeu.
 - `IHMSG_REDRAW_MENU` : Le menu doit être entièrement redessiné. (Le fond + tous les éléments).
 - `IHMSG_ELEM_CLICKED` : l'élément de menu s'est fait cliquer dessus.
 - `IHMSG_ELEM_WANTFOCUS` : l'élément de menu veut avoir le focus.
 - `IHMSG_CYCLE_FOCUS_OK` : on fait un cyclage de focus (Tab). L'élément de menu actuellement focusé accepte de lâcher le focus pour le transmettre à l'élément suivant.
 - `IHMSG_PLAY_ONCE_MORE` : message spécial utilisé dans un seul cas : quand on quitte le menu affichant que le héros est mort. Sert à indiquer que le joueur veut rejouer. C'est à ça que ça sert.
 - `IHMSG_CANCEL` : le joueur veut annuler le truc en cours.

Pour indiquer un message sans aucun IHMSG, il suffit d'utiliser un tuple vide. Comme je suis super malin, je me suis dit que j'allais créer une constante égal au tuple vide, afin d'exprimer qu'on veut renvoyer un message sans IHMSG. (Une sorte de typage spécifique, ou une lubie du genre). La constante s'appelle `IHMSG_VOID`.

Du coup, pour renvoyer un message vide, on écrit `IHMSG_VOID`, sans parenthèse. Et pour renvoyer un message contenant un IHMSG, on écrit `(IHMSG_REDRAW_MENU, )`, avec parenthèses. Ça fait un peu bizarre. Tant pis !

#### menucomn.py ####

Diverses fonctions et constantes communes au système de menu.

C'est principalement utilisé par la partie spécifique (les menu du jeu Blarg), mais la partie générique (le système de menu) utilise parfois une ou deux constantes contenues dans ce fichier. D'ailleurs c'est pas très bien, il faudrait essayer de séparer.

#### menuelem.py ####

Définition générique d'un élément de menu.

La classe `MenuElem` contient plusieurs fonctions presque vides. Pour créer un élément de menu effectuant des choses, il faut hériter ce `MenuElem` et overrider les fonctions nécessaires. Les commentaires de docstring détaillent le rôle de chaque fonction, ce qu'on peut mettre dedans, ce qu'elles doivent renvoyer, etc.

Un élément de menu peut être placé dans un `MenuManager`, ou bien dans un `MenuSubMenu` : un élément de menu spéciale, capable de stocker d'autres éléments. (Voir plus loin).

Un élément de menu peut définir `funcAction` : une fonction sans paramètre d'entrée, renvoyant un tuple de `IHMSG_*`, pouvant contenir tout ce qu'on veut. Cette fonction représente l'activation de l'élément. Elle est exécutée par le `MenuManager`, lorsque l'élément est focusé et que l'utilisateur appuie sur Espace ou Entrée. La fonction peut également être exécutée dans d'autres circonstances (voir `MenuSensitiveSquare`).

Si `funcAction` est None, l'élément de menu n'est pas activable.

Le module `menuelem.py` contient également la fonction `cycleFocus`, qui s'exécute lorsqu'il faut passer le focus d'un élément de menu à l'élément suivant dans une liste (par exemple, quand l'utilisateur appuie sur Tab). Un gros tas de commentaire au début du fichier décrit le fonctionnement des focus, ainsi que les différents "use cases".

La fonction `cycleFocus` aurait méritée d'être dans un fichier de code à part, mais je l'ai mise là car elle y est plutôt bien. Elle est utilisée à la fois par le `MenuManager` et le `MenuSubMenu`, donc elle est assez générique.

#### menumng.py ####

Contient la classe `MenuManager`, qui gère un menu, comportant des `MenuElem`.

On peut s'en servir de 2 manières différentes :

 - Utliser directement le `MenuManager`. On l'instancie, on place dedans les `MenuElem` en redéfinissant directement la variable membre `listMenuElem`, puis on appelle la fonction `initFocusCyclingInfo`, et ça fonctionne. C'est ce qui est fait dans les codes d'exemple du chapitre précédent.

 - Dériver le `MenuManager`. Dans l'`__init__` de la classe dérivée, on définit directement `listMenuElem`, puis on appelle `initFocusCyclingInfo`. C'est ce qui est fait dans la plupart des menus de Blarg.

Si on dérive, on peut également overrider les fonctions suivantes :

 - showBackground : Fonction affichant l'image de fond, derrière le menu.

 - beforeDrawMenu : Fonction vide. Elle est appelée à chaque fois qu'il faut (re)dessiner tout le menu, juste avant le dessin de l'image de fond et des éléments de menu.

 - startMenu : Fonction vide. Elle s'exécute au début de l'activation d'un menu. (Activation = lorsqu'on affiche le menu et qu'il récupère les événements souris et clavier. Équivalent du "OnActivate" dans les menus Windows ou autre).

 - periodicAction : Fonction vide. Elle s'exécute au début de chaque cycle, tant que le menu est activé.

Pour gérer les cyclages de focus, le `MenuManager` maintient 2 listes de `MenuElem`.

 - `listMenuElem` : la liste contenant tous les éléments de menu. Utilisée pour cycler lorsque le joueur appuie sur Tab.

 - `listMenuElemArrows` : liste contenant une partie des éléments de menu. Utilisée pour cycler lorsque le joueur appuie sur les flèches haut et bas. (Par exemple, dans le menu principal de Blarg, cette liste contient les éléments de texte sélectionnables, affichés au milieu de l'écran). Cette liste peut être None, dans ce cas, les flèches haut et bas ne font rien.

#### txtstock.py ####

Contient la classe `TextStock`, qui stocke tous les textes du jeu (menu, présentation, ...).

Les textes sont stockés dans un grand dictionnaire : `TextStock.DICT_LANGUAGE`.

 - clé : identifiant d'un texte. Ces identifiants sont définis comme des constantes statiques, au début de `TextStock`.
 - valeur : sous-dictionnaire :
    * clé : identifiants de langage. `LANG_FRENCH` ou `LANG_ENGL`
    * valeur : chaîne de caractère unicode avec le texte dedans.

La classe contient une variable membre `language`, qui indique la langue courante. Il est possible de changer sa valeur.

Le fichier `txtstock.py` effectue immédiatement une instanciation : `txtStock = TextStock()`. Lorsque les autres modules importent le fichier, ils utilisent cet objet instancié, contenant la langue courante. Ça permet de partager la valeur de langue courante entre tous les modules, sans se prendre la tête.

C'est pour ça que la fonction `MenuElem.changeLanguage` n'a pas de paramètres. Cette fonction sert à prévenir un élément de menu que la langue courante a changé. Pour avoir la nouvelle langue, il suffit de consulter l'instance dans `txtstock.py`.

### Modules définissant les éléments de menu ###

Tous les modules de ce chapitre définissent des classes qui sont dérivées de `MenuElem`.

#### menukey.py ####

Contient la classe `MenuSensitiveKey`. Élement de menu qui n'affiche rien, et qui est non focusable.

Cet élément réagit à l'appui d'une touche spécifique. Lorsque celle-ci est appuyée, la fonction d'activation `funcAction` est exécutée.

Ne réagit pas à un lâchage de touche ni à une touche déjà appuyée.

#### menuany.py ####

Contient la classe `MenuSensitiveAnyKeyButton`. Élement de menu qui n'affiche rien, et qui est non focusable.

Cet élement réagit à un appui de touche (n'importe laquelle) et/ou un clic de souris. Il est utile pour des menus de transition, du style : "appuyer sur une touche pour passer à l'écran suivant".

#### menuimg.py ####

Contient la classe `MenuImage`. Élément de men qui affiche une image.

Non focusable, non cliquable, non activable.

#### menutxt.py ####

Contient la classe `MenuText`. Affiche un texte non interactif.

Pour l'affichage et la config qui va avec (alignement horizontal et vertical, font, couleur, ...), la classe utilise en interne un `Lamoche`, une classe qui est également utilisée dans le jeu en lui-même.

Le texte à afficher se définit à l'instanciation, on peut le faire de 2 manières différentes :

 - Indiquer directement une chaîne de caractère dans le paramètre `text`, qui sera affichée tel quelle. Ensuite, le texte peut être changé par un appel à la fonction `changeFontAndText()`.

 - Indiquer un identifiant de texte de `TextStock`. Le texte affichée sera celui défini dans `txtStock.DICT_LANGUAGE`, avec la langue courante. Ensuite, la langue peut être changée en appelant `txtStock.changeLanguage(newLanguage)` puis `MenuText.changeLanguage()`.

Si on s'amuse à panacher les 2 manières de définir le texte, ça donne des comportements plus ou moins intéressant. C'est un fonctionnement qui n'est pas vraiment prévu.

#### menusesq.py ####

Contient la classe `MenuSensitiveSquare`. Elément de menu qui n'affiche rien, mais qui est focusable et activable. Il réagit quand on clique ou qu'on passe la souris dans une zone rectangulaire prédéfinie.

On n'utilise jamais directement cette classe, mais on la fait dériver pour avoir des éléments de menu interactifs. (Héritage multiple ou simple).

Cette classe contient 3 variables membres importantes :

 - `rectStimZone` : rectangle définissant la zone sensible, dans l'écran. On peut la définir directement, ou à partir de la variable membre existante `rectDrawZone` (qui aurait été définie par un autre moyen, tel qu'un héritage mulitple).

 - `funcAction` : voir `MenuElem`.

 - `clickType` : indique la manière dont est exécutée `funcAction` en fonction des événements de la souris. Les différentes valeurs possibles sont les constantes `MOUSE_*`, définies au début de ce fichier. (En gros : soit ça réagit au clic, soit ça réagit périodiquement tant que le curseur est dans le rectangle sensible).

Quel que soit la valeur de `clickType`, le `MenuSensitiveSquare` demande systématiquement à avoir le focus lorsque le curseur de souris passe sur le rectangle sensible.

TRIP: Désolé pour le nom de fonction `treatStimuliMouse`. Il faut bien évidemment lire `processStimuliMouse`. "Treat"... N'importe quoi. Même en français c'est moche, ce verbe "traiter".

#### menuseim.py ####

Contient la classe `MenuSensitiveImage`, héritée de `MenuSensitiveSquare`. Affiche une image.

Cette classe réagit aux clics ou aux mousehovers sur l'image, et exécute `funcAction`. (Comportement défini dans `MenuSensitiveSquare`).

Lorsque l'élément prend le focus, l'image s'affiche progressivement en plus clair. Lorsqu'il perd le focus, l'image s'affiche progressivement du clair vers le normal.

Les transitions clair<->normal se font sur 8 images. La liste de ces images est stockée dans la variable membre `listImgWithLight`. Elle est précalculée à l'instanciation de la classe, à partir de l'image normale.

Les transitions sont effectuées par la fonction `update`, qui s'exécute une fois par cycle de jeu. Pendant une transition, on ne réaffiche pas tous le menu entier, uniquement cet élément. Le booléen membre `mustBeRefreshed` est fixé à True durant tout le temps de transition.

#### menusetx.py ####

Contient la classe `MenuSensitiveText`, qui hérite à la fois de `MenuSensitiveSquare` et de `MenuText`.

Je ne sais pas trop comment est censé être géré l'héritage multiple en python. Dans le corps des fonctions, j'ai parfois besoin d'appeler explicitement une fonction de l'une ou l'autre des classes-mères. Ça fonctionne, c'est tout ce que j'attends.

Cette classe affiche un texte, comme `MenuText`. Elle réagit aux clics et aux mousehovers sur l'image, et exécute `funcAction`, comme `MenuSensitiveSquare`.

Lorsque l'élément prend le focus, le texte se met en mode "glow". Il change de couleur pour aller du blanc vers le bleu vers le blanc vers le bleu, etc. Contrairement au `MenuSensitiveImage`, les changements de couleur se font en yo-yo continu, tant que l'élément possède le focus.

Lorsque l'élément perd le focus, le texte fait une dernière petite transition pour passer progressivement de la couleur en cours vers le blanc. Puis il reste blanc.

Les images de textes changeant de couleur ne sont pas pré-calculées. En interne, on change la couleur du `Lamoche` et on fait un `font.render()` à chaque fois.

La liste des couleurs pour le glow est définie dans la variable membre `glowColorList`.

Le glow et la transition "glow->normal" sont effectuées par la fonction `update`, qui s'exécute une fois par cycle de jeu. Pendant un glow/transition, on ne réaffiche pas tous le menu entier, uniquement cet élément.

#### menulink.py ####

Contient la classe `MenuLink`, héritée de `MenuSensitiveText`.

Texte cliquable et focusable. La fonction `funcAction` pointe vers la fonction `mactQuitFullScreenAndGoToDaInterWeb`. Cette fonction désactive le mode plein écran (si on est actuellement dans ce mode), ouvre le navigateur internet par défaut, en lui indiquant une url égale au texte de l'élément de menu.

Pour ouvrir le navigateur par défaut vers une url, on utilise la fonction `webbrowser.open` (présente dans la librairie standard). Comme on n'est pas sûr que cette librairie existe sur tous les systèmes, il y a un try-catch au moment de son import.

Si l'import a échoué, lorsque l'utilisateur clique sur l'élément, on se contente de logger l'url vers la sortie standard. Comme ça le jeu peut fonctionner sur des systèmes bizarres n'ayant pas de navigateur.

#### menutick.py ####

Contient la classe `MenuSensitiveTick`, qui hérite à la fois de `MenuSensitiveImage` et de `MenuText`.

Cet élément de menu affiche à la fois une image (case à cocher) et un texte. La variable membre `rectDrawZone` est égale à la fusion des deux rectangles de l'image et du texte. La variable membre `rectStimZone` est déduite de `rectDrawZone`, avec une petite marge à chaque bord, comme d'habitude.

Lorsque cet élément a le focus, l'image de la case (cochée ou pas) s'affiche progressivement en plus clair (comme le `MenuSensitiveImage`). Cet élément a donc besoin de deux listes d'images différentes. Une liste de case cochée, de plus en plus claires. Et une liste de case pas cochée, de plus en plus claires. Tout cela doit être initialisé préalablement, et transmis lors de l'instanciation, par le paramètre `dicTickImage`.

En l'état, la classe `MenuSensitiveTick` ne modifie pas la valeur de son cochage lorsqu'elle est activée (par un clic ou par la touche Espace). Pour cela, il faut overrider `funcAction`, et appeler dedans la méthode `toggleTick`. J'ai fait exprès de rendre ça explicite, comme ça on peut désactiver le cochage/décochage si on a envie. Et on peut effectuer d'autres actions spécifiques dans `funcAction`.

La valeur de cochage courante est stockée dans la variable membre `boolTickValue`

On peut associer une valeur littérale à chacune des deux valeurs cochée/décochée. Pour cela, il faut passer les paramètres `dicLiteralFromBool` et `literalValInit` au moment de l'instanciation. Lorsque c'est défini, la variable membre `self.literTickValue` contient la valeur littérale courante.

#### menuedtx.py ####

WIP

### mot-clé utilisé dans les noms de variables ###

`mact` : "m-act", menu action.
`mbutt` : MenuElem de type bouton text (MenuSensitiveText)
`mbuttLink` : MenuElem de type bouton text (MenuSensitiveText), qui fait un lien vers un site web.
`mbuti` : MenuElem de type bouton image (MenuSensitiveImage)
`mkey` : MenuElem de type MenuSensitiveKey

"Création du menu" : Création de l'instance du menu, à partir de la classe.
(En général, c'est des classes héritées de celle-ci.

"activation du menu" : le menu est placé à l'écran. Et le joueur peut utiliser ses options.

## Description des menus spécifiques de Blarg ##

TODO.
