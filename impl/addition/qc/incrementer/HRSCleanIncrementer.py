from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumClassicalIncrementer import QuantumClassicalIncrementer
from impl.addition.qq.TTKAdderIP import TTKAdderIP
from impl.util.ancilla_registers import setup_anc_registers


class HRSCleanIncrementer(QuantumClassicalIncrementer):
    """
    Serial incrementer crated by Häner, Roetteler and Svore (https://arxiv.org/pdf/1611.07995)
    By assuming clean ancillas, we can save a subtraction.

    Requires 0 borrowable ('dirty') qubits.
    Requires n - s clean qubits.
    """

    def __init__(self,
                 dqa: int,  # dirty qubits available
                 cqa: int,  # clean qubits available
                 n: int,
                 s: int = 0,
                 c: int = 0,
                 overflow_qubit: bool = False
                 ):
        super().__init__(dqa, cqa, n, s, c, overflow_qubit=overflow_qubit)

    def get_circuit(self, *args) -> QuantumCircuit:
        if self.n == 0:
            return QuantumCircuit(0)

        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_o,
            self.register_g,
            self.register_anc,
            name=f"+{2 ** self.s}_{{HC}}"
        )

        # Just plug in an incrementer and shift everything up by s.
        if self.s > 0:
            # We can borrow the first s qubits from x. (Won't happen but just for completeness)
            borrowable = self.register_x[:self.s]

            circuit.append(HRSCleanIncrementer(
                self.dqa + self.s,  # Note that we gained s dirty qubits.
                self.cqa,
                self.n - self.s,
                0,
                self.c,
                self.overflow_qubit
            ).get_circuit(),
                           list(self.register_c) + list(self.register_x[self.s:]) + list(self.register_o) +
                           list(borrowable) + list(self.register_g) + list(self.register_anc))
            return circuit

        # We need n clean qubits
        register_g, register_anc, ext_reg_g, ext_reg_anc = setup_anc_registers(
            0,
            self.n,
            self.register_g,
            self.register_anc
        )

        # |x>|0> --> |x - 0>|0>
        # Simplification, since we assume clean ancilla, we can just ignore a subtraction

        circuit.x(register_anc)

        # |x - 0 - 0' + 1>|0' + 1>
        # TODO: Maybe replace with CircuitChooser adder?
        circuit.append(
            TTKAdderIP(
                len(ext_reg_g),
                len(ext_reg_anc),
                self.n,
                self.c,
                False,
                self.overflow_qubit).get_circuit().reverse_ops(),
            list(self.register_c) +
            list(register_g) +
            list(register_anc) +
            list(self.register_x) +
            list(self.register_o) +
            list(ext_reg_g) +
            list(ext_reg_anc)
        )

        # |x + 1>|0>
        circuit.x(register_anc)

        if self.overflow_qubit:
            if self.c > 0:
                circuit.mcx(self.register_c, self.register_o[0])
            else:
                circuit.x(self.register_o[0])

        cache[self.identifier] = circuit

        return circuit
