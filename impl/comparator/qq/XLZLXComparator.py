from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.comparator.QuantumQuantumComparator import QuantumQuantumComparator


class XLZLXComparator(QuantumQuantumComparator):
    """
    Comparator for image binarization by Xia, Li, Zhang, Liang and Xin (https://doi.org/10.1007/s11128-019-2334-2).
    """

    def __init__(self, dqa: int, cqa: int, n: int, c: int):
        super().__init__(dqa, cqa, n, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_y,
            self.register_r,
            self.register_g,
            self.register_anc,
            name=f"$<$"
        )

        # Special case for (n == 1), since it doesn't fully match the setup of the case n > 1.
        if self.n == 1:
            circuit.x(self.register_x[0])
            circuit.mcx(list(self.register_c) + [self.register_x[0], self.register_y[0]], self.register_r[0])
            circuit.x(self.register_x[0])
            return circuit

        # Apply CNOT from b_i to a_i
        for i in range(0, self.n):
            circuit.cx(self.register_y[i], self.register_x[i])

        # Apply CX from b_i to b_(i-1), except for b_1 which goes to the ancilla.
        circuit.cx(self.register_y[1], self.register_anc[0])

        for i in range(2, self.n):
            circuit.cx(self.register_y[i], self.register_y[i - 1])

        # Apply a CX from last b to result
        circuit.mcx(list(self.register_c) + [self.register_y[self.n - 1]], self.register_r[0])

        # Apply a CCX from a_0, b_0 to ancilla
        circuit.ccx(self.register_x[0], self.register_y[0], self.register_anc[0])

        # Special CCX from ancilla, a_1 to b_1
        circuit.x(self.register_x[1])
        circuit.ccx(self.register_anc[0], self.register_x[1], self.register_y[1])
        circuit.x(self.register_x[1])

        for i in range(2, self.n - 1):
            circuit.x(self.register_x[i])
            circuit.ccx(self.register_y[i - 1], self.register_x[i], self.register_y[i])
            circuit.x(self.register_x[i])

        ### MIDDLE OF CIRCUIT
        # Final special CCX from b_(n-2), a_(n-1) to result
        circuit.x(self.register_x[self.n - 1])
        circuit.mcx(list(self.register_c) + [self.register_y[self.n - 2], self.register_x[self.n - 1]],
                    self.register_r[0])
        circuit.x(self.register_x[self.n - 1])
        ### MIDDLE OF CIRCUIT

        for i in reversed(range(2, self.n - 1)):
            circuit.x(self.register_x[i])
            circuit.ccx(self.register_y[i - 1], self.register_x[i], self.register_y[i])
            circuit.x(self.register_x[i])

        # Special CCX from ancilla, a_1 to b_1
        circuit.x(self.register_x[1])
        circuit.ccx(self.register_anc[0], self.register_x[1], self.register_y[1])
        circuit.x(self.register_x[1])

        # Apply a CCX from a_0, b_0 to ancilla
        circuit.ccx(self.register_x[0], self.register_y[0], self.register_anc[0])

        for i in reversed(range(2, self.n)):
            circuit.cx(self.register_y[i], self.register_y[i - 1])

        # Apply CX from b_i to b_(i-1), except for b_1 which goes to the ancilla.
        circuit.cx(self.register_y[1], self.register_anc[0])

        # Apply CNOT from b_i to a_i
        for i in reversed(range(0, self.n)):
            circuit.cx(self.register_y[i], self.register_x[i])

        cache[self.identifier] = circuit

        return circuit
