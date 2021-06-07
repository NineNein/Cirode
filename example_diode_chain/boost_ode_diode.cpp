#include <iostream>
#include <vector>
#include <fstream>
#include <boost/numeric/odeint.hpp>

#include "diode_circuit.hpp"



//[ rhs_function
/* The type of container used to hold the state vector */
typedef std::vector< double > state_type;


diode_circuit::Components components;
diode_circuit::diode_circuit diode(components);

#define AMP 100.0

/* The rhs of x' = f(x) */
void ode( const state_type &x , state_type &dxdt , const double t )
{
    diode_circuit::Sources sources;
    sources.V1 = AMP*sin(1e4*t)+1.0;
    diode(x, dxdt, t, sources);
}
//]

#define TOTAL_TIME 0.01
#define DT 1e-6

//[ integrate_observer
struct push_back_state_and_time
{
    std::vector< state_type >& m_states;
    std::vector< double >& m_times;

    push_back_state_and_time( std::vector< state_type > &states , std::vector< double > &times )
    : m_states( states ) , m_times( times ) { }

    void operator()( const state_type &x , double t )
    {
        m_states.push_back( x );
        m_times.push_back( t );
    }
};
//]

int main(int /* argc */ , char** /* argv */ )
{
    using namespace std;
    using namespace boost::numeric::odeint;


    //[ state_initialization
    state_type x(DIODE_CIRCUIT_VECTOR_SIZE);

    for(int i =0; i < DIODE_CIRCUIT_VECTOR_SIZE; ++i){
        x[i] = 0.0; 
    }

    //]

    ofstream out("diode_data.bin", ios::out | ios::binary);
    if(!out) {
        cout << "Cannot open file.";
        return 1;
    }

    //[ integrate_const_loop
    const double dt = DT;
    const double total_time = TOTAL_TIME;
    const double vsize = DIODE_CIRCUIT_VECTOR_SIZE;

    out.write(reinterpret_cast<const char*>(&dt), sizeof(double));
    out.write(reinterpret_cast<const char*>(&total_time), sizeof(double));
    out.write(reinterpret_cast<const char*>(&vsize), sizeof(double));

    vector<state_type> x_vec;
    vector<double> times;

    runge_kutta_fehlberg78< state_type > stepper;
    size_t steps = integrate_const(stepper, ode ,
        x , 0.0 , total_time , dt ,
        push_back_state_and_time( x_vec , times ) );

    

    for( size_t i=0; i<=steps; i++ )
    {

        //diode_circuit::Quantities quantities = diode.quantities(x_vec[i]);

        double source = AMP*sin(1e4*times[i])+1.0;
       
        out.write(reinterpret_cast<const char*>(&times[i]), sizeof(double));
        out.write(reinterpret_cast<const char*>(&source), sizeof(double));
        for(int j =0; j < DIODE_CIRCUIT_VECTOR_SIZE; ++j){
            out.write(reinterpret_cast<const char*>(&x_vec[i][j]), sizeof(double));
        }
        
    }

    out.close();
        
    //]

}
