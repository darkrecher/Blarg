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

### Description des fichiers ###

IHMSG



### mot-clé utilisé dans les noms de variables ###

`mact` : "m-act", menu action.
`mbutt` : MenuElem de type bouton text (MenuSensitiveText)
`mbuttLink` : MenuElem de type bouton text (MenuSensitiveText), qui fait un lien vers un site web.
`mbuti` : MenuElem de type bouton image (MenuSensitiveImage)
`mkey` : MenuElem de type MenuSensitiveKey

"Création du menu" : Création de l'instance du menu, à partir de la classe.
(En général, c'est des classes héritées de celle-ci.

"activation du menu" : le menu est placé à l'écran. Et le joueur peut utiliser ses options.

## Description des menus de Blarg ##

TODO.
