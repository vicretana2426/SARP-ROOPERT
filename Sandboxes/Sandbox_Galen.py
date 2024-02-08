"This is for Galen"

mySave = r"/mnt/c/Users/gbhof/Documents/ROOPERT-Save-Files"
import getpass
import NewOOPSystem.DataManager as DM
import os

for root, dirs, files in os.walk(".", topdown = False):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))