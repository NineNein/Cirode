#include <vector>

typedef std::vector< double > state_type;

/*
Description of Circuit:
{{circuit_desc}}
*/

namespace {{circuit_name}}
{

    struct Components{
        {% for name, std_value in Components -%}
            double {{name}} = {{std_value}};
        {% endfor %}    
    };



    {% if Sources is defined and Sources[0] is defined %}
    struct Sources {
        {% for name, std_value in Sources -%}
            double {{name}} = {{std_value}};
        {% endfor %}
    };
    {% endif %}

    struct Quantities {
        {% for name in Quantities -%}
            double {{name}};
        {% endfor %}
    };

    class {{circuit_name}} {

        Components components;

    public:
        {{circuit_name}}(Components components) : components(components) { }

        {% if Sources is defined and Sources[0] is defined -%}
        Quantities quantities(const state_type &x, const Sources sources)
        {% else -%}
        Quantities quantities(const state_type &x)
        {% endif -%}
        {
            Quantities quants;
            {% for expr in quant_expr -%}
                {{expr}};
            {% endfor %}
            return quants;
        }

        {% if Sources is defined and Sources[0] is defined -%}
        void operator() ( const state_type &x , state_type &dxdt , const double /* t */, const Sources sources )
        {% else -%}
        void operator() ( const state_type &x , state_type &dxdt , const double /* t */)
        {% endif -%}
        {
            {% for expr in exprs -%}
                {{expr}};
            {% endfor %}
        }
    };

}