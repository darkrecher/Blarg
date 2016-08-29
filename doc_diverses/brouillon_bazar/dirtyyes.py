#/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""

Retrouvez ce superbe programmme, ainsi que son équivalent "pas-dirty",
sur mon blog : http://recher.wordpress.com/
(article du 13 juillet 2010)

Ce code est sous licence CC-BY. (Et encore, c'est presque trop bon.)

Les lignes de code ne dépassent jamais 80 caractères
Les lignes de commentaire ne dépassent jamais 100 caractères.
Ouais c'est bizarre. Mais j'avais envie.
"""

import pygame
import pygame.locals

#les alias de la mort
pygl = pygame.locals

#taille de l'écran de jeu.
SCREEN_SIZE_X = 400
SCREEN_SIZE_Y = 300

#aire de jeu. 
SCREEN_RECT = pygame.Rect(0, 0, SCREEN_SIZE_X, SCREEN_SIZE_Y)

SQUARE_MOVEMENT_X = 30

            
def main():
    """
    le programme principal ouech ouech tac tac yo
    """
    
    print "coucou !!! "
    
    # --------- Initialisation de tout le bordel -----------
    
    pygame.init()
    
    screen = pygame.display.set_mode(SCREEN_RECT.size)
    pygame.mouse.set_visible(0)
    
    # ---- code spécial dirty
    #on va foutre tous les sprites à afficher dans ce groupe.
    #Ce groupe est censé gérer les dirty Sprites, et en même temps, ils est censé
    #gérer les différents rectangles de l'aire de jeu qui doivent être rafraîchi.
    allsprites = pygame.sprite.LayeredDirty()
    # ---- fin code spécial dirty
    
    imgBackground = pygame.Surface(SCREEN_RECT.size)
    imgBackground.fill((0, 100, 0))
    imgBackground = imgBackground.convert()
    
    imgSprite = pygame.Surface((50, 50))
    imgSprite.fill((200, 0, 0))
    imgSprite = imgSprite.convert()
    
    #Ariel Dombasle : un cercle est un carré, un carré est un cercle
    
    # ---- code spécial dirty
    #On crée un dirtySprite, ça veut dire qu'il va pas forcément se réafficher à chaque cycle.
    spriteCarreRouge = pygame.sprite.DirtySprite()
    #Sauf qu'en fait si, il va se réafficher à chaque cycle. C'est ce que ça fait quand on met dirty à 2
    #Le but c'est d'avoir un fonctionnement le plus proche du "pas-dirty".
    spriteCarreRouge.dirty = 2    
    # ---- fin code spécial dirty
    spriteCarreRouge.image = imgSprite
    spriteCarreRouge.rect = pygame.Rect(10, 100, 0, 0)
    allsprites.add(spriteCarreRouge)
    
    #défintion d'attributs à l'arrache.
    spriteCarreRouge.counter = 7
    spriteCarreRouge.MoveX = SQUARE_MOVEMENT_X
    
    #On balance l'image de fond sur l'écran.
    screen.blit(imgBackground, (0, 0))
    #gros flip global pour rafraîchir tout l'écran.
    pygame.display.flip()

    # ------- Les objets du jeu --------
    
    #Ca c'est le putain d'objet qui permet de maîtriser le temps !!! 
    #Talaaaa, je suis le maître du temps. et des frames par secondes aussi.
    clock = pygame.time.Clock()
    
    # ---------- Mega grosse boucle du jeu ----------
    
    while 1:
    
        #Donc là si tout se passe bien le jeu va s'auto-ralentir pour atteindre 
        #le nombre de FPS spécifié par rapport au nombre de fois qu'il fait
        #cette boucle. Et si c'est trop lent, il s'auto-ralentit pas, mais c'est la merde.
        clock.tick(4)
        
        #mouvement du sprite, géré à l'arrache.
        if spriteCarreRouge.counter & 15 > 8:
            
            spriteCarreRouge.rect.move_ip(spriteCarreRouge.MoveX, 0)
            
            if spriteCarreRouge.rect.right > SCREEN_SIZE_X:
                spriteCarreRouge.MoveX = -SQUARE_MOVEMENT_X
           
            if spriteCarreRouge.rect.left < 0:
                spriteCarreRouge.MoveX = SQUARE_MOVEMENT_X

        #compteur, géré à l'arrache aussi.
        spriteCarreRouge.counter += 1
        spriteCarreRouge.counter &= 15
        
        #on efface tous les sprites existants, en redessinant dessus la surface imgBackground
        allsprites.clear(screen, imgBackground)
        
        #terminage du programme si le joueur appuie sur le fermage de fenêtre.
        for event in pygame.event.get():
            if event.type == pygl.QUIT:
                return
        
        #ne sert à rien, mais on sait jamais.
        allsprites.update()
        
        listRectToRepaint = allsprites.draw(screen)
        # ---- code spécial dirty
        print "mode dirty. liste des rect a repeinturer : ", listRectToRepaint
        # ---- fin code spécial dirty
        
        pygame.display.update(listRectToRepaint)
        # ---- spécial dirty : si on réaffiche tout à chaque fois, ça ne fait pas le bug ----
        #pygame.display.update()

        
# --- programme principal ---

#ça c'est fait.    
main()

#Et paf. 
pygame.quit()