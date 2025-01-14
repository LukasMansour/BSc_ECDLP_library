import numpy as np
from qiskit import QuantumCircuit


def apply_semiclassical_qft_phase_component(circuit: QuantumCircuit, register_x, register_qft, N: int, k: int):
    """
    Computes the phase shifts R_K from https://arxiv.org/pdf/1611.07995, Fig 1.
    (also used for the phase shifts in all semiclassical QFTs)

    :param circuit: QuantumCircuit, we have to pass it like this since Qiskit has some bugs for appending hybrid circuits.
    :param N: Number of measurements
    :param k: the parameter for the phase shift gate.
    :return:
    """

    for i in range(0, k):
        # The register this qubit was measured in
        with circuit.if_test((register_qft[i], 1)):
            circuit.p(-np.pi * (1 << (k - i)), register_x[0])
