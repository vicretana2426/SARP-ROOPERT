'''
Running this module will theoretically startup everything needed for ROOPERT to run

Before this program can be run, the user needs to create a directory (folder) somewhere in their computer that isn't going
to be python-restricted (so Documents, Desktop are good choices whereas Program Files probably won't work) named "ROOPERT-Save-Files".
Then, they need to copy the exact path of that directory and put it into the variable "saveDirectory" otherwise the program won't run.
I think that because vscode is running is linux, you also have to create the directory in linux. You can do this in the terminal or  
install a file manager to help you:

Run the following commands to install a file manager:
1. sudo add-apt-repository universe
2. sudo apt update
3. sudo apt install dolphin

And to open just type in "dolphin" to the linux terminal and press enter
To be honest dolphin was really buggy in wsl I'd recommend learning how to navigate around directories in the terminal it's not too hard

General startup sequence something like the following:

1. On first startup, create directories where needed
2. Parse all of the saved rocket files and instantiate Rocket objects from RocketDatabase.py with the parameters in said save files
3. Launch GUI with the rocket objects instantiated
4. Job done

'''

import os
import RocketDatabase as RD
import DataManager as DM


'''This is where user needs to specify save directory for their computer. Make sure it is named "ROOPERT-Save-Files" exactly, or ROOPERT
will not run. The r needs to be in front of the string so that python ignores the backslashes. 

For example, Line 29 could read:
DM.saveDirectory = r"/mnt/c/Users/gbhof/Documents/ROOPERT-Save-Files"

To make the code work, create your ROOPERT-Save-Files and paste in the address down here:'''

DM.saveDirectory = r"/mnt/c/Users/gbhof/Documents/ROOPERT-Save-Files"


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



