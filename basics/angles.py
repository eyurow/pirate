import numpy as np

def normalize_angle(angle):
    # Normalized angle to pi:-pi range
    _abs = abs(angle)
    sign = int(_abs / angle)
    revolutions = _abs//np.pi
    remaining = _abs%np.pi
    norm = (-sign * np.pi * (revolutions%2)) + sign * remaining
    return norm

def clockwise_distance(a1, a2):
    if a1 > np.pi or a1 <= -np.pi:
        a1 = normalize_angle(a1)
    if a2 > a1:
        return a1 - (a2 - np.pi*2)
    else:
        return a1 - a2