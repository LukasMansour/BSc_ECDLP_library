import math
import unittest
from random import Random

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister

from api.CircuitChooser import CircuitChooser
from api.NameFilters import custom_name_filter
from impl.encoding.binary_encoding import binary_encoding
from impl.multiplication.qc.modular.HRSConstantModularMultiplierOOP import HRSConstantModularMultiplierOOP
from impl_tests.testutil import execute_circuit


class HRSConstantModularMultiplierOOPTests(unittest.TestCase):

    def setUp(self):
        CircuitChooser().clear_caches()

    def test_constant_modular_multiplication(self):
        CircuitChooser()._name_filter = custom_name_filter(
            {"TTKAdderIP", "BasicIncrementer", "BasicConstantAdderIP",
             "RNSLModularNegationIP", "HRSConstantModularAdderIP", "RNSLModularAdderIP",
             "RNSLModularDoublerIP", "RNSLModularSquaringOOP", "HRSConstantModularMultiplierIP",
             "HRSConstantModularMultiplierOOP", "HRSComparator", "FullSubtractionComparator"
             }
        )
        for p in [7, 9, 13]:
            n = math.ceil(math.log2(p))
            for i in range(0, 5):
                # Init
                x_value = Random().randint(0, p - 1)
                a_value = Random().randint(0, p - 1)
                dirty_anc_available = 0
                clean_anc_available = 2

                constant_mod_adder = HRSConstantModularMultiplierOOP(
                    dirty_anc_available,
                    clean_anc_available,
                    n,
                    a_value,
                    p,
                    0
                )

                # Circuit init
                register_x = QuantumRegister(n, 'x')
                register_r = QuantumRegister(n, 'r')
                register_g = QuantumRegister(dirty_anc_available, 'g')
                register_anc = QuantumRegister(clean_anc_available, 'anc')

                classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
                classical_register_r = ClassicalRegister(len(register_r), 'cl_r')
                classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
                classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

                circuit = QuantumCircuit(register_x, register_r, register_g, register_anc,
                                         classical_register_x, classical_register_r, classical_register_g,
                                         classical_register_anc)
                # Encoding
                circuit.append(binary_encoding(n, x_value), register_x)
                # Operation
                circuit.append(constant_mod_adder.get_circuit(),
                               list(register_x) + list(register_r) + list(register_g) + list(register_anc))
                # Measurements
                circuit.measure(register_x, classical_register_x)
                circuit.measure(register_r, classical_register_r)
                circuit.measure(register_g, classical_register_g)
                circuit.measure(register_anc, classical_register_anc)

                counts = execute_circuit(circuit).get_counts()

                self.assertEqual(len(counts), 1)
                # extract x
                key_value = list(counts.items())[0]

                self.assertEqual(int(key_value[0].split(" ")[2], 2), (x_value * a_value) % p)
                self.assertEqual(int(key_value[0].split(" ")[3], 2), x_value)

                self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
                self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
                self.assertEqual(key_value[1], 1024)

    def test_controlled_constant_modular_multiplication(self):
        CircuitChooser()._name_filter = custom_name_filter(
            {"TTKAdderIP", "BasicIncrementer", "BasicConstantAdderIP",
             "RNSLModularNegationIP", "HRSConstantModularAdderIP", "RNSLModularAdderIP",
             "RNSLModularDoublerIP", "RNSLModularSquaringOOP", "HRSConstantModularMultiplierIP",
             "HRSConstantModularMultiplierOOP", "HRSComparator", "FullSubtractionComparator"
             }
        )
        for p in [7, 9, 13]:
            n = math.ceil(math.log2(p))
            for i in range(0, 5):
                # Init
                c = Random().randint(1, 2)
                activate_control = Random().randint(0, 1) == 0
                x_value = Random().randint(0, p - 1)
                a_value = Random().randint(0, p - 1)
                dirty_anc_available = 0
                clean_anc_available = 2

                constant_mod_adder = HRSConstantModularMultiplierOOP(
                    dirty_anc_available,
                    clean_anc_available,
                    n,
                    a_value,
                    p,
                    c
                )

                # Circuit init
                register_c = QuantumRegister(c, 'c')
                register_x = QuantumRegister(n, 'x')
                register_r = QuantumRegister(n, 'r')
                register_g = QuantumRegister(dirty_anc_available, 'g')
                register_anc = QuantumRegister(clean_anc_available, 'anc')

                classical_register_c = ClassicalRegister(len(register_c), 'cl_c')
                classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
                classical_register_r = ClassicalRegister(len(register_x), 'cl_r')
                classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
                classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

                circuit = QuantumCircuit(register_c, register_x, register_r, register_g, register_anc,
                                         classical_register_c, classical_register_x, classical_register_r,
                                         classical_register_g, classical_register_anc)
                # Encoding
                if activate_control:
                    circuit.x(register_c)
                circuit.append(binary_encoding(n, x_value), register_x)
                # Operation
                circuit.append(constant_mod_adder.get_circuit(), list(register_c) +
                               list(register_x) + list(register_r) + list(register_g) + list(register_anc))
                # Measurements
                circuit.measure(register_c, classical_register_c)
                circuit.measure(register_x, classical_register_x)
                circuit.measure(register_r, classical_register_r)
                circuit.measure(register_g, classical_register_g)
                circuit.measure(register_anc, classical_register_anc)

                counts = execute_circuit(circuit).get_counts()
                self.assertEqual(len(counts), 1)
                # extract x
                key_value = list(counts.items())[0]

                self.assertEqual(int(key_value[0].split(" ")[3], 2), x_value)
                if activate_control:
                    self.assertEqual(int(key_value[0].split(" ")[2], 2), (x_value * a_value) % p)
                    self.assertEqual(key_value[0].split(" ")[4], "1" * c)
                else:
                    self.assertEqual(int(key_value[0].split(" ")[2], 2), 0)
                    self.assertEqual(key_value[0].split(" ")[4], "0" * c)

                self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
                self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
                self.assertEqual(key_value[1], 1024)


if __name__ == '__main__':
    unittest.main()
