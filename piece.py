import pygame
from pygame.locals import *
from game_utils import *

import random

path_image = "assets/sprite/"
BLUE   = (146, 179, 255)

'''
Represents a single Piece on the Board,
serves as an abstract class
'''
class Piece():

    topleft = (225, 25)
    space = 2

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.points = 20

    def set_value(self, value):
        self.value = value
    
    def get_value(self):
        return self.value

    # Returns the part position
    def get_pos(self):
        return (self.x, self.y)
    
    def get_piece(self):

        # Pygame needs to be initialized
        if pygame.get_init():
            return (self.image, self.rect)
        else:
            return (None, None)
    
    # Update element rect
    def update_rect(self):

        if pygame.get_init():

            self.rect.topleft = self.topleft
            self.rect.left += self.x * (self.space + self.rect.width)
            self.rect.top  += self.y * (self.space + self.rect.height)

'''
Represents an area where you cannot have elements
'''
class Block(Piece):
    
    sprite = path_image + \
        "pieces/block/0.png"

    def __init__(self, x,y):
        Piece.__init__(self, x,y)

        if pygame.get_init():
            self.image, self.rect = load_image(
                self.sprite, -1)
        
        self.update_rect()

'''
Represents an Objective tile that needs to be
withdrawn from the field
'''
class Objective(Piece):

    sprite = path_image + \
        "pieces/objective/0.png"

    def __init__(self, x,y):
        Piece.__init__(self, x, y)
        
        if pygame.get_init():

            self.image, self.rect = load_image(
                self.sprite, -1)
        
        self.update_rect()
        self.points = 10000

'''
Represents the simplest piece in the field, before it
has any upgrade
'''
class Simple(Objective):

    # set of images
    sprites = [
        "%s%d.png" % (path_image + "pieces/simple/", i) \
            for i in range(6)
    ]

    def __init__(self, x, y, n):

        # initialize the element
        Objective.__init__(self, x, y)
        self.type = random.randint(0,n-1)

        if pygame.get_init():

            self.image, self.rect = load_image(
                self.sprites[self.type], -1)

        self.points = 0
        self.update_rect()

'''
Represents the simplest piece in the field with a
blue protection that needs to be broken
'''
class Protection(Simple):

    def __init__(self, x, y, n):

        Simple.__init__(self, x, y, n)

        if pygame.get_init():
        
            self.image, self.rect = load_image(
                self.sprites[self.type], -1)
            
            # Draw the transparent square
            s = pygame.Surface(self.rect.size)
            s.fill(BLUE)
            s.blit(self.image, (self.rect.left, self.rect.top))
            self.image = s

        self.update_rect()
        self.points = 1000


    pass

'''
Represents a striped piece, which has
the ability to eliminate an entire row or column,
depending on the movement of the piece
'''
class Stripped(Simple):

    sprites = [
        "%s%d.png" % (path_image + "pieces/stripped/", i) \
            for i in range(6)
    ]

    def __init__(self, x, y, t):
        Simple.__init__(self, x, y, 1)
        self.type = t

        if pygame.get_init():

            self.image, self.rect = load_image(
                self.sprites[self.type], -1)

        self.update_rect()
        self.points = 3000

'''
Represents a piece of special element, which has
the ability to eliminate the 8 pieces around itself.
'''
class Wrapped(Simple):

    sprites = [
        "%s%d.png" % (path_image + "pieces/wrapped/", i) \
            for i in range(6)
    ]

    def __init__(self, x, y, t):
        Simple.__init__(self, x, y, 1)
        self.type = t

        if pygame.get_init():

            self.image, self.rect = load_image(
                self.sprites[self.type], -1)

        self.update_rect()
        self.points = 6000
        pass

'''
Represents a bomb, which has
the ability to eliminate all pieces of
same color from the field.
'''
class Bomb(Simple):

    sprite = path_image + 'pieces/bomb/0.png'

    def __init__(self, x, y):
        Simple.__init__(self, x, y, 1)

        if pygame.get_init():

            self.image, self.rect = load_image(
                self.sprite, -1)

        
        self.type = -1
        self.update_rect()
        self.points = 10000
        pass