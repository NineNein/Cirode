import networkx as nx
import numpy as np
import sympy as sy

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



"""
Base class for OnePortElement
it will count automaticly element_id_counter up and such gives every element an unique ID
"""
element_id_counter = 0
class OnePortElement(object):
    def __init__(self, name, nodes, value):
        global element_id_counter
        assert len(nodes) == 2, "One Port Element needs two nodes"
        self.name = name
        self.nodes = nodes
        self.value = value

        self.id = element_id_counter
        element_id_counter += 1

    def stamp(self, state_vector,  Y, RHS):
        pass


class TwoPortElement(object):
    def __init__(self, name, nodes, value):
        global element_id_counter
        assert len(nodes) == 4, "Two Port Element needs four nodes"
        self.name = name
        self.nodes = nodes
        self.value = value

        self.id = element_id_counter
        element_id_counter += 1

    def stamp(self, state_vector,  Y, RHS):
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


    def stamp(self, state_vector,  Y, RHS, symbolic=True):
        k = self.nodes[0]-1
        l = self.nodes[1]-1

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
Class for a Capacitor, contains netlist command creation and the stamp for a Capacitor
"""
class C(OnePortElement):
    def __init__(self, name, nodes, value):
        super().__init__(name, nodes, value)

    def netlist_cmd(self):
        name = self.name.upper()
        if not name.startswith("C"):
            name = "C" + name

        return name + " " + str(self.nodes[0]) + " " + str(self.nodes[1]) + " " + str(self.value) 

    def stamp(self, state_vector, Y, RHS, symbolic=True):
        k = self.nodes[0]-1
        l = self.nodes[1]-1

        br_idx = state_vector.add_current(self.id)

        if symbolic:
            value = sy.Symbol(self.name)
        else:
            value = self.value


        if k >= 0:
            dk = state_vector.dt(k)
            if dk == -1:
                dk = state_vector.add_dt(k)
                Y[dk][k] = 1 ## add unit equation

            Y[k][br_idx] += 1
            Y[br_idx][dk] += value
        
        if l >= 0:
            dl = state_vector.dt(l)
            if dl == -1:
                dl = state_vector.add_dt(l)
                Y[dl][l] = 1 ## add unit equatio

            Y[l][br_idx] += -1
            Y[br_idx][dl] += -value

        Y[br_idx][br_idx] = 1

        RHS[br_idx] = 0.0

"""
Class for a Inductor, contains netlist command creation and the stamp for a Inductor
"""
class L(OnePortElement):
    def __init__(self, name, nodes, value):
        super().__init__(name, nodes, value)


    def netlist_cmd(self):
        name = self.name.upper()
        if not name.startswith("L"):
            name = "L" + name

        return name + " " + str(self.nodes[0]) + " " + str(self.nodes[1]) + " " + str(self.value) 

    def stamp(self, state_vector, Y, RHS, symbolic=True):
        k = self.nodes[0]-1
        l = self.nodes[1]-1

        br_idx = state_vector.add_current(self.id)

        if symbolic:
            value = sy.Symbol(self.name)
        else:
            value = self.value
        
        di = state_vector.dt(br_idx)
        if di == -1:
            di = state_vector.add_dt(br_idx)
            Y[di][br_idx] = 1 ## add unit equation

        if k >= 0:
            Y[k][br_idx] += 1
            Y[br_idx][k] += 1
        
        if l >= 0:
            Y[l][br_idx] += -1
            Y[br_idx][l] += -1

        Y[br_idx][di] = value

        RHS[br_idx] = 0.0


"""
Class for a Voltage Source, contains netlist command creation and the stamp for a Voltage Source
"""
class VS(OnePortElement): #Voltage Source
    def __init__(self, name, nodes, value):
        super().__init__(name, nodes, value)

    def netlist_cmd(self):
        name = self.name.upper()
        if not name.startswith("V"):
            name = "V" + name

        return name + " " + str(self.nodes[0]) + " " + str(self.nodes[1]) + " " + str(self.value) 

    def stamp(self, state_vector, Y, RHS, symbolic=True):
        k = self.nodes[0]-1
        l = self.nodes[1]-1

        state_vector.state_vector["sources"].append(self)

        br_idx = state_vector.add_current(self.id)

        if symbolic:
            value = sy.Symbol(self.name)
        else:
            value = self.value

        if k >= 0:
            Y[k][br_idx] += 1
            Y[br_idx][k] += 1
        
        if l >= 0:
            Y[l][br_idx] += -1
            Y[br_idx][l] += -1

        RHS[br_idx] = value

"""
Class for a Current Source, contains netlist command creation and the stamp for a Current Source
"""
class IS(OnePortElement): #Current Source
    def __init__(self, name, nodes, value):
        super().__init__(name, nodes, value)

    def netlist_cmd(self):
        name = self.name.upper()
        if not name.startswith("I"):
            name = "I" + name

        return name + " " + str(self.nodes[0]) + " " + str(self.nodes[1]) + " " + str(self.value) 

    def stamp(self, state_vector, Y, RHS, symbolic=True):
        k = self.nodes[0]-1
        l = self.nodes[1]-1

        state_vector.state_vector["sources"].append(self)

        if symbolic:
            value = sy.Symbol(self.name)
        else:
            value = self.value

        RHS[k] = -value
        RHS[l] = value

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

    def stamp(self, state_vector, Y, RHS, symbolic=True):
        k = self.nodes[0]-1
        l = self.nodes[1]-1

        state_vector.state_vector["ctrl_sources"].append(self)

        assert symbolic, "VCCS can't be used yet in non symbolic mode"

        value = sy.Symbol(self.name)

        RHS[k] = -value
        RHS[l] = value

"""
Class for a Diode, creates diode with an series resistor and a controlled current source
"""

class model:
    def __init__(self):
        pass

class diode_model(model):
    def __init__(self, name, IS=1e-14, UT = 0.025875, RS = 1e-10, CJO = 0, TT=0, BV=None, IBV=1e-10):
        """
        - name is the name of the model of the diode specified in the model line.
        - IS: saturation current,
        - UT: thermal voltage
        - RS: the series resistance, should not be zero because thise could lead to non possible root finding
        - CJO - junction capacitance , NOT CURRENTLY IMPLEMENTED
        - TT - transit time , NOT CURRENTLY IMPLEMENTED
        - BV - reverse bias breakdown voltage, None = Inf , NOT CURRENTLY IMPLEMENTED
        - IBV - the reverse bias breakdown current, NOT CURRENTLY IMPLEMENTED
        """
        self.name = name
        self.IS = IS
        self.UT = UT
        self.RS = RS
        self.CJO = CJO
        self.TT = TT
        self.BV = BV
        self.IBV = IBV


class Diode(OnePortElement): #  Controled Current Source
    def __init__(self, name, nodes, model):
        super().__init__(name, nodes, model.bandgap)
        self.model = model
       
    def netlist_cmd(self):
        name = self.name.upper()
        if not name.startswith("D"):
            name = "D" + name

        return name + " " + str(self.nodes[0]) + " " + str(self.nodes[1])

    def stamp(self, state_vector, Y, RHS, symbolic=True):
        expression = f"{self.model.IS}*(exp((V_{self.node[0]}-V_{self.node[1]})/({self.model.UT})) - 1)"

        ctrl_cs = CTRL_CS(self.name + "_ctrl_cs", self.nodes, expression, 0.6)
        resistor = R(self.name + "_R", self.nodes, self.model.RS)

        ctrl_cs.stamp(state_vector, Y, RHS, symbolic=symbolic)
        resistor.stamp(state_vector, Y, RHS, symbolic=symbolic)




"""
Main Circuit class which holds the definition of the Circuit and compiles circuit to matricies
"""
class Circuit():
    def __init__(self, ref_node):
        self.G = nx.MultiGraph()
        self.ref_node = ref_node

    def define(self, elements):
        for i, element in enumerate(elements):
            self.G.add_edges_from([(*element.nodes, {'element': element})])

    def name_by_id(self, id):
        for n1 ,n2 , data in self.G.edges(data=True):
            element = data["element"]
            if id == element.id:
                return element.name

    def to_netlist(self):
        netlist = ""
        for n1 ,n2 , data in self.G.edges(data=True):
            element = data["element"]
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
            element.stamp(X, Y, RHS, symbolic=symbolic)

        if len(RHS.to_list()) != X._idx()+1:
            RHS[X._idx()] = 0.0


        return X, Y.to_list(), RHS.to_list()

            
        
