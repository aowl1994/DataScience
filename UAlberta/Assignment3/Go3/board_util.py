EMPTY = 0
BLACK = 1
WHITE = 2
BORDER = 3
FLOODFILL = 4
import numpy as np
import sys
import random

class GoBoardUtil(object):
    
    @staticmethod       
    def playGame(board, color, **kwargs):
        komi = kwargs.pop('komi', 0)
        limit = kwargs.pop('limit', 1000)
        if kwargs:
            raise TypeError('Unexpected **kwargs: %r' % kwargs)
        numPass = 0
        for i in range(limit):
            if numPass == 2:
                break
            move = GoBoardUtil.generate_random_move(board, color)
            if move != None:
                if not (board.move(move,color)):
                    raise ValueError("Move given by GoBoardUtil is not valid!")
                numPass = 0
                # reseting number of pass variable
            else:
                board.move(move,color)
                numPass += 1
            color = GoBoardUtil.opponent(color)
        winner = board.get_winner(komi)
        return winner
    
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
        moves = board.get_empty_points()
        num_moves = len(moves)
        legal_moves = []
        for move in legal_moves:
            if board.check_legal(move, color):
                legal_moves.append(i)
        return legal_moves

    @staticmethod
    def generate_legal_moves_as_string(board, color):
        legal_moves = generate_legal_moves(board, color)
        gtp_moves = []
        for point in legal_moves:
            x, y = board._point_to_coord(point)
            gtp_moves.append(GoBoardUtil.format_point((x, y)))
        sorted_moves = ' '.join(sorted(gtp_moves))
        return sorted_moves

    @staticmethod
    def generate_random_move(board, color):
        moves = board.get_empty_points()
        while len(moves) > 0:
            index = random.randint(0,len(moves) - 1)
            move = moves[index]
            if board.check_legal(move, color) and not board.is_eye(move, color):
                return move
            else:
                # delete
                lastIndex = len(moves) - 1
                if index < lastIndex:
                    moves[index] = moves[lastIndex]
                moves.pop()
        return None

    @staticmethod
    def filter_moves(board, moves, selfatari):
        color = board.current_player
        good_moves = []
        for move in moves:
            if not GoBoardUtil.filter(board,move,color,selfatari):
                good_moves.append(move)
        return good_moves

    @staticmethod
    def filter(board, move, color, selfatari):
        if board.is_eye(move, color):
            return True
        if selfatari:
            if GoBoardUtil.selfatari(board, move, color):
                return True
        if not board.check_legal(move, color):
            return True
        return False

    @staticmethod 
    def filterMovesAndGenerate(board, moves, color, selfatari):
        candidate = None
        while len(moves) > 0:
            candidate = random.choice(moves)
            if GoBoardUtil.filter(board, candidate, color, selfatari):
                moves.remove(candidate)
            else:
                return candidate
        
    
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
            return None
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
        opponent = {WHITE:BLACK, BLACK:WHITE} 
        try:
            return opponent[color]    
        except:
            raise ValueError("Wrong color provided for opponent function")
            
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
        copy_board.current_player = board.current_player
        copy_board.ko_constraint =  board.ko_constraint 
        copy_board.white_captures = board.white_captures
        copy_board.black_captures = board.black_captures 

        
