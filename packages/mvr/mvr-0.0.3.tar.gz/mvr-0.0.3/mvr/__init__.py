name = "mvr_runner"

__version__ = '0.0.2'
__authors__ = 'Hunter Wapman; Aaron Clauset'

from numba import jit
import numpy as np
import copy


def rank_matrix(A, burn_in=10**6, samples=2000, sample_spacing=10000, repetitions=100):
    n = len(A)

    # the initial ranking is by out-degree
    initial_ranking = np.flip(np.sum(A, axis=1).argsort())

    ranking = np.zeros(n, dtype=int)
    for repetition in range(repetitions):
        repetition_ranking = run_mvr(
            A,
            copy.deepcopy(initial_ranking),
            burn_in,
            samples,
            sample_spacing
        )

        ranking = np.add(ranking, repetition_ranking)

    ranking = ranking / repetitions
    return ranking


def run_mvr(A, ranking, burn_in, samples, sample_spacing):
    n = len(A)

    step = 0
    max_steps = burn_in + (samples * sample_spacing)

    sampled_ranking = np.zeros(n, dtype=int)

    violation_count = get_violation_count(A, ranking)

    while step < max_steps:
        ranking, violation_count = take_step(A, ranking, violation_count)

        if step >= burn_in and not step % sample_spacing:
            sampled_ranking = np.add(sampled_ranking, ranking)

        step += 1

    sampled_ranking = sampled_ranking / samples
    return sampled_ranking


def take_step(A, ranking, old_violation_count):
    n = len(A)
    first, second = np.random.choice(n, 2, replace=False)

    ranking[first], ranking[second] = ranking[second], ranking[first]

    violation_count = get_violation_count(A, ranking)

    # undo the swap if it makes things worse
    if old_violation_count < violation_count:
        ranking[first], ranking[second] = ranking[second], ranking[first]
        violation_count = old_violation_count

    return ranking, violation_count


@jit(nopython=True)
def get_violation_count(A, ranking):
    count = 0
    n = len(ranking)
    for i in range(n):
        for j in range(n):
            if 0 < A[i, j] and ranking[i] < ranking[j]:
                count += A[i, j]

    return count
