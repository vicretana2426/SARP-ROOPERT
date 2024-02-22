'''The purpose of this module is to store information that multiple other modules need to access. I originally had this in
Executable.py, but that created a circular import error. On that note, this module should only contain global variables and 
basic, basic functions. It should NEVER import another module in this program'''

'''The variables below are critical for the file structure of this program. Importantly, the rockets list holds all the rocket 
objects and will contain all the saved rocket configurations after Executable.py runs it'''

saveDirectory = "not yet defined" #This is the save directory for everything ROOPERT, named ROOPERT-Save-Files. See Executable.py to define this
roopertSaveFiles = None #List of all of the directories in ROOPERT-Save-Files
rocketSaveFilePath = None #The path where all the rocket save folders are
rocketSaveFolders = None #List of all the saved rocket names 
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
        'fuelname' : 'Ethanol_75',
        'oxname' : 'N2O',
        'throat_radius_curvature' : None,
        'dp' : None,
        'impulseguess' : None,
        'rc' : None,
        'thetac' : None} 

# Units for parameters
unitdict = {
    'thrust' : "N",
    'time' : "s",
    'impulse' : "N*s",
    'rho_ox' : 'kg/M^3',
    'rho_fuel': 'kg/M^3',
    'pc' : "Pa, if cr is specified, this is Pressure at end of combustor",
    'pinj' : "Pa, only useful if you specify CR, otherwise assumed to be pc",
    'pe' : 'Pa',
    'g' : 'm/s^2',
    'rm' : 'o/f by mass',
    'phi' : 'ratio from stoich (1 is stoich, >1 is fuel rich)',
    'at' :  'm^2, area of throat',
    'rt' :  'm, radius of throat' ,
    'cr' :  'contraction area ratio',
    'rc' :  'm, combustion chamber radius',
    'ac' :  'm^2, area combustion chamber',
    'l_star' :  'm, volume cc/area throat',
    'mol_weight' :  'kg/mol',
    'gamma' :  'in cc',
    'gamma_exit' :  'in exit',
    'gamma_throat' :  'in throat',
    'isp' :  's',
    'temp_c' :  'K, chamber temp',
    'rg' :  'specific gas constant (SI units whatever they are)',
    'pr_throat' : "dimensionless?",
    'rho_throat' : 'kg/M^3',
    'temp_e' : 'K',
    'v_exit' : 'm/s',
    'a_exit' : 'm/s, speed of sound',
    'mach_exit' : 'Mach',
    'temp_throat' : 'K',
    'p_throat' : 'Pa',
    'v_throat' : 'm/s',
    'mdot' : 'kg/s',
    'mdot_ox' : 'kg/s',
    'mdot_fuel' : 'kg/s',
    'er' : 'Expansion Area Ratio',
    'cstar' : 'm/s',
    'cf' : 'dimensionless?',
    'c_eff' : 'm/s',
    'rho_av' : 'kg/s',
    'vc' : 'm^3',
    'theta_con' : 'radians' ,
    'lc' : 'm, combustor length',
    'theta_div' : 'radians',
    'ln_conical' : 'm, 15 degree conical',
    'ln_bell' : 'm',
    'throat_radius_curvature' : 'm',
    'ae' : 'm^2',
    're' : 'm^2',
    'nv' : 'dimenionless',
    'nvstar' : 'dimenionless',
    'nf' : 'dimenionless',
    'nw' : 'dimenionless',
    'fuelname' : '',
    'oxname' : '',
    'CEA' : '<- this is an object',
    'pambient' : 'Pa',
    'cf_efficiency' :  'Huzel and Huang page 16',
    'isp_efficiency' :  'dimensionless',
    'thetac' :  'converging section angle',
    'thetai' :  'diverging angle at throat',
    'thetae' : 'diverign angle at exit',# diverign angle at exit
    'kin_visc_fuel' : "Pa s m3/kg",
    'kin_visc_ox' : "Pa s m3/kg",
    'dyn_visc_fuel' : "Pa s",
    'dyn_visc_ox' : "Pa s"}
