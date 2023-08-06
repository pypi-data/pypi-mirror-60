import numpy as np
import mvr

if __name__ == '__main__':
    A = np.ndarray((2, 2), dtype=int)

    A[0, 0] = 1
    A[1, 0] = 0
    A[0, 1] = 1
    A[1, 1] = 2

    r = mvr.rank_matrix(A, burn_in=1, samples=2, sample_spacing=3, repetitions=1)
