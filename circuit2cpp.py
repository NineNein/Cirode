from jinja2 import Environment, FileSystemLoader, select_autoescape
from sympy import *
import sympy as sy
import re


def compile2cpp(Circuit, circuit_name, output_file):
    Cir = Circuit

    X, Y, RHS = Cir.matrices()

    #Prepare Righ Hand Side
    idxs = sorted(list(X.state_vector["dt"].keys()))

    if len(idxs) == 0:
        #raise ValueError("Netlist needs an dynamic Element")
        if len(X.state_vector["sources"]) == 0:
            raise ValueError("Netlist needs an dynamic Element or a source")

    m = sy.Matrix(Y)
    pprint(m)
    im = m**-1

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

    # x = ["" for i in range(len(res))]
    # for idx in range(X.number_of_nodes-1):
    #     x[idx] = str(idx) + ": V_" + str(idx+1)

    # for id, idx in X.state_vector["current"].items():
    #     x[idx] = str(idx) + ": I_" + Cir.name_by_id(id)

    # for i, idx in enumerate(idxs):
    #     idx_state = X.state_vector["dt"][idx]
    #     x[idx_state] = str(idx_state) + ": dxdt[" + str(i) + "]"


    # print(x)

    

    #Fill quantities struct with std_values
    quantities = []
    for n in range(X.number_of_nodes-1):
        value = "V_" + str(n+1)
        quantities.append(value)

    for id, idx in X.state_vector["current"].items():
        value = "I_" + Cir.name_by_id(id)
        quantities.append(value)


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
        if element in X.state_vector["sources"] or element in X.state_vector["ctrl_sources"]:
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


    #Fill ctrl_sources struct
    print(Cir.name2node)
    ctrl_sources = []
    for n1 ,n2 , data in Cir.G.edges(data=True):
        element = data["element"]
        if element not in X.state_vector["ctrl_sources"]:
            continue

        name = element.name

        for i, expr in enumerate(dt_expr): 
            dt_expr[i] = re.sub( str(name) + r'(?!(\w+))', 'ctrl_sources.' + str(name), expr, flags=re.IGNORECASE)

        for i, expr in enumerate(quant_expr): #Did this because I could not figure out a regex which starts after =
            quant_expr[i] = quant_expr[i].split("=")[0] + "=" + re.sub(str(name) + r'(?!(\w+))', 'ctrl_sources.' + str(name), quant_expr[i].split("=")[1], flags=re.IGNORECASE)


        expr = str(element.expression)

        #re_model = re.compile(r"V\((.*?)\)")
        output = re.findall(r"V\((.*?)\)", expr)
        if not output:
            continue

        for match in output:
            match_node = Cir.name2node[match]
            print(expr)
            expr = expr.replace("V("+str(match)+")", "quants.V_"+str(match_node))
            print(expr)

            
        ctrl_sources.append([name, element.value, expr])

        # expr = element.expression
        # for i, quant in enumerate(quantities):  
            
        #     expr = re.sub( str(quant) + r'(?!(\w+))', 'quants.' + str(quant), expr, flags=re.IGNORECASE)

        # ctrl_sources.append([name, element.value, expr])

        



    #Fill components struct with std_values
    components = []
    for n1 ,n2 , data in Cir.G.edges(data=True):
        element = data["element"]
        name = element.name
        value = str(element.value)
        components.append([name, value])





    

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



    if not ctrl_sources:

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

    else:
        template = env.get_template('circuit_template_ctrl_sources.hpp')

        circuit_name = circuit_name
        output = template.render(
            circuit_desc = Cir.to_netlist(),
            circuit_name=circuit_name, 
            exprs = dt_expr, 
            Sources = sources,
            Ctrl_Sources = ctrl_sources,
            quant_expr = quant_expr,
            Quantities = quantities,
            Components=components)

    output_file.write(output)


