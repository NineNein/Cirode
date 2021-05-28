#include <vector>
#include <gsl/gsl_vector.h>
#include <gsl/gsl_multiroots.h>
#include <iostream>

typedef std::vector< double > state_type;

/*
Generated by Cirode: https://github.com/NineNein/Cirode

Description of Circuit:
V1 1 0 1.0
RSD1 1 2 0.1
R2 0 3 1000.0
GD1_CTRL_CS 3 2 0.6

*/

namespace diode_circuit
{

    struct Components{
        double V1 = 1.0;
        double RSD1 = 0.1;
        double R2 = 1000.0;
        double D1_ctrl_cs = 0.6;
            
    };



    
    struct Sources {
        double V1 = 1.0;
        
    };
    

    
    struct Ctrl_Sources {
        double D1_ctrl_cs = 0.6;
        
    };
    

    struct Quantities {
        double V_1;
        double V_2;
        double V_3;
        double I_V1;
        double I_RSD1;
        double I_R2;
        
    };

    class diode_circuit;
    struct r_params{

        diode_circuit* obj;

        Sources sources;
        };


    int root_finding(const gsl_vector * xs, void *params, gsl_vector * f);


    class diode_circuit {


    public:

        Quantities _quantities(
            
            
            const Sources sources
            ,
            const Ctrl_Sources ctrl_sources
            ){
            Quantities quants;
            quants.V_1 = sources.V1;
            quants.V_2 = ctrl_sources.D1_ctrl_cs*this->components.R2;
            quants.V_3 = -ctrl_sources.D1_ctrl_cs*this->components.RSD1 + sources.V1;
            quants.I_V1 = ctrl_sources.D1_ctrl_cs;
            quants.I_RSD1 = -ctrl_sources.D1_ctrl_cs;
            quants.I_R2 = ctrl_sources.D1_ctrl_cs;
            
            return quants;
        }


        Ctrl_Sources get_ctrl_sources(
            
            
            const Sources sources
            ){
            const gsl_multiroot_fsolver_type *T;
            gsl_multiroot_fsolver *s;

            int status;
            size_t i, iter = 0;
            const size_t n = 1;

            struct r_params p{
                this,
                
                
                sources
                };

            gsl_multiroot_function f = {&root_finding, n, &p};


            gsl_vector *xs = gsl_vector_alloc (n);

            gsl_vector_set (xs, 0, 0.6);
            
            

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
                gsl_vector_get (s->x, 0) 
                
            };

            gsl_multiroot_fsolver_free (s);
            gsl_vector_free (xs);

            return ctrl_sources;

        }


        Components components;

        diode_circuit(Components components) : components(components) { }

        Quantities quantities(
            
            
            const Sources sources
            ){
            Quantities quants;
            Ctrl_Sources ctrl_sources = this->get_ctrl_sources(
                
                
                sources
                );

            quants.V_1 = sources.V1;
            quants.V_2 = ctrl_sources.D1_ctrl_cs*this->components.R2;
            quants.V_3 = -ctrl_sources.D1_ctrl_cs*this->components.RSD1 + sources.V1;
            quants.I_V1 = ctrl_sources.D1_ctrl_cs;
            quants.I_RSD1 = -ctrl_sources.D1_ctrl_cs;
            quants.I_R2 = ctrl_sources.D1_ctrl_cs;
            
            return quants;
        }

        };





    int root_finding(const gsl_vector * xs, void *params, gsl_vector * f){

        struct Ctrl_Sources ctrl_sources{
            gsl_vector_get (xs, 0) 
            
        };


        diode_circuit* obj = ((struct r_params *) params)->obj;

        Sources sources = ((struct r_params *) params)->sources;
        Quantities quants = obj->_quantities(
            
            
            sources
            ,
            ctrl_sources
            );


        double I_0     = gsl_vector_get(xs, 0);
        double Icalc_0 = 1e-15*(exp((quants.V_3-quants.V_2)/(0.025875)) - 1);
        gsl_vector_set (f, 0, I_0-Icalc_0);
        

        return GSL_SUCCESS;
    }

}