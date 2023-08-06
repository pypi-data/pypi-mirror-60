# CONNECT LIBRARIES
import grtoolkit.Mechanics.CircularMotion
import grtoolkit.Mechanics.Friction
import grtoolkit.Mechanics.Kinematics
import grtoolkit.Mechanics.ProjectileMotion
import grtoolkit.Mechanics.Pulleys

# EASY ACCESS
import math, scipy.constants
from grtoolkit.Math import algebraSolve, solveEqs

def magnitude(*args):
    square_sum = 0
    for arg in args:
        square_sum += arg**2
    return math.sqrt(square_sum)
     

def forceEq(find, **kwargs):
    """variables: f=force, m=mass, a=acceleration"""
    return algebraSolve("Eq(f,m*a)", find, **kwargs)

def weight(mass,gravity):
    return mass*gravity

def kineticEnergy(mass,velocity):
    """1 J = 1 N*m = 1 Kg*m**2/s**2"""
    return 0.5*mass*velocity**2

def workEnergy(find, printEq=False, **kwargs):
    """variables: 
                W=Work  f=force
                x, x0, x1 = distance, start, finish"""
    eq = list()
    eq.append("Eq(W, f*x)")
    eq.append("Eq(W,integrate(F,(x,x0,x1)))")
    eq.append("Eq(W, P*t)")
    return solveEqs(eq, find, printEq=printEq, **kwargs)

def power(find, printEq=False, **kwargs):
    """variables: 
                P=power  W=Work  t=time
                f=force  v=velocity
        Base Unit = Watts"""
    eq = list()
    eq.append("Eq(P, W/t)")
    eq.append("Eq(P, F*v)")
    return solveEqs(eq, find, printEq=printEq, **kwargs)

if __name__ == "__main__":
    pass
    power("P", printEq=True, W=400, t=60*4)
