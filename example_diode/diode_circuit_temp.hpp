#include <vector>

typedef std::vector< double > state_type;

/*
Generated by Cirode: https://github.com/NineNein/Cirode

Description of Circuit:
V1 1 0 1.0
I1 2 1 1.0
R1 0 2 1000.0
C1 0 2 1e-05

*/

namespace diode_circuit
{

    struct Components{
        double V1 = 1.0;
        double I1 = 1.0;
        double R1 = 1000.0;
        double C1 = 1e-05;
            
    };



    
    struct Sources {
        double V1 = 1.0;        
    };

    struct Ctrl_Sources {
        double I1 = 1.0;
        
    };
    

    struct Quantities {
        double V_1;
        double V_2;
        double I_V1;
        double I_R1;
        double I_C1;
        
    };

    class diode_circuit {

    public:

        Components components;

        diode_circuit(Components components) : components(components) { }

        Quantities _quantities(const state_type &x, const Sources sources, const Ctrl_Sources ctrl_sources)
        {
            Quantities quants;
            quants.V_1 = sources.V1;
            quants.V_2 = x[0];
            quants.I_V1 = ctrl_sources.I1;
            quants.I_R1 = x[0]/this->components.R1;
            quants.I_C1 = ctrl_sources.I1 - x[0]/this->components.R1;
            
            return quants;
        }

        int non_linear_sources(const gsl_vector * x, void *sources, gsl_vector * f){

            const double I1 = gsl_vector_get (x, 0);

            Sources sources = params;

            Ctrl_Sources ctrl_sources;

            ctrl_sources.I1 = I1;

            Quantities quantities = this._quantities(sources, ctrl_sources);

            double Vd = (quantities.V_1-quantities.V_2);

            double IS = 1e-15;
            double Vt = 0.025875;
            double Icalc = IS*(exp(Vd/Vt) - 1);

            const double y0 = I1 - Icalc;

            gsl_vector_set (f, 0, y0);


            return GSL_SUCCESS;
        }

        Quantities quantities(const state_type &x, const Sources sources)
        {

            Ctrl_Sources ctrl_sources;

            // call optimisation
                        
            return quants;
        }

        Ctrl_Sources _ctrl_sources(const state_type &x, const Sources sources){

        }

        void operator() ( const state_type &x , state_type &dxdt , const double /* t */, const Sources sources )
        {

            Ctrl_Sources ctrl_sources = this._ctrl_sources(x, sources);

            dxdt[0]=ctrl_sources.I1/this->components.C1 - x[0]/(this->components.C1*this->components.R1);
            
        }
        };

}