#include <vector>
#include <gsl/gsl_vector.h>
#include <gsl/gsl_multiroots.h>
#include <iostream>

typedef std::vector< double > state_type;

/*
Generated by Cirode: https://github.com/NineNein/Cirode

Description of Circuit:
{{circuit_desc}}
*/

#define {{circuit_name.upper()}}_VECTOR_SIZE {{vector_size}}

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

    {% if Ctrl_Sources is defined and Ctrl_Sources[0] is defined %}
    struct Ctrl_Sources {
        {% for name, std_value, expr in Ctrl_Sources -%}
            double {{name}} = {{std_value}};
        {% endfor %}
    };
    {% endif %}

    struct Quantities {
        {% for name in Quantities -%}
            double {{name}};
        {% endfor %}
    };

    class {{circuit_name}};
    struct r_params{

        {{circuit_name}}* obj;

        {% if exprs is defined and exprs[0] is defined -%}
        state_type x;
        {% endif -%}
        {% if Sources is defined and Sources[0] is defined -%}
        Sources sources;
        {% endif -%}
    };


    int root_finding(const gsl_vector * xs, void *params, gsl_vector * f);


    class {{circuit_name}} {


    public:

        Quantities _quantities(
            {% set comma = joiner(",") %}
            {% if exprs is defined and exprs[0] is defined -%} {{comma()}}
            const state_type &x
            {% endif -%}
            {% if Sources is defined and Sources[0] is defined -%} {{comma()}}
            const Sources sources
            {% endif -%}
            {% if Ctrl_Sources is defined and Ctrl_Sources[0] is defined -%} {{comma()}}
            const Ctrl_Sources ctrl_sources
            {% endif -%}
        ){
            Quantities quants;
            {% for expr in quant_expr -%}
                {{expr}};
            {% endfor %}
            return quants;
        }


        Ctrl_Sources get_ctrl_sources(
            {% set comma = joiner(",") %}
            {% if exprs is defined and exprs[0] is defined -%} {{comma()}}
            const state_type &x
            {% endif -%}
            {% if Sources is defined and Sources[0] is defined -%} {{comma()}}
            const Sources sources
            {% endif -%}
        ){
            const gsl_multiroot_fsolver_type *T;
            gsl_multiroot_fsolver *s;

            int status;
            size_t i, iter = 0;
            const size_t n = {{Ctrl_Sources|length}};

            struct r_params p{
                this,
                {% set comma = joiner(",") %}
                {% if exprs is defined and exprs[0] is defined -%} {{comma()}}
                x
                {% endif -%}
                {% if Sources is defined and Sources[0] is defined -%} {{comma()}}
                sources
                {% endif -%}
            };

            gsl_multiroot_function f = {&root_finding, n, &p};


            gsl_vector *xs = gsl_vector_alloc (n);

            {% for name, std_value, expr in Ctrl_Sources -%}
            gsl_vector_set (xs, {{loop.index-1}}, this->start_values[{{loop.index-1}}]);
            {% endfor %}
            

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
                {% for name, std_value, expr in Ctrl_Sources -%}
                gsl_vector_get (s->x, {{loop.index-1}}) {{ ", " if not loop.last else "" }}
                {% endfor %}
            };

            {% for name, std_value, expr in Ctrl_Sources -%}
            //this->start_values[{{loop.index-1}}] =  gsl_vector_get (s->x, {{loop.index-1}});
            {% endfor %}

            

            gsl_multiroot_fsolver_free (s);
            gsl_vector_free (xs);

            return ctrl_sources;

        }


        Components components;
        double start_values[{{vector_size}}];
        {{circuit_name}}(Components components) : components(components) { 

            {% for name, std_value, expr in Ctrl_Sources -%}
            this->start_values[{{loop.index-1}}] = {{std_value}};
            {% endfor -%}
            

        }

        Quantities quantities(
            {% set comma = joiner(",") %}
            {% if exprs is defined and exprs[0] is defined -%} {{comma()}}
            const state_type &x
            {% endif -%}
            {% if Sources is defined and Sources[0] is defined -%} {{comma()}}
            const Sources sources
            {% endif -%}
        ){
            Quantities quants;
            Ctrl_Sources ctrl_sources = this->get_ctrl_sources(
                {% set comma = joiner(",") %}
                {% if exprs is defined and exprs[0] is defined -%} {{comma()}}
                x
                {% endif -%}
                {% if Sources is defined and Sources[0] is defined -%} {{comma()}}
                sources
                {% endif -%}
            );

            {% for expr in quant_expr -%}
                {{expr}};
            {% endfor %}
            return quants;
        }

        {% if exprs is defined and exprs[0] is defined -%}
        {% if Sources is defined and Sources[0] is defined -%}
        void operator() ( const state_type &x , state_type &dxdt , const double t , const Sources sources )
        {% else -%}
        void operator() ( const state_type &x , state_type &dxdt , const double t)
        {% endif -%}
        {

            Ctrl_Sources ctrl_sources = this->get_ctrl_sources(
                {% if exprs is defined and exprs[0] is defined -%}
                x
                {% endif -%}
                {% if Sources is defined and Sources[0] is defined -%}
                ,sources
                {% endif -%}
            );

            {% for expr in exprs -%}
                {{expr}};
            {% endfor %}
        }
        {% endif -%}
    };





    int root_finding(const gsl_vector * xs, void *params, gsl_vector * f){

        struct Ctrl_Sources ctrl_sources{
            {% for name, std_value, expr in Ctrl_Sources -%}
            gsl_vector_get (xs, {{loop.index-1}}) {{ ", " if not loop.last else "" }}
            {% endfor %}
        };


        {{circuit_name}}* obj = ((struct r_params *) params)->obj;

        {% if exprs is defined and exprs[0] is defined -%}
        state_type x = ((struct r_params *) params)->x;
        {% endif -%}
        
        {% if Sources is defined and Sources[0] is defined -%}
        Sources sources = ((struct r_params *) params)->sources;
        {% endif -%}

        Quantities quants = obj->_quantities(
            {% set comma = joiner(",") %}
            {%- if exprs is defined and exprs[0] is defined %}{{comma()}} x
            {%- endif %}
            {% if Sources is defined and Sources[0] is defined -%} {{ comma() }}
            sources
            {% endif -%}
            {% if Ctrl_Sources is defined and Ctrl_Sources[0] is defined -%} {{ comma() }}
            ctrl_sources
            {% endif -%}
            );


        {% for name, std_value, expr in Ctrl_Sources -%}
        double I_{{loop.index-1}}     = gsl_vector_get(xs, {{loop.index-1}});
        double Icalc_{{loop.index-1}} = {{expr}};
        gsl_vector_set (f, {{loop.index-1}}, I_{{loop.index-1}}-Icalc_{{loop.index-1}});
        {% endfor %}

        return GSL_SUCCESS;
    }

}