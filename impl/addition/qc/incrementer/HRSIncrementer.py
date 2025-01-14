from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumClassicalIncrementer import QuantumClassicalIncrementer
from impl.addition.qq.TTKAdderIP import TTKAdderIP
from impl.util.ancilla_registers import setup_anc_registers


class HRSIncrementer(QuantumClassicalIncrementer):
    """
    Serial incrementer crated by Häner, Roetteler and Svore (https://arxiv.org/pdf/1611.07995)


    Requires n - s borrowable ('dirty') qubits.
    Requires 0 clean qubits.
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

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_o,
            self.register_g,
            self.register_anc,
            name=f"+{2 ** self.s}_{{HD}}"
        )

        # Just plug in an incrementer and shift everything up by s.
        if self.s > 0:
            # We can borrow the first s qubits from the x register.
            # In principle, one would then have a choice between multiple qubits, and could even optimize this
            # for an actual layout, unfortuantely I don't believe there is any computationally easy way to do this.
            borrowable = self.register_x[:self.s]

            circuit.append(
                HRSIncrementer(
                    self.dqa + self.s,  # We gained s borrowable qubits
                    self.cqa,
                    self.n - self.s,
                    0,
                    self.c,
                    self.overflow_qubit
                ).get_circuit(),
                list(self.register_c) + list(self.register_x[self.s:]) + list(self.register_o) + list(
                    borrowable) + list(self.register_g) + list(self.register_anc))
            return circuit

        # We need to borrow n qubits
        register_g, register_anc, ext_reg_g, ext_reg_anc = setup_anc_registers(
            self.n,
            0,
            self.register_g,
            self.register_anc
        )

        # |x>|g> --> |x - g>|g>
        # TODO: Maybe replace with CircuitChooser adder?
        circuit.append(
            TTKAdderIP(
                len(ext_reg_g),
                len(ext_reg_anc),
                self.n,
                self.c,
                False,
                self.overflow_qubit
            ).get_circuit().reverse_ops(),
            list(self.register_c) + list(register_g) + list(self.register_x) + list(
                self.register_o) + list(ext_reg_g) + list(ext_reg_anc))

        circuit.x(register_g)

        # |x -g - g' + 1>|g' + 1>
        # TODO: Maybe replace with CircuitChooser adder?
        circuit.append(
            TTKAdderIP(
                len(ext_reg_g),
                len(ext_reg_anc),
                self.n,
                self.c,
                False,
                self.overflow_qubit
            ).get_circuit().reverse_ops(),
            list(self.register_c) + list(register_g) + list(register_anc) + list(self.register_x) + list(
                self.register_o) + list(ext_reg_g) + list(ext_reg_anc))

        circuit.x(register_g)

        if self.overflow_qubit:
            if self.c > 0:
                circuit.mcx(self.register_c, self.register_o[0])
            else:
                circuit.x(self.register_o[0])

        cache[self.identifier] = circuit

        return circuit
