# Exploitation du code source

## Windows


### Lancement du jeu à partir du code source

Le jeu peut fonctionner avec python 2.5.4, ou une version 2.x supérieure (pas la version 3, car elle n'est pas rétro-compatible).

Cependant, la transformation en exécutable n'est peut-être pas réalisable avec une version supérieure à 2.5.4, à cause d'un bug dans pygame2exe. Pour plus de détails :

 - https://www.daniweb.com/programming/software-development/threads/247249/need-help-with-pygame-to-exe#post1447072
 - https://github.com/darkrecher/Kawax/blob/master/doc_diverses/message_forum_pygame_exe.md

Dans la partie "Windows" de cette documentation, on considérera donc uniquement la version python 2.5.4.

#### Installation de python

Télécharger le fichier d'installation `python-2.5.4.msi`, à partir de https://www.python.org/download/releases/2.5.4/

Exécuter ce fichier.

Choisir les options suivantes :

 - "Install for all users".
 - Le répertoire de destination que vous voulez. On considérera le choix par défaut : `C:\python25`
 - Installation complète (choisir toutes les features).

#### Installation de pygame

Télécharger le fichier `pygame-1.9.1.win32-py2.5.msi`, à partir de http://www.pygame.org/download.shtml.

Si vous utilisez une version plus récente de python, prenez garde à télécharger le pygame correspondant. Il y en a un pour les 2.6.x et un pour les 2.7.x. Ils sont récupérables au même endroit.

Exécuter le fichier téléchargé.

Choisir les options suivantes :

 - "Install for all users".
 - Indiquer le répertoire ou vous avez installé python. (`C:\python25\` ou autre)

#### Lancement du jeu

Télécharger tout le contenu de ce repository. On considèrera qu'il est mis à l'emplacement `C:\blarg\`.

Ouvrir une console MS-DOS

Exécuter les commandes suivantes

    cd C:\blarg\code
    C:\python25\python.exe zemain.py

Amusez-vous bien !


### Transformation en exécutable

#### Installation de py2exe

Télécharger le fichier `py2exe-0.6.9.win32-py2.5.exe`, à partir de http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/py2exe-0.6.9.win32-py2.5.exe/download?use_mirror=skylink&download=

Exécuter ce fichier, **en mode administrateur**.

S'il n'est pas lancé en mode administrateur, on risque d'obtenir un message d'avertissement "Could not create key. py2exe-py2.5" suivi de plusieurs autres messages.

Indiquer le répertoire ou vous avez installé python. (`C:\python25\` ou autre)

#### Création du .exe

Cette action utilise le fichier `code/pygame2exe.py`, qui a été créé à partir de ce tutoriel : http://www.pygame.org/wiki/Pygame2exe?parent=CookBook

Exécuter `code/build_blarg_exe.bat`. Une fenêtre s'ouvre, demandant parfois d'appuyer sur une touche pour continuer le processus.

Attention, si le python n'est pas installé dans `C:\python25\`, ce .bat ne marchera pas. Il faut alors exécuter manuellement les commandes indiquées dans le .bat, en adaptant le chemin d'installation de python.

À l'issue de l'exécution de ces commandes, un répertoire `C:\blarg\code\dist\` a été créé, contenant l'exécutable stand-alone du jeu. (Ce répertoire n'est pas versionné dans ce repository).

#### Message d'erreur possible

Parfois, on obtient un message d'erreur de cette forme :

    WindowsError: [Error 32]
    Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus:
    'build\\bdist.win32\\winexe\\{chemin de fichier quelconque}

Le texte `{chemin de fichier quelconque}` peut prendre diverses valeurs : `collect-2.5\\encodings`, `bundle-2.5\\python25.dll`, ...

Dans ce cas, il reste un répertoire `C:\blarg\code\build\`, qui ne sert plus à rien. Vous pouvez le supprimer ainsi que son contenu.

À priori, l'exécutable a été correctement créé même si ce message est apparu. Dans le doute, on peut réessayer (ce message semble apparaître aléatoirement).

#### Message d'avertissement

On obtient systématiquement le message d'avertissement suivant :

    Make sure you have the license if you distribute any of them, and
    make sure you don't distribute files belonging to the operating system.

    KERNEL32.dll - I:\WINDOWS\system32\KERNEL32.dll
    GDI32.dll - I:\WINDOWS\system32\GDI32.dll
    WSOCK32.dll - I:\WINDOWS\system32\WSOCK32.dll
    SHELL32.dll - I:\WINDOWS\system32\SHELL32.dll
    WINMM.DLL - I:\WINDOWS\system32\WINMM.DLL
    WS2_32.DLL - I:\WINDOWS\system32\WS2_32.DLL
    ADVAPI32.dll - I:\WINDOWS\system32\ADVAPI32.dll
    USER32.dll - I:\WINDOWS\system32\USER32.dll

Ça ne m'a jamais posé de problème. À priori, tous ces fichiers sont déjà présents sur la plupart des systèmes Windows. Pour distribuer le jeu, il suffit juste de distribuer le contenu du répertoire `dist`.

#### Lancement du jeu avec le .exe

Double-cliquer sur le fichier `C:\blarg\code\dist\blarg.exe`.

Au premier lancement, il peut y avoir le message d'erreur suivant.

    An error occurred, please see the blarg.exe.log file for details.

Mais le fichier de log mentionné n'est pas créé. Le jeu se lance correctement.

Ce message n'apparaît qu'une fois.

Si vous avez l'anti-virus Avast, celui-ci va couiner un petit peu au premier lancement (validation d'un .exe non connu). Mais ça se passe sans aucun problème.

Pour lancer le jeu en mode fenêtre, quelle que soit la config actuelle, double-cliquer sur le fichier `C:\blarg\code\dist\blarg_windowed.bat`

#### Redistribution de l'exécutable

Créer un fichier compressé (.zip ou autre), contenant tout le répertoire `dist`. À savoir, les fichiers et répertoires suivants :

 - fontzy
 - img
 - sound
 - blarg_windowed.bat
 - blarg.exe
 - MSVCR71.dll
 - w9xpopen.exe

Pour installer le jeu sur un autre ordinateur, il suffit de copier le .zip, de le décompresser n'importe où, et de double-cliquer sur blarg.exe.

Si vous modifiez et/ou redistribuez ce jeu, merci de respecter les termes de la licence (Art Libre ou CC-BY). En particulier : citer l'auteur. Un lien vers mon blog ou vers ce repository suffira.


### Ajout des icônes

Tentative d'avoir une icône représentant le héros de Blarg, dans la barre des tâches et dans le fichier .exe.

Ça marche plus ou moins bien.

Voir : https://github.com/darkrecher/Blarg/blob/master/doc_diverses/logo_icones/ajout_icones.md .


## Mac OS X


### Lancement du jeu à partir du code source

À priori, pas de souci de version de python, ni pour jouer, ni pour transformer en exécutable. On peut utiliser n'importe laquelle, de la 2.5 à la 2.x.

#### Installation de python et pygame

Je l'ai fait sur mon Mac, mais je ne me souviens plus des actions effectuées ! Je suppose que si je n'ai rien noté de spécial, c'est qu'il ne devait rien y avoir de compliqué.

Pour vérifier les versions de python et pygame, ouvrir un terminal et exécuter la commande `python`. Vous devriez avoir quelque chose comme cela :

    Python 2.6.4 (r264:75821M, Oct 27 2009, 19:48:32)
    [GCC 4.0.1 (Apple Inc. build 5493)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.

Ensuite, dans la console python, exécuter les commandes suivantes :

    >>> import pygame
    >>> print pygame.version.ver
    >>> 1.9.1release-svn2575

Si le python a été installé correctement, il devrait automatiquement être dans la variable PATH. Sinon, il est ici :
`/Library/Frameworks/Python.framework/Versions/2.6/Resources/Python.app/Contents/MacOS/Python/python`

(Adapter le "2.6" à la version de Python installée).

Mon répertoire lib contient les fichiers suivants :

    cd /Library/Frameworks/Python.framework/Versions/2.6/lib/python2.6/site-packages
    ls

    README
    altgraph-0.6.7-py2.6.egg
    easy-install.pth
    macholib-1.2.1-py2.6.egg
    modulegraph-0.7.3-py2.6.egg
    py2app-0.4.3-py2.6.egg
    pygame
    pygame-1.9.1release-py2.6.egg-info
    setuptools-0.6c11-py2.6.egg
    setuptools.pth

#### Lancement du jeu

Télécharger ce repository sur votre disque. On considèrera qu'il est à cet emplacement : `~/Documents/recher/blarg/`

Ouvrir un terminal et exécuter les commandes suivantes :

    cd ~/Documents/recher/blarg/code
    python zemain.py

Le jeu va se lancer.


### Transformation en exécutable

#### Installation de py2app et setuptools

Comme pour l'installation de python et pygame : je ne sais plus comment j'ai fait ! Et si ça se trouve, il n'y a rien à faire, c'est déjà pré-installé.

Se reporter au contenu de mon répertoire lib, et essayer d'avoir plus ou moins la même chose, en adaptant les divers numéros de versions.

#### Création du .app

Dans le repository, dupliquer le fichier `code/zemain.py` en le renommant `code/blarg.py`. C'est le moyen le plus simple de créer une app avec le bon nom.

Le fichier `code/blarg.py` n'est pas versionné dans ce repository, puisque c'est juste une copie.

Ouvrir un terminal et exécuter les commandes suivantes :

    cd ~/Documents/recher/blarg/code
    python pygame2macapp.py py2app --iconfile blarg_icon.icns

Les deux derniers paramètres : `--iconfile blarg_icon.icns` sont facultatifs. Ils permettent d'ajouter une icône au .app.

Deux répertoires sont créés :

 - `code/dist` : contient l'application `blarg.app`.
 - `code/build` : répertoire temporaire pouvant être supprimé.

Le contenu de ces 2 répertoires n'est pas versionné dans ce repository.

Double-cliquer sur `code/dist/blarg.app` pour lancer le jeu.

Pour lancer le jeu en mode fenêtre quelle que soit la config, il faut le faire par une ligne de commande. Le plus dur étant de trouver la commande exacte. C'est quelque chose comme ça :

    cd ~/Documents/recher/blarg/code/dist/blarg.app/Contents/MacOS
    ./blarg FORCE_WINDOWED

#### Création d'un disque .dmg contenant le .app

Ouvrir un terminal et exécuter les commandes suivantes :

    cd ~/Documents/recher/blarg/code/dist
    hdiutil create -imagekey zlib-level=9 -srcfolder blarg.app blarg.dmg

Ça met un certain temps. Des petits points s'écrivent dans le terminal, pour montrer qu'il est vivant.

Le fichier `dist/blarg.dmg` finit par être créé.

#### Gestion du fichier de sauvegarde

Au premier lancement du jeu, le fichier `dichmama.nil` (sauvegarde de la config et des scores) est automatiquement créé à l'intérieur de `blarg.app`. (Pour les Macqueux néophytes : une application `.app` est en réalité un dossier contenant plusieurs fichiers). En ce qui concerne Blarg, le fichier de sauvegarde se retrouve à cet emplacement : `blarg.app/Contents/Resources`.

Les "vrais applications" Mac ne mettent pas leurs fichiers de données dans le .app, mais dans un emplacement prévu à cet effet : `~/Library/Application Support` ou quelque chose comme ça. Je ne sais pas trop comment faire ça.

Cette sauvegarde dans le .app pose deux problèmes :

 - Si vous distribuez ce .app à d'autre personnes, vous embarquez votre sauvegarde avec. Rappelons que le jeu demande au joueur de saisir son nom uniquement dans le cas où le fichier de sauvegarde est encore inexistant. La saisie du code secret pour être invincible ne peut se faire qu'à ce moment là. En donnant un jeu possédant déjà un fichier `dichmama.nil`, vous empêchez d'autres personnes de valider leur code et de se faire leurs propres scores.

 - Les fichiers .dmg sont en lecture seule. Lorsque vous exécutez le .app contenu dans un .dmg, sans l'avoir préalablement extrait, la création du fichier `dichmama.nil` échoue silencieusement. Vous ne pouvez alors conserver ni votre code d'invincibilité, ni votre configuration de touches, ni vos scores. Il est donc conseillé d'extraire systématiquement le .app du .dmg pour jouer.

#### Redistribution de l'application

Copier le .app ou le .dmg sur un autre Mac, puis exécuter le jeu en double-cliquant sur le .app comme expliqué précédemment.

Si vous modifiez et/ou redistribuez ce jeu, merci de respecter les termes de la licence (Art Libre ou CC-BY). En particulier : citer l'auteur. Un lien vers mon blog ou vers ce repository suffira.


### Plantage éventuel à l'exécution

Si vous avez un peu joué avec le code source, vous risquez d'avoir l'erreur suivante au lancement de blarg.app.

    Fatal Python error: (pygame parachute) Bus Error
    Abort trap

Aucune fenêtre n'apparaît. Ce message est émis sur la sortie standard ou erreur. (Bref, dans la console).

Ça arrive avec les exécutables Mac, mais peut-être aussi sur d'autres systèmes.

Pour régler le problème, vérifiez que vous n'avez pas ajouté une instruction de ce genre dans le code :

    my_default_font = pygame.font.Font(None, 20)

Lorsqu'on instancie une police de caractère sans spécifier de fichier de police, le python parvient toujours à se débrouiller. Il s'en est gardé une sous le coude, il demande une police au système, il écrit les lettres lui-même avec son sang, ... Donc, quand on lance le jeu avec le code source, tout va bien.

Mais dans un exécutable, ça pète. Car la police par défaut n'est pas embarquée dedans. Le message d'erreur est vraiment cabbalistique.

Pour éviter ce genre de désagrément, indiquez toujours un fichier de police quand vous en instanciez une. N'importe laquelle, même un truc moche. Si vous ne savez pas où en trouver, prenez celle du repository : code/fontzy/tempesta.ttf

J'ai eu l'explication de ce bug grâce à ce post sur stackoverflow : http://stackoverflow.com/questions/3470377/my-py2app-app-will-not-open-whats-the-problem


### Ajout des icônes

Ça marche plus ou moins bien.

Voir : https://github.com/darkrecher/Blarg/blob/master/doc_diverses/logo_icones/ajout_icones.md .


## GNU/Linux, Ubuntu, Fedora, etc.

Il est certainement possible de jouer à Blarg sur ces systèmes, puisque python et pygame sont compatibles dessus. Mais je n'ai pas ce genre de chose chez moi. Désolé, je devrais certainement être qualifié de vilain monsieur.

Je vous laisse vous débrouiller tout seul, à coup de apt-get ou autres ésotériqueries. Ça ne devrait pas être trop difficile, je suis sûr que vous êtes très fort. Bon courage !

Si vous rencontrez des problèmes durant l'installation, l'exécution ou autre, n'hésitez pas à m'en faire part. Je les décrirais dans ce document pour en faire profiter tout le monde.

