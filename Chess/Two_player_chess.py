import pygame
import sys
from pygame.locals import *
from abc import ABC, abstractmethod
import os

pygame.init()

WINDOW_SIZE = (800, 800)
BOARD_SIZE = 8
SQUARE_SIZE = 800 // BOARD_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (247, 247, 105, 150)
MOVE_HIGHLIGHT = (106, 168, 79, 150)
CHECK_HIGHLIGHT = (255, 0, 0, 150)
FONT_SIZE = 32
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption('Two-Player Chess')
font = pygame.font.SysFont('Arial', FONT_SIZE)
IMAGES = {}


def load_images():
    images = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR',
              'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR',
              'bp', 'wp']
    print(f"Current working directory: {os.getcwd()}")
    print(f"Looking for images in: {os.path.join(os.getcwd(), 'images')}")

    for piece in images:
        try:
            image_path = os.path.join("images", f"{piece}.png")
            print(f"Trying to load: {image_path}")
            image = pygame.image.load(image_path)
            IMAGES[piece] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            print(f"Successfully loaded {piece}")
        except Exception as e:
            print(f"Error loading {piece}: {str(e)}")


load_images()


def draw_pieces(screen, board):
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "--":
                piece_surface = IMAGES.get(piece)
                if piece_surface:
                    piece_rect = piece_surface.get_rect()
                    piece_rect.center = (col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                         row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    screen.blit(piece_surface, piece_rect)


def draw_board(screen):
    colors = [pygame.Color("white"), pygame.Color("gray")]
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))


class Piece(ABC):
    def __init__(self, color, position):
        self.color = color
        self.position = position
        self.has_moved = False

        color_code = 'w' if color == 'white' else 'b'
        self.image_key = f"{color_code}{self.symbol}"

    def __str__(self):
        return f"{self.color[0]}{self.symbol}"

    def draw(self, screen):
        if self.image_key in IMAGES:
            image = IMAGES[self.image_key]
            x = self.position[1] * SQUARE_SIZE
            y = self.position[0] * SQUARE_SIZE
            piece_rect = image.get_rect()
            piece_rect.topleft = (x, y)
            screen.blit(image, piece_rect)
        else:
            print(f"Warning: Image not found for {self.image_key}")

    @abstractmethod
    def valid_moves(self, board):
        raise NotImplementedError("Subclasses must implement this method")

    def move(self, new_position, board):
        valid_moves = self.valid_moves(board)
        if new_position in valid_moves:
            self.position = new_position
            self.has_moved = True
            return True
        return False


class Pawn(Piece):
    symbol = 'p'

    def valid_moves(self, board):
        moves = []
        direction = 1 if self.color == 'black' else -1
        start_row = 1 if self.color == 'black' else 6

        forward = (self.position[0] + direction, self.position[1])
        if 0 <= forward[0] < 8 and board.get_piece(forward) is None:
            moves.append(forward)

            if self.position[0] == start_row:
                double_forward = (self.position[0] + 2 * direction, self.position[1])
                if board.get_piece(double_forward) is None:
                    moves.append(double_forward)

        for col_offset in [-1, 1]:
            capture_pos = (self.position[0] + direction, self.position[1] + col_offset)
            if 0 <= capture_pos[1] < 8:
                piece = board.get_piece(capture_pos)
                if piece is not None and piece.color != self.color:
                    moves.append(capture_pos)
                elif piece is None and board.en_passant_target == capture_pos:
                    adjacent_pos = (self.position[0], self.position[1] + col_offset)
                    adjacent_piece = board.get_piece(adjacent_pos)
                    if (adjacent_piece is not None and isinstance(adjacent_piece, Pawn) and
                            adjacent_piece.color != self.color):
                        moves.append(capture_pos)

        return moves

    def get_symbol(self):
        return 'b' if self.color == 'black' else 'w'


class Rook(Piece):
    symbol = 'R'

    def valid_moves(self, board):
        moves = []
        row, col = self.position
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    piece = board.get_piece((new_row, new_col))
                    if piece is None:
                        moves.append((new_row, new_col))
                    else:
                        if piece.color != self.color:
                            moves.append((new_row, new_col))
                        break
                else:
                    break
        return moves

    def get_symbol(self):
        return 'b' if self.color == 'black' else 'w'


class Knight(Piece):
    symbol = 'N'

    def valid_moves(self, board):
        moves = []
        row, col = self.position

        offsets = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        for dr, dc in offsets:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                piece = board.get_piece((new_row, new_col))
                if piece is None or piece.color != self.color:
                    moves.append((new_row, new_col))
        return moves

    def get_symbol(self):
        return 'b' if self.color == 'black' else 'w'


class Bishop(Piece):
    symbol = 'B'

    def valid_moves(self, board):
        moves = []
        row, col = self.position

        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    piece = board.get_piece((new_row, new_col))
                    if piece is None:
                        moves.append((new_row, new_col))
                    else:
                        if piece.color != self.color:
                            moves.append((new_row, new_col))
                        break
                else:
                    break
        return moves

    def get_symbol(self):
        return 'b' if self.color == 'black' else 'w'


class Queen(Piece):
    symbol = 'Q'

    def valid_moves(self, board):
        moves = []
        row, col = self.position

        directions = [
            (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        for dr, dc in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * dr, col + i * dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    piece = board.get_piece((new_row, new_col))
                    if piece is None:
                        moves.append((new_row, new_col))
                    else:
                        if piece.color != self.color:
                            moves.append((new_row, new_col))
                        break
                else:
                    break
        return moves

    def get_symbol(self):
        return 'b' if self.color == 'black' else 'w'


class King(Piece):
    symbol = 'K'

    def valid_moves(self, board, check_check=True):
        moves = []
        row, col = self.position

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    piece = board.get_piece((new_row, new_col))
                    if piece is None or piece.color != self.color:
                        moves.append((new_row, new_col))

        if check_check and not self.has_moved and not board.is_in_check(self.color):
            if (board.get_piece((row, 5)) is None and
                    board.get_piece((row, 6)) is None and
                    isinstance(board.get_piece((row, 7)), Rook) and
                    not board.get_piece((row, 7)).has_moved):
                if (not board.is_square_under_attack((row, 5), self.color) and
                        not board.is_square_under_attack((row, 6), self.color)):
                    moves.append((row, 6))

            if (board.get_piece((row, 1)) is None and
                    board.get_piece((row, 2)) is None and
                    board.get_piece((row, 3)) is None and
                    isinstance(board.get_piece((row, 0)), Rook) and
                    not board.get_piece((row, 0)).has_moved):
                if (not board.is_square_under_attack((row, 2), self.color) and
                        not board.is_square_under_attack((row, 3), self.color)):
                    moves.append((row, 2))

        return moves

    def get_symbol(self):
        return 'b' if self.color == 'black' else 'w'


class PieceFactory(ABC):
    @abstractmethod
    def create_piece(self, color, position):
        pass


class PawnFactory(PieceFactory):
    def create_piece(self, color, position):
        return Pawn(color, position)


class RookFactory(PieceFactory):
    def create_piece(self, color, position):
        return Rook(color, position)


class KnightFactory(PieceFactory):
    def create_piece(self, color, position):
        return Knight(color, position)


class BishopFactory(PieceFactory):
    def create_piece(self, color, position):
        return Bishop(color, position)


class QueenFactory(PieceFactory):
    def create_piece(self, color, position):
        return Queen(color, position)


class KingFactory(PieceFactory):
    def create_piece(self, color, position):
        return King(color, position)


class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.current_turn = 'white'
        self.game_over = False
        self.winner = None
        self.selected_piece = None
        self.valid_moves = []
        self.en_passant_target = None
        self.check = False
        self.promoting_pawn = None
        self.piece_factories = {
            'pawn': PawnFactory(),
            'rook': RookFactory(),
            'knight': KnightFactory(),
            'bishop': BishopFactory(),
            'queen': QueenFactory(),
            'king': KingFactory()
        }
        self._setup_board()

    def _setup_board(self):
        for col in range(8):
            self.grid[6][col] = self.piece_factories['pawn'].create_piece('white', (6, col))
            self.grid[1][col] = self.piece_factories['pawn'].create_piece('black', (1, col))

            self.grid[0][0] = self.piece_factories['rook'].create_piece('black', (0, 0))
            self.grid[0][7] = self.piece_factories['rook'].create_piece('black', (0, 7))
            self.grid[7][0] = self.piece_factories['rook'].create_piece('white', (7, 0))
            self.grid[7][7] = self.piece_factories['rook'].create_piece('white', (7, 7))

            self.grid[0][1] = Knight('black', (0, 1))
            self.grid[0][6] = Knight('black', (0, 6))
            self.grid[7][1] = Knight('white', (7, 1))
            self.grid[7][6] = Knight('white', (7, 6))

            self.grid[0][2] = Bishop('black', (0, 2))
            self.grid[0][5] = Bishop('black', (0, 5))
            self.grid[7][2] = Bishop('white', (7, 2))
            self.grid[7][5] = Bishop('white', (7, 5))

            self.grid[0][3] = Queen('black', (0, 3))
            self.grid[7][3] = Queen('white', (7, 3))

            self.grid[0][4] = King('black', (0, 4))
            self.grid[7][4] = King('white', (7, 4))

    def get_piece(self, position):
        row, col = position
        if 0 <= row < 8 and 0 <= col < 8:
            return self.grid[row][col]
        return None

    def is_square_under_attack(self, position, color):
        opponent_color = 'black' if color == 'white' else 'white'
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == opponent_color:
                    if isinstance(piece, King):
                        if position in piece.valid_moves(self, check_check=False):
                            return True
                    else:
                        if position in piece.valid_moves(self):
                            return True
        return False

    def is_in_check(self, color):
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        if not king_pos:
            return False
        return self.is_square_under_attack(king_pos, color)

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    for move in piece.valid_moves(self):
                        original_pos = piece.position
                        captured_piece = self.get_piece(move)
                        self.grid[original_pos[0]][original_pos[1]] = None
                        self.grid[move[0]][move[1]] = piece
                        piece.position = move
                        still_in_check = self.is_in_check(color)
                        self.grid[original_pos[0]][original_pos[1]] = piece
                        self.grid[move[0]][move[1]] = captured_piece
                        piece.position = original_pos
                        if not still_in_check:
                            return False
        return True

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if piece and piece.color == color:
                    if piece.valid_moves(self):
                        return False
        return True

    def select_piece(self, position):
        piece = self.get_piece(position)
        if piece is not None and piece.color == self.current_turn:
            print(f"Selected {piece} at {position}. Possible moves (before filtering): {piece.valid_moves(self)}")
            self.selected_piece = piece
            self.valid_moves = piece.valid_moves(self)
            valid_moves_filtered = []
            for move in self.valid_moves:
                original_pos = piece.position
                captured_piece = self.get_piece(move)
                self.grid[original_pos[0]][original_pos[1]] = None
                self.grid[move[0]][move[1]] = piece
                piece.position = move
                if not self.is_in_check(self.current_turn):
                    valid_moves_filtered.append(move)
                self.grid[original_pos[0]][original_pos[1]] = piece
                self.grid[move[0]][move[1]] = captured_piece
                piece.position = original_pos
            self.valid_moves = valid_moves_filtered
            return True
        return False

    def move_piece(self, end_pos):
        if self.selected_piece is None:
            return False

        if end_pos in self.valid_moves:
            start_pos = self.selected_piece.position

            if isinstance(self.selected_piece, Pawn) and end_pos == self.en_passant_target:
                captured_row = start_pos[0]
                captured_col = end_pos[1]
                self.grid[captured_row][captured_col] = None

            captured_piece = self.get_piece(end_pos)
            if captured_piece is not None and isinstance(captured_piece, King):
                self.game_over = True
                self.winner = self.current_turn

            if isinstance(self.selected_piece, King) and abs(start_pos[1] - end_pos[1]) == 2:
                if end_pos[1] > start_pos[1]:
                    rook_pos = (start_pos[0], 7)
                    rook = self.get_piece(rook_pos)
                    self.grid[start_pos[0]][5] = rook
                    self.grid[start_pos[0]][7] = None
                    rook.position = (start_pos[0], 5)
                else:
                    rook_pos = (start_pos[0], 0)
                    rook = self.get_piece(rook_pos)
                    self.grid[start_pos[0]][3] = rook
                    self.grid[start_pos[0]][0] = None
                    rook.position = (start_pos[0], 3)

            self.grid[start_pos[0]][start_pos[1]] = None
            self.grid[end_pos[0]][end_pos[1]] = self.selected_piece
            self.selected_piece.position = end_pos
            self.selected_piece.has_moved = True

            if isinstance(self.selected_piece, Pawn) and (end_pos[0] == 0 or end_pos[0] == 7):
                self.promoting_pawn = self.selected_piece
                return True

            if isinstance(self.selected_piece, Pawn) and abs(start_pos[0] - end_pos[0]) == 2:
                self.en_passant_target = (start_pos[0] + (end_pos[0] - start_pos[0]) // 2, start_pos[1])
            else:
                self.en_passant_target = None

            if not self.promoting_pawn:
                self.current_turn = 'black' if self.current_turn == 'white' else 'white'

            self.selected_piece = None
            self.valid_moves = []

            if self.is_checkmate(self.current_turn):
                self.game_over = True
                self.winner = 'white' if self.current_turn == 'black' else 'black'
            elif self.is_stalemate(self.current_turn):
                self.game_over = True
                self.winner = None

            return True
        return False

    def promote_pawn(self, piece_type):
        if not self.promoting_pawn:
            return False

        pos = self.promoting_pawn.position
        color = self.promoting_pawn.color

        if piece_type == 'queen':
            new_piece = Queen(color, pos)
        elif piece_type == 'rook':
            new_piece = Rook(color, pos)
        elif piece_type == 'bishop':
            new_piece = Bishop(color, pos)
        elif piece_type == 'knight':
            new_piece = Knight(color, pos)

        if new_piece:
            new_piece.position = pos
            new_piece.has_moved = True
            self.grid[pos[0]][pos[1]] = new_piece
            self.valid_moves = new_piece.valid_moves(self)

        self.promoting_pawn = None
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

        if self.is_checkmate(self.current_turn):
            self.game_over = True
            self.winner = 'white' if self.current_turn == 'black' else 'black'
        elif self.is_stalemate(self.current_turn):
            self.game_over = True
            self.winner = None

        return True

    def draw(self, surface):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(surface, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

                if self.selected_piece and (row, col) == self.selected_piece.position:
                    highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(HIGHLIGHT)
                    surface.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                elif (row, col) in self.valid_moves:
                    highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(MOVE_HIGHLIGHT)
                    surface.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.grid[row][col]
                if isinstance(piece, King) and piece.color == self.current_turn and self.is_in_check(self.current_turn):
                    highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(CHECK_HIGHLIGHT)
                    surface.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.grid[row][col]
                if piece:
                    piece.draw(surface)

        turn_text = f"{self.current_turn.capitalize()}'s turn"
        text_surface = font.render(turn_text, True, BLACK)
        surface.blit(text_surface, (10, 10))

        if self.promoting_pawn:
            options = ['queen', 'rook', 'bishop', 'knight']
            for i, option in enumerate(options):
                pygame.draw.rect(surface, WHITE,
                                 (i * SQUARE_SIZE, WINDOW_SIZE[1] - SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                text = font.render(option[0].upper(), True, BLACK)
                text_rect = text.get_rect(
                    center=(i * SQUARE_SIZE + SQUARE_SIZE // 2, WINDOW_SIZE[1] - SQUARE_SIZE // 2))
                surface.blit(text, text_rect)

        if self.game_over:
            if self.winner:
                game_over_text = f"Game Over! {self.winner.capitalize()} wins!"
            else:
                game_over_text = "Game Over! Stalemate - it's a draw!"
            text_surface = font.render(game_over_text, True, (255, 0, 0))
            text_rect = text_surface.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            pygame.draw.rect(surface, WHITE, text_rect.inflate(20, 20))
            surface.blit(text_surface, text_rect)


class ChessGame:
    def __init__(self):
        self.board = Board()

    def handle_click(self, position):
        row, col = position

        if self.board.promoting_pawn:
            if row == BOARD_SIZE - 1 and col < 4:
                piece_types = ['queen', 'rook', 'bishop', 'knight']
                selected_type = piece_types[col]
                self.board.promote_pawn(selected_type)
                return

        elif self.board.selected_piece:
            move_made = self.board.move_piece(position)
            if not move_made:
                self.board.select_piece(position)
        else:
            self.board.select_piece(position)

    def run(self):
        """Main game loop."""
        running = True
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        col = pos[0] // SQUARE_SIZE
                        row = pos[1] // SQUARE_SIZE
                        self.handle_click((row, col))

            screen.fill(WHITE)
            draw_board(screen)
            self.board.draw(screen)
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = ChessGame()
    game.run()
