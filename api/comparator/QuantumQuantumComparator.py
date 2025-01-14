from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumQuantumComparator(CircuitComponent):
    """
    This class denotes a controlled (by c bits) n-bit quantum-quantum comparator.

    It will apply the following unitary transformation: |x>|y>|0> --> |x>|y>|x < y>.
    |1> if x < y, |0> otherwise
    """

    def __init__(self, dqa: int, cqa: int, n: int, c: int = 0):
        super().__init__((type(self).__name__, dqa, cqa, n, c))
        self.dqa = dqa
        self.cqa = cqa
        self.n = n
        self.c = c
        self.register_c = QuantumRegister(c, 'c')
        self.register_x = QuantumRegister(n, 'x')
        self.register_y = QuantumRegister(n, 'y')
        self.register_r = QuantumRegister(1, 'r')
        self.register_g = QuantumRegister(dqa, 'g')
        self.register_anc = QuantumRegister(cqa, 'anc')
