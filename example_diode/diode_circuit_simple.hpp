#include <vector>

typedef std::vector< double > state_type;

/*
Generated by Cirode: https://github.com/NineNein/Cirode

Description of Circuit:
V1 1 0 1.0
I1 2 1 1.0
R1 0 2 1000.0

*/

namespace diode_circuit
{

    struct Components{
        double V1 = 1.0;
        double I1 = 1.0;
        double R1 = 1000.0;
            
    };



    
    struct Sources {
        double V1 = 1.0;
        double I1 = 1.0;
        
    };
    

    struct Quantities {
        double V_1;
        double V_2;
        double I_V1;
        double I_R1;
        
    };

    class diode_circuit {

    public:

        Components components;

        diode_circuit(Components components) : components(components) { }

        Quantities quantities(const Sources sources)
        {
            Quantities quants;
            quants.V_1 = sources.V1;
            quants.V_2 = sources.I1*this->components.R1;
            quants.I_V1 = sources.I1;
            quants.I_R1 = sources.I1;
            
            return quants;
        }

        };

}