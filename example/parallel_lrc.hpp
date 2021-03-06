#include <vector>

typedef std::vector< double > state_type;

/*
Generated by Cirode: https://github.com/NineNein/Cirode

Description of Circuit:
R1 0 1 1000.0
L1 0 1 0.001
C1 0 1 1e-06

*/

namespace parallel_lrc
{

    struct Components{
        double R1 = 1000.0;
        double L1 = 0.001;
        double C1 = 1e-06;
            
    };



    

    struct Quantities {
        double V_1;
        double I_R1;
        double I_L1;
        double I_C1;
        
    };

    class parallel_lrc {

    public:

        Components components;

        parallel_lrc(Components components) : components(components) { }

        Quantities quantities(const state_type &x)
        {
            Quantities quants;
            quants.V_1 = x[0];
            quants.I_R1 = x[0]/this->components.R1;
            quants.I_L1 = x[1];
            quants.I_C1 = -x[1] - x[0]/this->components.R1;
            
            return quants;
        }

        void operator() ( const state_type &x , state_type &dxdt , const double /* t */)
        {
            dxdt[0]=-x[1]/this->components.C1 - x[0]/(this->components.C1*this->components.R1);
            dxdt[1]=x[0]/this->components.L1;
            
        }
    };

}