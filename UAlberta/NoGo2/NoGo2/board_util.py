EMPTY = 0
BLACK = 1
WHITE = 2
BORDER = 3
FLOODFILL = 4
import numpy as np

class GoBoardUtil(object):

    @staticmethod
    def generate_legal_moves(board, color):
        """
        generate a list of legal moves

        Arguments
        ---------
        board : np.array
            a SIZExSIZE array representing the board
        color : {'b','w'}
            the color to generate the move for.
        """
        moves = board.get_empty_positions(color)
        num_moves = len(moves)
        np.random.shuffle(moves)
        illegal_moves = []

        for i in range(num_moves):
            if board.check_legal(moves[i], color):
                continue
            else:
                illegal_moves.append(i)
        legal_moves = np.delete(moves, illegal_moves)
        gtp_moves = []
        for point in legal_moves:
            x, y = board._point_to_coord(point)
            gtp_moves.append(GoBoardUtil.format_point((x, y)))
        sorted_moves = ' '.join(sorted(gtp_moves))
        return sorted_moves
            
    @staticmethod       
    def generate_random_move(board, color):
        """
        generate a random move, or 'None' if game is over

        Arguments
        ---------
        board : np.array
            a SIZExSIZE array representing the board
        color : {'b','w'}
            the color to generate the move for.
        """
        moves = board.get_empty_positions(color)
        num_moves = len(moves)
        np.random.shuffle(moves)
        move = None
        for i in range(num_moves):
            if board.check_legal(moves[i], color):
                move = moves[i]        
        return move
    
    @staticmethod
    def format_point(move):
        """
        Return coordinates as a string like 'a1', or 'pass'.

        Arguments
        ---------
        move : (row, col), or None for pass

        Returns
        -------
        The move converted from a tuple to a Go position (e.g. d4)
        """
        column_letters = "abcdefghjklmnopqrstuvwxyz"
        if move is None:
            return "pass"
        row, col = move
        if not 0 <= row < 25 or not 0 <= col < 25:
            raise ValueError
        return    column_letters[col - 1] + str(row) 
        
    @staticmethod
    def move_to_coord(point, board_size):
        """
        Interpret a string representing a point, as specified by GTP.

        Arguments
        ---------
        point : str
            the point to convert to a tuple
        board_size : int
            size of the board

        Returns
        -------
        a pair of coordinates (row, col) in range(1, board_size+1)

        Raises
        ------
        ValueError : 'point' isn't a valid GTP point specification for a board of size 'board_size'.
        """
        if not 0 < board_size <= 25:
            raise ValueError("board_size out of range")
        try:
            s = point.lower()
        except Exception:
            raise ValueError("invalid point")
        if s == "pass":
            raise ValueError("wrong coordinate")
        try:
            col_c = s[0]
            if (not "a" <= col_c <= "z") or col_c == "i":
                raise ValueError
            if col_c > "i":
                col = ord(col_c) - ord("a")
            else:
                col = ord(col_c) - ord("a") + 1
            row = int(s[1:])
            if row < 1:
                raise ValueError
        except (IndexError, ValueError):
            raise ValueError("wrong coordinate")
        if not (col <= board_size and row <= board_size):
            raise ValueError("wrong coordinate")
        return row, col
    
    @staticmethod
    def opponent(color):
        return WHITE + BLACK - color    
            
    @staticmethod
    def color_to_int(c):
        """convert character representing player color to the appropriate number"""
        color_to_int = {"b": BLACK , "w": WHITE, "e":EMPTY, "BORDER":BORDER, "FLOODFILL":FLOODFILL}
        try:
           return color_to_int[c] 
        except:
            raise ValueError("wrong color")
    
    @staticmethod
    def int_to_color(i):
        """convert number representing player color to the appropriate character """
        int_to_color = {BLACK:"b", WHITE:"w", EMPTY:"e", BORDER:"BORDER", FLOODFILL:"FLOODFILL"}
        try:
           return int_to_color[i] 
        except:
            raise ValueError("Provided integer value for color is invalid")
         
    @staticmethod
    def copyb2b(board, copy_board):
        """Return an independent copy of this Board."""
        copy_board.board = np.copy(board.board)
        copy_board.suicide = board.suicide  # checking for suicide move
        copy_board.winner = board.winner 
        copy_board.NS = board.NS
        copy_board.WE = board.WE
        copy_board._is_empty = board._is_empty
        copy_board.passes_black = board.passes_black
        copy_board.passes_white = board.passes_white
        copy_board.to_play = board.to_play
        copy_board.white_captures = board.white_captures
        copy_board.black_captures = board.black_captures 

    # Save time of transforming
    def generate_legal_moves_fast(board, color):
        """
        generate a list of legal moves

        Arguments
        ---------
        board : np.array
            a SIZExSIZE array representing the board
        color : {'b','w'}
            the color to generate the move for.
        """
        moves = board.get_empty_positions(color)
        num_moves = len(moves)
        np.random.shuffle(moves)

        illegal_moves = []
        for i in range(num_moves):
            if board.check_legal(moves[i], color):
                continue
            else:
                illegal_moves.append(i)
        legal_moves = np.delete(moves, illegal_moves)
        return sorted(legal_moves)


