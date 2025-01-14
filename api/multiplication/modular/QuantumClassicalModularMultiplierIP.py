from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumClassicalModularMultiplierIP(CircuitComponent):
    """
    This class denotes an n-bit quantum-classical in-place modular multiplier.

    It will apply the following unitary transformation: |x>|0> --> |a*x mod p>|0>.
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, p: int, c: int = 0):
        super().__init__((type(self).__name__, dqa, cqa, n, a, p, c))
        self.dqa = dqa
        self.cqa = cqa
        self.n = n
        self.a = a
        self.p = p
        self.c = c
        self.register_c = QuantumRegister(c, 'c')
        self.register_x = QuantumRegister(n, 'x')
        self.register_g = QuantumRegister(dqa, 'g')
        self.register_anc = QuantumRegister(cqa, 'anc')
