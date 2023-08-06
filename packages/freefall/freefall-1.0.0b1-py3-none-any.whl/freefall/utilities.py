"""
utilities.py

A collection of utility functions to support simulations.
"""

import math


def find_vx_vy(*, speed, angle):
    rads = math.radians(angle)
    vx = speed * math.cos(rads)
    vy = speed * math.sin(rads)
    return vx, vy


# This function is from the article Generate Floating Point Range in Python
# by Meenakshi Agarwal
def float_range(A, L=None, D=None):
    """float_range(stop) -> float_range object
    float_range(start, stop[, step]) -> float range object

    Return an object that produces a sequence of floating point numbers from 
    start (inclusive) to stop (exclusive) by step.  float_range(i, j) produces 
    i, i+1, i+2, ..., j-1.  start defaults to 0, and stop is omitted!  
    float_range(4) produces 0, 1, 2, 3.  These are exactly the valid indices for a 
    list of 4 elements.  When step is given, it specifies the increment (or 
    decrement).
    """
    if L == None:
        L = A + 0.0
        A = 0.0
    if D == None:
        D = 1.0
    while True:
        if D > 0 and A >= L:
            break
        elif D < 0 and A <= L:
            break
        yield A
        A = A + D
