import math

from scipy.special import binom


# TODO: Remove these permutations by finding a direct equation for the coefficients.
# Example:
# $$C(a_m) = (2^m)^{p-2}$$
# $$C(a_m,a_n) = (2^n + 2^m)^{p-2} - (2^n)^{p-2} - (2^m)^{p-2}, \textrm{with } m < n$$
# Expand to C(a_l, a_m, a_n) ??
def to_sum_k(n, k) -> []:
    cache = {}

    def to_sum_k_inner(n, k):
        res = cache.get((n, k), [])
        if res:
            return res

        if n == 1:
            res = [[k]]
        elif n > k or n <= 0:
            res = []
        else:
            for i in range(k):
                sub_results = to_sum_k_inner(n - 1, k - i)
                for sub in sub_results:
                    res.append(sub + [i])
        cache[(n, k)] = res
        return res

    return to_sum_k_inner(n, k)


# TODO: Remove these permutations by finding a direct equation for the coefficients.
def get_permutations_for_length(sum, num_integers, num_zeros=0) -> []:
    result = []
    for k in to_sum_k(num_integers, sum):
        if k.count(0) == num_zeros:
            result.append(k)
    return result


# Inefficient first variant
# def multinomial(n : int, k : []):
#     if sum(k) != n:
#         raise ValueError("sum of k must be equal to n")
#     prd = 1
#     for j in k:
#         prd *= math.factorial(j)
#     return math.factorial(n) // prd

# Based on the decomposition using binomial theorem
# TODO: Improve by using modular arithmetic. Pretty sure we can take advantage of factorials to know when a binom is zero.
def multinomial(params) -> int:
    if len(params) == 1:
        return 1
    return binom(sum(params), params[-1]) * multinomial(params[:-1])


def powerset(s) -> []:
    x = len(s)
    ps = []
    for i in range(1, 1 << x):
        ps.append([s[j] for j in range(x) if (i & (1 << j))])
    return ps


def get_coeffs(p: int, remove_larger_subsets=False) -> {}:
    coeffs = {}
    powset = powerset(list(range(0, math.ceil(math.log2(p)))))

    for subset in powset:
        # We know that the input will always be in the range [0, p], and so we do not need to handle cases with input >= p
        if remove_larger_subsets and (sum([2 ** place for place in subset]) >= p):
            continue
        coeff = 0
        for permutation in get_permutations_for_length(p - 2, len(subset)):
            temp = multinomial(permutation) % p
            for a, b in zip(subset, permutation):
                temp = (temp * (1 << (a * b))) % p  # Resubstitution b_1 = 2*a_1, b_2 = 4*a_2, b_3 = 8*a_3, etc.
            coeff = (coeff + temp) % p
        coeffs[tuple(sorted(subset))] = int(coeff)
    return coeffs
