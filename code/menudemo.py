#/usr/bin/env python
# -*- coding: iso-8859-1 -*-

"""
Blarg version 1.0

Démo du système de menu
Fichier principal, qui lance l'une des démos au choix, en fonction du
paramètre passé, ou de ce que l'utilisateur saisit.

J'aurais pu faire un menu qui lance les exemples de menus, ça aurait été
classe. Mais ça aurait rendu les exemples plus complexes, notamment au
niveau des initialisations. Là, chaque exemple est stand-alone dans son
fichier de launch, et ça va très bien.

Usage :
lancer le script en indiquant 1, 2 ou 3 en paramètres, pour lancer l'exemple
1, 2 ou 3.
Si le script est lancé sans paramètre, ou avec des paramètre incorrect, le
numéro de menu est demandé dans le prompt.
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

    while choice not in MENU_CHOICES:
        choice = raw_input("indiquez 1, 2 ou 3 pour declencher un menuz : ")

    launch_function_from_choice = {
        "1" : m.launch_demo_menu_empty.launch_demo_menu_empty,
        "2" : m.launch_demo_menu_labels.launch_demo_menu_labels,
        "3" : m.launch_demo_menu_event_teller.launch_demo_menu_event_teller,
    }
    launch_function = launch_function_from_choice[choice]
    launch_function()

