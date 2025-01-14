from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumClassicalModularAdderIP import QuantumClassicalModularAdderIP


class HRSConstantModularAdderIP(QuantumClassicalModularAdderIP):
    """
    Constant modular addition circuit by Häner, Roetteler and Svore (Fig. 6, https://arxiv.org/pdf/1611.07995).
    """

    def __init__(self, dqa: int, cqa, n: int, a: int, p: int, c: int = 0):
        super().__init__(dqa, cqa, n, a, p, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_g,
            self.register_anc,
            name=f"$[+{self.a}~mod~{self.p}]_{{HRS}}$"
        )

        # Comparison of quantum states
        # No extra qubits available to borrow
        # 1 clean qubit being used.
        qc_comp = CircuitChooser().choose_component(
            "QCComparator",
            (self.n, self.p - self.a, self.c),
            dirty_available=self.dqa,
            clean_available=max(self.cqa - 1, 0)
        )

        # CMP (N - a)
        circuit.append(qc_comp.get_circuit(),
                       list(self.register_c) +
                       list(self.register_x) +
                       [self.register_anc[0]] +
                       list(self.register_g) +
                       list(self.register_anc[1:])
                       )

        # Add_a
        # 1 clean qubit being used.
        qc_adder = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n, self.a, 1),
            dirty_available=self.dqa + self.c,
            clean_available=max(self.cqa - 1, 0)
        )

        # Can borrow the control qubits.
        borrowable = list(self.register_c)

        circuit.append(qc_adder.get_circuit(),
                       [self.register_anc[0]] +
                       list(self.register_x) +
                       borrowable +
                       list(self.register_g) +
                       list(self.register_anc[1:])
                       )

        # Flip the ancilla qubit
        if self.c > 0:
            circuit.mcx(self.register_c, self.register_anc[0])
        else:
            circuit.x(self.register_anc[0])

        # Sub_{N-a}
        # Can borrow the control qubits.
        # 1 clean qubit being used.
        qc1_adder = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n, self.p - self.a, 1),
            dirty_available=self.dqa + self.c,
            clean_available=max(self.cqa - 1, 0)
        )

        # Can borrow the control qubits.
        borrowable = list(self.register_c)

        circuit.append(qc1_adder.get_circuit().reverse_ops(),
                       [self.register_anc[0]] +
                       list(self.register_x) +
                       borrowable +
                       list(self.register_g) +
                       list(self.register_anc[1:])
                       )

        # CMP (a)
        # No qubits available to borrow
        # 1 clean qubit being used.
        qc1_comp = CircuitChooser().choose_component(
            "QCComparator",
            (self.n, self.a, self.c),
            dirty_available=self.dqa,
            clean_available=max(self.cqa - 1, 0)
        )

        circuit.append(
            qc1_comp.get_circuit(),
            list(self.register_c) +
            list(self.register_x) +
            [self.register_anc[0]] +
            list(self.register_g) +
            list(self.register_anc[1:])
        )

        cache[self.identifier] = circuit

        return circuit
