from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumQuantumAdderIP import QuantumQuantumAdderIP


class TTKAdderIP(QuantumQuantumAdderIP):
    """
    Addition circuit by Takahashi, Tani and Kunihiro (https://arxiv.org/abs/0910.2530).
    """

    def __init__(self, dqa: int, cqa: int, n: int, c: int = 0, incoming_carry_qubit=False, overflow_qubit: bool = True):
        if incoming_carry_qubit:
            # TODO: Add support for incoming carry.
            raise ValueError("TTKAdder does not support incoming carry.")
        super().__init__(dqa, cqa, n, c, incoming_carry_qubit=False, overflow_qubit=overflow_qubit)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_x,
            self.register_y,
            self.register_o,
            self.register_g,
            self.register_anc,
            name="$+_{TTK}$"
        )

        if self.overflow_qubit:
            s_register_x = (list(self.register_x) + [self.register_o[0]])
        else:
            s_register_x = self.register_x

        # Step 1: Apply a CNOT gate to B_i and A_i, with A_i as the control.
        for i in range(1, self.n):  # [1, n-1]
            circuit.cx(s_register_x[i], self.register_y[i])

        # Step 2: Apply a CNOT get from A_i to A_{i+1}, with control on A_i.
        if self.overflow_qubit:
            for i in range(self.n - 1, 0, -1):  # [n - 1, 1]
                circuit.cx(s_register_x[i], s_register_x[i + 1])
        else:
            # Skip over where z would have been.
            for i in range(self.n - 2, 0, -1):  # [n - 2, 1]
                circuit.cx(s_register_x[i], s_register_x[i + 1])

        # Step 3: Apply a Toffoli to B_i, A_i and A_{i+1}, with control on A_i and B_i.
        if self.overflow_qubit:
            for i in range(0, self.n):  # [0, n-1]
                circuit.ccx(s_register_x[i], self.register_y[i], s_register_x[i + 1])
        else:
            # Skip over where z would have been.
            for i in range(0, self.n - 1):  # [0, n-2]
                circuit.ccx(s_register_x[i], self.register_y[i], s_register_x[i + 1])

        # Step 4: Apply a CNOT get from A_i to B_{i}, with control on A_i AND
        # Apply a Toffoli gate from B_{i-1}, A_{i-1} to A_i with B_{i-1} and A_{i-1} as control.
        for i in range(self.n - 1, 0, -1):  # [n - 1, 1]
            circuit.cx(s_register_x[i], self.register_y[i])
            circuit.ccx(s_register_x[i - 1], self.register_y[i - 1], s_register_x[i])

        # Step 5: Apply a CNOT from A_i to A_{i+1} where A_i is the control.
        for i in range(1, self.n - 1):  # [1, n - 2]
            circuit.cx(s_register_x[i], s_register_x[i + 1])

        # Step 6: Apply a CNOT from Bi to A_i where A_i is the control.
        for i in range(0, self.n):  # [0, n-1]
            circuit.cx(s_register_x[i], self.register_y[i])

        # TODO: Improve TTK controlled circuit
        # AFAIK this should be doable as some rounds are inverses of each other and do not need to be controlled.
        if self.c > 0:
            circuit = circuit.control(self.c)

        cache[self.identifier] = circuit

        return circuit
