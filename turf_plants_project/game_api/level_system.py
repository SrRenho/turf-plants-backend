import math

# Quadratic coefficients for XP per level
A = 0.8517
B = 4.1483
C = 0.0  # optional offset, we set XP(0)=0


def xp_for_level(n: int) -> float:
    """XP required to go from level n -> n+1"""
    return A * n ** 2 + B * n + C


def total_xp_to_level(n: int) -> float:
    """Total cumulative XP required to reach level n"""
    # sum_{k=1}^{n-1} (A k^2 + B k) = A*(n-1)*n*(2n-1)/6 + B*(n-1)*n/2
    if n <= 1:
        return 0.0
    return A * (n - 1) * n * (2 * (n - 1) + 1) / 6 + B * (n - 1) * n / 2


def xp_progress(xp: float):
    """
    Given total XP, return:
      - current level (1–100)
      - XP already into current level
      - XP remaining until next level
    """
    if xp <= 0:
        return 1, 0.0, xp_for_level(1)

    # solve quadratic sum formula for level
    # sum_{k=1}^{n-1} (A k^2 + B k) <= xp
    # approximate level using inverse of quadratic formula for sum of squares + linear
    # we do numeric approximation (O(1) closed form is messy), so we can use math.sqrt and linear approx

    # Using approximate formula: total_xp ≈ (A/3) n^3 + (B/2) n^2
    # Solve (A/3) n^3 + (B/2) n^2 - xp = 0  -> cubic
    # We'll use simple approximation: n ≈ ((3 * xp) / A) ** (1/3) for large n ignoring B, then adjust
    n_approx = ((3 * xp) / A) ** (1 / 3)
    n = max(1, int(math.floor(n_approx)))

    # refine n downward if cumulative sum exceeds xp
    while total_xp_to_level(n + 1) <= xp and n < 100:
        n += 1
    while total_xp_to_level(n) > xp and n > 1:
        n -= 1

    level = min(n, 100)
    spent = total_xp_to_level(level)
    into_level = xp - spent
    if level >= 100:
        return 100, max(0.0, into_level), 0.0

    cost = xp_for_level(level)
    return level, max(0.0, into_level), cost

