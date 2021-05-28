# Currently adding Controlled sources
- controlled sources can be used to implement diodes
- uses GSL libary to find roots

- static ctrl diodes still bugy
- need to check sign convention...

### subcircuts
- implementation of subcircuit
- if subcircuit can have parameters which can be specifed by a model command
it would be possible to define diodes and transitors this way


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



# Stamps for Capacitor and Inductor
dt/dx is handeld as variable, and x is handeld as known. Such the system can be expressed
as dt/dx = f(x). This can be then solved by any integrator who accept this form.

Values in brackets (x) are fixed, and wont be added if an other matrix stamp is added.

## Capacitor Stamp

|    | l | k | br | dl | dk |
|:--:|:-:|:-:|:--:|:--:|:--:|
| l  |   |   | 1  |    |    |
| k  |   |   | -1 |    |    |
| br |   |   | 1  | C  | -C |
| dl |(1)|   |    |    |    |
| dk |   |(1)|    |    |    |


## Indcutor Stamp

|    | l | k  | br  | di |
|:--:|:-:|:--:|:---:|:--:|
| l  |   |    | 1   |    |
| k  |   |    | -1  |    |
| br | 1 | -1 |     | L  |
| di |   |    | (1) |    |


http://www.ecircuitcenter.com/SpiceTopics/Non-Linear%20Analysis/Non-Linear%20Analysis.htm
http://qucs.sourceforge.net/tech/node16.html


#install libs
sudo apt-get install libboost-all-dev
sudo apt-get install libgsl-dev