#include <iostream>
#include <vector>
#include <fstream>
#include <boost/numeric/odeint.hpp>

#include "diode_circuit.hpp"


diode_circuit::Components components;
diode_circuit::diode_circuit diode(components);

#define TOTAL_TIME 0.01
#define DT 1e-6

int main(int /* argc */ , char** /* argv */ )
{
    using namespace std;
    using namespace boost::numeric::odeint;

    ofstream out("diode_data.bin", ios::out | ios::binary);
    if(!out) {
        cout << "Cannot open file.";
        return 1;
    }

    //[ integrate_const_loop
    const double dt = DT;
    const double total_time = TOTAL_TIME;

    out.write(reinterpret_cast<const char*>(&dt), sizeof(double));
    out.write(reinterpret_cast<const char*>(&total_time), sizeof(double));
    
    for(double t = 0; t < TOTAL_TIME; t += DT)
    {
        diode_circuit::Sources sources;
        sources.V1 = 1.0*sin(1e4*t)+1.0;
        diode_circuit::Quantities quantities = diode.quantities(sources);

        out.write(reinterpret_cast<const char*>(&t), sizeof(double));
        out.write(reinterpret_cast<const char*>(&quantities.V_1), sizeof(double));
        out.write(reinterpret_cast<const char*>(&quantities.V_2), sizeof(double));
        out.write(reinterpret_cast<const char*>(&quantities.V_3), sizeof(double));
    }

    out.close();
        
}
