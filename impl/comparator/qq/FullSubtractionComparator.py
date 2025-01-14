from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Gate

from api.CircuitChooser import CircuitChooser
from api.comparator.QuantumQuantumComparator import QuantumQuantumComparator


class FullSubtractionComparator(QuantumQuantumComparator):
    """
    Comparator that uses a subtraction-based system
    Implementation also taken/adapted from there.
    """

    def __init__(self, dqa: int, cqa: int, n: int, c: int):
        super().__init__(dqa, cqa, n, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_y,
            self.register_r,
            self.register_g,
            self.register_anc,
            name=f"$<$"
        )

        # Subtracion of two quantum states
        # No qubits available to borrow
        qq_adder = CircuitChooser().choose_component(
            "QQAdderIP", (self.n, self.c, False, True),
            dirty_available=self.dqa,
            clean_available=self.cqa,
        )

        # subtract x -y and the msb result bit will be in r.
        circuit.append(qq_adder.get_circuit().reverse_ops(),
                       list(self.register_c) +
                       list(self.register_y) +
                       list(self.register_x) +
                       list(self.register_r) +
                       list(self.register_g) +
                       list(self.register_anc)
                       )

        # Addition of two quantum states
        # result qubit can be borrowed when restoring the state.
        qq1_adder = CircuitChooser().choose_component(
            "QQAdderIP",
            (self.n, self.c, False, False),
            dirty_available=self.dqa + 1,
            clean_available=self.cqa,
        )

        borrowable = list(self.register_r)

        circuit.append(qq1_adder.get_circuit(),
                       list(self.register_c) +
                       list(self.register_y) +
                       list(self.register_x) +
                       borrowable +
                       list(self.register_g) +
                       list(self.register_anc)
                       )

        # circuit.mcx(list(self.register_c), self.register_r[0]) if self.c > 0 else circuit.x(self.register_r[0])

        cache[self.identifier] = circuit

        return circuit


def compare2() -> Gate:
    register_x = QuantumRegister(2, 'x')
    register_y = QuantumRegister(2, 'y')
    register_r = QuantumRegister(1, 'r')

    cmp2 = QuantumCircuit(register_x, register_y, register_r, name='cmp2')

    cmp2.x(register_r)

    cmp2.cx(register_y[0], register_x[0])
    cmp2.cx(register_y[1], register_x[1])
    cmp2.cswap(register_x[1], register_x[0], register_r[0])
    cmp2.cswap(register_x[1], register_y[0], register_y[1])
    cmp2.cx(register_y[0], register_x[0])
    return cmp2.to_gate()
