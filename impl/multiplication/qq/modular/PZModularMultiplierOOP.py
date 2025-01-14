from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.multiplication.modular.QuantumQuantumModularMultiplierOOP import QuantumQuantumModularMultiplierOOP


class PZModularMultiplierOOP(QuantumQuantumModularMultiplierOOP):
    """
    Based on Proos and Zalka (https://arxiv.org/pdf/quant-ph/0301141 , Section 4.3.2).
    Also See: (https://arxiv.org/pdf/1706.06752, Fig 6.)
    """

    def __init__(self, dqa: int, cqa: int, n: int, p: int, c: int):
        super().__init__(dqa, cqa, n, p, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_x,
            self.register_y,
            self.register_r,
            self.register_g,
            self.register_anc,
            name=f"|x*y mod {self.p}>"
        )

        # Addition of two quantum states mod p. with 1 control
        # Will be repeated n times in the exact same conditions.
        # Always has (n-1) qubits in register_x to borrow.
        qq_mod_add = CircuitChooser().choose_component(
            "QQModAdderIP",
            (self.n, self.p, 1),
            dirty_available=self.dqa + self.n - 1,
            clean_available=self.cqa
        )

        borrowable = [x for x in self.register_x]
        borrowable.remove(self.register_x[self.n - 1])

        circuit.append(
            qq_mod_add.get_circuit(),
            [self.register_x[self.n - 1]] +
            list(self.register_y) +
            list(self.register_r) +
            borrowable +
            list(self.register_g) +
            list(self.register_anc)
        )

        for i in reversed(range(0, self.n - 1)):
            # IP Modular Multiplication *2 (Modular doubling)
            # Will be repeated n - 1 times in the exact same conditions.
            # With 2*n borrable qubits (register_x and register_y)
            qc_mod_dbl = CircuitChooser().choose_component(
                "QCModDoublerIP",
                (self.n, self.p, self.c),
                dirty_available=self.dqa + self.n + self.n,
                clean_available=self.cqa
            )

            borrowable = list(self.register_x) + list(self.register_y)

            circuit.append(
                qc_mod_dbl.get_circuit(),
                list(self.register_r) +
                borrowable +
                list(self.register_g) +
                list(self.register_anc)
            )

            borrowable = [x for x in self.register_x]
            borrowable.remove(self.register_x[i])

            circuit.append(
                qq_mod_add.get_circuit(),
                [self.register_x[i]] +
                list(self.register_y) +
                list(self.register_r) +
                borrowable +
                list(self.register_g) +
                list(self.register_anc)
            )

        cache[self.identifier] = circuit

        return circuit
