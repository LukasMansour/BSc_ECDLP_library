import sympy
from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.CircuitNotSupportedError import CircuitNotSupportedError
from api.multiplication.modular.QuantumClassicalModularMultiplierIP import QuantumClassicalModularMultiplierIP


class HRSConstantModularMultiplierIP(QuantumClassicalModularMultiplierIP):
    """
    Modular multiplication circuit by Häner, Roetteler and Svore (https://arxiv.org/pdf/1611.07995).
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, p: int, c: int):
        if not sympy.isprime(p):
            raise CircuitNotSupportedError(
                "p must be a prime number, as we use the modular inverse, which is only guaranteed to exist for primes p.")
        if cqa < n:
            raise CircuitNotSupportedError("HRSConstantModularMultiplierIP: requires at least n clean ancilla qubits.")
        super().__init__(dqa, cqa, n, a, p, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_g,
            self.register_anc,
            name=f"$\\cdot {self.a}~mod~{self.p}$"
        )

        # OOP Multiplcation by a
        qc_mul_1 = CircuitChooser().choose_component(
            "QCModMulOOP",
            (self.n, self.a, self.p, self.c),
            dirty_available=self.dqa,
            clean_available=self.cqa - self.n
        )

        circuit.append(
            qc_mul_1.get_circuit(),
            list(self.register_c) +
            list(self.register_x) +
            list(self.register_anc[:self.n]) +
            list(self.register_g) +
            list(self.register_anc[self.n:])
        )
        # OOP Multiplication by (p - pow(a, -1, p))
        qc_mul_2 = CircuitChooser().choose_component(
            "QCModMulOOP",
            (self.n, pow(self.a, -1, self.p), self.p, self.c),
            dirty_available=self.dqa,
            clean_available=self.cqa - self.n
        )

        # subtract (a^{-1}ax)
        circuit.append(
            qc_mul_2.get_circuit().reverse_ops(),
            list(self.register_c) +
            list(self.register_anc[:self.n]) +
            list(self.register_x) +
            list(self.register_g) +
            list(self.register_anc[self.n:])
        )

        if self.c > 0:
            for i in range(0, self.n):
                # Since we know the register_x[i] now contains zeros, we can simplify this controlled swap and save an MCX.
                circuit.mcx(list(self.register_c) + [self.register_anc[i]], self.register_x[i])
                circuit.mcx(list(self.register_c) + [self.register_x[i]], self.register_anc[i])
        else:
            for i in range(0, self.n):
                # Since we know the register_x[i] now contains zeros, we can simplify this swap to two CNOTs.
                circuit.cx(self.register_anc[i], self.register_x[i])
                circuit.cx(self.register_x[i], self.register_anc[i])

        cache[self.identifier] = circuit

        return circuit
