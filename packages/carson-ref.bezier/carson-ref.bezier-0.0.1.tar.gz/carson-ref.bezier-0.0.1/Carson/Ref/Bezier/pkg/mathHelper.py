from functools import reduce


def _combination_decorator(fun):
    def job(*args):
        n, r = args
        assert n >= 0 and r >= 0, f'input parameters are not correct, n={n}, r={r}'
        if r > n:
            return 0
        return fun(*args)
    return job


@_combination_decorator
def ncr(n: int, r: int):
    """
    ncr(1, 0) = ncr(n, n) = 1
    ncr(n, r) = 0 for r > n
    """
    r = min(r, n - r)
    n_initial = 1
    numerator = reduce(lambda a, b: a * b, range(n, n - r, -1), n_initial)  # npr(n, r)
    denominator = reduce(lambda a, b: a * b, range(1, r + 1, 1), n_initial)
    return numerator / denominator
