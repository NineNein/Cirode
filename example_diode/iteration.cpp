#include <iostream>
#include <vector>
#include <fstream>
#include <math.h>
#include "diode_circuit_simple.hpp"

#include <gsl/gsl_vector.h>
#include <gsl/gsl_multiroots.h>


//[ rhs_function
/* The type of container used to hold the state vector */
typedef std::vector< double > state_type;


diode_circuit::Components components;
diode_circuit::diode_circuit diode(components);



int non_linear_sources(const gsl_vector * x, void *params, gsl_vector * f){

    const double I1 = gsl_vector_get (x, 0);

    diode_circuit::Sources sources;
    sources.I1 = I1;
    diode_circuit::Quantities quantities = diode.quantities(sources);

    double Vd = (quantities.V_1-quantities.V_2);

    double IS = 1e-15;
    double Vt = 0.025875;

    double Icalc = IS*(exp(Vd/Vt) - 1);

    const double y0 = I1 - Icalc;

    gsl_vector_set (f, 0, y0);


    return GSL_SUCCESS;
}

/*
There are two cases of controlled sources

1) The Control is independent of the output of the source

2) The Output of the source feeds back to the input



*/

double current(double I1){

    diode_circuit::Sources sources;
    sources.I1 = I1;
    diode_circuit::Quantities quantities = diode.quantities(sources);

    double Vd = (quantities.V_1-quantities.V_2);

    double IS = 1e-15;
    double Vt = 0.025875;

    double Icalc = IS*(exp(Vd/Vt) - 1);

    return I1 - Icalc;
}


struct rparams{};


int
print_state (size_t iter, gsl_multiroot_fsolver * s)
{
  printf ("iter = %7u x = % .7f"
          "f(x) = % .7e\n",
          iter,
          gsl_vector_get (s->x, 0),
          //gsl_vector_get (s->x, 1),
          gsl_vector_get (s->f, 0));
          //gsl_vector_get (s->f, 1));
}

int main(int /* argc */ , char** /* argv */ )
{
    using namespace std;

    const gsl_multiroot_fsolver_type *T;
    gsl_multiroot_fsolver *s;

    int status;
    size_t i, iter = 0;

    const size_t n = 1;
    struct rparams p;
    gsl_multiroot_function f = {&non_linear_sources, n, &p};


    gsl_vector *x = gsl_vector_alloc (n);
    gsl_vector_set (x, 0, 0.6);


    T = gsl_multiroot_fsolver_hybrids;
    s = gsl_multiroot_fsolver_alloc (T, n);
    gsl_multiroot_fsolver_set (s, &f, x);

    print_state (iter, s);

    do
        {
        iter++;
        status = gsl_multiroot_fsolver_iterate (s);

        print_state (iter, s);

        if (status)   /* check if solver is stuck */
            break;

        status =
            gsl_multiroot_test_residual (s->f, 1e-7);
        }
    while (status == GSL_CONTINUE && iter < 1000);

    printf ("status = %s\n", gsl_strerror (status));

    gsl_multiroot_fsolver_free (s);
    gsl_vector_free (x);








/*
e.g.

voltages in, calculating sources currents

new voltages out


*/


    double Vd = 0.6;

    diode_circuit::Sources sources;

    for(int i = 0; i < 100; ++i){

        

        double IS = 1e-15;
        double Vt = 0.025875;

        
        sources.V1 = 1.0; 

        sources.I1 = IS*(exp(Vd/Vt) - 1);

        diode_circuit::Quantities quantities = diode.quantities(sources);

        //Vd = (quantities.V_1-quantities.V_2);


        //cout<<(quantities.V_1-quantities.V_2)<<endl;

        if((quantities.V_1-quantities.V_2) > Vd){
            Vd += (quantities.V_1-quantities.V_2)/1000.0;
        }else{
            Vd -= (quantities.V_1-quantities.V_2)/1000.0;
        }

        //cout<<quantities.V_1<<endl;
        //cout<<quantities.V_2<<endl;
        //cout<<"Vd "<<Vd<<endl;
    }

        cout<<sources.I1<<endl;
        cout<<current(sources.I1)<<endl;




}