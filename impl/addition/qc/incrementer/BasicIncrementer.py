from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumClassicalIncrementer import QuantumClassicalIncrementer


class BasicIncrementer(QuantumClassicalIncrementer):
    """
    Very basic and inefficient incrementer based on MCX gates.

    Requires 0 ('dirty') qubits and 0 clean qubits.
    """

    def __init__(self,
                 dqa: int,  # dirty qubits available
                 cqa: int,  # clean qubits available
                 n: int,
                 s: int = 0,
                 c: int = 0,
                 overflow_qubit: bool = False,
                 ):
        super().__init__(dqa, cqa, n, s, c, overflow_qubit=overflow_qubit)

    def get_circuit(self, *args) -> QuantumCircuit:
        if self.n == 0:
            return QuantumCircuit(0)

        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(self.register_x, self.register_o, self.register_g, self.register_anc,
                                 name=f"+{2 ** self.s}_B")
        s_register_x = list(self.register_x) + list(self.register_o)

        if self.overflow_qubit:
            self.n += 1

        for i in reversed(range(self.s + 1, self.n)):
            circuit.mcx(s_register_x[self.s:i], i)

        # Apply the final NOT gate
        circuit.x(self.s)

        if self.c > 0:
            circuit = circuit.control(self.c)

        cache[self.identifier] = circuit

        return circuit
