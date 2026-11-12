"""Small exact statistics for §3.4: sign test, Holm, nearest rank, lag-1 autocorrelation, Clopper-Pearson."""
import math


def sign_test(base_ae, model_ae):
    """One-sided exact sign test that the model's AE is lower. Ties drop.

    Returns (wins, losses, ties, p) with p = sum_{k=w}^{n} C(n, k) / 2^n."""
    wins = sum(1 for b, m in zip(base_ae, model_ae) if m < b)
    losses = sum(1 for b, m in zip(base_ae, model_ae) if m > b)
    ties = len(base_ae) - wins - losses
    n = wins + losses
    p = sum(math.comb(n, k) for k in range(wins, n + 1)) / 2 ** n if n else None
    return wins, losses, ties, p


def holm(ps, alpha=0.05):
    """Holm's step-down procedure: {key: rejected} for a dict of p-values."""
    order = sorted((k for k in ps if ps[k] is not None), key=lambda k: (ps[k], k))
    m = len(order)
    out = {k: False for k in ps}
    for i, k in enumerate(order):
        if ps[k] <= alpha / (m - i):
            out[k] = True
        else:
            break
    return out


def nearest_rank(xs, p):
    """Sorted ascending, the element at 1-based position ceil(p * n)."""
    s = sorted(xs)
    # p is the float 0.1 or 0.9, so p * n is computed in floating point. For every n this project meets (12 to
    # 39 past errors) the float product gives the same position as exact arithmetic: 0.1 * 30 is 3.0, position 3.
    return s[math.ceil(p * len(s)) - 1] if s else None


def lag1(xs):
    """sum_{t=2}^{n} (x_t - m)(x_{t-1} - m) / sum_{t=1}^{n} (x_t - m)^2; None under three values."""
    n = len(xs)
    if n < 3:
        return None
    m = sum(xs) / n
    den = sum((x - m) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((xs[t] - m) * (xs[t - 1] - m) for t in range(1, n)) / den


def binom_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p)."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _solve(f, target, lo=0.0, hi=1.0):
    """Bisection for a decreasing f(p) = target on [lo, hi]."""
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided interval for a binomial proportion, as fractions."""
    # Upper end: P(X <= k | p) = alpha/2. Lower end: P(X >= k | p) = alpha/2, which is
    # P(n - X <= n - k | 1 - p) = alpha/2, solved for 1 - p.
    hi = 1.0 if k == n else _solve(lambda p: binom_cdf(k, n, p), alpha / 2)
    lo = 0.0 if k == 0 else 1 - _solve(lambda q: binom_cdf(n - k, n, q), alpha / 2)
    return lo, hi
