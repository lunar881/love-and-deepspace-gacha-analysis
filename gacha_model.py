"""Love and Deepspace: how many pulls do different types of players need?

Rules (see README for sources):
  - 5-star rate = 1% up to pull 60, +10 percentage points per pull from pull 61, 100% at pull 70
  - Multi banner: 5 limited cards, 3 selected (25% each), 1 chosen as Precise Wish
  - After a miss, the next 5-star is guaranteed to be the target
  - Solo banner: 50/50, guarantee after a loss
The pity counter is not carried over in this single-banner version (start from zero).
"""
import random
import numpy as np
import matplotlib.pyplot as plt

BASE, SOFT_START, SOFT_STEP, HARD = 0.01, 61, 0.10, 70
COST = 150          # diamonds per pull
N = 200_000         # simulations per scenario
random.seed(1)

def chance(n):
    """Chance of a 5-star on pull number n since the last 5-star."""
    if n >= HARD: return 1.0
    if n >= SOFT_START: return min(1.0, BASE + SOFT_STEP * (n - SOFT_START + 1))
    return BASE

def wait_for_5star():
    n = 0
    while True:
        n += 1
        if random.random() < chance(n):
            return n

def pulls_until(p_first):
    """The first 5-star is acceptable with probability p_first;
    otherwise the second 5-star is guaranteed to be acceptable."""
    t = wait_for_5star()
    if random.random() < p_first:
        return t
    return t + wait_for_5star()

scenarios = {
    "Solo banner: featured card (50/50)": 0.50,
    "Multi, type A: one specific card": 0.25,
    "Multi, type B: either of two cards": 0.50,
    "Multi, type C: any of the three selected": 0.75,
}
data = {k: np.array([pulls_until(p) for _ in range(N)]) for k, p in scenarios.items()}

print(f"{'Scenario':45} {'mean':>5} {'P50':>4} {'P90':>4} {'P99':>4} {'<=70':>6} {'<=100':>6} {'<=140':>6}")
for k, a in data.items():
    print(f"{k:45} {a.mean():5.1f} {int(np.percentile(a,50)):4d} {int(np.percentile(a,90)):4d} {int(np.percentile(a,99)):4d} "
          f"{(a<=70).mean():6.1%} {(a<=100).mean():6.1%} {(a<=140).mean():6.1%}")
print("Diamonds (P50 / P90):", {k: (int(np.percentile(a,50))*COST, int(np.percentile(a,90))*COST) for k, a in data.items()})

xs = np.arange(0, 141)
plt.figure(figsize=(9, 5))
for k, a in data.items():
    solo = k.startswith("Solo")
    # solo and multi type B have identical odds, so draw solo as a thick dotted line on top
    plt.plot(xs, [(a <= x).mean() for x in xs], label=k + (" (same as type B)" if solo else ""),
             ls=":" if solo else "-", lw=3.5 if solo else 1.8, zorder=3 if solo else 2)
plt.axvline(70, ls="--", c="grey"); plt.axvline(140, ls="--", c="grey")
plt.xlabel("Number of pulls")
plt.ylabel("Share of players who got the card they want")
plt.title("Love and Deepspace: how many pulls does it take?")
plt.legend(fontsize=8); plt.grid(alpha=.3); plt.tight_layout()
plt.savefig("satisfaction.png", dpi=120)
