import networkx as nx
import numpy as np
import sympy as sy

element_id_counter = 0
class OnePortElement(object):
    def __init__(self, name, nodes, value):
        global element_id_counter
        assert len(nodes) == 2, "One Port Element needs two nodes"
        self.name = name
        self.nodes = list(map(str,nodes))
        self.value = value

        self.id = element_id_counter
        element_id_counter += 1

    def stamp(self, state_vector,  Y, RHS, name2node, symbolic=True):
        pass

"""
Class for a Resistor, contains netlist command creation and the stamp for a resistor
"""
class R(OnePortElement):
    def __init__(self, name, nodes, value):
        super().__init__(name, nodes, value)


    def netlist_cmd(self):
        name = self.name.upper()
        if not name.startswith("R"):
            name = "R" + name

        return name + " " + str(self.nodes[0]) + " " + str(self.nodes[1]) + " " + str(self.value) 

    def replace(self, node_map, parameters):
        pass

    def stamp(self, state_vector,  Y, RHS, name2node, symbolic=True):
        k = name2node[self.nodes[0]]-1
        l = name2node[self.nodes[1]]-1

        if symbolic:
            value = sy.Symbol(self.name)
        else:
            value = self.value

        br_idx = state_vector.add_current(self.id)

        if k >= 0:
            Y[k][br_idx] = 1
            Y[br_idx][k] = 1
            
        if l >= 0:
            Y[l][br_idx] = -1
            Y[br_idx][l] = -1
            
        Y[br_idx][br_idx] = value

        RHS[br_idx] = 0

"""
Class for a Controled Current Source, contains netlist command creation and the stamp for a Controled Current Source
"""
class CTRL_CS(OnePortElement): #  Controled Current Source
    def __init__(self, name, nodes, expression, start_value):
        super().__init__(name, nodes, start_value)
        self.expression = expression

    def netlist_cmd(self):
        name = self.name.upper()
        if not name.startswith("G"):
            name = "G" + name

        return name + " " + str(self.nodes[0]) + " " + str(self.nodes[1]) + " " + str(self.value) 

    def stamp(self, state_vector, Y, RHS, name2node, symbolic=True):
        k = name2node[self.nodes[0]]-1
        l = name2node[self.nodes[1]]-1

        state_vector.state_vector["ctrl_sources"].append(self)

        assert symbolic, "VCCS can't be used yet in non symbolic mode"

        value = sy.Symbol(self.name)

        RHS[k] = -value
        RHS[l] = value

############################



'''
Model could be represent by a struct in C++ code such,
model parameter could be scanned easily within c++ code
'''

class Parameter():
    def __init__(self, name, value=None):
        self.name = name
        self.symbol = sy.Symbol(self.name)
        self.value = value

class Model():
    def __init__(self, **kwargs):
        self.params = {}
        for name, value in kwargs.items():
            self.params[name] = Parameter(name, value)

    def __getattr__(self, attr):
        if attr  in self.params.keys():
            return self.params[attr].symbol

        return self.__getattribute__(name)


    def __setattr__(self, attr, value):
        if attr in self.params.keys():
            self.params[attr].value = value

        super().__setattr__(attr, value)

    def value(self, symbol):
        for name, param in self.params.items():
            if param.symbol == symbol:
                return param.value

        raise ValueError("Symbol not found in Model")


class Expression():
    pass


class _SubCircuit():
    def __init__(self, subcircuit, name, nodes, parameter):
        self.nodes = []
        self.subcir = subcircuit
        self.parameter = parameter

        assert len(nodes) == len(self.subcir.export_nodes), "Number of nodes not as expected from SubCircut"

    def components(self, circuit):
        #generate map subcircuit node to parent circuit free node
        node_map = {}
        for en, n in zip(self.subcir.export_nodes, self.nodes):
            node_map[en] = n

        for node in self.subcir.nodes:
            if node not in node_map:
                node_map[node] = circuit.generate_free_node()

        clist = []

        for element in self.subcir.components:
            clist.append(element.replace(node_map, self.parameter))

        return clist

class SubCircuit():
    def __init__(self, export_nodes, model):
        self.components = []
        self.model = model
        self.voltages = {} #for voltages and currents
        self.export_nodes = export_nodes
        self.nodes = []

    def generate_free_node(self):
        used_node_nrs = []
        
        for node_name in self.nodes:
            try:
                node_nr = int(node_name)
                used_node_nrs.append(node_nr)
            except:
                continue
        #must be not super efficient jet: get the smalest number which is not in list
        for i in range(len(used_node_nrs)+1):
            if i not in used_node_nrs:
                self.nodes.append(str(i))
                return str(i)

    def V(self, node):
        symbol = sy.symbol("V_"+str(node))
        self.voltages[node] = symbol
        return symbol

    def I(self, component):
        pass

    def define(self, elements):
        for element in elements:
            for node in element.nodes:
                if not node in self.nodes:
                    self.nodes.append(str(node))

        for element in elements:
            if isinstance(element, _SubCircuit):
                components = element.components(self)
                for component in components:
                    self.components.append(component)
            else:
                self.components.append(element)

    def __call__(self, name, nodes, parameter):
        return _SubCircuit(self, name, nodes, parameter)
        #return (list of components) should work with subcircuit in subcircuit too


class Circuit:
    def __init__(self):
        pass

    def V(self, node):
        pass

    def I(self, component):
        pass

    def define(self, components):
        pass

from sympy.functions import *

diode_model = Model("Diode",
    IS = 0,
    UT = 0,
    RS = 0.1
)



diode = SubCircuit([1,3], diode_model)
# expression = lambda param: f"{param.IS}*(exp((V(3)-V(2))/({param.UT})) - 1)"
expression = diode_model.IS * exp((diode.V(2)-diode.V(3))/diode_model.UT) - 1



diode.define([
    R("R1", [1, 2], params.R1),
    CTRL_CS("C1", [2, 3], expression), #CTRL source accept function or string
])


c = Circuit(0)
model = diode_model("RS":0.1, "IS": 1e-6, "UT": 0.3433)
c.define([
    R("R1", [1, 2], 300),
    diode("D1", [1,2], model)
])