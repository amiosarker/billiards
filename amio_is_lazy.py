import os
import sys

os.chdir('/Users/amiosarker/dev/Programing/python/billiards/indexed_sprites')

for file in os.listdir():
    if " copy" in file:
        os.rename(file, file.replace(" copy", ""))
