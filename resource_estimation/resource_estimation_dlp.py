import json
import os
import sys
import time
from random import Random
import math

import sympy


sys.path.insert(0, "../")

from api.CircuitChooser import CircuitChooser
from api.Metrics import gate_count_metric, gate_depth_metric, cz_count_metric, cz_depth_metric, \
    gate_count_metric_circuit, cz_count_metric_circuit, gate_depth_metric_circuit, \
    cz_depth_metric_circuit  # , t_count_metric_circuit, t_depth_metric_circuit
from impl.shors.Shors_DLP import shors_dlp
from impl_tests.testutil import num_non_idle_qubits

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

width = sys.argv[4] # 'high', 'medium' or 'low'

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

# all the n-bit primes
primes_n_bit = list(sympy.primerange(2 ** (n - 1) + 1, 2 ** n))

# Generate 5 different instances.
while len(instances) < num_instances:
    rand_prime = primes_n_bit[random.randint(0, len(primes_n_bit) - 1)]
    g = random.randint(2, rand_prime - 1)
    b = random.randint(2, rand_prime - 1)
    while g == b:
        b = random.randint(2, rand_prime - 1)
    instances.add((g, b, rand_prime))

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
for g, b, p in instances:
    print(f"Starting resource estimate: [{choice_metric_key}: {g},{b},{p}]")
    CircuitChooser()._metric = choice_metrics[choice_metric_key]
    if width == 'low':
        circuit = shors_dlp(g, b, p, extra_qubits=0) # low width
    elif width == 'medium':
        circuit = shors_dlp(g, b, p, extra_qubits=math.ceil(math.log2(p))) # medium width
    elif width == 'high':
        circuit = shors_dlp(g, b, p, extra_qubits=5*math.ceil(math.log2(p))) # high width
    else:
        raise ValueError(f"Width '{width}' is not supported.")

    for key, eval_metric in eval_metrics.items():
        full_results[key].append(eval_metric(circuit))

    full_results["qubit_count"].append(num_non_idle_qubits(circuit))

total_time = time.time() - start_time

for key, eval_metric in eval_metrics.items():
    full_results[key + "_average"] = sum(full_results[key]) / len(full_results[key])

data = {
    "runtime_in_sec": total_time,
    "n": n,
    "instances": list(instances),
    "choice_metric": choice_metric_key,
    "results": full_results,
    "seed": seed,
    "num_instances": num_instances
}
with open(filename, "w") as outfile:
    json.dump(data, outfile)

print(f"Saved to {filename}")
