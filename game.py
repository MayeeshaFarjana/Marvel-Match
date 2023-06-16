import sys, pygame, time, random
import numpy as np
from pygame.locals import *
from os import listdir
from os.path import isfile, join
import copy

import piece
import board
import game_utils

size = width, height = 800, 600

'''
Color Set
'''
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
GREY       = (180, 180, 180)
RED        = (240,  19,  30)
ORANGE     = (255, 139,   0)
YELLOW     = (255, 211,   0)
GREEN      = ( 53, 181,  53)
BLUE       = (  5,  60, 242)
PURPLE     = (191,   0, 255)
IRON       = (120,   0,   0)
PINK       = (255, 202, 213)
CYAN       = (224, 254, 254)
PERIWINKLE = (199, 206, 234)
PALEORANGE = (255, 218, 193)
SALMON     = (255, 154, 162)
MINT       = (181, 234, 215)
LIGHTYELLOW= (255, 255, 216)
WINE       = (198,   4,   4)
CAPBLUE    = ( 38, 110, 246)

'''
elements colors
'''
PIECE_COLORS = [
    ORANGE,
    CAPBLUE,
    PURPLE,
    YELLOW,
    GREEN,
    WINE
]

'''
mode colors
'''
MODE_COLORS = {}
MODE_COLORS['POINTS'] = ORANGE
MODE_COLORS['BLOCKS'] = BLUE
MODE_COLORS['OBJECTIVE'] = GREEN
MODE_COLORS['MIX'] = RED

'''
Tests phase set
'''
TEST_MAPS = [
    "levels/95_95_points_protection_objective.csv",
    "levels/85_85_points_protection_objective.csv",
    "levels/75_75_points_protection_objective.csv"
]


class Game(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.status = 'start' # initial game state
        self.frame = 0 # game frames
        self.color = random.choice(PIECE_COLORS) # screen color
        self.board = None # playing field
        self.pick = None # chosen piece
        self.objective_image = None # object image
        self.level = 0 # Game starting level

    def _pygame_init(self):
        # Initialize Everything
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Marvel Match')
        icon = pygame.image.load('logo.png')
        pygame.display.set_icon(icon)
        pygame.mouse.set_visible(1)

    def play(self):
        
        # Initializes pygame and the interface
        self._pygame_init()

        # Prepare Game Objects
        clock = pygame.time.Clock()
    
        # Main Loop
        going = True
        while going:

            # Guarantees the game's 60 frames
            clock.tick(60)
            
            # Current frame information
            self.frame += 1
            if self.frame > 60:
                self.color = random.choice(PIECE_COLORS)
                self.frame = 0

            # capture events
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT: 
                    going = False
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self._set_start_screen()

            # choosing the state
            if self.status == 'start':
                background = self._start_screen()
            elif self.status == 'game':
                background = self._game_screen()
            elif self.status == 'level':
                background = self._level_screen()

            # painting the canvas
            self.screen.blit(background, (0, 0))
            pygame.display.flip()

        pygame.quit()

        # Game Over
    
    # Adds text with the font on the screen
    def _add_nes_text(self, string, text_size=60, reverse=False, 
            centerx=size[0]/2, centery=size[1]/2, left=None, 
            right=None, top=None, bottom=None):
        
        # order of colors
        colors = [WHITE, BLACK]
        if reverse:
            colors = list(reversed(colors))

        # shadow space
        plus = 2

        texts, pos = [], []
        
        # Initialize the front font
        font_path = 'assets/fonts/AVENGEANCE HEROIC AVENGER AT.otf'
        font_path_two = 'assets/fonts/Snufkin.otf'
        font = pygame.font.Font(font_path, text_size)
        font_two = pygame.font.Font(font_path_two, text_size)

        # Create initial text
        front = font.render(string, 1, colors[0])
        frontpos = front.get_rect(centerx=centerx, centery=centery)

        # If you have left position, update
        if left is not None:
            frontpos.left = left
        
        # If you have right position, update
        if right is not None:
            frontpos.right = right
        
        # If you have top position, update
        if top is not None:
            frontpos.top = top
        
        # If you have bottom position, update
        if bottom is not None:
            frontpos.bottom = bottom

        # create the shadow
        back = font.render(string, 1, colors[1])
        backpos = back.get_rect()
        backpos.right = frontpos.right + plus
        backpos.bottom = frontpos.bottom + plus

        return [back,front], [backpos, frontpos]

    def _add_text(self, string, text_size=60, reverse=False, 
            centerx=size[0]/2, centery=size[1]/2, left=None, 
            right=None, top=None, bottom=None):
        
        # order of colors
        colors = [WHITE, BLACK]
        if reverse:
            colors = list(reversed(colors))

        # shadow space
        plus = 2

        texts, pos = [], []
        
        # Initialize the front font
        font_path_two = 'assets/fonts/Snufkin.otf'
        font_two = pygame.font.Font(font_path_two, text_size)

        # Create initial text
        front = font_two.render(string, 1, colors[0])
        frontpos = front.get_rect(centerx=centerx, centery=centery)

        # If you have left position, update
        if left is not None:
            frontpos.left = left
        
        # If you have right position, update
        if right is not None:
            frontpos.right = right
        
        # If you have top position, update
        if top is not None:
            frontpos.top = top
        
        # If you have bottom position, update
        if bottom is not None:
            frontpos.bottom = bottom

        # create the shadow
        back = font_two.render(string, 1, colors[1])
        backpos = back.get_rect()
        backpos.right = frontpos.right + plus
        backpos.bottom = frontpos.bottom + plus

        return [back,front], [backpos, frontpos]

    def _add_text_pix(self, string, text_size=60, reverse=False, 
            centerx=size[0]/2, centery=size[1]/2, left=None, 
            right=None, top=None, bottom=None):
        
        # order of colors
        colors = [WHITE, BLACK]
        if reverse:
            colors = list(reversed(colors))

        # shadow space
        plus = 2

        texts, pos = [], []
        
        # Initialize the front font
        font_path_three = 'assets/fonts/pixel_nes.otf'
        font_three = pygame.font.Font(font_path_three, text_size)

        # Create initial text
        front = font_three.render(string, 1, colors[0])
        frontpos = front.get_rect(centerx=centerx, centery=centery)

        # If you have left position, update
        if left is not None:
            frontpos.left = left
        
        # If you have right position, update
        if right is not None:
            frontpos.right = right
        
        # If you have top position, update
        if top is not None:
            frontpos.top = top
        
        # If you have bottom position, update
        if bottom is not None:
            frontpos.bottom = bottom

        # Create a shadow
        back = font_three.render(string, 1, colors[1])
        backpos = back.get_rect()
        backpos.right = frontpos.right + plus
        backpos.bottom = frontpos.bottom + plus

        return [back,front], [backpos, frontpos]

    # Initialize the icon image
    def _get_objective_image(self):
        
        if self.objective_image is None:
            self.objective_image = game_utils.load_image(
                "assets/sprite/pieces/objective/0.png",
                size=(35,35)
            )

    # Get a random level from the levels folder
    def _pick_a_level(self):
        mypath = "levels/"
        onlyfiles = [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]
        onlyfiles.append(None)

        return random.choice(onlyfiles)

    # Initialize necessary information for Game_Screen
    def _set_game_screen(self):
        self.status = 'game'
        self.board = board.Board(file=TEST_MAPS[self.level])
        self._get_objective_image()
        self.blocks = self.board.blocks
        self.objectives = self.board.canes
        self.round_info = None
        self.timer = 0 # Round messages time
        self.end = False # Check if it's game over
        self.win = False # Check if you have won the game

    # Initializes the information needed for Start Screen
    def _set_start_screen(self):
        self.status = 'start'

    def _set_level_screen(self):
        self.status = 'level'

    # Works all home screen operations
    def _start_screen(self):
        
        # Home screen event capture
        for event in self.events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self._set_level_screen()

        # Create the background
        background = pygame.Surface(self.screen.get_size())
        background = background.convert()
        background.fill(self.color)

        # Puts the letters on the screen with shading
        if pygame.font:
            
            texts, textpos = self._add_nes_text("mArvel mAtch", text_size=80)
            background.blit(texts[0], textpos[0])
            background.blit(texts[1], textpos[1])


            # CLICK WITH THE MOUSE!
            if self.frame % 60 <= 30:
                texts, textpos = self._add_nes_text(
                    "Avengers, Assemble!",
                    centery= size[1] - 30,
                    text_size=40)
                background.blit(texts[0], textpos[0])
                background.blit(texts[1], textpos[1])

        return background

    def _level_screen(self):

        # Create the background
        background = pygame.Surface(self.screen.get_size())
        background = background.convert()
        background.fill(RED)

        levels = []

        # Puts the letters on the screen with shading
        if pygame.font:
            
            # SELECT LEVEL
            texts, textpos = self._add_nes_text(
                "flAme on!",
                text_size=60,
                top=10)
            background.blit(texts[0], textpos[0])
            background.blit(texts[1], textpos[1])
            

            # Add all words
            for i in [1, 2, 3]:
                string = "level %d" % i

                i -= 2

                # LEVEL i
                texts, textpos = self._add_nes_text(
                    string,
                    text_size=50,
                    top=size[1]/2 + i*80)
                background.blit(texts[0], textpos[0])
                background.blit(texts[1], textpos[1])

                rect = copy.deepcopy(textpos[0])
                rect.width += 15
                rect.height -= 15

                rect.topleft = textpos[0].topleft
                rect.left -= 10
                rect.top += 10

                levels.append(textpos[0])

        # Home screen event capture
        for event in self.events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                
                # mouse position
                pos = pygame.mouse.get_pos()

                # Cycles through all the tiles in the field
                find = False
                for i, l in enumerate(levels):
                    
                    # Check for collision
                    if l.collidepoint(pos):
                        self.level = i
                        find = True
                        break
                
                # If you can't find it, remove the element
                if find:
                    self._set_game_screen()

        return background

    # Draw a square around the part position
    def _draw_square(self, background, piece, color=BLACK, width=3):

        # Take the size of the square
        l = piece.rect.left -width
        t = piece.rect.top -width
        w = piece.rect.width +width
        h = piece.rect.height +width

        # draw the square
        pygame.draw.rect(
            background,
            color,
            (l, t, w, h),
            width)
        
        return background

    # Checks if the selected part is valid
    def _check_picked_piece(self, p):

        # If you clicked on a block, it returns nothing
        if type(p) is piece.Block or type(p) is piece.Objective:
            return None

        # If you didn't choose one,
        # return to play
        if self.pick is None:
                return p
        
        # Get the position of the two pieces
        x = abs(self.pick.x - p.x)
        y = abs(self.pick.y - p.y)

        # If the distance between the two is greater,
        # invalid position
        if x > 1 or y > 1:
            return None
        
        # Take the possibility to click on it or
        # click diagonally
        if x == y:
            return None
        
        # test the movement
        self.round_info = self.board.test_move(p, self.pick)

        # Returns no part selects
        return None

    # Returns the amount of game points
    def _get_points(self):

        value = str(self.board.points)
        value = ''.join(reversed(value))

        size = len(value)
        for i in range(size, 9):
            value += '0'

        number = ''
        for i, c in enumerate(value):
            number += c
            if i % 3 == 2:
                number += '.'

        if number[-1] == '.':
            number = number[:-1]

        number = ''.join(reversed(number))
        return number

    # Print game mode on screen
    def _print_game_mode(self, background):
        
        # Box where the game mode is
        pygame.draw.rect(
            background,
            WHITE,
            (15, 25, 190, 90),
        )
        
        # Box where the game mode is
        pygame.draw.rect(
            background,
            BLACK,
            (15, 25, 190, 90),
            10
        )

        texts, pos = self._add_nes_text(
            "gAme mode",
            text_size=25,
            reverse=True,
            left=55,
            top=35,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)

        pygame.draw.line(
            background, 
            RED, 
            (30, 70), 
            (190, 70), 
            2
        )
        
        texts, pos = self._add_text(
            self.board.mode,
            text_size=25,
            reverse=True,
            centerx=pos[1].centerx,
            top=pos[1].bottom + 10,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)
        
        
    # Score Box
    def _print_game_points(self, background):

        rect = pygame.draw.rect(
            background,
            WHITE,
            (10, 130, 200, 90),
        )

        rect = pygame.draw.rect(
            background,
            BLACK,
            (10, 130, 200, 90),
            10
        )

        texts, pos = self._add_nes_text(
            "score",
            text_size=27,
            reverse=True,
            centerx = rect.centerx,
            top=150,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)

        pygame.draw.line(
            background, 
            RED, 
            (30, 175), 
            (190, 175), 
            2
        )

        texts, pos = self._add_text(
            self._get_points(),
            text_size=24,
            reverse=True,
            right=pos[1].right + 30,
            top=pos[1].bottom+5,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)

    # Moves Box
    def _print_game_moves(self, background):
        
        rect = pygame.draw.rect(
            background,
            WHITE,
            (15, 235, 190, 105),
        )

        rect = pygame.draw.rect(
            background,
            BLACK,
            (15, 235, 190, 105),
            10
        )

        texts, pos = self._add_nes_text(
            "moves",
            text_size=30,
            reverse=True,
            centerx=rect.centerx+2,
            top=250,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)

        pygame.draw.line(
            background, 
            RED, 
            (pos[1].left - 2, pos[1].bottom), 
            (pos[1].right - 5, pos[1].bottom), 
            2
        )

        texts, pos = self._add_text(
            str(self.board.moves),
            text_size=40,
            reverse=True,
            centerx=pos[1].centerx,
            centery=pos[1].centery + 47,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)

        pass
    
    # Returns the number of specific goals
    def _get_objectives_string(self, a, b):
        string = ""

        string += str(a - b)
        string += "/"
        string += str(a)

        return string

    # Returns the amount of points needed to earn
    def _get_points_string(self):

        points = self.board.w_points
        m = int(points/1000000)
        
        if m > 0:
            return ("%dM" % m)
        
        k = int(points/1000)
        if k > 0:
            return ("%dK" % k)
        
        return str(points)

    # Objective Box
    def _print_game_objectives(self, background):

        pygame.draw.rect(
            background,
            WHITE,
            (15, 355, 190, 225),
        )

        rect = pygame.draw.rect(
            background,
            BLACK,
            (15, 355, 190, 225),
            10
        )

        texts, pos = self._add_text_pix(
            "GOALS",
            text_size=40,
            reverse=True,
            centerx=rect.centerx+2,
            top=rect.top,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)

        pygame.draw.line(
            background, 
            RED, 
            (pos[1].left - 2, pos[1].bottom), 
            (pos[1].right - 5, pos[1].bottom), 
            2
        )

        ''' Number of Points Required. '''

        # Background of the field where the points are
        pygame.draw.rect(
            background,
            GREY,
            (pos[1].left-5, pos[1].bottom +10,
            155, 40),
        )

        rect_b = pygame.draw.rect(
            background,
            BLACK,
            (pos[1].left-5, pos[1].bottom +10,
            155, 40),
            3
        )

        texts, pos = self._add_text_pix(
            "PTS",
            text_size=30,
            reverse=True,
            left=pos[1].left,
            top=pos[1].bottom +10,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)
        
        texts_aux, pos_aux = self._add_text_pix(
            self._get_points_string(),
            text_size=22,
            reverse=True,
            centery=pos[1].centery,
            centerx=pos[1].right + 40,
        )
        for t, p in zip(texts_aux, pos_aux):
            background.blit(t,p)
        
        if self.board.points >= self.board.w_points:
            self._draw_complete(background, rect_b)
        
        ''' Number of Objectives Required. '''

        pygame.draw.rect(
            background,
            GREY,
            (pos[1].left-5, pos[1].bottom +10,
            155, 50),
        )

        rect_b = pygame.draw.rect(
            background,
            BLACK,
            (pos[1].left-5, pos[1].bottom +10,
            155, 50),
            3
        )

        image = self.objective_image[0]
        rect = self.objective_image[1]
        rect.left = pos[1].left +10
        rect.top = pos[1].bottom +18
        background.blit(image, rect)

        texts_aux, pos_aux = self._add_text_pix(
            self._get_objectives_string(self.objectives, self.board.canes),
            text_size=22,
            reverse=True,
            centery=rect.centery,
            centerx=rect.right + 55,
        )
        for t, p in zip(texts_aux, pos_aux):
            background.blit(t,p)

        if self.board.canes == 0:
            self._draw_complete(background, rect_b)

        ''' Number of Blocks Required '''

        pygame.draw.rect(
            background,
            GREY,
            (pos[1].left-5, rect.bottom +15,
            155, 50),
        )

        rect_b = pygame.draw.rect(
            background,
            BLACK,
            (pos[1].left-5, rect.bottom +15,
            155, 50),
            3
        )

        rect = pygame.draw.rect(
            background,
            BLUE,
            (rect.left, rect.bottom +23,
            rect.width, rect.height),
            5
        )

        s = pygame.Surface(rect.size)
        s.set_alpha(128)
        s.fill(BLUE)
        background.blit(s, (rect.left, rect.top))

        texts, pos = self._add_text_pix(
            self._get_objectives_string(self.blocks, self.board.blocks),
            text_size=22,
            reverse=True,
            centery=rect.centery,
            centerx=rect.right + 55,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)

        if self.board.blocks == 0:
            self._draw_complete(background, rect_b)

    # If you have already completed the objectives, put a cross
    def _draw_complete(self, background, rect_b):

            pygame.draw.line(
                background, 
                RED, 
                rect_b.topright, 
                rect_b.bottomleft, 
                5
            )

            pygame.draw.line(
                background, 
                RED, 
                rect_b.topleft, 
                rect_b.bottomright, 
                5
            )

    # Prints all game information on the screen
    def _print_game_info(self, background):

        self._print_game_mode(background)
        self._print_game_points(background)
        self._print_game_moves(background)
        self._print_game_objectives(background)
    
    def _print_game_level(self, background):

        level = self.level + 1
        string = "level %d" % level
        texts, pos = self._add_nes_text(
            string,
            text_size=25,
            centerx=470,
            top=0,
        )

        for t, p in zip(texts,pos):
            background.blit(t,p)

    # Print the Round information
    def _print_round_info(self, background):
        points = self.round_info[0]
        pieces = self.round_info[1]
        self.end = self.round_info[2]
        self.win = self.round_info[3]

        # Paint the background of the field
        rect = pygame.draw.rect(
            background,
            MODE_COLORS[self.board.mode],
            (230,
            size[1]/2 - 50, 
            550, 
            80),
        )

        # Make the movement field
        pygame.draw.rect(
            background,
            WHITE,
            (230 -5,
            size[1]/2 - 55, 
            550 +10, 
            80 +10),
            10
        )

        # Make the movement field
        pygame.draw.rect(
            background,
            BLACK,
            (230,
            size[1]/2 - 50, 
            550, 
            80),
            10
        )

        string = "%d POINTS AVENGED" % points
        texts, pos = self._add_text_pix(
            string,
            text_size=25,
            centerx=rect.centerx+2,
            top=rect.top +5,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)
        
        string = "%d TROOPS DESTROYED" % pieces
        texts, pos = self._add_text_pix(
            string,
            text_size=25,
            centerx=rect.centerx+2,
            bottom=rect.bottom -10,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)

    # Print the end of the game
    def _print_end_game(self, background):
        
        string, color = None, None
        # If won
        if self.win:
            string = "you Avenged!"
            color = RED
        # If lost
        else:
            string = "hAil hydrA!"
            color = BLACK

        left = 145
        top = size[1]/2 - 45
        width = 500
        height = 100

        # Make the movement field
        pygame.draw.rect(
            background,
            BLACK,
            (left -5,
            top -5, 
            width +10, 
            height +10),
            15
        )

        # Paint the background of the field
        rect = pygame.draw.rect(
            background,
            color,
            (left,
            top, 
            width, 
            height),
        )

        # Make the movement field
        rect = pygame.draw.rect(
            background,
            WHITE,
            (left,
            top, 
            width, 
            height),
            10
        )

        # Print end of game String
        texts, pos = self._add_nes_text(
            string,
            reverse=False,
            text_size=70,
        )
        for t, p in zip(texts,pos):
            background.blit(t,p)

    def get_reward_canes(self):
        canes = self.board.get_canes_reward()
        value = self.objectives - len(canes)

        for c in canes:
            value += c

        return float(value/self.objectives)


    def get_reward(self):
        p_blocks = 1
        p_canes = 1
        p_points = 1

        count = 0
        total = 0


        if self.blocks > 0:
            if self.blocks != self.board.blocks:
                blocks = 1/(self.blocks/(self.blocks - self.board.blocks))
            else:
                blocks = 0
            total += blocks
            count += p_blocks
        

        if self.objectives > 0:
            total += self.get_reward_canes()
            count += p_canes

        if self.board.w_points > 0:
            points = 0
            if self.board.points >= self.board.w_points:
                points = 1
            else:
                points = self.board.points/self.board.w_points
            
            total += points
            count += p_points
        
        if count > 0:
            return total/count
        else:
            return 1.0

    # Write the reward in the file
    def _write_reward(self):
        r = self.get_reward()

        i = self.level +1
        filename = "information/%d.txt" % i
        f = open(filename, "a+")

        string = "\n" + str(r)
        f.write(string)

        f.close()

    # Works all game screen operation  
    def _game_screen(self):
        
        # Possible game screen events
        for event in self.events:
            
            # Pressed with the mouse (left button)
            if event.type == MOUSEBUTTONDOWN and event.button == 1:

                # It only accepts movements if there is no message on the screen
                if self.round_info is None and not self.end:

                    # mouse position
                    pos = pygame.mouse.get_pos()

                    # Cycles through all the tiles in the field
                    find = False
                    for pieces in self.board.level:
                        for p in pieces:
                            
                            # Check for collision
                            if p.rect.collidepoint(pos):
                                self.pick = self._check_picked_piece(p) 
                                find = True
                                break
                        
                        # If found, exit the loop
                        if find:
                            break
                    
                    # If you can't find it, remove the part.
                    if not find:
                        self.pick = None
                
                # if the phase is over
                elif self.end:
                    self._write_reward()
                    self._set_level_screen()

        # Create the phase background
        background = pygame.Surface(self.screen.get_size())
        background = background.convert()
        background.fill(MODE_COLORS[self.board.mode])

        # Print game information
        self._print_game_info(background)
        
        # Add white color to background
        # Print the outline
        pygame.draw.rect(
            background,
            WHITE,
            (self.board.level[0][0].rect.left -5,
            self.board.level[0][0].rect.top -5,
            self.board.level[8][8].rect.right -215,
            self.board.level[8][8].rect.bottom -15),
        )

        # Print the parts on the screen
        for pieces in self.board.level:
            for p in pieces:
                background.blit(p.image, p.rect)
                background = self._draw_square(background, p)
        
        # print the outline
        pygame.draw.rect(
            background,
            BLACK,
            (self.board.level[0][0].rect.left -5,
            self.board.level[0][0].rect.top -5,
            self.board.level[8][8].rect.right -215,
            self.board.level[8][8].rect.bottom -15),
            10
        )
        
        # Print the chosen part
        if self.pick is not None:
            self._draw_square(
                background,
                self.pick,
                color=RED,
                width=5)

        # Print the information on the screen
        if self.round_info is not None:

            self.timer += 1
            if self.timer < 90:
                self._print_round_info(background)
            else:
                self.timer = 0
                self.round_info = None
        
        # Check if it's game over
        elif self.end:
            self._print_end_game(background)

        # Print the screen level
        self._print_game_level(background)

        # Returns the screen to be printed
        return background