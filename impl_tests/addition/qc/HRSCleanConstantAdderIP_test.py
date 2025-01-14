import unittest
from random import Random

from qiskit import QuantumRegister, QuantumCircuit, ClassicalRegister

from api.CircuitChooser import CircuitChooser
from api.NameFilters import custom_name_filter
from impl.addition.qc.HRSCleanConstantAdderIP import HRSCleanConstantAdderIP
from impl.encoding.binary_encoding import binary_encoding
from impl_tests.testutil import execute_circuit, index_last_1


class HRSCleanConstantAdderTests(unittest.TestCase):
    def setUp(self):
        CircuitChooser().clear_caches()

    def test_addition_basic_incrementer(self):
        CircuitChooser()._name_filter = custom_name_filter({"BasicIncrementer"})
        n = 4
        for i in range(0, 10):
            # Init
            x_value = Random().randint(1, 2 ** n - 1)
            a_value = Random().randint(1, 2 ** n - 1)
            dirty_anc_available = 0
            clean_anc_available = 1

            # Circuit init
            register_x = QuantumRegister(n, 'x')
            register_g = QuantumRegister(dirty_anc_available, 'g')
            register_anc = QuantumRegister(clean_anc_available, 'anc')

            classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
            classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
            classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

            circuit = QuantumCircuit(register_x, register_g, register_anc,
                                     classical_register_x, classical_register_g, classical_register_anc)
            # Encoding
            circuit.append(binary_encoding(n, x_value), register_x)
            # Operation
            circuit.append(
                HRSCleanConstantAdderIP(
                    dirty_anc_available,
                    clean_anc_available,
                    n,
                    a_value,
                    0
                ).get_circuit(), list(register_x) + list(register_g) + list(register_anc))
            # Measurements
            circuit.measure(register_x, classical_register_x)
            circuit.measure(register_g, classical_register_g)
            circuit.measure(register_anc, classical_register_anc)

            counts = execute_circuit(circuit).get_counts()
            self.assertEqual(len(counts), 1)
            # extract x
            key_value = list(counts.items())[0]

            self.assertEqual(int(key_value[0].split(" ")[2], 2), (x_value + a_value) % (1 << n))
            self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
            self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
            self.assertEqual(key_value[1], 1024)

    def test_addition_gidney_incrementer(self):
        CircuitChooser()._name_filter = custom_name_filter({"GidneyIncrementer"})
        n = 4
        for i in range(0, 10):
            # Init
            x_value = Random().randint(1, 2 ** n - 1)
            a_value = Random().randint(1, 2 ** n - 1)
            dirty_anc_available = n - n // 2
            clean_anc_available = 1

            # Circuit init
            register_x = QuantumRegister(n, 'x')
            register_g = QuantumRegister(dirty_anc_available, 'g')
            register_anc = QuantumRegister(clean_anc_available, 'anc')

            classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
            classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
            classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

            circuit = QuantumCircuit(register_x, register_g, register_anc,
                                     classical_register_x, classical_register_g, classical_register_anc)
            # Encoding
            circuit.append(binary_encoding(n, x_value), register_x)
            # Operation
            circuit.append(
                HRSCleanConstantAdderIP(
                    dirty_anc_available,
                    clean_anc_available,
                    n,
                    a_value,
                    0
                ).get_circuit(), list(register_x) + list(register_g) + list(register_anc))
            # Measurements
            circuit.measure(register_x, classical_register_x)
            circuit.measure(register_g, classical_register_g)
            circuit.measure(register_anc, classical_register_anc)

            counts = execute_circuit(circuit).get_counts()
            self.assertEqual(len(counts), 1)
            # extract x
            key_value = list(counts.items())[0]

            self.assertEqual(int(key_value[0].split(" ")[2], 2), (x_value + a_value) % (1 << n))
            self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
            self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
            self.assertEqual(key_value[1], 1024)

    def test_addition_hrs_incrementer(self):
        CircuitChooser()._name_filter = custom_name_filter({"HRSIncrementer"})
        n = 4
        for i in range(0, 10):
            # Init
            x_value = Random().randint(1, 2 ** n - 1)
            a_value = Random().randint(1, 2 ** n - 1)
            dirty_anc_available = max(n - index_last_1(a_value) - n // 2,
                                      0)  # here we start to see why this incrementer is so powerful.
            clean_anc_available = 1

            # Circuit init
            register_x = QuantumRegister(n, 'x')
            register_g = QuantumRegister(dirty_anc_available, 'g')
            register_anc = QuantumRegister(clean_anc_available, 'anc')

            classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
            classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
            classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

            circuit = QuantumCircuit(register_x, register_g, register_anc,
                                     classical_register_x, classical_register_g, classical_register_anc)
            # Encoding
            circuit.append(binary_encoding(n, x_value), register_x)
            # Operation
            circuit.append(
                HRSCleanConstantAdderIP(
                    dirty_anc_available,
                    clean_anc_available,
                    n,
                    a_value,
                    0
                ).get_circuit(), list(register_x) + list(register_g) + list(register_anc))
            # Measurements
            circuit.measure(register_x, classical_register_x)
            circuit.measure(register_g, classical_register_g)
            circuit.measure(register_anc, classical_register_anc)

            counts = execute_circuit(circuit).get_counts()
            self.assertEqual(len(counts), 1)
            # extract x
            key_value = list(counts.items())[0]

            self.assertEqual(int(key_value[0].split(" ")[2], 2), (x_value + a_value) % (1 << n))
            self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
            self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
            self.assertEqual(key_value[1], 1024)

    def test_controlled_addition_basic_incrementer(self):
        CircuitChooser()._name_filter = custom_name_filter({"BasicIncrementer"})
        n = 4
        for i in range(0, 10):
            # Init
            c = Random().randint(1, 2)
            activate_control = Random().randint(0, 1) == 0
            x_value = Random().randint(1, 2 ** n - 1)
            a_value = Random().randint(1, 2 ** n - 1)
            dirty_anc_available = 0
            clean_anc_available = 1

            # Circuit init
            register_c = QuantumRegister(c, 'c')
            register_x = QuantumRegister(n, 'x')
            register_g = QuantumRegister(dirty_anc_available, 'g')
            register_anc = QuantumRegister(clean_anc_available, 'anc')

            classical_register_c = ClassicalRegister(len(register_c), 'cl_c')
            classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
            classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
            classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

            circuit = QuantumCircuit(register_c, register_x, register_g, register_anc,
                                     classical_register_c, classical_register_x, classical_register_g,
                                     classical_register_anc)
            # Encoding
            if activate_control:
                circuit.x(register_c)

            circuit.append(binary_encoding(n, x_value), register_x)
            # Operation
            circuit.append(
                HRSCleanConstantAdderIP(
                    dirty_anc_available,
                    clean_anc_available,
                    n,
                    a_value,
                    c
                ).get_circuit(), list(register_c) + list(register_x) + list(register_g) + list(register_anc))
            # Measurements
            circuit.measure(register_c, classical_register_c)
            circuit.measure(register_x, classical_register_x)
            circuit.measure(register_g, classical_register_g)
            circuit.measure(register_anc, classical_register_anc)

            counts = execute_circuit(circuit).get_counts()
            self.assertEqual(len(counts), 1)
            # extract x
            key_value = list(counts.items())[0]

            if activate_control:
                self.assertEqual(int(key_value[0].split(" ")[2], 2), (x_value + a_value) % (1 << n))
                self.assertEqual(key_value[0].split(" ")[3], "1" * c)
            else:
                self.assertEqual(int(key_value[0].split(" ")[2], 2), x_value)
                self.assertEqual(key_value[0].split(" ")[3], "0" * c)

            self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
            self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
            self.assertEqual(key_value[1], 1024)

    def test_controlled_addition_gidney_incrementer(self):
        CircuitChooser()._name_filter = custom_name_filter({"GidneyIncrementer"})
        n = 4
        for i in range(0, 10):
            # Init
            c = Random().randint(1, 2)
            activate_control = Random().randint(0, 1) == 0
            x_value = Random().randint(1, 2 ** n - 1)
            a_value = Random().randint(1, 2 ** n - 1)
            dirty_anc_available = max(n - n // 2 - c, 0)
            clean_anc_available = 1

            # Circuit init
            register_c = QuantumRegister(c, 'c')
            register_x = QuantumRegister(n, 'x')
            register_g = QuantumRegister(dirty_anc_available, 'g')
            register_anc = QuantumRegister(clean_anc_available, 'anc')

            classical_register_c = ClassicalRegister(len(register_c), 'cl_c')
            classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
            classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
            classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

            circuit = QuantumCircuit(register_c, register_x, register_g, register_anc,
                                     classical_register_c, classical_register_x, classical_register_g,
                                     classical_register_anc)
            # Encoding
            if activate_control:
                circuit.x(register_c)

            circuit.append(binary_encoding(n, x_value), register_x)
            # Operation
            circuit.append(
                HRSCleanConstantAdderIP(
                    dirty_anc_available,
                    clean_anc_available,
                    n,
                    a_value,
                    c
                ).get_circuit(), list(register_c) + list(register_x) + list(register_g) + list(register_anc))
            # Measurements
            circuit.measure(register_c, classical_register_c)
            circuit.measure(register_x, classical_register_x)
            circuit.measure(register_g, classical_register_g)
            circuit.measure(register_anc, classical_register_anc)

            counts = execute_circuit(circuit).get_counts()
            self.assertEqual(len(counts), 1)
            # extract x
            key_value = list(counts.items())[0]

            if activate_control:
                self.assertEqual(int(key_value[0].split(" ")[2], 2), (x_value + a_value) % (1 << n))
                self.assertEqual(key_value[0].split(" ")[3], "1" * c)
            else:
                self.assertEqual(int(key_value[0].split(" ")[2], 2), x_value)
                self.assertEqual(key_value[0].split(" ")[3], "0" * c)

            self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
            self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
            self.assertEqual(key_value[1], 1024)

    def test_controlled_addition_hrs_incrementer(self):
        CircuitChooser()._name_filter = custom_name_filter({"HRSIncrementer"})
        n = 5
        for i in range(0, 10):
            # Init
            c = Random().randint(1, 2)
            activate_control = Random().randint(0, 1) == 0
            x_value = Random().randint(1, 2 ** n - 1)
            a_value = Random().randint(1, 2 ** n - 1)
            dirty_anc_available = max(n - index_last_1(a_value) - n // 2 - c, 0)
            clean_anc_available = 1

            # Circuit init
            register_c = QuantumRegister(c, 'c')
            register_x = QuantumRegister(n, 'x')
            register_g = QuantumRegister(dirty_anc_available, 'g')
            register_anc = QuantumRegister(clean_anc_available, 'anc')

            classical_register_c = ClassicalRegister(len(register_c), 'cl_c')
            classical_register_x = ClassicalRegister(len(register_x), 'cl_x')
            classical_register_g = ClassicalRegister(len(register_g), 'cl_g')
            classical_register_anc = ClassicalRegister(len(register_anc), 'cl_anc')

            circuit = QuantumCircuit(register_c, register_x, register_g, register_anc,
                                     classical_register_c, classical_register_x, classical_register_g,
                                     classical_register_anc)
            # Encoding
            if activate_control:
                circuit.x(register_c)

            circuit.append(binary_encoding(n, x_value), register_x)
            # Operation
            circuit.append(
                HRSCleanConstantAdderIP(
                    dirty_anc_available,
                    clean_anc_available,
                    n,
                    a_value,
                    c
                ).get_circuit(), list(register_c) + list(register_x) + list(register_g) + list(register_anc))
            # Measurements
            circuit.measure(register_c, classical_register_c)
            circuit.measure(register_x, classical_register_x)
            circuit.measure(register_g, classical_register_g)
            circuit.measure(register_anc, classical_register_anc)

            counts = execute_circuit(circuit).get_counts()
            self.assertEqual(len(counts), 1)
            # extract x
            key_value = list(counts.items())[0]

            if activate_control:
                self.assertEqual(int(key_value[0].split(" ")[2], 2), (x_value + a_value) % (1 << n))
                self.assertEqual(key_value[0].split(" ")[3], "1" * c)
            else:
                self.assertEqual(int(key_value[0].split(" ")[2], 2), x_value)
                self.assertEqual(key_value[0].split(" ")[3], "0" * c)

            self.assertEqual(key_value[0].split(" ")[1], "0" * len(register_g))
            self.assertEqual(key_value[0].split(" ")[0], "0" * len(register_anc))
            self.assertEqual(key_value[1], 1024)


if __name__ == '__main__':
    unittest.main()
