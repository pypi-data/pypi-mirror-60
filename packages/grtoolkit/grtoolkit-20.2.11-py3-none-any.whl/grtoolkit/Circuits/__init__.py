import grtoolkit.Circuits.Filters

from grtoolkit.Math import solveEqs

def ohmsLaw(find, printEq=False, **kwargs):
    """variables: 
                V=voltage       (V)
                I=current       (A)
                R=resistance    (ohm) 
                P=power         (W)"""
    eq = list()
    eq.append("Eq(V,I*R)")    
    eq.append("Eq(P,V*I)")
    return solveEqs(eq, find, printEq=printEq, **kwargs)

def currentDC(find="I", printEq=False, **kwargs):
    """variables: 
                I=current
                Q=charge
                t, t0, t1 = time initial/final"""
    eq = list()
    eq.append("Eq(I,Q/t)")    
    eq.append("Eq(Q,integrate(i,[t,t0,t1]))")
    return solveEqs(eq, find, printEq=printEq, **kwargs)

# currentDC(t1=2,t0=1)