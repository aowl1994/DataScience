"""
glossary:
    point : int
        coordinate of point on the board
    color : int
        color code of the point represented in interger, imported from board utility
        EMPTY = 0
        BLACK = 1
        WHITE = 2
        BORDER = 3
        FLOODFILL = 4

"""

import numpy as np
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL 

class GoBoard(object):

    def move(self, point, color):
        """
        Play a move on the board.
        Arguments:
            point
        Return:
            color
        """
        move_inspection, msg = self._play_move(point, color)
        if not move_inspection:
            raise ValueError(msg)
            return False
        else:
            self.to_play = GoBoardUtil.opponent(color)
            # Assignment2 - 2.solver
            self.depth += 1
            return True

    @staticmethod
    def showboard(board, bd_size):
        #TODO: would be nice to have a nicer printout of the board
        pass

    def get_color(self, point):
        """
        Return the state of the specified point.
        Arguments:
            point
        Return:
            color
        """
        return self.board[point]

    def check_legal(self, point, color):
        """
        Arguments:
            point, color
        Return:
            bool
            Whether the playing point with the given color is
            legal.
        """
        sboard = np.array(self.board, copy = True)
        # swap out true board for simulation board, and try to play the move
        result, _ = self._play_move(point, color)
        # reset true board; return result
        self.board = sboard
        return result

    def get_winner(self):
        """
        Returns:
        winner: color of winner, if the game is over, or None if not
        """
        if len(GoBoardUtil.generate_legal_moves(self, self.to_play)) == 0:
            return GoBoardUtil.opponent(self.to_play)
        else:
            return None

    def get_twoD_board(self):
        """
        Return: numpy array
        a two dimensional numpy array with same values as in the self.board without having the borders
        """
        board = np.zeros((self.size, self.size), dtype = np.int32)
        for i in range(self.size):
            row = (i+1) * self.NS + 1
            board[i,:] = self.board[row:row + self.size]
        return board

        
    def get_empty_positions(self, color):
        """
        Arguments:
            color
        Return:
            list of empty points 
        """
        moves = []
        for y in range(1, self.size + 1, 1):
            for x in range(1, self.size + 1, 1):
                point = self._coord_to_point(x, y)
                if self.get_color(point) != EMPTY:
                    continue
                moves.append(point)
        return moves


    def __init__(self, size):
        """
        Creates a board that uses 1-dimensional representation of points
        """
        self.reset(size)


    def reset(self, size):
        """
        Create an initial board position, or
        reset the board to a new size

        Arguments
        ---------
        size : int
            size of board to reset to
        """

        self.name = "Board 1D"
        self.version = 0.1
        self.size = size
        self.NS = size + 1
        self.WE = 1
        self.suicide = True # checking for suicide move
        self._is_empty = True
        self.passes_white = 0
        self.passes_black = 0
        self.white_captures = 0
        self.black_captures = 0
        self.to_play = BLACK
        self._empty_positions = {BLACK:[], WHITE:[]}
        self.maxpoint = size * size + 3 * (size + 1)  # zero indexing
        """
        The array is one-dimensional and this representation is 
        achieved through _coord_to_point function.
        Below is an example of point numbering on the 3x3 board 
        (indices of the numpy array).
        Spaces are added for illustration to separate board points 
        from border points.
        There is only one column buffer between rows (e.g. point 12).
        
        16   17 18 19   20

        12   13 14 15   16
        08   09 10 11   12
        04   05 06 07   08

        00   01 02 03   04
        """
        self.board = np.ones(self.maxpoint, dtype = np.int16) * BORDER
        self._empty_filling(self.board)

        # Assignment2 - 2.solve
        self.depth = 0


    def copy(self):
        """Return an independent copy of this board."""
        b = GoBoard(self.size)
        b.board = np.copy(self.board)
        b.suicide = self.suicide
        b.NS = self.NS
        b.WE = self.WE
        b._is_empty = self._is_empty
        b.passes_black = self.passes_black
        b.passes_white = self.passes_white
        b.to_play = self.to_play
        b.white_captures = self.white_captures
        b.black_captures = self.black_captures
        return b


    def _empty_filling(self, board):
        """
        Fills points inside board with EMPTY
        Arguments
        ---------
        board : numpy array
            receives a numpy array filled with BORDER

        """
        for ind in range(1, self.size + 1, 1):
            indices = [j for j in range(ind * self.NS + 1, ind * self.NS + self.size + 1, 1)]
            np.put(board, indices, EMPTY)
        
    """
------------------------------------------------------------------------------
    Helper functions for playing a move
------------------------------------------------------------------------------
    """

    def _liberty(self, point, color):
        """
        ---------
        Return
        ---------
        liberty: int
             Number of liberties that the given point has
        """

        group_points = [point]
        liberty = 0
        met_points = [point]
        while group_points:
            p = group_points.pop()
            met_points.append(p)
            neighbors = self._neighbors(p)
            for n in neighbors:
                if self.board[n] == BORDER:
                    continue
                if self.board[n] == color and n not in met_points:
                    group_points.append(n)
                elif self.board[n] == EMPTY and n not in met_points:
                    liberty += 1
        return liberty


    def _liberty_flood(self, board):
        """
        This function find the liberties of flood filled board.
        return True if it finds any liberty and False otherwise
        Arguments
        ---------
        board : numpy array

        Return
        ---------
        bool:
             whether the flood filled group in the board has any liberty
        """
        inds = list(*np.where(board == FLOODFILL))
        for f in inds:
            f_neighbors = self._neighbors(f)
            found_liberties = board[f_neighbors] == EMPTY
            if found_liberties.any():
                return True
        return False


    def _flood_fill(self, point):
        """
        Creates a new board and fills the connected groups to the given point
        Arguments
        ---------
        point

        Return
        ---------
         a new board with points in the neighbor of given point with same color replaced with
         FLOODFILL(=4)
         This is based on https://github.com/pasky/michi/blob/master/michi.py --> floodfill
        """
        fboard = np.array(self.board, copy = True)
        flood_list = [point]
        color = fboard[point]
        fboard[point] = FLOODFILL
        while flood_list:
            current_point = flood_list.pop()
            neighbors = self._neighbors(current_point)
            for n in neighbors :
                if fboard[n] == color:
                    fboard[n] = FLOODFILL
                    flood_list.append(n)
        return fboard


    def _play_move(self, point, color):
        """
        This function is for playing the move
        Arguments
        ---------
        point, color

        Return
        ---------
        State of move and appropriate message for that move
        """

        if self.board[point] != EMPTY:
            c = self._point_to_coord(point)
            msg = "occupied"
            return False, msg
        self.board[point] = color
        self._is_empty = False
        self.caps = []
        single_captures = []
        cap_inds = None
        neighbors = self._neighbors(point)
        for n in neighbors:
            if self.board[n] == BORDER:
                continue
            if self.board[n] != color:
                if self.board[n] != EMPTY:
                    fboard = self._flood_fill(n)
                    if not self._liberty_flood(fboard):
                        #there is a capture, which is illegal
                        self.board[point] = EMPTY
                        c = self._point_to_coord(point)
                        msg = "capture"
                        return False, msg
        fboard = self._flood_fill(point)
        if self._liberty_flood(fboard) and self.suicide:
            #non suicidal move
            c = self._point_to_coord(point)
            msg = "Playing a move with %s color in the row and column %d %d is permitted"%(color, c[0], c[1])
            return True, msg
        else:
            # undoing the move because of being suicidal
            self.board[point] = EMPTY
            if cap_inds != None:
                self.board[cap_inds] = GoBoardUtil.opponent(color)
            c = self._point_to_coord(point)
            msg = "suicide"
            return False, msg


    def _neighbors(self, point):
        """
        All neighbors of the point
        Arguments
        ---------
        point

        Returns
        -------
        list of neighbors of the given point
        """
        return [point - 1, point + 1, point - self.NS, point + self.NS]


    def _diag_neighbors(self, point):
        """
        All diagonal neighbors of the point
        Arguments
        ---------
        point

        Returns
        -------
        list of diagnoal neighbors of the given point
        """

        return [point - self.NS - 1, point - self.NS + 1, point + self.NS - 1, point + self.NS + 1]


    def _on_board(self, point):
        """
        returns True if point is inside the board and not on the borders.
        Arguments
        ---------
        point

        Returns
        -------
         bool
        """
        return self.board[point] != BORDER


    def _points_color(self, point):
        """
        Return the state of the specified point.

        Arguments
        ---------
        point

        Returns
        -------
         color: string
                 color representing the specified point .
        """
        p_int_color = self.board[point]
        return GoBoardUtil.int_to_color(p_int_color)

    def _coord_to_point(self, row, col):
        """
        Transform two dimensional presentation to one dimension.

        Arguments
        ---------
        x , y : int
                coordinate on the board  1 <= x <= size, 1 <= y <= size

        Returns
        -------
        point
        """
        if row < 0 or col < 0:
            raise ValueError("Wrong coordinates, Coordinates should be larger than 0")
        return self.NS * row + col

    def _point_to_coord(self, point):
        """
        Transform one dimension presentation to two dimensional.

        Arguments
        ---------
        point

        Returns
        -------
        x , y : int
                coordinate on the board  1 <= x <= size, 1 <= y <= size
        """
        if point is None:
            return 'pass'
        row, col = divmod(point, self.NS)
        return row, col

