import qiskit.result
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator

caches = set()


def register_cache(cache: dict):
    caches.add(cache)


def execute_circuit(circuit: QuantumCircuit, shots=1024) -> qiskit.result.Result:
    simulator = AerSimulator(method='statevector')
    # Allow circuit to run on our backend.

    circuit = generate_preset_pass_manager(backend=simulator, optimization_level=3).run(circuit)

    job = simulator.run(circuit, shots=shots)

    return job.result()


# Helper function to get the last 1 in the binary representation of n
def index_last_1(n):
    binary_str = bin(n)[2:]

    return (len(binary_str) - binary_str.rfind('1') - 1) if '1' in binary_str else 0



# Adapted from https://www.youtube.com/watch?v=lOTw8d9tIvc
# I am nearly sure there is a better way to do this
def num_non_idle_qubits(qc: QuantumCircuit):
    gate_count = { qubit: False for qubit in qc.qubits }
    for gate in qc.data:
        for qubit in gate.qubits:
            gate_count[qubit] = True
    return list(gate_count.values()).count(True)