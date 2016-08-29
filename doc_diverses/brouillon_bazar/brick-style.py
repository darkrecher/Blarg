#/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
This simple example is used for the line-by-line tutorial
that comes with pygame. It is based on a 'popular' web banner.
Note there are comments here, but for the full explanation, 
follow along in the tutorial.
"""


#Import Modules
import os, pygame

#moi je fais pas comme l'autre débile. Je nomme les trucs que j'importe. Même si y'en a beaucoup.
#Je fais pas un putain de import * juste parce que : oh lala y'en a trop. Dans ce cas là, on met un *. Mais MERDE !
from pygame.locals import RLEACCEL, QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP

if not pygame.mixer: print 'Warning, sound disabled'


SCREEN_SIZE_X = 400
SCREEN_SIZE_Y = 300


#classes for our game objects
class Raquette(pygame.sprite.Sprite):
    """
    plaf !
    """
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        
        raquetteRect = pygame.Rect(10, SCREEN_SIZE_Y-20, 50, 10)
        
        raquetteImg = pygame.Surface(raquetteRect.size).convert()
        raquetteImg.fill((200, 200, 200))
        
        #self.image, self.rect = load_image('avatar.png', -1)
        self.image = raquetteImg
        self.rect = raquetteRect
        
        self.areaAuthorized = pygame.Rect(0, SCREEN_SIZE_Y-20, SCREEN_SIZE_X, 10)
        
        
    def update(self):
        "move the fist based on the mouse position"
        pos = pygame.mouse.get_pos()
        self.rect.centerx = pos[0]
        self.rect.clamp_ip(self.areaAuthorized)
        

class Ball(pygame.sprite.Sprite):
    """moves a monkey critter across the screen. it can spin the
       monkey when it is punched."""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite intializer
        #self.image, self.rect = load_image('expl2.PNG', -1)
        
        ballRect = pygame.Rect(20, 20, 10, 10)
        ballImg = pygame.Surface(ballRect.size).convert()
        ballImg.fill((255, 255, 255))
        
        self.image = ballImg
        self.rect = ballRect
        self.movement = [3, 3]

        
#        screen = pygame.display.get_surface()
#        self.area = screen.get_rect()
#        self.rect.topleft = 10, 10
#        self.move = 9
#        self.dizzy = 0

    def update(self):
        "walk or spin, depending on the monkeys state"
        #self.rect.move_ip(self.movement[0], self.movement[1])
        self.rect.move_ip( *self.movement )
        
        #à foutre dans une fonction, peut être.
#        if self.rect.bottom > SCREEN_SIZE_Y:
#            self.rect.bottom = SCREEN_SIZE_Y
#            self.movement[1] = -abs(self.movement[1])

        if self.rect.top < 0:
            self.rect.top = 0
            self.movement[1] = abs(self.movement[1])

        if self.rect.right > SCREEN_SIZE_X:
            self.rect.right = SCREEN_SIZE_X
            self.movement[0] = -abs(self.movement[0])

        if self.rect.left < 0:
            self.rect.left = 0
            self.movement[0] = abs(self.movement[0])
            
    def bounceOnRaquette(self, raquetteRect):
        """
        je code en franglais et je vous emmerde !!
        """
        if self.rect.colliderect(raquetteRect):
            self.rect.bottom = raquetteRect.top
            self.movement[1] = -abs(self.movement[1])


def main():
    """
    blablabla
    """
    
#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE_X, SCREEN_SIZE_Y))
    pygame.display.set_caption('Brick-style !!!')
    pygame.mouse.set_visible(0)

#Create The Backgound
    background = pygame.Surface(screen.get_size())

    
    background = background.convert()
    background.fill((10, 10, 10))

#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    clock = pygame.time.Clock()
    ball = Ball()
    raquette = Raquette()
    allsprites = pygame.sprite.RenderPlain((raquette, ball))

    if pygame.font:
        font = pygame.font.Font(None, 36)
        failText = font.render("FAIL !!", 1, (255, 10, 10))
        textpos = failText.get_rect(centerx=background.get_width()/2, centery = 100)
        #background.blit(failText, textpos)

#Main Loop
    while 1:
        clock.tick(60)

    #Handle Input Events
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return
                
        ball.bounceOnRaquette(raquette.rect)
        
        if ball.rect.bottom > SCREEN_SIZE_Y:
            background.blit(failText, textpos)

        allsprites.update()

    #Draw Everything
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__': main()