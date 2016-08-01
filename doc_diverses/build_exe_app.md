# Exploitation du code source #

## Windows ##

### Lancement du jeu à partir du code source ###

Le jeu peut fonctionner avec python 2.5.4, ou une version 2.x supérieure (pas la version 3, car elle n'est pas rétro-compatible).

Cependant, la transformation en exécutable n'est peut-être pas réalisable avec une version supérieure à 2.5.4, à cause d'un bug dans pygame2exe. Pour plus de détails concernant ce bug :

 - https://www.daniweb.com/programming/software-development/threads/247249/need-help-with-pygame-to-exe#post1447072
 - https://github.com/darkrecher/Kawax/blob/master/doc_diverses/message_forum_pygame_exe.md

Dans la partie "Windows" de cette documentation, on considérera donc uniquement la version python 2.5.4.

#### Installation de python ####

Télécharger le fichier d'installation `python-2.5.4.msi`, à partir de https://www.python.org/download/releases/2.5.4/

Exécuter ce fichier.

Choisir les options suivantes :

 - "Install for all users".
 - Le répertoire de destination que vous voulez. On considérera le choix par défaut : `C:\python25`
 - Installation complète (choisir toutes les features).

#### Installation de pygame ####

Télécharger le fichier `pygame-1.9.1.win32-py2.5.msi`, à partir de http://www.pygame.org/download.shtml.

Si vous utilisez une version plus récente de python, prenez garde à télécharger le pygame correspondant. Il y en a un pour les 2.6.x et un pour les 2.7.x. Ils sont récupérables au même endroit.

Exécuter le fichier téléchargé.

Choisir les options suivantes :

 - "Install for all users".
 - Indiquer le répertoire ou vous avez installé python. (`C:\python25\` ou autre)

#### Lancement du jeu ####

Télécharger tout le contenu de ce repository. On considèrera qu'il est mis à l'emplacement `C:\blarg\`.

Ouvrir une console MS-DOS

Exécuter les commandes suivantes

    cd C:\blarg\code
    C:\python25\python.exe main.py

Amusez-vous bien !

### Transformation en exécutable  ###

#### Installation de py2exe ####

Télécharger le fichier `py2exe-0.6.9.win32-py2.5.exe`, à partir de http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/py2exe-0.6.9.win32-py2.5.exe/download?use_mirror=skylink&download=

Exécuter ce fichier, **en mode administrateur**.

S'il n'est pas lancé en mode administrateur, on risque d'obtenir un message d'avertissement "Could not create key. py2exe-py2.5" suivi de plusieurs autres messages.

Indiquer le répertoire ou vous avez installé python. (`C:\python25\` ou autre)

#### Création du .exe ####

Cette action utilise le fichier `code/pygame2exe.py`, qui a été créé à partir de ce tutoriel : http://www.pygame.org/wiki/Pygame2exe?parent=CookBook

Exécuter `code/build_blarg_exe.bat`. Une fenêtre s'ouvre, demandant parfois d'appuyer sur une touche pour continuer le processus.

Attention, si le python n'est pas installé dans `C:\python25\`, ce .bat ne marchera pas. Il faut exécuter les commandes du .bat via une console, en adaptant le chemin d'installation de python.

À l'issue de l'exécution de ces commandes, un répertoire `C:\blarg\code\dist\` a été créé, contenant l'exécutable stand-alone du jeu.

##### Message d'erreur possible

Parfois, on obtient un message d'erreur de cette forme :

    WindowsError: [Error 32]
    Le processus ne peut pas accéder au fichier car ce fichier est utilisé par un autre processus:
    'build\\bdist.win32\\winexe\\{chemin de fichier quelconque}

Le texte `{chemin de fichier quelconque}` peut prendre diverses valeurs : `collect-2.5\\encodings'`, `bundle-2.5\\python25.dll`, ...

Dans ce cas, il reste un répertoire `C:\blarg\code\build\`. Il ne sert plus à rien une fois une fois que l'exécutable a été créé. Vous pouvez le supprimer ainsi que son contenu.

À priori, la création de l'exécutable s'est faite correctement même si ce message est apparu. Dans le doute, on peut relancer la construction (ce message semble apparaître aléatoirement).

##### Message d'avertissement

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

#### Lancement du jeu avec le .exe ####

Double-cliquer sur le fichier `C:\blarg\code\dist\blarg.exe`.

Au premier lancement, il peut y avoir le message d'erreur suivant.

    An error occurred, please see the blarg.exe.log file for details.

Mais le fichier de log mentionné n'est pas créé. Le jeu se lance correctement.

Ce message n'apparaît qu'une fois.

Si vous avez l'anti-virus Avast, celui-ci va couiner un petit peu au premier lancement (validation d'un .exe non connu). Mais ça se passe sans aucun problème.

Le contenu du répertoire `dist` n'est pas versionné dans ce repository.

Pour lancer le jeu en mode fenêtre, quelle que soit la config actuelle, double-cliquer sur le fichier `C:\blarg\code\dist\blarg_windowed.bat`

#### Redistribution de l'exécutable ####

Créer un fichier compressé (.zip ou autre), contenant tout le répertoire `dist`. À savoir, les fichiers et répertoires suivants :

 - fontzy
 - img
 - sound
 - blarg_windowed.bat
 - blarg.exe
 - MSVCR71.dll
 - w9xpopen.exe

Pour installer le jeu sur un autre ordinateur, il suffit de copier le .zip, de le décompresser n'importe où, et de double-cliquer sur blarg.exe.

Si vous redistribuez ce jeu, ou une version modifiée, merci de respecter les termes de la licence (Art Libre ou CC-BY). En particulier : citer l'auteur. Un lien vers mon blog ou vers ce repository suffira.


#### Ajout de l'icône dans le .exe

Il y a une option pour ça dans py2exe. Mais je n'arrive pas à la faire fonctionner.

Pour la version de l'exécutable sur Indie DB, j'avais utilisé resource hacker, pour intégrer l'icône dans le .exe.

Je ne sais pas si je vais le refaire, car j'aime pas trop ce concept de bidouiller un .exe avec un outil différent de celui qui a été utilisé pour le fabriquer au départ. Ça risque de corrompre le fichier.

Il y a d'autres solutions, mais pas très élégantes non plus.

TODO : je laisse ça en plan pour l'instant. Je fais la conversion pour Mac. Si j'arrive à avoir les icônes comme il faut sous Mac, ça vaudra le coup de le faire aussi pour PC, histoire d'avoir un truc vraiment parfait.

Sinon : osef.

Pistes possibles :

 - http://www.wikihow.com/Change-the-Icon-for-an-Exe-File
 - http://windowsitpro.com/systems-management/how-do-i-execute-exe-files-without-typing-extension
 - http://convertico.com/
 - Le répertoire `code/shortcut_icon` de ce repository.

## Mac OS X

Todo.

Brouillon :


## Mac OS X ##

### Lancement du jeu à partir du code source ###

À priori, pas de souci de version de python, ni pour jouer, ni pour transformer en exécutable. On peut utiliser n'importe laquelle, de la 2.5 à la 2.x.

#### Installation de python et pygame ####

Je l'ai fait sur mon Mac, mais je ne me souviens plus des actions effectuées ! Si je n'ai rien noté de spécial, c'est qu'il ne devait rien y avoir de compliqué. (Je suppose).

Mon header python est comme ça :

    Python 2.6.4 (r264:75821M, Oct 27 2009, 19:48:32)
    [GCC 4.0.1 (Apple Inc. build 5493)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.

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

La valeur de la variable python `pygame.version.ver` est : `'1.9.1release-svn2575'`

Je ne sais pas trop dans quelle mesure ces renseignement sont utiles. Faites-en ce que vous voulez.

#### Lancement du jeu ####

Télécharger tout le contenu de ce repository. On considèrera qu'il est mis à l'emplacement `~/Documents/recher/blarg/`

Ouvrir un terminal et exécuter les commandes suivantes :

    cd ~/Documents/recher/blarg/code
    python zemain.py

En supposant que l'exécutable python a été mis dans le path. Normalement, ça se fait automatiquement à l'installation.

Sinon, il faudrait faire quelque chose dans ce style (en prenant garde au numéro de version 2.6 / 2.7 / autre) :

`/Library/Frameworks/Python.framework/Versions/2.6/Resources/Python.app/Contents/MacOS/Python/python zemain.py`

Le jeu devrait se lancer.

### Transformation en exécutable  ###

#### Installation de py2app et setuptools ####

Comme pour l'installation de python et pygame : je ne sais plus comment j'ai fait ! Et si ça se trouve, il n'y a rien à faire, c'est déjà pré-installé.

Se reporter au contenu de mon répertoire lib, et essayer d'avoir plus ou moins la même chose, en adaptant les divers numéros de versions.

#### Création du .app ####

Dupliquer le fichier `code/zemain.py`, en le nommant `code/blarg.py`. (C'est le moyen le plus simple de créer une app avec le bon nom).

Le fichier `code/blarg.py` n'est pas versionné dans ce repository, puisque c'est juste une copie.

Ouvrir un terminal et exécuter les commandes suivantes :

    cd ~/Documents/recher/blarg/code
    python pygame2macapp.py py2app

ou bien (voir plus loin)

python pygame2macapp.py py2app --iconfile blarg_icon.icns

Deux répertoires sont créés :

 - `code/build`. Répertoire temporaire qui peut être supprimé.
 - `code/dist`. Contient l'application `blarg.app`.

Le contenu de ces 2 répertoires n'est pas versionné dans ce repository.

Il est possible d'avoir un .app avec l'icône de son choix. J'étais parvenu à le faire pour mon jeu précédent (Blarg). Je ne l'ai pas fait pour celui-là, car j'ai la flemme et c'est un jeu terminé fortement à l'arrache.

Double-cliquer sur `code/dist/blarg.app`. Le jeu devrait se lancer sans problème.

#### Création d'un disque .dmg contenant le .app ####

Ouvrir un terminal et exécuter les commandes suivantes :

    cd ~/Documents/recher/blarg/code/dist
    hdiutil create -imagekey zlib-level=9 -srcfolder blarg.app blarg.dmg

Ça met un certain temps. Des petits points s'écrivent dans le terminal, pour montrer qu'il est vivant.

Le fichier `dist/blarg.dmg` devrait être créé.

#### Lancement du jeu à partir du disque .dmg ####

Double-cliquer sur le .dmg pour monter le disque, comme on fait d'habitude sur les Mac.

Dans le disque, double-cliquer sur l'appli `blarg.app`.

Pour les applications enregistrant des fichiers de sauvegarde, il faut préalablement copier le .app sur le disque dur (à l'endroit qu'on veut). Sinon, ça ne sauvegarde rien. Je l'avais constaté avec mon jeu précédent.


#### Redistribution de l'application ####

Copier simplement le .dmg sur un autre Mac. Puis exécuter le jeu comme expliqué dans le chapitre précédent.

Si vous redistribuez ce jeu, ou une version modifiée, merci de respecter les termes de la licence (Art Libre ou CC-BY). En particulier : citer l'auteur. Un lien vers mon blog ou vers ce repository suffira. (Là je me répète un peu, mais j'y tiens)


### Plantage éventuel à l'exécution ###

Si vous avez un peu joué avec le code source, vous risquez d'avoir l'erreur suivante au lancement de blarg.app.

    Fatal Python error: (pygame parachute) Bus Error
    Abort trap

Aucune fenêtre n'apparaît. Ce message est émis sur la sortie standard ou erreur. (Bref, dans la console).

Ça arrive avec les exécutables Mac, mais peut-être aussi sur d'autres systèmes.

Pour régler le problème, vérifiez que vous n'avez pas ajouté une instruction de ce genre dans le code :

    my_default_font = pygame.font.Font(None, 20)

Lorsqu'on instancie une police de caractère sans spécifier de fichier de police, le python parvient toujours à se débrouiller. Il s'en est gardé une sous le coude, il demande une police au système, il écrit les lettres lui-même avec son sang, ... Donc, quand on lance le jeu avec le code source, tout va bien.

Mais dans un exécutable, ça pète. Car la police par défaut n'est pas embarquée dedans. Le message d'erreur est vraiment cabbalistique, mais il faut faire avec.

Pour éviter ce genre de désagrément, indiquez toujours un fichier de police quand vous en instanciez une. N'importe quelle fichier, même un truc moche. Si vous ne savez pas où il y en a, prenez celui du repository : code/fontzy/tempesta.ttf

J'ai eu l'explication de ce bug grâce à ce post sur stackoverflow : http://stackoverflow.com/questions/3470377/my-py2app-app-will-not-open-whats-the-problem

## GNU/Linux, Ubuntu, Fedora, etc. ##

Il est certainement possible de jouer à Blarg sur ces systèmes, puisque python et pygame sont compatibles dessus. Mais je n'ai pas ce genre de chose chez moi. Désolé, je devrais certainement être qualifié de vilain monsieur.

Je vous laisse vous débrouiller tout seul, à coup de apt-get ou autres cabalisteries. Ça ne devrait pas être trop difficile, je suis sûr que vous êtes très fort. Bon courage !

Si vous rencontrez des problèmes durant l'installation, l'exécution ou autre, n'hésitez pas à m'en faire part. Je les décrirais dans ce document pour en faire profiter tout le monde.


# icônes

création du .icns

à partir du .gif.
car à partir du .png, ça fait un truc bizarre.



iconComposer

Alert
Extract Large 1bit mask from data also?


Image does not have a representation with same dimensions.
Use a scaled version

re-meme question qu avant

# lancer en windowed sous mac

mac-mini-de-recher-psychotrope:~/Documents/recher/blarg_test/blarg.app/Contents/MacOS recherpsychotrope$ ./blarg FORCE_WINDOWED
coucou
tchaw
mac-mini-de-recher-psychotrope:~/Documents/recher/blarg_test/blarg.app/Contents/MacOS recherpsychotrope$ ./blarg
coucou
tchaw
mac-mini-de-recher-psychotrope:~/Documents/recher/blarg_test/blarg.app/Contents/MacOS recherpsychotrope$ pwd
/Users/recherpsychotrope/Documents/recher/blarg_test/blarg.app/Contents/MacOS
mac-mini-de-recher-psychotrope:~/Documents/recher/blarg_test/blarg.app/Contents/MacOS recherpsychotrope$
