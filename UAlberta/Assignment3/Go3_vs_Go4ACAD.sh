#!/bin/bash
set -eu
RESULTDIR="Go3_vs_Go4ACAD"
# Modify paths to your programs below as needed
GO3="Go3/Go3.py"
GO4ACAD="Go4ACAD/Go4.py"
TWOGTP=gogui-twogtp 

run() {
echo Match with $NUGAMES games on board size $BOARDSIZE. Storing results in $RESULTDIR

mkdir -p $RESULTDIR
$TWOGTP -black "$GO3" -white "$GO4ACAD" \
-auto  -komi 6.5 -size $BOARDSIZE -games $NUGAMES \
-sgffile $RESULTDIR/game -threads 8

$TWOGTP -analyze $RESULTDIR/game.dat -force
}

NUGAMES=100
BOARDSIZE=5
run
