#!/usr/bin/python3
from gtp_connection import GtpConnection
import numpy as np
from board_util import GoBoardUtil
import argparse
import sys
from pattern import pat3set

parser = argparse.ArgumentParser(description='Process Arguments for number of simulation')
parser.add_argument('-s','--sim',type=int, nargs='?', default=10, help='define number of simulations for each legal move, #playout --> sim*num_of_legal_moves')
args = parser.parse_args()
num_simulation = args.sim

# pair = (move, percentage)
def byPercentage(pair):
    return pair[1]

def writeMoves(board, moves, count, numSimulations):
    gtp_moves = []
    for i in range(len(moves)):
        if moves[i] != None:
            x, y = board._point_to_coord(moves[i])
            gtp_moves.append((GoBoardUtil.format_point((x, y)),
                          float(count[i])/float(numSimulations)))
        else:
            gtp_moves.append(('Pass',float(count[i])/float(numSimulations)))
    sys.stderr.write("win rates: {}\n"
                     .format(sorted(gtp_moves, key = byPercentage,
                                               reverse = True)))
    sys.stderr.flush()

def select_best_move(board, moves, moveWins):
    max_child = np.argmax(moveWins)
    return moves[max_child]

class Go4Player(object):
    """
    Flat Monte Carlo implementation that uses simulation for finding the best child of a given node
    """

    version = 0.3
    name = "Go4"
    def __init__(self,num_simulation=50,size=5,limit=100):
        """
        self.selfatari & self.pattern gets created in the gtp_connection, 
        when instance of GtpConnection is created
        """
        self.num_simulation = num_simulation
        self.limit = limit
    
    def simulate(self, board, cboard, move, toplay):
        GoBoardUtil.copyb2b(board,cboard)
        assert cboard.board.all() == board.board.all()
        cboard.move(move, toplay)
        opp = GoBoardUtil.opponent(toplay)
        return GoBoardUtil.playGame(cboard,
                opp,
                komi= self.komi,
                limit=self.limit,
                selfatari=self.selfatari,
                pattern=self.pattern)

    def simulateMove(self, board, cboard, move, toplay):
        wins = 0
        for _ in range(self.num_simulation):
            result = self.simulate(board, cboard, move, toplay)
            if result == toplay:
                wins += 1
        return wins
        
    def get_move(self, board, toplay):
        cboard = board.copy()
        emptyPoints = board.get_empty_points()
        moves = []
        ### Assignment 3 - genmove
        #policy_moves, type_of_move = GoBoardUtil.generate_all_policy_moves(board,
         #                                       self.pattern,
          #                                      self.selfatari)
        for p in emptyPoints:
        #for p in policy_moves:
            if not GoBoardUtil.filleye_filter(board, p, toplay):
                moves.append(p)
        if not moves: # pass move only, no need to simulate
            return None
        moves.append(None) # None for Pass
        moveWins = []
        for move in moves:
            wins = self.simulateMove(board, cboard, move, toplay)
            moveWins.append(wins)
        writeMoves(board, moves, moveWins, self.num_simulation)
        return select_best_move(board, moves, moveWins)

    def get_properties(self):
        return dict(
            version=self.version,
            name=self.__class__.__name__,
        )


if __name__=='__main__':
    c = GtpConnection(Go4Player(num_simulation))
    c.start_connection()

