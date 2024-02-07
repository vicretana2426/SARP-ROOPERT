'''
Running this module will theoretically startup everything needed for ROOPERT to run

General startup sequence something like the following:

1. On first startup, create directories where needed
2. Parse all of the saved rocket files and instantiate Rocket objects from RocketDatabase.py with the parameters in said save files
3. Launch GUI with the rocket objects instantiated
4. Job done

'''

import os
import RocketDatabase as RD
import DataManager as DM


'''This is where ROOPERT will check to see if you have already created a save file. If not, it will create one'''

if not os.path.exists(r"/tmp/ROOPERT-Save-Files"):
    os.mkdir(r"/tmp/ROOPERT-Save-Files")


DM.saveDirectory = r"/tmp/ROOPERT-Save-Files"


#Make sure that the user defined a save directory. If they didn't, throw an error that prevents the rest of the program from running
if (DM.saveDirectory == "not yet defined"):
    raise Exception("Need to define save directory for ROOPERT. Check Executable.py for how to do so.")

#define a list that contains the name of each directory in ROOPERT-Save-Files
DM.roopertSaveFiles = os.listdir(DM.saveDirectory)

#try to create a directory called balls and update the roopert save files list, otherwise do nothing
try:
    os.makedirs(os.path.join(DM.saveDirectory, "balls"), exist_ok = False)
    DM.roopertSaveFiles = os.listdir(DM.saveDirectory)
except:
    pass

'''Try to create a save directory for rocket save files specifically. This is where individual rocket configurations will be stored.
If a save directory has already been created, then nothing will happen'''
try:
    os.makedirs(os.path.join(DM.saveDirectory, "Rocket-Save-Files"))
    DM.roopertSaveFiles = os.listdir(DM.saveDirectory)
except:
    pass

#Save the save path for the rocket save files to the data manager so that other modules can access it
DM.rocketSaveFilePath = os.path.join(DM.saveDirectory, "Rocket-Save-Files")
#Now, compile a list of all the saved rocket names to a list rocketSaveFiles
DM.rocketSaveFiles = os.listdir(DM.rocketSaveFilePath)

'''Now it's time to actually instantiate the Rocket objects from the rocket class. The goal of this is to turn all of the information
in the Rocket-Save-Files directory into the memory of the program when it runs. Do note that all this module does is provide the 
name of the Rocket. The module RocketDatabase only needs the name of the rocket to initialize the rocket and all the information
saved in its save folder'''

for rocketSaveFile in DM.rocketSaveFiles:
    DM.rockets.append(RD.Rocket(rocketSaveFile))

'''END OF DEVELOPMENT -- everything after this point is just my personal testing'''
for rocket in DM.rockets:
    rocket.Print_Info()



