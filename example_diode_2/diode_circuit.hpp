#include <vector>
#include <gsl/gsl_vector.h>
#include <gsl/gsl_multiroots.h>
#include <iostream>

typedef std::vector< double > state_type;

/*
Generated by Cirode: https://github.com/NineNein/Cirode

Description of Circuit:
V1 5 0 1.0
R5 1 5 0.1
C2 0 2 1e-05
R2 0 2 1000.0
R1 0 3 1000.0
C1 0 3 1e-05
G1 2 1 0.6
R6 4 2 0.1
G2 3 4 0.6

*/

namespace diode_circuit
{

    struct Components{
        double V1 = 1.0;
        double R5 = 0.1;
        double C2 = 1e-05;
        double R2 = 1000.0;
        double R1 = 1000.0;
        double C1 = 1e-05;
        double G1 = 0.6;
        double R6 = 0.1;
        double G2 = 0.6;
            
    };



    
    struct Sources {
        double V1 = 1.0;
        
    };
    

    
    struct Ctrl_Sources {
        double G1 = 0.6;
        double G2 = 0.6;
        
    };
    

    struct Quantities {
        double V_1;
        double V_2;
        double V_3;
        double V_4;
        double V_5;
        double I_V1;
        double I_R5;
        double I_C2;
        double I_R2;
        double I_R1;
        double I_C1;
        double I_R6;
        
    };

    class diode_circuit;
    struct r_params{

        diode_circuit* obj;

        state_type x;
        Sources sources;
        };


    int root_finding(const gsl_vector * xs, void *params, gsl_vector * f);


    class diode_circuit {


    public:

        Quantities _quantities(
            
            
            const state_type &x
            ,
            const Sources sources
            ,
            const Ctrl_Sources ctrl_sources
            ){
            Quantities quants;
            quants.V_1 = sources.V1;
            quants.V_2 = -ctrl_sources.G1*this->components.R5 + sources.V1;
            quants.V_3 = x[0];
            quants.V_4 = -ctrl_sources.G2*this->components.R6 + x[0];
            quants.V_5 = x[1];
            quants.I_V1 = ctrl_sources.G1;
            quants.I_R5 = ctrl_sources.G1;
            quants.I_C2 = ctrl_sources.G1 - ctrl_sources.G2 - x[0]/this->components.R2;
            quants.I_R2 = x[0]/this->components.R2;
            quants.I_R1 = x[1]/this->components.R1;
            quants.I_C1 = ctrl_sources.G2 - x[1]/this->components.R1;
            quants.I_R6 = ctrl_sources.G2;
            
            return quants;
        }


        Ctrl_Sources get_ctrl_sources(
            
            
            const state_type &x
            ,
            const Sources sources
            ){
            const gsl_multiroot_fsolver_type *T;
            gsl_multiroot_fsolver *s;

            int status;
            size_t i, iter = 0;
            const size_t n = 2;

            struct r_params p{
                this,
                
                
                x
                ,
                sources
                };

            gsl_multiroot_function f = {&root_finding, n, &p};


            gsl_vector *xs = gsl_vector_alloc (n);

            gsl_vector_set (xs, 0, 0.6);
            gsl_vector_set (xs, 1, 0.6);
            
            

            //T = gsl_multiroot_fsolver_hybrids;
            //T = gsl_multiroot_fsolver_hybrid;
            //T = gsl_multiroot_fsolver_broyden;
            T = gsl_multiroot_fsolver_dnewton;
            s = gsl_multiroot_fsolver_alloc (T, n);
            gsl_multiroot_fsolver_set (s, &f, xs);

            do
            {
            iter++;
            status = gsl_multiroot_fsolver_iterate (s);

            if (status){   /* check if solver is stuck */
                std::cout<<"solver is stuck"<<std::endl;
                break;
            }

            status =
                gsl_multiroot_test_residual (s->f, 1e-7);
            }
            while (status == GSL_CONTINUE && iter < 1000);

            

            struct Ctrl_Sources ctrl_sources{
                gsl_vector_get (s->x, 0) , 
                gsl_vector_get (s->x, 1) 
                
            };

            gsl_multiroot_fsolver_free (s);
            gsl_vector_free (xs);

            return ctrl_sources;

        }


        Components components;

        diode_circuit(Components components) : components(components) { }

        Quantities quantities(
            
            
            const state_type &x
            ,
            const Sources sources
            ){
            Quantities quants;
            Ctrl_Sources ctrl_sources = this->get_ctrl_sources(
                
                
                x
                ,
                sources
                );

            quants.V_1 = sources.V1;
            quants.V_2 = -ctrl_sources.G1*this->components.R5 + sources.V1;
            quants.V_3 = x[0];
            quants.V_4 = -ctrl_sources.G2*this->components.R6 + x[0];
            quants.V_5 = x[1];
            quants.I_V1 = ctrl_sources.G1;
            quants.I_R5 = ctrl_sources.G1;
            quants.I_C2 = ctrl_sources.G1 - ctrl_sources.G2 - x[0]/this->components.R2;
            quants.I_R2 = x[0]/this->components.R2;
            quants.I_R1 = x[1]/this->components.R1;
            quants.I_C1 = ctrl_sources.G2 - x[1]/this->components.R1;
            quants.I_R6 = ctrl_sources.G2;
            
            return quants;
        }

        void operator() ( const state_type &x , state_type &dxdt , const double t , const Sources sources )
        {

            Ctrl_Sources ctrl_sources = this->get_ctrl_sources(
                x
                ,sources
                );

            dxdt[0]=ctrl_sources.G1/this->components.C2 - ctrl_sources.G2/this->components.C2 - x[0]/(this->components.C2*this->components.R2);
            dxdt[1]=ctrl_sources.G2/this->components.C1 - x[1]/(this->components.C1*this->components.R1);
            
        }
        };





    int root_finding(const gsl_vector * xs, void *params, gsl_vector * f){

        struct Ctrl_Sources ctrl_sources{
            gsl_vector_get (xs, 0) , 
            gsl_vector_get (xs, 1) 
            
        };


        diode_circuit* obj = ((struct r_params *) params)->obj;

        state_type x = ((struct r_params *) params)->x;
        Sources sources = ((struct r_params *) params)->sources;
        Quantities quants = obj->_quantities(
             x
            ,
            sources
            ,
            ctrl_sources
            );


        double I_0     = gsl_vector_get(xs, 0);
        double Icalc_0 = 1e-15*(exp((quants.V_2-quants.V_3)/0.025875) - 1);
        gsl_vector_set (f, 0, I_0-Icalc_0);
        double I_1     = gsl_vector_get(xs, 1);
        double Icalc_1 = 1e-15*(exp((quants.V_4-quants.V_5)/0.025875) - 1);
        gsl_vector_set (f, 1, I_1-Icalc_1);
        

        return GSL_SUCCESS;
    }

}