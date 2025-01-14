from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.multiplication.modular.QuantumClassicalModularSquarerOOP import QuantumClassicalModularSquarerOOP


class RNSLModularSquaringOOP(QuantumClassicalModularSquarerOOP):
    """
    Modular squaring circuit by Roetteler, Naehrig, Svore and Lauter (https://arxiv.org/pdf/1706.06752, Fig 6.).
    """

    def __init__(self, dqa: int, cqa: int, n: int, p: int, c: int):
        if p % 2 == 0:
            raise ValueError("Modulus must be odd!")
        super().__init__(dqa, cqa, n, p, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_x,
            self.register_r,
            self.register_g,
            self.register_anc,
            name=f"|x^2 mod {self.p}>"
        )

        for i in reversed(range(0, self.n)):
            circuit.cx(self.register_x[i], self.register_anc[0])

            # Addition of two quantum states mod p. with 1 control
            # Will be repeated n times in the exact same conditions.
            # No qubits available for borrowing
            qq_mod_add = CircuitChooser().choose_component(
                "QQModAdderIP",
                (self.n, self.p, 1),
                dirty_available=self.dqa,
                clean_available=self.cqa - 1
            )

            circuit.append(
                qq_mod_add.get_circuit(),
                [self.register_anc[0]] +
                list(self.register_x) +
                list(self.register_r) +
                list(self.register_g) +
                list(self.register_anc[1:])
            )

            circuit.cx(self.register_x[i], self.register_anc[0])

            if i > 0:  # Don't double for the LSB.
                # IP Modular Multiplication *2 (Modular doubling)
                # Will be repeated n - 1 times in the exact same conditions.
                # With n borrable qubits (register_x)
                qc_mod_dbl = CircuitChooser().choose_component(
                    "QCModDoublerIP",
                    (self.n, self.p, 0),
                    dirty_available=self.dqa + self.n,
                    clean_available=self.cqa
                )

                borrowable = list(self.register_x)
                borrowable.remove(self.register_x[i])
                borrowable.append(self.register_x[i])
                # push x[i] to the last borrowable position to improve parallelism.

                circuit.append(
                    qc_mod_dbl.get_circuit(),
                    list(self.register_r) +
                    borrowable +
                    list(self.register_g) +
                    list(self.register_anc)
                )

        cache[self.identifier] = circuit

        return circuit
