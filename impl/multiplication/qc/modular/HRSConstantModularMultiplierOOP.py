from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.multiplication.modular.QuantumClassicalModularMultiplierOOP import QuantumClassicalModularMultiplierOOP


class HRSConstantModularMultiplierOOP(QuantumClassicalModularMultiplierOOP):
    """
    Modular multiplication circuit out of place by Häner, Roetteler and Svore (https://arxiv.org/pdf/1611.07995).
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, p: int, c: int):
        super().__init__(dqa, cqa, n, a, p, c)

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
            name=f"$\\cdot {self.a} ~mod~{self.p}$"
        )

        for i in range(0, self.n):
            # Each adder has n - 1 qubits available to borrow (from register_x)
            adder = CircuitChooser().choose_component(
                "QCModAdderIP",
                (self.n, (self.a * (2 ** i)) % self.p, self.p, self.c + 1),
                dirty_available=self.dqa + self.n - 1,
                clean_available=self.cqa
            )

            borrowable = list(self.register_x)
            borrowable.remove(self.register_x[i])

            circuit.append(adder.get_circuit(),
                           list(self.register_c) +
                           [self.register_x[i]] +
                           list(self.register_r) +
                           borrowable +
                           list(self.register_g) +
                           list(self.register_anc)
                           )

        cache[self.identifier] = circuit

        return circuit
