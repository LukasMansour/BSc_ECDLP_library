from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumClassicalIncrementer(CircuitComponent):
    """
    This class denotes an n-bit quantum-classical incrementer.

    It will apply the following unitary transformation: |x>|0> --> |(x + 1) mod 2**n>|0>.
    """

    def __init__(self, dqa: int, cqa: int, n: int, s: int, c: int = 0, overflow_qubit: bool = False):
        super().__init__((type(self).__name__, dqa, cqa, n, s, c, overflow_qubit))
        self.dqa = dqa
        self.cqa = cqa
        self.n = n
        self.s = s
        self.c = c
        self.overflow_qubit = overflow_qubit
        self.register_c = QuantumRegister(c, 'c')
        self.register_x = QuantumRegister(n, 'x')
        self.register_o = QuantumRegister(1, 'o') if overflow_qubit else QuantumRegister(0, 'o')
        self.register_g = QuantumRegister(dqa, 'g')
        self.register_anc = QuantumRegister(cqa, 'anc')
