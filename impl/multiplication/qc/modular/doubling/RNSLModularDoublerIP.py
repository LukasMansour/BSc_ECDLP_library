from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.multiplication.modular.QuantumClassicalModularDoublerIP import QuantumClassicalModularDoublerIP
from impl.multiplication.qc.BitshiftMultiplierIP import LeftwardBitshiftMultiplierIP


class RNSLModularDoublerIP(QuantumClassicalModularDoublerIP):
    """
    Modular addition circuit by Roetteler, Naehrig, Svore and Lauter (https://arxiv.org/pdf/1706.06752, Fig 4.).

    Slight improvement implemented from (https://arxiv.org/pdf/2001.09580, Fig 3.). (Adaptation to modular doubling).
    """

    def __init__(self, dqa: int, cqa: int, n: int, p: int, c: int):
        super().__init__(dqa, cqa, n, p, c)
        if not p % 2 == 1:
            raise ValueError("p must be an odd number!")

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_g,
            self.register_anc,
            name=f"$\\cdot2 ~mod~{self.p}$"
        )

        # Apply the bit shift *2 (|x>|0>)
        circuit.append(
            LeftwardBitshiftMultiplierIP(self.n + 1, self.c, True).get_circuit(),
            list(self.register_c) +
            list(self.register_x) +
            [self.register_anc[0]]
        )
        # -p
        qc_adder_1 = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n + 1, self.p, 0),
            dirty_available=self.dqa,
            clean_available=self.cqa - 1
        )

        circuit.append(
            qc_adder_1.get_circuit().reverse_ops(),
            list(self.register_x) +
            [self.register_anc[0]] +
            list(self.register_g) +
            list(self.register_anc[1:])
        )
        # Conditional +p.
        qc_adder_2 = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n, self.p, 1),
            dirty_available=self.dqa,
            clean_available=self.cqa - 1
        )

        circuit.append(
            qc_adder_2.get_circuit(),
            [self.register_anc[0]] +
            list(self.register_x) +
            list(self.register_g) +
            list(self.register_anc[1:])
        )

        circuit.x(self.register_x[0])
        circuit.cx(self.register_x[0], self.register_anc[0])
        circuit.x(self.register_x[0])

        if self.c > 0:
            circuit.x(self.register_c)
            circuit.mcx(list(self.register_c) + [self.register_x[0]], self.register_anc[0])
            circuit.x(self.register_c)

        cache[self.identifier] = circuit

        return circuit
