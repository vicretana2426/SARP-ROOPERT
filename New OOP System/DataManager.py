'''The purpose of this module is to store information that multiple other modules need to access. I originally had this in
Executable.py, but that created a circular import error. On that note, this module should only contain global variables and 
basic, basic functions. It should NEVER import another module in this program'''

'''The variables below are critical for the file structure of this program. Importantly, the rockets list holds all the rocket 
objects and will contain all the saved rocket configurations after Executable.py runs it'''

saveDirectory = "not yet defined" #This is the save directory for everything ROOPERT, named ROOPERT-Save-Files. See Executable.py to define this
roopertSaveFiles = None #List of all of the directories in ROOPERT-Save-Files
rocketSaveFilePath = None #The path where all the rocket save folders are
rocketSaveFiles = None #List of all the saved rocket names 
rockets = [] #List of all the instantiated rocket objects




#Blank Params. Use dict.fromkeys(blankParams) to access these. Just figured to put it here for ease of use
blankParams = {  
        'thrust' : None,
        'time' : None,
        'pc' : None,
        'pe' : None,
        'cr' : None,
        'TWR' : None,
        'lstar' : None,
        'fuelname' : None,
        'Ethanol_75' : None,
        'oxname' : None,
        'N2O' : None,
        'throat_radius_curvature' : None,
        'dp' : None,
        'impulseguess' : None,
        'rc' : None,
        'thetac' : None} 
