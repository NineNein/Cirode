"""

RXXXXXXX N1 N2 VALUE
CXXXXXXX N+ N- VALUE 
LYYYYYYY N+ N- VALUE

Iname N+ N- VALUE

"""


import circuit
from circuit import Circuit

def oneport(line, namelist):
    line = line.lower()
    words = line.split()

    if len(words) < 3:
        return False

    node_number = []
    for w in words[1:3]:
        if w.isdigit():
            node_number.append(int(w))
        else:
            if w not in namelist:
                namelist.append(w)
            node_number.append(namelist.index(w))

    return words, node_number

def resistor(line, component_list, namelist):
    words, nodes = oneport(line, namelist)

    if words[0][0] != "r":
        return False

    name = words[0].upper()
    value = float(words[3])
    
    component_list.append(circuit.R(name, nodes , value))

    return True


def inductor(line, component_list, namelist):
    words, nodes = oneport(line, namelist)

    if words[0][0] != "l":
        return False

    name = words[0].upper()
    value = float(words[3])
    
    component_list.append(circuit.L(name, nodes , value))

    return True


def capacitor(line, component_list, namelist):
    words, nodes = oneport(line, namelist)

    if words[0][0] != "c":
        return False

    name = words[0].upper()
    value = float(words[3])
    
    component_list.append(circuit.C(name, nodes , value))

    return True

def current_source(line, component_list, namelist):
    words, nodes = oneport(line, namelist)

    if words[0][0] != "i":
        return False

    name = words[0].upper()
    value = float(words[3])
    
    component_list.append(circuit.IS(name, nodes , value))

    return True

components = [
    resistor,
    inductor,
    capacitor,
    current_source,
]

def parse_netlist(netlist_io):
    component_list = []

    namelist = ["GND"]

    for line in netlist_io:
        if line.lstrip().startswith("*") or line.isspace():
            continue

        found = False
        for component in components:
            if component(line, component_list, namelist):
                found = True
                break
        if not found:
            raise ValueError("Not Component found for: " + line)
        

    return component_list