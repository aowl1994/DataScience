#!/usr/bin/python3
"""
This function is loosely based on https://github.com/Rochester-NRT/RocAlphaGo/blob/develop/AlphaGo/mcts.py
"""

import numpy as np
import random
from board_util import GoBoardUtil, BLACK, WHITE
from feature import Feature
from feature import Features_weight

PASS = 'pass'

def uct_val(node, child, exploration, max_flag):
    if child._n_visits == 0:
        return float("inf")
    if max_flag:
        return float(child._black_wins)/child._n_visits + exploration*np.sqrt(np.log(node._n_visits)/child._n_visits) + node._prob_simple_feature / (1.0 + node._n_visits)
    else:
        return float(child._n_visits - child._black_wins)/child._n_visits + exploration*np.sqrt(np.log(node._n_visits)/child._n_visits) + node._prob_simple_feature / (1.0 + node._n_visits)

class TreeNode(object):
    """A node in the MCTS tree.
    """
    version = 0.1
    name = "MCTS Player"
    def __init__(self, parent):
        """
        parent is set when a node gets expanded
        """
        self._parent = parent
        self._children = {}  # a map from move to TreeNode
        self._n_visits = 0
        self._black_wins = 0
        self._expanded = False
        self._move = None
        self._prob_simple_feature = 1.0

    def expand(self, board, color):
        """Expands tree by creating new children.
        """
        gammas_sum = 0.0
        moves = board.get_empty_points()
        all_board_features = Feature.find_all_features(board)
        for move in moves:
            if move not in self._children:
                if board.check_legal(move, color) and not board.is_eye(move, color):
                    self._children[move] = TreeNode(self)
                    self._children[move]._move = move
                    if len(Features_weight) != 0:
                        # when we have features weight, use that to compute knowledge (gamma) of each move
                        assert move in all_board_features
                        self._children[move]._prob_simple_feature = Feature.compute_move_gamma(Features_weight, all_board_features[move])
                        gammas_sum += self._children[move]._prob_simple_feature

        self._children[PASS] = TreeNode(self)
        self._children[PASS]._move = move
        
        # when we have features weight, use that to compute knowledge (gamma) of each move
        if len(Features_weight) != 0:
            self._children[PASS]._prob_simple_feature = Feature.compute_move_gamma(Features_weight, all_board_features["PASS"])
            gammas_sum += self._children[PASS]._prob_simple_feature
        
        # Normalize to get probability
        if len(Features_weight) != 0 and gammas_sum != 0.0:
            for move in moves:
                if move not in self._children:
                    if board.check_legal(move, color) and not board.is_eye(move, color):
                        self._children[move]._prob_simple_feature = self._children[move]._prob_simple_feature / gammas_sum
            self._children[PASS]._prob_simple_feature = self._children[PASS]._prob_simple_feature / gammas_sum
        self._expanded = True

    def select(self, exploration, max_flag):
        """Select move among children that gives maximizes UCT. 
        If number of visits are zero for a node, value for that node is infinity so definitely will  gets selected

        It uses: argmax(child_num_black_wins/child_num_vists + C * sqrt(2 * ln * Parent_num_vists/child_num_visits) )
        Returns:
        A tuple of (move, next_node)
        """
        return max(self._children.items(), key=lambda items:uct_val(self, items[1], exploration, max_flag))

    def update(self, leaf_value):
        """Update node values from leaf evaluation.
        Arguments:
        leaf_value -- the value of subtree evaluation from the current player's perspective.
        
        Returns:
        None
        """
        self._black_wins += leaf_value
        self._n_visits += 1

    def update_recursive(self, leaf_value):
        """Like a call to update(), but applied recursively for all ancestors.

        Note: it is important that this happens from the root downward so that 'parent' visit
        counts are correct.
        """
        # If it is not root, this node's parent should be updated first.
        if self._parent:
            self._parent.update_recursive(leaf_value)
        self.update(leaf_value)


    def is_leaf(self):
        """Check if leaf node (i.e. no nodes below this have been expanded).
        """
        return self._children == {}

    def is_root(self):
        return self._parent is None


class MCTS(object):

    def __init__(self):
        self._root = TreeNode(None)
        self.init_color = BLACK
    
    def _playout(self, board, color):
        """Run a single playout from the root to the given depth, getting a value at the leaf and
        propagating it back through its parents. State is modified in-place, so a copy must be
        provided.

        Arguments:
        board -- a copy of the board.
        color -- color to play
        

        Returns:
        None
        """
        node = self._root 
        # This will be True olny once for the root
        if not node._expanded:
            node.expand(board, color)
        while not node.is_leaf():
            # Greedily select next move.                
            max_flag = color == self.init_color
            move, next_node = node.select(self.exploration,max_flag)
            if move!=PASS:
                assert board.check_legal(move, color)
            if move == PASS:
                move = None
            board.move(move, color)
            color = GoBoardUtil.opponent(color) 
            node = next_node
        assert node.is_leaf()
        if not node._expanded:
            node.expand(board, color)

        board.current_player = color
        leaf_value = self._evaluate_rollout(board, color)  
        # Update value and visit count of nodes in this traversal.
        node.update_recursive(leaf_value)

    def _evaluate_rollout(self, board, color):
        """Use the rollout policy to play until the end of the game, returning +1 if the current
        player wins, -1 if the opponent wins, and 0 if it is a tie.
        """
        winner = GoBoardUtil.playGame(board,
                color,
                komi=self.komi,
                limit=self.limit,
                selfatari=self.selfatari,
                pattern=self.pattern)
        if winner == BLACK:
            return 1
        else:
            return 0

    def get_move(self,
            board,
            color,
            komi,
            limit,
            selfatari,
            pattern,
            num_simulation,
            exploration):
        """Runs all playouts sequentially and returns the most visited move.
        """
        self.komi = komi
        self.limit = limit
        self.selfatari = selfatari
        self.pattern = pattern
        self.toplay = color
        self.exploration = exploration
        for n in range(num_simulation):
            board_copy = board.copy()
            self._playout(board_copy, color)
        # choose a move that has the most visit 
        moves_ls = [(move, node._n_visits) for move, node in self._root._children.items()]

        if not moves_ls:
            return None
        moves_ls = sorted(moves_ls,key=lambda i:i[1],reverse=True)
        move = moves_ls[0]
        self.print_stat(board, self._root, color)
        if move[0] == PASS:
            return None
        assert board.check_legal(move[0], color)
        return move[0]
        
    def update_with_move(self, last_move):
        """Step forward in the tree, keeping everything we already know about the subtree, assuming
        that get_move() has been called already. Siblings of the new root will be garbage-collected.
        """
        if last_move in self._root._children:
            self._root = self._root._children[last_move]
        else:
            self._root = TreeNode(None)
        self._root._parent = None

    def good_print(self, board, node, color, num_nodes):
        cboard = board.copy()
        print("\nTaking a tour of select in tree like in one of the playouts! \n")
        print(cboard.get_twoD_board())
        if node._move != None:
            pointString = board.point_to_string(move)
        else:
            pointString = 'Root'
        print("\nMove: {} Numebr of children {}, Number of visits: {}"
                .format(pointString,len(node._children),node._n_visits))
            
        while not node.is_leaf():
            moves_ls = []
            max_flag = color == BLACK
            for move,child in node._children.items():
                uctval = uct_val(node,child,exploration,max_flag)
                moves_ls.append((move,uctval))
            moves_ls = sorted(moves_ls,key=lambda i:i[1],reverse=max_flag)
            if moves_ls:
                print("\nPrinting {} of {} childs that have highest UCT value \n".format(num_nodes, point))
                for i in range(num_nodes):
                    move = moves_ls[i][0]
                    child_val = moves_ls[i][1]
                    child_node = moves_ls[i][2]
                    print("\nChild point:{} ;UCT Value {}; Number of visits: {}; Number of Black wins: {}"
                        .format(cboard.point_to_string(move), child_val, child_node._n_visits, child_node._black_wins))
                                                                      
             # Greedily select next move.
            max_flag = color == self.init_color
            move, next_node = node.select(self.exploration,max_flag)
            if move==PASS:
                move = None
            assert cboard.check_legal(move, color)
            string_point = cboard.point_to_string(move)
            cboard.move(move, color)
            print("\nboard in simulation after chosing child {} in tree.".format(string_point))
            print(cboard.get_twoD_board())
            color = GoBoardUtil.opponent(color)
            node = next_node
        assert node.is_leaf()
        cboard.current_player = color
        leaf_value = self._evaluate_rollout(cboard, color)
        print("\nWinner of simulation is: {} color, Black is 0 an".format(leaf_value))

    def print_stat(self, board, root, color):
        s_color = GoBoardUtil.int_to_color(color)
        print("Numebr of children {}".format(len(root._children)))
        print("Number of roots visits: {}".format(root._n_visits))
        stats=[]
        for move,node in root._children.items():
            if color == self.init_color:
                wins = node._black_wins
            else:
                wins = node._n_visits - node._black_wins
            visits = node._n_visits
            if visits:
                win_rate = float(wins)/visits
            else:
                win_rate = 0
            if move==PASS:
                move = None
            pointString = board.point_to_string(move)
            stats.append((pointString,win_rate,wins,visits))
        print("Statistics: {}".format(sorted(stats,key=lambda i:i[3],reverse=True)))
