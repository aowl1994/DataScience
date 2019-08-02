mkdir mm_training_data
cd mm_training_data
GO6=/path/to/your/Go6.py
GAMEDIR=/path/to/your/games # You should have a directory called 'games' which contains sgf files
echo $GAMEDIR
/Users/xiaochenjun/igo/gogui-1.4.9/bin/gogui-statistics -program "python3 $GO6" -commands "features_mm_file" -size 7 \
-quiet -force $GAMEDIR/*sgf
