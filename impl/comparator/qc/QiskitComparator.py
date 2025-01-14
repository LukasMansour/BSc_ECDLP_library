from qiskit import QuantumCircuit
from qiskit.circuit.library import IntegerComparator

from api.CircuitChooser import CircuitChooser
from api.comparator.QuantumClassicalComparator import QuantumClassicalComparator


class QiskitComparator(QuantumClassicalComparator):
    """
    Constant comparison circuit in the Qiskit library.
    I could not find any reference to where this is from.
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, c: int = 0):
        super().__init__(dqa, cqa, n, a % (1 << n), c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]
        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_r,
            self.register_g,
            self.register_anc,
            name=f"$<{self.a}$"
        )

        if self.c > 0:
            circuit.append(
                IntegerComparator(num_state_qubits=self.n, value=self.a, geq=False).control(self.c),
                list(self.register_c) +
                list(self.register_x) +
                list(self.register_r) +
                list(self.register_anc[:self.n - 1])
            )
        else:
            circuit.append(
                IntegerComparator(num_state_qubits=self.n, value=self.a, geq=False),
                list(self.register_x) +
                list(self.register_r) +
                list(self.register_anc[:self.n - 1])
            )

        cache[self.identifier] = circuit

        return circuit
