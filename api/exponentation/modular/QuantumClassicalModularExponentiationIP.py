import math

from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumClassicalModularExponentiationIP(CircuitComponent):
    """
    This class denotes an n-bit quantum-classical modular exponentiation.

    It will apply the following unitary transformation: |x>|y> --> |x>|y * a^x mod p>.
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, p: int, c: int = 0):
        super().__init__((type(self).__name__, dqa, cqa, n, a, p, c))
        self.mod_bit_len = math.ceil(math.log2(p))
        self.dqa = dqa
        self.cqa = cqa
        self.n = n
        self.a = a
        self.p = p
        self.c = c
        self.register_c = QuantumRegister(c, 'c')
        self.register_x = QuantumRegister(n, 'x')
        self.register_y = QuantumRegister(self.mod_bit_len, 'y')
        self.register_g = QuantumRegister(dqa, 'g')
        self.register_anc = QuantumRegister(cqa, 'anc')
