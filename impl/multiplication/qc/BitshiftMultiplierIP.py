from qiskit import QuantumCircuit

from api.multiplication.QuantumClassicalMultiplierIP import QuantumClassicalMultiplierIP


# TODO: Bit-shifts as a component in CircuitChooser
# TODO: Implement more efficient bit-shifting, e.g. cyclic.
class RightwardBitshiftMultiplierIP(QuantumClassicalMultiplierIP):
    """
    Constant multiplication circuit based on rightward bit-shifting.

    first_zero can be an improvement to the circuit, if register_x[0] is guaranteed to be |0> (from: https://arxiv.org/pdf/2305.11410)
    """

    def __init__(self, n: int, c: int = 0, first_zero: bool = False):
        super().__init__(n, 2, c)
        self.first_zero = first_zero

    def get_circuit(self, *args) -> QuantumCircuit:
        circuit = QuantumCircuit(self.register_x, name="x >> 1")

        for i in range(0, self.n - 1):
            if self.first_zero:
                circuit.cx(i + 1, i)
                circuit.cx(i, i + 1)
            else:
                circuit.swap(i, i + 1)

        if self.c > 0:
            circuit = circuit.control(self.c)

        return circuit


class LeftwardBitshiftMultiplierIP(QuantumClassicalMultiplierIP):
    """
    Constant multiplication circuit based on left-ward bit-shifting.

    first_zero can be an improvement to the circuit, if register_x[-1] is guaranteed to be |0> (from: https://arxiv.org/pdf/2305.11410)
    """

    def __init__(self, n: int, c: int = 0, last_zero: bool = False):
        super().__init__(n, 2, c)
        self.last_zero = last_zero

    def get_circuit(self, *args) -> QuantumCircuit:
        circuit = QuantumCircuit(self.register_x, name="x << 1")

        for i in range(0, self.n - 1):
            if self.last_zero:
                circuit.cx(self.n - 2 - i, self.n - 1 - i)
                circuit.cx(self.n - 1 - i, self.n - 2 - i)
            else:
                circuit.swap(self.n - 1 - i, self.n - 2 - i)

        if self.c > 0:
            circuit = circuit.control(self.c)

        return circuit
