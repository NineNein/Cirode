#https://electronics.stackexchange.com/questions/324485/nonlinear-equation-solvers-in-spice-simulators

"""
.model D D(IS =1e-15,UT = 0.025875, RS = 0.1)

V1 1 0 1

D1 1 2 D
C2 0 2 1e-5
R2 0 2 1000

D2 2 3 D
R1 0 3 1000
C1 0 3 1e-5
"""


def add(i):
    ret = f"""
D{i} {i} {i+1} D
R{i} 0 {i+1} 1000
C{i} 0 {i+1} 1e-5
"""

    return i+1, ret

netlist = """
.model D D(IS =1e-15,UT = 0.025875, RS = 0.1)
V1 1 0 1
"""
n = 1
for i in range(4):
    n, sn = add(n)
    netlist += sn

print(netlist)
    
with open("netlist.txt", "w") as f:
    f.write(netlist)