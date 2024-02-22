"This is for Galen"

import sys
sys.path.insert(1,"./")
import NewOOPSystem.DataManager as DM
import os

os.chdir(DM.saveDirectory)
for root, dirs, files in os.walk(".", topdown = True):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))
