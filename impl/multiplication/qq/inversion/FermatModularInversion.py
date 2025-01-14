import sympy
from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.CircuitNotSupportedError import CircuitNotSupportedError
from api.multiplication.modular.QuantumQuantumModularInverterOOP import QuantumQuantumModularInverterOOP
from impl.util.modular_inversion_coefficients import get_coeffs


class FermatModularInversion(QuantumQuantumModularInverterOOP):
    """
    Modular inversion circuit based on Fermat's last theorem
    Created by Lukas Mansour, with help by Tobias Hartung.

    Takes |x>|0> to |x>|x^(-1) mod p>
    """

    def __init__(self, dqa: int, cqa: int, n: int, p: int, c: int):
        if c > 0:
            # Pretty sure we don't need conditional modular inversion.
            raise CircuitNotSupportedError("Not supported yet")
        # Probabilistic check
        if not sympy.isprime(p):
            raise CircuitNotSupportedError("Circuit is only valid for prime modulus.")
        super().__init__(dqa, cqa, n, p, c)

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        # Get coefficients of the gates
        # Currently not doable in polynomial time, but I believe this part can definitely be reduced to polynomial time.
        # Unfortunately the number of subsets, cannot be reduced, unless we can find out the following:
        # For which p are <= log(p) coefficients non-zero (exponentially many entries are 0)
        # And then for such p, which subsets have a zero coefficient.
        # Without having to calculate all coefficients for all permutations (since we know which ones will be zero)
        # And since there are exponentially many that are 0 (the existance of these 'p' can be emperically checked)
        # We would have for certain primes, a way of creating the modular inverse in polynomial time, outperforming GCD.
        coeffs = get_coeffs(self.p, remove_larger_subsets=True)

        circuit = QuantumCircuit(
            self.register_x,
            self.register_r,
            self.register_g,
            self.register_anc,
            name=f"$MODINV({self.p})$"
        )

        for (subset, coeff) in sorted(coeffs.items(), key=lambda x: x[1]):
            if coeff % self.p == 0:
                continue

            control_qubits = [self.register_x[i] for i in subset]

            borrowable = [x for x in self.register_x]
            for control_qubit in control_qubits:
                borrowable.remove(control_qubit)

            # Each adder has n - len(subset) qubits available to borrow (from register_x)
            adder = CircuitChooser().choose_component(
                "QCModAdderIP",
                (self.n, coeff % self.p, self.p, len(subset)),
                dirty_available=self.dqa + len(borrowable),
                clean_available=self.cqa
            )

            circuit.append(
                adder.get_circuit(),
                control_qubits +
                list(self.register_r) +
                borrowable +
                list(self.register_g) +
                list(self.register_anc),
            )

        cache[self.identifier] = circuit

        return circuit
