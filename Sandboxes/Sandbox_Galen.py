"This is for Galen"

paramnames = [
    'thrust', #Newtons
    'time', #s
    'impulse', #N*s
    'rho_ox', #Kg/M^3
    'rho_fuel', #Kg/M^3
    'pc', #Pa, if cr is specified, this is Pressure at end of combustor
    'pinj',#Pa, only useful if you specify CR, otherwise assumed to be pc
    'pe', #Pa
    'g', #m/s^2
    'rm', #o/f by weight
    'phi', #ratio from stoich (1 is stoich, >1 is fuel rich)
    'at', # m^2, area of throat
    'rt', # m, radius of throat 
    'cr', # contraction ratio
    'rc', # m, combustion chamber radius
    'ac', # m^2, area combustion chamber
    'l_star', # m, volume cc/area throat
    'mol_weight', # kg/mol
    'gamma', # in cc
    'gamma_exit', # in exit
    'gamma_throat', # in throat
    'isp', # s
    'temp_c', # K, chamber temp
    'rg', # specific gas constant (SI units if what they are)
    'pr_throat',
    'rho_throat',
    'temp_e',
    'v_exit',
    'a_exit',
    'mach_exit',
    'temp_throat',
    'p_throat',
    'v_throat',
    'mdot',
    'mdot_ox',
    'mdot_fuel',
    'er',
    'cstar',
    'cf',
    'c_eff',
    'rho_av',
    'vc',
    'theta_con',
    'lc',
    'theta_div',
    'ln_conical',
    'ln_bell',
    'throat_radius_curvature',
    'ae',
    're',
    'nv',
    'nvstar',
    'nf',
    'nw',
    'fuelname',
    'oxname',
    'CEA',
    'pambient',
    'cf_efficiency', # Huzel and Huang page 16
    'isp_efficiency',
    'thetac', # converging section angle
    'thetai', # diverging angle at throat
    'thetae',# diverign angle at exit
    'kin_visc_fuel',
    'kin_visc_ox',
    'dyn_visc_fuel',
    'dyn_visc_ox',
    'P_tank_ox',
    'P_tank_fuel',
    'numengines',
    'propmass'] 


def thrust(params):
    try:
        return params['mdot']*9.81*params['isp']
    except:
        print('Could not calculate Thrust')
        return None


params = dict.fromkeys(paramnames)
params['numengines'] = 9
params['mdot'] = 9
params['isp'] = 9

for param in params:
    print(param)

try:
    print(globals()['thrust'](params))
except:
    print("helo")
