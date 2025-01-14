import numpy as np
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit import Gate

from api.CircuitChooser import CircuitChooser
from api.addition.QuantumClassicalAdderIP import QuantumClassicalAdderIP


class HRSConstantAdderIP(QuantumClassicalAdderIP):
    """
    Constant addition circuit by Häner, Roetteler and Svore (https://arxiv.org/pdf/1611.07995 , Fig. 5)
    """

    def __init__(self, dqa: int, cqa: int, n: int, a: int, c: int = 0):
        super().__init__(dqa, cqa, n, a % (1 << n), c)

    def get_circuit(self, *args) -> QuantumCircuit:
        if self.n == 0 or self.a == 0:
            return QuantumCircuit(
                self.register_c,
                self.register_x,
                self.register_g,
                self.register_anc,
                name=f"[+{self.a}]_{{HD}}"
            )

        cache = CircuitChooser().cache

        if cache.get(self.identifier, None) is not None:
            return cache[self.identifier]

        # Length of the bit sections
        higher_bit_size = self.n >> 1
        lower_bit_size = ((self.n - 1) >> 1) + 1

        c_h = self.a >> lower_bit_size  # Constant to add on the higher bits
        c_l = self.a & ((1 << lower_bit_size) - 1)  # Constant to add on the lower bits

        circuit = QuantumCircuit(
            self.register_c,
            self.register_x,
            self.register_g,
            self.register_anc,
            name=f"[+{self.a}]_{{HD}}"
        )

        # Helper registers
        register_x_l = list(self.register_x[0:lower_bit_size])
        register_x_h = list(self.register_x[lower_bit_size:lower_bit_size + higher_bit_size])

        register_main_anc = (list(self.register_g) + list(self.register_anc))[0]
        if register_main_anc in self.register_anc:
            register_g = self.register_g
            register_anc = self.register_anc[1:]
        else:
            register_g = self.register_g[1:]
            register_anc = self.register_anc

        # Get bit representation of a.
        a_bits = [int(i) for i in np.binary_repr(self.a, self.n)[::-1]]

        # Here we start a recursive step, basically splitting the circuit into a higher and lower part recursively
        # Handle the recursive end cases (n == 2 and n == 1):
        if self.n == 2:
            if a_bits[0] == 1:
                circuit.mcx(list(self.register_c) + [register_x_l[0]], register_x_h[0])  # low + carry = high.
                circuit.mcx(list(self.register_c), register_x_l[0]) if self.c > 0 else circuit.x(register_x_l[0])
            if a_bits[1] == 1:
                circuit.mcx(list(self.register_c), register_x_h[0]) if self.c > 0 else circuit.x(register_x_h[0])

            return circuit

        # Recursive end case, one qubit left:
        elif self.n == 1:
            if a_bits[0] == 1:
                circuit.mcx(list(self.register_c), register_x_l[0]) if self.c > 0 else circuit.x(register_x_l[0])

            return circuit

        # Recursive main case:
        controlled_incrementer = CircuitChooser().choose_component(
            "QCIncrementer",
            (higher_bit_size, 0, 1),
            self.dqa + lower_bit_size - 1,  # We can borrow from x_l, but we are using one.
            self.cqa  # Number of clean qubits stays the same.
        )

        # + 1
        borrowable = list(register_x_l) + list(register_g)

        circuit.append(controlled_incrementer.get_circuit(),
                       [register_main_anc] + list(register_x_h) + borrowable + list(register_anc))

        circuit.cx([register_main_anc], register_x_h)
        # CARRY Gate
        circuit.append(carry_gate(lower_bit_size, c_l, self.c),
                       list(self.register_c) + list(register_x_l) + [register_main_anc] + list(
                           register_x_h[:lower_bit_size - 1]))
        # +1
        circuit.append(controlled_incrementer.get_circuit(),
                       list([register_main_anc]) + list(register_x_h) + borrowable + list(register_anc))
        # CARRY GATE
        circuit.append(carry_gate(lower_bit_size, c_l, self.c),
                       list(self.register_c) + list(register_x_l) + [register_main_anc] + list(
                           register_x_h[:lower_bit_size - 1]))

        circuit.cx([register_main_anc], register_x_h)

        low_add = HRSConstantAdderIP(self.dqa, self.cqa, lower_bit_size, c_l, self.c)

        circuit.append(low_add.get_circuit(),
                       list(self.register_c) + list(register_x_l) + list(self.register_g) + list(self.register_anc))

        high_add = HRSConstantAdderIP(self.dqa, self.cqa, higher_bit_size, c_h, self.c)

        # Attempt to parallelize by choosing from the last qubits

        circuit.append(high_add.get_circuit(),
                       list(self.register_c) +
                       list(register_x_h) +
                       list(
                           reversed(list(self.register_g))) +  # Attempt to parallelize by choosing from the last qubits
                       list(reversed(
                           list(self.register_anc))))  # Attempt to parallelize by choosing from the last qubits

        cache[self.identifier] = circuit

        return circuit


def carry_gate(n, a, c=0) -> Gate:
    """
    Calculates the carry of (y + p) and stores it on the qubit c.
    Requires n qubits to encode |x>
    Requires n - 1 dirty qubits
    Requires 1 qubit for the result of the carry.

    :param n: Number of qubits to encode |x>
    :param a: The constant_modular to add.
    :param c: Number of control qubits.
    :return:
    """
    register_c = QuantumRegister(c, 'c')
    register_a = QuantumRegister(n, 'a')
    register_g = QuantumRegister(n - 1, 'g')  # Use an optimization: register_g[0] = register_a[0]
    register_r = QuantumRegister(1, 'r')

    circuit = QuantumCircuit(register_c, register_a, register_r, register_g, name=rf"MSB(+{a})")

    if a < 0:
        # Remove the minus sign.
        p_bits = [int(i) for i in np.binary_repr(a, 1000)[::-1][:-1][:n]]
    else:
        p_bits = [int(i) for i in np.binary_repr(a, 1000)[::-1][:n]]
    ### Forward passthrough ###

    circuit.mcx(list(register_c) + [register_g[-1]], register_r[0])

    for i in range(n - 2, 0, -1):  # [n-2, 1]
        if p_bits[i + 1] == 1:
            circuit.cx(register_a[i + 1], register_g[i])
            circuit.x(register_a[i + 1])
        circuit.ccx(register_g[i - 1], register_a[i + 1], register_g[i])

    # Handle index (1) -- uppermost section
    if p_bits[0] == 0 and p_bits[1] == 1:
        circuit.cx(register_a[1], register_g[0])
        circuit.x(register_a[1])
        # no CCX part.
    elif p_bits[0] == 0 and p_bits[1] == 0:
        pass
    else:
        # Apply the CCX part
        if p_bits[1] == 1:
            circuit.cx(register_a[1], register_g[0])
            circuit.x(register_a[1])
        circuit.ccx(register_a[0], register_a[1], register_g[0])

    for i in range(1, n - 1):  # [2, n - 2]
        # in both cases c_i = 1 and c_i = 0, only the ccnot gate is controlled by g
        # therefore I only need to apply this again
        circuit.ccx(register_g[i - 1], register_a[i + 1], register_g[i])

    # Toggle g again before symmetry
    circuit.mcx(list(register_c) + [register_g[-1]], register_r[0])

    ### Backward passthrough ###
    for i in range(n - 2, 0, -1):  # [n-2, 1]
        circuit.ccx(register_g[i - 1], register_a[i + 1], register_g[i])

    # Handle index (1)
    if p_bits[0] == 0 and p_bits[1] == 1:
        circuit.x(register_a[1])
        circuit.cx(register_a[1], register_g[0])
        # no ccx part
    elif p_bits[0] == 0 and p_bits[1] == 0:
        pass
    else:
        # Apply the CCX part
        circuit.ccx(register_a[0], register_a[1], register_g[0])
        if p_bits[1] == 1:
            circuit.x(register_a[1])
            circuit.cx(register_a[1], register_g[0])

    for i in range(1, n - 1):  # [1, n-2]
        # Apply CCX part
        circuit.ccx(register_g[i - 1], register_a[i + 1], register_g[i])
        # Reverse conditional part
        if p_bits[i + 1] == 1:
            circuit.x(register_a[i + 1])
            circuit.cx(register_a[i + 1], register_g[i])

    return circuit.to_gate()
