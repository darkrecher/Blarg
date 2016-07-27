#/usr/bin/env python
# -*- coding: utf-8 -*-
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

date de la dernière relecture-commentage : 17/02/2011

fichier qui gère une partie du jeu. (une partie dans le sens "je joue une partie")
putain de langue française.
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


#identifiants des dictionnaires d'images, à transmettre aux classes correspondantes
(DIC_IMG_HEROBODY,    #corps du héros
 DIC_IMG_HEROHEAD,    #tête du héros
 DIC_IMG_MAGICIAN,    #magicien
 DIC_IMG_AMMOVIEWER,  #AmmoViewer (classe affichant les cartouches, à gauche)
 DIC_IMG_LIFEPOINT,   #LifePointViewer (classe affichant les points de vie)
) = range(5)

#fichier contenant la superbe image de fond moche du jeu.
IMG_BG_GAME_FILENAME = "bggame.png"


#mapping de touche par défaut. Pour le héros.
# - clé : identifiant d'une touche. C'est pas le code de la touche du clavier.
#         C'est mon identifiant interne à moi tout seul.
# - valeur : tuple de 2 elements
#    * identifiant du stimuli à envoyer au héros.
#    * sous-tuple. liste de paramètres à envoyer en même temps que le stimuli.
#                  ça ne sers que pour le stimuli de mouvement, pour indiquer
#                  les coorodnnées X,Y de déplacement à appliquer au héros.
DIC_KEY_STIM_INFO_MAPPING = {
    KEY_DIR_UP     : (STIMULI_HERO_MOVE,   (pyRect( 0,      -SPEED), ) ),
    KEY_DIR_DOWN   : (STIMULI_HERO_MOVE,   (pyRect( 0,      +SPEED), ) ),
    KEY_DIR_RIGHT  : (STIMULI_HERO_MOVE,   (pyRect(+SPEED,  0),      ) ),
    KEY_DIR_LEFT   : (STIMULI_HERO_MOVE,   (pyRect(-SPEED,  0),      ) ),
    KEY_FIRE       : (STIMULI_HERO_FIRE,   (), ),
    KEY_RELOAD     : (STIMULI_HERO_RELOAD, (), ),
}

#position du bord haut-droit du label affichant le score.
#le score est écrit avec le texte aligné à droite, sur ce bord droit.
POS_LABEL_SCORE = pyRect(GAME_INFO_LIMIT_X-5, 2)



class Game():
    """
    classe qui gère tout le jeu.
    """

    def __init__(self, screen, scoreManager, fontScore):
        """
        constructeur. (thx captain obvious)

        entrée :
            screen : Surface principale de l'écran, sur laquelle s'affiche le jeu.
            scoreManager : classe gérant le score, les hiscores, etc...
            fontScore : police de caractères utilisée pour afficher le score
        """
        self.screen = screen
        self.scoreManager = scoreManager
        self.fontScore = fontScore


    def loadGameStuff(self):
        """
        chargement de tous le bazar nécessaire au jeu. Sprites, images, ...
        """

        #Chargement des images et rangement dans des dictionnaires et dans les
        #classes qui vont bien.

        #ce dictionnaire va contenir les dictionnaires d'images.
        # - clé : identifiant du dictionnaire d'image (DIC_IMG_XXX)
        # - valeur : un dictionnaire dicImg, avec :
        #             - clé : un identifiant d'image
        #             - valeur : une surface contenant l'image.
        #ces dicImg doivent être chargés avec la fonction loadImgInDict.
        self.dicImg = {}

        #liste de tuple de 2 elem, avec :
        # - identifiant du dictionnaire d'image (DIC_IMG_XXX)
        # - sous-sous-tuple, contenant les paramètres à fournir à la fonction loadImgInDict,
        #   pour charger ces images. Voir common.loadImgInDict pour avoir le détail (à la gorgée)
        PARAM_FOR_LOADING_THE_DIC_IMG = (

            (DIC_IMG_HEROBODY,   (herobody.LIST_IMG_FILE_SHORT_NAME,
                                  herobody.IMG_FILENAME_PREFIX)),

            (DIC_IMG_HEROHEAD,   (herohead.LIST_IMG_FILE_SHORT_NAME,
                                  herohead.IMG_FILENAME_PREFIX)),

            (DIC_IMG_MAGICIAN,   (magician.LIST_IMG_FILE_SHORT_NAME,
                                  magician.IMG_FILENAME_PREFIX)),

            #pour çui là, on est obligé de spécifier explicitement la couleur transparente (black)
            #car elle n'est pas dans le coin supérieur gauche de l'écran pour certaines images.
            (DIC_IMG_AMMOVIEWER, (ammoview.LIST_IMG_FILE_SHORT_NAME,
                                  ammoview.IMG_FILENAME_PREFIX, COLOR_BLACK)),

            #pas de préfixe de nom de fichier pour ce dico là.
            (DIC_IMG_LIFEPOINT,  (lifeview.LIST_VESTEJEAN_IMG_FILENAME, )),

        )

        #chargement de tous les dictionnaires d'images, et rangement dans le gros
        #dictionnaire principale self.dicImg.
        for dicImgKey, dicImgLoadParam in PARAM_FOR_LOADING_THE_DIC_IMG:
            self.dicImg[dicImgKey] = loadImgInDict(*dicImgLoadParam)

        #j'ai trippé sur ce dictionnaire de dictionnaire, juste pour factoriser les appels
        #à loadImgInDict. Oui je suis débile et j'aime ça.

        #chargement de la grande image du background du jeu (herbe, mur, etc.)
        self.imgBackground = loadImg(IMG_BG_GAME_FILENAME, None)

        #il faut compléter le dictionnaire contenant les images de la tête du héros.
        #on doit créer la tête regardant à gauche à partir de la tête regardant à droite.
        herohead.preRenderFlippedHeadLeftRight(self.dicImg[DIC_IMG_HEROHEAD])

        #récupération, dans le dictionnaire de dictionnaire machin,
        #d'une référence vers l'image du magicien dans son état normal.
        imgMagiNormal = self.dicImg[DIC_IMG_MAGICIAN][magician.IMG_NORMAL]
        #on a besoin de cette image de magicien lorsqu'on doit charger toutes les
        #images des SimpleSprite. Elle est nécessaire pour le SimpleSprite de MagDyingRotate
        #(le magicien qui meurt en tournoyant et en volant dans les airs youhouuuu)
        self.dicImgInfoSpriteSimple = loadAllSprSimpleImgInfo(imgMagiNormal)


    def isMagicianActive(self, magicianGenerator,
                         groupMagicianAppearing, groupMagician):
        """
        indique si y'a encore des magiciens actifs. Les magiciens actifs sont les trucs suivants :
         - des magiciens pas encore créés, mais en réserve dans des genPattern
         - des magiciens en train d'apparaître
         - des magiciens vivants, et qui sont toujours en mouvement
             (donc soit des magiRand, soit des magiLine qui sont pas arrivés à destination.)

        et donc par conséquent, les magiciens inactifs sont les suivants :
         - ceux qui sont morts, ou en train de crever ou en train d'exploser.
         - les magiLine qui sont arrivés à destination.

        entrée :
            magicianGenerator : classe éponyme, permet de générer les waves de magiciens
            groupMagicianAppearing : groupe de sprite contenant les magiciens en train
                                     de faire leur anim d'apparition.
            groupMagician : groupe de sprite contenant tous les autres magiciens.

        j'ai besoin de tous ces paramètres en entrée car ils ne sont pas stockés comme attribut,
        dans la classe elle-même. Et j'ai pas envie de les stocker, comme ça, je suis sûr qu'entre
        deux parties, je refabrique tout et je repars complètement à neuf. (Les seuls trucs
        que je stocke, c'est les images, les sons, et la configs,
        car ils viennent de fichier de données.

        plat-dessert :
            boolean. True : il y a encore des magiciens actifs. False : Il n'y en a plus.
        """

        #on vérifie si il reste des magiciens pas encore créés, en réserve dans des genPattern
        if len(magicianGenerator.listGenPattern) > 0:
            return True

        #on vérifie si il reste des magiciens en train d'apparaître
        if len(groupMagicianAppearing) > 0:
            return True

        #on vérifie si il reste des magiciens vivants.

        activStates = (magician.ALIVE, magician.HURT)

        for magi in groupMagician:
            if magi.currentState in activStates and not magi.isMoveFinished():
                return True

        #on n'a trouvé aucun magicien actif.
        return False


    def buildDicKeyCodeStimInfo(self, dicKeyCodeMapping):
        """
        construit le dicKeyCodeStimInfo. Dictionnaire contenant le mapping de touche
        réellement utilisé pour jouer cette partie.

        Bon, je m'explique, parce que c'est le bordel.

        idKey : mon identifiant de touche interne. C'est à dire :
                KEY_DIR_UP, KEY_DIR_DOWN, KEY_DIR_RIGHT, KEY_DIR_LEFT, KEY_FIRE, KEY_RELOAD.

        realKeyCode : int. Code de la touche envoyé par le clavier quand le joueur appuie dessus.

        stimuliInfo : tuple. Info de stimuli à envoyer au héros. C'est à dire :
                      STIMULI_HERO_MOVE + les coordonnées, STIMULI_HERO_FIRE, STIMULI_HERO_RELOAD

        entrées :
            dicKeyCodeMapping. dico de correspondance : idKey -> realKeyCode
            (ce dico dépend de la config définie par le joueur)

        ce fichier de code contient :
            DIC_KEY_STIM_INFO_MAPPING. dico de correspondance : idKey -> stimuliInfo
            (ce dico est une constante)

        plat-dessert :
            définition de self.dicKeyCodeStimInfo.
            dico de correspondance : realKeyCode -> StimuliInfo
        """
        self.dicKeyCodeStimInfo = {}

        #il faut avoir autant de clés dans DIC_KEY_STIM_INFO_MAPPING que dans dicKeyCodeMapping,
        #sinon, on va paumer des trucs en chemins, ou ça va planter.
        #Mais je suis fort, et je sais que j'ai pas besoin de vérifier ça.

        for idKey, keyCodeInfo in dicKeyCodeMapping.items():
            #bon, y'a pas une correspondance directe idKey -> realKeyCode.
            #En vrai c'est : idKey -> (realKeyCode, <truc à la con>).
            realKeyCode = keyCodeInfo[0]
            stimuliInfo = DIC_KEY_STIM_INFO_MAPPING[idKey]
            self.dicKeyCodeStimInfo[realKeyCode] = stimuliInfo


    def playOneGame(self, dicKeyCodeMapping, dogDom):
        """
        fonction pour jouer une partie.
        la partie s'arrête quand le joueur a appuyé sur Echap,
        ou si un événement "quit" (alt-F4, fermage de fenêtre) est reçu,
        ou si le héros perd toutes ses vies.

        entréees:
         - dicKeyCodeMapping : voir fonction buildDicKeyCodeStimInfo de ce fichier
         - dogDom : boolean. Indique si le héros perd des vies ou pas.

        plat-dessert : tuple de 2 elem :

         - sous-tuple ihmsgInfo. Il peut contenir les valeurs suivantes :
             * IHMSG_QUIT et IHMSG_TOTALQUIT : le joueur veut quitter le jeu. (Alt-F4, ou autre)
             * IHMSG_QUIT : le joueur veut juste quitter la partie (il a appuyé sur Esc)
             * tuple vide : le joueur voulait pas quitter la partie, mais bon, on l'a quand
                            même fait quitter parce qu'il est mort, mmmm'voyez.

         - nbrErreur. int : nombre d'erreur qui ont eu lieu durant le jeu.
           dans l'état actuel des choses, je vois pas d'erreurs possibles. Haha.

        pré-conditions :
          - le self.scoreManager référencé par cette classe, doit avoir été configuré
            pour qu'il contienne le nom et les stats du joueur sélectionné.
          - et faut avoir exécuté loadGameStuff, evidemment.
        """
        nbrErreur = 0

        # --- initialisation des trucs ---

        self.buildDicKeyCodeStimInfo(dicKeyCodeMapping)

        #initialisation des scores pour cette partie (pas les stats, les scores)
        self.scoreManager.initCurrentGameData()

        #on va foutre tous les sprites à afficher dans le groupe allSprites.
        #y'aura d'autres group de sprites, mais ce sera que pour la gestion, pas l'affichage.
        #Du coup, pas de gestion de quel sprite est devant ou derrière. osef. pas besoin.
        allSprites = pygame.sprite.RenderUpdates()

        #classes pour gérer les simpleSprites
        spriteSimpleManager = SpriteSimpleManager(allSprites)
        param = (spriteSimpleManager, self.dicImgInfoSpriteSimple)
        spriteSimpleGenerator = SpriteSimpleGenerator(*param)

        #Ca c'est le putain d'objet qui permet de maîtriser le temps !!!
        #Talaaaa, je suis le maître du temps. et des frames par secondes aussi.
        clock = pygame.time.Clock()

        #création du label affichant le score, en l'initialisant avec la valeur de départ : 0
        score = self.scoreManager.currentScore

        lblScore = lamoche.Lamoche(POS_LABEL_SCORE, self.fontScore,
                                   str(score), alignX=lamoche.ALIGN_RIGHT)

        allSprites.add(lblScore)

        #groupe de sprite qui va contenir tous les magiciens.
        groupMagician = pygame.sprite.Group()
        #groupe de sprite qui va contenir tous les magiciens faisant leur anim d'apparition.
        groupMagicianAppearing = pygame.sprite.Group()

        #objet gérant les collisions entre les bullets tirés par le héros et les magiciens
        collHandlerBulletMagi = CollHandlerBulletMagi(groupMagician)
        #objet gérant les collisions entre le héros et les magiciens.
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

        #ajout des sprites composant le héro, dans le groupe allSprites
        allSprites.add(theHero.heroBody)
        allSprites.add(theHero.heroHead)

        #création du magician Generator. Classe qui génère les waves successives de magiciens.
        param = (groupMagicianAppearing, self.dicImg[DIC_IMG_MAGICIAN],
                 spriteSimpleGenerator, theHero)

        magicianGenerator = maggen.MagicianGenerator(*param)

        # --- affichage inital des éléments ---

        #on remplit le screen tout en noir. (juste après on mettra l'image de fond,
        #mais on n'est pas sûr qu'elle remplisse tout l'écran : donc paf.)
        self.screen.fill(COLOR_BLACK)
        #Maintenant on balance l'image de fond sur l'écran.
        self.screen.blit(self.imgBackground, (0, 0))

        #on affiche initialement tous les points de vie (vestes en jean)
        lifePointViewer.groupLifePoints.draw(self.screen)

        #pas la peine d'afficher toutes les cartouches, ça se fait tout seul, le AmmoViewer
        #les fait apparaître une par une vachement vite, et je trouve ça cool.

        #pas la peine d'afficher le score. Ca va se faire tout seul dès le premier cycle,
        #avec le scoreManager.scoreChanged qui s'init à True lors d'une nouvelle partie.

        #les autres trucs (heros, magiciens, ...) sont systématiquement réaffichés à chaque cycle,
        #donc pas la peine de s'en soucier ici.

        #(c'est quand même bizarre que ce soit pas géré au même niveau pour tous les objets, cette
        #histoire d'affichagee initial.)

        #gros flip global pour tout rafraîchir.
        pygame.display.flip()

        #compteur pour effectuer un rafraîchissement total de l'écran tous les X cycles.
        #si je fais pas ça, ça fait un rafraichissement progressif très moche lorsque
        #l'ordi s'est mis en veille pendant une partie.
        counterTotalFlip = 0

        # ---------- Mega grosse boucle du jeu ----------

        while 1: #ça, c'est la classe, déjà pour commencer.

            #Donc là si tout se passe bien le jeu va s'auto-ralentir pour atteindre
            #le nombre de FPS spécifié par rapport au nombre de fois qu'il fait
            #cette boucle. Et si c'est trop lent, il s'auto-ralentit pas, mais c'est la merde.
            clock.tick(FRAME_PER_SECOND)

            #les sprites de l'ammoViewer ( = BulletShell = cartouches )
            #ils ne changent pas forcément. Donc on commence par déterminer si y'aura
            #un changement. Si oui, il faudra les clearer et les réafficher,
            #comme des sprites normaux qui changent tout le temps.
            mustUpdateAmmoViewer = ammoViewer.determineIsUpdatingSthg()
            #pareil, mais pour les points de vie
            #nom trop long de merde
            mustUpdatLife = lifePointViewer.determineIsUpdatingSthg()
            mustUpdateLifePointViewer = mustUpdatLife

            #on efface tous les sprites existants, en redessinant dessus la surface imgBackground
            allSprites.clear(self.screen, self.imgBackground)

            #même chose pour les sprites de l'ammoViewer, mais seulement si c'est nécessaire
            if mustUpdateAmmoViewer:
                param = (self.screen, self.imgBackground)
                ammoViewer.groupBulShell.clear(*param)

            #même même chose. Bon, faudra peut être réfléchir à de la factorisation. ou pas.
            if mustUpdateLifePointViewer:
                param = (self.screen, self.imgBackground)
                lifePointViewer.groupLifePoints.clear(*param)

            #Récup et gestion des events (y'a presque rien. Les events des touches viennent après.
            for event in pygame.event.get():
                #on quitte la partie si le joueur fait un événement de quittage (alt-F4, ...)
                #et il faudra carrément quitter le programme.
                if event.type == pygl.QUIT:
                    #on indique dans les params de retour qu'il faut quitter tout le jeu)
                    return ((IHMSG_QUIT, IHMSG_TOTALQUIT), nbrErreur)

            #on récupère un gros dictionnaire contenant toute les touches,
            #avec des booléens indiquant si elles sont appuyées ou pas.
            dictKeyPressed = pygame.key.get_pressed()

            #prises en compte des commandes du jeu-lui-même, selon les touches appuyées.
            #C'est rigolo d'écrire "machin-lui-même", ça me fait penser quand j'organisais
            #le congrès industriel. J'ai vraiment servi à rien sur ce truc.

            #on quitte la partie si le joueur a appuyé sur Echap. Mais on quittera pas le prog
            if dictKeyPressed[pygl.K_ESCAPE]:
                #on indique dans les params de retour qu'il faut juste quitter la partie.
                return ((IHMSG_QUIT, ), nbrErreur)

            #prises en compte des commandes liées au héros, selon les touches appuyées.
            #(le joueur ne peut plus faire bouger/tirer/recharger le héros si il crève)
            if theHero.currentState not in (hero.DYING, hero.DEAD):

                for key, stimuliInfo in self.dicKeyCodeStimInfo.items():
                    if dictKeyPressed[key] :
                        #l'une des touches correspondant à un stimuli à envoyer au héros
                        #a été appuyée. on récupère dans le dico de mapping l'identifiant du
                        #stimuli, et les paramètres. Et on balance tout ça au héros.
                        stimuliId, stimuliParam = stimuliInfo
                        theHero.takeStimuliGeneric(stimuliId, stimuliParam)

            #si on a enregistré des mouvements à faire pour le héros, on les effectue
            theHero.makeBufferMove()

            #on fait avancer la machine à état du héros. (il recharge, il réarme, ...)
            theHero.advanceStateOneStep()

            #update du générateur de wave de magicien.
            magicianGenerator.update()

            #update de tous les sprites de magiciens en train de faire leurs anim d'apparition
            groupMagicianAppearing.update()

            #on récupère la liste de tous les magiciens ayant fini leur anim d'apparition.
            listMagiToTransfer = [ magi for magi in groupMagicianAppearing
                                   if magi.currentState == magician.ALIVE ]

            #il faut transférer ces magiciens de groupMagicianAppearing vers groupMagician,
            #pour qu'ils puissent vivre leur vie. (oh oui !)
            for magicianToTransfer in listMagiToTransfer:
                groupMagicianAppearing.remove(magicianToTransfer)
                groupMagician.add(magicianToTransfer)
                #il faut l'ajouter dans allSprites. En fait, quand le sprite
                #de magicien est "appearing", il ne s'affiche pas par lui-même.
                #Il contient un SimpleSprite qui s'affiche et se gère tout seul
                #avec le SpriteSimpleManager. Quand le magicien a fini son anim d'appearing,
                #il doit s'afficher, comme les autres. On le balance alors dans allSprites.
                #Putain c'est le bordel. Faudra simplifier ça un jour.
                allSprites.add(magicianToTransfer)

            #lancement de l'update sur chaque magicien.
            #on fait d'abord l'update, et plus tard on fera les remove. Ca évite de se trimbaler
            #pendant un cycle supplémentaire des magiciens qui servent à rien. (ah bon ?)
            groupMagician.update()

            #on regarde si il y a encore des magiciens actifs dans le jeu.
            #Si y'en a plus, faut avertir le générateur de waves de magicien.
            #Il a besoin de connaître cet info, pour passer directement à la wave suivante,
            #calculer les bonus, etc...
            param = (magicianGenerator, groupMagicianAppearing, groupMagician)

            if not self.isMagicianActive(*param):
                magicianGenerator.takeStimuliNoMoreActiveMagi()

            #lancement de l'update sur les SimpleSprite, et supression de ceux
            #qui servent plus à rien.
            spriteSimpleManager.updateAndRemoveSprites()

            #update de la tronche du héros. (gestion du smiling)
            theHero.heroHead.update()

            #update de l'ammoViewer, si nécessaire.
            if mustUpdateAmmoViewer:
                ammoViewer.updateAmmoViewer()

            #même chose pour lifePointViewer.
            if mustUpdateLifePointViewer:
                lifePointViewer.update()

            #supression des magiciens crevés. je préfère le faire en deux étapes.
            #D'abord on construit la liste des magiciens à supprimer,
            #puis on les supprime des deux groups de sprites.
            #(celui pour l'affichage, et celui pour la gestion spécifique des magiciens)
            #je veux pas parcourir les elements du groupe et les virer en même temps,
            #c'est un peu dangereux, et bizarre.
            listMagicianToRemove = [ magi for magi in groupMagician
                                     if magi.currentState == magician.DEAD ]

            for magicianToRemove in listMagicianToRemove:
                groupMagician.remove(magicianToRemove)
                allSprites.remove(magicianToRemove)

            #tests de collision entre le héros et les magiciens. Si y'en a, le héro a mal.
            #Et faudra lui enlever un point de vie. (le collisionHandler gère ça tout seul)
            collHandlerHeroMagi.testCollisionHeroMagi(theHero)

            #reaffichage eventuel du score, si il a changé
            if self.scoreManager.scoreChanged:
                #recupération de la nouvelle valeur de score, auprès du scoreManager
                score = self.scoreManager.currentScore
                #transmission de cet valeur au label affichant le score
                lblScore.updateAttrib(text=str(score))
                #indication au scoreManager que c'est bon, on a pris en compte le changement.
                self.scoreManager.scoreChanged = False

            #Redessinage de tous les sprites, bordel. (osef de l'ordre de dessin)
            #on récupère une liste de "dirty Rect". C'est à dire les zones de l'écran
            #qui ont dû être redessinées.
            listDirtyRects = allSprites.draw(self.screen)

            #Redessinage des sprites de l'ammoViewer, si c'est nécessaire.
            if mustUpdateAmmoViewer:
                listDirtyRectsAmmo = ammoViewer.groupBulShell.draw(self.screen)
                #Il faut ajouter les dirty Rects de ce redessinage aux dirty rects
                #du redessinage global.
                addListRectOrNot(listDirtyRects, listDirtyRectsAmmo)

            #même chose. mais pour le LifePointViewer.
            if mustUpdateLifePointViewer:
                #nom à rallonge de merde
                funcDraw = lifePointViewer.groupLifePoints.draw
                listDirtyRectsLifePoint = funcDraw(self.screen)
                #ajout des dirty Rects de ce redessinage aux dirty rects globalaux
                addListRectOrNot(listDirtyRects, listDirtyRectsLifePoint)

            #rafraichissement partiel de l'écran la plupart du temps.
            #rafraichissement total tous les 256 cycles. Car quand le PC se
            #met en veille et qu'on le réveille, ça fait un écran tout noir, qui se dénoircit
            #au fur et à mesure que des personnages le nettoient.
            if counterTotalFlip & 255:

                #Et là on rafraîchit l'écran pour tout afficher. Mais on ne rafraîchit
                #que les zones nécessaires, (les dirty Rect). Héhé, pas folle la guepe.
                #Si en fait la guepe elle est folle. Et en plus c'est un animal de merde.
                pygame.display.update(listDirtyRects)

            else:

                #gros flip global pour tout rafraîchir.
                pygame.display.flip()
                #remise à zero du compteur de gros flip global
                counterTotalFlip = 0

            counterTotalFlip += 1

            #fin de la partie si le héros est mort.
            if theHero.currentState == hero.DEAD:
                #on renvoie un tuple d'ihm avec rien dedans. Pour indiquer que le joueur
                #n'a pas exprimé l'intention de quitter la partie ou le jeu. Il est juste mort.
                return (IHMSG_VOID, nbrErreur)

