import math

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

from api.CircuitChooser import CircuitChooser
from impl.util.semiclassical_qft import apply_semiclassical_qft_phase_component


def shors_ecdlp(points: [], p: int, with_modular_inversion=True, extra_qubits = 0) -> QuantumCircuit:
    # g^k = b mod p, find k
    n = math.ceil(math.log2(p))
    # deal with extra qubits clause
    # Check if number of extra qubits is higher than our limit of simulatable qubits
    num_required =  1 + 2*n + 2*n + 2
    if num_required + extra_qubits > AerSimulator().num_qubits:
        extra_qubits = max(AerSimulator().num_qubits - num_required, 0)
    if num_required + extra_qubits > AerSimulator().num_qubits:
        raise ValueError('Too many qubits for problem instance required.')
    # construct the circuit.
    register_x = QuantumRegister(1, "x")
    register_psi = QuantumRegister(2 * n, "\\psi")
    register_ancilla = QuantumRegister(2 * n + 2 + extra_qubits, "anc")
    classical_register_qft = ClassicalRegister(2 * n + 2, "cl_qft")

    circuit = QuantumCircuit(register_x, register_psi, register_ancilla, classical_register_qft)

    for k in range(0, 2 * n + 2):
        # Apply entering Hadamard
        circuit.h(register_x[0])
        ec_point_addition = CircuitChooser().choose_component(
            "QCECPointAdderIP",
            (n, points[k], p, 1, with_modular_inversion),
            dirty_available=0,
            clean_available=len(register_ancilla)
        )

        circuit.append(
            ec_point_addition.get_circuit(),
            [register_x[0]] +
            list(register_psi) +
            list(register_ancilla)
        )

        apply_semiclassical_qft_phase_component(
            circuit,
            [register_x[0]],
            classical_register_qft,
            2 * n + 2,
            k
        )
        # Apply exiting hadamard
        circuit.h(register_x[0])

        # measure it in corresponding classical reg
        circuit.measure(register_x[0], classical_register_qft[k])

        if k < 2 * n + 1:  # Skip last reset
            with circuit.if_test((classical_register_qft[k], 1)):
                circuit.x(register_x[0])

    return circuit
