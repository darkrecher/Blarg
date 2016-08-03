# PC


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


# icône Mac

brouillon

création du .icns

à partir du .gif.
car à partir du .png, ça fait un truc bizarre.



iconComposer

Alert
Extract Large 1bit mask from data also?


Image does not have a representation with same dimensions.
Use a scaled version

re-meme question qu avant

## lancer en windowed sous mac

mac-mini-de-recher-psychotrope:~/Documents/recher/blarg_test/blarg.app/Contents/MacOS recherpsychotrope$ ./blarg FORCE_WINDOWED
coucou
tchaw
mac-mini-de-recher-psychotrope:~/Documents/recher/blarg_test/blarg.app/Contents/MacOS recherpsychotrope$ ./blarg
coucou
tchaw
mac-mini-de-recher-psychotrope:~/Documents/recher/blarg_test/blarg.app/Contents/MacOS recherpsychotrope$ pwd
/Users/recherpsychotrope/Documents/recher/blarg_test/blarg.app/Contents/MacOS
mac-mini-de-recher-psychotrope:~/Documents/recher/blarg_test/blarg.app/Contents/MacOS recherpsychotrope$
