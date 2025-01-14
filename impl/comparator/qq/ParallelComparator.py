import numpy as np
from qiskit import QuantumCircuit, AncillaRegister, QuantumRegister
from qiskit.circuit import Gate

from api.CircuitChooser import CircuitChooser
from api.CircuitNotSupportedError import CircuitNotSupportedError
from api.comparator.QuantumQuantumComparator import QuantumQuantumComparator


class ParallelComparator(QuantumQuantumComparator):
    """
    Comparator (I believe by Egretta Thula) (https://egrettathula.wordpress.com/2023/04/18/efficient-quantum-comparator-circuit/).
    Implementation also taken/adapted from there.
    """

    def __init__(self, dqa: int, cqa: int, n: int, c: int):
        if cqa < n - 1:  # requires at least self.n - 1 clean qubits
            raise CircuitNotSupportedError("ParallelComparator requires n - 1 clean qubits.")
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
        s_register_anc = [self.register_r] + list(self.register_anc)

        l = list(range(self.n))
        _sequence = []
        steps = int(np.ceil(np.log2(self.n)))
        anc_idx = 1
        for step in range(steps):
            _sequence.append(l.copy())
            for m in range(int(len(l) / 2) - 1, -1, -1):
                circuit.append(compare2(),
                               [self.register_x[l[2 * m]], self.register_x[l[2 * m + 1]],
                                self.register_y[l[2 * m]], self.register_y[l[2 * m + 1]], s_register_anc[anc_idx]])
                l.pop(2 * m + 1)
                anc_idx = anc_idx + 1

        # Copy result
        circuit.x(self.register_x[0])
        circuit.mcx(list(self.register_c) + [self.register_x[0], self.register_y[0]], s_register_anc[0])
        circuit.x(self.register_x[0])
        # if self.c > 0:
        #     circuit.mcx(list(self.register_c), s_register_anc[0])
        # else:
        #     circuit.x(s_register_anc[0])

        # Uncompute
        for step in range(steps):
            l = _sequence.pop(-1)
            for m in range(int(len(l) / 2)):
                anc_idx = anc_idx - 1
                circuit.append(compare2().inverse(),
                               [self.register_x[l[2 * m]], self.register_x[l[2 * m + 1]], self.register_y[l[2 * m]],
                                self.register_y[l[2 * m + 1]], s_register_anc[anc_idx]])

        cache[self.identifier] = circuit

        return circuit


def compare2() -> Gate:
    register_x = QuantumRegister(2, 'x')
    register_y = QuantumRegister(2, 'y')
    register_r = AncillaRegister(1, 'r')

    cmp2 = QuantumCircuit(register_x, register_y, register_r, name='cmp2')

    cmp2.x(register_r)

    cmp2.cx(register_y[0], register_x[0])
    cmp2.cx(register_y[1], register_x[1])
    cmp2.cswap(register_x[1], register_x[0], register_r[0])
    cmp2.cswap(register_x[1], register_y[0], register_y[1])
    cmp2.cx(register_y[0], register_x[0])
    return cmp2.to_gate()
