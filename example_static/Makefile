
netlist: netlist.txt
	python3 ../cirode.py netlist.txt static_circuit

ode: boost_ode_lrc.cpp netlist.txt
	python3 ../cirode.py netlist.txt static_circuit
	g++ -o ode boost_ode_lrc.cpp