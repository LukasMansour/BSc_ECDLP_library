from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Gate

from api.CircuitChooser import CircuitChooser
from api.CircuitNotSupportedError import CircuitNotSupportedError
from api.addition.QuantumQuantumAdderIP import QuantumQuantumAdderIP


class CDKMAdderIP(QuantumQuantumAdderIP):
    """
    Addition circuit by Cuccaro, Draper, Kutin and Moulton (https://arxiv.org/abs/quant-ph/0410184).

    Has two variants for UMA (Unmajority-Add) Circuits,
    0 --> simpler version
    1 --> Better parallelism version
    """

    def __init__(self, dqa: int, cqa: int, n: int, c: int = 0, incoming_carry_qubit=False, overflow_qubit: bool = True,
                 variant=1):
        if incoming_carry_qubit:
            raise ValueError("CDKMAdder's first ancilla qubit is the incoming carry.")
        if cqa < 1:  # Requires at least one ancilla.
            raise CircuitNotSupportedError("Not enough clean qubits available.")

        super().__init__(dqa, cqa, n, c, incoming_carry_qubit=False, overflow_qubit=overflow_qubit)
        # TODO: Add better support for Variant(s).
        self.variant = variant

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_x,
            self.register_y,
            self.register_o,
            self.register_g,
            self.register_anc,
            name="$+_{CDKM}$"
        )

        # Apply first MAJ gate to (c_0, b_0, a_0)
        circuit.append(maj_circuit(), [self.register_anc[0], self.register_y[0], self.register_x[0]])
        for i in range(1, self.n):  # [1, n-1]
            circuit.append(maj_circuit(), [self.register_x[i - 1], self.register_y[i], self.register_x[i]])

        # Now apply the carry bit if necessary
        if self.overflow_qubit:
            circuit.cx(self.register_x[self.n - 1], self.register_o[0])

        if self.variant == 0:
            uma_circuit = uma_circuit_a
        elif self.variant == 1:
            uma_circuit = uma_circuit_b
        else:
            raise ValueError("Unknown UMA variant.")
        # Now apply the UMA gates
        for i in range(self.n - 1, 0, -1):  # [n-1, 1]
            circuit.append(uma_circuit(), [self.register_x[i - 1], self.register_y[i], self.register_x[i]])

        # Apply last UMA gate
        circuit.append(uma_circuit(), [self.register_anc[0], self.register_y[0], self.register_x[0]])

        # TODO: Improve CDKM controlled circuit
        # See: https://arxiv.org/pdf/1612.07424 for improvements for specific cases.
        # AFAIK this should be doable as some rounds are inverses of each other and do not need to be controlled.
        if self.c > 0:
            circuit = circuit.control(self.c)

        cache[self.identifier] = circuit

        return circuit


def maj_circuit() -> Gate:
    """
    Gets the Majority circuit (MAJ).

    Source: https://arxiv.org/abs/quant-ph/0410184
    :return: Gate on 3 qubits, representing the MAJ circuit
    """
    register = QuantumRegister(3, 'm')

    circuit = QuantumCircuit(register, name="$MAJ$")

    circuit.cx(register[2], register[1])
    circuit.cx(register[2], register[0])
    circuit.ccx(register[0], register[1], register[2])

    return circuit.to_gate()


def uma_circuit_a() -> Gate:
    """
    Gets the Unmajority and Add (UMA).
    This is the 2-CNOT version

    Source: https://arxiv.org/abs/quant-ph/0410184

    :return: Gate on 3 qubits, representing the UMA circuit
    """
    register = QuantumRegister(3, 'm')

    circuit = QuantumCircuit(register, name="$UMA_a$")

    circuit.ccx(register[0], register[1], register[2])
    circuit.cx(register[2], register[0])
    circuit.cx(register[0], register[1])

    return circuit.to_gate()


def uma_circuit_b() -> Gate:
    """
    Gets the Unmajority and Add (UMA).
    This is the 3-CNOT version

    Source: https://arxiv.org/abs/quant-ph/0410184

    :return: Gate on 3 qubits, representing the UMA circuit
    """
    register = QuantumRegister(3, 'm')

    circuit = QuantumCircuit(register, name="$UMA_b$")

    circuit.x(register[1])
    circuit.cx(register[0], register[1])
    circuit.ccx(register[0], register[1], register[2])
    circuit.x(register[1])
    circuit.cx(register[2], register[0])
    circuit.cx(register[2], register[1])

    return circuit.to_gate()
