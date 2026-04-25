import pygame
from pices import Piece, Pawn, Rook, Knight, Bishop, King, Queen, Ghost

import math
#
#PYGAME SETUP
#
WIDTH = 800
HEIGHT = 800

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

pygame.init()
#
#GLOBAL VARIABLE
#
selected_piece = None
selected_piece_moves = []
pieces = []
ghosts = []
check_pieces = []
current_turn = "white"
move_counter = 0


white_king = None
black_king = None
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
    color = (0, 0, 0)
    for i in range(len(board["gridd"])):
        x = (i % board_size) * square_size + render_offset[0]
        y = (i // board_size) * square_size + render_offset[1]
        w = 255 * ((i + (i // board_size) % 2) % 2)
        color = (w, w, w)
        if selected_piece != None:
            if selected_piece == board["gridd"][i]:
                color = (100, 155, 100)
            for move in selected_piece_moves:
                if i == move[0]:
                    if move[1]:
                        color = (155, 100, 100)
                    else:
                        color = (255, 255, 0)
        if board["gridd"][i] in check_pieces:
            color = (255, 255, 0)
        draw_square(display, (x, y), square_size, color)
def render_pieces(display, piece_list):
    for piece in piece_list:
        piece.render(display)

def load_piece_image(path, board):
    square_size = board["square size"]

    path = "images/" + path
    image = pygame.image.load(path)
    image = pygame.transform.scale(image, (square_size, square_size))
    image.set_colorkey((0, 0, 0))
    return image

def place_piece(piece: Piece, board, pos):
    board_size = board["size"]
    square_size = board["square size"]
    render_offset = board["render offset"]
    gridd = board["gridd"]
    if piece in gridd:
        gridd[piece.get_board_index()] = None
    pos_index = int(pos[0] + pos[1] * board_size)
    gridd[pos_index] = piece
    piece.set_pos((pos[0] * square_size + render_offset[0], pos[1] * square_size + render_offset[1]))

def place_piece_from_index(board, piece, index):
    board_size = board["size"]
    place_piece(piece, board, [index % board_size, index // board_size])

def get_pressed_pieces(piece_list):
    mpos = pygame.mouse.get_pos()
    
    for piece in piece_list:
        if piece.type == "ghost" or piece.color != current_turn:
            continue
        rect = piece.get_rect()
        if piece.get_rect().collidepoint(mpos):
            return piece
def get_square_from_pos(board, pos):
    board_size = board["size"]
    square_size = board["square size"]
    render_offset = board["render offset"]
    return (pos[0] - render_offset[0]) // square_size + ((pos[1] - render_offset[1]) // square_size * board_size)

"""
#   Returnerar en lista med alla möjliga moves en spelpjäs kan göra
#   den returnerar en lista med par med en int och en bool [move index, har dödat]
"""
def get_possible_moves(board, piece: Piece):
    board_size = board["size"]
    square_size = board["square size"]
    render_offset = board["render offset"]
    gridd = board["gridd"]
    moves = []
    move_direction = -1 if piece.color == "white" else 1
    
    for move in piece.moveset:
        new_index = piece.get_board_index()
        for i in range(move.range):
            
            
            xPos = new_index % board_size + move.vector[0]
            yPos = new_index // board_size + move.vector[1] * move_direction
            
            if xPos < 0 or xPos >= board_size:
                break
            if yPos < 0 or yPos >= board_size:
                break
            
            new_index = new_index + move.vector[0] + move.vector[1] * board_size * move_direction
            
            if gridd[new_index] == None:
                if move.kill_only:
                    break
                moves.append([new_index, False])
            else:
                obstructing_piece: Piece = gridd[new_index]
                if obstructing_piece.type == "ghost" and piece.type != "pawn":
                    moves.append([new_index, False])
                    continue
                if move.can_kill:
                    if obstructing_piece.color == piece.color:
                        break
                    moves.append([new_index, True])
                    break

    return moves

def execute_move(board, piece: Piece, move, pieces):
    
    special = piece.on_move_code(move) #kan vara void
    piece_index = piece.get_board_index()
    if special == "spawn ghost":
        idx = piece_index + (move[0] - piece_index) // 2
        ghost = Ghost(idx, piece)
        ghosts.append(ghost)
        pieces.append(ghost)
        board["gridd"][idx] = ghost

    gridd = board["gridd"]
    gridd[piece_index] = None

    if gridd[move[0]] != None:
        if gridd[move[0]].type == "ghost":
            if gridd[move[0]].color != piece.color and piece.type == "pawn":
                pieces.remove(gridd[move[0]].parent)
        else:
            pieces.remove(gridd[move[0]])
        


    gridd[move[0]] = piece
    place_piece_from_index(board, piece, move[0])
    if move[1]:
        print("You killed a little guy!")

def choose_move(board, piece):
    global move_counter
    mpos = pygame.mouse.get_pos()
    possible_moves = get_possible_moves(board, piece)
    target_pos = get_square_from_pos(board, mpos)
    for move in possible_moves:
        if move[0] == target_pos:
            execute_move(board, piece, move, pieces)
            return "move executed"
    return "no execute"

def get_all_thretening_pieces(piece: Piece, pieces: list[Piece], board):
    piece_index = piece.get_board_index()
    all_thretening_pieces = [] #en lista med par
    for other_piece in pieces:
        if other_piece.color == piece.color:
            continue
        moves = get_possible_moves(board, other_piece)
        for move in moves:
            if move[0] == piece_index and move[1]:
                all_thretening_pieces.append(other_piece)
                continue
    return all_thretening_pieces


def simulate_moves(board, piece_index, pieces):
    global white_king
    global black_king
    black_king_idx = black_king.get_board_index()
    white_king_idx = white_king.get_board_index()
    pieces_clone = pieces.copy()
    board_clone = board.copy()
    piece = board_clone["gridd"][piece_index]
    moves = get_possible_moves(board, piece)
    result_data = [] #en lista med listor som säger om 
    for move in moves:
        data = {"white king in check": False, "black king in chek": False, "move": move}
        board_clone = board.copy()
        
        execute_move(board_clone, piece, move, pieces_clone)
        threats_to_black_king = get_all_thretening_pieces(board_clone["gridd"][black_king_idx], pieces_clone, board_clone)
        threats_to_white_king = get_all_thretening_pieces(board_clone["gridd"][white_king_idx], pieces_clone, board_clone)

        data["white king in check"] = len(threats_to_white_king) > 0
        data["black king in check"] = len(threats_to_black_king) > 0
        result_data.append(data)
    return result_data


        

#
#SETUP FUNCTION
#
size = 8
main_board = mk_board(size)

images = {"white pawn": load_piece_image("bonne.png", main_board),
          "black pawn": load_piece_image("bonne2.png", main_board),
          "white rook": load_piece_image("rook.png", main_board),
          "black rook": load_piece_image("rook2.png", main_board),
          "white knight": load_piece_image("horce.png", main_board),
          "black knight": load_piece_image("horce2.png", main_board),
          "white bishop": load_piece_image("bishop.png", main_board),
          "black bishop": load_piece_image("bishop2.png", main_board),
          "white queen": load_piece_image("queen.png", main_board),
          "black queen": load_piece_image("queen2.png", main_board),
          "white king": load_piece_image("king.png", main_board),
          "black king": load_piece_image("king2.png", main_board)}



def place_pieces_normaly(board):
    global white_king
    global black_king
    for i in range(8):
        w_pawn = Pawn(board, images, "white")
        b_pawn = Pawn(board, images, "black")
        place_piece(b_pawn, board, (i, 1))
        place_piece(w_pawn, board, (i, 6))
        pieces.append(b_pawn)
        pieces.append(w_pawn)
    
    b_rook1 = Rook(board, images, "black")
    b_rook2 = Rook(board, images, "black")
    b_knight1 = Knight(board, images, "black")
    b_knight2 = Knight(board, images, "black")
    b_bishop1 = Bishop(board, images, "black")
    b_bishop2 = Bishop(board, images, "black")
    b_king = King(board, images, "black")
    b_queen = Queen(board, images, "black")
    place_piece(b_rook1, board, (0, 0))
    place_piece(b_knight1, board, (1, 0))
    place_piece(b_bishop1, board, (2, 0))
    place_piece(b_queen, board, (3, 0))
    place_piece(b_king, board, (4, 0))
    place_piece(b_bishop2, board, (5, 0))
    place_piece(b_knight2, board, (6, 0))
    place_piece(b_rook2, board, (7, 0))
    pieces.append(b_rook1)
    pieces.append(b_knight1)
    pieces.append(b_bishop1)
    pieces.append(b_queen)
    pieces.append(b_king)
    pieces.append(b_bishop2)
    pieces.append(b_knight2)
    pieces.append(b_rook2)

    w_rook1 = Rook(board, images, "white")
    w_rook2 = Rook(board, images, "white")
    w_knight1 = Knight(board, images, "white")
    w_knight2 = Knight(board, images, "white")
    w_bishop1 = Bishop(board, images, "white")
    w_bishop2 = Bishop(board, images, "white")
    w_king = King(board, images, "white")
    w_queen = Queen(board, images, "white")
    place_piece(w_rook1, board, (0, 7))
    place_piece(w_knight1, board, (1, 7))
    place_piece(w_bishop1, board, (2, 7))
    place_piece(w_queen, board, (3, 7))
    place_piece(w_king, board, (4, 7))
    place_piece(w_bishop2, board, (5, 7))
    place_piece(w_knight2, board, (6, 7))
    place_piece(w_rook2, board, (7, 7))
    pieces.append(w_rook1)
    pieces.append(w_knight1)
    pieces.append(w_bishop1)
    pieces.append(w_queen)
    pieces.append(w_king)
    pieces.append(w_bishop2)
    pieces.append(w_knight2)
    pieces.append(w_rook2)

    white_king = w_king
    black_king = b_king
place_pieces_normaly(main_board)
#
#GAME LOOP
#

move_executed = "no"
while True:
    if move_executed == "move executed":
        move_counter += 1
        for ghost in ghosts.copy():
            ghost.update()
            if ghost.health < 1:
                ghosts.remove(ghost)
                if main_board["gridd"][ghost.board_index] == ghost:
                    main_board["gridd"][ghost.board_index] = None 
    
        move_executed = "no"
        current_turn = "white" if move_counter % 2 == 0 else "black"
        
        check_pieces.clear()
        if current_turn == "white":
            check_pieces = get_all_thretening_pieces(white_king, pieces, main_board)
            if len(check_pieces) > 0:
                check_pieces.append(white_king)
        if current_turn == "black":
            check_pieces = get_all_thretening_pieces(black_king, pieces, main_board)
            if len(check_pieces) > 0:
                check_pieces.append(black_king)
        print(check_pieces)
    window.fill((255, 255, 255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            pressed_piece = get_pressed_pieces(pieces)
            
            if len(check_pieces) > 0 and pressed_piece.type != "king":
                simulated_move_data = simulate_moves(main_board, pressed_piece.get_board_index(), pieces)
                for move_data in simulated_move_data:
                    if move_data["white king in check"] or move_data["black king in check"]:
                        continue
                    else:
                        selected_piece_moves.append(move_data["move"])
                print("your king is in danger!!")
            
            
            if not selected_piece:
                selected_piece = pressed_piece
                if selected_piece:
                    selected_piece_moves = get_possible_moves(main_board, selected_piece)
            else:
                move_executed = choose_move(main_board, selected_piece)
                selected_piece = None
                selected_piece_moves = []

    render_board(window, main_board)
    render_pieces(window, pieces)

    pygame.display.update()
    clock.tick(60)