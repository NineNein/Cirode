
netlist: netlist.txt
	python3 ../cirode.py netlist.txt diode_circuit

# ode: boost_ode_lrc.cpp netlist.txt
# 	python3 ../cirode.py netlist.txt diode_circuit
# 	g++ -o ode boost_ode_lrc.cpp

# diode: iteration.cpp
# 	g++ -o diode iteration.cpp -lgsl -lgslcblas -lm
# 	./diode

diode: boost_ode_diode.cpp diode_circuit.hpp
	g++ -o diode boost_ode_diode.cpp  -lgsl -lgslcblas -lm