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

TODO.

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

Quel que soit la valeur de `clickType`, le `MenuSensitiveSquare` demande systématiquement à avoir le focus lorsque le curseur de souris passe sur le rectangle sensible.

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

Contient la classe `MenuEditableText`, héritée de `MenuSensitiveText`. Il s'agit d'une zone de texte éditable. L'élément est focusable, mais pas cliquable ni activable. (`funcAction()` est None).

À priori, tous les caractères bizarres peuvent être écrits (accents, majuscules, trémas, ...). L'utilisateur peut appuyer sur backspace pour effacer la dernière lettre.

Le curseur reste toujours à la fin du texte. Les flèches gauche et droite ne font rien. On ne peut pas sélectionner tout ou partie du texte. On ne peut pas faire de copier-coller. Donc c'est un peu rustique, mais c'est suffisant.

La valeur courante du texte saisi est accessible par la classe `Lamoche` interne à l'élément. C'est à dire : `self.theLamoche.text`.

La classe override la fonction `MenuElement.takeStimuliKeys()`, afin de récupérer les appuis de touche et d'en déduire les modifications à applique au texte saisi. Lorsqu'une modif est faite, on envoie le message `IHMSG_REDRAW_MENU`, afin de demander un redessin global du menu. C'est obligé, pour effacer entièrement le texte précédent, et afficher le texte courant. (Sinon ça fait des superpositions dégueulasses).

L'élément est un `MenuSensitiveSquare` (puisque c'est un `MenuSensitiveText`), mais avec la variable membre `clickType = MOUSE_NONE`. Ça veut dire que quand on clique dessus, il ne se passe rien. Cependant, le focus est toujours attribué à cet élément lorsqu'on passe la souris dessus. Les saisies de texte ne sont prises en compte que quand l'élément a le focus.

Contrairement au `MenuSensitiveText`, le texte est toujours affiché en blanc, même lorsqu'il y a le focus. C'est le curseur qui change de couleur en continu : bleu -> blanc -> bleu -> blanc...

Lorsqu'il n'y a pas le focus, le curseur est bleu (et non pas blanc). C'est important que le curseur soit d'une couleur différente que le texte, sinon ça embrouille un peu.

L'affichage du texte et du curseur est géré par la fonction `draw()`. La modification périodique de l'index indiquant la couleur du curseur en cours est effectuée par la fonction `MenuSensitiveText.update()` (elle n'est pas overridée dans cette classe). Donc l'index évolue pareil, mais la liste de couleur (`glowColorList`) n'est pas la même entre le `MenuSensitiveText` et le `MenuEditableText`.

#### menukrec.py ####

Contient la classe `MenuOneKeyRecorder`. Élément de menu qui ne s'affiche pas, qui est non focusable, mais qui peut quand même exécuter une `funcAction()`.

Cet élément possède deux fonctions spécifiques : `activateRecording()` et `desactivateRecording()`, permettant d'activer et désactiver l'enregistrement des touches.

Lorsque l'enregistrement est activé, les appuis de touches sont enregistrés. Seul le dernier appui est gardé en mémoire. Il est accessible par les variables membres `keyRecorded` (code numérique de la touche appuyée) et `charKeyRecorded` (caractère correspond à la touche appuyée).

Lorsque l'enregistrement est activé, `funcAction()` est exécutée à chaque appui de touche.

Dans Blarg, c'est cet élément qui permet de configurer les touches du jeu.

<a class="mk-toclify" id="menusubmpy"></a>
#### menusubm.py ####

Contient la classe `MenuSubMenu`. Élément de menu top génial, dans lequel on met d'autres éléments de menu (de n'importe quel type), qu'on appelle "sous-éléments".

Le sub-menu s'affiche dans un rectangle à l'écran, définie par `rectDrawZone` (transmis à l'instanciation). L'affichage ne déborde jamais de cet écran.

Les coordonnées des sous-éléments sont définies par rapport à une zone interne au sub-menu, et non pas par rapport à l'écran. C'est à dire qu'un sous-élément en coordonnée (0, 0) apparaîtra à la coordonnée `(rectDrawZone.x, rectDrawZone.y)` de l'écran.

La zone interne peut être plus grande que `rectDrawZone`, elle peut même être plus grande que l'écran. Sa taille est définie par la taille de la variable membre `surfaceInside` (objet `pygame.Surface`).

La taille de la zone interne est calculée automatiquement, à l'instanciation et lors d'un changement de langue (fonction `renderElemInside()`). Elle est calculée en fonction des sous-éléments, et de leurs `rectDrawZone`. La fonction `renderElemInside()` effectue également un dessin de tous les sous-éléments dans `surfaceInside`, afin d'initialiser l'aspect général du sub-menu.

La fonction `SubMenu.draw` redessine les sous-éléments ayant leur valeur `mustBeRefreshed` à True, puis extrait un sous-rectangle de `surfaceInside` pour l'afficher à l'écran, à la position de `rectDrawZone`.

Le sous-rectangle est défini par la variable membre `sourceRectToBlit`. Si la zone interne est plus grande que l'écran, `sourceRectToBlit` n'en prend qu'une partie. On ne voit donc pas le sub-menu en entier.

Des fonctions spécifiques (`scrollVertically()` et `scrollSetPosition()`) permettent de déplacer verticalement `sourceRectToBlit`, afin de faire scroller la zone interne. On ne peut pas scroller horizontalement, car je n'en ai pas eu besoin pour Blarg.

À priori il y aurait un bug : si un quelconque élément de menu envoie le message `IHMSG_REDRAW_MENU`, on est censé redessiner tous les éléments de menu. Mais lorsqu'on demande de redessiner le sub-menu, il inspecte ces sous-éléments et ne redessine que ceux ayant `mustBeRefreshed` à True.

Pour forcer un redessin complet, il faudrait appeler `renderElemInside()`. Le problème, c'est que quand le `MenuManager` demande un dessin, il ne précise pas si c'est pour un redessin complet, ou si c'est pour une autre raison. Donc pour l'instant, on va laisser comme ça. Tant pis pour le bug.

Les événements souris sont transmis aux sous-éléments (en tenant compte des décalage de coordonnées du au scrolling vertical et à la position d'affichage du sub-menu à l'écran).

Les événements de touche ne sont pas transmis. Ce n'est pas bien, mais j'en ai pas eu besoin.

Les cyclages de focus sont transmis. C'est à dire que lorsque le sub-menu reçoit un événement de cyclage, il fait cycler le focus en interne, dans les sub-menu (le sous-élément ayant le focus est indiqué par la variable membre `focusedElemInside`). Tant qu'on n'est pas arrivé au dernier sous-élément, le sub-menu répond qu'il ne veut pas lâcher le focus (il ne renvoie pas le message `IHMSG_CYCLE_FOCUS_OK`). Lorsqu'on est arrivé au dernier sous-élément et que l'utilisateur cycle une dernière fois, on accepte de lâcher le focus.

Le sub-menu possède une `funcAction()`, mais elle n'est pas censée être overridée. Cette `funcAction()` exécute la `funcAction()` du sous-élément ayant actuellement le focus (si elle existe). De cette manière, l'événement d'activation est propagé. Lorsque l'utilisateur appuie sur Espace ou Entrée, c'est le sous-élémemnt actuellement focusé qui est activé.

Dans Blarg, le sub-menu permet d'afficher le texte scrollable des Credits (liens vers mes sites, noms des contributeurs, lien vers la licence, ...).

En théorie, on devrait pouvoir mettre un sub-menu dans un sub-menu dans un sub-menu etc. Mais je n'ai pas testé.

### mot-clé utilisé dans les noms de variables ###

`mact` : "m-act" : menu action.

`mbutt` : MenuElem de type `MenuSensitiveText` (texte cliquable).

`mbuttLink` : MenuElem de type `MenuLink`, constituant un lien vers un site web.

`mbuti` : MenuElem de type `MenuSensitiveImage` (image cliquable).

`mkey` : MenuElem de type `MenuSensitiveKey` (réaction à une touche spécifique).

"Création du menu" : Instanciation d'un `MenuManager`, ou d'une classe héritée.

"activation du menu" : affichage et activation du `MenuManager` à l'écran. Exécution de la méthode `handleMenu()`. Le joueur peut utiliser les options du menu.

## Description des menus spécifiques de Blarg ##

TODO.
