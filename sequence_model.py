"""Banner series: how carry-over of the pity counter and guarantee affects the result.
The player gets B pulls per banner, pulls until the target card is obtained or pulls run out
(unused pulls are saved), over K banners in a row.
carry=True: real rules (the 1-70 counter and the 50/50 guarantee carry over to the next banner).
carry=False: hypothetical case where counter and guarantee reset at the end of each banner.
The Precise Wish point on multi banners does not carry over (as described by the author).
"""
import random, numpy as np

BASE, SOFT_START, SOFT_STEP, HARD = 0.01, 61, 0.10, 70
def chance(n):
    if n >= HARD: return 1.0
    if n >= SOFT_START: return min(1.0, BASE + SOFT_STEP * (n - SOFT_START + 1))
    return BASE

def run(kind, B, K, carry):
    pity, flag, avail, got = 0, False, 0, 0
    for _ in range(K):
        avail += B
        wish, done = False, False
        while avail > 0 and not done:
            avail -= 1
            pity += 1
            if random.random() < chance(pity):
                pity = 0
                if kind == "solo":
                    if flag or random.random() < 0.5:
                        done, flag = True, False
                    else:
                        flag = True
                else:  # multi, type A: one specific card out of the three selected
                    if wish or random.random() < 0.25:
                        done = True
                    else:
                        wish = True
        got += done
        if not carry:
            pity, flag = 0, False
    return got, avail

random.seed(7)
K, N = 10, 20000
print(f"Banners (out of {K}) where the card was obtained, mean over N={N} runs")
print(f"{'':10}{'B':>4} {'carry':>8} {'no carry':>9}")
for kind in ("solo", "multi A"):
    for B in (30, 45, 60, 70):
        k = "solo" if kind == "solo" else "multi"
        c = np.mean([run(k, B, K, True)[0] for _ in range(N)])
        n = np.mean([run(k, B, K, False)[0] for _ in range(N)])
        print(f"{kind:10}{B:4d} {c:8.2f} {n:9.2f}")

# --- chart ---
import matplotlib.pyplot as plt
budgets = (30, 45, 60, 70)
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, (title, k) in zip(axes, (("Solo banner", "solo"), ("Multi banner, one specific card", "multi"))):
    c = [np.mean([run(k, B, K, True)[0] for _ in range(5000)]) for B in budgets]
    n = [np.mean([run(k, B, K, False)[0] for _ in range(5000)]) for B in budgets]
    ax.plot(budgets, c, marker="o", label="pity carries over (real rules)")
    ax.plot(budgets, n, marker="o", ls="--", label="pity resets each banner (hypothetical)")
    ax.set_title(title); ax.set_xlabel("Pulls per banner"); ax.grid(alpha=.3)
axes[0].set_ylabel(f"Banners (of {K}) where the card was obtained")
axes[0].legend(fontsize=8)
plt.tight_layout(); plt.savefig("sequence.png", dpi=120)
