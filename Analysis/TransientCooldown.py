"""Just a place to run stuff, currently has some test code
usefull as it has a bunch of commonly used import statements
CURRENT CONFIGURATION: FIRST ORDER SIZINGS FOR MID AUTUMN 2022"""
import sys
sys.path.insert(1,"./")
import scipy.optimize
#from Components.ThrustChamber import ThrustChamber
from rocketcea.cea_obj import add_new_fuel, add_new_oxidizer, add_new_propellant
import numpy as np
import math
import Components.ThrustChamber as ThrustChamber
import Components.CoolingSystem as CS
from rocketcea.cea_obj_w_units import CEA_Obj
import Toolbox.RListGenerator as RListGenerator
from matplotlib import cm
import Toolbox.RocketCEAAssister as RA
import os
import Toolbox.IsentropicEquations as IE
import Toolbox.RocketEquation as RE
import difflib
import re as regex
from rocketprops.rocket_prop import get_prop
import Toolbox.Constant as const
import DetermineOptimalMR as DOMR
import matplotlib.pyplot as plt
import FirstOrderCalcs as FAC
import Components.ThrustChamber as ThrustChamber
import Components.StructuralApproximation as SA
from scipy.optimize import minimize_scalar
from Toolbox import PressureDropCalculator as PD
import Toolbox.CADAssistant as CAD

def fixedRSquareChanelSetup(params,xlist, rlist,chlist,chanelToLandRatio,twlist,nlist,helicitylist = None,dxlist = None):# MAKE SURE TO PASS SHIT  ALREADY FLIPPED
    if helicitylist is None:
        helicitylist = np.ones(np.size(xlist))*math.pi/2
    if dxlist is None:
        dxlist=np.ones(np.size(xlist))
        index = 1
        while index<np.size(xlist):
            dxlist[index]=abs(xlist[index-1]-xlist[index])
            index = index+1
        dxlist[0]=dxlist[1] # this is shit, but I actuall calculate an extra spatial step at the start for some reason, so our CC is 1 dx too long. Makes the graphs easier to work with tho lol, off by one error be damned

    #FOR NOW THIS IS ASSUMING SQUARE CHANELS!
    #\     \  pavail\     \ 
    # \     \ |----| \     \
    #  \     \        \     \
    #   \     \        \     \
    # sin(helicitylist) pretty much makes sure that we are using the paralax angle to define the landwidth
    perimavailable = math.pi*2*(rlist+twlist)/nlist*np.sin(helicitylist)
    landwidthlist=perimavailable/(chanelToLandRatio+1)
    cwlist=perimavailable-landwidthlist

    alistflipped=chlist*cwlist
    salistflipped=cwlist/dxlist
    vlistflipped = params['mdot_fuel'] / params['rho_fuel'] / alistflipped / nlist
    #if np.min(cwlist/chlist)>10:
    #    raise Exception(f"Aspect Ratio is crazyyyyy")

    hydraulicdiamlist=4*alistflipped/(2*chlist+2*cwlist)
    coolingfactorlist = np.ones(xlist.size)
    heatingfactorlist = np.ones(xlist.size)*.6 # .6 is from cfd last year, i think its bs but whatever
    """Fin cooling factor func is 2*nf*CH+CW. nf is calculated as tanh(mL)/ml. Ml is calculated as sqrt(hpL^2/ka),
    h=hc, P=perimeter in contact with coolant = dx, A = dx*landwidth/2 (assuming only half the fin works on the coolant, 2* factor in other spot,
    I think I can do that because of axisymmetric type), k=kw, L=height of fin = chanel height
    This is all from "A Heat Transfer Textbook, around page 166 and onwards."""
    fincoolingfactorfunc = lambda hc,kw,ind : (math.tanh(chlist[ind]*math.sqrt(2*hc/kw*landwidthlist[ind]))/\
            (chlist[ind]*math.sqrt(2*hc/kw*landwidthlist[ind])))*2*chlist[ind] + cwlist[ind]

    return alistflipped, nlist, coolingfactorlist, heatingfactorlist, xlist, vlistflipped, twlist, hydraulicdiamlist, salistflipped, dxlist, fincoolingfactorfunc, cwlist

def RunCoolingSystemTransient(chlist,
twlist,
nlist,
helicitylist,
params,
xlist,
rlist,
chanelToLandRatio, 
TC ):

    machlist,preslist,templist = TC.flowSimple(params)
    alistflipped, nlist, coolingfactorlist, heatingfactorlist, xlist, vlistflipped, twlistflipped,\
     hydraulicdiamlist, salistflipped, dxlist, fincoolingfactorfunc, cwlist   = fixedRSquareChanelSetup(params = params,
                                        xlist = np.flip(xlist), rlist = np.flip(rlist),chlist = chlist ,
                                        chanelToLandRatio = chanelToLandRatio ,twlist = twlist ,nlist = nlist,
                                        helicitylist=helicitylist)

    Twgmat, hgmat, Qdotmat, Twcmat, hcmat, Tcmat, coolantpressuremat, qdotmat, fincoolingfactormat, rhomat, viscositymat, Remat, time = CS.transientTemperature(
        None, TC, params, salistflipped, nlist, coolingfactorlist,
        heatingfactorlist, xlist, vlistflipped, 293, params['pc'] + params['pc']*.2 + 50*const.psiToPa, twlistflipped, hydraulicdiamlist, rgaslist = rlist, fincoolingfactorfunc=fincoolingfactorfunc, dxlist = dxlist)

    material = "inconel 715"
    #Structure = CS.StructuralAnalysis(rlist, xlist, nlist, chlist, cwlist, twlist, material)
    FOSlist = xlist# Structure.FOS(Twglist,Twclist,coolantpressurelist,preslist)
    xlist=np.flip(xlist) #idk whats flipping this haha but its something in the steadystatetemps function, so we have to flip it back
    return alistflipped, xlist, vlistflipped,\
     hydraulicdiamlist, salistflipped, dxlist, fincoolingfactorfunc, cwlist,\
        Twgmat, hgmat, Qdotmat, Twcmat, hcmat, Tcmat, coolantpressuremat, qdotmat, fincoolingfactormat, rhomat, viscositymat, Remat,\
            FOSlist, time

args = {
        'thrust': 1200 * const.lbToN,  # Newtons
        'time': 7.5,  # s
        # 'rho_ox' : 1141, #Kg/M^3
        # 'rho_fuel' : 842,
        'pc': 300 * const.psiToPa,
        'pe': 10 * const.psiToPa,
        'phi':1,
       # 'cr': 5.295390217,
        'lstar': 1.24,
        'fuelname': 'Ethanol_75',
        'oxname': 'N2O',
        'throat_radius_curvature': .0254 *2,
        'dp': 150 * const.psiToPa,
        'impulseguess' :  495555.24828424345,
        'rc' : .08,
        'thetac' : (35*math.pi/180),
        'isp_efficiency' : .9} #623919}
configtitle = "Subscale 3_29_23"
output=True


# FIRST DETERMINE INITIAL ESTIMATES FOR IDEAL PARAMS
path=os.path.join( "Configs",configtitle)
if output:
    os.makedirs(path,exist_ok=True)
ispmaxavg, mrideal, phiideal, ispmaxeq, ispmaxfrozen = DOMR.optimalMr(args, plot=output)
if output:
    plt.savefig(os.path.join(path, "idealisp.png"))
print(f"isp max = {ispmaxavg}, ideal mr is {mrideal}")
args['rm']=mrideal
params = FAC.SpreadsheetSolver(args)

# get pressure drop



dt=.025

#params['thrust'] = totalmass*thrusttoweight_approx*9.81 #recompute with a resonable thrust
params = FAC.SpreadsheetSolver(args)
miapprox,lambdainit,totalmass, wstruct, newheight, heightox, heightfuel, vol_ox, vol_fuel, P_tank  = SA.mass_approx(params['pc'],params['dp'], 12, params['rho_fuel'],params['rho_ox'], params['thrust'], params['isp'], params['time'], params['rm'])
L, hlist, vlist, thrustlist, isplist, machlist =\
    RE.rocketEquationCEA(params, mi = miapprox, thrust = params['thrust'], burntime = params['time'],\
         L = None, H = None, dt=dt, Af=None, ispcorrection = None)
newargs = {
    'thrust': params['thrust'],  # Newtons
    'time': params['time'],  # s
    'pc': params['pc'],
    'pe': params['pe'],
    'rm' : params['rm'],
    'rc': params['rc'],
    'lstar': params['lstar'],
    'fuelname': params['fuelname'],
    'oxname': params['oxname'],
    'throat_radius_curvature': params['throat_radius_curvature'],
    'dp': params['dp'],
    'isp_efficiency' : params['isp_efficiency']}
params = FAC.SpreadsheetSolver(newargs)
# now do it again with cr instead of rc to get all the specific values for finite combustors
newargs = {
    'thrust': params['thrust'],  # Newtons
    'time': params['time'],  # s
    'pc': params['pc'],
    'pe': params['pe'],
    'rm' : params['rm'],
    'cr': params['cr'],
    'lstar': params['lstar'],
    'fuelname': params['fuelname'],
    'oxname': params['oxname'],
    'throat_radius_curvature': params['throat_radius_curvature'],
    'dp': params['dp'],
    'isp_efficiency' : params['isp_efficiency']}
params = FAC.SpreadsheetSolver(newargs)

if output:
    with open(os.path.join(path, "mass_output.txt"), "w") as f:
        print(f"This is supposed to be a CSV! Eventually it should be passed params and get all that data too!", file=f)
            #overwriting current file
mis, lambdas, totalmasses, wstruct, newheight, heightox, heightfuel, vol_ox, vol_fuel, P_tank = \
    SA.mass_approx(params['pc'], params['dp'], 12, params['rho_fuel'], params['rho_ox'],
                                                params['thrust'], params['isp'], params['time'], params['rm'],
                printoutput=output, outputdir=path)
if output:
    with open(os.path.join(path, "mass_output.txt"), "a") as f:
        for param in list(params):
            if params[param] is None:
                print(param + f", NONE", file=f)
            else:
                #try:
                #    print(param + f", " +'%.3f'%(params[param]), file=f)
                #except:
                print(param + f", {params[param]}", file=f)
        print(f"Deltav, {params['isp']*9.81*math.log(1/L)}", file=f)
    title = f"Fuel = {params['fuelname']}, " \
            f"Ox = {params['oxname']}, " \
            f"mi = {int(((1 / lambdas) * params['mdot'] * params['time'] - params['mdot'] * params['time']))}," \
            f" mp = {int(params['mdot'] * params['time'])}, " \
            f"Mtotal = {int((1 / lambdas) * params['mdot'] * params['time'])}"
    RE.ShitPlotter(hlist, vlist, thrustlist, isplist, machlist, time=params['time'], title=title, dt=dt)
    plt.savefig(os.path.join(path, "trajectory.png"))
### Now that we have the "optimal rocket", figure out flow and wall temps

#conevol = math.pi*params['rc']**3*math.tan(params['thetac'])/3 - math.pi*params['rt']**3*math.tan(params['thetac'])/3
if params['thetac'] is None:
    params['thetac'] = math.pi*35/180
volfunc = lambda lc : math.pi*params['rc']**2*lc  +\
    math.pi*params['rc']**3/math.tan(params['thetac'])/3 -\
        math.pi*params['rt']**3/math.tan(params['thetac'])/3
lstarminimizer = lambda lc : volfunc(lc)/(params['rt']**2*math.pi) - params['lstar']
result = scipy.optimize.root(lstarminimizer, .05, args=(), method='hybr', jac=None, tol=None, callback=None, options=None)
params['lc']=result['x'][0]
xlist = np.linspace(0, params['lc'] + (params['rc'] - params['rt']) / math.tan(params['thetac']) + params['ln_conical'], 100)
    
rlist,xlist = RListGenerator.paraRlist(xlist, params['lc'], params['rc'],
                                params['lc'] + (params['rc'] - params['rt'])/(math.tan(params['thetac'])),
                                params['rt'],
                                params['lc'] + (params['rc'] - params['rt'])/(math.tan(params['thetac'])) + params['ln_conical'],
                                params['re'], params['lc']*1.5, .0254*1.5, .0254*.4, math.pi/6, 8*math.pi/180, params['er'])  # xlist, xns, rc, xt, rt, xe, re
# xlist, xns, rc, xt, rt_sharp, xe_cone, re_cone, rcf, rtaf, rtef, thetai, thetae, ar

params['mdot_fuel'] = params['mdot_fuel']*2 #we are dumpong half the fuel

TC = ThrustChamber.ThrustChamber(rlist,xlist)
print(TC.rt, TC.xt, TC.xns)

machlist,preslist,templist = TC.flowSimple(params)
xlistflipped = np.flip(xlist)
rlistflipped  = np.flip(rlist)
chlist  = (TC.rt/rlistflipped)**.5*.003 
twlist  = (rlistflipped/TC.rt)*.001 
nlist  = np.ones(len(xlist))*44
ewlist  = np.ones(len(xlist))*.005
#HELICITY IS DEFINED AS 90 DEGREES BEING A STAIGHT CHANEL, 0 DEGREES BEING COMPLETILY CIRCUMFRNEITAL
helicitylist  = (rlistflipped**1.5/TC.rt**1.5)*45*math.pi/180
#chanelToLandRatio = 2



for index in range(0,np.size(helicitylist )):
    if helicitylist [index]>math.pi/2:
        helicitylist [index] = math.pi/2

perimavailable = math.pi*2*(np.flip(rlist)+twlist)/nlist*np.sin(helicitylist)

chanelToLandRatio=2#1/(1-min(cwlist_full)/min(perimavailable))-1#

alistflipped, xlist, vlistflipped,\
    hydraulicdiamlist, salistflipped, dxlist, fincoolingfactorfunc, cwlist,\
        Twgmat, hgmat, Qdotmat, Twcmat, hcmat, Tcmat, coolantpressuremat, qdotmat, fincoolingfactormat, rhomat, viscositymat, Remat, FOSlist, time = RunCoolingSystemTransient(chlist,
twlist,
nlist,
helicitylist,
params,
xlist,
rlist,
chanelToLandRatio, 
TC )


xlist = np.flip(xlist)
plt.figure()
for sec in range(math.ceil(Twgmat.shape[0]/10)):
    plt.plot(xlist,Twgmat[sec*10,:], label=f"time = {sec} secs")
plt.plot(xlist,Twgmat[Twgmat.shape[0]-1,:], label =f"final, time = {Twgmat.shape[0]/10} secs")
plt.title(f"Gas Side Wall Temp Curves")
plt.xlabel("TC Position [m]")
plt.ylabel("Temp [K]")
plt.legend()


plt.figure()
for sec in range(math.ceil(Twgmat.shape[0]/10)):
    plt.plot(xlist,Twcmat[sec*10,:], label=f"time = {sec} secs")
plt.plot(xlist,Twcmat[Twgmat.shape[0]-1,:], label =f"final, time = {Twgmat.shape[0]/10} secs")
plt.title(f"Coolant Side Wall Temp Curves")
plt.xlabel("TC Position [m]")
plt.ylabel("Temp [K]")
plt.legend()



plt.figure()
for sec in range(math.ceil(Twgmat.shape[0]/10)):
    plt.plot(xlist,Tcmat[sec*10,:], label=f"time = {sec} secs")
plt.plot(xlist,Tcmat[Twgmat.shape[0]-1,:], label =f"final, time = {Twgmat.shape[0]/10} secs")
plt.title(f"Coolant Temp Curves")
plt.xlabel("TC Position [m]")
plt.ylabel("Temp [K]")
plt.legend()
plt.show()



if output:
    #Twglist, hglist, qdotlist, Twclist, hclist, Tclist, coolantpressurelist, qdotlist, Trlist, rholist, viscositylist, Relist = CS.steadyStateTemperatures(None,TC, params, salistflipped,n, coolingfactorlist,
    #                        heatingfactorlist, xlistflipped, vlistflipped ,293, params['pc']+params['dp'][0], twlistflipped, hydraulicdiamlist)

    title="ChamberTemps"
    fig, axs = plt.subplots(3,3)
    fig.suptitle(title)

    axs[0,1].plot(xlistflipped,hglist , 'g')  # row=0, column=0
    axs[1,1].plot(xlistflipped,hclist , 'r')# row=1, column=0
    axs[2,1].plot(np.hstack((np.flip(TC.xlist),xlist)),np.hstack((np.flip(rlist),-rlist)) , 'k') # row=0, column=0


    axs[0,1].set_title('hglist')
    axs[1,1].set_title('hclist')
    axs[2,1].set_title('Thrust Chamber Shape')

    axs[0,0].plot(xlistflipped,Twglist , 'g', label="Gas Side Wall Temp")
    axs[0,0].plot(xlistflipped,Twclist , 'r', label="CoolantSide Wall Temp") # row=0, column=0
    axs[0,0].plot(xlistflipped,Tclist , 'b', label="Coolant Temp") #
    axs[1,0].plot(xlistflipped,Tclist , 'r')# row=1, column=0
    axs[2,0].plot(xlistflipped,hydraulicdiamlist , 'r')# row=1, column=0

    axs[0,0].set_title('Twg')
    axs[1,0].set_title('Tc')
    axs[2,0].set_title('hydraulicdiam')
    axs[0,0].legend()

    axs[0,2].plot(xlistflipped,Twglist*const.degKtoR-458.67 , 'g', label="Gas Side Wall Temp, F")
    #axs[0,2].plot(xlistflipped,Tcoatinglist*const.degKtoR-458.67 , 'k', label="Opposite side of coating Temp, F")
    axs[0,2].plot(xlistflipped,Twclist * const.degKtoR-458.67, 'r', label="CoolantSide Wall Temp, F") # row=0, column=0

    axs[0,2].plot(xlistflipped,Tclist * const.degKtoR-458.67, 'b', label="Coolant Temp, F") #
    axs[1,2].plot(xlistflipped,coolantpressurelist /const.psiToPa, 'k')
    axs[2,2].plot(xlistflipped,rholist, 'k') # row=0, column=0

    axs[0,2].set_title('Twg')
    axs[1,2].set_title('coolantpressure (psi)')
    axs[2,2].set_title('density of coolant')
    axs[0,2].legend()
    plt.savefig(os.path.join(path, "temperatures.png"))
    print(f"max twg = {np.max(Twglist)} in kelvin, {np.max(Twglist)*const.degKtoR} in Rankine (freedom)\n max Twc ="
            f" {np.max(Twclist)} in kelvin, {np.max(Twclist)*const.degKtoR} in Rankine (freedom)")
    # Hide x labels and tick labels for top plots and y ticks for right plots.

    title="Flow properties along thrust chamber"
    fig1, axs1 = plt.subplots(4,1)

    fig1.suptitle(title)

    axs1[0].plot(TC.xlist,machlist , 'g')  # row=0, column=0
    axs1[1].plot(TC.xlist,preslist , 'r')# row=1, column=0
    axs1[2].plot(TC.xlist,templist , 'b') # row=0, column=0
    axs1[3].plot(np.hstack((np.flip(TC.xlist),xlist)),np.hstack((np.flip(rlist),-rlist)) , 'k') # row=0, column=0


    axs1[0].set_title('Mach')
    axs1[1].set_title('Pressure')
    axs1[2].set_title('temperature')
    plt.savefig(os.path.join(path, "flowprops.png"))

    title=f"Chamber Wall Temperatures: Temp At Injector Face = {Twglist[-1]}"
    plt.figure()
    plt.plot(xlistflipped,Twglist , 'g', label="Gas Side Wall Temp, K")
    plt.plot(xlistflipped,Twclist , 'r', label="CoolantSide Wall Temp, K") # row=0, column=0
    plt.plot(xlistflipped,Tclist , 'b', label="Coolant Temp, K") # 
    plt.xlabel("Axial Position [m From Injector Face]")
    plt.ylabel("Temperature [K]")
    plt.legend()
    plt.title(title)
    plt.savefig(os.path.join(path, "ChamberTemps_LachlanFormat.png"))

    axs[0,1].plot(xlistflipped,hglist , 'g')  # row=0, column=0
    axs[1,1].plot(xlistflipped,hclist , 'r')# row=1, column=0
    axs[2,1].plot(np.hstack((np.flip(TC.xlist),xlist)),np.hstack((np.flip(rlist),-rlist)) , 'k') # row=0, column=0


    axs[0,1].set_title('hglist')
    axs[1,1].set_title('hclist')
    axs[2,1].set_title('Thrust Chamber Shape')

    axs[0,0].plot(xlistflipped,Twglist , 'g', label="Gas Side Wall Temp")
    axs[0,0].plot(xlistflipped,Twclist , 'r', label="CoolantSide Wall Temp") # row=0, column=0
    axs[0,0].plot(xlistflipped,Tclist , 'b', label="Coolant Temp") #
    axs[1,0].plot(xlistflipped,Tclist , 'r')# row=1, column=0
    axs[2,0].plot(xlistflipped,hydraulicdiamlist , 'r')# row=1, column=0

    axs[0,0].set_title('Twg')
    axs[1,0].set_title('Tc')
    axs[2,0].set_title('hydraulicdiam')
    axs[0,0].legend()

    axs[0,2].plot(xlistflipped,Twglist*const.degKtoR-458.67 , 'g', label="Gas Side Wall Temp, F")
    #axs[0,2].plot(xlistflipped,Tcoatinglist*const.degKtoR-458.67 , 'k', label="Opposite side of coating Temp, F")
    axs[0,2].plot(xlistflipped,Twclist * const.degKtoR-458.67, 'r', label="CoolantSide Wall Temp, F") # row=0, column=0

    axs[0,2].plot(xlistflipped,Tclist * const.degKtoR-458.67, 'b', label="Coolant Temp, F") #
    axs[1,2].plot(xlistflipped,coolantpressurelist /const.psiToPa, 'k')
    axs[2,2].plot(xlistflipped,rholist, 'k') # row=0, column=0

    axs[0,2].set_title('Twg')
    axs[1,2].set_title('coolantpressure (psi)')
    axs[2,2].set_title('density of coolant')
    axs[0,2].legend()
    plt.savefig(os.path.join(path, "temperatures.png"))
    print(f"max twg = {np.max(Twglist)} in kelvin, {np.max(Twglist)*const.degKtoR} in Rankine (freedom)\n max Twc ="
            f" {np.max(Twclist)} in kelvin, {np.max(Twclist)*const.degKtoR} in Rankine (freedom)")


    title=f"Chamber Wall Temperatures: Temp At Injector Face = {Twglist[-1]}"
    plt.figure()
    plt.plot(xlistflipped,Twglist , 'g', label="Gas Side Wall Temp, K")
    plt.plot(xlistflipped,Twclist , 'r', label="CoolantSide Wall Temp, K") # row=0, column=0
    plt.plot(xlistflipped,Tclist , 'b', label="Coolant Temp, K") # 
    plt.xlabel("Axial Position [m From Injector Face]")
    plt.ylabel("Wall Temperature [K]")
    plt.title(title)
    plt.savefig(os.path.join(path, "ChamberTemps_LachlanFormat.png"))

    axs[0,1].plot(xlistflipped,hglist , 'g')  # row=0, column=0
    axs[1,1].plot(xlistflipped,hclist , 'r')# row=1, column=0
    axs[2,1].plot(np.hstack((np.flip(TC.xlist),xlist)),np.hstack((np.flip(rlist),-rlist)) , 'k') # row=0, column=0


    axs[0,1].set_title('hglist')
    axs[1,1].set_title('hclist')
    axs[2,1].set_title('Thrust Chamber Shape')

    axs[0,0].plot(xlistflipped,Twglist , 'g', label="Gas Side Wall Temp")
    axs[0,0].plot(xlistflipped,Twclist , 'r', label="CoolantSide Wall Temp") # row=0, column=0
    axs[0,0].plot(xlistflipped,Tclist , 'b', label="Coolant Temp") #
    axs[1,0].plot(xlistflipped,Tclist , 'r')# row=1, column=0
    axs[2,0].plot(xlistflipped,hydraulicdiamlist , 'r')# row=1, column=0

    axs[0,0].set_title('Twg')
    axs[1,0].set_title('Tc')
    axs[2,0].set_title('hydraulicdiam')
    axs[0,0].legend()

    axs[0,2].plot(xlistflipped,Twglist*const.degKtoR-458.67 , 'g', label="Gas Side Wall Temp, F")
    #axs[0,2].plot(xlistflipped,Tcoatinglist*const.degKtoR-458.67 , 'k', label="Opposite side of coating Temp, F")
    axs[0,2].plot(xlistflipped,Twclist * const.degKtoR-458.67, 'r', label="CoolantSide Wall Temp, F") # row=0, column=0

    axs[0,2].plot(xlistflipped,Tclist * const.degKtoR-458.67, 'b', label="Coolant Temp, F") #
    axs[1,2].plot(xlistflipped,coolantpressurelist /const.psiToPa, 'k')
    axs[2,2].plot(xlistflipped,rholist, 'k') # row=0, column=0

    axs[0,2].set_title('Twg')
    axs[1,2].set_title('coolantpressure (psi)')
    axs[2,2].set_title('density of coolant')
    axs[0,2].legend()
    plt.savefig(os.path.join(path, "temperatures.png"))
    print(f"max twg = {np.max(Twglist)} in kelvin, {np.max(Twglist)*const.degKtoR} in Rankine (freedom)\n max Twc ="
            f" {np.max(Twclist)} in kelvin, {np.max(Twclist)*const.degKtoR} in Rankine (freedom)")

    #plt.show()

    classpltxlist=np.flip(xlist) #idk whats flipping this haha but its something in the steadystatetemps function, so we have to flip it back
    #xlist = np.flip(xlist) # flip it back damnit!
    helicitylist = np.flip(helicitylist)

    xlistnew, ylistnew,zlistnew,hydrualicdiamlistnew,chlistnew = CAD.ChanelBean(xlist,rlist,np.flip(twlist),
                    helicitylist, np.flip(chlist), np.flip(cwlist)) 
    plt.figure()

    plt.plot(xlistnew[:,0],zlistnew[:,0])
    plt.title("zig-zag bean lol")
    path=os.path.join( "Configs","CAD_"+configtitle)
    os.makedirs(path,exist_ok=True)
    np.savetxt(os.path.join( path,"rlistflipped.csv"), rlistflipped, delimiter=",")   
    np.savetxt(os.path.join( path,"twlist.csv"), twlist, delimiter=",") 
    np.savetxt(os.path.join( path,"chlist.csv"), chlist, delimiter=",") 
    np.savetxt(os.path.join( path,"cwlist.csv"), cwlist, delimiter=",") 
    np.savetxt(os.path.join( path,"hydraulicdiamlist.csv"), hydraulicdiamlist, delimiter=",") 
    np.savetxt(os.path.join( path,"nlist.csv"), nlist, delimiter=",") 
    #with open(os.path.join(path, "chanelsweepcurve.sldcrv"), "w") as f:
    #    for i in range(len(xchanel)):
    #        #print(f"{xchanel[i]} {ychanel[i]} {zchanel[i]}", file=f) # this if for olivers axis's
    #        print(f"{ychanel[i]} {xchanel[i]} {zchanel[i]}", file=f) # this if for roberts axis's
    #with open(os.path.join(path, "chanelguidingcurve_height.sldcrv"), "w") as f:
    #    for i in range(len(xchanel)):
    #        #print(f"{xchanel[i]} {ychanel[i]} {zchanel[i]}", file=f) # this if for olivers axis's
    #        print(f"{yheight[i]} {xheight[i]} {zheight[i]}", file=f) # this if for roberts axis's
    #with open(os.path.join(path, "chanelguidingcurve_width.sldcrv"), "w") as f:
    #    for i in range(len(xchanel)):
    #        #print(f"{xchanel[i]} {ychanel[i]} {zchanel[i]}", file=f) # this if for olivers axis's
    #        print(f"{ywidth[i]} {xwidth[i]} {zwidth[i]}", file=f) # this if for roberts axis's
    for index in range(0,xlistnew.shape[0]):
        with open(os.path.join(path, f"ThrustChamber_Curve{index}.sldcrv"), "w") as f:
            for i in range(len(xlistnew[1,:])):
                #print(f"{xchanel[i]} {ychanel[i]} {zchanel[i]}", file=f) # this if for olivers axis's
                print(f"{ylistnew[index,i]} {xlistnew[index,i]} {zlistnew[index,i]}", file=f) # this if for roberts axis's

    with open(os.path.join(path, "internalradius.sldcrv"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {rlist[i]} {0}", file=f)
    newxlist, externalrlist = CAD.rlistExtender(xlist,rlist,ewlist+np.flip(chlist)+np.flip(twlist))
    with open(os.path.join(path, "externalradius.sldcrv"), "w") as f:
        for i in range(len(xlist)):
            print(f"{newxlist[i]} {externalrlist[i]} {0}", file=f)
    with open(os.path.join(path, "midprofile.sldcrv"), "w") as f:
        for i in range(int(xlistnew.shape[0]/2)):
            print(f"{ylistnew[i*2,int(len(xlist)/2)]} {xlistnew[i*2,int(len(xlist)/2)]} {zlistnew[i*2,int(len(xlist)/2)]}", file=f) # this if for roberts axis's
        for i in np.flip(np.arange(int(xlistnew.shape[0]/2))):
            print(f"{ylistnew[i*2+1,int(len(xlist)/2)]} {xlistnew[i*2+1,int(len(xlist)/2)]} {zlistnew[i*2+1,int(len(xlist)/2)]}", file=f)
    with open(os.path.join(path, "quarterprofile.sldcrv"), "w") as f:
        for i in range(int(xlistnew.shape[0]/2)):
            print(f"{ylistnew[i*2,int(len(xlist)/4)]} {xlistnew[i*2,int(len(xlist)/4)]} {zlistnew[i*2,int(len(xlist)/4)]}", file=f) # this if for roberts axis's
        for i in np.flip(np.arange(int(xlistnew.shape[0]/2))):
            print(f"{ylistnew[i*2+1,int(len(xlist)/4)]} {xlistnew[i*2+1,int(len(xlist)/4)]} {zlistnew[i*2+1,int(len(xlist)/4)]}", file=f)
    with open(os.path.join(path, "threeqprofile.sldcrv"), "w") as f:
        for i in range(int(xlistnew.shape[0]/2)):
            print(f"{ylistnew[i*2,int(len(xlist)/4*3)]} {xlistnew[i*2,int(len(xlist)/4*3)]} {zlistnew[i*2,int(len(xlist)/4*3)]}", file=f) # this if for roberts axis's
        for i in np.flip(np.arange(int(xlistnew.shape[0]/2))):
            print(f"{ylistnew[i*2+1,int(len(xlist)/4*3)]} {xlistnew[i*2+1,int(len(xlist)/4*3)]} {zlistnew[i*2+1,int(len(xlist)/4*3)]}", file=f)

    #NOW MAKE BOX CURVES

    xlistnew, ylistnew,zlistnew = CAD.ChanelBoxCorners(xlist,rlist,np.flip(twlist),
                    helicitylist, np.flip(chlist), np.flip(cwlist)) 
    path=os.path.join( "Configs","CAD_CDR_Engine_Box_flippedtw_refined")
    os.makedirs(path,exist_ok=True)

    for index in range(0,4):
        with open(os.path.join(path, f"ThrustChamber_Curve{index}.sldcrv"), "w") as f:
            for i in range(len(xlistnew[1,:])):
                #print(f"{xchanel[i]} {ychanel[i]} {zchanel[i]}", file=f) # this if for olivers axis's
                print(f"{ylistnew[index,i]} {xlistnew[index,i]} {zlistnew[index,i]}", file=f) # this if for roberts axis's

    with open(os.path.join(path, "internalradius.sldcrv"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {rlist[i]} {0}", file=f)
    newxlist, externalrlist = CAD.rlistExtender(xlist,rlist,ewlist+np.flip(chlist)+np.flip(twlist))
    with open(os.path.join(path, "externalradius.sldcrv"), "w") as f:
        for i in range(len(xlist)):
            print(f"{newxlist[i]} {externalrlist[i]} {0}", file=f)
    with open(os.path.join(path, "Twglist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {Twglist[i]}", file=f)
    with open(os.path.join(path, "Twclist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {Twclist[i]}", file=f)
    with open(os.path.join(path, "QdotTotallist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {Qdotlist[i]*nlist[i]*(abs(xlist[0]-xlist[1]))}", file=f)
    with open(os.path.join(path, "qdotlist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {Qdotlist[i]*nlist[i]/(math.pi*rlist[i]*2)}", file=f)
    with open(os.path.join(path, "QdotPerChanellist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {Qdotlist[i]*(abs(xlist[0]-xlist[1]))}", file=f)
    with open(os.path.join(path, "Machlist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {machlist[i]}", file=f)
    with open(os.path.join(path, "GasTemplist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {templist[i]}", file=f)
    with open(os.path.join(path, "GasPressurelist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {preslist[i]}", file=f)
    with open(os.path.join(path, "CoolantPressurelist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {coolantpressurelist[i]}", file=f)
    with open(os.path.join(path, "CoolantTemperaturelist.txt"), "w") as f:
        for i in range(len(xlist)):
            print(f"{xlist[i]} {Tclist[i]}", file=f)


    thetalist = np.arange(0, 2*math.pi, .1)
    theta, r = np.meshgrid(thetalist, rlist-.01)
    theta, xgrid = np.meshgrid(thetalist, xlist)
    zgrid = r*np.cos(thetalist)
    ygrid = r*np.sin(thetalist)
    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    for index in range(0,xlistnew.shape[0]):
        ax.plot(xlistnew[index,], zlistnew[index,], ylistnew[index,],linewidth=.5)
    #chanel0 = ax.plot(xlistnew[0,], zlistnew[0,], ylistnew[0,],'r',linewidth=.5)
    #chanel1 = ax.plot(xlistnew[1,], zlistnew[1,], ylistnew[1,],'g',linewidth=.5)
    #chanel2 = ax.plot(xlistnew[2,], zlistnew[2,], ylistnew[2,],'b',linewidth=.5)
    #chanel3 = ax.plot(xlistnew[3,], zlistnew[3,], ylistnew[3,],'m',linewidth=.5)
    surf = ax.plot_surface(zgrid,ygrid,xgrid, cmap=cm.coolwarm,
                        linewidth=0, antialiased=True, alpha=.5)

    # Customize the z axis.
    ax.set_zlim(0, np.max(xlist))
    # A StrMethodFormatter is used automatically
    ax.zaxis.set_major_formatter('{x:.02f}')

    # Add a color bar which maps values to colors.
    fig.colorbar(surf, shrink=0.5, aspect=5)


    plt.show()

    print("end")

if ~output:
    params['mi'] = mis
    params['L'] = lambdas
    params['M'] = totalmasses
    params['wstruct'] = wstruct
    params['newheight'] = newheight
    params['heightox'] = heightox
    params['heightfuel'] = heightfuel
    params['vol_ox'] = vol_ox
    params['vol_fuel'] = vol_fuel
    params['P_tank'] = P_tank
    params['twg_max'] = np.max(Twglist)
    params['twc_max'] =  np.max(Twclist)
