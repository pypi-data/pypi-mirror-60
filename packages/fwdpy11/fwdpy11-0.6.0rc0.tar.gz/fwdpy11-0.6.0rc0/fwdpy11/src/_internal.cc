#include <pybind11/pybind11.h>

namespace py = pybind11;

void init_DiploidPopulationGeneticValueVector(py::module&);

PYBIND11_MODULE(_internal, m)
{
    init_DiploidPopulationGeneticValueVector(m);
}
