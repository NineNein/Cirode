from sympy.functions import *
from sympy import *


n1 = Symbol("V(1)")
n2 = Symbol("V(2)")

expression = 234 * (exp((n1-n2)/1224) - 1)

n3 = Symbol("V(1)")

print(expression)


expression = expression.subs(n2, UnevaluatedExpr(n3))


print(expression)
