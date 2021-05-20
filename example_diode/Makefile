
netlist: netlist.txt
	python3 ../cirode.py netlist.txt diode_circuit

# ode: boost_ode_lrc.cpp netlist.txt
# 	python3 ../cirode.py netlist.txt diode_circuit
# 	g++ -o ode boost_ode_lrc.cpp

diode: iteration.cpp
	g++ -o diode iteration.cpp -lgsl -lgslcblas -lm
	./diode

gsl_test: gsltest.cpp
	g++ -o gsl gsltest.cpp  -lgsl -lgslcblas -lm