import os
import sys

os.chdir('/Users/amiosarker/dev/Programing/python/billiards/indexed_sprites')
def is_number(s):
    try:
        float(s)  # or int(s) for integers only
        return True
    except ValueError:
        return False
    

for file in os.listdir():
    if " copy" in file:
        os.rename(file, file.replace(" copy", ""))
    if not is_number(file[0]+file[1]) and is_number(file[0]):
        os.rename(file, file.replace(file[0], "0"+file[0]))
    if is_number(file[0]+file[1]) and file[2]!="_":
        os.rename(file, file.replace(file[0]+file[1],file[0]+file[1]+"_"))
    if " " in file:
        os.replace(file, file.replace(" ","_"))

