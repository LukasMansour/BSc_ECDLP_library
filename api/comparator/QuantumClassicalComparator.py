from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumClassicalComparator(CircuitComponent):
    """
    This class denotes a controlled (by c bits) n-bit quantum-classical comparator.

    It will apply the following unitary transformation: |x>|0> --> |x>|x < a>.
    |1> if x < a, |0> otherwise
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, c: int = 0):
        super().__init__((type(self).__name__, dqa, cqa, n, a, c))
        self.dqa = dqa
        self.cqa = cqa
        self.n = n
        self.a = a
        self.c = c
        self.register_c = QuantumRegister(c, 'c')
        self.register_x = QuantumRegister(n, 'x')
        self.register_r = QuantumRegister(1, 'r')
        self.register_g = QuantumRegister(dqa, 'g')
        self.register_anc = QuantumRegister(cqa, 'anc')
