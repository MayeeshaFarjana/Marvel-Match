from sre_parse import State
import pygame
import numpy as np
from pygame.locals import *
import copy
import random

import piece
import game_utils


# special types
special = (
    piece.Stripped,
    piece.Wrapped,
    piece.Bomb
)

# Types that don't break
extra = (
    piece.Objective,
    piece.Block
)

'''
working with
all movement and goals
'''
class Board(pygame.sprite.Sprite):

    # launcher
    def __init__(self, file=None, string=None):
        pygame.sprite.Sprite.__init__(self)
        
        # Random State
        self.state = None

        # Starting the information with the file
        if file is not None:
            self.info, self.map = game_utils.load_level(file)
        elif string is not None:
            self.info, self.map = game_utils.load_level_string(string)
        else:
            self.info, self.map = None, None

        # Number of Destroyed Parts
        self.piece_destroyed = 0

        # Number of points since the last round
        self.last_round_points = 0

        # Initialize the maps
        self._create_labels()
        self._set_info()
        self._create_level()

    def copy_level(self, level):
        for x in range(9):
            for y in range(9):
                self.level[x][y] = copy.deepcopy(level[x][y])
        pass

    def _print_board(self):
        for i in range(9):
            for j in range(9):
                p = self.level[i][j]
                string = ''
                if p is None:
                    string += '_'
                elif type(p) is piece.Block:
                    string += 'X'
                elif type(p) is piece.Objective:
                    string += "O"
                elif type(p) is piece.Simple:
                    string += "s"
                elif type(p) is piece.Protection:
                    string += "p"
                elif type(p) is piece.Stripped:
                    string += "S"
                elif type(p) is piece.Wrapped:
                    string += "W"
                elif type(p) is piece.Bomb:
                    string += "B"
                else:
                    string += "_"
                print("%s " % string, end="")
            print("")
        print("")

    def get_canes_reward(self):
        canes = []

        level = self.map
        for i, row in enumerate(level):
            for j, p in enumerate(row):
                if self.labels[j][i] == 3:
                    x = i/8
                    canes.append(x)
        
        return canes

    # Return the random state
    def get_random_state(self):
        if self.state is None:
            self.state = random.getstate()
        return self.state
    
    # Set the random state
    def set_random_state(self, state):
        self.state = state

    # Update random state
    def update_random_state(self):
        if State is not None:
            random.setstate(self.state)

    # Check if the game is finished
    def is_finished(self):

        # checks if the score made is higher than necessary
        if self.w_points > self.points:
            return False
        
        # Checks if ingredients are already off the map
        if self.canes > 0:
            return False
        
        # Checks if all locks are destroyed
        if self.blocks > 0:
            return False
        
        # The game is over
        return True

    # Defines labels for special parts positions
    def _create_labels(self, first=True):
        level = self.map

        # Initialize labels to 0
        self.labels = np.zeros((9,9), dtype=int)
        if first:
            if level is not None:
                for i, row in enumerate(level):
                    for j, p in enumerate(row):
                        
                        # If there is a purpose or protection
                        if p == 2 or p == 3:
                            self.labels[j][i] = p
        else:
            for x in range(9):
                for y in range(9):
                    p = self.level[x][y]
                    if p is not None:
                        if type(p) is piece.Objective:
                            self.labels[x][y] = 3
                        elif type(p) is piece.Protection:
                            self.labels[x][y] = 2

    # Update goals
    def _update_objectives(self):

        self.canes, self.blocks = 0, 0
        for x in range(9):
            for y in range(9):
                if self.labels[x][y] == 2:
                    self.blocks += 1
                elif self.labels[x][y] == 3:
                    self.canes += 1

    # Add game mode
    def _set_mode(self):
        modes = 0

        # For a point goal, update
        if self.w_points > 0:
            self.mode = 'POINTS'
            modes += 1

        # For blocking goals, update
        if self.blocks > 0:
            self.mode = 'BLOCKS'
            modes += 1

        # For item goals, update
        if self.canes > 0:
            self.mode = 'OBJECTIVE'
            modes += 1

        # If you have more than one mode, upgrade to MIX
        if modes > 1:
            self.mode = 'MIX'

    # Add map information
    def _set_info(self):
        info = self.info
        
        self.points = 0
        if info is not None:
            self.moves = info[0]
            self.w_points = info[1]
            self.types = info[2]
        else:
            self.w_points = 9999999
            self.blocks = 0
            self.canes = 0
            self.moves = 75
            self.types = 6
        
        # Update the goals
        self._update_objectives()

        # Update game mode
        self._set_mode()

    # Checks if the map does not have sequences of 3 or more
    def _check_board(self, level):

        # Go through the whole field
        for i in range(9):
            for j in range(9):
                
                # Take the part and its type
                p = level[i][j]
                t = None
                try:
                    t = p.type
                except:
                    continue

                # If it's bigger, you don't need to check
                if i + 2 < 9:

                    # If you found a sequence of the same type,
                    # returns True
                    for index in range(1,3):
                        p_aux = level[i+index][j]
                        t_aux = None
                        try:
                            t_aux = p_aux.type
                        except:
                            break

                        if t != t_aux:
                            break
                    else:
                        return True

                # If it's bigger, you don't need to check
                if j + 2 < 9:

                    # If you found a sequence of the same type,
                    # returns True
                    for index in range(1,3):
                        p_aux = level[i][j+index]
                        t_aux = None
                        try:
                            t_aux = p_aux.type
                        except:
                            break

                        if t != t_aux:
                            break
                    else:
                        return True
        
        return False

    # Generate the game map
    def _create_level(self, first=True):
        level = self.map
        self.level = np.zeros((9, 9), dtype=object)

        # If the level has been passed, initialize
        if level is not None:
            for i, row in enumerate(level):
                for j, p in enumerate(row):
                    check = True

                    # Spawns pieces while it's not a legal move
                    while(check):
                        
                        # Add a Protection
                        if self.labels[j][i] == 2:
                            self.level[j][i] = piece.Protection(j,i,self.types)
                        
                        # Add a Goal
                        elif self.labels[j][i] == 3:
                            self.level[j][i] = piece.Objective(j,i)

                        # Add a block
                        elif p == 0:
                            self.level[j][i] = piece.Block(j,i)

                        # Add a single part
                        else:
                            self.level[j][i] = piece.Simple(j,i,self.types)
                        
                        # Check if there are possible moves
                        check = self._check_board(self.level)

        # If not, create a pattern
        else:
            for x in range(9):
                for y in range(9):
                    check = True
                    while(check):
                        self.level[x][y] = piece.Simple(x,y,self.types)
                        check = self._check_board(self.level)
        
        if not self._has_moves():
            return self._create_level(first=False)

    # Returns a list of all parts
    def get_board(self):

        list_pieces = []
        for i in range(9):
            for j in range(9):
                list_pieces.append(
                    self.level[i][j].get_piece()
                )
        
        return list_pieces

    # Move the two pieces in place
    def _move_pieces(self, p1, p2):
        # Check the new positions
        pos1 = (p1.x, p1.y)
        pos2 = (p2.x, p2.y)
        p1.x = pos2[0]
        p1.y = pos2[1]
        p2.x = pos1[0]
        p2.y = pos1[1]

        # Make a copy of the level and change the positions
        self.level[p1.x][p1.y] = p1
        self.level[p2.x][p2.y] = p2
        p1.update_rect()
        p2.update_rect()

    # Check all combinations with this part
    def _check_combinations(self, p, factor):

        # Check the sequence to the left of the part
        x = p.x -1
        left = 0
        while x >= 0:
            
            # Checks if it's the same type, in case something happens
            # error, it's a class with no "type", so skip it
            try:
                if self.level[x][p.y].type == p.type:
                    left += 1
                else:
                    break
            except:
                break
            
            x -= 1
        
        # Check the sequence to the right of the part
        x = p.x +1
        right = 0
        while x < 9:
            
            # Check if it's the same type, in case something happens
            # error, it's a class with no "type", so skip it
            try:
                if self.level[x][p.y].type == p.type:
                    right += 1
                else:
                    break
            except:
                break

            x += 1
        
        # Check the sequence above the piece
        y = p.y -1
        top = 0
        while y >= 0:
            
            try:
                if self.level[p.x][y].type == p.type:
                    top += 1
                else:
                    break
            except:
                break
            
            y -= 1
        
        # Check the sequence below the part
        y = p.y +1
        bottom = 0
        while y < 9:
            
            # Checks if it's the same type, in case something happens
            # error, it's a class with no "type", so skip it
            try:
                if self.level[p.x][y].type == p.type:
                    bottom += 1
                else:
                    break
            except:
                break

            y += 1
        
        # Get string size
        row = left + right + 1 # line
        col = top + bottom + 1 # column

        # New part in place?
        new_piece = None
        if row >= 5 or col >= 5: # EQUAL TO BOMB
            new_piece = piece.Bomb(p.x, p.y)
        elif row >= 3 and col >= 3: # EQUAL TO WRAPPED
            new_piece = piece.Wrapped(p.x, p.y, p.type)
        elif row == 4 or col == 4: # IQUAL TO STRIPPED
            new_piece = piece.Stripped(p.x, p.y, p.type)

        # Indicates whether the part has been deleted
        delete = False

        # check the line
        if row >= 3:
            delete = True
            for i in range(p.x - left, p.x + right + 1):
                self._destroy_single_piece(self.level[i][p.y])
        
        # Check the Column
        if col >= 3:
            delete = True
            for j in range(p.y - top, p.y + bottom + 1):
                self._destroy_single_piece(self.level[p.x][j])
        
        # If the part was deleted, delete it
        if delete:
            if new_piece is not None:
                self.level[p.x][p.y] = new_piece
            
            # total parts
            total = row + col - 1
            total -= 2
            self.points += (total * 60) * factor

    # Destroy the field pieces
    def _destroy_pieces(self, pieces, factor=0):
        
        factor += 1

        # Check the combination of these two pieces
        for p in pieces:
            self._check_combinations(p, factor)

        # Checks if a goal was found
        found_objective = False

        # Cycle through all columns
        for x in range(9):
            
            blocks = True

            # Go from the lowest position to the top
            for y in reversed(range(9)):

                # If you found the objective while you have blocks below, delete it!
                if type(self.level[x][y]) is piece.Objective and blocks:
                    found_objective = True
                    self._eliminate_piece(self.level[x][y])

                # If not block
                if type(self.level[x][y]) is not piece.Block:
                    blocks = False

                # If the position is None, it is necessary fetch the positions
                if self.level[x][y] is None:
                    find = False

                    # Scroll until you find a different piece
                    # of None and different form of Block
                    for i in reversed(range(y)):

                        p = self.level[x][i]
                        if (p is not None) and (type(p) is not piece.Block):
                            find = True
                            
                            # Update with new position
                            p.x = x
                            p.y = y
                            self.level[x][y] = p

                            # Remove the part from the old position
                            self.level[x][i] = None

                            # If you have combinations, destroy in location of this part
                            if self._check_board(self.level):
                                return self._destroy_pieces([p], factor=factor)
                            
                            # Update the position in the field
                            self.level[x][y].update_rect()

                            # Already added piece, you can get out of the loop!
                            break
                    
                    # If you didn't find any parts,
                    # add new pieces to positions
                    if not find:
                        
                        # Start from the piece to the top
                        for i in reversed(range(y+1)):
                            
                            # If it's not protection, add the new part!
                            if type(self.level[x][i]) is not piece.Block:

                                # Add the new part
                                self.level[x][i] = piece.Simple(x,i,self.types)

                                # If it generates a new possibility, destroy!
                                if self._check_board(self.level):
                                    return self._destroy_pieces([self.level[x][i]], factor=factor)
                        
                        # Already added enough pieces,
                        # can jump to next position
                        break
        
        # Found objective, destroyed again
        if found_objective:
            return self._destroy_pieces([])

        # Checks the parts in the last position
        destroy = False
        for x in range(9):
            if type(self.level[x][8]) is piece.Objective:
                self._eliminate_piece(self.level[x][8])
                destroy = True
        
        # If destroyed, redo it again
        if destroy:
            return self._destroy_pieces([])


        # Update objective labels
        self._create_labels(first=False)
        
        # The Board is complete again, now
        # if there are no possible moves, generate it again
        if not self._has_moves():
            self._create_level(first=False)
        
        # Update positions
        self._update_rects()

    # Update parts rects
    def _update_rects(self):
        for x in range(9):
            for y in range(9):
                p = self.level[x][y]
                p.x = x
                p.y = y
                p.update_rect()

    # Used to check if the board has possible moves
    def _has_moves(self):

        # Go through the whole field
        for y in range(9):
            for x in range(9):

                # Get the part type
                p = self.level[x][y]
                try:
                    t = p.type
                except:
                    continue
                
                # Check sequences to verify moves
                if x + 3 < 9:
                    
                    # Go through the next 3 pieces and
                    # check if there is only one different type
                    count = 0
                    for index in range(1,4):
                        p_aux = self.level[x+index][y]
                        t_aux = None
                        try:
                            t_aux = p_aux.type
                        except:
                            break
                        
                        # If the types are different,
                        # sum 1
                        if t_aux != t:
                            count += 1
                        
                        # If found more than 1, skip
                        if count > 1:
                            break
                    # If you went through this whole process, you have movements
                    else:
                        return True
                
                # Check sequences to verify moves
                if y + 3 < 9:

                    # Go through the next 3 pieces and
                    # check if there is only one different type
                    count = 0
                    for index in range(1,4):
                        p_aux = self.level[x][y+index]
                        t_aux = None
                        try:
                            t_aux = p_aux.type
                        except:
                            break
                        
                        # If the types are different,
                        # sum 1
                        if t_aux != t:
                            count += 1
                        
                        # If found more than 1, skip
                        if count > 1:
                            break
                    # If you went through this whole process, you have movements
                    else:
                        return True
        
        # has no move
        return False

    # information returned
    def _finish_move(self):

        # Calculates the number of points made
        points = self.points - self.last_round_points
        self.last_round_points = self.points

        # Update goals
        self._update_objectives()

        return (
            points, # Points Made this round,
            self.piece_destroyed, # Pieces Eliminated this round,
            self.is_finished() or (self.moves == 0), # Indicates whether the match has ended 
            self.is_finished() # Indicates whether the match has been won
        )  

    # Tests if movement is possible
    def test_move(self, p1, p2, mcts=False):

        if mcts:
            self.update_random_state()

        # If the game is over, you cannot play!
        if self.is_finished():
            return None

        self.piece_destroyed = 0

        # If you don't have special combinations
        if not self._special_comb(p1, p2):

            # Swap the position pieces
            self._move_pieces(p1,p2)

            # If valid moves emerged,
            # destroy the pieces in sequence
            if self._check_board(self.level):

                self._destroy_pieces([p1,p2])
                self.moves -= 1
                return self._finish_move()
            
            # No valid moves appeared, returns the
            # parts to the correct location
            else:
                self._move_pieces(p1,p2)
        
        # There were special combinations!
        else:
            self._destroy_pieces([])
            self.moves -= 1
            return self._finish_move()

        return None

    # Used to eliminate this piece from the field
    def _eliminate_piece(self, p):
        if p is not None:
            self.piece_destroyed += 1
            self.points += p.points
            self.level[p.x][p.y] = None

    # Delete row and column at the same time
    def _special_double_stripped(self, p):

        if p is None:
            return

        x = p.x
        for y in range(9):
            aux_p = self.level[x][y]
            self._destroy_single_piece(aux_p)
        
        y = p.y
        for x in range(9):
            aux_p = self.level[x][y]
            self._destroy_single_piece(aux_p)

    # Eliminate the 24 pieces around
    def _special_double_wrapped(self, p):

        if p is None:
            return

        # Makes the same as normal, but with a larger size
        self._special_wrapped(p, size=2)

    # Destroy all field pieces
    def _special_double_bomb(self):

        # Destroy all field pieces
        for x in range(9):
            for y in range(9):
                p = self.level[x][y]
                self._destroy_single_piece(p)

    # Delete 3 rows and 3 columns 
    def _special_stripped_wrapped(self, p, size=2):
        
        if p is None:
            return

        # Returns the ranges
        x, y, end_x, end_y = self._get_wrapped_size(p, size)

        # Scroll diagonally, deleting row and column
        i = 0
        while i < 3:
            if end_x <= 8 and end_y <= 8:
                aux_p = self.level[x+i][y+i]
                self._special_double_stripped(aux_p)
            else:
                break
            i += 1

    # Turns all tiles of the same type into stripes and activates them
    def _special_stripped_bomb(self, p):

        if p is None:
            return

        # Go through all the pieces
        for x in range(9):
            for y in range(9):
                aux_p = self.level[x][y]

                # If it's the same type, activate them as striped
                if self._can_destroy(aux_p) and aux_p.type == p.type:
                    self._special_stripped(aux_p)

    # Turns all pieces of the same type into gummies, and activates them 
    def _special_wrapped_bomb(self, p):

        if p is None:
            return

        # Go through all the pieces
        for x in range(9):
            for y in range(9):
                aux_p = self.level[x][y]

                # If it's the same type, activate them as striped
                if self._can_destroy(aux_p) and aux_p.type == p.type:
                    self._special_wrapped(aux_p)

    # delete an entire row or column, randomly 
    def _special_stripped(self, p):

        if p is None:
            return

        # Decide on the move option
        option = random.choice([True, False])

        # If it's True, it's row
        if option:
            y = p.y

            # Traverses the entire row
            for x in range(9):
                aux_p = self.level[x][y]
                self._destroy_single_piece(aux_p)

        # If it's False, it's Column
        else:
            x = p.x

            # Traverses the entire column
            for y in range(9):
                aux_p = self.level[x][y]
                if self._can_destroy(aux_p):
                    self._eliminate_piece(aux_p)

    # eliminate the 8 pieces around it 
    def _special_wrapped(self, p, size=1):

        if p is None:
            return

        x, y, end_x, end_y = self._get_wrapped_size(p, size)
        
        # Go through the entire area
        for i in range(x, end_x):
            for j in range(y, end_y):
                aux_p = self.level[i][j]
                self._destroy_single_piece(aux_p)

    # Returns gum-like intervals
    def _get_wrapped_size(self, p, size):
        # Take previous positions 
        x = p.x - size
        y = p.y - size

        # if it passed the shores
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        
        # Take the final positions
        end_x = p.x + size + 1
        end_y = p.y + size + 1

        # if it passed the shores
        if end_x > 8:
            end_x = 8
        if end_y > 8:
            end_y = 8
        
        return x, y, end_x, end_y

    # eliminates all pieces of the same color from the field.
    def _special_bomb(self, p):

        t = None
        # If the part is None, decide a random type
        if p is None:
            t = random.randint(0,self.types -1)
        else:
            t = p.type


        # Go through all positions
        for x in range(9):
            for y in range(9):
                aux_p = self.level[x][y]
                
                # If the part can be destroyed
                if self._can_destroy(aux_p) and aux_p.type == t:
                    self._destroy_single_piece(aux_p)

    # Destroys a single piece, referring to its type
    def _destroy_single_piece(self, p):

        # If you don't have a part, skip to the next one.
        if p is None:
            return 

        # If it's a special part, activate it
        if self._is_special(p):
            return self._special_type(p)
        
        # If not Blocking or targeting, delete
        elif self._can_destroy(p):
            # Destroy the part to not have double effect
            return self._eliminate_piece(p)

    # Decide what type the piece is and activate its power 
    def _special_type(self, p):
        
        # delete the part
        self._eliminate_piece(p)

        if type(p) is None:
            return
        elif type(p) is piece.Stripped:
            return self._special_stripped(p)
        elif type(p) is piece.Wrapped:
            return self._special_wrapped(p)
        elif type(p) is piece.Bomb:
            return self._special_bomb(None)

    # Check if it's a special part
    def _is_special(self, p):

        # If it's None, it's not special
        if p is None:
            return False
        
        # If it's Striped, it's special
        elif type(p) is piece.Stripped:
            return True
        
        # If it's Gum, it's special
        elif type(p) is piece.Wrapped:
            return True

        # If it's Bomb, it's special
        elif type(p) is piece.Bomb:
            return True
        
        # Any other case is false
        return False

    # Used to check if a part can be destroyed
    def _can_destroy(self, p):

        # It's None, it's not a piece
        if p is None:
            return False
        # If it's a simple piece, you can't
        elif type(p) is piece.Piece:
            return False
        # A block cannot be destroyed
        elif type(p) is piece.Block:
            return False
        elif type(p) is piece.Objective:
            return False
        
        # The rest can be destroyed
        return True

    # Method for all special combinations
    def _special_comb(self, p1, p2):
        
        # If one of the two is None
        if p1 is None or p2 is None:
            return False

        # Eliminate the pieces from the field to not have a double effect
        if self._is_special(p1) and self._is_special(p2):
            self._eliminate_piece(p1)
            self._eliminate_piece(p2)
        elif type(p1) is piece.Bomb:
            self._eliminate_piece(p1)
        elif type(p2) is piece.Bomb:
            self._eliminate_piece(p2)

        # If the 2 types are the same
        if type(p1) is type(p2):

            # If it's striped type
            if type(p1) is piece.Stripped:
                # Delete row and column at the same time
                self._special_double_stripped(p1)
                return True
            
            # if it's like gum
            elif type(p1) is piece.Wrapped:

                # Eliminate the 24 pieces around
                self._special_double_wrapped(p1)
                return True
            
            # If it's Bomb type
            elif type(p1) is piece.Bomb:
                # Destroy all field pieces
                self._special_double_bomb()
                return True
        
        # The two types are different
        else:

            # If the first piece is Striped
            if type(p1) is piece.Stripped:
                
                # If the second piece is Gum
                if type(p2) is piece.Wrapped:

                    # Delete 3 rows and 3 columns
                    self._special_stripped_wrapped(p1)
                    return True

                # If the second part is Bomb
                elif type(p2) is piece.Bomb:

                    # Transforms all tiles into the same type
                    # in stripes and activate them 
                    self._special_stripped_bomb(p1)
                    return True
            
            # If the first piece is Gum
            elif type(p1) is piece.Wrapped:
                
                # If the second piece is Striped
                if type(p2) is piece.Stripped:

                    # Delete 3 rows and 3 columns
                    self._special_stripped_wrapped(p1)
                    return True
                
                # If the second part is Bomb
                elif type(p2) is piece.Bomb:

                    # Transform all tiles of the same type 
                    # into gums, and activate them
                    self._special_wrapped_bomb(p1)
                    return True
            
            # If the first part is Bomb
            elif type(p1) is piece.Bomb:
                
                # If the second piece is Striped
                if type(p2) is piece.Stripped:

                    # Transforms all tiles into the same type
                    # in stripes and activate them
                    self._special_stripped_bomb(p2)
                    return True
                
                # If the second piece is Gum
                elif type(p2) is piece.Wrapped:

                    # Transforms all tiles into the same type
                    # into gummies, and activate them
                    self._special_wrapped_bomb(p2)
                    return True
        
        # If one of the pieces is Bomb at this point, the other is
        # a single piece
        if (type(p1) is piece.Bomb) or (type(p2) is piece.Bomb):

            # Activates the power of the PUMP Part on the Simple part
            if p1.type != -1:
                self._special_bomb(p1)
            else:
                self._special_bomb(p2)
            
            return True

        # No special part combinations
        return False
    
    # Method for all combinations
    def _check_move(self, p1, p2, moves):
        
        # If either one is none
        if p1 is None or p2 is None:
            return

        # If both pieces are special, the move is valid.
        if self._is_special(p1) and self._is_special(p2):
            moves.append((p1,p2))
            return
        
        # If one of the pieces is a bomb, the move is valid.
        if type(p1) is piece.Bomb or type(p2) is piece.Bomb:
            moves.append((p1,p2))
            return
        
        # Change the position of pieces
        self._move_pieces(p1, p2)
        
        # If it generates moves, the move is valid
        if self._check_board(self.level):
            moves.append((p1,p2))
        
        # Returns the parts to their original position
        self._move_pieces(p1, p2)

    # Print the possible moves
    def _print_possible_moves(self, moves):
        print("[")
        for move in moves:
            print("(%d,%d) -> " % (move[0].x, move[0].y), end="")
            print("(%d,%d)" % (move[1].x, move[1].y))
        print("]")

    # Returns a list of tuples with all possible moves
    def possible_moves(self):

        # If the game is already in terminal state, return None
        if self.is_finished():
            return None

        moves = []
        # Go through all the possibilities
        for x in range(9):
            for y in range(9):
                p1 = self.level[x][y]

                # If this piece cannot be destroyed, skip to the next one.
                if not self._can_destroy(p1):
                    continue
                
                # Horizontal Combination
                if x + 1 < 9:
                    p2 = self.level[x+1][y]
                    if self._can_destroy(p2):
                        self._check_move(p1, p2, moves)

                # Vertical Combination
                if y + 1 < 9:
                    p2 = self.level[x][y+1]
                    if self._can_destroy(p2):
                        self._check_move(p1, p2, moves)

        return moves