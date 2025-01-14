from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumClassicalAdderIP(CircuitComponent):
    """
    This class denotes an n-bit quantum-classical adder.

    It will apply the following unitary transformation: |x>|0> --> |(x + a) mod 2**n>|0>.
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
        self.register_g = QuantumRegister(dqa, 'g')
        self.register_anc = QuantumRegister(cqa, 'anc')
