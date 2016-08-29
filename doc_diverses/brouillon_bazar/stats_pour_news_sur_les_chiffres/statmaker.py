#/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Blarg version 1.0

    La page du jeu sur indieDB : http://www.indiedb.com/games/blarg
    Liens vers d'autres jeux sur mon blog : http://recher.wordpress.com/jeux
    Mon twitter : http://twitter.com/_Recher_

    Ce superbe jeu, son code source, ses images, et son euh... contenu sonore est disponible,
    au choix, sous la licence Art Libre ou la licence CC-BY-SA

    Copyright 2010 Réchèr
    Copyleft : cette oeuvre est libre, vous pouvez la redistribuer et/ou la modifier selon les
    termes de la Licence Art Libre. Vous trouverez un exemplaire de cette Licence sur le site
    Copyleft Attitude http://www.artlibre.org ainsi que sur d'autres sites.

    Creative Commons - Paternité - Partage des Conditions Initiales à l'Identique 2.0 France
    http://creativecommons.org/licenses/by-sa/2.0/fr/deed.fr

Fichier de code qui sert à rien. il analyse le code de mon jeu pour sortir des stats qui poutrent.

bon, il me faut quoi ?

 - si c'est une ligne vide, ou pas.
 - si y'a un diese de commentaire ou pas (on cherche pas les # qui serait entre guillemets et qui serait donc pas des commentaires. Osef)
 - nombre de caractère espace au début. Faut que ce soit des multiples de 4. Et on enregistre la valeur max
 - longueur totale de la ligne, et position du commentaire.
 - code pas plus loin que 79 char
 - comm pas plus loin que 99 char
 - pas d'espace en fin de ligne, sauf si comm.

 - quatre types de lignes : vide, comm, comm avec code, que code
 - et faut compter les caractères de code, de comm et d'espace d'indentation

"""

import os

#PATHNAME_PYTHON_FILES = "C:/Recher/magi_shotgun/"

PATHNAME_PYTHON_FILES = "C:/Recher/hahastat"


STR_COMMENTARY = "#"

STR_TRIQUOTE = "\"" * 3


(LINE_CODE_ONLY,
 LINE_CODE_AND_COMM,
 LINE_COMMENT_ONLY,
 LINE_COMMENT_TRIQUOTE,
 LINE_TRIQUOTE,
 LINE_EMPTY,
) = range(6)

#j'ai besoin de la liste ordonnée, juste pour l'écriture à l'écran
ORDERED_LIST_LINE_TYPE = (LINE_CODE_ONLY, LINE_CODE_AND_COMM, LINE_COMMENT_ONLY,
                          LINE_COMMENT_TRIQUOTE, LINE_TRIQUOTE, LINE_EMPTY)

DICT_DESCRIPTION_TYPE_LINE = {
    LINE_CODE_ONLY        : "lignes avec que du code :",
    LINE_CODE_AND_COMM    : "lignes avec du code et des commentaires :",
    LINE_COMMENT_ONLY     : "lignes avec uniquement du commentaire de type diese :",
    LINE_COMMENT_TRIQUOTE : "lignes avec du commentaire entre triple-double-quote :",
    LINE_TRIQUOTE         : "lignes avec juste une triple-double-quote :",
    LINE_EMPTY            : "lignes vides :",
}


(CHAR_CODE,
 CHAR_COMMENT,
 CHAR_COMMENT_TRIQUOTE,
 CHAR_SPACE_INDENT_COMM,
 CHAR_SPACE_INDENT_CODE,
) = range(5)

#pareil
ORDERED_LIST_CHAR_TYPE = (CHAR_CODE, CHAR_COMMENT, CHAR_COMMENT_TRIQUOTE,
                          CHAR_SPACE_INDENT_COMM, CHAR_SPACE_INDENT_CODE)

DICT_DESCRIPTION_TYPE_CHAR = {
    CHAR_CODE              : "caractères de code :",
    CHAR_COMMENT           : "caractères de commentaires de type diese :",
    CHAR_COMMENT_TRIQUOTE  : "caractères de commentaires entre triple-double-quote :",
    CHAR_SPACE_INDENT_COMM : "caractères d'indentation dans des commentaires :",
    CHAR_SPACE_INDENT_CODE : "caractères d'indentation dans du code :",
}


def argleu(message):
    """
    zob
    """
    print "!" * 70
    print "!" * 10 + message + "!" * 10
    print "!" * 70



class PythonFileAnalyzer():

    DIC_STAT_LINE_INIT = {
        LINE_EMPTY             : 0,
        LINE_CODE_ONLY         : 0,
        LINE_COMMENT_ONLY      : 0,
        LINE_CODE_AND_COMM     : 0,
        LINE_TRIQUOTE          : 0,
        LINE_COMMENT_TRIQUOTE  : 0,
    }

    DIC_STAT_LINE_CHAR_INIT = {
       CHAR_SPACE_INDENT_COMM  : 0,
       CHAR_SPACE_INDENT_CODE  : 0,
       CHAR_COMMENT            : 0,
       CHAR_COMMENT_TRIQUOTE   : 0,
       CHAR_CODE               : 0,
    }


    def __init__(self):
        """
        zob
        """
        #nommage fail (avec s et sans s)
        self.dicTotalNbrLines = dict(self.DIC_STAT_LINE_INIT)
        self.dicTotalNbrChar = dict(self.DIC_STAT_LINE_CHAR_INIT)
        self.totalNbrFunction = 0
        self.totalNbrClass = 0

        self.resetFileStat()


    def resetFileStat(self):
        """
        zob
        """
        #nommage fail (avec s et sans s)
        self.dicNbrLines = dict(self.DIC_STAT_LINE_INIT)
        self.dicNbrChar = dict(self.DIC_STAT_LINE_CHAR_INIT)

        self.nbrFunction = 0
        self.nbrClass = 0


        #mouirf. useless
        self.previousNbrCodeSpaceIndent = 0
        self.nbrImbricationCurrent = 0
        self.nbrImbricationMax = 0

        self.inTriquoteComment = False


    def analyzePythonFile(self, pythonFilename):
        """
        zob
        """

        self.resetFileStat()

        pythonFile = open(PATHNAME_PYTHON_FILES + os.sep + pythonFilename, "r")

        for line in pythonFile.xreadlines():
            self.analyzePythonLine(line)

        if self.inTriquoteComment:
            argleu("petit problème de finissage de fichier dedans un commentaire triquote")


    def analyzePythonLine(self, line):
        """
        zob
        """

        #print line
        line = line.strip("\r\n")

        if len(line) == 0:

            self.dicNbrLines[LINE_EMPTY] += 1
            return

        if len(line) > 99:
            argleu(line + " : superieur a 99. not-Argh !")

        cursorSpace = 0
        while line[cursorSpace] == " ":
            cursorSpace += 1

        #print "nombre d'espace d'indentation au début : ", cursorSpace


        if STR_TRIQUOTE in line:

            self.inTriquoteComment = not(self.inTriquoteComment)

            if cursorSpace + len(STR_TRIQUOTE) != len(line):
                argleu(line + " : triple-quote avec d'autres trucs ailleurs")

            self.dicNbrLines[LINE_TRIQUOTE] += 1
            self.dicNbrChar[CHAR_SPACE_INDENT_COMM] += cursorSpace
            self.dicNbrChar[CHAR_COMMENT_TRIQUOTE]  += len(STR_TRIQUOTE)
            return


        if self.inTriquoteComment:

            self.dicNbrLines[LINE_COMMENT_TRIQUOTE] += 1
            self.dicNbrChar[CHAR_SPACE_INDENT_COMM] += cursorSpace
            self.dicNbrChar[CHAR_COMMENT_TRIQUOTE]  += len(line) - cursorSpace
            return


        if line[cursorSpace] == STR_COMMENTARY:

            self.dicNbrLines[LINE_COMMENT_ONLY] += 1
            self.dicNbrChar[CHAR_SPACE_INDENT_COMM] += cursorSpace
            self.dicNbrChar[CHAR_COMMENT]  += len(line) - cursorSpace
            return


        if STR_COMMENTARY in line:

            posStrCommentary = line.find(STR_COMMENTARY)

            if posStrCommentary > 79:
                argleu(line + " peut-être code plus que 79 char")

            self.dicNbrLines[LINE_CODE_AND_COMM] += 1
            self.dicNbrChar[CHAR_SPACE_INDENT_CODE] += cursorSpace
            self.dicNbrChar[CHAR_CODE]  += posStrCommentary - cursorSpace
            self.dicNbrChar[CHAR_COMMENT]  += len(line) - posStrCommentary

            if "def " in line[:posStrCommentary]:
                self.nbrFunction += 1

            if "class " in line[:posStrCommentary]:
                self.nbrClass += 1

            return

        else:

            if len(line) > 79:
                argleu(line + " code plus que 79 char. La c'est sur")

            self.dicNbrLines[LINE_CODE_ONLY] += 1
            self.dicNbrChar[CHAR_SPACE_INDENT_CODE] += cursorSpace
            self.dicNbrChar[CHAR_CODE]  += len(line) - cursorSpace

            if "def " in line:
                self.nbrFunction += 1

            if "class " in line:
                self.nbrClass += 1

            return


    def addCurrentFileStatToTotalStat(self):
        """
        zob
        """
        for statKey, statValCurrentFile in self.dicNbrLines.items():
            statValTotal = self.dicTotalNbrLines[statKey]
            statValTotal += statValCurrentFile
            self.dicTotalNbrLines[statKey] = statValTotal

        #factorisation fail
        for statKey, statValCurrentFile in self.dicNbrChar.items():
            statValTotal = self.dicTotalNbrChar[statKey]
            statValTotal += statValCurrentFile
            self.dicTotalNbrChar[statKey] = statValTotal

        self.totalNbrFunction += self.nbrFunction
        self.totalNbrClass += self.nbrClass


    def _printStatInfo(self, dicLines, dicChars, nbrFunction, nbrClass):
        """
        zob
        """

        print "-" * 50
        print "-- COMPTAGE DU NOMBRE DE LIGNES SELON LEUR TYPE --"
        print "-" * 50
        print ""

        sumLine = 0

        for lineType in ORDERED_LIST_LINE_TYPE:

            descripLine = DICT_DESCRIPTION_TYPE_LINE[lineType]
            nbrLine = dicLines[lineType]
            print descripLine.ljust(55), str(nbrLine).rjust(5)
            print ""
            sumLine += nbrLine

        print "nombre total de ligneu : ", sumLine
        print ""

        #factorisation fail

        print "-" * 50
        print "-- COMPTAGE DU NOMBRE DE CHARS SELON LEUR TYPE --"
        print "-" * 50
        print ""

        sumChar = 0

        for charType in ORDERED_LIST_CHAR_TYPE:

            descripChar = DICT_DESCRIPTION_TYPE_CHAR[charType]
            nbrChar = dicChars[charType]
            sumChar += nbrChar
            print descripChar.ljust(55), str(nbrChar).rjust(5)
            print ""

        print "nombre total de chareu : ", sumChar
        print ""

        print "nombre de fonction : ", nbrFunction
        print "nombre de class : ", nbrClass


    def printCurrentFileInfo(self):
        """
        zob
        """
        self._printStatInfo(self.dicNbrLines, self.dicNbrChar, self.nbrFunction, self.nbrClass)


    def printTotalInfo(self):
        """
        zob
        """
        self._printStatInfo(self.dicTotalNbrLines, self.dicTotalNbrChar, self.totalNbrFunction, self.totalNbrClass)


if __name__ == "__main__":

    print "yohop"

    pythonFileAnalyzer = PythonFileAnalyzer()

    for filename in os.listdir(PATHNAME_PYTHON_FILES):
        if filename.endswith(".py"):
            print "------------------- ", filename, " -------------------"

            pythonFileAnalyzer.analyzePythonFile(filename)

            pythonFileAnalyzer.printCurrentFileInfo()

            pythonFileAnalyzer.addCurrentFileStatToTotalStat()

    print "DER TOTALEU  !! YAAAAHHH !!!"

    pythonFileAnalyzer.printTotalInfo()

    print "tchouss"













