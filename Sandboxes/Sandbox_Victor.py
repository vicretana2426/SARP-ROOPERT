"This is for VICTOR RETANA"

'''This module will be used for debugging, feel free
to play around here as much as you would like !!'''

import sys
sys.path.insert(1, "./")
import Analysis.FirstOrderCalcs as FAC
import Toolbox.Constant as const
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


for i in params:
    print(i, params[i])







