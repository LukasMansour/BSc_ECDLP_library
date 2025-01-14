import math

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator

from api.CircuitChooser import CircuitChooser
from impl.util.semiclassical_qft import apply_semiclassical_qft_phase_component


def shors_dlp(g: int, b: int, p: int, extra_qubits = 0) -> QuantumCircuit:
    # g^k = b mod p, find k
    n = math.ceil(math.log2(p))
    N = 2 * n
    # deal with extra qubits clause
    # Check if number of extra qubits is higher than our limit of simulatable qubits
    num_required =  1 + n + n + 1
    if num_required + extra_qubits > AerSimulator().num_qubits:
        extra_qubits = max(AerSimulator().num_qubits - num_required, 0)
    if num_required + extra_qubits > AerSimulator().num_qubits:
        raise ValueError('Too many qubits for problem instance required.')
    # construct the circuit.
    register_x = QuantumRegister(1, "x")
    register_psi = QuantumRegister(n, "\\psi")
    register_ancilla = QuantumRegister(n + 1 + extra_qubits, "anc")
    classical_register_qft = ClassicalRegister(n, "cl_qft")
    classical_register_qft_2 = ClassicalRegister(n, "cl_qft_2")

    circuit = QuantumCircuit(register_x, register_psi, register_ancilla,
                             classical_register_qft, classical_register_qft_2)
    circuit.x(register_psi[0])

    for i in range(0, n):
        circuit.h(register_x[0])
        multiplier = CircuitChooser().choose_component(
            "QCModMulIP",
            (n, g ** (2 ** (N - i - 1)) % p, p, 1),
            dirty_available=0,
            clean_available=len(register_ancilla)
        )

        circuit.append(
            multiplier.get_circuit(),
            [register_x[0]] +
            list(register_psi) +
            list(register_ancilla)
        )

        apply_semiclassical_qft_phase_component(
            circuit,
            [register_x[0]],
            classical_register_qft,
            N,
            i
        )

        circuit.h(register_x[0])

        # measure it in corresponding classical reg
        circuit.measure(register_x[0], classical_register_qft[i])
        with circuit.if_test((classical_register_qft[i], 1)):
            circuit.x(register_x[0])

    for i in range(0, n):

        circuit.h(register_x[0])
        multiplier = CircuitChooser().choose_component(
            "QCModMulIP",
            (n, b ** (2 ** (N - i - 1)) % p, p, 1),
            dirty_available=0,
            clean_available=len(register_ancilla)
        )

        circuit.append(
            multiplier.get_circuit(),
            [register_x[0]] +
            list(register_psi) +
            list(register_ancilla)
        )

        apply_semiclassical_qft_phase_component(
            circuit,
            [register_x[0]],
            list(classical_register_qft) + list(classical_register_qft_2),
            N,
            n + i
        )

        circuit.h(register_x[0])

        # measure it in corresponding classical reg
        circuit.measure(register_x[0], classical_register_qft_2[i])
        # skip last
        if i < n - 1:
            with circuit.if_test((classical_register_qft_2[i], 1)):
                circuit.x(register_x[0])

    return circuit
