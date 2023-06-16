import pygame
import numpy as np
from pygame.locals import *
import os, sys

fonts = {}
fonts['NES'] = 'assets/fonts/AVENGEANCE HEROIC AVENGER AT.otf'


""" Load the image, returning the surface and rect """
def load_image(name, colorkey=None, size=(60,60)):

    try:
        image = pygame.image.load(name)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    
    image = image.convert_alpha()
    image = pygame.transform.scale(image, size)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    
    return image, image.get_rect()

""" Load the sound, returning its Sound Object """
def load_sound(name):

    class NoneSound:
        def play(self): pass
    if not pygame.mixer:
        return NoneSound()
    
    try:
        sound = pygame.mixer.Sound(name)
    except pygame.error as message:
        raise SystemExit(message)
    
    return sound

""" Load a phase from a csv file. """
def load_level(file_csv):

    # Check if the file exists
    if os.path.exists(file_csv):
        file = open(file_csv, "r")
    else:
        print("File '%s' don't Exist!" % file_csv)
        exit()
    
    # Start reading lines
    line = file.readline()

    # Get the information from the fields
    info = [int(x) for x in line.split(',')]

    level = []
    for i in range(9):
        line = file.readline()
        level.append([int(x) for x in line.split(',')])

    return info, level

def load_level_string(string):
    lines = string.split("\n")
    info = [int(x) for x in lines[0].split(',')]

    level = []
    for i in range(1, 10):
        line = lines[i]
        level.append([int(x) for x in line.split(',')])
    
    return info, level