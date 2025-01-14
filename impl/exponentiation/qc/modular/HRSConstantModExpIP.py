from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.exponentation.modular.QuantumClassicalModularExponentiationIP import QuantumClassicalModularExponentiationIP


class HRSConstantModExpIP(QuantumClassicalModularExponentiationIP):
    """
    Modular exponentiation circuit in place by Häner, Roetteler and Svore (https://arxiv.org/pdf/1611.07995).
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, p: int, c: int):
        super().__init__(dqa, cqa, n, a, p, c)

    def get_circuit(self) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_y,
            self.register_g,
            self.register_anc,
            name=f"${self.a}^x~mod~{self.p}$"
        )
        for i in range(0, self.n):
            # Each multiplier has n - 1 qubits available to borrow (from register_x)
            multiplier = CircuitChooser().choose_component(
                "QCModMulIP",
                (self.mod_bit_len, self.a ** (2 ** i) % self.p, self.p, 1),
                dirty_available=self.dqa + self.n - 1,
                clean_available=self.cqa
            )

            borrowable = [x for x in self.register_x]
            borrowable.remove(self.register_x[i])

            circuit.append(
                multiplier.get_circuit(),
                [self.register_x[i]] +
                list(self.register_y) +
                list(self.register_g) +
                borrowable +
                list(self.register_anc)
            )

        cache[self.identifier] = circuit

        return circuit
