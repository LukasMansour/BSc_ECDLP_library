from typing import Hashable

from qiskit import QuantumCircuit

from api.CircuitComponent import CircuitComponent
from resource_estimation.automatic_optimisation import auto_opt  # , auto_opt_solovay_kitaev, remove_cl_operations


def default_metric(component: CircuitComponent) -> float:
    return 0


def gate_count_metric(component: CircuitComponent) -> float:
    return gate_count_metric_circuit(component.get_circuit(), component.get_global_identifier())


gate_count_cache = {}


def gate_count_metric_circuit(circuit: QuantumCircuit, identifier: Hashable = None) -> float:
    if identifier is None or gate_count_cache.get(identifier, None) is None:
        result = sum(dict(auto_opt(circuit).count_ops()).values())
        if identifier is not None:
            gate_count_cache[identifier] = result
            return result
        else:
            return result
    else:
        return gate_count_cache[identifier]


def gate_depth_metric(component: CircuitComponent) -> float:
    return gate_depth_metric_circuit(component.get_circuit(), component.get_global_identifier())


gate_depth_cache = {}


def gate_depth_metric_circuit(circuit: QuantumCircuit, identifier: Hashable = None) -> float:
    if identifier is None or gate_depth_cache.get(identifier, None) is None:
        result = auto_opt(circuit).depth()
        if identifier is not None:
            gate_depth_cache[identifier] = result
            return result
        else:
            return result
    else:
        return gate_depth_cache[identifier]


def cz_count_metric(component: CircuitComponent) -> float:
    return cz_count_metric_circuit(component.get_circuit(), component.get_global_identifier())


cz_count_cache = {}


def cz_count_metric_circuit(circuit: QuantumCircuit, identifier: Hashable = None) -> float:
    if identifier is None or cz_count_cache.get(identifier, None) is None:
        result = dict(auto_opt(circuit).count_ops()).get('cz', 0)
        if identifier is not None:
            cz_count_cache[identifier] = result
            return result
        else:
            return result
    else:
        return cz_count_cache[identifier]


def cz_depth_metric(component: CircuitComponent) -> float:
    return cz_depth_metric_circuit(component.get_circuit(), component.get_global_identifier())


cz_depth_cache = {}


def cz_depth_metric_circuit(circuit: QuantumCircuit, identifier: Hashable = None) -> float:
    if identifier is None or cz_depth_cache.get(identifier, None) is None:
        result = auto_opt(circuit).depth(lambda gate: gate[0].name in ['cz'])
        if identifier is not None:
            cz_depth_cache[identifier] = result
            return result
        else:
            return result
    else:
        return cz_depth_cache[identifier]

# def t_count_metric(component: CircuitComponent) -> float:
#     return t_count_metric_circuit(component.get_circuit())
#
# def t_count_metric_circuit(circuit : QuantumCircuit) -> float:
#     gate_counts = auto_opt_solovay_kitaev(circuit).count_ops()
#     return dict(gate_counts).get('t', 0) + dict(gate_counts).get('tdg', 0)
#
# def t_depth_metric(component: CircuitComponent) -> float:
#     return t_depth_metric_circuit(component.get_circuit())
#
# def t_depth_metric_circuit(circuit : QuantumCircuit) -> float:
#     circuit = auto_opt_solovay_kitaev(circuit)
#     return circuit.depth(lambda gate: gate[0].name in ['t', 'tdg'])
