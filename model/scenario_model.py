"""
scenario_model.py
-----------------
Monte Carlo simulation for AUM and Net Income projections.
Replaces Crystal Ball for Python-native environments.

Outputs:
  - outputs/scenario_results.csv
  - outputs/scenario_chart.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

np.random.seed(42)
SIMULATIONS = 10_000
YEARS       = 3          # forecast horizon
OUT_CSV     = "outputs/scenario_results.csv"
OUT_CHART   = "outputs/scenario_chart.png"

# ── Base assumptions (Grupo TX 2024 actuals) ─────────────────────────────────
BASE_AUM        = 1_100_000   # USD thousands
BASE_NET_INCOME =     72_000

AUM_GROWTH_MEAN  = 0.20       # expected annual growth
AUM_GROWTH_STD   = 0.06       # volatility around that growth
INCOME_MARGIN    = 0.065      # net income / aum (stable assumption)


def simulate_aum(base: float, mean: float, std: float,
                 n_sim: int, n_years: int) -> np.ndarray:
    """Returns shape (n_sim, n_years) of AUM values."""
    growth = np.random.normal(mean, std, size=(n_sim, n_years))
    growth = np.clip(growth, -0.30, 0.50)   # cap extreme scenarios
    factors = np.cumprod(1 + growth, axis=1)
    return base * factors


def run_simulation() -> pd.DataFrame:
    aum_paths    = simulate_aum(BASE_AUM, AUM_GROWTH_MEAN, AUM_GROWTH_STD,
                                SIMULATIONS, YEARS)
    income_paths = aum_paths * INCOME_MARGIN

    records = []
    for yr_idx in range(YEARS):
        year = 2025 + yr_idx
        aum_yr    = aum_paths[:, yr_idx]
        income_yr = income_paths[:, yr_idx]
        records.append({
            "Year":               year,
            "AUM_Bear_P10":       np.percentile(aum_yr, 10)  / 1e3,
            "AUM_Base_P50":       np.percentile(aum_yr, 50)  / 1e3,
            "AUM_Bull_P90":       np.percentile(aum_yr, 90)  / 1e3,
            "Income_Bear_P10":    np.percentile(income_yr,10) / 1e3,
            "Income_Base_P50":    np.percentile(income_yr,50) / 1e3,
            "Income_Bull_P90":    np.percentile(income_yr,90) / 1e3,
        })

    return pd.DataFrame(records).round(1)


def plot_fan_chart(df: pd.DataFrame):
    NAVY, GOLD, TEAL = "#1B3A6B", "#C8972B", "#2E7D9A"
    GRAY = "#9CA3AF"

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), facecolor="white")
    fig.text(0.5, 1.01,
             "Grupo TX — 3-Year Monte Carlo Projection (10,000 simulations)",
             ha="center", fontsize=13, fontweight="bold", color="#1F2937")

    for ax, bear, base, bull, color, label in [
        (axes[0], "AUM_Bear_P10",    "AUM_Base_P50",    "AUM_Bull_P90",
         NAVY, "AUM (USD Millions)"),
        (axes[1], "Income_Bear_P10", "Income_Base_P50", "Income_Bull_P90",
         GOLD, "Net Income (USD Millions)"),
    ]:
        years = df["Year"].tolist()
        ax.fill_between(years, df[bear], df[bull],
                        alpha=0.15, color=color, label="P10–P90 range")
        ax.plot(years, df[base], color=color, linewidth=2.5,
                marker="o", markersize=8, markerfacecolor="white",
                markeredgewidth=2, label="Base case (P50)")
        ax.plot(years, df[bear], color=color, linewidth=1,
                linestyle="--", alpha=0.6, label="Bear (P10)")
        ax.plot(years, df[bull], color=color, linewidth=1,
                linestyle="--", alpha=0.6, label="Bull (P90)")

        for _, row in df.iterrows():
            ax.annotate(f"${row[base]:,.0f}M",
                        xy=(row["Year"], row[base]),
                        xytext=(0, 10), textcoords="offset points",
                        ha="center", fontsize=9, fontweight="bold", color=color)

        ax.set_title(label, fontsize=11, fontweight="bold", color="#1F2937", pad=10)
        ax.set_xticks(years)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#E5E7EB")
        ax.yaxis.set_visible(False)
        ax.tick_params(axis="x", labelsize=10, labelcolor=GRAY, length=0)
        ax.legend(frameon=False, fontsize=8, labelcolor=GRAY)

    plt.tight_layout()
    plt.savefig(OUT_CHART, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Chart saved -> {OUT_CHART}")


if __name__ == "__main__":
    print(f"Running {SIMULATIONS:,} Monte Carlo simulations ({YEARS}-year horizon)...")
    df = run_simulation()

    print("\n-- Scenario Results --")
    print(df.to_string(index=False))

    df.to_csv(OUT_CSV, index=False)
    print(f"\nResults saved -> {OUT_CSV}")

    plot_fan_chart(df)
    print("Done.")
