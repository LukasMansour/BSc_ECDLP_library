import math

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister

from api.CircuitChooser import CircuitChooser
from impl.util.semiclassical_qft import apply_semiclassical_qft_phase_component


def shors_semiclassical(g: int, p: int) -> QuantumCircuit:
    # g^k = 1 mod p, find k
    n = math.ceil(math.log2(p))
    N = 2 * n
    # construct the circuit.
    register_x = QuantumRegister(1, "x")
    register_psi = QuantumRegister(n, "\\psi")
    register_ancilla = QuantumRegister(n + 1, "anc")
    classical_register_qft = ClassicalRegister(N, "cl")

    circuit = QuantumCircuit(register_x, register_psi, register_ancilla, classical_register_qft)
    circuit.x(register_psi[0])

    for i in range(0, N):  # [0, N-1]
        circuit.h(register_x[0])

        multiplier = CircuitChooser().choose_component(
            "QCModMulIP",
            (n, g ** (2 ** (N - 1 - i)) % p, p, 1),
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
        # skip last
        if i < N - 1:
            with circuit.if_test((classical_register_qft[i], 1)):
                circuit.x(register_x[0])

    return circuit
