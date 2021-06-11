import networkx as nx
import numpy as np
import sympy as sy
from stamp_elements import *

GND = 0 # Will be assumed in calculation cant be changes

###
# https://www3.math.tu-berlin.de/preprints/files/Preprint-01-2017.pdf !
###

"""
avector and amatrix are vector and matrix with arbitary size
such it is easy to fill the MNA stamps without previous determination of the size
of needed vector or matrix
"""
class avector:
    def __init__(self, init_value = 0.0):
        self.init_value = init_value
        self.v = {}

    def __getitem__(self, key):
        return self.v.get(key, self.init_value)

    def __setitem__(self, key, value):
        self.v[key] = value

    def to_list(self):
        vm = max(list(self.v.keys()))+1
        tlist = [ 0 for i in range(vm)]
        for k, value in self.v.items():
                tlist[k] = value

        return tlist

class amatrix:
    def __init__(self, init_value = 0.0):
        self.init_value = init_value
        self.m = {}

    def __getitem__(self, key):
        if key not in self.m:
            self.m[key] = avector(init_value = self.init_value)
        return self.m[key]

    def to_list(self):
        n = max(list(self.m.keys()))

        m = 0
        for key, value in self.m.items():
            vm = max(list(value.v.keys()))
            if vm > m:
                m = vm

        n += 1
        m += 1

        tlist = [ [0]*m for i in range(n)]

        for j, vector in self.m.items():
            for k, value in vector.v.items():
                tlist[j][k] = value


        return tlist


"""
State vector
holds information about which entry/index are corresponding to which current or derivative
the first n entries are the node voltages
It also holds a list of used sources
"""

class state_vector:
    def __init__(self, number_of_nodes):
        self.number_of_nodes = number_of_nodes
        self.state_vector = {
            "current" : {},  #id of element, idx in the state vector
            "dt" : {}, #idx of related variabeel, idx in the state vector
            "sources" : [], #list of sources
            "ctrl_sources" : [], #list of controled sources
            "nonlinear" : [], #list of non linear elements
        }

    def _idx(self):
        i_values = list(self.state_vector["current"].values())
        i_dt = list(self.state_vector["dt"].values())

        if not i_dt and not i_values:
            idx = self.number_of_nodes - 1 - 1 #GND dont count 
        else:
            idx = max(i_values + i_dt)

        return idx

    def add_current(self, id):
        if id not in self.state_vector["current"]:
            self.state_vector["current"][id] = self._idx()+1

        return self.state_vector["current"][id]

    def add_dt(self, var_idx):
        if var_idx not in self.state_vector["dt"]:
            self.state_vector["dt"][var_idx] = self._idx()+1

        return self.state_vector["dt"][var_idx]

    def current(self, id):
        return self.state_vector["current"].get(id, -1)

    def dt(self, var_idx):
        return self.state_vector["dt"].get(var_idx, -1)





# """
# Class for a Diode, creates diode with an series resistor and a controlled current source
# """

# class model:
#     def __init__(self):
#         pass

# class diode_model(model):
#     def __init__(self, name, IS=1e-14, UT = 0.025875, RS = 1e-10, CJO = 0, TT=0, BV=None, IBV=1e-10):
#         """
#         - name is the name of the model of the diode specified in the model line.
#         - IS: saturation current,
#         - UT: thermal voltage
#         - RS: the series resistance, should not be zero because thise could lead to non possible root finding
#         - CJO - junction capacitance , NOT CURRENTLY IMPLEMENTED
#         - TT - transit time , NOT CURRENTLY IMPLEMENTED
#         - BV - reverse bias breakdown voltage, None = Inf , NOT CURRENTLY IMPLEMENTED
#         - IBV - the reverse bias breakdown current, NOT CURRENTLY IMPLEMENTED
#         """
#         self.name = name
#         self.IS = IS
#         self.UT = UT
#         self.RS = RS
#         self.CJO = CJO
#         self.TT = TT
#         self.BV = BV
#         self.IBV = IBV
#         self.bandgap = 0.6


# class Diode(OnePortElement, ComposedElement): #  Controled Current Source
#     def __init__(self, name, nodes, model):
#         super().__init__(name, nodes, model.bandgap)
#         self.model = model

       
#     def compose(self, circuit):

#         print("compose")

#         #n0 = circuit.name2node[self.nodes[0]]
#         #n1 = circuit.name2node[self.nodes[1]]
        

#         if self.model.RS != 0:
#             between_node = circuit.generate_free_node()
#             #expression = f"{self.model.IS}*(exp((V({self.nodes[1]})-V({between_node}))/({self.model.UT})) - 1)"
#             expression = f"{self.model.IS}*(exp((V({between_node})-V({self.nodes[1]}))/({self.model.UT})) - 1)"
#             self.resistor = R("RS" + self.name, [self.nodes[0], between_node], self.model.RS)
#             self.ctrl_cs = CTRL_CS(self.name + "_ctrl_cs", [self.nodes[1], between_node], expression, 0.6)
            
#             circuit.add_element(self.resistor)
#         else:
#             expression = f"{self.model.IS}*(exp((V({self.nodes[1]})-V({self.nodes[0]}))/({self.model.UT})) - 1)"
#             self.ctrl_cs = CTRL_CS(self.name + "_ctrl_cs", self.nodes, expression, 0.6)
        
#         circuit.add_element(self.ctrl_cs)



#     def netlist_cmd(self):
#         name = self.name.upper()
#         if not name.startswith("D"):
#             name = "D" + name

#         return name + " " + str(self.nodes[0]) + " " + str(self.nodes[1])

#     def stamp(self, state_vector, Y, RHS, symbolic=True):
#         print("stamp")


"""
Main Circuit class which holds the definition of the Circuit and compiles circuit to matricies
"""

class Parameter():
    def __init__(self, name, value=None):
        self.name = name
        self.symbol = sy.Symbol(self.name)
        self.value = value

class Model():
    def __init__(self, name, **kwargs):
        print(kwargs)
        self.params = {}
        self.name = name
        for name, value in kwargs.items():
            self.params[name] = Parameter(name, value)

    def __repr__(self):
        pairs = []
        for name, param in self.params.items():
            pairs.append(str(name) + "=" + str(param.value))

        return " ".join(pairs)

    def __getattr__(self, attr):
        if attr in self.params.keys():
            return self.params[attr].symbol

        


    def __setattr__(self, attr, value):
        if attr is not "params":
            if attr in self.params.keys():
                self.params[attr].value = value

        super().__setattr__(attr, value)

    def exists(self, symbol):
        for name, param in self.params.items():
            if param.symbol == symbol:
                return True

        return False

    def value(self, symbol):
        for name, param in self.params.items():
            if param.symbol == symbol:
                return param.value

        raise ValueError("Symbol not found in Model")


class _SubCircuit():
    def __init__(self, subcircuit, name, nodes, parameter):
        self.nodes = list(map(str,nodes))
        self.subcir = subcircuit
        self.parameter = parameter
        self.name = name

        assert len(nodes) == len(self.subcir.export_nodes), "Number of nodes not as expected from SubCircut"

    def netlist_cmd(self):
        nodes_str = []
        for node in self.nodes:
            nodes_str = " ".join(self.nodes)

        return self.name + " " + nodes_str + " " + str(self.parameter.name)

    def components(self, circuit):
        #generate map subcircuit node to parent circuit free node
        node_map = {}
        for en, n in zip(self.subcir.export_nodes, self.nodes):
            node_map[str(en)] = str(n)


        for node in self.subcir.nodes:
            if node not in node_map:
                node_map[node] = circuit.generate_free_node()

        print("Node Map: ", self.name, node_map)

        clist = []

        for element in self.subcir.components:
            new_element = element.replace(self.subcir, circuit, node_map, self.parameter)
            new_element.name = new_element.name  + "_" +  self.name
            clist.append(new_element)

        return clist

class SubCircuit():
    def __init__(self, name, export_nodes, model):
        self.name = name
        self.components = []
        self.model = model
        self.voltages = {} #for voltages and currents
        self.export_nodes = list(map(str,export_nodes))
        self.nodes = []
        self.elements = []

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
        node = str(node)
        if node not in self.voltages:
            symbol = sy.Symbol("V("+str(node) + ")")
            self.voltages[node] = symbol

        return self.voltages[node]

    def I(self, component):
        pass

    def define(self, elements):
        self.elements = elements
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


"""
Main Circuit class which holds the definition of the Circuit and compiles circuit to matricies
"""
class Circuit():
    def __init__(self, ref_node):
        self.name = ""
        self.G = nx.MultiGraph()
        self.ref_node = ref_node
        self.name2node = {} #0 as reserved as GND
        self.elements = []
        self.voltages = {} #for voltages and currents

    def add_element(self, element):
        self.G.add_edges_from([(*element.nodes, {'element': element})])

    def generate_free_node(self):
        used_node_nrs = []
        
        for node_name in self.name2node.keys():
            try:
                node_nr = int(node_name)
                used_node_nrs.append(node_nr)
            except:
                continue

        #must be not super efficient jet: get the smalest number which is not in list
        for i in range(len(used_node_nrs)+1):
            if i not in used_node_nrs:
                self.name2node[str(i)] = max(self.name2node.values())+1
                return str(i)

    def V(self, node):
        if node not in self.voltages:
            symbol = sy.Symbol("V("+str(node) + ")")
            self.voltages[node] = symbol
            
        return self.voltages[node]

    def I(self, component):
        pass
            
    def define(self, celements):

        self.elements = celements
        # Get all nodes
        name_nodes = [str(self.ref_node)] #Ref node is 0
        for i, element in enumerate(celements):
            for node in element.nodes:
                if not node in name_nodes:
                    name_nodes.append(str(node))

        #assing a ascending number to it
        for i, name_node in enumerate(name_nodes):
            self.name2node[name_node] = i

        #Get elements from subcircuits
        elements = []
        for element in celements:
            if isinstance(element, _SubCircuit):
                components = element.components(self)
                for component in components:
                    elements.append(component)
            else:
                elements.append(element)

        print(name_nodes)

        print(self.name2node)
        
        #add elements to graph
        for i, element in enumerate(elements):
            self.add_element(element)

    def name_by_id(self, id):
        for n1 ,n2 , data in self.G.edges(data=True):
            element = data["element"]
            if id == element.id:
                return element.name

    def unwraped_netlist(self):
        netlist = ""
        for n1 ,n2 , data in self.G.edges(data=True):
            element = data["element"]
            netlist = netlist + element.netlist_cmd() + "\n"

        return netlist

    def to_netlist(self):
        netlist = ""
        for element in self.elements:
            netlist = netlist + element.netlist_cmd() + "\n"

        return netlist

    def matrices(self, symbolic = True):
        n = self.G.number_of_nodes()

        Y = amatrix()
        RHS = avector() # soruces
        X = state_vector(n)

        if symbolic:
            Y = amatrix(init_value = 0)
            RHS = avector(init_value = 0) # soruces

        ## Add Stamp to Matrices
        for n1 ,n2 , data in self.G.edges(data=True):
            element = data["element"]
            element.stamp(X, Y, RHS, self.name2node, symbolic=symbolic)

        if len(RHS.to_list()) != X._idx()+1:
            RHS[X._idx()] = 0.0


        return X, Y.to_list(), RHS.to_list()