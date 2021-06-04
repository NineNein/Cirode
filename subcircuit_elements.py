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