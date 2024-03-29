"""This is the essence of Phase 1.
The idea is you pass it a dicitonary of parameters you know, and it'll fill out the dictionary
Look at the dictionary paramnames to see what variable options are supported
The variable calculations are stored in the functions after SpreadsheetSovler
An example of how to use this module:

import FirstOrderCalcs as FAC
args = {
        'thrust': 5000 * const.lbToN,  # Newtons
        'time': 30,  # s
        # 'rho_ox' : 1141, #Kg/M^3
        # 'rho_fuel' : 842,
        'pc': 350 * const.psiToPa,
        'pe': 14.7 * const.psiToPa,
        'phi': 1,
        'fuelname': 'Ethanol',
        'oxname': 'LOX',
        'throat_radius_curvature': .02}

    params = FAC.SpreadsheetSolver(args)
"""

import sys
sys.path.insert(1,"./")
import numpy as np
import sympy as sym
import math
import difflib
from rocketcea.cea_obj_w_units import CEA_Obj
import Toolbox.RocketCEAAssister as RA
import Toolbox.IsentropicEquations as IE
from rocketprops.rocket_prop import get_prop
import re as regex
import Toolbox.Constant as const
from scipy import interpolate


def SpreadsheetSolver(args : dict, defaults : dict = None): #defaults can be things like gravity, etc. arguments in spreadsheetsolver are from the dict(? does this mean any dict?)
    paramnames = [ #parameter names
    'thrust', #Newtons
    'time', #s, burn time
    'impulse', #N*s,
    'rho_ox', #Kg/M^3, density of oxidizer
    'rho_fuel', #Kg/M^3, density of fuel
    'pc', #Pa, if cr is specified, this is Pressure at end of combustor
    'pinj',#Pa, only useful if you specify CR, otherwise assumed to be pc, pressure at injector plate
    'pe', #Pa, pressure at nozzle exit
    'g', #m/s^2, gravitational acceleration
    'rm', #o/f by weight, mixture ratio - oxidizer divided by fuel
    'phi', #ratio from stoich (1 is stoich, >1 is fuel rich, used when determing mixture ratio BY WEIGHT)
    'at', # m^2, area of throat
    'rt', # m, radius of throat
    'cr', # contraction ratio
    'rc', # m, combustion chamber radius
    'ac', # m^2, area combustion chamber
    'l_star', # m, chamber volume cc/area throat, characteristic length
    'mol_weight', # kg/mol
    'gamma', # in cc, specific heat ratio
    'gamma_exit', # gamma at exit
    'gamma_throat', # gamma in throat
    'isp', # s
    'temp_c', # K, chamber temp
    'rg', # specific gas constant (SI units if what they are)
    'pr_throat', #Prandtl number in throat
    'rho_throat', #density at throat
    'temp_e', #temperature at exit
    'v_exit', #velocity of exiting gases
    'a_exit', #speed of sound at nozzle exit
    'mach_exit', #nozzle exit mach number
    'temp_throat', #temperature at throat
    'p_throat', # equal to pc^2 divided by Pexit. Not sure why this is happening. It will give us a pressure. @@@@ REVIEW LATER. Pexit at throat should be the result. Check line 272
    'v_throat', #speed of gas at throat. because the flow at throat should be mach 1, we don't multiply the speed of sound at the throat by a mach number
    'mdot', #mass flow rate
    'mdot_ox', #oxidizer mass flow rate
    'mdot_fuel', #fuel mass flow rate
    'er', #nozzle Expansion area Ratio
    'cstar', #characteristic velocity
    'cf', #thrust coefficient
    'c_eff', #not referred to in FAC. May not be used anywhere wip function?
    'rho_av', #not referred to in FAC. May not be used anywhere wip function?
    'vc', #not referred to in FAC. May not be used anywhere wip function?
    'theta_con', #not referred to in FAC. May not be used anywhere wip function?
    'lc', #defined on line 418. check Hazel and Huang pg 73 for more info - this is combustion chamber length.
    'theta_div', #not referred to in FAC. May not be used anywhere wip function?
    'ln_conical', #defined on line 459. used in FINALCONFIGOUTPUT
    'ln_bell', #not referred to in FAC. May not be used anywhere wip function?
    'throat_radius_curvature', #not referred to in FAC. May not be used anywhere wip function?
    'ae', #ae(params) on line 461. area of nozzle exit = area of throat * expansion ratio, or 'ae' = 'at' * 'er'
    're', #defined on line 463 radius of exit
    'nv', #not referred to in FAC. May not be used anywhere wip function?
    'nvstar', #not referred to in FAC. May not be used anywhere wip function?
    'nf', #not referred to in FAC. May not be used anywhere wip function?
    'nw', #not referred to in FAC. May not be used anywhere wip function?
    'fuelname', #name of fuel
    'oxname', #name of oxidizer
    'CEA', #this key's value is actually the object CEA_Obj(...), and the ... holds the values of all the parameters that have been inputted. More on CEA_Obj can be found at RocketCEA
    'pambient', #Pa, ambient pressure
    'cf_efficiency', # Huzel and Huang page 16 - correction factor gives you actual thrust coefficient from ideal thrust coefficient calculated
    'isp_efficiency', # Huzel and Huang page 16 - correction factor gives you actual isp from ideal isp calculated
    'thetac', # converging section angle
    'thetai', # diverging angle at throat
    'thetae', # diverign angle at exit
    'kin_visc_fuel', #defined on line 473... doesn't seem to be used anywhere? function itself seems to be doing stuff.
    'kin_visc_ox', #defined on line 488... function is doing stuff but its not called
    'dyn_visc_fuel', #defined on line 496... function is doing stuff but its not called
    'dyn_visc_ox', #defined on line 510... function is doing stuff but its not called
    'P_tank_ox', #believe this is the pressure of the oxidizer tank. not sure
    'P_tank_fuel', #believe this is the pressure of the fuel tank. not sure
    'numengines', #number of engines
    'propmass']#total propellant mass
#proposal - order these parameters alphabetically?

    params = dict.fromkeys(paramnames) #turns the sequence of parameter names into keys and a dictionary

    params['g'] = 9.81

    #HERE IS WHERE YOU SET DEFAULT VALUES EARLY SO THINGS DONT BREAK IF YOU FORGET TO PASS STUFF
    if params['pambient'] is None:
        params['pambient']=14.7*const.psiToPa #14.7 psi * conversion factor to Pa gives 101,352.972 Pa, standard Earth pressure
    if params['pe'] is None:
        if 'er' not in args.keys() or args['er'] is None: #if there is no area ratio available then we just set nozzle exit pressure to ambient pressure
            params['pe'] = params['pambient']
    if params['cf_efficiency'] is None:
        params['cf_efficiency'] = .95 #automatically assumes thrust coefficient correction factor is .95
    if params['isp_efficiency'] is None:
        params['isp_efficiency'] = .9 #automatically assumes isp correction factor is .9

    for arg in list(args): #checks each arg for errors/exceptions
        try:
            params[arg] = args[arg] #this sets arg in params equal to arg in args
        except:
            try:
                print("Parameter " + arg + " isn't supported or is mispelled. Did you mean " +
                      difflib.get_close_matches(arg, paramnames)[0] + "? That's what I'm going to use!")
                params[difflib.get_close_matches(arg, paramnames)[0]] = args[arg]
            except:
                print("Parameter" + arg + "isn't supported or is mispelled")

    if params['CEA'] is None: # need to have cea object to do other stuff sio make sure to get this done first
        try: # fuel should be in format "Ethanol_65" for 65% ethanol, 35% water
            RA.makeEthanolBlend(int(regex.search(r'\d+', params['fuelname']).group()))
        except:
            print("fuel is " + params['fuelname'])
        if params['cr'] is None:
            if params['rc'] is None:
                params['CEA'] = CEA_Obj(oxName=params['oxname'], fuelName=params['fuelname'], useFastLookup=1, isp_units='sec', cstar_units='m/s',
                                        pressure_units='Pa', temperature_units='K', sonic_velocity_units='m/s',
                                        enthalpy_units='J/kg', density_units='kg/m^3', specific_heat_units='J/kg-K',
                                        viscosity_units='millipoise', thermal_cond_units='W/cm-degC', fac_CR=None,
                                        make_debug_prints=False) #defines basis we're going off in CEA calculator for later use of CEA_Obj as a base function. more information on RocketCEA website
                if params['pe'] is None:
                    if params['rm'] is None:
                        params['rm'] = rm(params)
                        params['pe'] = pe(params)
                    else:
                        params['pe'] = pe(params)
            else:
                params['CEA'] = CEA_Obj(oxName=params['oxname'], fuelName=params['fuelname'], useFastLookup=1, isp_units='sec', cstar_units='m/s',
                                        pressure_units='Pa', temperature_units='K', sonic_velocity_units='m/s',
                                        enthalpy_units='J/kg', density_units='kg/m^3', specific_heat_units='J/kg-K',
                                        viscosity_units='millipoise', thermal_cond_units='W/cm-degC', fac_CR=None,
                                        make_debug_prints=False)
                # here we calculate a bunch of stuff assuming ideal, then calculate cr, then make a new cea object with that cr

                togglerm = False
                toggleer = False
                togglerc = False
                if params['rm'] is None:
                    params['rm'] = rm(params)
                    togglerm = True
                if params['pe'] is None:
                    params['pe'] = pe(params)
                if params['pc'] is None:
                    params['pc'] = pc(params)

                if params['er'] is None:
                    params['er'] = er(params)
                    toggleer = True
                if params['rc'] is None:
                    params['rc'] = rc(params)
                    togglerc = True
                molandgam = params['CEA'].get_Chamber_MolWt_gamma(Pc=params['pc'], MR=params['rm'], eps=params['er']),  # kg/mol, from rocketcea, Pc = combustion end pressure, MR = mixing ratio, eps = Nozzle Expansion Area Ratio
                params['mol_weight'] = molandgam[0][0]
                params['gamma'] = molandgam[0][1]
                if params['cf'] is None:
                    params['cf'] = cf(params)
                if params['at'] is None:
                    params['at'] = at(params)
                if params['ac'] is None:
                    params['cr'] = (math.pi*params['rc']**2)/at(params)
                else:
                    params['cr'] = (params['ac'])/at(params)
                params['CEA'] = CEA_Obj(oxName=params['oxname'], fuelName=params['fuelname'],useFastLookup=1,  isp_units='sec',
                                        cstar_units='m/s',
                                        pressure_units='Pa', temperature_units='K', sonic_velocity_units='m/s',
                                        enthalpy_units='J/kg', density_units='kg/m^3', specific_heat_units='J/kg-K',
                                        viscosity_units='millipoise', thermal_cond_units='W/cm-degC', fac_CR=params['cr'],
                                        make_debug_prints=False)
                params['cf'] = None
                params['at'] = None
                if togglerm:
                    params['rm'] = None
                if toggleer:
                    params['er'] = None
                if togglerc:
                    params['rc'] = None

                PinjOverPcombEstimate = 1.0 + 0.54 / params['cr'] ** 2.2 # FROM https://rocketcea.readthedocs.io/en/latest/finite_area_comb.html
                params['pinj']=params['pc']*params['CEA'].cea_obj.get_Pinj_over_Pcomb(
                    Pc=params['CEA'].Pc_U.uval_to_dval(params['pc'])*PinjOverPcombEstimate, MR=1.0, fac_CR=params['cr'])

                params['cr'] = None
                if params['pe'] is None:
                        if params['rm'] is None:
                            params['rm'] = rm(params)
                            params['pe'] = pe(params)
                        else:
                            params['pe'] = pe(params)

        else:
            params['CEA'] = CEA_Obj(oxName=params['oxname'], fuelName=params['fuelname'],useFastLookup=1,  isp_units='sec',
                                    cstar_units='m/s',
                                    pressure_units='Pa', temperature_units='K', sonic_velocity_units='m/s',
                                    enthalpy_units='J/kg', density_units='kg/m^3', specific_heat_units='J/kg-K',
                                    viscosity_units='millipoise', thermal_cond_units='W/cm-degC', fac_CR=params['cr'],
                                    make_debug_prints=False)
            PinjOverPcombEstimate = 1.0 + 0.54 / params['cr'] ** 2.2 # FROM https://rocketcea.readthedocs.io/en/latest/finite_area_comb.html
            params['pinj']=params['pc']*params['CEA'].cea_obj.get_Pinj_over_Pcomb(
                Pc=params['CEA'].Pc_U.uval_to_dval(params['pc'])*PinjOverPcombEstimate, MR=1.0, fac_CR=params['cr'])
            if params['pe'] is None:
                    if params['rm'] is None:
                        params['rm'] = rm(params)
                        params['pe'] = pe(params)
                    else:
                        params['pe'] = pe(params)

        if params['rm'] is None:
            params['rm'] = rm(params)
        if params['pc'] is None:
            params['pc'] = pc(params)
        if params['er'] is None:
            params['er'] = er(params)


        molandgam = params['CEA'].get_Chamber_MolWt_gamma(Pc=params['pc'], MR=params['rm'], eps=params['er']),  # kg/mol
        params['mol_weight'] = molandgam[0][0]
        params['gamma'] = molandgam[0][1]
        molandgam = params['CEA'].get_exit_MolWt_gamma(Pc=params['pc'], MR=params['rm'], eps=params['er']),  # kg/mol
        params['gamma_exit'] = molandgam[0][1]  # in exit
        molandgam = params['CEA'].get_Throat_MolWt_gamma(Pc=params['pc'], MR=params['rm'], eps=params['er']),  # kg/mol
        params['gamma_throat'] = molandgam[0][1]
        temps = params['CEA'].get_Temperatures(Pc=params['pc'], MR=params['rm'], eps=params['er'], frozen=0,
                                               frozenAtThroat=0)
        params['isp'] = params['isp_efficiency']*\
        params['CEA'].estimate_Ambient_Isp(Pc=params['pc'], MR=params['rm'], eps=params['er'], Pamb=params['pambient'],
                                           frozen=0, frozenAtThroat=0)[0]
        params['temp_c'] = temps[0]
        throatTrasnport = params['CEA'].get_Throat_Transport(Pc=params['pc'], MR=params['rm'], eps=params['er'],
                                                             frozen=0)
        params['rg'] = const.R/ params['mol_weight'],  # specific gas constant (SI units if what they are)
        params['pr_throat'] = throatTrasnport[3] #Prandtl no.
        params['rho_throat'] = \
        params['CEA'].get_Densities(Pc=params['pc'], MR=params['rm'], eps=params['er'], frozen=0, frozenAtThroat=0)[1]
        params['temp_e'] = temps[2]
        sonicvelos = params['CEA'].get_SonicVelocities(Pc=params['pc'], MR=params['rm'], eps=params['er'], frozen=0,
                                                       frozenAtThroat=0)
        params['mach_exit'] = params['CEA'].get_MachNumber(Pc=params['pc'], MR=params['rm'], eps=params['er'], frozen=0,
                                                           frozenAtThroat=0)

        params['a_exit'] = sonicvelos[2]
        params['v_exit'] = params['mach_exit'] * params['a_exit']

        params['temp_throat'] = temps[1]
        params['p_throat'] = params['pc']*params['CEA'].get_Throat_PcOvPe(Pc=params['pc'], MR=params['rm']) #Pc^2 divided by Pressure at exit of throat is the result. Should be Pressure at exit of throat, so the multiply sign should be a divide sign
        params['v_throat'] = sonicvelos[1]

        chambertransport = params['CEA'].get_Chamber_Transport(Pc=params['pc'], MR=params['rm'], eps=params['er'], frozen=0)
        params['prns'] = chambertransport[3]
        params['viscosityns'] = chambertransport[1]*10**(-6)
        params['cpns'] = chambertransport[0]

        params['cstar'] = params['isp_efficiency']*params['CEA'].get_Cstar(Pc=params['pc'], MR=params['rm'])

    for param in list(params):
        if params[param] is None:
            try:
                params[param] = globals()[param](params)
            except:
                print('Couldnt calculate ' + param + " first time around")


    #Do this many times so that if we need calcualted values for other values we can get them the second time around
    changecount = -1
    attempts = 0
    while not changecount == 0 and attempts <= 5:
        changecount = 0
        attempts += 1
        for param in list(params):
            if params[param] is None:
                try:
                    params[param] = globals()[param](params)
                    changecount += 1
                except:
                    pass
    for param in list(params):
        if params[param] is None:
            try:
                params[param] = globals()[param](params)
            except:
                print(param + " not yet supported")
    return params

# Below are all the functions, pulled from various textbooks.
# For some variables, there are multiple ways of calculating depending on
# what inputs are provided. If your input combo is not supported, feel
# free to add edge cases using if statements, or add clutter to these functions.
# Anything that can be solved with a quick anaylitcal calucaltion should go here.
def thrust(params):
    try:
        return params['mdot']*9.81*params['isp']
    except:
        print('Could not calculate Thrust')
        return None
def time(params): #s
    try:
        return params['propmass']/params['mdot']/params['numengines']
    except:
        pass
    try:
        return params['impulse']/params['thrust']
    except:
        print('Could not calculate time')
        return None
def impulse(params): #N*s
    try:
        return params['thrust']*params['time']
    except:
        print('Could not calculate impulse')
        return None
def rho_ox(params): #Kg/M^3 IMPLEMENT THIS USING FLUID PROPS
    try:
        pObj = get_prop(params['oxname'])
        if params['P_tank_ox'] is None:
            return 1000 *pObj.SG_compressed(pObj.TdegRAtPsat(40),
                                  params['pc'] / const.psiToPa)
        else:
            return 1000*pObj.SG_compressed(pObj.TdegRAtPsat(40),
                                  params['P_tank_ox'] / const.psiToPa)
    except:
        print("rocketProps busted lol")
    return None
def rho_fuel(params): #Kg/M^3MPLEMENT THIS USING FLUID PROPS
    try:
        pObj = get_prop(params['fuelname'])
        sattemp = pObj.TdegRAtPsat(40)
        if sattemp < 293:
            temp=sattemp/const.degKtoR
        else:
            temp = 293

        if params['P_tank_fuel'] is None:
            return 1000 * pObj.SG_compressed(temp*const.degKtoR,
                                            params['pc'] / const.psiToPa)
        else:
            return 1000 * pObj.SG_compressed(temp*const.degKtoR,
                                            params['P_tank_fuel'] / const.psiToPa)
    except AttributeError:
        print('Fuel does not exist, assuming its a water ethanol blend')
        ethpercent = int(regex.search(r'\d+', params['fuelname']).group())/100
        pObj = get_prop("ethanol")
        ethdens = 1000 * pObj.SG_compressed(293*const.degKtoR,
                                         params['pc'] / const.psiToPa)
        pObj = get_prop("water")
        waterdens = 1000 * pObj.SG_compressed(293 * const.degKtoR,
                                            params['pc'] / const.psiToPa)
        return ethpercent*ethdens +(1-ethpercent)*waterdens
    except:
        print("rocketProps busted lol")
    return None
def pc(params): #Pa, calculate using throat conditions and backtrack
    print('You should input PC, will set up calculator later, now its just 700 psi (4.82 mpa)')
    return 700*6894.76
def pe(params): #Pa, this is only called if you specified an er and want to get a exit ressure for it
    return params['pc']/params['CEA'].get_PcOvPe(Pc=params['pc'], MR=params['rm'], eps=params['er'], frozen=0, frozenAtThroat=0)
def g(params): #m/s^2 his hsould never be called
    print('this should not be called this is a default value')
def rm(params): #o/f by weight
    try:
        return params['CEA'].getMRforER(ERphi=params['phi'])
    except:
        print('INSTALL ROCKETCEA IDIOT')



def phi(params): #ratio from stoich (1 is stoich, >1 is fuel rich)
    temp = params['CEA'].get_eqratio(Pc=params['pc'], MR=params['rm'])
    return temp[0]
def at(params): # m^2, area of throat assume choked at throat
    #return IE.AreaForChokedFlow(params['p_throat'],params['temp_throat'],params['gamma_throat'],params['mdot'], const.R/params['mol_weight'])
    if params['cr'] is None:
        #return IE.AreaForChokedFlow( IE.totalP(params['p_throat'],params['gamma_throat'],1), IE.totalT(params['temp_throat'],params['gamma_throat'],1) ,params['gamma_throat'], params['mdot'],
        #                        const.R / params['mol_weight']*1000)
        return params['thrust'] / params['cf'] / params['pc']
    else:
        #return IE.AreaForChokedFlow( IE.totalP(params['pc'],params['gamma'],IE.machFromP(params['pinj'],params['pc'],params['gamma'])),
        #                            IE.totalT(params['temp_c'],params['gamma'],IE.machFromP(params['pinj'],params['pc'],params['gamma'])) ,params['gamma_throat'], params['mdot'],
        #                      const.R / params['mol_weight']*1000)
        return params['thrust']/params['cf']/params['pc']
def rt(params): # m, radius of throat
    return math.sqrt(params['at']/const.pi)
"""THESE NEXT THREE ARE SUPER PRELIMINARY SIZINGS BASED OFF OF DIAGRAMS IN HUZEL AND HUANG PAGE 73"""
def cr(params): # contraction ratio
    if params['rc'] is None:
        CRInterpolator = interpolate.interp1d([i*const.inToM for i in [.2, .5, 1, 2, 5]],
                                            [i*const.inToM for i in [15, 9, 5.5, 4, 3]], kind='linear') #CR vs Throat Diam, visually copied from textbook
        print(CRInterpolator(params['rt']*2))
        return CRInterpolator(params['rt']*2)
    else:
        return params['rc']**2/(params['rt']**2)
def lc(params): #this actually gives lc a value - lc is combustion chamber length
    CLInterpolator = interpolate.interp1d([i * const.inToM for i in [.2, .5, 1, 2, 5, 10]],
                                          [i * const.inToM for i in [1.8,3,4,5,7.5, 10]],
                                          kind='linear')  # CL vs Throat Diam, visually copied from textbook
    return CLInterpolator(params['rt'] * 2)
def rc(params): # m, combustion chamber radius
    if params['cr'] is None:
        return math.sqrt(params['l_star']*params['at']/(params['lc']*const.pi))
    else:
        return math.sqrt(params['at']*params['cr']/const.pi)
def ac(params): # m^2, area combustion chamber
    if params['cr'] is None:
        return const.pi*(params['l_star'] * params['at'] / (params['lc']))
    else:
        return params['at']*params['cr']
def l_star(params): # m, volume cc/area throat
    return 40*const.inToM # THIS IS KERALOX LSTAR FROM HUZEL AND HUANG PAGE 72 WE HSOULD DO MORE RESEARCH
def mdot(params): #mass flow rate
    return params['thrust']/params['isp']/(const.gravity)
def mdot_ox(params): #oxidizer mass flow rate
    return params['rm']*params['mdot']/(params['rm']+1)
def mdot_fuel(params): #fuel mass flow rate
    return params['mdot']/(params['rm']+1)
def er(params):
    if params['pe'] < 10000:
        print("Noone ever expands completely to vacuum! Just input an ER, going to assume youre exapnding to 10000 pa for now")
        params['pe'] =10000
    return params['CEA'].get_eps_at_PcOvPe(Pc=params['pc'], MR=params['rm'], PcOvPe=params['pc']/params['pe'], frozen=0, frozenAtThroat=0)
    Me = (((params['pe']/params['pc'])**((1-params['gamma'])/params['gamma'])-1)*2/(params['gamma']-1))**.5
    er = ((params['gamma']+1)/2)**((-params['gamma']+1)/(2*(params['gamma']-1)))*((1+(params['gamma']-1)/2*(me**2))**((params['gamma']+1)/(2*(params['gamma']-1))))/me

def cf(params):
    return params['cf_efficiency']*((2*params['gamma']**2)/(params['gamma']-1)*(2/(params['gamma']+1))**((params['gamma']+1)/(params['gamma']-1))*(1-(params['pe']/params['pc'])**((params['gamma']-1)/params['gamma'])))**.5+params['er']*(params['pe']-params['pambient'])/params['pc']
"""def c_eff(params):
def rho_av(params):
def vc(params): 
def theta_con(params):
def theta_div(params):

def ln_bell(params):
"""
def ln_conical(params): #is this guy used anywhere bruh
    return (params['re']-params['rt'])/math.sin(15*math.pi/180)
def ae(params):
    return params['at']*params['er']
def re(params):
    return math.sqrt(params['at']*params['er']/const.pi)
"""
def nv(params):
def nvstar(params):
def nf(params):
def nw(params):
def fuelname(params):
def oxname(params):
"""
def kin_visc_fuel(params):
    if not (get_prop(params['fuelname']) is None):
        pObj = get_prop(params['fuelname'])
        ethpercent = None
        pObjWater = None
    else:
        try:
            print('Fuel does not exist, assuming its a water ethanol blend')
            ethpercent = int(regex.search(r'\d+', params['fuelname']).group()) / 100
            pObj = get_prop("ethanol")
            pObjWater = get_prop("water")
        except:
            print("rocketProps busted lol")
    return viscosityfunc(293,  pObj, pObjWater, ethpercent)/params['rho_fuel'] # reutning this is Pa s m3/kg

def kin_visc_ox(params):
    try:
        pObj = get_prop(params['oxname'])
        ethpercent = None
        pObjWater = None
    except:
        print("rocketProps cant find ox")
    return viscosityfunc(293,  pObj, pObjWater, ethpercent)/params['rho_ox'] # reutning this is Pa s m3/kg
def dyn_visc_fuel(params):
    if not (get_prop(params['fuelname']) is None):
        pObj = get_prop(params['fuelname'])
        ethpercent = None
        pObjWater = None
    else:
        try:
            print('Fuel does not exist, assuming its a water ethanol blend')
            ethpercent = int(regex.search(r'\d+', params['fuelname']).group()) / 100
            pObj = get_prop("ethanol")
            pObjWater = get_prop("water")
        except:
            print("rocketProps busted lol")
    return viscosityfunc(293,  pObj, pObjWater, ethpercent) # reutning this is Pa s
def dyn_visc_ox(params):
    try:
        pObj = get_prop(params['oxname'])
        ethpercent = None
        pObjWater = None
    except:
        print("rocketProps cant find ox")
    return viscosityfunc(293,  pObj, pObjWater, ethpercent) # reutning this is Pa s

def viscosityfunc(    temp, pObj, pObjWater, ethpercent):
    if ethpercent is None:
        return .1 * pObj.ViscAtTdegR(temp * const.degKtoR)
    else:

        viscosityeth = .1 * pObj.ViscAtTdegR(temp * const.degKtoR)
        viscositywater = .1 * pObjWater.ViscAtTdegR(temp * const.degKtoR)

        return  ethpercent * viscosityeth + (1 - ethpercent) * viscositywater




def propmass(params):
    return params['mdot']*params['time']






