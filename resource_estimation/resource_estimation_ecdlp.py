import json
import math
import os
import sys
import time
from random import Random

sys.path.insert(0, "../")

from api.CircuitChooser import CircuitChooser
from api.Metrics import gate_count_metric, gate_depth_metric, cz_count_metric, cz_depth_metric, \
    gate_count_metric_circuit, cz_count_metric_circuit, gate_depth_metric_circuit, \
    cz_depth_metric_circuit  # , t_count_metric_circuit, t_depth_metric_circuit
from impl.shors.Shors_ECDLP import shors_ecdlp
from impl_tests.testutil import num_non_idle_qubits
from impl.classical_ec.elliptic_curves import point_doubling, get_curve

num_instances = 2

choice_metrics = {
    "gate_count": gate_count_metric,
    "gate_depth": gate_depth_metric,
    "cz_count": cz_count_metric,
    "cz_depth": cz_depth_metric,
}
eval_metrics = {
    "gate_count": gate_count_metric_circuit,
    "gate_depth": gate_depth_metric_circuit,
    "cz_count": cz_count_metric_circuit,
    "cz_depth": cz_depth_metric_circuit,
    # "t_count": t_count_metric_circuit,
    # "t_depth": t_depth_metric_circuit,
}
n = int(sys.argv[1])  # Number of bits.
choice_metric_key = sys.argv[2]  # metric
# gate_count
# gate_depth
# cz_count
# cz_depth
seed = int(sys.argv[3])  # Seed

width = sys.argv[4]  # 'high', 'medium' or 'low'

if len(sys.argv) >= 6:
    results_directory = sys.argv[5]
else:
    results_directory = f"./{width}_width/"

if not os.path.exists(results_directory):
    os.makedirs(results_directory)

filename = f"{results_directory}/{choice_metric_key}_{n}.json"

if os.path.exists(filename):
    print("Terminating due to already existing output file.")
    sys.exit(0)

random = Random(seed)

instances = set()

instance_file = f"./ecgen_instances/curves_{n}.json"

with open(instance_file) as f:
    curves = json.load(f)

for curve in curves:
    elliptic_curve = get_curve(int(curve["a"], 16), int(curve["b"], 16), int(curve["field"]["p"], 16))
    P = (int(curve["subgroups"][0]["x"], 16), int(curve["subgroups"][0]["y"], 16))
    # Random m between 2 and the point order (exclusive), so that we get a point Q.
    Q = point_doubling(elliptic_curve, P, random.randint(2, int(curve["order"], 16) - 1))
    instances.add((elliptic_curve,P, Q))

full_results = {
    "gate_count": [],
    "gate_depth": [],
    "cz_count": [],
    "cz_depth": [],
    # "t_count": [],
    # "t_depth": [],
    "qubit_count": []
}

start_time = time.time()
for elliptic_curve, P, Q in instances:
    print(f"Starting resource estimate for curve: [{choice_metric_key}: {elliptic_curve},{P},{Q}]")

    points = []
    # Classically generate the points [P, 2P, 4P, ... , 2^n*P]
    for i in range(0, n + 1):
        points.append(point_doubling(elliptic_curve, P, 2 ** i))
    # And then generate the points [Q, 2Q, ... 2^n*Q]
    for j in range(0, n + 1):
        points.append(point_doubling(elliptic_curve, Q, 2 ** j))

    CircuitChooser()._metric = choice_metrics[choice_metric_key]

    p = elliptic_curve.modulus

    # with_modular_inversion=False to set modular inversion to O(1)
    if width == 'low':
        circuit = shors_ecdlp(points, p, with_modular_inversion=False, extra_qubits=0)  # low width
    elif width == 'medium':
        circuit = shors_ecdlp(points, p, with_modular_inversion=False, extra_qubits=math.ceil(math.log2(p)))  # medium width
    elif width == 'high':
        circuit = shors_ecdlp(points, p, with_modular_inversion=False, extra_qubits=5 * math.ceil(math.log2(p)))  # high width
    else:
        raise ValueError(f"Width '{width}' is not supported.")

    for key, eval_metric in eval_metrics.items():
        full_results[key].append(eval_metric(circuit))

    full_results["qubit_count"].append(num_non_idle_qubits(circuit))

total_time = time.time() - start_time

for key, eval_metric in eval_metrics.items():
    full_results[key + "_average"] = sum(full_results[key]) / len(full_results[key])

# make instances serializable:
serialized_instances = []
for instance in instances:
    serialized_instances.append((str(instance[0]), instance[1], instance[2]))

data = {
    "runtime_in_sec": total_time,
    "n": n,
    "instances": serialized_instances,
    "choice_metric": choice_metric_key,
    "results": full_results,
    "seed": seed,
    "num_instances": num_instances
}
with open(filename, "w") as outfile:
    json.dump(data, outfile)

print(f"Saved to {filename}")
