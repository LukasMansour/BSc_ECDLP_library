import unittest
from random import Random

from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit

from api.CircuitChooser import CircuitChooser
from impl.comparator.qc.HRSComparator import HRSComparator
from impl.encoding.binary_encoding import binary_encoding
from impl_tests.testutil import execute_circuit


class HRSComparatorTests(unittest.TestCase):

    def setUp(self):
        CircuitChooser().clear_caches()

    def test_comparison(self):
        n = 4
        for i in range(0, 10):
            # Init
            x_value = Random().randint(1, 2 ** n - 1)
            a_value = Random().randint(1, 2 ** n - 1)
            dirty_anc_available = n - 1
            clean_anc_available = 0

            # Circuit init
            register_x = QuantumRegister(n, 'x')
            register_r = QuantumRegister(1, 'r')
            register_g = QuantumRegister(dirty_anc_available, 'g')
            register_anc = QuantumRegister(clean_anc_available, 'anc')

            classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
            classical_register_r = ClassicalRegister(1, 'cl_r')
            classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
            classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

            circuit = QuantumCircuit(register_x, register_r, register_g, register_anc,
                                     classical_register_x, classical_register_r, classical_register_g,
                                     classical_register_anc)
            # Encoding
            circuit.append(binary_encoding(n, x_value), register_x)
            # Operation
            circuit.append(HRSComparator(dirty_anc_available, clean_anc_available, n, a_value, 0).get_circuit(),
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

            self.assertEqual(int(key_value[0].split(" ")[3], 2), x_value)
            if x_value < a_value:
                self.assertEqual(key_value[0].split(" ")[2], "1")
            else:
                self.assertEqual(key_value[0].split(" ")[2], "0")

            self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
            self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
            self.assertEqual(key_value[1], 1024)
