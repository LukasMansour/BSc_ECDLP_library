import math
from dataclasses import dataclass
from typing import Callable

import libnum


@dataclass
class EllipticCurve:
    curve_function: Callable[[int], int]
    curve_derivative: Callable[[int], int]
    a: int
    b: int
    modulus: int

    def __hash__(self):
        return hash((self.a, self.b, self.modulus))

    def __str__(self):
        return f"(a={self.a}, b={self.b}, modulus={self.modulus})"


def get_curve(a: int, b: int, modulus: int) -> EllipticCurve:
    """
    Returns the elliptic curve function (y^2 = x^3 + a*x + b)

    :param a: The a-parameter of the elliptic curve.
    :param b: The b-parameter of the elliptic curve.
    :param modulus: The modulus of the elliptic curve.
    :return: (curve_func, curve_derivative_func, a, b, modulus)
    """

    def curve_function(x) -> int:
        return ((x ** 3) + a * x + b) % modulus

    def curve_derivative(x) -> int:
        return (3 * (x ** 2) + a) % modulus

    return EllipticCurve(curve_function, curve_derivative, a, b, modulus)


def get_curve_points(curve: EllipticCurve, number_of_points: int) -> [(int, int)]:
    """
    Exponential time algorithm to get
    :param curve: An EllipticCurve parameter instance.
    :return: A list of points on the curve according to the number of points requested.
    """

    points = []
    for x in range(0, min(number_of_points, curve.modulus)):
        if libnum.has_sqrtmod_prime_power(curve.curve_function(x), curve.modulus):
            square_roots = libnum.sqrtmod_prime_power(curve.curve_function(x), curve.modulus)
            # we might have two solutions for sr in square_roots:
            for sr in square_roots:
                points.append((x, sr))
    return points


def point_self_addition(curve: EllipticCurve, point: (int, int)) -> (int, int):
    """
    Adds a point to itself on the curve. (Also known as 'point doubling').

    :param curve: An EllipticCurve parameter instance.
    :param point: The point to double
    :return: The new point on the curve after self addition_in_place.
    """
    x, y = point
    # If it is the point at infinite
    if x is None and y is None:
        return None, None

    # Make sure it is on the curve
    assert curve.curve_function(x) == (y ** 2) % curve.modulus, f"({x}, {y}) not on curve."

    # from math_utils import modinv
    # tangent_slope = ((curve.curve_derivative(x)) * modinv(2 * y, curve.modulus)) % curve.modulus
    tangent_slope = ((curve.curve_derivative(x)) * pow(2 * y, -1, curve.modulus)) % curve.modulus
    new_x = (tangent_slope ** 2 - 2 * x) % curve.modulus
    new_y = (tangent_slope * (x - new_x) - y) % curve.modulus
    return new_x, new_y


def point_addition(curve: EllipticCurve, p: (int, int), q: (int, int)) -> (int, int):
    xp, yp = p
    xq, yq = q

    if xq == yq and yq is None:
        return xp, yp
    if xp == yp and yp is None:
        return xq, yq

    assert curve.curve_function(xq) == (yq ** 2) % curve.modulus, "q not on curve"
    assert curve.curve_function(xp) == (yp ** 2) % curve.modulus, "p not on curve"

    if xq == xp and yq == yp:
        return point_self_addition(curve, p)
    elif xq == xp:
        return None, None  # Return the point at Infinity

    slope = ((yq - yp) * pow((xq - xp), -1, curve.modulus)) % curve.modulus
    xr = (slope ** 2 - xp - xq) % curve.modulus
    yr = (slope * (xp - xr) - yp) % curve.modulus
    return xr, yr


def point_doubling(curve: EllipticCurve, p: (int, int), m: int):
    if m == 1:
        return p

    res = (None, None)  # Point at Infinity
    temp = p  # track doubled P val
    while m > 0:
        bit = m & 1
        if bit == 1:
            res = point_addition(curve, res, temp)  # point add
        temp = point_self_addition(curve, temp)  # point double (temp = 2*temp)
        m >>= 1  # Shift to the right by 1.
    return res


def point_negation(curve: EllipticCurve, p: (int, int)) -> (int, int):
    xp, yp = p

    if (xp is None) and (yp is None):
        return None, None

    return xp, curve.modulus - yp


def all_powers(curve: EllipticCurve, m: int, generator: (int, int)) -> [(int, int)]:
    current_point = generator
    result = [current_point]

    for i in range(0, math.ceil(math.log2(m))):
        current_point = point_self_addition(curve, current_point)
        result.append(current_point)
    return result
