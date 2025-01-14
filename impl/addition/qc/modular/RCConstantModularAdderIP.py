from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumClassicalModularAdderIP import QuantumClassicalModularAdderIP


class RCConstantModularAdderIP(QuantumClassicalModularAdderIP):
    """
    Constant modular addition circuit by Rines and Chuang (https://arxiv.org/pdf/1801.01081 , Fig 2.).
    """

    def __init__(self, dqa: int, cqa, n: int, a: int, p: int, c: int = 0):
        super().__init__(dqa, cqa, n, a, p, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_g,
            self.register_anc,
            name=f"$[+{self.a}~mod~{self.p}]_{{RC}}$"
        )

        # Extended register x by [register_anc[0]] since it is for two's complement addition.
        s_register_x = list(self.register_x) + [self.register_anc[0]]

        # +X (here: +a)
        qc_adder = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n + 1, self.a, self.c),
            dirty_available=self.dqa,
            clean_available=self.cqa - 1
        )

        circuit.append(qc_adder.get_circuit(),
                       list(self.register_c) +
                       s_register_x +
                       list(self.register_g) +
                       list(self.register_anc[1:])
                       )

        # -N (here: -p)
        # Control qubits available to borrow
        # 1 clean ancilla used.

        qc1_adder = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n + 1, self.p, 0),
            dirty_available=self.dqa + self.c,
            clean_available=self.cqa - 1
        )

        borrowable = list(self.register_c)

        circuit.append(qc1_adder.get_circuit().reverse_ops(),
                       s_register_x +
                       borrowable +
                       list(self.register_g) +
                       list(self.register_anc[1:])
                       )

        # Copy out the MSB
        circuit.cx(s_register_x[-1], self.register_anc[1])

        # +N (here: +p)
        # Control qubits available to borrow
        # 2 clean ancillas used.
        qc2_adder = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n + 1, self.p, 1),
            dirty_available=self.dqa + self.c,
            clean_available=self.cqa - 2
        )

        borrowable = list(self.register_c)

        circuit.append(qc2_adder.get_circuit(),
                       [self.register_anc[1]] +
                       s_register_x +
                       borrowable +
                       list(self.register_g) +
                       list(self.register_anc[2:])
                       )

        # -X (here: -a)
        # Now we just need to reset the ancilla.
        # Control qubits available to borrow
        qc3_adder = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n + 1, self.a, 0),
            dirty_available=self.dqa + self.c,
            clean_available=self.cqa - 2
        )

        borrowable = list(self.register_c)

        circuit.append(qc3_adder.get_circuit().reverse_ops(),
                       s_register_x +
                       borrowable +
                       list(self.register_g) +
                       list(self.register_anc[2:])
                       )

        # Extract MSB
        circuit.mcx(list(self.register_c) + [s_register_x[-1]], self.register_anc[1])

        # x first, just in case the ancilla is borrowed by the final gate.
        circuit.x(self.register_anc[1])

        # Final addition, we once again have two clean qubit available and the control qubit(s).

        qc4_adder = CircuitChooser().choose_component(
            "QCAdderIP",
            (self.n + 1, self.a, 0),
            dirty_available=self.dqa + self.c,
            clean_available=self.cqa - 1
        )

        circuit.append(
            qc4_adder.get_circuit(),
            s_register_x +
            borrowable +
            list(self.register_g) +
            list(self.register_anc[1:])
        )

        cache[self.identifier] = circuit

        return circuit
