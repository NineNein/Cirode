from sympy import *
from sympy.functions import *


nb, ne, nc, UT, IS, q = symbols("nb ne nc UT IS q")

expr_icf = IS * (exp((ne-nb)/(UT)) - 1.0)
expr_icr = IS * (exp((nc-nb)/(UT)) - 1.0)


expr_ice = (expr_icf-expr_icr)/q

print(expr_ice)