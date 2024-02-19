'''GUI Development'''

import sys
sys.path.insert(1,"./")
import DataManager as dm
import numpy as np
import os
import PySimpleGUI as sg
import json
import Toolbox.Constant as const #for conversions of units
import math
import pandas as pd

# Populates with default parameters. changes to the dictionary in datamanager and in defaults will automatically be taken into account
defaults = { #default values ROOPERT starts with
        'thrust': 4000 * const.lbToN,  # Newtons
        'time': 40,  # s
        # 'rho_ox' : 1141, #Kg/M^3
        # 'rho_fuel' : 842,
        'pc': 300 * const.psiToPa, # Pa
        'pe': 14.7 * const.psiToPa, # Pa
       # 'phi':1,
        'cr': None, # unitless
        'TWR' : 4, # unitless
        'lstar': 1.24, # m
        'fuelname': 'Ethanol_75',
        'oxname': 'N2O',
        'throat_radius_curvature': .0254 *2, # rad
        'dp': 150 * const.psiToPa, # Pa
        'rc' : .11, # m
        'thetac' : (35*math.pi/180) # Pa
}
sg.theme('Dark Purple 3')

params = dm.blankParams
unitdict = {}
functionlist = ['func1', 'func2', 'func3']

for key in params.keys():
    try:
        params[key] = defaults[key]
    except:
        params[key] = None

for key in params.keys():
    try:
        unitdict[key] = dm.unitdict[key]
    except:
        unitdict[key] = ''

name_column = [[]]
input_column = [[]]

for key in params.keys():
    name_column.append([sg.Text(key)])
    input_column.append([sg.InputText(default_text=params[key], key=key, size = 10), sg.Text(unitdict[key])])

function_column = [
    [sg.Text("Function Name"), sg.Combo(functionlist, size = 10,  default_value=functionlist[0], k="-FUNC NAME-", enable_events=True, readonly=True)],
    [sg.Button("Run Function")]
]

layout = [
    [
        sg.Column(name_column),
        sg.VSeperator(),
        sg.Column(input_column),
    ],
    [
        sg.Column(function_column),
        sg.Push(),
        sg.Column([[sg.Image(filename=os.path.join(os.getcwd(), 'NewOOPSystem/sarp-logo-white.png'), size=(80, 80))]]),
    ],
]

window = sg.Window("ROOPERT", layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
window.close()