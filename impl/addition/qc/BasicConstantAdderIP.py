from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumClassicalAdderIP import QuantumClassicalAdderIP


class BasicConstantAdderIP(QuantumClassicalAdderIP):
    """
    Constant addition circuit based on repeated incrementer.
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, c: int = 0):
        super().__init__(dqa, cqa, n, a % (1 << n), c)

    def get_circuit(self, *args) -> QuantumCircuit:
        if self.n == 0 or self.a == 0:
            return QuantumCircuit(self.register_c, self.register_x, self.register_g, self.register_anc,
                                  name=f"[+{self.a}]_B")

        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_g,
            self.register_anc,
            name=f"+{self.a}"
        )

        # Convert from little endian (bin(a)[2:]) to big endian
        # Then from LTR iterate over them and apply an addition at each bit.
        for index, bit in enumerate(reversed(bin(self.a)[2:])):
            if bit == '1':
                incrementer = CircuitChooser().choose_component(
                    "QCIncrementer",
                    (self.n, index, self.c),
                    self.dqa,
                    self.cqa
                )
                circuit.append(
                    incrementer.get_circuit(),
                    list(self.register_c) +
                    list(self.register_x) +
                    list(self.register_g) +
                    list(self.register_anc)
                )

        cache[self.identifier] = circuit

        return circuit
