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

Cette action utilise le fichier `code/pygame2exe.py` quip a été créé à partir de ce tutoriel : http://www.pygame.org/wiki/Pygame2exe?parent=CookBook

Exécuter `code/build_blarg_exe.bat`

Attention, si le python n'est pas installé dans `C:\python25\`, ce .bat ne marchera pas. Il faut exécuter les commandes du .bat via une console, en adaptant le chemin d'installation de python.

À l'issue de l'exécution de ces commandes, un répertoire `C:\blarg\code\dist\` a été créé, contenant l'exécutable stand-alone du jeu.

Parfois, on obtient un message d'erreur de cette forme :

    WindowsError: [Error 32]
    Le processus ne peut pas accÚder au fichier car ce fichier est utilisÚ par un autre processus:
    'build\\bdist.win32\\winexe\\collect-2.5\\encodings'

Ou bien ?

    WindowsError: [Error 32]
    Le processus ne peut pas accÚder au fichier car ce fichier est utilisÚ par un autre processus:
    'build\\bdist.win32\\winexe\\bundle-2.5\\python25.dll'

Même avec ce message, la création de l'exécutable devrait avoir été faite.

D'autre part, on obtient le message d'avertissement suivant :

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

Ça ne m'a jamais posé de problème. À priori, tous ces fichiers sont déjà présents sur la plupart des systèmes Windows. Pour distribuer le jeu, il suffit juste de distribuer le contenu du répertoire dist.

#### Lancement du jeu avec le .exe ####

Double-cliquer sur le fichier `C:\blarg\code\dist\blarg.exe`.

Au premier lancement, il peut y avoir le message d'erreur suivant.

    An error occurred, please see the blarg.exe.log file for details.

Mais le fichier de log mentionné n'est pas créé. Le jeu se lance correctement.

Le message d'erreur n'apparaît qu'une fois.

Si vous avez l'anti-virus Avast, celui-ci va couiner un petit peu au premier lancement (validation d'un .exe non connu). Mais ça se passe sans aucun problème.

Le contenu du répertoire `dist` n'est pas versionné dans ce repository.

#### Redistribution de l'exécutable ####

Créer un fichier compressé (.zip ou autre), contenant tout le répertoire `dist`. À savoir, les fichiers et répertoires suivants :

    fontzy
    img
    sound
    blarg.exe
    MSVCR71.dll
    w9xpopen.exe

Pour installer le jeu sur un autre ordinateur, il suffit de copier le .zip, de le décompresser n'importe où, et de double-cliquer sur main.exe.

Si vous redistribuez ce jeu, ou une version modifiée, merci de respecter les termes de la licence (Art Libre ou CC-BY). En particulier : citer l'auteur. Un lien vers mon blog ou vers ce repository suffira.


# Mac OS X

Todo.
