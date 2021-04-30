import circuit
import circuit2cpp
import netlist_parser

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("netlist", type=str, help="netlist file")
    parser.add_argument("circuit", type=str, help="circuit name")

    args = parser.parse_args()

    with open(args.netlist, "r") as f:
        component_list = netlist_parser.parse_netlist(f)

    Cir = circuit.Circuit(circuit.GND)
    Cir.define(component_list)

    
    
    with open(args.circuit + ".hpp", "w") as f:
        circuit2cpp.compile2cpp(Cir, args.circuit, f)