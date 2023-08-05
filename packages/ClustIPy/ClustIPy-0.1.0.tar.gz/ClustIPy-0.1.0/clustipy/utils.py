from hilbertcurve.hilbertcurve import HilbertCurve
import numpy as np


def hilbert_curve(p=12, n=2):
    hilbert_curve = HilbertCurve(p, n)
    coords = []
    i = 0
    while True:
        try:
            coords.append(hilbert_curve.coordinates_from_distance(i))
            i += 1
        except:
            break
    np.savez_compressed(f'hilvert_p{p}_n{n}.npz', np.array(coords))
