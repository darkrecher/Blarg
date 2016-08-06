# Ajout de l'icône

Les objectifs étaient les suivants :

 - Dans la barre des tâches Windows et le dock Mac, le jeu s'affiche une icône représentant le héros.
 - Le .exe Windows et le .app Mac s'affichent avec cette même icône, dans l'explorateur/finder

Ces objectifs n'ont été que partiellement réalisés.

## Windows

### Icône dans la barre des tâches

Effectué grâce à du code python dans le fichier `mainclas.py` :

    gamIcon = loadImg("gam_icon.gif", doConversion=False)
    pygame.display.set_icon(gamIcon)

Ça marche très bien.

Au passage, cela définit également l'îcône en haut à gauche de la fenêtre du jeu.

Lorsqu'on passe en mode plein écran puis qu'on repasse en mode fenêtre, l'icône reste présent dans la barre des tâches, mais a disparu de la fenêtre. À priori, ça pourrait être réglé en remettant l'instruction `pygame.display.set_icon` juste après changement de mode. Ça mériterait d'être testé à l'occasion.

### Icône dans le .exe

Il existe une variable dans `pygame2exe.py` permettant de choisir l'icône : `self.icon_file`.

Mais je n'ai jamais réussi à la faire fonctionner. J'ai spécifié un fichier .ico et un fichier .png, dans les deux cas, ça ne fait rien.

Pour information, le fichier `gam_icon.ico` a été créé à partir de `gam_icon.png`, via le site `http://convertico.com/`. Ces deux fichiers ont été déplacés dans `git/Blarg/code/shortcut_icon`, car ils ne servent plus à rien.

Pour l'exécutable mis à disposition sur [indiedb](http://www.indiedb.com/games/blarg), j'avais défini l'icône en utilisant le logiciel Resource Hacker. Mais je n'aime pas trop cette idée, car on bidouille un .exe avec un logiciel n'ayant rien à voir avec le python ni py2exe, et on ne sait pas trop ce que ça fait car le code source n'est pas librement disponible. Il y a des avertissements ici et là précisant que Resource Hacker peut corrompre les .exe, et que si ça arrive, ils déclinent toute responsabilités, blablabla.

J'avais une autre idée :

 - Renommer l'exécutable en enlevant l'extension ".exe"

 - Créer un .bat qui autoriserait temporairement d'exécuter des fichiers sans extension (http://windowsitpro.com/systems-management/how-do-i-execute-exe-files-without-typing-extension) pour démarrer le jeu

 - Convertir ce .bat en un .exe, en lui ajoutant l'icône, avec l'utilitaire Bat to Exe Converter.

Sauf qu'il est écrit un peu partout sur internet que ce fameux "Bat to Exe Converter" contient des virus. Et même si apparemment, ce serait que des faux positifs, je préfère ne pas prendre de risque.

J'avais une dernière idée : créer un raccourci relatif avec un icône dedans, mais c'était un peu cheap et un peu n'importe quoi. Juste pour rigoler, j'ai essayé d'automatiser cette création de raccourci. Pour ceux que ça intéresse, l'embryon de script est ici : `git/Blarg/code/shortcut_icon/createShortcut.vbs`

J'ai trouvés ces diverses idées ici : http://www.wikihow.com/Change-the-Icon-for-an-Exe-File


## Mac OSX

### Icône dans la barre des tâches

Effectué grâce à du code python dans le fichier `mainclas.py` :

    gamIcon = loadImg("gam_icon.gif", doConversion=False)
    pygame.display.set_icon(gamIcon)

(C'est le même pour PC et pour Mac).

Ça ne marche pas très bien.

Au moment du lancement du jeu, on voit bien l'icône de Blarg dans le dock (au départ, l'icône du dock est pris à partir de l'icône du .app).

Ensuite, pendant quelques secondes, on voit l'icône de pygame dans le dock : le serpent jaune tenant une manette entre les dents.

Finalement, on revient à l'icône de Blarg, vraisemblablement lorsque l'instruction `set_icon` dans le code du jeu est exécutée.

Le problème a été signalé ici : https://mail.python.org/pipermail/pythonmac-sig/2009-January/020834.html

Il y a une proposition de solution ici : http://www.mail-archive.com/pythonmac-sig@python.org/msg09705.html

Copie de la solution :

> You need two files, a bitmap of the icon, here dubbed "AppIcon.png",
> and an icns file created in Icon Composer, here dubbed "AppIcon.icns".
> Place both folder where your main python script is located then, in
> the main python script, append the following just after pygame.init(),
> *before* pygame.display.set_mode().
>
> pygame.display.set_icon(pygame.image.load('AppIcon.png'))
>
> Next, when you build using py2app, build as follows:
>
> python setup.py py2app --iconfile AppIcon.icns --resources AppIcon.png

Mais j'ai essayé, ça ne marche pas mieux.

### icône dans le .app

L'icône est intégré dans le .app lors de sa création, lorsqu'on exécute la commande `python pygame2macapp.py py2app --iconfile blarg_icon.icns`

Le fichier d'icône `blarg_icon.icns` est déjà présent dans le repository, au bon endroit.

Ça marche très bien.

### création du fichier blarg_icon.icns

Télécharger et installer l'application iconComposer. (Je ne sais plus d'où je l'ai récupérée ni quelle version j'ai. Il est 

possible que que je l'ai eu en installant Xcode. J'ai oublié, désolé).

**Attention, il semble que ça ne marche bien qu'avec le .gif, et pas le .png**

 - Démarrer iconComposer.

 - prendre le fichier `/code/img/gam_icon.gif` et le glisser-déplacer dans la fenêtre de iconComposer, (case "image RGB, 

large 32x32").

 - L'image s'ajoute dans cette case, ainsi que dans le Hit Mask (la case d'â côté).

 - Prendre l'image qu'on vient d'ajouter dans la case RGB 32x32 et la glisser déplacer dans la case du haut, puis celle du 

bas et celle de tout en bas.

 - Générer le fichier .icns en sélectionnant l'option idoine dans le menu de l'application. (Je ne sais plus exactement son 

nom).

Durant les glisser-déplacer de fichier et d'images, des messages peuvent poser diverses questions : 

 - "Extract Large 1bit mask from data also?" : répondre "oui".

 - "Image does not have a representation with same dimensions." : répondre "Use a scaled version"

Avant la génération de l'icône, la fenêtre doit ressembler à ceci :

![screenshot iconComposer gif](https://raw.githubusercontent.com/darkrecher/Blarg/master/doc_diverses/logo_icones/ 	

screenshot_iconComposer_gif.tiff)

Si on part de l'image en .png, ça merdouille et ça ressemble à ça :

![screenshot iconComposer png](https://raw.githubusercontent.com/darkrecher/Blarg/master/doc_diverses/logo_icones/ 	

screenshot_iconComposer.tiff)

Une fois le fichier blarg_icon.icns généré, il peut être directement utilisé lors de la créatio ndu .app.
