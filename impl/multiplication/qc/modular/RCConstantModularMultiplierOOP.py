import math

from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.CircuitNotSupportedError import CircuitNotSupportedError
from api.multiplication.modular.QuantumClassicalModularMultiplierOOP import QuantumClassicalModularMultiplierOOP


class RCConstantModularMultiplierOOP(QuantumClassicalModularMultiplierOOP):
    """
    Constant modular multiplication circuit by Rines and Chuang (https://arxiv.org/pdf/1801.01081 , Fig 6.).
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, p: int, c: int = 0):
        if p % 2 == 0:
            raise CircuitNotSupportedError("Circuit is only valid for odd modulus.")
        super().__init__(dqa, cqa, n, a, p, c)
        self.m = math.ceil(math.log2(n))

    def get_circuit(self, *args) -> QuantumCircuit:
        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_r,
            self.register_g,
            self.register_anc,
            name=f"$\\cdot {self.a} ~mod~{self.p}$"
        )

        for i in range(0, self.n):
            # Each adder has n - 1 qubits available to borrow (from register_x)
            adder = CircuitChooser().choose_component(
                "QCAdderIP",
                (self.n + self.m, (self.a * (2 ** i)) % self.p, self.c + 1),
                dirty_available=self.dqa + self.n - 1,
                clean_available=self.cqa - self.m
            )

            borrowable = list(self.register_x)
            borrowable.remove(self.register_x[i])

            circuit.append(
                adder.get_circuit(),
                list(self.register_c) +
                [self.register_x[i]] +
                list(self.register_r) +  # result register t
                list(self.register_anc[:self.m]) +  # result register t
                borrowable +
                list(self.register_g) +
                list(self.register_anc[self.m:])
            )

        # circuit.barrier()
        # Round of adders for Q-DIV component
        for k in reversed(range(0, self.m)):
            # Not perfectly the k from the paper, but the same meaning, (iterate in [0, m-1] and set corresponding circuit values)
            # TODO: Improvement? Use select-undo-adder from https://arxiv.org/pdf/1801.01081 Appendix A.2.
            # We can borrow n qubits from x and k the t part of m.
            k_inv = (self.m - k - 1)

            adder = CircuitChooser().choose_component(
                "QCAdderIP",
                (self.n + k + 1, (2 ** k) * self.p, self.c),
                dirty_available=self.dqa + self.n + k_inv,
                clean_available=self.cqa - self.m
            )
            borrowable = list(self.register_x) + list(self.register_anc[(self.m - k_inv):self.m])

            circuit.append(
                adder.get_circuit().reverse_ops(),
                list(self.register_c) +
                list(self.register_r) +  # result register t
                list(self.register_anc[:self.m - k_inv]) +  # result register t
                borrowable +
                list(self.register_g) +
                list(self.register_anc[self.m:])
            )

            adder_2 = CircuitChooser().choose_component(
                "QCAdderIP",
                (self.n + k, (2 ** k) * self.p, self.c + 1),
                dirty_available=self.dqa + self.n + k_inv,
                clean_available=self.cqa - self.m
            )

            borrowable = list(self.register_x) + list(self.register_anc[(self.m - k_inv):self.m])

            circuit.append(
                adder_2.get_circuit(),
                list(self.register_c) +
                [self.register_anc[self.m - k_inv - 1]] +
                list(self.register_r) +  # result register t
                list(self.register_anc[:(self.m - k_inv - 1)]) +  # result register t
                borrowable +
                list(self.register_g) +
                list(self.register_anc[self.m:])
            )

            if self.c > 0:
                circuit.mcx(self.register_c, self.register_anc[self.m - k_inv - 1])  # Apply the not after the control
            else:
                circuit.x(self.register_anc[self.m - k_inv - 1])

        # circuit.barrier()

        # In principle the result (|x * a mod p> is now stored in register_r and)
        # Now we need to do some uncomputation, which is unfortuantely the expensive part
        # This to simply correct the qubits in register_anc[:m] back to |0>

        # Multiply register register_anc[:m]  by p
        # Inline multiplication by p, I believe this is described in https://arxiv.org/pdf/1801.01081
        # However, I believe https://quantumcomputing.stackexchange.com/questions/26240/is-it-possible-to-turn-modular-multiplication-into-in-place-operation
        # is a better explanation
        for i in range(1, self.m):
            # Each adder has 2n qubits available to borrow (from register_x and register_r)
            # Additionally, we also have the (m - i - 1) qubits in register m.
            adder = CircuitChooser().choose_component(
                "QCAdderIP",
                (i, self.p >> 1, self.c + 1),
                dirty_available=self.dqa + self.n + self.n + (self.m - i - 1),
                # We can borrow from register_x and register_r
                clean_available=self.cqa - self.m
            )

            borrowable = list(self.register_r) + list(self.register_x) + list(self.register_anc[0:self.m - i - 1])

            circuit.append(
                adder.get_circuit(),
                list(self.register_c) +
                [self.register_anc[self.m - i - 1]] +
                list(self.register_anc[self.m - i:self.m]) +
                borrowable +
                list(self.register_g) +
                list(self.register_anc[self.m:])
            )

        # Now add the result back into this register
        # n qubits available to borrow from register_x
        qq_adder = CircuitChooser().choose_component(
            "QQAdderIP",
            (self.m, self.c, False, False),
            dirty_available=self.dqa + self.n,
            clean_available=self.cqa - self.m
        )

        borrowable = list(self.register_x)

        circuit.append(
            qq_adder.get_circuit(),
            list(self.register_c) +
            list(self.register_r[:self.m]) +  # first m LSBs
            list(self.register_anc[:self.m]) +
            borrowable +
            list(self.register_g) +
            list(self.register_anc[self.m:])
        )

        # TODO: Improve this using binary tree structure according to paper.
        # Not entirely sure, if that is even feasibly doable, since they don't even reference a paper to find the idea in.

        for i in range(0, self.n):
            # Each adder has n - 1 qubits available to borrow (from register_x)
            adder = CircuitChooser().choose_component(
                "QCAdderIP",
                (self.m, (self.a * (2 ** i)) % self.p, self.c + 1),
                dirty_available=self.dqa + 2 * self.n - 1,
                clean_available=self.cqa - self.m
            )

            borrowable = list(self.register_r) + list(self.register_x)
            borrowable.remove(self.register_x[i])

            circuit.append(
                adder.get_circuit().reverse_ops(),
                list(self.register_c) +
                [self.register_x[i]] +
                list(self.register_anc[:self.m]) +  # result register t
                borrowable +
                list(self.register_g) +
                list(self.register_anc[self.m:])
            )

        cache[self.identifier] = circuit

        return circuit
