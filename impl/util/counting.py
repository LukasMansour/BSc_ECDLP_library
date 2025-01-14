from collections import OrderedDict

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Instruction
from qiskit.transpiler.passes import SolovayKitaev


def get_ideal_gate_count(circuit: QuantumCircuit) -> OrderedDict[Instruction, int]:
    circuit = transpile(circuit, basis_gates=['cz', 'id', 'rz', 'sx', 'x'], optimization_level=3)
    return circuit.count_ops()


def get_t_gate_count(circuit: QuantumCircuit) -> OrderedDict[Instruction, int]:
    circuit = transpile(circuit, basis_gates=['u3', 'cx'], optimization_level=3)
    circuit.remove_final_measurements(inplace=True)
    # Convert that using SolovayKitaev to Clifford+T gateset: Clifford + ['t', 'tdg']
    skd = SolovayKitaev(recursion_degree=2)
    circuit = skd(circuit)

    return circuit.count_ops()


def get_ideal_gate_depth(circuit: QuantumCircuit) -> int:
    circuit = transpile(circuit, basis_gates=['cz', 'id', 'rz', 'sx', 'x'], optimization_level=3)
    return circuit.depth()


def get_t_gate_depth(circuit: QuantumCircuit) -> int:
    circuit = transpile(circuit, basis_gates=['u3', 'cx'], optimization_level=3)
    circuit.remove_final_measurements(inplace=True)
    # Convert that using SolovayKitaev to Clifford+T gateset: Clifford + ['t', 'tdg']
    skd = SolovayKitaev(recursion_degree=2)
    circuit = skd(circuit)

    return circuit.depth(lambda gate: gate[0].name in ['t', 'tdg'])
