from qiskit import QuantumCircuit

from api.CircuitChooser import CircuitChooser
from api.ec_point_addition.QuantumClassicalECPointAdderIP import QuantumClassicalECPointAdderIP


class RNSLECPointAdderIP(QuantumClassicalECPointAdderIP):
    """
    This class denotes an n-bit quantum-classical elliptic-curve point addition circuit.
    EC Point addition based on https://arxiv.org/pdf/1706.06752 (RNSL)

    It will apply the following unitary transformation: |x_1>|y_1>|0> --> |x_3>|y_3|0>.
    Where (x_1, y_1) + (x_2, y_2) = (x_3, y_3) according to elliptic curve addition.
    """

    def __init__(self,
                 dqa: int,
                 cqa: int,
                 n: int,
                 ec_point: (int, int),
                 p: int,
                 c: int = 0,
                 with_modular_inversion: bool = True):
        super().__init__(dqa, cqa, n, ec_point, p, c)
        self.with_modular_inversion = with_modular_inversion

    # noinspection PyUnboundLocalVariable
    def get_circuit(self) -> QuantumCircuit:
        cache = CircuitChooser().cache

        param_identifier = (self.identifier, self.with_modular_inversion)
        if cache.get(param_identifier, None) is not None:
            return cache[param_identifier]

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_y,
            self.register_g,
            self.register_anc,
            name=f"$+({self.ec_point[0]}, {self.ec_point[1]})$"
        )

        # Helper registers:
        register_t = self.register_anc[0:self.n]
        register_lambda = self.register_anc[self.n:2 * self.n]

        # -x_2
        # (n + 1 borrowable)
        qc_mod_adder_1 = CircuitChooser().choose_component(
            "QCModAdderIP",
            (self.n, self.ec_point[0], self.p, 0),
            dirty_available=self.dqa + self.n + self.c,
            clean_available=self.cqa
        )

        borrowable = list(self.register_y) + list(self.register_c)

        circuit.append(
            qc_mod_adder_1.get_circuit().reverse_ops(),
            list(self.register_x) +
            list(self.register_g) +  # Improve parallelism: choose register_g first, only use y if necessary.
            borrowable +
            list(self.register_anc)
        )

        # -y_2
        # Adders for y_2 (n borrowable)
        qc_mod_adder_2 = CircuitChooser().choose_component(
            "QCModAdderIP",
            (self.n, self.ec_point[1], self.p, self.c),
            dirty_available=self.dqa + self.n,
            clean_available=self.cqa
        )

        borrowable = list(self.register_x)

        circuit.append(
            qc_mod_adder_2.get_circuit().reverse_ops(),
            list(self.register_c) +
            list(self.register_y) +
            list(reversed(list(
                self.register_g))) +  # Improve parallelism: choose the last bits of g, so -x_2 can choose the first bits of g.
            borrowable +
            list(self.register_anc)
        )

        if self.with_modular_inversion:
            # Modular inverter (n+1 borrowable, n less clean)
            qc_mod_inverter_1 = CircuitChooser().choose_component(
                "QQModInversionOOP",
                (self.n, self.p, 0),
                dirty_available=self.dqa + self.n + self.c,
                clean_available=self.cqa - self.n  # n used now to store result.
            )

            borrowable = list(self.register_y) + list(self.register_c)

            circuit.append(
                qc_mod_inverter_1.get_circuit(),
                list(self.register_x) +
                list(register_t) +
                list(self.register_g) +
                borrowable +
                list(self.register_anc[self.n:])
            )
        # Quantum Quantum multiplication y*t --> lambda
        # n + 1 borrowable, n less clean
        qq_mod_multiplier_1 = CircuitChooser().choose_component(
            "QQModMulOOP",
            (self.n, self.p, 0),
            dirty_available=self.dqa + self.n + self.c,
            clean_available=self.cqa - 2 * self.n
        )

        borrowable = list(self.register_x) + list(self.register_c)

        circuit.append(
            qq_mod_multiplier_1.get_circuit(),
            list(self.register_y) +
            list(register_t) +
            list(register_lambda) +
            list(self.register_g) +
            borrowable +
            list(self.register_anc[2 * self.n:])
        )

        borrowable = list(register_t) + list(self.register_c)

        circuit.append(
            qq_mod_multiplier_1.get_circuit().reverse_ops(),
            list(register_lambda) +
            list(self.register_x) +
            list(self.register_y) +
            list(self.register_g) +
            borrowable +
            list(self.register_anc[2 * self.n:])
        )

        # Modular inversion, again stored into register t
        if self.with_modular_inversion:
            qc_mod_inverter_2 = CircuitChooser().choose_component(
                "QQModInversionOOP",
                (self.n, self.p, 0),
                dirty_available=self.dqa + 2 * self.n + self.c,
                clean_available=self.cqa - 2 * self.n
            )

            borrowable = list(self.register_y) + list(self.register_c) + list(register_lambda)

            circuit.append(
                qc_mod_inverter_2.get_circuit().reverse_ops(),
                list(self.register_x) +
                list(register_t) +
                list(self.register_g) +
                borrowable +
                list(self.register_anc[2 * self.n:])
            )

        # Modular Squaring lambda into t
        # Quantum-Quantum squarer (2n + 1 borrowable, 0 clean)
        qq_mod_sqr_1 = CircuitChooser().choose_component(
            "QCModSquaringOOP",
            (self.n, self.p, 0),
            dirty_available=self.dqa + 2 * self.n + self.c,
            clean_available=self.cqa - 2 * self.n
        )
        borrowable = list(self.register_y) + list(self.register_x) + list(self.register_c)

        circuit.append(
            qq_mod_sqr_1.get_circuit(),
            list(register_lambda) +
            list(register_t) +
            list(self.register_g) +
            borrowable +
            list(self.register_anc[2 * self.n:])
        )

        # x - t
        # Quantum-Quantum Adder (subtraction) (2n borrowable, 0 clean)
        qq_mod_adder_1 = CircuitChooser().choose_component(
            "QQModAdderIP",
            (self.n, self.p, self.c),
            dirty_available=self.dqa + 2 * self.n,
            clean_available=self.cqa - 2 * self.n
        )

        borrowable = list(self.register_y) + list(register_lambda)

        circuit.append(
            qq_mod_adder_1.get_circuit().reverse_ops(),
            list(self.register_c) +
            list(register_t) +
            list(self.register_x) +
            list(self.register_g) +
            borrowable +
            list(self.register_anc[2 * self.n:])
        )

        # +3x_2
        # Adders for 3x_2 (3n borrowable, 0 clean)
        qc_mod_adder_3 = CircuitChooser().choose_component(
            "QCModAdderIP",
            (self.n, (3 * self.ec_point[0]) % self.p, self.p, self.c),
            dirty_available=self.dqa + 3 * self.n,
            clean_available=self.cqa - 2 * self.n
        )

        borrowable = list(self.register_y) + list(register_t) + list(register_lambda)

        circuit.append(
            qc_mod_adder_3.get_circuit(),
            list(self.register_c) +
            list(self.register_x) +
            list(self.register_g) +
            borrowable +
            list(self.register_anc[2 * self.n:])
        )

        # Modular Squaring lambda into t

        borrowable = list(self.register_y) + list(self.register_c) + list(self.register_x)

        circuit.append(
            qq_mod_sqr_1.get_circuit().reverse_ops(),
            list(register_lambda) +
            list(register_t) +
            list(self.register_g) +
            borrowable +
            list(self.register_anc[2 * self.n:])
        )

        # Quantum Quantum multiplication x*lambda --> y
        borrowable = list(register_t) + list(self.register_c)

        circuit.append(
            qq_mod_multiplier_1.get_circuit(),
            list(register_lambda) +
            list(self.register_x) +
            list(self.register_y) +
            list(self.register_g) +
            borrowable +
            list(self.register_anc[2 * self.n:])
        )

        # Modular inversion, again stored into register t
        if self.with_modular_inversion:
            borrowable = list(self.register_y) + list(self.register_c) + list(register_lambda)

            circuit.append(
                qc_mod_inverter_2.get_circuit(),
                list(self.register_x) +
                list(register_t) +
                list(self.register_g) +
                borrowable +
                list(self.register_anc[2 * self.n:])
            )

        # Quantum Quantum multiplication y*t --> lambda
        borrowable = list(self.register_x) + list(self.register_c)

        circuit.append(
            qq_mod_multiplier_1.get_circuit().reverse_ops(),
            list(self.register_y) +
            list(register_t) +
            list(register_lambda) +
            list(self.register_g) +
            borrowable +
            list(self.register_anc[2 * self.n:])
        )
        if self.with_modular_inversion:
            borrowable = list(self.register_y) + list(self.register_c)

            circuit.append(
                qc_mod_inverter_1.get_circuit().reverse_ops(),
                list(self.register_x) +
                list(register_t) +
                list(self.register_g) +
                borrowable +
                list(self.register_anc[self.n:])
            )

        # Modular negation
        # (n borrowable, 2n clean)
        qc_mod_neg_1 = CircuitChooser().choose_component(
            "QCModularNegationIP",
            (self.n, self.p, self.c),
            dirty_available=self.dqa + self.n,
            clean_available=self.cqa
        )

        borrowable = list(self.register_y)

        circuit.append(
            qc_mod_neg_1.get_circuit(),
            list(self.register_c) +
            list(self.register_x) +
            list(self.register_g) +
            list(borrowable) +
            list(self.register_anc)
        )
        # +x_2
        borrowable = list(self.register_y) + list(self.register_c)

        circuit.append(
            qc_mod_adder_1.get_circuit(),
            list(self.register_x) +
            list(self.register_g) +  # Improve parallelism: choose register_g first, only use y if necessary.
            borrowable +
            list(self.register_anc)
        )
        # -y_2
        borrowable = list(self.register_x)

        circuit.append(
            qc_mod_adder_2.get_circuit().reverse_ops(),
            list(self.register_c) +
            list(self.register_y) +
            list(reversed(list(
                self.register_g))) +  # Improve parallelism: choose the last bits of g, so -x_2 can choose the first bits of g.
            borrowable +
            list(self.register_anc)
        )

        cache[param_identifier] = circuit

        return circuit
