from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumClassicalMultiplierIP(CircuitComponent):
    """
    This class denotes an n-bit quantum-classical multiplier.

    It will apply the following unitary transformation: |x>|0> --> |a*x mod 2**n>|0>.
    """

    def __init__(self, n: int, a: int, c: int = 0):
        super().__init__((type(self).__name__, n, a, c))
        self.n = n
        self.a = a
        self.c = c
        self.register_c = QuantumRegister(c, 'c')
        self.register_x = QuantumRegister(n, 'x')
