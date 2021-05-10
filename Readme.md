# Integrator Independent MNA Circuit Simulator
The aim of this project is to create a tool which can compile a circuit into a system of first
order ordinary differential equation (ODE) which can be solved by an integrator of the choice of the user.

The motivation for this project was the need to add a simulation of a circuit to another simulation. Also to find a quicker and more efficient way to derive the ODE for the circuit than by hand.
On the one hand I learned something on the other hand i could have just used: http://lcapy.elec.canterbury.ac.nz/

# Requirements 
### Python
- networkx
- sympy
- numpy
- jinja2
- matplotlib (for examples)

### C++
- g++
- boost ode

### Usage
See examples.
```
python3 cirode.py <netlist filename> <name of circuit>
```
This will output a <name of circuit>.hpp file based on the circuit in descibed in netlist which can be used in an itegrator, see boost_ode_lrc.cpp

#### Makefile Example
This example will compile the circuit described in the netlist file to a c++ file.


#### simple_lrc.py
This example shows how to simulate a simple circuit in python.

# ToDo
- Implement two port devices, e.g. inductor coupling
- Implement (better) Sources
- Implement output of ODE
