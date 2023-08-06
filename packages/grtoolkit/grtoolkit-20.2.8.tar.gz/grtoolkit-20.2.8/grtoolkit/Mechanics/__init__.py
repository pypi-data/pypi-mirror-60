import math
# from math import radians, degrees
# import scipy.constants
# from sympy import diff
# from grtoolkit.Python import dictionary_add_modify

# from sympy import *
# from grtoolkit.Math import *
from grtoolkit.Math import solveEqs, printEquations, algebraSolve

import grtoolkit.Mechanics.CircularMotion
import grtoolkit.Mechanics.Kinematics
import grtoolkit.Mechanics.ProjectileMotion
import grtoolkit.Mechanics.Pulleys

def magnitude(*args):
    for arg in args:
        square_sum += arg**2
    return math.sqrt(square_sum)
     

def forceEq(find, **kwargs):
    """variables: f=force, m=mass, a=acceleration"""
    return algebraSolve("Eq(f,m*a)", find, **kwargs)

if __name__ == "__main__":
    pass


