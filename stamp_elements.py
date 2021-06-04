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

    def replace(self, node_map, parameters):
        pass

    def stamp(self, state_vector,  Y, RHS, name2node, symbolic=True):
        pass


class TwoPortElement(object):
    def __init__(self, name, nodes, value):
        global element_id_counter
        assert len(nodes) == 4, "Two Port Element needs four nodes"
        self.name = name
        self.nodes = list(map(str,nodes))
        self.value = value

        self.id = element_id_counter
        element_id_counter += 1

    def replace(self, node_map, parameters):
        pass

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


    def replace(self, subcircuit, circuit, node_map, parameters):
        new_nodes = []
        new_value = self.value
        for node in self.nodes:
            if node not in node_map:
                raise ValueError("node_map does not contain node")

            new_nodes.append(node_map[node])

        if parameters.exists(self.value):
            new_value = parameters.value(self.value)

        return R(self.name, new_nodes, new_value)
        

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

    def stamp(self, state_vector, Y, RHS, name2node, symbolic=True):
        k = name2node[self.nodes[0]]-1
        l = name2node[self.nodes[1]]-1

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

    def stamp(self, state_vector, Y, RHS, name2node, symbolic=True):
        k = name2node[self.nodes[0]]-1
        l = name2node[self.nodes[1]]-1

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

    def stamp(self, state_vector, Y, RHS, name2node, symbolic=True):
        k = name2node[self.nodes[0]]-1
        l = name2node[self.nodes[1]]-1

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

    def stamp(self, state_vector, Y, RHS, name2node, symbolic=True):
        k = name2node[self.nodes[0]]-1
        l = name2node[self.nodes[1]]-1

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

    def replace(self, subcircuit, circuit, node_map, parameters):
        new_nodes = []
        new_value = self.value
        for node in self.nodes:
            if node not in node_map:
                raise ValueError("node_map does not contain node")

            new_nodes.append(node_map[node])

        if parameters.exists(self.value):
            new_value = parameters.value(self.value)

        print("Replace Nodes and parameters in Expression")

        new_expression = self.expression
        subs = {}
        print(new_expression)
        for node in subcircuit.nodes:
            print(node, subcircuit.V(node), circuit.V(node_map[node]))
            subs[sy.UnevaluatedExpr(subcircuit.V(node))] = sy.UnevaluatedExpr(circuit.V(node_map[node]))

        #new_expression = new_expression.subs(subcircuit.V(node), circuit.V(node_map[node]))
        print(subs)
        new_expression = new_expression.subs(subs)

        for name, param in parameters.params.items(): 
            new_expression = new_expression.subs(param.symbol, param.value)
        
        print(new_expression)
        return CTRL_CS(self.name, new_nodes, new_expression, new_value)

    def stamp(self, state_vector, Y, RHS, name2node, symbolic=True):
        k = name2node[self.nodes[0]]-1
        l = name2node[self.nodes[1]]-1

        state_vector.state_vector["ctrl_sources"].append(self)

        assert symbolic, "VCCS can't be used yet in non symbolic mode"

        value = sy.Symbol(self.name)

        RHS[k] = -value
        RHS[l] = value