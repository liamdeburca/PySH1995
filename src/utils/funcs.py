"""
Random functions.
"""

RYDBERG_H: float = 1.09678e-3

def calculateWave(
    n1: int, 
    n2: int,
    z: int = 1,
) -> float:
    """
    Calculates the emitted wavelength for a specific transition.
    """
    if n1 > n2: return calculateWave(n2, n1)
    return (z**2 * RYDBERG_H * (1 / n1**2 - 1 / n2**2))**-1