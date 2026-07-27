"""Generate the reproducible figures used in the Bayesian learning post."""

from math import exp, lgamma, log, pi, sqrt
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "public" / "img" / "bayes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


PAPER = "#f5f0e6"
INK = "#28333b"
BLUE = "#386fa4"
RED = "#b24c3f"
GOLD = "#c6923a"
GRID = "#d8d0c4"


plt.rcParams.update(
    {
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "font.family": "DejaVu Sans",
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "grid.alpha": 0.65,
    }
)


def beta_pdf(x: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    """Evaluate a Beta density without requiring SciPy."""

    # Use log-gamma to avoid computing large factorial-like values directly.
    log_normalizer = lgamma(alpha) + lgamma(beta) - lgamma(alpha + beta)
    return np.exp(
        (alpha - 1) * np.log(x)
        + (beta - 1) * np.log1p(-x)
        - log_normalizer
    )


def approximate_interval(x: np.ndarray, density: np.ndarray) -> tuple[float, float]:
    """Approximate a 95% interval from a density evaluated on a grid."""

    cdf = np.cumsum(density)
    cdf = cdf / cdf[-1]
    return float(np.interp(0.025, cdf, x)), float(np.interp(0.975, cdf, x))


def generate_coin_figure() -> None:
    """Plot how repeated coin tosses update a Beta prior."""

    rng = np.random.default_rng(20260727)
    true_probability = 0.70
    observations = rng.binomial(1, true_probability, size=100)
    grid = np.linspace(0.001, 0.999, 800)

    checkpoints = [0, 10, 30, 100]
    figure, axes = plt.subplots(2, 2, figsize=(13, 8), sharex=True, sharey=True)
    axes = axes.ravel()

    for axis, sample_count in zip(axes, checkpoints):
        observed = observations[:sample_count]
        heads = int(observed.sum())
        tails = sample_count - heads

        # Beta(1, 1) is a uniform prior. Every head adds one to alpha;
        # every tail adds one to beta, giving Beta(1 + heads, 1 + tails).
        alpha = 1 + heads
        beta = 1 + tails
        density = beta_pdf(grid, alpha, beta)
        lower, upper = approximate_interval(grid, density)

        axis.plot(grid, density, color=BLUE, linewidth=2.4)
        axis.fill_between(grid, density, color=BLUE, alpha=0.14)
        axis.axvline(true_probability, color=RED, linestyle="--", linewidth=1.5)
        axis.axvspan(lower, upper, color=GOLD, alpha=0.12)
        axis.set_title(f"n = {sample_count}   heads = {heads}   tails = {tails}")
        axis.set_xlim(0, 1)
        axis.set_ylim(bottom=0)
        axis.set_xlabel("p: probability of heads")
        axis.set_ylabel("density")

    figure.suptitle("Bayesian update for a coin toss", fontsize=18, y=0.98)
    figure.text(
        0.5,
        0.01,
        "Dashed line: simulation truth p = 0.70   |   Shaded band: approximate 95% credible interval",
        ha="center",
        fontsize=10,
        color="#5d665f",
    )
    figure.tight_layout(rect=(0, 0.04, 1, 0.95))
    figure.savefig(OUTPUT_DIR / "coin-bayesian-update.png", dpi=180, bbox_inches="tight")
    plt.close(figure)

    print(
        "coin example:",
        f"heads={int(observations.sum())}",
        f"tails={int(100 - observations.sum())}",
        f"posterior=Beta({1 + observations.sum()}, {1 + 100 - observations.sum()})",
    )


def generate_mh_figure() -> None:
    """Run a hand-written Metropolis-Hastings sampler and plot its output."""

    rng = np.random.default_rng(20260727)
    true_mean = 1.0
    data = rng.normal(loc=true_mean, scale=1.0, size=20)

    def log_unnormalized_posterior(mu: float) -> float:
        # With a flat prior and known sigma=1, the log-likelihood is enough.
        # Working in log space prevents products of many tiny probabilities
        # from underflowing to zero.
        return float(-0.5 * np.sum((data - mu) ** 2))

    current_mu = 0.0
    current_log_posterior = log_unnormalized_posterior(current_mu)
    samples: list[float] = []
    accepted = 0
    total_steps = 50_000

    for _ in range(total_steps):
        # Propose a nearby value. The proposal width controls how far the
        # random walk can move at each step.
        proposed_mu = current_mu + rng.normal(0, 0.5)
        proposed_log_posterior = log_unnormalized_posterior(proposed_mu)

        # The normalizing constant cancels in the ratio, so compare only
        # the unnormalized log posterior values.
        log_accept_ratio = proposed_log_posterior - current_log_posterior
        if log(rng.random()) < min(0.0, log_accept_ratio):
            current_mu = proposed_mu
            current_log_posterior = proposed_log_posterior
            accepted += 1

        # Record the current state even when the proposal was rejected.
        samples.append(current_mu)

    burn_in = 5_000
    posterior_samples = np.asarray(samples[burn_in:])
    posterior_mean = float(posterior_samples.mean())
    posterior_std = float(posterior_samples.std())
    lower, upper = np.quantile(posterior_samples, [0.025, 0.975])

    figure, (trace_axis, histogram_axis) = plt.subplots(1, 2, figsize=(14, 5.5))
    trace_axis.plot(posterior_samples, color=BLUE, linewidth=0.35, alpha=0.75)
    trace_axis.axhline(true_mean, color=RED, linestyle="--", linewidth=1.5)
    trace_axis.set_title("Trace after burn-in")
    trace_axis.set_xlabel("iteration")
    trace_axis.set_ylabel("mu")

    histogram_axis.hist(
        posterior_samples,
        bins=60,
        density=True,
        color=BLUE,
        alpha=0.55,
        edgecolor=PAPER,
    )
    curve_x = np.linspace(posterior_samples.min(), posterior_samples.max(), 400)
    curve_y = np.exp(-0.5 * ((curve_x - posterior_mean) / posterior_std) ** 2)
    curve_y = curve_y / (posterior_std * sqrt(2 * pi))
    histogram_axis.plot(curve_x, curve_y, color=INK, linewidth=2, label="normal approximation")
    histogram_axis.axvline(true_mean, color=RED, linestyle="--", linewidth=1.5, label="true mu = 1")
    histogram_axis.axvspan(lower, upper, color=GOLD, alpha=0.14, label="95% interval")
    histogram_axis.set_title("Posterior samples for mu")
    histogram_axis.set_xlabel("mu")
    histogram_axis.set_ylabel("density")
    histogram_axis.legend(frameon=False)

    figure.suptitle("A small Metropolis-Hastings experiment", fontsize=18, y=1.01)
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / "mh-posterior-sampler.png", dpi=180, bbox_inches="tight")
    plt.close(figure)

    print(
        "MH example:",
        f"acceptance_rate={accepted / total_steps:.3f}",
        f"posterior_mean={posterior_mean:.3f}",
        f"posterior_std={posterior_std:.3f}",
        f"interval=({lower:.3f}, {upper:.3f})",
    )


if __name__ == "__main__":
    generate_coin_figure()
    generate_mh_figure()
