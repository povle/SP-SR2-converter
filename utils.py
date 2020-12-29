import numpy as np
from transforms3d.euler import euler2mat, mat2euler


def parse_numstr(string: str):
    return [float(x) for x in string.split(',')]


def create_numstr(floats: list):
    return ','.join([str(round(x, 8)) for x in floats])


ROT = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])
def rotate(angles: list):
    angles = [n * np.pi/180 for n in angles]
    M = euler2mat(*[angles[n] for n in (2, 0, 1)], 'szxy')
    angles = mat2euler(np.matmul(M, ROT), 'szxy')
    angles = [angles[n] * 180/np.pi for n in (1, 2, 0)]
    return angles
