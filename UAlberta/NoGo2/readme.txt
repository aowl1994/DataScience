# NoGo2

======================
Shuming Zhang   1401170
Xinghua Bi      1275127
Zichong Huang   1398109











======================
Go1_v2.py is for measuring time. It has no time limit.

test_case_easy:
1. 10s  > 1.76353618
2. 70s  > 8.721734015
3. 50s  > 4.135701034
4. 5s   > 0.048165899999998985
5. 1s   > 0.0002755449999991555

test_case_medium:
1. 50s	< 600 ???
2. 50s	> 35.40853579999998
3. 100s

test_case_hard:
1. 20s
2. 100s
3. 100s

Optimization.1
Store all searched state winner and move

Optimization.2
Store the state from different angle


=================
Test Command
=================
$ gogui-regress Go1.py <GTPFILE> -output output/
