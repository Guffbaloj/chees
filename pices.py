import pygame
import copy
pygame.init()
class Piece:
    def __init__(self, board, e_type, images, color):
        self.board = board
        self.type = e_type
        self.pos = (0, 0)
        self.images = images
        self.moveset = []
        self.color = color
        self.first_move = True
    def update(self):
        pass  

    def set_pos(self, new_pos):
        self.pos = new_pos

    def get_rect(self):
        square_size = self.board["square size"]
        rect = pygame.rect.Rect(self.pos[0], self.pos[1], square_size, square_size)
        return rect
    def get_board_index(self):
        board_size = self.board["size"]
        square_size = self.board["square size"]
        render_offset = self.board["render offset"]
        return (self.pos[0] - render_offset[0]) // square_size + ((self.pos[1] - render_offset[1]) // square_size * board_size)

    def render(self, display: pygame.Surface):
        img: pygame.Surface = self.images[self.color + " " + self.type]
        rect = img.get_rect()
        display.blit(img, self.pos, rect)

    def on_move_code(self, move):
        self.first_move = False
    
    def clone(self):
        return copy.copy(self)
    def __getstate__(self):
        # Copy the object's state but remove the 'image' or 'surface'
        state = self.__dict__.copy()
        if 'images' in state: 
            del state['images'] # Don't try to clone the actual Pygame image
        return state

    def __setstate__(self, state):
        # Restore the state (you'll need to re-link images manually if needed)
        self.__dict__.update(state)

class Move:
    def __init__(self, vector: list[int, int], range = 8, can_kill = True, kill_only = False):
        self.vector = vector
        self.range = range
        self.can_kill = can_kill
        self.kill_only = kill_only

class Pawn(Piece):
    def __init__(self, board, images, color):
        super().__init__(board, "pawn", images, color)
        self.moveset = [Move([0, 1], range= 2, can_kill= False),
                        Move([1, 1], range= 1, can_kill= True, kill_only= True),
                        Move([-1, 1], range= 1, can_kill= True, kill_only= True)]
    def on_move_code(self, move):
        if self.first_move:
            self.moveset[0] = Move([0, 1], range= 1, can_kill= False)
            bidx = self.get_board_index()
            if abs(bidx - move[0]) == 2 * self.board["size"]: #Om bonden har gått 2 steg:
                return "spawn ghost"

        super().on_move_code(move)

class Knight(Piece):
    def __init__(self, board, images, color):
        super().__init__(board, "knight", images, color)
        self.moveset = [Move([2, -1], range= 1, can_kill= True),
                        Move([2, 1], range= 1, can_kill= True),
                        Move([-1,2], range= 1, can_kill= True),
                        Move([1, 2], range= 1, can_kill= True),
                        Move([-2, -1], range= 1, can_kill= True),
                        Move([-2, 1], range= 1, can_kill= True),
                        Move([-1,-2], range= 1, can_kill= True),
                        Move([1, -2], range= 1, can_kill= True)]

class Rook(Piece):
    def __init__(self, board, images, color):
        super().__init__(board, "rook", images, color)
        self.moveset = [Move([0, -1], range= 8, can_kill= True),
                        Move([0, 1], range= 8, can_kill= True),
                        Move([-1,0], range= 8, can_kill= True),
                        Move([1, 0], range= 8, can_kill= True)]

class Bishop(Piece):
    def __init__(self, board, images, color):
        super().__init__(board, "bishop", images, color)
        self.moveset = [Move([-1, -1], range= 8, can_kill= True),
                        Move([1, 1], range= 8, can_kill= True),
                        Move([-1,1], range= 8, can_kill= True),
                        Move([1, -1], range= 8, can_kill= True)]

class Queen(Piece):
    def __init__(self, board, images, color):
        super().__init__(board, "queen", images, color)
        self.moveset = [Move([-1, -1], range= 8, can_kill= True),
                        Move([1, 1], range= 8, can_kill= True),
                        Move([-1,1], range= 8, can_kill= True),
                        Move([1, -1], range= 8, can_kill= True),
                        Move([0, -1], range= 8, can_kill= True),
                        Move([0, 1], range= 8, can_kill= True),
                        Move([-1,0], range= 8, can_kill= True),
                        Move([1, 0], range= 8, can_kill= True)]
class King(Piece):
    def __init__(self, board, images, color):
        super().__init__(board, "king", images, color)
        self.moveset = [Move([-1, -1], range= 1, can_kill= True),
                        Move([1, 1], range= 1, can_kill= True),
                        Move([-1,1], range= 1, can_kill= True),
                        Move([1, -1], range= 1, can_kill= True),
                        Move([0, -1], range= 1, can_kill= True),
                        Move([0, 1], range= 1, can_kill= True),
                        Move([-1,0], range= 1, can_kill= True),
                        Move([1, 0], range= 1, can_kill= True)]

class Ghost:
    def __init__(self, board_index, parent):
        self.parent = parent
        self.color = parent.color
        self.board_index = board_index
        self.health = 2
        self.moveset = []
        self.type = "ghost"
    def render(self, display):
        pass
    def get_board_index(self):
        return self.board_index
    def update(self):
        self.health -= 1
    def clone(self):
        return copy.copy(self)