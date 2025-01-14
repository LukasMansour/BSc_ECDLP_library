from qiskit import QuantumCircuit, generate_preset_pass_manager
from qiskit_aer import AerSimulator

backend = AerSimulator()

pass_manager = generate_preset_pass_manager(
    optimization_level=3,
    basis_gates=['rx', 'ry', 'rz', 'cz'],  # Universal gate-set: rotational.
    # approximation_degree=0.99, # Uncomment for approximation.
    backend=backend,
)

# # from https://quantumcomputing.stackexchange.com/questions/25672/remove-inactive-qubits-from-qiskit-circuit
# def remove_idle_wires(circ : QuantumCircuit):
#     dag = circuit_to_dag(circ)
#
#     idle_wires = list(dag.idle_wires())
#     for w in idle_wires:
#         dag.qubits.remove(w)
#
#     print(dag_to_circuit(dag))
#     return dag_to_circuit(dag)

def auto_opt(circuit: QuantumCircuit) -> QuantumCircuit:
    circuit = pass_manager.run(circuit)
    return circuit

# Too bad performance to use in resource analysis :(
# pass_manager_2 = generate_preset_pass_manager(
#     optimization_level=3,
#     basis_gates=['u1', 'u2', 'u3', 'cx'],  # Universal gate-set 1,2 and 3-qubit unitaries + CX
#     # approximation_degree=0.99, # Uncomment for approximation.
#     backend=AerSimulator()
# )
# def remove_cl_operations(circuit : QuantumCircuit) -> QuantumCircuit:
#     if len(circuit.clbits) > 0:
#         circuit_copy = circuit.copy()
#         for idx, _instruction in reversed(list(enumerate(circuit_copy.data))):
#             for _clbit in _instruction.clbits:
#                     del circuit_copy.data[idx]
#         return circuit_copy
#     return circuit
#
# def auto_opt_solovay_kitaev(circuit: QuantumCircuit) -> QuantumCircuit:
#     circuit = remove_cl_operations(circuit)
#     # This would be a good set of basis gates for a SK decomposition.
#     # giving it too little gates will make this take unbearably long.
#     basis = ["x", "y", "z", "s", "sdg", "t", "tdg", "h"]
#     approx = generate_basic_approximations(basis, depth=3)
#     skd = SolovayKitaev(recursion_degree=3, basic_approximations=approx)
#     return skd(pass_manager_2.run(circuit))
