import math
import unittest

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister

from api.CircuitChooser import CircuitChooser
from api.NameFilters import custom_name_filter
from impl.ec_point_addition.qc.RNSLECPointAdderIP import RNSLECPointAdderIP
from impl.encoding.binary_encoding import binary_encoding
from impl_tests.testutil import execute_circuit


class RNSLECPointAdderIPTests(unittest.TestCase):

    def test_ec_addition(self):
        CircuitChooser()._name_filter = custom_name_filter(
            {"TTKAdderIP", "HRSIncrementer", "BasicConstantAdderIP",
             "RNSLModularNegationIP", "HRSConstantModularAdderIP", "RNSLModularAdderIP",
             "RNSLModularDoublerIP", "RNSLModularSquaringOOP", "HRSConstantModularMultiplierIP",
             "HRSConstantModularMultiplierOOP", "FermatModularInversion", "PZModularMultiplierOOP",
             "HRSComparator", "FullSubtractionComparator"
             }
        )
        # Choose an elliptic curve e.g: (x^3 + 3) mod 7.
        p = 7
        A = 0
        B = 3
        n = math.ceil(math.log2(p))
        dirty_anc_available = 0
        clean_anc_available = 2 * n + 2

        # (1,5) + (6,3) = (1,2)
        # (1,5) + (2,2) = (6,3)
        # (1,5) + (2,5) = (4,2)
        points = [(6, 3), (2, 2), (2, 5)]
        results = [(1, 2), (6, 3), (4, 2)]
        for index, point in enumerate(points):
            ec_point_adder = RNSLECPointAdderIP(
                dirty_anc_available,
                clean_anc_available,
                n,
                point,
                p,
                0
            )
            register_x = QuantumRegister(n, 'x')  # x-coordinate of the point
            register_y = QuantumRegister(n, 'y')  # y-coordinate of the point
            # for debugging purposes we split the ancilla register
            register_t = QuantumRegister(n, 't')
            register_lambda = QuantumRegister(n, '\\lambda')
            # Use the lambda qubits as borrowed qubits.
            register_anc = QuantumRegister(clean_anc_available - 2 * n, 'anc')  # Clean Ancilla

            classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
            classical_register_y = ClassicalRegister(len(register_y), 'cl_y')
            classical_register_t = ClassicalRegister(len(register_t), 'cl_t')
            classical_register_lambda = ClassicalRegister(len(register_lambda), 'cl_lambda')
            classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

            circuit = QuantumCircuit(register_x, register_y, register_t, register_lambda, register_anc,
                                     classical_register_x, classical_register_y, classical_register_t,
                                     classical_register_lambda, classical_register_anc)
            circuit.append(binary_encoding(n, 1), list(register_x))
            circuit.append(binary_encoding(n, 5), list(register_y))
            circuit.append(ec_point_adder.get_circuit()
                           , list(register_x) + list(register_y) + list(register_t) + list(register_lambda) + list(
                    register_anc))

            circuit.measure(register_x, classical_register_x)
            circuit.measure(register_y, classical_register_y)
            circuit.measure(register_t, classical_register_t)
            circuit.measure(register_lambda, classical_register_lambda)
            circuit.measure(register_anc, classical_register_anc)

            counts = execute_circuit(circuit).get_counts()
            self.assertEqual(len(counts), 1)
            # extract x
            key_value = list(counts.items())[0]

            self.assertEqual(int(key_value[0].split(" ")[4], 2), results[index][0])
            self.assertEqual(int(key_value[0].split(" ")[3], 2), results[index][1])
            self.assertEqual(key_value[0].split(" ")[2], "0" * len(register_t))
            self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_lambda))
            self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
            self.assertEqual(key_value[1], 1024)


if __name__ == '__main__':
    unittest.main()
