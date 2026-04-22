import pygame

class Piece:
    def __init__(self, board, e_type, images):
        self.board = board
        self.type = e_type
        self.pos = (0, 0)
        self.images = images
    def update(self):
        pass  

    def set_pos(self, new_pos):
        self.pos = new_pos

    def render(self, display: pygame.Surface):
        img: pygame.Surface = self.images[self.type]
        rect = img.get_rect()
        display.blit(self.images[self.type], self.pos, rect)

