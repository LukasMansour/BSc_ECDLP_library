from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.CircuitNotSupportedError import CircuitNotSupportedError
from api.addition.QuantumClassicalAdderIP import QuantumClassicalAdderIP
from impl.encoding.binary_encoding import binary_encoding


class CopyCTRLConstantAdderIP(QuantumClassicalAdderIP):
    """
    Constant addition circuit based on a copy-controlling circuit.
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, c: int = 0):
        if a > 0 and cqa < n:
            raise CircuitNotSupportedError("Not enough clean qubits available.")
        super().__init__(dqa, cqa, n, a % (1 << n), c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if self.n == 0 or self.a == 0:
            return QuantumCircuit(
                self.register_c,
                self.register_x,
                self.register_g,
                self.register_anc,
                name=f"[+{self.a}]_{{CC}}"
            )

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_g,
            self.register_anc,
            name=f"[+{self.a}]_{{CC}}"
        )

        # The idea behind the copy controlled adder is very simple.
        # Load the number we want to add to an ancilla register (copy) conditionally (controlled).
        circuit.append(
            binary_encoding(self.n, self.a, False, self.c),
            list(self.register_c) + list(self.register_anc[:self.n])
        )

        # Plug in a quantum-quantum adder! (will add 0 if control qubit was 0).
        qq_adder = CircuitChooser().choose_component(
            "QQAdderIP",
            (self.n, 0, False, False),
            dirty_available=self.dqa + self.c,
            clean_available=max(self.cqa - self.n, 0)  # used n to store the ancillas.
        )

        borrowable = list(self.register_c)

        circuit.append(
            qq_adder.get_circuit(),
            list(self.register_anc[:self.n]) +  # source
            list(self.register_x) +  # target
            list(self.register_g) +
            borrowable +
            list(self.register_anc[self.n:])
        )

        # Now unload the number from the ancilla register.
        circuit.append(
            binary_encoding(self.n, self.a, False, self.c),
            list(self.register_c) + list(self.register_anc[:self.n])
        )

        cache[self.identifier] = circuit

        return circuit
