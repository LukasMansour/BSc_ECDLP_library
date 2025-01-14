from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Gate

from api.CircuitChooser import CircuitChooser
from api.CircuitNotSupportedError import CircuitNotSupportedError
from api.addition.QuantumClassicalIncrementer import QuantumClassicalIncrementer
from impl.util.ancilla_registers import setup_anc_registers


class GidneyIncrementer(QuantumClassicalIncrementer):
    """
    Linear Incrementer by Craig Gidney (https://algassert.com/circuits/2015/06/12/Constructing-Large-Increment-Gates.html)

    Requires n + 1 borrowable ('dirty') qubits.
    Requires 0 clean qubits.
    """

    def __init__(self,
                 dqa: int,  # dirty qubits available
                 cqa: int,  # clean qubits available
                 n: int,
                 s: int = 0,
                 c: int = 0,
                 overflow_qubit: bool = False
                 ):
        if dqa + cqa < n + 1 - s:
            raise CircuitNotSupportedError("Not enough dirty qubits available.")
        super().__init__(dqa, cqa, n, s, c, overflow_qubit=overflow_qubit)

    def get_circuit(self, *args) -> QuantumCircuit:
        if self.n == 0:
            return QuantumCircuit(0)

        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_x,
            self.register_o,
            self.register_g,
            self.register_anc,
            name=f"+{2 ** self.s}_G"
        )

        # Notice the difference between register g and self.register_g !
        # Requires n + 1 dirty qubits.
        register_g, register_anc, ext_reg_g, ext_reg_anc = setup_anc_registers(
            self.n + 1,
            0,
            list(self.register_g) + list(self.register_x[:self.s]),  # we can borrow the first s qubits from x.
            self.register_anc
        )

        for i in range(self.s, self.n):
            circuit.cx(register_g[self.s], self.register_x[i])

        for i in range(self.s + 1, self.n + 1):
            circuit.x(register_g[i])

        if self.overflow_qubit:
            circuit.x(self.register_o[0])

        for i in range(self.s, self.n):
            circuit.append(gidney_downward_part(), [register_g[i], register_g[i + 1], self.register_x[i]])

        if self.overflow_qubit:
            circuit.cx(register_g[-1], self.register_o[0])

        for i in reversed(range(self.s, self.n)):
            circuit.append(gidney_upward_part(), [register_g[i], register_g[i + 1], self.register_x[i]])

        for i in range(self.s + 1, self.n + 1):
            circuit.x(register_g[i])

        for i in range(self.s, self.n):
            circuit.append(gidney_downward_part(), [register_g[i], register_g[i + 1], self.register_x[i]])

        if self.overflow_qubit:
            circuit.cx(register_g[-1], self.register_o[0])

        for i in reversed(range(self.s, self.n)):
            circuit.append(gidney_upward_part(), [register_g[i], register_g[i + 1], self.register_x[i]])

        for i in range(self.s, self.n):
            circuit.cx(register_g[self.s], self.register_x[i])

        if self.c > 0:
            circuit = circuit.control(self.c)

        cache[self.identifier] = circuit

        return circuit


def gidney_downward_part() -> Gate:
    register_g = QuantumRegister(2, 'g')
    register_x = QuantumRegister(1, 'x')

    circuit = QuantumCircuit(register_g, register_x)

    circuit.cx(register_g[0], register_x[0])
    circuit.cx(register_g[1], register_g[0])
    circuit.ccx(register_g[0], register_x[0], register_g[1])

    return circuit.to_gate()


def gidney_upward_part() -> Gate:
    register_g = QuantumRegister(2, 'g')
    register_x = QuantumRegister(1, 'x')

    circuit = QuantumCircuit(register_g, register_x)

    circuit.ccx(register_g[0], register_x[0], register_g[1])
    circuit.cx(register_g[1], register_g[0])
    circuit.cx(register_g[1], register_x[0])

    return circuit.to_gate()
