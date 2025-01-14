import json
import math
import os
import sys
from random import Random

import sympy
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from quaspy.math.groups import IntegerModRingMulSubgroupElement
from quaspy.orderfinding.general.postprocessing.ekera import solve_j_for_r
from quaspy.logarithmfinding.general.postprocessing import solve_j_k_for_d_given_r
from quaspy.orderfinding.general.postprocessing.ekera import solve_j_for_r_mod_N

sys.path.insert(0, "../../")

from api.CircuitChooser import CircuitChooser
from api.Metrics import gate_count_metric
from impl.shors.Shors_DLP import shors_dlp

shots = 2000
n = int(sys.argv[1])  # Number of bits.
seed = int(sys.argv[2])  # Seed

if len(sys.argv) >= 4:
    results_directory = sys.argv[3]
else:
    results_directory = f"./largest_instance_dlp/"

if not os.path.exists(results_directory):
    os.makedirs(results_directory)

filename = f"{results_directory}/{n}.json"

if os.path.exists(filename):
    print("Terminating due to already existing output file.")
    sys.exit(0)

random = Random(seed)

# all the n-bit primes
primes_n_bit = list(sympy.primerange(2 ** (n - 1) + 1, 2 ** n))
p = primes_n_bit[random.randint(0, len(primes_n_bit) - 1)]
g = random.randint(2, p - 1)
b = g**random.randint(2, p - 1) % p # Ensure b exists, by doing in this way.

simulator = AerSimulator()
CircuitChooser()._metric = gate_count_metric
circuit = generate_preset_pass_manager(backend=simulator, optimization_level=3).run(shors_dlp(g, b, p))
# run circuit
job = simulator.run(circuit, shots=shots)

counts = job.result().get_counts()


n = math.ceil(math.log2(p))

r = p - 1  # Backup frequency if all else fails, is always p - 1
found_period = False
for (j, _) in counts.items():
    r_cand = solve_j_for_r(j, n, n, IntegerModRingMulSubgroupElement(g, p))

    if r_cand is not None:
        found_period = True
        r = min(r, r_cand)

result_list = list()
for result in counts.keys():
    # split result measurements
    result_s = result.split(" ")
    m_stage1 = int(result_s[1], 2)
    m_stage2 = int(result_s[0], 2)

    result_list.append((m_stage1, m_stage2, counts[result]))


num_correct = 0
num_wrong = 0
x = -1

for (j, k, freq) in result_list:
    # Issue: https://github.com/ekera/quaspy/issues/2
    if b == 1:
        x_cand = solve_j_for_r_mod_N(j, n, 0, g, p)
    else:
        x_cand = solve_j_k_for_d_given_r(j, k, n, 0, n, IntegerModRingMulSubgroupElement(g, p),
                                         IntegerModRingMulSubgroupElement(b, p), r)

    if x_cand is not None and ((g ** x_cand) % p) == b:
        if x != -1:
            x = min(x, int(x_cand))
        else:
            x = int(x_cand)
        num_correct += freq
    else:
        num_wrong += freq

is_correct = ((g ** x) % p) == b

data = {
    "n": n,
    "instance": {
        "g": g,
        "b": b,
        "p": p
    },
    "counts": dict(counts),
    "period": int(r),
    "found_period": found_period,
    "dlp_results": {
        "num_correct": num_correct,
        "num_wrong": num_wrong,
        "is_correct": is_correct,
        "x": int(x)
    }
}

with open(filename, "w") as outfile:
    json.dump(data, outfile)

print(f"Saved to {filename}")
