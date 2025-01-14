from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumClassicalModularDoublerIP(CircuitComponent):
    """
    This class denotes an n-bit quantum-classical modular doubler.

    It will apply the following unitary transformation: |x>|0> --> |x>|2x mod p>.
    """

    def __init__(self, dqa: int, cqa: int, n: int, p: int, c: int = 0):
        super().__init__((type(self).__name__, dqa, cqa, n, p, c))
        self.dqa = dqa
        self.cqa = cqa
        self.n = n
        self.p = p
        self.c = c
        self.register_c = QuantumRegister(c, 'c')
        self.register_x = QuantumRegister(n, 'x')
        self.register_g = QuantumRegister(dqa, 'g')
        self.register_anc = QuantumRegister(cqa, 'anc')
