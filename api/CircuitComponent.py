from typing import Hashable

from qiskit import QuantumCircuit


class CircuitComponent:
    """
    Represents a circuit component.
    """

    def __init__(self, identifier: Hashable):
        self.identifier = identifier
        pass

    def get_circuit(self, *args) -> QuantumCircuit:
        """
        Abstract method to define the circuit to be added.
        :return: QuantumCircuit
        """
        raise NotImplementedError()

    def get_global_identifier(self) -> Hashable:
        """
        Abstract method to define the global identifier.
        Recommended to use a tuple of values to uniquely identify the circuit.
        e.g. (circuit_class, n, params)
        :return: Global identifier in the form of something hashable.
        """
        return self.identifier
