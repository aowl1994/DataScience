"""
Module for playing games of Go using GoTextProtocol

This code is based off of the gtp module in the Deep-Go project
by Isaac Henrion and Amos Storkey at the University of Edinburgh.
"""
import traceback
import sys
import os
from board import GoBoard
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, FLOODFILL
import numpy as np
import re

class GtpConnection():

    def __init__(self, go_engine, debug_mode = False):
        """
        Play Go over a GTP connection

        Parameters
        ----------
        go_engine: GoPlayer
            a program that is capable of playing go by reading GTP commands
        komi : float
            komi used for the current game
        board: GoBoard
            SIZExSIZE array representing the current board state
        """
        self.stdout = sys.stdout
        self._debug_mode = debug_mode
        sys.stdout = self
        self.go_engine = go_engine
        self.go_engine.komi = 0
        self.go_engine.selfatari = 1 
        self.go_engine.pattern = 1
        self.board = GoBoard(7)
        self.param_options = {
            "selfatari" :  self.go_engine.selfatari,
            "pattern" : self.go_engine.pattern
        }
        self.commands = {
            "protocol_version": self.protocol_version_cmd,
            "quit": self.quit_cmd,
            "name": self.name_cmd,
            "boardsize": self.boardsize_cmd,
            "showboard": self.showboard_cmd,
            "clear_board": self.clear_board_cmd,
            "komi": self.komi_cmd,
            "version": self.version_cmd,
            "known_command": self.known_command_cmd,
            "set_free_handicap": self.set_free_handicap,
            "genmove": self.genmove_cmd,
            "list_commands": self.list_commands_cmd,
            "play": self.play_cmd,
            "final_score": self.final_score_cmd,
            "legal_moves": self.legal_moves_cmd,
            "policy_moves": self.policy_moves_cmd,
            "random_moves": self.random_moves_cmd,
            "go_param": self.go_param_cmd,
            "gogui-analyze_commands": self.gogui_analyze_cmd,
            "num_sim": self.num_sim_cmd,
            "showoptions": self.showoptions_cmd
        }

        # used for argument checking
        # values: (required number or arguments, error message on argnum failure)
        self.argmap = {
            "boardsize": (1, 'Usage: boardsize INT'),
            "komi": (1, 'Usage: komi FLOAT'),
            "known_command": (1, 'Usage: known_command CMD_NAME'),
            "set_free_handicap": (1, 'Usage: set_free_handicap MOVE (e.g. A4)'),
            "genmove": (1, 'Usage: genmove {w, b}'),
            "play": (2, 'Usage: play {b, w} MOVE'),
            "legal_moves": (0, 'Usage: legal_moves does not have arguments'),
            "go_param": (2,'Usage: goparam {{{0}}} {{0,1}}'.format(' '.join(list(self.param_options.keys())))),
            "num_sim":(1,'Usage: num_sim #(e.g. num_sim 100 )'),
            "showoptions":(0,'Usage: showoptions does not have arguments')
        }
    def __del__(self):
        sys.stdout = self.stdout

    def write(self, data):
        self.stdout.write(data)

    def flush(self):
        self.stdout.flush()

    def start_connection(self):
        """
        start a GTP connection. This function is what continuously monitors
        the user's input of commands.
        """
        self.debug_msg("Start up successful...\n\n")
        line = sys.stdin.readline()
        while line:
            self.get_cmd(line)
            line = sys.stdin.readline()

    def get_cmd(self, command):
        """
        parse the command and execute it

        Arguments
        ---------
        command : str
            the raw command to parse/execute
        """
        if len(command.strip(' \r\t')) == 0:
            return
        if command[0] == '#':
            return
        # Strip leading numbers from regression tests
        if command[0].isdigit():
            command = re.sub("^\d+", "", command).lstrip()

        elements = command.split()
        if not elements:
            return
        command_name = elements[0]; args = elements[1:]
        if self.arg_error(command_name, len(args)):
            return
        if command_name in self.commands:
            try:
                self.commands[command_name](args)
            except Exception as e:
                self.debug_msg("Error executing command {}\n".format(str(e)))
                self.debug_msg("Stack Trace:\n{}\n".format(traceback.format_exc()))
                raise e
        else:
            self.debug_msg("Unknown command: {}\n".format(command_name))
            self.error('Unknown command')
            sys.stdout.flush()

    def arg_error(self, cmd, argnum):
        """
        checker function for the number of arguments given to a command

        Arguments
        ---------
        cmd : str
            the command name
        argnum : int
            number of parsed argument

        Returns
        -------
        True if there was an argument error
        False otherwise
        """
        if cmd in self.argmap and self.argmap[cmd][0] != argnum:
            self.error(self.argmap[cmd][1])
            return True
        return False

    def debug_msg(self, msg = ''):
        """ Write a msg to the debug stream """
        if self._debug_mode:
            sys.stderr.write(msg); sys.stderr.flush()

    def error(self, error_msg = ''):
        """ Send error msg to stdout and through the GTP connection. """
        sys.stdout.write('? {}\n\n'.format(error_msg)); sys.stdout.flush()

    def respond(self, response = ''):
        """ Send msg to stdout """
        sys.stdout.write('= {}\n\n'.format(response)); sys.stdout.flush()

    def reset(self, size):
        """
        Resets the state of the GTP to a starting board

        Arguments
        ---------
        size : int
            the boardsize to reinitialize the state to
        """
        self.board.reset(size)

    def protocol_version_cmd(self, args):
        """ Return the GTP protocol version being used (always 2) """
        self.respond('2')

    def quit_cmd(self, args):
        """ Quit game and exit the GTP interface """
        self.respond()
        exit()

    def name_cmd(self, args):
        """ Return the name of the player """
        self.respond(self.go_engine.name)

    def version_cmd(self, args):
        """ Return the version of the player """
        self.respond(self.go_engine.version)

    def clear_board_cmd(self, args):
        """ clear the board """
        self.reset(self.board.size)
        self.respond()

    def boardsize_cmd(self, args):
        """
        Reset the game and initialize with a new boardsize

        Arguments
        ---------
        args[0] : int
            size of reinitialized board
        """
        self.reset(int(args[0]))
        self.respond()

    def showboard_cmd(self, args):
        self.respond('\n' + str(self.board.get_twoD_board()))
    
    def showoptions_cmd(self,args):
        options = dict()
        options['komi'] = self.go_engine.komi
        options['pattern'] = self.go_engine.pattern
        options['selfatari'] = self.go_engine.selfatari
        options['num_sim'] = self.go_engine.num_simulation
        self.respond(options)
        
    def komi_cmd(self, args):
        """
        Set the komi for the game

        Arguments
        ---------
        args[0] : float
            komi value
        """
        self.go_engine.komi = float(args[0])
        self.respond()

    def known_command_cmd(self, args):
        """
        Check if a command is known to the GTP interface

        Arguments
        ---------
        args[0] : str
            the command name to check for
        """
        if args[0] in self.commands:
            self.respond("true")
        else:
            self.respond("false")

    def list_commands_cmd(self, args):
        """ list all supported GTP commands """
        self.respond(' '.join(list(self.commands.keys())))

    def set_free_handicap(self, args):
        """
        clear the board and set free handicap for the game

        Arguments
        ---------
        args[0] : str
            the move to handicap (e.g. B2)
        """
        self.board.reset(self.board.size)
        for point in args:
            move = GoBoardUtil.move_to_coord(point, self.board.size)
            point = self.board._coord_to_point(*move)
            if not self.board.move(point, BLACK):
                self.debug_msg("Illegal Move: {}\nBoard:\n{}\n".format(move, str(self.board.get_twoD_board())))
        self.respond()

    def legal_moves_cmd(self, args):
        """
        list legal moves for current player
        """
        color = self.board.current_player
        legal_moves = GoBoardUtil.generate_legal_moves(self.board, color)
        self.respond(GoBoardUtil.sorted_point_string(legal_moves, self.board.NS))

    def num_sim_cmd(self, args):
        self.go_engine.num_simulation = int(args[0])
        self.respond()

    def go_param_cmd(self, args):
        valid_values = [0,1]
        valid_params = ['selfatari','pattern']
        param = args[0]
        param_value = int(args[1])
        if param not in valid_params:
            self.error('Unkown parameters: {}'.format(param))
        if param_value not in valid_values:
            self.error('Argument 2 ({}) must be of type bool'.format(param_value))
        if param ==valid_params[1]:
            self.go_engine.pattern = param_value
        elif param == valid_params[0]:
            self.go_engine.selfatari = param_value
        self.param_options[param] = param_value
        self.respond()

    def policy_moves_cmd(self, args):
        """
            Return list of policy moves for the current_player of the board
        """
        policy_moves, type_of_move = GoBoardUtil.generate_all_policy_moves(self.board,
                                                self.go_engine.pattern,
                                                self.go_engine.selfatari)
        if len(policy_moves) == 0:
            self.respond("Pass")
        else:
            response = type_of_move + " " + GoBoardUtil.sorted_point_string(policy_moves, self.board.NS)
            self.respond(response)

    def random_moves_cmd(self, args):
        """
            Return list of random moves (legal, but not eye-filling)
        """
        moves = GoBoardUtil.generate_random_moves(self.board)
        if len(moves) == 0:
            self.respond("Pass")
        else:
            self.respond(GoBoardUtil.sorted_point_string(moves, self.board.NS))

    def gogui_analyze_cmd(self, args):
        try:
            self.respond("pstring/Legal Moves/legal_moves\n"
                         "pstring/Policy Moves/policy_moves\n"
                         "pstring/Random Moves/random_moves\n"
                        )
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))

    def play_cmd(self, args):
        """
        play a move as the given color

        Arguments
        ---------
        args[0] : {'b','w'}
            the color to play the move as
            it gets converted to  Black --> 1 White --> 2
            color : {0,1}
            board_color : {'b','w'}
        args[1] : str
            the move to play (e.g. A5)
        """
        try:
            board_color = args[0].lower()
            board_move = args[1]
            color= GoBoardUtil.color_to_int(board_color)
            if args[1].lower()=='pass':
                self.debug_msg("Player {} is passing\n".format(args[0]))
                self.board.current_player = GoBoardUtil.opponent(color)
                self.respond()
                return
            move = GoBoardUtil.move_to_coord(args[1], self.board.size)
            if move:
                move = self.board._coord_to_point(move[0], move[1])
            else:
                self.error("Error in executing the move %s, check given move: %s"%(move,args[1]))
                return
            if not self.board.move(move, color):
                self.respond("Illegal Move: {}".format(board_move))
                return
            else:
                self.debug_msg("Move: {}\nBoard:\n{}\n".format(board_move, str(self.board.get_twoD_board())))
            self.respond()
        except Exception as e:
            self.respond("illegal move: {} {} {}".format(board_color, board_move, str(e)))

    def final_score_cmd(self, args):
        self.respond(self.board.final_score(self.go_engine.komi))

    def genmove_cmd(self, args):
        """
        generate a move for the specified color

        Arguments
        ---------
        args[0] : {'b','w'}
            the color to generate a move for
            it gets converted to  Black --> 1 White --> 2
            color : {0,1}
            board_color : {'b','w'}
        """
        try:
            board_color = args[0].lower()
            color = GoBoardUtil.color_to_int(board_color)
            self.debug_msg("Board:\n{}\nko: {}\n".format(str(self.board.get_twoD_board()),
                                                          self.board.ko_constraint))
            move = self.go_engine.get_move(self.board, color)
            if move is None:
                self.respond("pass")
                return

            if not self.board.check_legal(move, color):
                move = self.board._point_to_coord(move)
                board_move = GoBoardUtil.format_point(move)
                self.respond("Illegal move: {}".format(board_move))
                raise RuntimeError("Illegal move given by engine")

            # move is legal; play it
            self.board.move(move, color)
            self.debug_msg("Move: {}\nBoard: \n{}\n".format(move, str(self.board.get_twoD_board())))
            move = self.board._point_to_coord(move)
            board_move = GoBoardUtil.format_point(move)
            self.respond(board_move)
        except Exception as e:
            self.respond('Error: {}'.format(str(e)))
