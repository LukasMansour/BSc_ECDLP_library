from qiskit import QuantumRegister

from api.CircuitComponent import CircuitComponent


class QuantumQuantumAdderIP(CircuitComponent):
    """
    This class denotes a controlled (by c bits) n-bit quantum-quantum adder.

    It will apply the following unitary transformation: |x>|y> --> |x>|x + y mod (2**n)>.

    These are the additional options (not supported by every implementation!):
    'incoming_carry_qubit': If an incoming carry qubit should be included.
    'overflow_qubit': If an overflow qubit should be included.
    """

    def __init__(self, dqa: int, cqa: int, n: int, c: int = 0, incoming_carry_qubit: bool = False,
                 overflow_qubit: bool = False):
        super().__init__((type(self).__name__, dqa, cqa, n, c, incoming_carry_qubit, overflow_qubit))
        self.dqa = dqa
        self.cqa = cqa
        self.n = n
        self.c = c
        self.register_c = QuantumRegister(c, 'c')
        self.register_x = QuantumRegister(n, 'x')
        self.register_y = QuantumRegister(n, 'y')
        self.incoming_carry_qubit = incoming_carry_qubit
        self.register_in = QuantumRegister(1, 'in') if incoming_carry_qubit else QuantumRegister(0, 'in')
        self.overflow_qubit = overflow_qubit
        self.register_o = QuantumRegister(1, 'o') if overflow_qubit else QuantumRegister(0, 'o')
        self.register_g = QuantumRegister(dqa, 'g')
        self.register_anc = QuantumRegister(cqa, 'anc')
