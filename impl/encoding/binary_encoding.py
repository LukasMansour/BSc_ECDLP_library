from qiskit import QuantumCircuit, QuantumRegister


def binary_encoding(n: int, value: int, big_endian: bool = False, c: int = 0) -> QuantumCircuit:
    required_qubits = value.bit_length()

    if required_qubits > n:
        raise ValueError(f"Required qubits to encode {value} is {required_qubits}, yet only {n} where provided.")

    q = QuantumRegister(n, 'q')
    circuit = QuantumCircuit(q, name=f'$|{bin(value)[2:].zfill(n)} \\rangle$')

    for i in range(0, required_qubits):
        if (value & 1) == 1:  # get the rightmost_bit
            if big_endian:
                circuit.x(q[n - 1 - i])  # use n here and not required_qubits!
            else:
                circuit.x(q[i])
        value >>= 1  # Shift bits to the right once (divide by 2)

    if c > 0:
        return circuit.control(c)
    else:
        return circuit
