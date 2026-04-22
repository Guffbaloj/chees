import pygame
from pices import Piece
import math
#
#PYGAME SETUP
#
WIDTH = 1200
HEIGHT = 80

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.init()
#
#FUNCTIONS
#
def draw_square(display, pos, size, color):
    rect = pygame.rect.Rect(pos[0], pos[1], size, size)
    pygame.draw.rect(display, color, rect)

def mk_board(size):
    gridd = []
    for i in range(size * size):
        gridd.append(None)
    
    square_size = min(WIDTH, HEIGHT) // size
    render_offset = ((WIDTH - size * square_size)// 2, (HEIGHT - size * square_size) // 2)
    board = {"gridd": gridd, "size": size, "square size": square_size, "render offset": render_offset}
    return board

def render_board(display, board):
    board_size = board["size"]
    square_size = board["square size"]
    render_offset = board["render offset"]
    for i in range(len(board["gridd"])):
        x = (i % board_size) * square_size + render_offset[0]
        y = (i // board_size) * square_size + render_offset[1]
        w = 255 * ((i + (i // board_size) % 2) % 2)
        draw_square(display, (x, y), square_size, (w, w, w))

def load_piece_image(path, board):
    square_size = board["square size"]

    path = "images/" + path
    image = pygame.image.load(path)
    image = pygame.transform.scale(image, (square_size, square_size))
    image.set_colorkey((0, 0, 0))
    return image

def place_piece(piece, board, pos):
    board_size = math.sqrt(len(board))
    square_size = min(WIDTH, HEIGHT) // board_size
    if piece in board:
        board.remove(piece)
    pos_index = int(pos[0] + pos[1] * board_size)
    board[pos_index] = piece
    piece.set_pos((pos[0] * square_size, pos[1] * square_size))


#
#GAME LOOP
#
size = 8
main_board = mk_board(size)
images = {"pawn": load_piece_image("bonne.png", main_board)}

pawn1 = Piece(main_board, "pawn", images)
place_piece(pawn1, main_board, (0, 1))
while True:
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
    render_board(window, main_board)
    pawn1.render(window)

    pygame.display.update()
    clock.tick(60)