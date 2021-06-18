import pyparsing as pp

import circuit
from circuit import Circuit
import sympy as sy
import pprint

import stamp_elements as se

pp = pprint.PrettyPrinter(indent=4)

from pyparsing import (
    Word,
    OneOrMore,
    alphas,
    nums,
    alphanums,
    printables,
    pyparsing_common,
    Char,
    Combine,
    Forward,
    FollowedBy,
    StringEnd,
    Group,
    LineEnd,
    Suppress,
    Optional,
    ZeroOrMore,
    restOfLine,
    White,
    Literal,
    ParserElement
)


ParserElement.setDefaultWhitespaceChars(' \t')

NL = Suppress(LineEnd())


used_param_start, used_param_end = Suppress('{'), Suppress('}')

used_param = used_param_start + Word(alphanums) + used_param_end

number_expr = pyparsing_common.number.copy()
value_unit = Group(number_expr("value") + Optional(Word(alphas))("unit"))
#value = (value_unit("unit_value") + NL) ^ (used_param("param") + NL)
value = Word(printables) + NL
passive = Char(alphas, excludeChars='Xx')("ident") + Word(nums)("number") + Group(OneOrMore( ~FollowedBy( value ) + Word(alphanums) ))("nodes")  + value 

# Xamp 5 4 2  ACamplifier PARAMS: Cin=20n Rbias=2.7K

name = Word(printables, excludeChars='_=')

param_start =  Suppress('PARAMS:')
param = Group(name("name")  + Suppress(Char('=')) + name("default"))
params = Group(param_start + OneOrMore(param))

subopt = (Word(printables) + NL) ^ (Word(printables) + params + NL)

subcir_elem = Char('Xx')("ident") + Word(alphanums)("name") + Group(OneOrMore( ~FollowedBy( subopt ) + Word(alphanums) ))("nodes")  + subopt 


cmd_line = Group(passive | subcir_elem)
cmd_lines = OneOrMore(cmd_line | NL)


sub_start, sub_end = Suppress('.SUBCKT'), Suppress('.ENDS')








nodes = Group(OneOrMore(~FollowedBy(param_start) + Word(alphanums)))

subcir_info = sub_start + Group(name("name") + nodes("nodes") + Optional(params("parameter")) )("info") + NL
subcir = Group(subcir_info + cmd_lines('net') + sub_end)




elem = Group(subcir("sub") |  cmd_lines("net"))


Lines =  ZeroOrMore(elem | NL)("elements")


import queue

def parse_value(value):
    try:
        value = float(value)
    except:
        value = sy.Symbol(value)

    return value

def parse_netlist(netlist_io):
    
    circuits = queue.LifoQueue()
    cir = circuit.Circuit(circuit.GND)

    subcircuits = {}

    top_cir = [cir, []]

    def cmd(string, location, tokens):
        nonlocal top_cir, circuits
        print("c::", tokens)
        tokens = tokens[0]

        idf = tokens[0]
        number = tokens[1]

        name = idf+number

        nodes = tokens[2]

        value = tokens[3]

        

        elm = None
        if idf.upper() == "R":
            value = parse_value(value)
            elm = se.R(name, nodes, value)

        if idf.upper() == "C":
            value = parse_value(value)
            elm = se.C(name, nodes, value)

        if idf.upper() == "L":
            value = parse_value(value)
            elm = se.L(name, nodes, value)

        if idf.upper() == "X":
            print("Sub Cir ", tokens, nodes, value, tokens[4])

            if value not in subcircuits:
                raise ValueError("SubCircuit not found " + str(value))

            params = {}


            if len(tokens) == 5: #with params
                for pname, pvalue in tokens[4]:
                    params[pname] = parse_value(pvalue)

            print('sub ', params)

            model = circuit.Model(str(params), **params)
            elm = subcircuits[value](name, nodes, model)

        if elm is not None:
            print("asd: ", elm.netlist_cmd())
            top_cir[1].append(elm)

        return tokens

    def start_subcir(string, location, tokens):
        nonlocal top_cir, circuits, subcircuits
        print("s::", tokens)
        tokens = tokens[0]

        params = {}

        sub_name = tokens[0]
        nodes = tokens[1]

        if len(tokens) == 3: #with params
            for name, value in tokens[2]:
                params[name] = value

        model = circuit.Model(sub_name, **params)
        sub = circuit.SubCircuit(sub_name, nodes, model)

        #print(params)

        subcircuits[sub_name] = sub

        circuits.put(top_cir)
        top_cir = [sub, []]

        return tokens

    def end_subcir(string, location, tokens):
        nonlocal top_cir, circuits
        print("e::", tokens)

        for c in top_cir[1]:
            print(c.netlist_cmd())
        top_cir[0].define(top_cir[1])

        top_cir = circuits.get()

        return tokens

    subcir_info.setParseAction(start_subcir)
    sub_end.setParseAction(end_subcir)
    cmd_line.setParseAction(cmd)

    pstr = Lines.parseString(net)
    print("------")
    pp.pprint(pstr.asDict())

    top_cir[0].define(top_cir[1])

    print("netlist: \n", cir.to_netlist())

    print(subcircuits.keys())

    return cir

if __name__ == '__main__':

    net = """

    L1 0 1 16


    .SUBCKT ddfd 1 2 3 PARAMS: value=1231 v1alue=1231 

    R1 1 2 1.000e+003 

    R2 2 0 value
    .ENDS

    C1 0 1 1
    X1 2 0 1 ddfd PARAMS: value=1231 v1alue=1231 
    """

    
    parse_netlist(net)