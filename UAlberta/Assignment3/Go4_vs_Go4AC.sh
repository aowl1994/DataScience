#!/bin/bash
set -eu
RESULTDIR="Go4_vs_Go4AC"
# Modify paths to your programs below as needed
GO4="Go4/Go4.py"
GO4AC="Go4AC/Go4.py"
TWOGTP=gogui-twogtp 

run() {
echo Match with $NUGAMES games on board size $BOARDSIZE. Storing results in $RESULTDIR

mkdir -p $RESULTDIR
$TWOGTP -black "$GO4" -white "$GO4AC" \
-auto  -komi 6.5 -size $BOARDSIZE -games $NUGAMES \
-sgffile $RESULTDIR/game -threads 8

$TWOGTP -analyze $RESULTDIR/game.dat -force
}

NUGAMES=100
BOARDSIZE=5
run
