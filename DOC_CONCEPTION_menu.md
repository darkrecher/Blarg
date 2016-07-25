# Document de conception de Blarg (système de menu) #

Ce document décrit la manière dont est organisé le système de menu de Blarg (menu principal, config des touches, affichage des high scores, ...).

L'organisation du code du jeu en lui-même est décrite dans cet autre document : https://github.com/darkrecher/Blarg/blob/master/DOC_CONCEPTION_jeu.md .

## Introduction ##

Le code est assez densément commenté. Ce document se bornera donc à décrire sommairement le but de chaque classe.

Durant la réalisation de ce jeu, le PEP8 a été foulé aux pieds, écartelé, équarri et humilié en place publique par des petits enfants jetant des cailloux. C'est la faute à l'entreprise dans laquelle je bossais à l'époque, qui m'a appris à coder en python avec les conventions de nommage du C++. Il va falloir faire avec !

Le système de menu se veut le plus générique et le plus réutilisable possible. Même si en réalité, euh... Bref.

Les noms des fichiers définissant le système de menu commencent tous par "menu". Les noms des fichiers définissant les menus spécifique à Blarg commencent tous par "menuz". J'aurais dû ranger tout ça correctement dans des répertoires, mais j'étais un vilain.

## Description du système de menu générique ##

### Menus d'exemple ###

Ces exemples sont indépendants du jeu et permettent de donner une première idée de ce que peut faire le système de menu.

Pour les exécuter, ouvrir une console et entrer les commandes suivantes :

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

Flèche bleue pleine, de A vers B : Référence. L'objet A possède une référence vers l'objet B, qu'il garde tout le long de sa vie.

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
 - `IHMSG_PLAY_ONCE_MORE` : message spécial utilisé dans un seul cas : lorsqu'on quitte le menu de fin de partie. Sert à indiquer que le joueur veut rejouer.
 - `IHMSG_CANCEL` : le joueur veut annuler le truc en cours.

Pour indiquer un message sans aucun IHMSG, il suffit d'utiliser un tuple vide. Comme je suis super malin, je me suis dit que j'allais créer une constante égale au tuple vide, afin d'exprimer explicitement la notion de message vide (une lubie s'apparentant à du typage spécifique). La constante s'appelle `IHMSG_VOID`.

Du coup, pour renvoyer un message vide, on écrit `IHMSG_VOID`, sans parenthèse. Pour renvoyer un message contenant un IHMSG, on écrit `(IHMSG_REDRAW_MENU, )`, avec parenthèses. Ça fait bizarre. Tant pis !

#### menucomn.py ####

Diverses fonctions et constantes communes au système de menu.

C'est principalement utilisé par la partie spécifique (menus du jeu Blarg). Mais la partie générique utilise parfois une ou deux constantes contenues dans ce fichier. D'ailleurs c'est pas très bien, il faudrait essayer de séparer.

<a class="mk-toclify" id="menuelempy"></a>
#### menuelem.py ####

Contient la classe `MenuElem` : définition générique d'un élément de menu.

La plupart des fonctions de cette classe sont vides. Pour créer un élément de menu effectuant des choses, il faut faire un héritage et overrider les fonctions nécessaires. Les commentaires de docstring détaillent le rôle de chaque fonction, ce qu'on peut mettre dedans, ce qu'elles doivent renvoyer, etc.

Un `MenuElem` peut être placé dans un `MenuManager` ou dans un `MenuSubMenu` (un `MenuElem` spécial stockant d'autres `MenuElem`, [voir `MenuSubMenu`](#menusubmpy)).

Un `MenuElem` peut définir `funcAction()` : une fonction sans paramètre d'entrée, renvoyant un tuple de `IHMSG_*`. Cette fonction représente l'activation de l'élément. Elle est exécutée par le `MenuManager`, lorsque l'élément est focusé et que l'utilisateur appuie sur Espace ou Entrée. La fonction peut également être exécutée dans d'autres circonstances ([voir `MenuSensitiveSquare`](#menusesqpy)).

Si `funcAction()` vaut None, l'élément de menu n'est pas activable.

Le module `menuelem.py` contient également la fonction `cycleFocus()`, qui s'exécute lorsqu'il faut passer le focus à l'élément suivant d'une liste (par exemple, quand l'utilisateur appuie sur Tab). Un gros tas de commentaire au début du fichier décrit le fonctionnement des focus, ainsi que les différents "use cases".

La fonction `cycleFocus()` aurait méritée d'être dans un fichier de code à part, mais je l'ai mise là car elle y est plutôt bien. Elle est utilisée à la fois par le `MenuManager` et le `MenuSubMenu`, donc elle est assez générique.

#### menumng.py ####

Contient la classe `MenuManager` gérant un menu avec des `MenuElem` dedans.

On peut créer un `MenuManager` de 2 manières différentes :

 - Utiliser directement la classe de base. On l'instancie, on place dedans les `MenuElem` en redéfinissant la variable membre `listMenuElem`, puis on appelle la fonction `initFocusCyclingInfo()`. C'est ce qui est fait dans les codes d'exemple du chapitre précédent.

 - Dériver la classe. Dans l'`__init__`, on définit `listMenuElem`, puis on appelle `initFocusCyclingInfo()`. C'est ce qui est fait dans la plupart des menus de Blarg.

Dans les deux cas, l'activation du menu se fait en appelant la fonction `handleMenu()`.

Le terme "activation" est à peu près l'équivalent du "OnActivate" dans les menus Windows ou autre. Il désigne le fait d'afficher le menu et de démarrer une boucle prenant en compte les événements souris et clavier. La boucle s'arrête sur récupération d'un `IHMSG_QUIT` ou d'un `IHMSG_TOTALQUIT`.

Si on dérive, on peut également overrider les fonctions suivantes :

 - `showBackground()` : Fonction affichant l'image de fond, derrière le menu.

 - `beforeDrawMenu()` : Fonction vide. Elle est appelée à chaque fois qu'il faut (re)dessiner tout le menu, juste avant le dessin de l'image de fond et des éléments.

 - `startMenu()` : Fonction vide, s'exécute au début de l'activation d'un menu.

 - `periodicAction()` : Fonction vide, s'exécute au début de chaque cycle, tant que le menu est activé.

Le `MenuManager` envoie systématiquement tous les événements souris et clavier à tous ses éléments de menus, pas seulement à celui qui a le focus. C'est ensuite aux éléments de les gérer, en fonction de leur état de focus et d'autres choses.

Pour gérer les cyclages de focus, le `MenuManager` possède 2 listes de `MenuElem`.

 - `listMenuElem` : liste contenant tous les éléments de menu. Utilisée pour cycler lorsque le joueur appuie sur Tab.

 - `listMenuElemArrows` : liste contenant une partie des éléments de menu. Utilisée pour cycler lorsque le joueur appuie sur les flèches haut et bas. Par exemple, dans le menu principal de Blarg, cette liste contient les gros textes sélectionnables, mais ne contient pas les mini-options tels que les choix de langue. Cette liste peut être None, dans ce cas, les flèches haut et bas ne font rien.

Dans la fonction `handleMenu()`, lorsque le `MenuManager` transmet à un `MenuElem` des stimulis de touche, de mouvement de souris ou d'activation, il met préalablement à jour sa variable `self.menuElemTakingEvent`. Ça permet de garder une référence vers le `MenuElem` recevant actuellement l'événement, ce qui peut être utile quand on se retrouve dans une `funcAction` un peu générique, qu'on aurait associée à plusieurs `MenuElem`.

#### txtstock.py ####

Contient la classe `TextStock`, qui stocke tous les textes du jeu (menu, présentation, ...).

Les textes sont dans le dictionnaire `TextStock.DICT_LANGUAGE`.

 - clé : identifiant d'un texte. Ces identifiants sont définis comme des constantes statiques, au début de `TextStock`.
 - valeur : sous-dictionnaire :
    * clé : identifiants de langage. `LANG_FRENCH` ou `LANG_ENGL`
    * valeur : chaîne de caractère unicode avec le texte dedans.

La classe contient une variable membre `language`, indiquant la langue courante. Il est possible de changer sa valeur.

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

Pour l'affichage et la config associée (alignement horizontal et vertical, police, couleur, ...), la classe utilise en interne un `Lamoche`.

Le texte à afficher se définit à l'instanciation, de l'une des manières suivantes :

 - Indiquer directement une chaîne de caractère dans le paramètre `text`, qui sera affichée tel quelle. Elle pourra ensuite être modifiée par la méthode `changeFontAndText()`.

 - Indiquer un identifiant de texte de `TextStock`. Le texte affichée sera celui défini dans `txtStock.DICT_LANGUAGE`, avec la langue courante. La langue pourra ensuite être changée en appelant `txtStock.changeLanguage(newLanguage)` puis `MenuText.changeLanguage()`.

Il est déconseillé de s'amuser à panacher les 2 manières de définir le texte (cas non prévu et non testé).

<a class="mk-toclify" id="menusesqpy"></a>
#### menusesq.py ####

Contient la classe `MenuSensitiveSquare`. Elément de menu qui n'affiche rien, mais qui est focusable et activable. Il réagit quand on clique ou qu'on passe la souris dans une zone rectangulaire prédéfinie.

On n'utilise jamais directement cette classe, mais on la fait dériver pour avoir des éléments de menu interactifs. (Héritage multiple ou simple).

Cette classe contient 3 variables membres importantes :

 - `rectStimZone` : rectangle définissant la zone sensible dans l'écran. On peut la définir directement, ou à partir de la variable membre existante `rectDrawZone` (qui aurait été définie par un autre moyen, tel qu'un héritage mulitple).

 - `funcAction()` : [voir `MenuElem`](#menuelempy).

 - `clickType` : indique la manière dont est exécutée `funcAction()` en fonction des événements de la souris. Les différentes valeurs possibles sont les constantes `MOUSE_*`, définies au début du fichier. (Soit ça réagit aux clics, soit ça réagit périodiquement tant que le curseur est dans le rectangle sensible, soit ça réagit jamais).

Quel que soit la valeur de `clickType`, le `MenuSensitiveSquare` demande systématiquement à avoir le focus lorsque le curseur de souris passe sur le rectangle sensible. Pas besoin de cliquer pour prendre le focus.

TRIP: Désolé pour le nom de fonction `treatStimuliMouse`. Il faut bien évidemment lire `processStimuliMouse`. "Treat", "traiter", ... N'importe quoi. Même en français c'est moche.

#### menuseim.py ####

Contient la classe `MenuSensitiveImage`, héritée de `MenuSensitiveSquare`. Affiche une image.

On pourrait penser que cette classe ait également besoin d'hériter de `MenuImage`, mais en fait non.

Cette classe réagit aux clics ou aux mousehovers sur l'image, comme un `MenuSensitiveSquare`.

Lorsque l'élément prend le focus, l'image s'affiche progressivement en plus clair. Lorsqu'il perd le focus, ça revient progressivement vers le normal.

Les transitions clair<->normal se font sur 8 images. La liste de ces images est stockée dans la variable membre `listImgWithLight`. Elle est précalculée à l'instanciation de la classe, à partir de l'image normale.

Les transitions sont effectuées par la fonction `update()`, exécutée une fois par cycle de jeu. Durant tout le temps de transition, le booléen membre `mustBeRefreshed` est fixé à True, c'est à dire qu'on ne réaffiche pas le menu en entier, mais uniquement cet élément.

#### menusetx.py ####

Contient la classe `MenuSensitiveText`, qui hérite à la fois de `MenuSensitiveSquare` et de `MenuText`.

Je ne sais pas trop comment est censé être géré l'héritage multiple en python. Dans le corps des fonctions, j'ai parfois besoin d'appeler explicitement une fonction de l'une ou l'autre des classes-mères. Ça fonctionne, c'est tout ce que j'attends.

Cette classe affiche un texte, comme `MenuText`. Elle réagit aux clics et aux mousehovers et exécute `funcAction()`, comme `MenuSensitiveSquare`.

Lorsque l'élément prend le focus, le texte se met en mode "glow". Il change de couleur pour aller du blanc vers le bleu vers le blanc vers le bleu, etc. Contrairement au `MenuSensitiveImage`, les changements de couleur se font en yo-yo continu, tant que l'élément possède le focus.

Lorsque l'élément perd le focus, le texte fait une dernière petite transition pour revenir progressivement de la couleur en cours vers le blanc.

Les images du texte "glow" ne sont pas pré-calculées. En interne, on change la couleur du `Lamoche` et on fait un `font.render()` à chaque fois.

La liste des couleurs pour le glow est définie dans la variable membre `glowColorList`.

Le glow et la transition "glow->normal" sont effectuées par la fonction `update()`, à chaque cycle de jeu. Pendant un glow/transition, on ne réaffiche pas le menu en entier, mais uniquement cet élément. (`mustBeRefreshed = True` pendant tout le temps qu'on a le focus).

#### menulink.py ####

Contient la classe `MenuLink`, héritée de `MenuSensitiveText`.

Texte cliquable et focusable. La fonction `funcAction()` pointe vers la fonction `mactQuitFullScreenAndGoToDaInterWeb`. Cette fonction désactive le mode plein écran (si on est actuellement dans ce mode) et ouvre le navigateur internet par défaut en lui fournissant l'url correspondant au texte de l'élément de menu.

Pour aller vers l'url, on utilise `webbrowser.open()`, présent dans la librairie standard. Comme on n'est pas sûr que cette librairie existe sur tous les systèmes, il y a un try-catch au moment de son import, lors du lancement du jeu.

Si l'import a échoué, on se contentera de logger l'url vers la sortie standard au moment où l'utilisateur clique sur le `menulink`. Comme ça le jeu peut fonctionner sur des systèmes bizarres n'ayant pas de navigateur.

#### menutick.py ####

Contient la classe `MenuSensitiveTick`, qui hérite à la fois de `MenuSensitiveImage` et de `MenuText`.

Cet élément de menu affiche à la fois une image (case à cocher) et un texte. La variable membre `rectDrawZone` est égale à la fusion des deux rectangles de l'image et du texte. La variable membre `rectStimZone` est déduite de `rectDrawZone`, avec une petite marge à chaque bord, comme pour la plupart des autres éléments cliquables.

Lorsque cet élément a le focus, l'image de la case (cochée ou pas) s'affiche progressivement en plus clair (comme le `MenuSensitiveImage`). Cet élément a donc besoin de deux listes d'images différentes. Une liste de cases cochées, de plus en plus claires, et une liste de cases pas cochées, de plus en plus claires. Tout cela doit être initialisé préalablement et transmis lors de l'instanciation, via le paramètre `dicTickImage`.

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

Lorsqu'il n'y a pas le focus, le curseur est bleu. C'est important qu'il soit d'une couleur différente que le texte, sinon ça embrouille.

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

Les initialisations de tout le bazar sont effectuées en partie dans la fonction `__init__()` et en partie dans la fonction `main` (qui est appelée juste après l'init). Il n'y a pas vraiment de justification sur le fait que certaines actions sont dans l'init et d'autres dans le main. J'ai fait ça un peu au feeling.

En vrac, les actions effectuées sont les suivantes :

 - Chargement des polices de caractères (bon y'en a qu'une en fait).

 - Création d'un `Archivist`, permettant de charger/sauvegarder les données dans le fichier `dichmama.nil`.

 - Modification de l'icône de l'application, qui est censé apparaître dans la barre des tâches ou le dock.

 - Création d'une fenêtre, ou activation du mode plein écran (selon la config et les paramètres). Récupération de l'objet `pygame.Surface` correspondant à la zone de dessin à l'écran.

 - Initialisation de la classe `Game` permettant de jouer des parties. [voir DOC_CONCEPTION_jeu](https://github.com/darkrecher/Blarg/blob/master/DOC_CONCEPTION_jeu.md#gamegame)

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

Il y a quelques menus supplémentaires à afficher avant le menu principal (l'histoire du jeu, la description des touches, la saisie du nom du joueur). Les fonctions `handleMenu()` sont exécutées les unes après les autres. Chacun de ces menus comporte un moyen simple pour le joueur de le quitter, et donc de passer au suivant. En général, il suffit juste d'appuyer sur une touche.

Le nom saisi est enregistré dans le fichier de sauvegarde, hashé avec du SHA-512, et comparé avec le hash du nom magique permettant de débloquer le mode invincible.

##### fonction mactPlaySeveralGames() #####

Lance une ou plusieurs parties, les unes après les autres, et enregistre le score obtenu à chaque fin de partie.

Cette fonction est envoyée en paramètre au menu principal, ce qui lui permet de l'exécuter lorsque l'utilisateur clique sur l'option "Jouer".

Pour plus de détail : [doc conception jeu, chapitre "Lancement d'une partie"](https://github.com/darkrecher/Blarg/blob/master/DOC_CONCEPTION_jeu.md#lancement-dune-partie)

#### prezanim/PresentationAnim ####

Cette classe effectue les actions suivantes :
 - Chargement des images nécessaires à la présentation.
 - Affichage d'une première image, avec le texte "LOADINGE". Cette action est effectuée le plus vite possible, afin de montrer au joueur qu'il se passe bien quelque chose.
 - Pré-calcul des différentes images du titre. Il apparaît agrandi au début puis se réduit petit à petit.
 - Chargement des sons.
 - Exécution de l'animation. Un objet `pygame.time.Clock` gère le FPS. À chaque cycle, on affiche les images en les déplaçant.
   * Le magicien se déplace de droite à gauche.
   * Morac se déplace de gauche à droite, en même temps le magicien recule un peu.
   * Le titre apparaît en gros, puis se réduit.

Lorsque l'animation est terminée, l'image finale est récupérée (fond + magicien + Morac + titre), elle est fortement assombrie, puis stockée dans `imgBgMainMenu`. Le code extérieur (`MainClass`) récupérera cette image, qui sera utilisée comme fond pour le menu principal.

L'image du texte "Blarg" est également récupérée et réutilisée de la même manière (variable `imgTitle`). Aucun traitement n'est appliqué dessus. C'est juste pour éviter de charger deux fois la même image à deux endroits différents du code.

#### menugen.py ####

Contient une seule grosse fonction `generateAllMenuManager()`, qui effectue les actions suivantes :

 - Chargement de toutes les images nécessaires aux menus : boutons, pseudo-fenêtre, ...
 - Précalcul des images de tickBox. [Voir menutick.](https://github.com/darkrecher/Blarg/blob/master/DOC_CONCEPTION_menu.md#menutickpy)
 - Création des menus, un par un, et rangement dans un dictionnaire `dicAllMenu`. Chaque menu est associé à une clé (valeur numérique). Celles-ci sont définies dans `menucomn.py`, il s'agit des variables commençant par `MENU_`.
 - Récupération de la langue courante, stockée dans le fichier de sauvegarde, transmise par l'`Archivist`.
 - Application du changement de langue courante sur tous les menus, afin de les initialiser.
 - Renvoi de `dicAllMenu`.

#### menuzmai/MenuManagerMain ####

Classe définissant le menu principal du jeu. Il y a beaucoup de choses, mais c'est assez simple. Les commentaires dans le code sont suffisants.

Quelques détails :

Il y a un `MenuImage` affichant le titre "Blarg". Pourtant, ce titre est déjà présent dans l'image de background, mais en assombri. [(Voir prezanim)](https://github.com/darkrecher/Blarg/blob/master/DOC_CONCEPTION_menu.md#prezanimpresentationanim). On le réaffiche par dessus en pas-assombri, pour que ça ressorte bien.

L'élément `mkeyQuitEsc` est utilisé dans plusieurs menus. Il réagit à un appui sur la touche Esc, et envoie un IHMSG demandant à quitter le menu en cours. Dans le menu principal, le fait de quitter le menu en cours fait quitter complètement le jeu.

Les `MenuElem` sont rangés dans trois listes :
 - `listMenuElemButtText` : liste des options textes (jouer, high scores, ...)
 - `listMenuElemOther` : liste avec tous les autres éléments.
 - `listMenuElem` : tous les éléments (concaténation des deux listes précédentes).

Ça permet de définir plus facilement le cyclage de focus avec les flèches haut et bas. [(Voir menumng)](https://github.com/darkrecher/Blarg/blob/master/DOC_CONCEPTION_menu.md#menumngpy). Ce cyclage se fait sur les éléments de `listMenuElemButtText`.

Ça permet aussi de rajouter plus facilement une option texte : on modifie `listMenuElemButtText` et on reconstruit `listMenuElem`. C'est ce qui est fait lorsqu'il faut rajouter l'option du mode invincible (fonction `MenuManagerMain.addDogDom`).

Pour rappel : "DogDom", "EdomEdog" et les termes de ce genre sont une façon stupidement obfusquée de mentionner le "god mode", le mode invincible.

#### menuzwak/MenuManagerWaitOrPressAnyKey ####

Menu utilisé pour la transition entre la présentation du jeu et le menu principal.

Ce menu attend que le joueur appuie sur une touche, puis il se quitte. (Le code extérieur s'occupe ensuite d'activer le menu principal). Il y a également un timer, qui fait quitter automatiquement au bout de 100 cycles.

Ce menu n'affiche absolument rien. Il n'a pas d'image de background et le seul `MenuElem` qu'il possède ne dessine rien à l'écran. Donc lorsqu'on l'active, ce qui était précédemment affiché reste à l'écran, à savoir : la dernière image de l'animation de présentation.

#### menuzsto/MenuManagerStory ####

Contient 3 éléments :
 - un `MenuSubMenu` contenant plusieurs textes décrivant l'histoire du jeu. La `Surface` d'affichage de ce submenu est plus grande (en hauteur) que l'écran. Tous les textes sont placés dans la partie basse de la `Surface`, on ne les voit pas au début. La fonction `periodicAction` du menu décale progressivement la zone à afficher à l'écran. On voit donc le texte apparaître, à partir du bas de l'écran.
 - le `mkeyQuitEsc`
 - un `MenuSensitiveAnyKeyButton`. Si le joueur appuie sur une touche et que le décalage de la zone n'est pas fini, on applique un gros décalage qui termine immédiatement le scroll. Si le décalage est fini, l'appui de touche fait quitter le menu.

C'est donc un peu étrange, car on a deux éléments qui réagissent à des appuis de touche. Lorsque le joueur appuie sur Esc, Deux `funcAction` différentes sont exécutées. Elles peuvent demander à quitter le menu en cours en même temps. Ça ne pose pas de problèmes.

#### menuzman/MenuManagerManual ####

Menu non interactif, affichant le manuel du jeu. L'élément `manyQuit` fait quitter sur un appui de touche ou un clic. Tous les autres éléments ne sont pas interactifs :

 - `self.mimgManual` : grosse image affichant le manuel.
 - `self.listMenuText` : Les `MenuText` décrivant les 3 actions du héros. "mouvement", "pan", "recharger".
 - `listMenuTextKey` (définis dans `__init__`) : Les `MenuText` affichant les noms des touches associées aux actions.

Les éléments de `listMenuTextKey` sont également stockés dans le dictionnaire `self.dicMenuElemKey`.
 - Clé : identifiant de touche permettant au héro d'effectuer une action. (KEY_DIR_UP, KEY_FIRE, KEY_RELOAD, ...)
 - Valeur : `MenuText`, affichant le nom de la touche mappée.

Ce menu sera hérité pour créer `MenuManagerConfig` (menu permettant de configurer les touches). Certaines fonctions sont utilisées dans les deux menus : `initCommonStuff()`, `determKeyNameFont()`.

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

L'élément `manyQuit` fait quitter sur un appui de touche ou un clic. Tous les autres éléments ne sont pas interactifs.

Le menu contient 4 `MenuText`, mais seuls deux sont affichés :

 - Soit les deux premiers (`self.listMenuTextNorm`) dans le cas où le joueur a saisi un nom quelconque,
 - soit les deux derniers (`self.listMenuTextDogDom`) dans le cas où le joueur a saisi le nom secret permettant de débloquer le mode invincible.

Par défaut, c'est le texte normal qui est affiché. Pour avoir le texte du nom secret, le code extérieur doit appeler la fonction `MenuManagerNameIsALie.setNameTyped(self, nameTyped)`, avant d'activer le menu.

#### menuzdea/MenuManagerHeroDead ####

Menu apparaissant à la fin d'une partie, lorsque le joueur est mort.

Contient des `MenuText` affichant le score et le nombre de magiciens tués/explosés lors de la partie. La mise à jour de ces valeurs est effectuée par la fonction `updateMenuTextStat()`, que le code extérieur doit appeler avant d'activer le menu.

Ce menu contient deux éléments interactifs :

 - `mkeyQuitEsc` : élément générique réagissant à la touche Echap pour quitter (message `IHMSG_QUIT`).

 - `mkeyPlayOnceMore` : élément réagissant à l'appui sur la touche Entrée. Il renvoie un tuple de deux messages : `(IHMSG_QUIT, IHMSG_PLAY_ONCE_MORE)`. Ce dernier message, contrairement à tous les autres, est spécifique au jeu Blarg. Le système de menu ne s'en sert jamais. Lorsque le menu se quitte, le code extérieur contrôle la présence de `IHMSG_PLAY_ONCE_MORE` pour déterminer si il faut jouer une nouvelle partie ou pas.

L'image de fond de ce menu est différente des autres. (Image du héros mort transformé en potion de mana).

#### menuzsco/MenuManagerHighScore ####

Menu affichant les scores. L'élément `manyQuit` fait quitter sur un appui de touche ou un clic. Tous les autres éléments ne sont pas interactifs.

Lors de l'instanciation, il faut lui passer un `Archivist` en paramètre. Le menu s'occupe de récupérer les valeurs de score et d'effectuer les calculs nécessaires pour afficher les scores.

L'`Archivist` ne stocke pas la valeur du meilleur score, il stocke uniquement les nombres de magiciens tués et explosés durant la partie ayant créé le meilleur score. (Il stocke d'autres statistiques, dont certaines ne servent à rien, mais c'est pas grave).

Il faut donc recalculer le meilleur score à partir des nombres de magiciens. C'est le menu qui s'occupe de cette tâche, en appelant la fonction `scoremn.scoreFromKillBurst()`. C'est la même fonction utilisée pour calculer le score pendant le jeu. Ça permet de garantir que le calcul effectué est le même dans tous les cas. (Certes, c'est un calcul super simple, mais ça me semblait important de le définir à un seul endroit, car ce n'est pas une opération anodine).

À chaque fois que le menu est activé, l'ensemble de ces `MenuText` est regénéré. Il y en a de 2 sortes. Les "statiques" affichant le texte statique, et les "scoriques", affichant les valeurs de score.

Les MenuText sont organisés par bloc. Un bloc = un joueur. La fonction `buildOnePlayerMenuText()` génère les `MenuText` d'un bloc.

La fonction `getHiScoreStat` récupère une stat de score à afficher.

Tout cela est un peu alambiqué, mais c'est pas grave. C'est de l'alambiqué local.

#### menuzcre/MenuManagerCredits ####

Menu affichant le texte des crédits. Il est constitué des éléments suivants :

 - `self.msubCreditsText` : un `MenuSubMenu`, contenant des `MenuText` et des `MenuLink` décrivant les credits. Ce sub-menu est affiché sur la quasi-totalité de l'écran. Il y a juste une marge en haut et en bas.

 - Deux `MenuSensitiveImage` en haut et en bas, en mode `MOUSE_HOVER` (l'activation de ces éléments se fait périodiquement, dès que le curseur de souris est dessus). Ces deux éléments font scroller le sub-menu. L'image du haut est plus petite que celle du bas, car je me suis dit que le joueur aura systématiquement envie de scroller vers le bas, mais pas forcément envie de scroller vers le haut.

 - Un autre `MenuSensitiveImage` qui fait quitter le menu.

 - L'élément générique `mkeyQuitEsc`, qui fait quitter lorsqu'on appuie sur la touche Esc.

Les événement de clic sur le sub-menu sont transmis aux `MenuElem` contenus dedans, (en tenant compte des décalages). L'événement peut alors arriver sur un `MenuLink`, qui est alors activé, et ouvre le navigateur web par défaut vers le lien en question.

Il y a un comportement pas génial avec le sub-menu : le cyclage de focus parmi les éléments et les sous-éléments fonctionnent, mais ne tient pas compte du scrolling ni de ce qui est visible à l'écran. Donc lorsque le joueur appuie sur Tab, il voit le focus passer sur les `MenuSensitiveImage`, puis il le voit éventuellement passer sur quelques `MenuLink`, puis plus rien, car le focus est en train de cycler sur d'autres `MenuLink` non visible à l'écran. Au bout de quelques appuis sur Tab, le cyclage fait un tour et on revient sur les `MenuSensitiveImage`. Mais ça fait quand même bizarre. Faudrait tenir compte de ce qui est visible à l'écran. Dans une hypothétique version future du système de menu, il faudrait arranger ça.

Lorsqu'on reste appuyé sur les touches haut et bas, le scrolling se fait en continu. Ces actions ne sont pas déclenchées par des `MenuElem`, car je n'en ai pas créé qui soient capable de s'activer périodiquement tant qu'une touche reste appuyée. Ces actions sont déclenchées dans la fonction `periodicAction` du menu lui-même. On contrôle le contenu de `self.dictKeyPressed` (dictionnaire indiquant quelles touches sont actuellement appuyées), et on exécute éventuellement un coup de scrolling vers le haut et/ou vers le bas. La variable `self.dictKeyPressed` est périodiquement mise à jour par la classe-mère, dans la fonction `MenuManager.handleMenu()`.

#### menuzcon/MenuManagerConfig ####

Menu permettant de configurer le jeu.

Il est hérité de `MenuManagerManual` (menu affichant la configuration). Le code qui détermine les texte des noms des touches ("left", "right", ...) est mutualisé dans `MenuManagerManual`. Dans le manuel, on met ces textes dans des `MenuText`, alors que dans la config, on les met dans des `MenuSensitiveText`.

La config courante des touches est contenue dans `self.dicKeyMapping`. La structure de ce dictionnaire est la même que celle de `archiv.py/DEFAULT_KEY_MAPPING`. Pour une description détaillée : voir commentaire dans le code ou [voir MenuManagerManual](https://github.com/darkrecher/Blarg/blob/master/DOC_CONCEPTION_menu.md#menuzmanmenumanagermanual).

D'autres petits bouts de code sont également mutualisés : image de la fenêtre, texte statique, initialisation de `dicKeyMapping` à partir de l'`archivist`.

L'élément `mtickSound` permet d'activer/désactiver le son (fonction `mactToggleSound()`). La valeur courante de l'activation du son est stockée dans `self.mtickSound.literTickValue`. Ce n'est pas un booléen, cela correspond à la valeur litérale stockée dans l'archivist. La conversion vers le booléen est effectuée par la fonction `theSoundYargler.changeSoundEnablation()`.

Le bouton `mbuttResetDefaults` exécute la fonction `mactResetDefaults`. Cette fonction remet les touches par défaut et réactualise les textes des `MenuSensitiveText` affichant les noms des touches.

L'élément `self.mOneKeyRecorder` est une instance de `MenuOneKeyRecorder`. Il permet d'enregistrer un appui de touche du joueur, lorsqu'il veut changer la configuration. Il n'y a qu'un seul `MenuOneKeyRecorder`, qui est utilisé pour toutes les touches.

Lorsque le joueur change la configuration d'une touche, l'enchaînement d'action suivant se produit :

 - Le joueur clique sur le `MenuSensitiveText` d'une touche.
 - La fonctoin `mactConfigKey` est exécutée. (C'est la même quelle que soit le `MenuSensitiveText` cliqué).
   * La variable `self.menuElemKeyActive` prend la valeur du `MenuSensitiveText` cliqué.
   * Exécution de `self.refreshMenuElemKeyActive(False, "???")`, afin d'afficher des points d'interrogation sur la touche actuellement en cours de configuration.
   * Exécution de `mOneKeyRecorder.activateRecording()`, pour démarrer l'enregistrement des touches.
 - Le joueur appuie sur une touche. Cela active la `funcAction()` du `self.mOneKeyRecorder`.
 - La fonction `mactNewKeyTyped` est exécutée.
   * Récupération du code et du caractère de la touche appuyée, stockés par le `self.mOneKeyRecorder`.
   * Récupération de l'identifiant de touche concernée (`KEY_DIR_UP`, `KEY_FIRE`, ...), à partir de `self.menuElemKeyActive`.
   * Mise à jour de `self.dicKeyMapping`.
   * Exécution de la fonction `stopKeyRecording()`
     * Exécution de `self.refreshMenuElemKeyActive()`, afin d'enlever les points d'interrogation et mettre le nom de la nouvelle touche sur le `MenuSensitiveText` de la touche qui vient d'être configuré.
     * Exécution de `mOneKeyRecorder.desactivateRecording()`, pour arrêter l'enregistrement des touches.
 - Le joueur peut ensuite cliquer sur un autre `MenuSensitiveText` pour configurer une autre touche.

Il s'agit ici du cas nominal. Il y a un peu plus de code dans les fonctions citées, pour prendre en compte les cas tordus. Ils sont à peu près bien expliquées par les commentaires. Liste rapide des cas tordus :

 - La plupart des autres fonctions de ce menu exécutent `stopKeyRecording()`, afin de désactiver l'enregistrement de touche courant lorsque l'utilisateur décide de faire autre chose.
 - La variable `self.justRecordedIsAnActivationKey` permet de configurer une touche pour y associer espace ou entrée, sans réactiver un enregistrement de touche.
 - L'élément `mkeyQuitOrCancel` est exécuté lorsque le joueur appuie sur Esc. Il ne fait pas forcément quitter le menu. Il annule l'enregistrement de touche en cours s'il y en a un, sinon il fait quitter le menu. Dans la liste de tous éléments du menu, `mkeyQuitOrCancel` doit être impérativement placé avant `self.mOneKeyRecorder`.
 - On ne peut pas configurer une touche pour y associer Esc ou Tab. C'est fait exprès.

Lorsqu'on quitte le menu, la nouvelle configuration (activation du son + touches) est automatiquement enregistrée dans l'`archivist`, qui le sauvegarde immédiatement dans le fichier. C'est un peu mal fichu car on ne peut pas quitter sans sauvegarder. Il faudrait un bouton "OK" et un bouton "Annuler", comme dans tout menu normal, mais j'avais la flemme de le faire.


Voilà, cette documentation est finie. Bon courage pour ceux qui l'ont lu, et encore plus bon courage pour ceux qui voudraient en faire quelque chose !
