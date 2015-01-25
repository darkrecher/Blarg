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

### Description des modules ###

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

### menuelem.py ###

Définition générique d'un élément de menu.

La classe `MenuElem` contient plusieurs fonctions presque vides. Pour créer un élément de menu effectuant des choses, il faut hériter ce `MenuElem` et overrider les fonctions nécessaires. Les commentaires de docstring détaillent le rôle de chaque fonction, ce qu'on peut mettre dedans, ce qu'elles doivent renvoyer, etc.

Un élément de menu peut être placé dans un `MenuManager`, ou bien dans un `MenuSubMenu` : un élément de menu spéciale, capable de stocker d'autres éléments. (Voir plus loin).

Le module `menuelem.py` contient également la fonction `cycleFocus`, qui s'exécute lorsqu'il faut passer le focus d'un élément de menu à l'élément suivant dans une liste (par exemple, quand l'utilisateur appuie sur Tab). Un gros tas de commentaire au début du fichier décrit le fonctionnement des focus, ainsi que les différents "use cases".

La fonction `cycleFocus` aurait méritée d'être dans un fichier de code à part, mais je l'ai mise là car elle y est plutôt bien. Elle est utilisée à la fois par le `MenuManager` et le `MenuSubMenu`, donc elle est assez générique.

### menumng.py ###

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
