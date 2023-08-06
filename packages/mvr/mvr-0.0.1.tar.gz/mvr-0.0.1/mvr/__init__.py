name = "mvr_runner"

__version__ = '0.0.1'
__authors__ = 'Hunter Wapman; Aaron Clauset'

from numba import jit
import numpy as np
import copy


def rank_matrix(A, burn_in=10**6, samples=2000, sample_spacing=10000, repetitions=100):
    n = len(A)

    # the initial ranking is by out-degree
    initial_ranking = np.flip(np.sum(A, axis=1).argsort())

    repetition_rankings = np.zeros((repetitions, n), dtype=int)
    for repetition in range(repetitions):
        repetition_rankings[repetition] = run_mvr(
            A,
            copy.deepcopy(initial_ranking),
            burn_in,
            samples,
            sample_spacing
        )

    return get_averaged_ranking(repetition_rankings)


def run_mvr(A, ranking, burn_in, samples, sample_spacing):
    n = len(A)

    step = 0
    max_steps = burn_in + (samples * sample_spacing)

    sample_number = 0
    sampled_rankings = np.zeros((samples, n), dtype=int)

    violation_count = get_violation_count(A, ranking)

    while step < max_steps:
        ranking, n_violations = take_step(A, ranking, violation_count)

        if step >= burn_in and not step % sample_spacing:
            sampled_rankings[sample_number] = ranking
            sample_number += 1

        step += 1

    return get_averaged_ranking(sampled_rankings)


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
def get_averaged_ranking(rankings):
    return rankings.sum(axis=0) / len(rankings)


@jit(nopython=True)
def get_violation_count(A, ranking):
    count = 0
    n = len(ranking)
    for i in range(n):
        for j in range(n):
            if 0 < A[i, j] and ranking[i] < ranking[j]:
                count += A[i, j]

    return count
