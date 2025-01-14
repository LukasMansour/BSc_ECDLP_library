from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumClassicalModularNegatorIP import QuantumClassicalModularNegationIP
from impl.encoding.binary_encoding import binary_encoding


class RNSLModularNegationIP(QuantumClassicalModularNegationIP):
    """
    Modular negation circuit by Roetteler, Naehrig, Svore and Lauter (https://arxiv.org/pdf/1706.06752).
    It is not documented in the paper, but can be found in their codebase.
    Takes advantage of (x-y) = (2C(x) + y), where 2C is the two's complement.
    """

    def __init__(self, dqa: int, cqa: int, n: int, p: int, c: int):
        super().__init__(dqa, cqa, n, p, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        neg_p = (1 << self.n) - self.p - 1

        circuit = QuantumCircuit(
            self.register_x,
            self.register_g,
            self.register_anc,
            name=f"$-[0]~mod~{self.p}$"
        )

        # Check if input is 0
        circuit.x(self.register_x)
        circuit.mcx(list(self.register_x), self.register_anc[0])
        circuit.x(self.register_x)
        # If it was all zeros, then we want to return the modulus, so we get p' + p and then invert
        circuit.append(binary_encoding(self.n, self.p, c=1),
                       [self.register_anc[0]] + list(self.register_x))

        # Subtraction of p
        qc_adder = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n, neg_p, 0),
            dirty_available=self.dqa,
            clean_available=self.cqa - 1
        )

        # Add m' to x
        circuit.append(
            qc_adder.get_circuit(),
            list(self.register_x) +
            list(self.register_g) +
            list(self.register_anc[1:])
        )
        # Now if all 1s, reset the ancilla
        circuit.mcx(list(self.register_x), self.register_anc[0])
        # Finally move back into correct representation
        circuit.x(self.register_x)

        # TODO: Improve controlling
        if self.c > 0:
            circuit = circuit.decompose(reps=2).control(self.c)

        cache[self.identifier] = circuit

        return circuit
