import math

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister
from qiskit.circuit.library import QFTGate

from impl.exponentiation.qc.modular.HRSConstantModExpIP import HRSConstantModExpIP


def shors_original(g: int, p: int) -> QuantumCircuit:
    # g^k = 1 mod p, find k
    n = math.ceil(math.log2(p))
    N = 2 * n + 1
    # construct the circuit.
    register_x = QuantumRegister(N, "x")
    register_psi = QuantumRegister(n, "\\psi")
    register_anc = QuantumRegister(N + 1, "anc")
    classical_register_qft = ClassicalRegister(N, "qft_reg")

    circuit = QuantumCircuit(register_x, register_psi, register_anc, classical_register_qft)
    circuit.h(register_x)
    circuit.x(register_psi[0])

    circuit.append(
        HRSConstantModExpIP(0, len(register_anc), N, g, p, 0).get_circuit(),
        list(register_x) +
        list(register_psi) +
        list(register_anc)
    )

    circuit.append(QFTGate(N).inverse(), register_x)
    circuit.measure(register_x, classical_register_qft)

    return circuit
