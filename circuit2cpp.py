from jinja2 import Environment, FileSystemLoader, select_autoescape
from sympy import *
import sympy as sy
import re

def compile2cpp(Circuit, circuit_name, output_file):
    Cir = Circuit

    X, Y, RHS = Cir.matrices()
    m = sy.Matrix(Y)
    im = m**-1

    

    #Prepare Righ Hand Side
    idxs = sorted(list(X.state_vector["dt"].keys()))
    for i, idx in enumerate(idxs):
        value = sy.Symbol("x["+ str(i) + "]")
        idx_state = X.state_vector["dt"][idx]
        RHS[idx_state] = value

    #Solve System
    rhs = sy.Matrix(RHS)
    res = (rhs.T*im.T).T #Upsa now its right...


    #Generate expression for dy/dt = f(y)
    dt_expr = []
    for i, idx in enumerate(idxs):
        idx_state = X.state_vector["dt"][idx]
        dt_expr.append("dxdt[" + str(i)+ "]=" +  ccode(res[idx_state]))

    #Generate expression other circuit quantities
    quant_expr = []
    for idx in range(X.number_of_nodes-1):
        name = "V_" + str(idx+1)
        quant_expr.append("quants." + name + " = " +  ccode(res[idx]))

    for id, idx in X.state_vector["current"].items():
        name = "I_" + Cir.name_by_id(id)
        quant_expr.append("quants." + name + " = " +  ccode(res[idx]))


    ## replace names in both expr with this->components.name to adapt to template.hpp
    for n1 ,n2 , data in Cir.G.edges(data=True):
        element = data["element"]
        if element in X.state_vector["sources"]:
            continue

        name = element.name
        for i, expr in enumerate(dt_expr): 
            dt_expr[i] = re.sub( str(name) + r'(?!(\w+))', 'this->components.' + str(name), expr, flags=re.IGNORECASE)

        for i, expr in enumerate(quant_expr): #Did this because I could not figure out a regex which starts after =
            quant_expr[i] = quant_expr[i].split("=")[0] + "=" + re.sub(str(name) + r'(?!(\w+))', 'this->components.' + str(name), quant_expr[i].split("=")[1], flags=re.IGNORECASE)

        

    #Fill sources struct
    sources = []
    for n1 ,n2 , data in Cir.G.edges(data=True):
        element = data["element"]
        if element not in X.state_vector["sources"]:
            continue

        name = element.name
        sources.append([name, element.value])
        for i, expr in enumerate(dt_expr): 
            dt_expr[i] = re.sub( str(name) + r'(?!(\w+))', 'sources.' + str(name), expr, flags=re.IGNORECASE)

        for i, expr in enumerate(quant_expr): #Did this because I could not figure out a regex which starts after =
            quant_expr[i] = quant_expr[i].split("=")[0] + "=" + re.sub(str(name) + r'(?!(\w+))', 'sources.' + str(name), quant_expr[i].split("=")[1], flags=re.IGNORECASE)



    #Fill components struct with std_values
    components = []
    for n1 ,n2 , data in Cir.G.edges(data=True):
        element = data["element"]
        name = element.name
        value = str(element.value)
        components.append([name, value])


    #Fill quantities struct with std_values
    quantities = []
    for n in range(X.number_of_nodes-1):
        value = "V_" + str(n+1)
        quantities.append(value)

    for id, idx in X.state_vector["current"].items():
        value = "I_" + Cir.name_by_id(id)
        quantities.append(value)



    import os 
    from os.path import relpath

    __location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

    relp = relpath(__location__, os.getcwd())
    filename = os.path.join(relp, '')
    
    #Execute Template
    templateLoader = FileSystemLoader(searchpath=filename)
    env = Environment(
        loader=templateLoader,
        autoescape=select_autoescape(['c++'])
    )

    #template = env.get_template(dir_path + '/circuit_template.hpp')
    template = env.get_template('circuit_template.hpp')

    circuit_name = circuit_name
    output = template.render(
        circuit_desc = Cir.to_netlist(),
        circuit_name=circuit_name, 
        exprs = dt_expr, 
        Sources = sources,
        quant_expr = quant_expr,
        Quantities = quantities,
        Components=components)

    output_file.write(output)


