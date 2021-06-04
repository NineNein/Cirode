from circuit import *
from sympy.functions import *


"""
Simple Diode Model
"""

diode_model = Model("Diode",
    IS = 1e-14,
    UT = 0.025875,
    RS = 0.001
)

diode = SubCircuit("Diode", [1,3], diode_model)
expression = diode_model.IS * (exp((diode.V(2)-diode.V(3))/diode_model.UT) - 1)
diode.define([
    R("R1", [1, 2], diode_model.RS),
    CTRL_CS("G1", [3, 2], expression, 0.6), #CTRL source accept function or string
])


"""
 Gummel-Poon Model 
"""
INF = 1e30
npn_bjt_model = Model("npn_bjt",
    IS  = 1e-16,        #transport saturation current
    BF  = 100,          #ideal max. forward beta
    NF  = 1,            #forward-current emission coefficient
    VAF = INF,          #forward early voltage
    IKF = INF,          #fcorner for forward-beta high-current roll-off
    ISE = 0,            #B–E leakage saturation current
    NE  = 1.5,          #B–E leakage emission coefficient
    BR  = 1,            #ideal max. reverse beta
    NR  = 1,            #reverse-current emission coefficient
    VAR = INF,          #reverse early voltage
    IKR = INF,          #corner for reverse-beta high-current roll-off
    ISC = 0,            #B–C leakage saturation current
    NC  = 2,            #B–C leakage emission coefficient
    RB  = 0,            #zero-bias base resistance
    IRB = INF,          #current where base resistance falls half-way to its minimum
    RBM = 0,            #minimum base resistance at high currents, !!! same value as RB
    RE  = 0,            #emitter resistance
    RC  = 0,            #collector resistance
    CJE = 0,            #B–E zero-bias depletion capacitance
    VJE = 0.75,         #B–E built-in potential
    MJE = 0.33,         #B–E junction exponential factor
    TF  = 0,            #ideal forward transit time
    XTF = 0,            #coefficient for bias dependence of TF
    VTF = INF,          #voltage describing VBC dependence of TF
    ITF = 0,            #high-current parameter for effect on TF
    PTF = 0,            #excess phase at frequency = 1/(2π TF)
    CJC = 0,            #B–C zero-bias depletion capacitance
    VJC = 0.75,         #B–C built-in potential
    MJC = 0.33,         #B–C junction exponential factor
    XCJC = 1,           #fraction of B–C depletion capacitance connected to internal base node
    TR  = 0,            #ideal reverse transit time
    CJS = 0,            #zero-bias collector–substrate capacitance
    VJS = 0.75,         #substrate–junction built-in potential
    MJS = 0,            #substrate–junction exponential factor
    XTB = 0,            #forward- and reverse-beta temperature exponent
    EG  = 1.1,          #energy gap for temperature effect of IS
    XTI = 3,            #temperature exponent for effect of IS
    KF  = 0,            #flicker-noise coefficient
    AF  = 1,            #flicker-noise exponent
    FC  = 0.5,          #coefficient for forward-bias depletion capacitance formula
    TNOM = 27           #parameter measurement temperature
)

npn_bjt = SubCircuit("npn_bjt", [1,2,3], npn_bjt_model)
npn_bjt.define([
    R("Re", ["E", "E'"], npn_bjt_model.RE),
    R("Rc", ["C", "C'"], npn_bjt_model.RC),
    R("Rb", ["B", "B'"], npn_bjt_model.RB),


    CTRL_CS("G1", [3, 2], expression, 0.6), #CTRL source accept function or string
])