# Cmput 496 sample code
# 33 Patterns
# Written by Chenjun Xiao
# Code is from the michi project on Github:
# https://github.com/pasky/michi/blob/master/michi.py

from functools import reduce
import collections

pat3src = [  # 3x3 playout patterns; X,O are colors, x,o are their inverses
           ["XOX",  # hane pattern - enclosing hane
            "...",
            "???"],
           ["XO.",  # hane pattern - non-cutting hane
            "...",
            "?.?"],
           ["XO?",  # hane pattern - magari
            "X..",
            "x.?"],
           # ["XOO",  # hane pattern - thin hane
           #  "...",
           #  "?.?", "X",  - only for the X player
           [".O.",  # generic pattern - katatsuke or diagonal attachment; similar to magari
            "X..",
            "..."],
           ["XO?",  # cut1 pattern (kiri] - unprotected cut
            "O.o",
            "?o?"],
           ["XO?",  # cut1 pattern (kiri] - peeped cut
            "O.X",
            "???"],
           ["?X?",  # cut2 pattern (de]
            "O.O",
            "ooo"],
           ["OX?",  # cut keima
            "o.O",
            "???"],
           ["X.?",  # side pattern - chase
            "O.?",
            "   "],
           ["OX?",  # side pattern - block side cut
            "X.O",
            "   "],
           ["?X?",  # side pattern - block side connection
            "x.O",
            "   "],
           ["?XO",  # side pattern - sagari
            "x.x",
            "   "],
           ["?OX",  # side pattern - cut
            "X.O",
            "   "],
           ]

def pat3_expand(pat):
    """ All possible neighborhood configurations matching a given pattern;
        used just for a combinatoric explosion when loading them in an
        in-memory set. """
    def pat_rot90(p):
        return [p[2][0] + p[1][0] + p[0][0], p[2][1] + p[1][1] + p[0][1], p[2][2] + p[1][2] + p[0][2]]
    def pat_vertflip(p):
        return [p[2], p[1], p[0]]
    def pat_horizflip(p):
        return [l[::-1] for l in p]
    def pat_swapcolors(p):
        return [l.replace('X', 'Z').replace('x', 'z').replace('O', 'X').replace('o', 'x').replace('Z', 'O').replace('z', 'o') for l in p]
    def pat_wildexp(p, c, to):
        i = p.find(c)
        if i == -1:
            return [p]
        return reduce(lambda a, b: a + b, [pat_wildexp(p[:i] + t + p[i+1:], c, to) for t in to])
    def pat_wildcards(pat):
        return [p for p in pat_wildexp(pat, '?', list('.XO '))
                for p in pat_wildexp(p, 'x', list('.O '))
                for p in pat_wildexp(p, 'o', list('.X '))]
    return [p for p in [pat, pat_rot90(pat)]
            for p in [p, pat_vertflip(p)]
            for p in [p, pat_horizflip(p)]
            for p in [p, pat_swapcolors(p)]
            for p in pat_wildcards(''.join(p))]

pat3list = [p.replace('O', 'x') for p in pat3src for p in pat3_expand(p)]

pat3set = set(pat3list)

def switch_color(pattern):
    p = pattern
    p=p.replace('x', 'O')
    p=p.replace('X', 'x')
    p=p.replace('O', 'X')
    return p

def generate_pattern_index():
    """
    Assign all symmetric pattern with the same pattern index, which is used for learning.
    There are three types of symmetry: rotation symmetry, reflection symmetry and color symmetry.
    """
    index = 0
    p_index = {}
    for p in pat3list:
        if p in p_index:
            continue
        p1 = p[6]+p[3]+p[0]+p[7]+p[4]+p[1]+p[8]+p[5]+p[2]
        p2 = p[8]+p[7]+p[6]+p[5]+p[4]+p[3]+p[2]+p[1]+p[0]
        p3 = p[2]+p[5]+p[8]+p[1]+p[4]+p[7]+p[0]+p[3]+p[6]
        p4 = p[6]+p[7]+p[8]+p[3]+p[4]+p[5]+p[0]+p[1]+p[2]
        p5 = p[2]+p[1]+p[0]+p[5]+p[4]+p[3]+p[8]+p[7]+p[6]
        p6 = p[0]+p[3]+p[6]+p[1]+p[4]+p[7]+p[2]+p[5]+p[8]
        p7 = p[8]+p[5]+p[2]+p[7]+p[4]+p[1]+p[6]+p[3]+p[0]
        p_index[p]=index
        p_index[p1]=index
        p_index[p2]=index
        p_index[p3]=index
        p_index[p4]=index
        p_index[p5]=index
        p_index[p6]=index
        p_index[p7]=index

        p_index[switch_color(p)]=index
        p_index[switch_color(p1)]=index
        p_index[switch_color(p2)]=index
        p_index[switch_color(p3)]=index
        p_index[switch_color(p4)]=index
        p_index[switch_color(p5)]=index
        p_index[switch_color(p6)]=index
        p_index[switch_color(p7)]=index
        index = index+1
    return p_index

patIndex = generate_pattern_index()



