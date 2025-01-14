import json
import os
import sys
from random import Random

from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from quaspy.math.groups import PointOnShortWeierstrassCurveOverPrimeField, ShortWeierstrassCurveOverPrimeField
from quaspy.orderfinding.general.postprocessing.ekera import solve_j_for_r
from quaspy.logarithmfinding.general.postprocessing import solve_j_k_for_d_given_r

sys.path.insert(0, "../../")

from api.CircuitChooser import CircuitChooser
from api.Metrics import gate_count_metric
from impl.classical_ec.elliptic_curves import point_doubling, get_curve
from impl.shors.Shors_ECDLP import shors_ecdlp

shots = 2000
n = int(sys.argv[1])  # Number of bits.
seed = int(sys.argv[2])  # Seed

if len(sys.argv) >= 4:
    results_directory = sys.argv[3]
else:
    results_directory = f"./largest_instance_ecdlp/"

if not os.path.exists(results_directory):
    os.makedirs(results_directory)

filename = f"{results_directory}/{n}.json"

if os.path.exists(filename):
    print("Terminating due to already existing output file.")
    sys.exit(0)

random = Random(seed)

instance_file = f"../ecgen_instances/curves_{n}.json"

with open(instance_file) as f:
    curve = json.load(f)[0]

elliptic_curve = get_curve(int(curve["a"], 16), int(curve["b"], 16), int(curve["field"]["p"], 16))
p = elliptic_curve.modulus
P = (int(curve["subgroups"][0]["x"], 16), int(curve["subgroups"][0]["y"], 16))
# Random m between 2 and the point order (exclusive), so that we get a point Q.
Q = point_doubling(elliptic_curve, P, random.randint(2, int(curve["order"], 16) - 1))

points = []
# Classically generate the points [P, 2P, 4P, ... , 2^n*P]
for i in range(0, n + 1):
    points.append(point_doubling(elliptic_curve, P, 2 ** i))
# And then generate the points [Q, 2Q, ... 2^n*Q]
for j in range(0, n + 1):
    points.append(point_doubling(elliptic_curve, Q, 2 ** j))

simulator = AerSimulator()

CircuitChooser()._metric = gate_count_metric
circuit = generate_preset_pass_manager(backend=simulator, optimization_level=3).run(shors_ecdlp(points, p))

# Allow circuit to run on our backend.
job = simulator.run(circuit, shots=shots)

counts = job.result().get_counts()

r = 2 * p + 2  # Backup frequency if all else fails, should be more or else similar to Hasse's bound (probably wrong)

found_order = False
for (j, _) in counts.items():
    r_cand = solve_j_for_r(
        j,
        n + 1,
        n + 1,
        PointOnShortWeierstrassCurveOverPrimeField(
            P[0],
            P[1],
            E=ShortWeierstrassCurveOverPrimeField(elliptic_curve.a,
                                                  elliptic_curve.b,
                                                  elliptic_curve.modulus)
        )
    )
    if r_cand is not None:
        found_order = True
        r = min(r, r_cand)

result_list = list()
for result in counts.keys():
    # split result measurements
    m_stage1 = int(result[:n // 2], 2)
    m_stage2 = int(result[n // 2:], 2)

    result_list.append((m_stage1, m_stage2, counts[result]))

num_correct = 0
num_wrong = 0
m = -1

quaspy_curve = ShortWeierstrassCurveOverPrimeField(elliptic_curve.a, elliptic_curve.b, elliptic_curve.modulus)

for (j, k, freq) in result_list:
    m_cand = solve_j_k_for_d_given_r(j, k, n + 1, 0, n + 1,
                                     PointOnShortWeierstrassCurveOverPrimeField(P[0], P[1], E=quaspy_curve),
                                     PointOnShortWeierstrassCurveOverPrimeField(Q[0], Q[1], E=quaspy_curve), r)

    if m_cand is not None and (point_doubling(elliptic_curve, P, m_cand)) == Q:
        if m != -1:
            m = min(m, int(m_cand))
        else:
            m = int(m_cand)
        num_correct += freq
    else:
        num_wrong += freq

m_correct = point_doubling(elliptic_curve, P, m) == Q
order_correct = int(curve["order"], 16) == r

data = {
    "n": n,
    "instance": {
        "p": p,
        "a": elliptic_curve.a,
        "b": elliptic_curve.b,
        "P": P,
        "Q": Q,
    },
    "counts": dict(counts),
    "order": int(r),
    "order_correct": order_correct,
    "found_order": found_order,
    "ecdlp_results": {
        "num_correct": num_correct,
        "num_wrong": num_wrong,
        "m_correct": m_correct,
        "m": int(m)
    }
}

with open(filename, "w") as outfile:
    json.dump(data, outfile)

print(f"Saved to {filename}")

