from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.comparator.QuantumClassicalComparator import QuantumClassicalComparator
from impl.addition.qc.HRSConstantAdderIP import carry_gate
from impl.util.ancilla_registers import setup_anc_registers


class HRSComparator(QuantumClassicalComparator):
    """
    Constant comparison circuit by Häner, Roetteler and Svore (https://arxiv.org/pdf/1611.07995)
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, c: int = 0):
        super().__init__(dqa, cqa, n, a % (1 << n), c)

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
            name=f"$<{self.a}$"
        )

        # We need n-1 borrowed qubits
        register_g, _, _, _ = setup_anc_registers(
            self.n - 1,
            0,
            self.register_g,
            self.register_anc
        )

        a_inverted = 0 - self.a

        circuit.append(carry_gate(self.n, a_inverted, self.c),
                       list(self.register_c) + list(self.register_x) + list(self.register_r) + register_g)

        # Handle negative / overflowing numbers correctly
        if (a_inverted & (1 << self.n)) >> self.n == 1:
            if self.c > 0:
                circuit.mcx(self.register_c, self.register_r[0])
            else:
                circuit.x(self.register_r[0])

        cache[self.identifier] = circuit

        return circuit
