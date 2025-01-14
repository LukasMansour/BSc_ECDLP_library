import math
import unittest
from random import Random

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister

from api.CircuitChooser import CircuitChooser
from api.NameFilters import custom_name_filter
from impl.encoding.binary_encoding import binary_encoding
from impl.exponentiation.qc.modular.HRSConstantModExpIP import HRSConstantModExpIP
from impl_tests.testutil import execute_circuit


class HRSConstantModExpIPTests(unittest.TestCase):

    def test_modular_exponentiation(self):
        CircuitChooser()._name_filter = custom_name_filter(
            {"TTKAdderIP", "HRSIncrementer", "HRSConstantAdderIP",
             "RNSLModularNegationIP", "HRSConstantModularAdderIP", "RNSLModularAdderIP",
             "RNSLModularDoublerIP", "RNSLModularSquaringOOP", "HRSConstantModularMultiplierIP",
             "HRSConstantModularMultiplierOOP", "HRSComparator", "FullSubtractionComparator"
             }
        )
        for p in [7, 11, 13]:
            n = math.ceil(math.log2(p))
            for i in range(0, 3):
                # Init
                x_value = Random().randint(0, p - 1)
                y_value = Random().randint(1, p - 1)
                dirty_anc_available = 0
                clean_anc_available = n + 1

                constant_modexp = HRSConstantModExpIP(
                    dirty_anc_available,
                    clean_anc_available,
                    n,
                    y_value,
                    p,
                    0
                )

                # Circuit init
                register_x = QuantumRegister(n, 'x')
                register_y = QuantumRegister(n, 'y')
                register_g = QuantumRegister(dirty_anc_available, 'g')
                register_anc = QuantumRegister(clean_anc_available, 'anc')

                classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
                classical_register_y = ClassicalRegister(len(register_y), 'cl_y')
                classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
                classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

                circuit = QuantumCircuit(register_x, register_y, register_g, register_anc,
                                         classical_register_x, classical_register_y, classical_register_g,
                                         classical_register_anc)
                # Encoding
                circuit.append(binary_encoding(n, x_value), register_x)
                # Encode y as 1, or else y * a^x mod p will always be 0
                circuit.append(binary_encoding(n, 1), register_y)
                # Operation
                circuit.append(
                    constant_modexp.get_circuit(),
                    list(register_x) +
                    list(register_y) +
                    list(register_g) +
                    list(register_anc)
                )
                # Measurements
                circuit.measure(register_x, classical_register_x)
                circuit.measure(register_y, classical_register_y)
                circuit.measure(register_g, classical_register_g)
                circuit.measure(register_anc, classical_register_anc)

                counts = execute_circuit(circuit).get_counts()
                self.assertEqual(len(counts), 1)
                # extract x
                key_value = list(counts.items())[0]

                self.assertEqual(int(key_value[0].split(" ")[3], 2), x_value)
                self.assertEqual(int(key_value[0].split(" ")[2], 2), (y_value ** x_value) % p)
                self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
                self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
                self.assertEqual(key_value[1], 1024)


if __name__ == '__main__':
    unittest.main()
