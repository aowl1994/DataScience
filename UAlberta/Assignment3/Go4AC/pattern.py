# Cmput 496 sample code
# 33 Patterns
# Written by Chenjun Xiao
# Code is from the michi project on Github:
# https://github.com/pasky/michi/blob/master/michi.py

from functools import reduce

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

pat3set = set([p.replace('O', 'x') for p in pat3src for p in pat3_expand(p)])



