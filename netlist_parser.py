"""

RXXXXXXX N1 N2 VALUE
CXXXXXXX N+ N- VALUE 
LYYYYYYY N+ N- VALUE

Iname N+ N- VALUE

"""


import circuit
from circuit import Circuit
import re
import string

def oneport(line, namelist):
    #line = line.lower()
    words = line.split()

    if len(words) < 3:
        return False, None, None

    node_number = []
    for w in words[1:3]:
        if w.isdigit():
            node_number.append(int(w))
        else:
            if w not in namelist:
                namelist.append(w)
            node_number.append(namelist.index(w))

    return True, words, node_number

def resistor(line, component_list, namelist):
    success, words, nodes = oneport(line, namelist)

    if not success:
        return False

    if words[0][0].lower() != "r":
        return False

    name = words[0].upper()
    value = float(words[3])
    
    component_list.append(circuit.R(name, nodes , value))

    return True


def inductor(line, component_list, namelist):
    success, words, nodes = oneport(line, namelist)

    if not success:
        return False

    if words[0][0].lower() != "l":
        return False

    name = words[0].upper()
    value = float(words[3])
    
    component_list.append(circuit.L(name, nodes , value))

    return True


def capacitor(line, component_list, namelist):
    success, words, nodes = oneport(line, namelist)

    if not success:
        return False

    if words[0][0].lower() != "c":
        return False

    name = words[0].upper()
    value = float(words[3])
    
    component_list.append(circuit.C(name, nodes , value))

    return True

def current_source(line, component_list, namelist):
    success, words, nodes = oneport(line, namelist)

    if not success:
        return False

    if words[0][0].lower() != "i":
        return False

    name = words[0].upper()
    value = float(words[3])
    
    component_list.append(circuit.IS(name, nodes , value))

    return True

def votlage_source(line, component_list, namelist):
    success, words, nodes = oneport(line, namelist)

    if not success:
        return False

    if words[0][0].lower() != "v":
        return False

    name = words[0].upper()
    value = float(words[3])
    
    component_list.append(circuit.VS(name, nodes , value))

    return True

def ctrl_current_source(line, component_list, namelist):
    success, words, nodes = oneport(line, namelist)

    if not success:
        return False

    if words[0][0].lower() != "g":
        return False

    name = words[0].upper()
    
    value = float(words[3])

    idx = len(' '.join(words[:4]))
    expression = line[idx+1:-1]

    print(expression)
    
    component_list.append(circuit.CTRL_CS(name, nodes , expression, value))

    return True


### Model Section

def diode_model(name, model, params):
    if model.upper() != "D":
        return False
    
    return True

models = [
    diode_model
]

def model(line, variable, namelist):
    re_model = re.compile(r".model\s\s*(\w+)\s\s*(\w+)\s*\((.*?)\)")
    output = re_model.match(line)
    if not output:
        return False

    name  = output.group(1)
    model = output.group(2)
    str_params = output.group(3)
    str_params = str_params.lstrip().split(",")

    params = {}
    for param in str_params:
        key, value = param.split("=")
        key = key.translate(str.maketrans('', '', string.whitespace))
        value = value.translate(str.maketrans('', '', string.whitespace))
        params[key] = float(value)

    for m in models:
        if m(name, model, params):
            break
    
    
    return False
    
    
instructions = [
    model
]


components = [
    resistor,
    inductor,
    capacitor,
    current_source,
    votlage_source,
    ctrl_current_source,
]

def parse_netlist(netlist_io):
    component_list = []

    namelist = ["GND"]

    lines = []
    for line in netlist_io:
        if line.lstrip().startswith("#") or line.isspace():
            continue

        line = line.split("#")[0]
        lines.append(line)

    parsed_lines = []

    #instructions
    for j, line in enumerate(lines):
        for instruction in instructions:
            if instruction(line, component_list, namelist):
                parsed_lines.append(j)
                break


    #Components
    for j, line in enumerate(lines):
        for component in components:
            if component(line, component_list, namelist):
                parsed_lines.append(j)
                break



    line_nrs = set(range(len(lines))) 
    parsed_lines = set(parsed_lines)

    missing = list(sorted(line_nrs - parsed_lines))
    if len(missing) != 0:
        raise ValueError("Cant parse line(s): " + str(missing))

    return component_list