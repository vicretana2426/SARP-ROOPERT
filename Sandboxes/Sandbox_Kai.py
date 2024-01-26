#this is kais sandbox


import numpy as np
import matplotlib.pyplot as plt
import Toolbox.Constant as const
import math as m
import pandas



import Analysis.FirstOrderCalcs as FAC
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
print(FAC.lc(params))
print(params['lc'])

michael = 5

cheese = michael

print(cheese)

print(FAC.SpreadsheetSolver(args))

print(params)

print(params['viscosityns'], params['prns'], params['cpns'])

a = False

b = True
if not a == True and b == False:
        print("buh")
else:
        print("womp womp")

