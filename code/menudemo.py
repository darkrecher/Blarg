#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

D�mo du syst�me de menu
Fichier principal, qui lance l'une des d�mos au choix, en fonction du
param�tre pass�, ou de ce que l'utilisateur saisit.

J'aurais pu faire un menu qui lance les exemples de menus, �a aurait �t�
classe. Mais �a aurait rendu les exemples plus complexes, notamment au
niveau des initialisations. L�, chaque exemple est stand-alone dans son
fichier de launch, et �a va tr�s bien.

Enfin... Pas tout � fait stand-alone � cause des imports, mais presque.

Usage :
Lancer le script en indiquant 1, 2 ou 3 en param�tre.
Si le script est lanc� sans param�tre, ou avec des param�tres incorrects,
le num�ro est demand� dans le prompt.
"""


import sys
import menudemo_files.launch_demo_menu_empty
import menudemo_files.launch_demo_menu_labels
import menudemo_files.launch_demo_menu_event_teller
m = menudemo_files


if __name__ == "__main__":

    MENU_CHOICES = ("1", "2", "3")
    choice = ""
    if len(sys.argv) > 1 and sys.argv[1] in MENU_CHOICES:
        choice = sys.argv[1]

    if choice not in MENU_CHOICES:
        print ""
        print "1 : menu vide. (Pour quitter : clic sur fermeture fenetre)."
        print ""
        print "2 : menu avec des labels standards. (Pour quitter : Echap)."
        print ""
        print "3 : menu avec des elements specifique reagissant aux clics"
        print "    et aux focus."
        print "    Pour cycler le focus : Tab."
        print "    Pour activer l'element courant : Espace ou Entree."
        print "    Pour quitter : Echap."
        print ""
    while choice not in MENU_CHOICES:
        choice = raw_input("indiquez 1, 2 ou 3 pour declencher un menu : ")

    launch_function_from_choice = {
        "1" : m.launch_demo_menu_empty.launch_demo_menu_empty,
        "2" : m.launch_demo_menu_labels.launch_demo_menu_labels,
        "3" : m.launch_demo_menu_event_teller.launch_demo_menu_event_teller,
    }
    launch_function = launch_function_from_choice[choice]
    launch_function()

