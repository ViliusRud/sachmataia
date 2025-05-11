import unittest
from Two_player_chess import Board, Pawn, Queen, Rook, Bishop, Knight, King


class TestChessPieces(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_pawn_promotion(self):
        for i in range(8):
            for j in range(8):
                self.board.grid[i][j] = None

        self.board.grid[1][0] = Pawn('white', (1, 0))
        self.board.current_turn = 'white'  # Ensure it's white's turn

        self.board.select_piece((1, 0))
        move_result = self.board.move_piece((0, 0))  # Move to promotion square

        self.assertTrue(move_result, "Pawn movement failed")

        self.assertIsNotNone(self.board.promoting_pawn, "Pawn not ready for promotion")

        promotion_result = self.board.promote_pawn('queen')
        self.assertTrue(promotion_result, "Promotion failed")

        promoted_piece = self.board.grid[0][0]
        self.assertIsNotNone(promoted_piece, "No piece at promotion square")
        self.assertIsInstance(promoted_piece, Queen, "Piece not promoted to Queen")
        self.assertEqual(promoted_piece.color, 'white', "Promoted piece has wrong color")
        self.assertEqual(promoted_piece.position, (0, 0), "Promoted piece at wrong position")

        self.assertEqual(self.board.current_turn, 'black', "Turn not changed after promotion")

    def test_promoted_queen_movement(self):
        for i in range(8):
            for j in range(8):
                self.board.grid[i][j] = None

        self.board.grid[1][0] = Pawn('white', (1, 0))
        self.board.current_turn = 'white'

        self.board.select_piece((1, 0))
        self.board.move_piece((0, 0))
        self.board.promote_pawn('queen')

        self.board.current_turn = 'white'

        self.board.select_piece((0, 0))
        valid_moves = self.board.valid_moves

        expected_moves = [
            (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),  # Vertical
            (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7),  # Horizontal
            (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)  # Diagonal
        ]

        for move in expected_moves:
            self.assertIn(move, valid_moves, f"Queen should be able to move to {move}")

    def test_promoted_rook(self):
        self.board = Board()
        for i in range(8):
            for j in range(8):
                self.board.grid[i][j] = None

        self.board.grid[1][0] = Pawn('white', (1, 0))
        self.board.current_turn = 'white'
        self.board.select_piece((1, 0))
        self.board.move_piece((0, 0))
        self.board.promote_pawn('rook')

        promoted_piece = self.board.grid[0][0]
        self.assertIsInstance(promoted_piece, Rook, "Piece not promoted to Rook")


if __name__ == '__main__':
    unittest.main()
