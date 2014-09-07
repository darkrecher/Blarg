#/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
Blarg version 1.0

    La page du jeu sur indieDB : http://www.indiedb.com/games/blarg
    Liens vers d'autres jeux sur mon blog : http://recher.wordpress.com/jeux
    Mon twitter : http://twitter.com/_Recher_

    Ce superbe jeu, son code source, ses images, et son euh... contenu sonore est disponible,
    au choix, sous la licence Art Libre ou la licence CC-BY-SA

    Copyright 2010 R�ch�r
    Copyleft : cette oeuvre est libre, vous pouvez la redistribuer et/ou la modifier selon les
    termes de la Licence Art Libre. Vous trouverez un exemplaire de cette Licence sur le site
    Copyleft Attitude http://www.artlibre.org ainsi que sur d'autres sites.

    Creative Commons - Paternit� - Partage des Conditions Initiales � l'Identique 2.0 France
    http://creativecommons.org/licenses/by-sa/2.0/fr/deed.fr

date de la derni�re relecture-commentage : 17/02/2011

fichier qui g�re une partie du jeu. (une partie dans le sens "je joue une partie")
putain de langue fran�aise.
"""

import pygame
import pygame.locals
pygl = pygame.locals

from common import (securedPrint, pyRect, SCREEN_RECT, COLOR_BLACK,
                    loadImg, loadImgInDict, addListRectOrNot,
                    FRAME_PER_SECOND, COORD_HERO_START, GAME_INFO_LIMIT_X,
                    IHMSG_QUIT, IHMSG_TOTALQUIT, IHMSG_VOID,
                    KEY_DIR_UP, KEY_DIR_DOWN, KEY_DIR_RIGHT, KEY_DIR_LEFT,
                    KEY_FIRE, KEY_RELOAD,
                    STIMULI_HERO_MOVE, STIMULI_HERO_FIRE, STIMULI_HERO_RELOAD,
                    SPEED, )

from sprsiman import SpriteSimpleManager
from sprsigen import SpriteSimpleGenerator, loadAllSprSimpleImgInfo
import lamoche
import herobody
import herohead
from cobulmag import CollHandlerBulletMagi
from cohermag import CollHandlerHeroMagi
from scoremn  import ScoreManager
import ammoview
import lifeview
import hero
import magician
import maggen


#identifiants des dictionnaires d'images, � transmettre aux classes correspondantes
(DIC_IMG_HEROBODY,    #corps du h�ros
 DIC_IMG_HEROHEAD,    #t�te du h�ros
 DIC_IMG_MAGICIAN,    #magicien
 DIC_IMG_AMMOVIEWER,  #AmmoViewer (classe affichant les cartouches, � gauche)
 DIC_IMG_LIFEPOINT,   #LifePointViewer (classe affichant les points de vie)
) = range(5)

#fichier contenant la superbe image de fond moche du jeu.
IMG_BG_GAME_FILENAME = "bggame.png"


#mapping de touche par d�faut. Pour le h�ros.
# - cl� : identifiant d'une touche. C'est pas le code de la touche du clavier.
#         C'est mon identifiant interne � moi tout seul.
# - valeur : tuple de 2 elements
#    * identifiant du stimuli � envoyer au h�ros.
#    * sous-tuple. liste de param�tres � envoyer en m�me temps que le stimuli.
#                  �a ne sers que pour le stimuli de mouvement, pour indiquer
#                  les coorodnn�es X,Y de d�placement � appliquer au h�ros.
DIC_KEY_STIM_INFO_MAPPING = {
    KEY_DIR_UP     : (STIMULI_HERO_MOVE,   (pyRect( 0,      -SPEED), ) ),
    KEY_DIR_DOWN   : (STIMULI_HERO_MOVE,   (pyRect( 0,      +SPEED), ) ),
    KEY_DIR_RIGHT  : (STIMULI_HERO_MOVE,   (pyRect(+SPEED,  0),      ) ),
    KEY_DIR_LEFT   : (STIMULI_HERO_MOVE,   (pyRect(-SPEED,  0),      ) ),
    KEY_FIRE       : (STIMULI_HERO_FIRE,   (), ),
    KEY_RELOAD     : (STIMULI_HERO_RELOAD, (), ),
}

#position du bord haut-droit du label affichant le score.
#le score est �crit avec le texte align� � droite, sur ce bord droit.
POS_LABEL_SCORE = pyRect(GAME_INFO_LIMIT_X-5, 2)



class Game():
    """
    classe qui g�re tout le jeu.
    """

    def __init__(self, screen, scoreManager, fontScore):
        """
        constructeur. (thx captain obvious)

        entr�e :
            screen : Surface principale de l'�cran, sur laquelle s'affiche le jeu.
            scoreManager : classe g�rant le score, les hiscores, etc...
            fontScore : police de caract�res utilis�e pour afficher le score
        """
        self.screen = screen
        self.scoreManager = scoreManager
        self.fontScore = fontScore


    def loadGameStuff(self):
        """
        chargement de tous le bazar n�cessaire au jeu. Sprites, images, ...
        """

        #Chargement des images et rangement dans des dictionnaires et dans les
        #classes qui vont bien.

        #ce dictionnaire va contenir les dictionnaires d'images.
        # - cl� : identifiant du dictionnaire d'image (DIC_IMG_XXX)
        # - valeur : un dictionnaire dicImg, avec :
        #             - cl� : un identifiant d'image
        #             - valeur : une surface contenant l'image.
        #ces dicImg doivent �tre charg�s avec la fonction loadImgInDict.
        self.dicImg = {}

        #liste de tuple de 2 elem, avec :
        # - identifiant du dictionnaire d'image (DIC_IMG_XXX)
        # - sous-sous-tuple, contenant les param�tres � fournir � la fonction loadImgInDict,
        #   pour charger ces images. Voir common.loadImgInDict pour avoir le d�tail (� la gorg�e)
        PARAM_FOR_LOADING_THE_DIC_IMG = (

            (DIC_IMG_HEROBODY,   (herobody.LIST_IMG_FILE_SHORT_NAME,
                                  herobody.IMG_FILENAME_PREFIX)),

            (DIC_IMG_HEROHEAD,   (herohead.LIST_IMG_FILE_SHORT_NAME,
                                  herohead.IMG_FILENAME_PREFIX)),

            (DIC_IMG_MAGICIAN,   (magician.LIST_IMG_FILE_SHORT_NAME,
                                  magician.IMG_FILENAME_PREFIX)),

            #pour �ui l�, on est oblig� de sp�cifier explicitement la couleur transparente (black)
            #car elle n'est pas dans le coin sup�rieur gauche de l'�cran pour certaines images.
            (DIC_IMG_AMMOVIEWER, (ammoview.LIST_IMG_FILE_SHORT_NAME,
                                  ammoview.IMG_FILENAME_PREFIX, COLOR_BLACK)),

            #pas de pr�fixe de nom de fichier pour ce dico l�.
            (DIC_IMG_LIFEPOINT,  (lifeview.LIST_VESTEJEAN_IMG_FILENAME, )),

        )

        #chargement de tous les dictionnaires d'images, et rangement dans le gros
        #dictionnaire principale self.dicImg.
        for dicImgKey, dicImgLoadParam in PARAM_FOR_LOADING_THE_DIC_IMG:
            self.dicImg[dicImgKey] = loadImgInDict(*dicImgLoadParam)

        #j'ai tripp� sur ce dictionnaire de dictionnaire, juste pour factoriser les appels
        #� loadImgInDict. Oui je suis d�bile et j'aime �a.

        #chargement de la grande image du background du jeu (herbe, mur, etc.)
        self.imgBackground = loadImg(IMG_BG_GAME_FILENAME, None)

        #il faut compl�ter le dictionnaire contenant les images de la t�te du h�ros.
        #on doit cr�er la t�te regardant � gauche � partir de la t�te regardant � droite.
        herohead.preRenderFlippedHeadLeftRight(self.dicImg[DIC_IMG_HEROHEAD])

        #r�cup�ration, dans le dictionnaire de dictionnaire machin,
        #d'une r�f�rence vers l'image du magicien dans son �tat normal.
        imgMagiNormal = self.dicImg[DIC_IMG_MAGICIAN][magician.IMG_NORMAL]
        #on a besoin de cette image de magicien lorsqu'on doit charger toutes les
        #images des SimpleSprite. Elle est n�cessaire pour le SimpleSprite de MagDyingRotate
        #(le magicien qui meurt en tournoyant et en volant dans les airs youhouuuu)
        self.dicImgInfoSpriteSimple = loadAllSprSimpleImgInfo(imgMagiNormal)


    def isMagicianActive(self, magicianGenerator,
                         groupMagicianAppearing, groupMagician):
        """
        indique si y'a encore des magiciens actifs. Les magiciens actifs sont les trucs suivants :
         - des magiciens pas encore cr��s, mais en r�serve dans des genPattern
         - des magiciens en train d'appara�tre
         - des magiciens vivants, et qui sont toujours en mouvement
             (donc soit des magiRand, soit des magiLine qui sont pas arriv�s � destination.)

        et donc par cons�quent, les magiciens inactifs sont les suivants :
         - ceux qui sont morts, ou en train de crever ou en train d'exploser.
         - les magiLine qui sont arriv�s � destination.

        entr�e :
            magicianGenerator : classe �ponyme, permet de g�n�rer les waves de magiciens
            groupMagicianAppearing : groupe de sprite contenant les magiciens en train
                                     de faire leur anim d'apparition.
            groupMagician : groupe de sprite contenant tous les autres magiciens.

        j'ai besoin de tous ces param�tres en entr�e car ils ne sont pas stock�s comme attribut,
        dans la classe elle-m�me. Et j'ai pas envie de les stocker, comme �a, je suis s�r qu'entre
        deux parties, je refabrique tout et je repars compl�tement � neuf. (Les seuls trucs
        que je stocke, c'est les images, les sons, et la configs,
        car ils viennent de fichier de donn�es.

        plat-dessert :
            boolean. True : il y a encore des magiciens actifs. False : Il n'y en a plus.
        """

        #on v�rifie si il reste des magiciens pas encore cr��s, en r�serve dans des genPattern
        if len(magicianGenerator.listGenPattern) > 0:
            return True

        #on v�rifie si il reste des magiciens en train d'appara�tre
        if len(groupMagicianAppearing) > 0:
            return True

        #on v�rifie si il reste des magiciens vivants.

        activStates = (magician.ALIVE, magician.HURT)

        for magi in groupMagician:
            if magi.currentState in activStates and not magi.isMoveFinished():
                return True

        #on n'a trouv� aucun magicien actif.
        return False


    def buildDicKeyCodeStimInfo(self, dicKeyCodeMapping):
        """
        construit le dicKeyCodeStimInfo. Dictionnaire contenant le mapping de touche
        r�ellement utilis� pour jouer cette partie.

        Bon, je m'explique, parce que c'est le bordel.

        idKey : mon identifiant de touche interne. C'est � dire :
                KEY_DIR_UP, KEY_DIR_DOWN, KEY_DIR_RIGHT, KEY_DIR_LEFT, KEY_FIRE, KEY_RELOAD.

        realKeyCode : int. Code de la touche envoy� par le clavier quand le joueur appuie dessus.

        stimuliInfo : tuple. Info de stimuli � envoyer au h�ros. C'est � dire :
                      STIMULI_HERO_MOVE + les coordonn�es, STIMULI_HERO_FIRE, STIMULI_HERO_RELOAD

        entr�es :
            dicKeyCodeMapping. dico de correspondance : idKey -> realKeyCode
            (ce dico d�pend de la config d�finie par le joueur)

        ce fichier de code contient :
            DIC_KEY_STIM_INFO_MAPPING. dico de correspondance : idKey -> stimuliInfo
            (ce dico est une constante)

        plat-dessert :
            d�finition de self.dicKeyCodeStimInfo.
            dico de correspondance : realKeyCode -> StimuliInfo
        """
        self.dicKeyCodeStimInfo = {}

        #il faut avoir autant de cl�s dans DIC_KEY_STIM_INFO_MAPPING que dans dicKeyCodeMapping,
        #sinon, on va paumer des trucs en chemins, ou �a va planter.
        #Mais je suis fort, et je sais que j'ai pas besoin de v�rifier �a.

        for idKey, keyCodeInfo in dicKeyCodeMapping.items():
            #bon, y'a pas une correspondance directe idKey -> realKeyCode.
            #En vrai c'est : idKey -> (realKeyCode, <truc � la con>).
            realKeyCode = keyCodeInfo[0]
            stimuliInfo = DIC_KEY_STIM_INFO_MAPPING[idKey]
            self.dicKeyCodeStimInfo[realKeyCode] = stimuliInfo


    def playOneGame(self, dicKeyCodeMapping, dogDom):
        """
        fonction pour jouer une partie.
        la partie s'arr�te quand le joueur a appuy� sur Echap,
        ou si un �v�nement "quit" (alt-F4, fermage de fen�tre) est re�u,
        ou si le h�ros perd toutes ses vies.

        entr�ees:
         - dicKeyCodeMapping : voir fonction buildDicKeyCodeStimInfo de ce fichier
         - dogDom : boolean. Indique si le h�ros perd des vies ou pas.

        plat-dessert : tuple de 2 elem :

         - sous-tuple ihmsgInfo. Il peut contenir les valeurs suivantes :
             * IHMSG_QUIT et IHMSG_TOTALQUIT : le joueur veut quitter le jeu. (Alt-F4, ou autre)
             * IHMSG_QUIT : le joueur veut juste quitter la partie (il a appuy� sur Esc)
             * tuple vide : le joueur voulait pas quitter la partie, mais bon, on l'a quand
                            m�me fait quitter parce qu'il est mort, mmmm'voyez.

         - nbrErreur. int : nombre d'erreur qui ont eu lieu durant le jeu.
           dans l'�tat actuel des choses, je vois pas d'erreurs possibles. Haha.

        pr�-conditions :
          - le self.scoreManager r�f�renc� par cette classe, doit avoir �t� configur�
            pour qu'il contienne le nom et les stats du joueur s�lectionn�.
          - et faut avoir ex�cut� loadGameStuff, evidemment.
        """
        nbrErreur = 0

        # --- initialisation des trucs ---

        self.buildDicKeyCodeStimInfo(dicKeyCodeMapping)

        #initialisation des scores pour cette partie (pas les stats, les scores)
        self.scoreManager.initCurrentGameData()

        #on va foutre tous les sprites � afficher dans le groupe allSprites.
        #y'aura d'autres group de sprites, mais ce sera que pour la gestion, pas l'affichage.
        #Du coup, pas de gestion de quel sprite est devant ou derri�re. osef. pas besoin.
        allSprites = pygame.sprite.RenderUpdates()

        #classes pour g�rer les simpleSprites
        spriteSimpleManager = SpriteSimpleManager(allSprites)
        param = (spriteSimpleManager, self.dicImgInfoSpriteSimple)
        spriteSimpleGenerator = SpriteSimpleGenerator(*param)

        #Ca c'est le putain d'objet qui permet de ma�triser le temps !!!
        #Talaaaa, je suis le ma�tre du temps. et des frames par secondes aussi.
        clock = pygame.time.Clock()

        #cr�ation du label affichant le score, en l'initialisant avec la valeur de d�part : 0
        score = self.scoreManager.currentScore

        lblScore = lamoche.Lamoche(POS_LABEL_SCORE, self.fontScore,
                                   str(score), alignX=lamoche.ALIGN_RIGHT)

        allSprites.add(lblScore)

        #groupe de sprite qui va contenir tous les magiciens.
        groupMagician = pygame.sprite.Group()
        #groupe de sprite qui va contenir tous les magiciens faisant leur anim d'apparition.
        groupMagicianAppearing = pygame.sprite.Group()

        #objet g�rant les collisions entre les bullets tir�s par le h�ros et les magiciens
        collHandlerBulletMagi = CollHandlerBulletMagi(groupMagician)
        #objet g�rant les collisions entre le h�ros et les magiciens.
        collHandlerHeroMagi = CollHandlerHeroMagi(groupMagician)

        #objet affichant les cartouches dans le chargeur.
        param = (self.dicImg[DIC_IMG_AMMOVIEWER], spriteSimpleGenerator)
        ammoViewer = ammoview.AmmoViewer(*param)

        #objet affichant les points de vie
        param = (self.dicImg[DIC_IMG_LIFEPOINT], )
        lifePointViewer = lifeview.LifePointViewer(*param)

        #weeeeee caaaaan beeee heeeeerooooooo !!!!
        theHero = hero.Hero(self.dicImg[DIC_IMG_HEROBODY],
                            self.dicImg[DIC_IMG_HEROHEAD],
                            COORD_HERO_START, collHandlerBulletMagi,
                            spriteSimpleGenerator, ammoViewer,
                            lifePointViewer, self.scoreManager, dogDom)

        #ajout des sprites composant le h�ro, dans le groupe allSprites
        allSprites.add(theHero.heroBody)
        allSprites.add(theHero.heroHead)

        #cr�ation du magician Generator. Classe qui g�n�re les waves successives de magiciens.
        param = (groupMagicianAppearing, self.dicImg[DIC_IMG_MAGICIAN],
                 spriteSimpleGenerator, theHero)

        magicianGenerator = maggen.MagicianGenerator(*param)

        # --- affichage inital des �l�ments ---

        #on remplit le screen tout en noir. (juste apr�s on mettra l'image de fond,
        #mais on n'est pas s�r qu'elle remplisse tout l'�cran : donc paf.)
        self.screen.fill(COLOR_BLACK)
        #Maintenant on balance l'image de fond sur l'�cran.
        self.screen.blit(self.imgBackground, (0, 0))

        #on affiche initialement tous les points de vie (vestes en jean)
        lifePointViewer.groupLifePoints.draw(self.screen)

        #pas la peine d'afficher toutes les cartouches, �a se fait tout seul, le AmmoViewer
        #les fait appara�tre une par une vachement vite, et je trouve �a cool.

        #pas la peine d'afficher le score. Ca va se faire tout seul d�s le premier cycle,
        #avec le scoreManager.scoreChanged qui s'init � True lors d'une nouvelle partie.

        #les autres trucs (heros, magiciens, ...) sont syst�matiquement r�affich�s � chaque cycle,
        #donc pas la peine de s'en soucier ici.

        #(c'est quand m�me bizarre que ce soit pas g�r� au m�me niveau pour tous les objets, cette
        #histoire d'affichagee initial.)

        #gros flip global pour tout rafra�chir.
        pygame.display.flip()

        #compteur pour effectuer un rafra�chissement total de l'�cran tous les X cycles.
        #si je fais pas �a, �a fait un rafraichissement progressif tr�s moche lorsque
        #l'ordi s'est mis en veille pendant une partie.
        counterTotalFlip = 0

        # ---------- Mega grosse boucle du jeu ----------

        while 1: #�a, c'est la classe, d�j� pour commencer.

            #Donc l� si tout se passe bien le jeu va s'auto-ralentir pour atteindre
            #le nombre de FPS sp�cifi� par rapport au nombre de fois qu'il fait
            #cette boucle. Et si c'est trop lent, il s'auto-ralentit pas, mais c'est la merde.
            clock.tick(FRAME_PER_SECOND)

            #les sprites de l'ammoViewer ( = BulletShell = cartouches )
            #ils ne changent pas forc�ment. Donc on commence par d�terminer si y'aura
            #un changement. Si oui, il faudra les clearer et les r�afficher,
            #comme des sprites normaux qui changent tout le temps.
            mustUpdateAmmoViewer = ammoViewer.determineIsUpdatingSthg()
            #pareil, mais pour les points de vie
            #nom trop long de merde
            mustUpdatLife = lifePointViewer.determineIsUpdatingSthg()
            mustUpdateLifePointViewer = mustUpdatLife

            #on efface tous les sprites existants, en redessinant dessus la surface imgBackground
            allSprites.clear(self.screen, self.imgBackground)

            #m�me chose pour les sprites de l'ammoViewer, mais seulement si c'est n�cessaire
            if mustUpdateAmmoViewer:
                param = (self.screen, self.imgBackground)
                ammoViewer.groupBulShell.clear(*param)

            #m�me m�me chose. Bon, faudra peut �tre r�fl�chir � de la factorisation. ou pas.
            if mustUpdateLifePointViewer:
                param = (self.screen, self.imgBackground)
                lifePointViewer.groupLifePoints.clear(*param)

            #R�cup et gestion des events (y'a presque rien. Les events des touches viennent apr�s.
            for event in pygame.event.get():
                #on quitte la partie si le joueur fait un �v�nement de quittage (alt-F4, ...)
                #et il faudra carr�ment quitter le programme.
                if event.type == pygl.QUIT:
                    #on indique dans les params de retour qu'il faut quitter tout le jeu)
                    return ((IHMSG_QUIT, IHMSG_TOTALQUIT), nbrErreur)

            #on r�cup�re un gros dictionnaire contenant toute les touches,
            #avec des bool�ens indiquant si elles sont appuy�es ou pas.
            dictKeyPressed = pygame.key.get_pressed()

            #prises en compte des commandes du jeu-lui-m�me, selon les touches appuy�es.
            #C'est rigolo d'�crire "machin-lui-m�me", �a me fait penser quand j'organisais
            #le congr�s industriel. J'ai vraiment servi � rien sur ce truc.

            #on quitte la partie si le joueur a appuy� sur Echap. Mais on quittera pas le prog
            if dictKeyPressed[pygl.K_ESCAPE]:
                #on indique dans les params de retour qu'il faut juste quitter la partie.
                return ((IHMSG_QUIT, ), nbrErreur)

            #prises en compte des commandes li�es au h�ros, selon les touches appuy�es.
            #(le joueur ne peut plus faire bouger/tirer/recharger le h�ros si il cr�ve)
            if theHero.currentState not in (hero.DYING, hero.DEAD):

                for key, stimuliInfo in self.dicKeyCodeStimInfo.items():
                    if dictKeyPressed[key] :
                        #l'une des touches correspondant � un stimuli � envoyer au h�ros
                        #a �t� appuy�e. on r�cup�re dans le dico de mapping l'identifiant du
                        #stimuli, et les param�tres. Et on balance tout �a au h�ros.
                        stimuliId, stimuliParam = stimuliInfo
                        theHero.takeStimuliGeneric(stimuliId, stimuliParam)

            #si on a enregistr� des mouvements � faire pour le h�ros, on les effectue
            theHero.makeBufferMove()

            #on fait avancer la machine � �tat du h�ros. (il recharge, il r�arme, ...)
            theHero.advanceStateOneStep()

            #update du g�n�rateur de wave de magicien.
            magicianGenerator.update()

            #update de tous les sprites de magiciens en train de faire leurs anim d'apparition
            groupMagicianAppearing.update()

            #on r�cup�re la liste de tous les magiciens ayant fini leur anim d'apparition.
            listMagiToTransfer = [ magi for magi in groupMagicianAppearing
                                   if magi.currentState == magician.ALIVE ]

            #il faut transf�rer ces magiciens de groupMagicianAppearing vers groupMagician,
            #pour qu'ils puissent vivre leur vie. (oh oui !)
            for magicianToTransfer in listMagiToTransfer:
                groupMagicianAppearing.remove(magicianToTransfer)
                groupMagician.add(magicianToTransfer)
                #il faut l'ajouter dans allSprites. En fait, quand le sprite
                #de magicien est "appearing", il ne s'affiche pas par lui-m�me.
                #Il contient un SimpleSprite qui s'affiche et se g�re tout seul
                #avec le SpriteSimpleManager. Quand le magicien a fini son anim d'appearing,
                #il doit s'afficher, comme les autres. On le balance alors dans allSprites.
                #Putain c'est le bordel. Faudra simplifier �a un jour.
                allSprites.add(magicianToTransfer)

            #lancement de l'update sur chaque magicien.
            #on fait d'abord l'update, et plus tard on fera les remove. Ca �vite de se trimbaler
            #pendant un cycle suppl�mentaire des magiciens qui servent � rien. (ah bon ?)
            groupMagician.update()

            #on regarde si il y a encore des magiciens actifs dans le jeu.
            #Si y'en a plus, faut avertir le g�n�rateur de waves de magicien.
            #Il a besoin de conna�tre cet info, pour passer directement � la wave suivante,
            #calculer les bonus, etc...
            param = (magicianGenerator, groupMagicianAppearing, groupMagician)

            if not self.isMagicianActive(*param):
                magicianGenerator.takeStimuliNoMoreActiveMagi()

            #lancement de l'update sur les SimpleSprite, et supression de ceux
            #qui servent plus � rien.
            spriteSimpleManager.updateAndRemoveSprites()

            #update de la tronche du h�ros. (gestion du smiling)
            theHero.heroHead.update()

            #update de l'ammoViewer, si n�cessaire.
            if mustUpdateAmmoViewer:
                ammoViewer.updateAmmoViewer()

            #m�me chose pour lifePointViewer.
            if mustUpdateLifePointViewer:
                lifePointViewer.update()

            #supression des magiciens crev�s. je pr�f�re le faire en deux �tapes.
            #D'abord on construit la liste des magiciens � supprimer,
            #puis on les supprime des deux groups de sprites.
            #(celui pour l'affichage, et celui pour la gestion sp�cifique des magiciens)
            #je veux pas parcourir les elements du groupe et les virer en m�me temps,
            #c'est un peu dangereux, et bizarre.
            listMagicianToRemove = [ magi for magi in groupMagician
                                     if magi.currentState == magician.DEAD ]

            for magicianToRemove in listMagicianToRemove:
                groupMagician.remove(magicianToRemove)
                allSprites.remove(magicianToRemove)

            #tests de collision entre le h�ros et les magiciens. Si y'en a, le h�ro a mal.
            #Et faudra lui enlever un point de vie. (le collisionHandler g�re �a tout seul)
            collHandlerHeroMagi.testCollisionHeroMagi(theHero)

            #reaffichage eventuel du score, si il a chang�
            if self.scoreManager.scoreChanged:
                #recup�ration de la nouvelle valeur de score, aupr�s du scoreManager
                score = self.scoreManager.currentScore
                #transmission de cet valeur au label affichant le score
                lblScore.updateAttrib(text=str(score))
                #indication au scoreManager que c'est bon, on a pris en compte le changement.
                self.scoreManager.scoreChanged = False

            #Redessinage de tous les sprites, bordel. (osef de l'ordre de dessin)
            #on r�cup�re une liste de "dirty Rect". C'est � dire les zones de l'�cran
            #qui ont d� �tre redessin�es.
            listDirtyRects = allSprites.draw(self.screen)

            #Redessinage des sprites de l'ammoViewer, si c'est n�cessaire.
            if mustUpdateAmmoViewer:
                listDirtyRectsAmmo = ammoViewer.groupBulShell.draw(self.screen)
                #Il faut ajouter les dirty Rects de ce redessinage aux dirty rects
                #du redessinage global.
                addListRectOrNot(listDirtyRects, listDirtyRectsAmmo)

            #m�me chose. mais pour le LifePointViewer.
            if mustUpdateLifePointViewer:
                #nom � rallonge de merde
                funcDraw = lifePointViewer.groupLifePoints.draw
                listDirtyRectsLifePoint = funcDraw(self.screen)
                #ajout des dirty Rects de ce redessinage aux dirty rects globalaux
                addListRectOrNot(listDirtyRects, listDirtyRectsLifePoint)

            #rafraichissement partiel de l'�cran la plupart du temps.
            #rafraichissement total tous les 256 cycles. Car quand le PC se
            #met en veille et qu'on le r�veille, �a fait un �cran tout noir, qui se d�noircit
            #au fur et � mesure que des personnages le nettoient.
            if counterTotalFlip & 255:

                #Et l� on rafra�chit l'�cran pour tout afficher. Mais on ne rafra�chit
                #que les zones n�cessaires, (les dirty Rect). H�h�, pas folle la guepe.
                #Si en fait la guepe elle est folle. Et en plus c'est un animal de merde.
                pygame.display.update(listDirtyRects)

            else:

                #gros flip global pour tout rafra�chir.
                pygame.display.flip()
                #remise � zero du compteur de gros flip global
                counterTotalFlip = 0

            counterTotalFlip += 1

            #fin de la partie si le h�ros est mort.
            if theHero.currentState == hero.DEAD:
                #on renvoie un tuple d'ihm avec rien dedans. Pour indiquer que le joueur
                #n'a pas exprim� l'intention de quitter la partie ou le jeu. Il est juste mort.
                return (IHMSG_VOID, nbrErreur)

