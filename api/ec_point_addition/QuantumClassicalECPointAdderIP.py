from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumClassicalECPointAdderIP(CircuitComponent):
    """
    This class denotes an n-bit quantum-classical multiplier.

    It will apply the following unitary transformation: |x>|0> --> |a*x mod 2**n>|0>.
    """

    def __init__(self, dqa: int, cqa: int, n: int, ec_point: (int, int), p: int, c: int = 0):
        super().__init__((type(self).__name__, dqa, cqa, n, ec_point, p, c))
        self.dqa = dqa
        self.cqa = cqa
        self.n = n
        self.ec_point = ec_point
        self.p = p
        self.c = c
        self.register_c = QuantumRegister(c, 'c')
        self.register_x = QuantumRegister(n, 'x')
        self.register_y = QuantumRegister(n, 'y')
        self.register_g = QuantumRegister(dqa, 'g')
        self.register_anc = QuantumRegister(cqa, 'anc')
