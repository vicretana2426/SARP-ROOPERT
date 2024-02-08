'''This module contains the class Rocket. For the momemnt, I don't see any other purpose for it.'''

import DataManager as DM
import os
import numpy as np
import csv

'''Important class. The goal of this is to store all the information that is specific to a rocket. Currently, the rocket only stores
a name and a dictionary params (this is a dictionary that David has used freqruently throughout his code), but in the future it can hold
as many variables as we need it to'''

'''Important note on the keyword self. Self refers to any variable that is specific to an instance of an object. Any variable or 
function that changes based on which instance of an object we are referencing needs to have 'self' in it. For variables, use
self.varName. For functions, include self as the first argument.
'''

class Rocket:

    '''This is the constructor of the class. It is set up specifically so that all it takes to instantiate a rocket is the name.
    All other data will be created if there is no save file for that rocket name yet. If data already exists, it will load that data
    and instantiate the rocket object from that data'''
    def __init__(self, name):

        #Set the most identifying feature, the name of the rocket
        self.name = name
        #This will set the save path to the name of the rocket, whether this directory has already been created or not
        self.savePath = os.path.join(DM.rocketSaveFilePath, self.name)

        
        
        '''Attempt to create a save directory. If this is successful, define a blank set of params and save it so that a 
        params.csv file is created. If unsuccessful, this means a save directory is already created. Load the params.csv in this
        directory and use it to define the params of this object'''
        try:
            #Make the directory
            os.makedirs(self.savePath)
            #Log
            print("Created Save Folder for " + self.name)
            #Set the params variable in this class to blank params and save
            self.params = DM.blankParams
            self.Save_Data()
        except:
            #Define a path for the params.csv file
            self.paramsCSV = open(os.path.join(self.savePath, "params.csv"), "r")
            #Define a DictReader object for the params.csv file
            self.paramsReader = csv.DictReader(self.paramsCSV)
            #define a blank params dictionary
            self.params = dict.fromkeys(DM.blankParams)
            
            '''This for loop is just going to iterate over one row. The row contains all of the values of the params dictionary'''
            for row in self.paramsReader:

                '''This iterates through each key in the row and sets it's value to the blank params we just defined'''
                for param in self.params:
                    self.params[param] = row[param]
            #Log
            print("Loaded Existing Save File for " + self.name)

        self.rocketSaveFiles = os.listdir(self.savePath)

        for rocketSaveFile in self.rocketSaveFiles:
            if (rocketSaveFile == "Charts"):
                print("we found a chart")
            elif (rocketSaveFile == "Engine"):
                print("We found an engine")
            else:
                print("We don't know what the heck " + rocketSaveFile + " is!")
        print(self.rocketSaveFiles)

    

    '''This function simply prints out the identifying characteristics of the rocket.'''
    def Print_Info(self):
        print("Rocket " + self.name + " has the following params:")
        print(self.params)


    '''This is the function to save the data in this rocket object to it's save folder. Importantly, it assumes that the variable
    savePath has already been defined'''
    def Save_Data(self):
        #open the params.csv file and save it to a variable paramsCSV
        self.paramsCSV = open(os.path.join(self.savePath, "params.csv"), "w")
        #Set the fieldnames of the file to the typical params format. The fieldnames on the csv file correspond to the keys of the dictionary
        self.fieldnames = dict.fromkeys(DM.blankParams)
        #Define a CSV Writer
        self.paramsWriter = csv.DictWriter(self.paramsCSV, self.fieldnames)
        #Write the header and the current values of params
        self.paramsWriter.writeheader()
        self.paramsWriter.writerow(self.params)
            
    '''This is a testing function I created just for the purposes of testing to make sure this file-saving stuff works'''
    def Define_Random_Params(self):
        for param in self.params:
            self.params[param] = np.random.randint(0, 10)
        
            
        
