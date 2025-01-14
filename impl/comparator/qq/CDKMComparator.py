from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.comparator.QuantumQuantumComparator import QuantumQuantumComparator
from impl.addition.qq.CDKMAdderIP import maj_circuit


class CDKMComparator(QuantumQuantumComparator):
    """
    High-bit comparator based on the addition circuit by Cuccaro, Draper, Kutin and Moulton (https://arxiv.org/abs/quant-ph/0410184).
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

        circuit.x(self.register_x)

        # Apply first MAJ gate to (c_0, b_0, a_0)
        circuit.append(
            maj_circuit(),
            [self.register_anc[0], self.register_y[0], self.register_x[0]]
        )
        for i in range(1, self.n):  # [1, n-1]
            circuit.append(
                maj_circuit(),
                [self.register_x[i - 1], self.register_y[i], self.register_x[i]]
            )

        # Extract the output
        circuit.mcx(list(self.register_c) + [self.register_x[self.n - 1]], self.register_r[0])

        # Now apply the UMA gates
        for i in range(self.n - 1, 0, -1):  # [n-1, 1]
            circuit.append(
                maj_circuit().reverse_ops(),
                [self.register_x[i - 1], self.register_y[i], self.register_x[i]]
            )

        # Apply last UMA gate
        circuit.append(
            maj_circuit().reverse_ops(),
            [self.register_anc[0], self.register_y[0], self.register_x[0]]
        )

        circuit.x(self.register_x)

        cache[self.identifier] = circuit

        return circuit
