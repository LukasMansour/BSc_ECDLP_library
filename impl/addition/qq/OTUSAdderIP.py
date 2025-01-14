from math import log2

from qiskit import QuantumCircuit
from qiskit.circuit import Gate

from api.CircuitChooser import CircuitChooser
from api.CircuitNotSupportedError import CircuitNotSupportedError
from api.addition.QuantumQuantumAdderIP import QuantumQuantumAdderIP
from impl.util.ancilla_registers import setup_anc_registers


class OTUSAdderIP(QuantumQuantumAdderIP):
    """
    Addition circuit by Oonishi, Tanaka, Uno, Satoah, Van Meter and Kunihiro (https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=9655478).
    Special thanks to: https://egrettathula.wordpress.com/2024/06/29/a-logarithmic-depth-quantum-adder/
    """

    def __init__(self, dqa: int, cqa: int, n: int, c: int = 0, incoming_carry_qubit=False, overflow_qubit: bool = True):
        if incoming_carry_qubit:
            # TODO: Add support for incoming carry.
            raise CircuitNotSupportedError("OTUSAdder does not support incoming carry.")
        if not overflow_qubit:
            # TODO: Add support for not having an overflow qubit
            raise CircuitNotSupportedError("OTUSAdder does not support not having an overflow qubit.")
        super().__init__(dqa, cqa, n, c, incoming_carry_qubit=False, overflow_qubit=True)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        log2n = int(log2(self.n))
        num_anc = 2 * self.n - log2n - bin(self.n)[2:].count('1') - 1

        circuit = QuantumCircuit(
            self.register_x,
            self.register_y,
            self.register_o,
            self.register_g,
            self.register_anc,
            name="$+_{OTUS}$"
        )

        register_g, register_anc, ext_reg_g, ext_reg_anc = setup_anc_registers(
            0,
            num_anc,
            list(self.register_g),
            list(self.register_anc),
        )

        register_anc.insert(self.n - 1, self.register_o[0])

        # P-Rounds
        P_rounds = []
        p_dict = {0: {}}
        for i in range(0, self.n):
            p_dict[0][i] = self.register_y[i]

        _index = self.n - 0
        for t in range(1, log2n):
            p_dict[t] = {}
            for i in range(1, int(self.n / 2 ** t)):
                p_dict[t][i] = register_anc[_index]
                triple = (p_dict[t - 1][2 * i], p_dict[t - 1][2 * i + 1], p_dict[t][i])
                P_rounds.append(triple)
                _index += 1

        # G-rounds
        G_rounds = []
        for t in range(1, log2n + 1):
            for i in range(int(self.n / 2 ** t)):
                triple = (register_anc[2 ** t * i + 2 ** (t - 1) - 1], p_dict[t - 1][2 * i + 1],
                          register_anc[2 ** t * i + 2 ** t - 1])
                G_rounds.append(triple)

        # C-rounds
        C_rounds = []
        for t in range(int(log2(2 * self.n / 3)), 0, -1):
            for i in range(1, int((self.n - 2 ** (t - 1)) / 2 ** t) + 1):
                triple = (
                    register_anc[2 ** t * i - 1], p_dict[t - 1][2 * i], register_anc[2 ** t * i + 2 ** (t - 1) - 1])
                C_rounds.append(triple)

        # Black
        for i in range(0, self.n):
            if i == (self.n - 1):
                circuit.ccx(self.register_x[i], self.register_y[i], register_anc[i])
            elif i < (self.n - 1):
                circuit.append(ccix(), [self.register_x[i], self.register_y[i], register_anc[i]])
            circuit.cx(self.register_x[i], self.register_y[i])

        # Blue
        for triple in P_rounds:
            circuit.rccx(triple[0], triple[1], triple[2])

        # Red
        for triple in G_rounds:
            if triple[1] == self.register_y[self.n - 1]:
                circuit.ccx(triple[0], triple[1], triple[2])
            else:
                circuit.append(ccix(), [triple[0], triple[1], triple[2]])

        # Green
        for triple in C_rounds:
            if triple[2] == register_anc[self.n - 1]:
                circuit.ccx(triple[0], triple[1], triple[2])
            else:
                circuit.append(ccix(), [triple[0], triple[1], triple[2]])

        # Blue
        for triple in reversed(P_rounds):
            circuit.rccx(triple[0], triple[1], triple[2])

        # Black
        for i in range(self.n - 1):
            circuit.cx(register_anc[i], self.register_y[i + 1])
            circuit.x(self.register_y[i])
        for i in range(1, self.n - 1):
            circuit.cx(self.register_x[i], self.register_y[i])

        # Blue
        for triple in P_rounds:
            if triple[1] == self.register_y[self.n - 1]: continue
            circuit.rccx(triple[0], triple[1], triple[2])

        # Green
        for triple in reversed(C_rounds):
            if triple[2] == register_anc[self.n - 1]: continue
            circuit.append(ccixdg(), [triple[0], triple[1], triple[2]])

        # Red
        for triple in reversed(G_rounds):
            if triple[1] == self.register_y[self.n - 1]: continue
            circuit.append(ccixdg(), [triple[0], triple[1], triple[2]])

        # Blue
        for triple in reversed(P_rounds):
            if triple[1] == self.register_y[self.n - 1]: continue
            circuit.rccx(triple[0], triple[1], triple[2])

        # Black
        for i in range(self.n - 1):
            if i > 0:
                circuit.cx(self.register_x[i], self.register_y[i])
            circuit.append(ccixdg(), [self.register_x[i], self.register_y[i], register_anc[i]])
            circuit.x(self.register_y[i])

        # TODO: Improve OTUS controlled circuit
        # AFAIK this should be doable as some rounds are inverses of each other and do not need to be controlled.
        if self.c > 0:
            circuit = circuit.control(self.c)

        cache[self.identifier] = circuit

        return circuit


def ccix() -> Gate:
    qc = QuantumCircuit(3, name="CCIX")
    qc.h(2)
    qc.cx(0, 2)
    qc.t(2)
    qc.cx(1, 2)
    qc.tdg(2)
    qc.cx(0, 2)
    qc.t(2)
    qc.cx(1, 2)
    qc.tdg(2)
    qc.h(2)
    return qc.to_gate()


def ccixdg() -> Gate:
    qc = QuantumCircuit(3, name="CCIXDG")
    qc.h(2)
    qc.t(2)
    qc.cx(1, 2)
    qc.tdg(2)
    qc.cx(0, 2)
    qc.t(2)
    qc.cx(1, 2)
    qc.tdg(2)
    qc.cx(0, 2)
    qc.h(2)
    return qc.to_gate()
