from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumQuantumModularAdderIP import QuantumQuantumModularAdderIP


class RNSLModularAdderIP(QuantumQuantumModularAdderIP):
    """
    Modular addition circuit by Roetteler, Naehrig, Svore and Lauter (https://arxiv.org/pdf/1706.06752, Fig 3.).
    Slight improvement implemented from (https://arxiv.org/pdf/2001.09580, Fig 3.).
    """

    # TODO: Make a variant of this based on a quantum classical comparator?

    def __init__(self, dqa: int, cqa: int, n: int, p: int, c: int = 0):
        super().__init__(dqa, cqa, n, p, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_y,
            self.register_g,
            self.register_anc,
            name=f"$[+~mod~{self.p}]_{{RNSL}}$"
        )

        # Addition of two quantum states
        # No extra qubits available to borrow
        # 1 clean qubit used
        qq_adder = CircuitChooser().choose_component(
            "QQAdderIP",
            (self.n, self.c, False, True),
            dirty_available=self.dqa,
            clean_available=self.cqa - 1
        )
        circuit.append(
            qq_adder.get_circuit(),
            list(self.register_c) +
            list(self.register_x) +
            list(self.register_y) +
            [self.register_anc[0]] +
            list(self.register_g) +
            list(self.register_anc[1:])
        )
        # Now we have |x>|x + y>
        # Subtraction of p
        # n (from reg_x) + control qubits available to borrow
        qc_adder_1 = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n + 1, self.p, 0),
            dirty_available=self.dqa + self.n + self.c,
            clean_available=self.cqa - 1
        )

        borrowable = list(self.register_x) + list(self.register_c)

        circuit.append(
            qc_adder_1.get_circuit().reverse_ops(),
            list(self.register_y) +
            [self.register_anc[0]] +
            borrowable +
            list(self.register_g) +
            list(self.register_anc[1:])
        )
        # Now we have |x>|x + y - p>
        # Addition of p conditioned on ancilla
        # n (from_reg_x) + control qubits available to borrow
        qc_adder_2 = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n, self.p, 1),
            dirty_available=self.dqa + self.n + self.c,
            clean_available=self.cqa - 1

        )

        circuit.append(
            qc_adder_2.get_circuit(),
            [self.register_anc[0]] +
            list(self.register_y) +
            borrowable +
            list(self.register_g) +
            list(self.register_anc[1:])
        )

        # Quantum Quantum comparator
        # No qubits available to borrow
        qq_comp = CircuitChooser().choose_component(
            "QQComparator",
            (self.n, self.c),
            dirty_available=self.dqa,
            clean_available=self.cqa - 1
        )

        circuit.append(
            qq_comp.get_circuit(),
            list(self.register_c) +
            list(self.register_y) +
            list(self.register_x) +
            [self.register_anc[0]] +
            list(self.register_g) +
            list(self.register_anc[1:])
        )

        circuit.x(self.register_anc[0])

        cache[self.identifier] = circuit

        return circuit
