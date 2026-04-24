"""
monte_carlo.py — Grupo TX Revenue Simulation
---------------------------------------------
Inputs:  historical revenue from grupo_tx_financials.xlsx
Outputs: /outputs/mc_histogram.png
         /outputs/mc_paths.png
         /outputs/mc_summary.csv
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings, os

warnings.filterwarnings("ignore")
np.random.seed(42)

# ── Config ────────────────────────────────────────────────────────────────────
N_SIM      = 10_000
N_YEARS    = 5
DATA_FILE  = r"data\grupo_tx_financials.xlsx"
OUT_DIR    = "outputs"

NAVY  = "#1B3A6B"
GOLD  = "#C8972B"
TEAL  = "#2E7D9A"
RED   = "#DC2626"
GREEN = "#16A34A"
GRAY  = "#9CA3AF"
DARK  = "#1F2937"

# ── 1. Load historical revenue ────────────────────────────────────────────────
def load_revenue() -> pd.Series:
    df = pd.read_excel(DATA_FILE, sheet_name="Tabla Maestra ", header=1)
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Año"]).copy()
    df["Año"]             = df["Año"].astype(str).str.strip()
    df["Ingresos totales"] = pd.to_numeric(df["Ingresos totales"], errors="coerce")
    df = df.sort_values("Año").reset_index(drop=True)
    return df.set_index("Año")["Ingresos totales"]

# ── 2. Estimate parameters from history ──────────────────────────────────────
def estimate_params(revenue: pd.Series) -> dict:
    log_returns = np.log(revenue / revenue.shift(1)).dropna()
    mu          = log_returns.mean()
    sigma       = log_returns.std()

    # Drift-adjusted mean (geometric Brownian motion correction)
    drift = mu - 0.5 * sigma ** 2

    return {
        "mu":         mu,
        "sigma":      sigma,
        "drift":      drift,
        "mean_growth": np.exp(mu) - 1,
        "vol":         sigma,
        "years":       list(revenue.index),
        "last_revenue": revenue.iloc[-1],
        "historical":   revenue,
    }

# ── 3. Run simulation ─────────────────────────────────────────────────────────
def simulate(params: dict) -> np.ndarray:
    """
    Returns array of shape (N_SIM, N_YEARS).
    Each row = one simulation path of year-end revenues.
    """
    base   = params["last_revenue"]
    drift  = params["drift"]
    sigma  = params["sigma"]

    shocks  = np.random.normal(0, 1, size=(N_SIM, N_YEARS))
    returns = np.exp(drift + sigma * shocks)           # annual return factors
    paths   = base * np.cumprod(returns, axis=1)       # compounded revenue paths
    return paths

# ── 4. Statistics ─────────────────────────────────────────────────────────────
def build_summary(paths: np.ndarray, params: dict) -> pd.DataFrame:
    base_year = int(params["years"][-1])
    records   = []

    for yr_idx in range(N_YEARS):
        year   = base_year + yr_idx + 1
        col    = paths[:, yr_idx]
        records.append({
            "Year":         year,
            "P5_Downside":  np.percentile(col,  5),
            "P25":          np.percentile(col, 25),
            "Median_P50":   np.percentile(col, 50),
            "Mean_Expected":col.mean(),
            "P75":          np.percentile(col, 75),
            "P95_Upside":   np.percentile(col, 95),
            "Std_Dev":      col.std(),
        })

    df = pd.DataFrame(records)

    # Growth vs base year
    base = params["last_revenue"]
    for col in ["P5_Downside", "Median_P50", "Mean_Expected", "P95_Upside"]:
        df[col + "_Growth"] = ((df[col] / base) - 1) * 100

    return df.round(0)

# ── 5. Chart A — Histogram of final-year outcomes ────────────────────────────
def plot_histogram(paths: np.ndarray, params: dict, summary: pd.DataFrame):
    final_col = paths[:, -1]                      # Year 5 distribution
    final_yr  = int(params["years"][-1]) + N_YEARS

    p5   = np.percentile(final_col,  5)
    p50  = np.percentile(final_col, 50)
    mean = final_col.mean()
    p95  = np.percentile(final_col, 95)

    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor="white")
    fig.subplots_adjust(top=0.80)

    # Histogram
    n, bins, patches = ax.hist(final_col / 1e6, bins=80, color=NAVY,
                                alpha=0.75, edgecolor="white", linewidth=0.3, zorder=3)

    # Color the tails
    for patch, left in zip(patches, bins[:-1]):
        if left * 1e6 < p5:
            patch.set_facecolor(RED)
            patch.set_alpha(0.6)
        elif left * 1e6 > p95:
            patch.set_facecolor(GREEN)
            patch.set_alpha(0.6)

    # Vertical lines
    for val, color, lbl, ls in [
        (p5,   RED,   f"P5  — Bear  ${p5/1e6:,.1f}M",   "--"),
        (p50,  TEAL,  f"P50 — Base  ${p50/1e6:,.1f}M",  "-"),
        (mean, GOLD,  f"Mean        ${mean/1e6:,.1f}M",  "-."),
        (p95,  GREEN, f"P95 — Bull  ${p95/1e6:,.1f}M",  "--"),
    ]:
        ax.axvline(val / 1e6, color=color, linewidth=2, linestyle=ls, zorder=4)
        ax.text(val / 1e6, ax.get_ylim()[1] * 0.97, f"  {lbl}",
                color=color, fontsize=8, va="top", rotation=90,
                fontweight="bold")

    # Styling
    fig.text(0.13, 0.97,
             f"Year {final_yr} Revenue Distribution  —  {N_SIM:,} Simulations",
             fontsize=14, fontweight="bold", color=DARK, va="top")
    fig.text(0.13, 0.90,
             f"Based on historical growth:  Mean {params['mean_growth']*100:.1f}%  |  "
             f"Volatility {params['vol']*100:.1f}%  |  Horizon: {N_YEARS} years",
             fontsize=10, color=GRAY, va="top")

    ax.set_xlabel("Revenue (USD Millions)", fontsize=10, color=GRAY)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#E5E7EB")
    ax.tick_params(labelsize=9, labelcolor=GRAY, length=0)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}M"))
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#F3F4F6", linewidth=0.7)

    path = os.path.join(OUT_DIR, "mc_histogram.png")
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Saved -> {path}")

# ── 6. Chart B — Simulation paths ────────────────────────────────────────────
def plot_paths(paths: np.ndarray, params: dict, summary: pd.DataFrame):
    base_year = int(params["years"][-1])
    hist_rev  = params["historical"]
    years_fwd = [base_year + i + 1 for i in range(N_YEARS)]
    all_years = list(hist_rev.index) + [str(y) for y in years_fwd]

    fig, ax = plt.subplots(figsize=(12, 6), facecolor="white")
    fig.subplots_adjust(top=0.80)

    # 20 random paths (light, in background)
    # x covers from last historical point through all forecast years
    fwd_x_paths = range(len(hist_rev) - 1, len(all_years))
    sample_idx = np.random.choice(N_SIM, 20, replace=False)
    for idx in sample_idx:
        path_vals = [params["last_revenue"]] + list(paths[idx])
        ax.plot(fwd_x_paths,
                [v / 1e6 for v in path_vals],
                color=NAVY, alpha=0.12, linewidth=0.8, zorder=1)

    # Historical actuals (solid, bold)
    hist_x = range(len(hist_rev))
    ax.plot(list(hist_x), [v / 1e6 for v in hist_rev.values],
            color=NAVY, linewidth=2.5, marker="o", markersize=7,
            markerfacecolor="white", markeredgewidth=2,
            label="Historical Revenue", zorder=4)

    # Annotate historical
    for xi, (yr, val) in enumerate(hist_rev.items()):
        ax.text(xi, val / 1e6 + 0.8, f"${val/1e6:.1f}M",
                ha="center", fontsize=8.5, fontweight="bold", color=NAVY)

    # Percentile ribbons (forward)
    fwd_x     = range(len(hist_rev) - 1, len(all_years))
    base_anchor = params["last_revenue"]

    p5_vals  = [base_anchor] + list(summary["P5_Downside"])
    p50_vals = [base_anchor] + list(summary["Median_P50"])
    p95_vals = [base_anchor] + list(summary["P95_Upside"])
    mean_vals= [base_anchor] + list(summary["Mean_Expected"])

    ax.fill_between(fwd_x, [v/1e6 for v in p5_vals], [v/1e6 for v in p95_vals],
                    color=NAVY, alpha=0.07, label="P5–P95 range", zorder=2)
    ax.fill_between(fwd_x, [v/1e6 for v in p5_vals], [v/1e6 for v in p50_vals],
                    color=RED, alpha=0.06, zorder=2)

    for vals, color, label, lw, ls in [
        (p95_vals,  GREEN, "Bull  (P95)", 2.2, "--"),
        (mean_vals, GOLD,  "Base  (Mean)",2.5, "-"),
        (p50_vals,  TEAL,  "Median (P50)",2.0, "-"),
        (p5_vals,   RED,   "Bear  (P5)", 2.0, "--"),
    ]:
        ax.plot(fwd_x, [v/1e6 for v in vals],
                color=color, linewidth=lw, linestyle=ls,
                marker="o", markersize=5, markerfacecolor="white",
                markeredgewidth=1.5, label=label, zorder=4)
        # Label final year
        ax.text(fwd_x[-1] + 0.05, vals[-1] / 1e6,
                f"  ${vals[-1]/1e6:,.1f}M",
                color=color, fontsize=8.5, fontweight="bold", va="center")

    # Vertical separator: history vs forecast
    ax.axvline(len(hist_rev) - 1, color="#E5E7EB",
               linewidth=1.2, linestyle="--", zorder=3)
    ax.text(len(hist_rev) - 1 + 0.08, ax.get_ylim()[0] + 1,
            "Forecast ->", color=GRAY, fontsize=8.5)

    # X-axis labels
    ax.set_xticks(range(len(all_years)))
    ax.set_xticklabels(all_years, fontsize=9, color=GRAY)

    fig.text(0.13, 0.97,
             "Grupo TX — Revenue Simulation Paths (10,000 runs)",
             fontsize=14, fontweight="bold", color=DARK, va="top")
    fig.text(0.13, 0.90,
             f"Historical base: 2023–2025  |  Forecast: {base_year+1}–{base_year+N_YEARS}  |  "
             f"Growth assumption: {params['mean_growth']*100:.1f}% mean, {params['vol']*100:.1f}% vol",
             fontsize=10, color=GRAY, va="top")

    ax.set_ylabel("Revenue (USD Millions)", fontsize=10, color=GRAY)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:,.0f}M"))
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#E5E7EB")
    ax.tick_params(labelsize=9, labelcolor=GRAY, length=0)
    ax.yaxis.grid(True, color="#F3F4F6", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=9, labelcolor=DARK, loc="upper left")

    path = os.path.join(OUT_DIR, "mc_paths.png")
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Saved -> {path}")

# ── 7. Export summary CSV ─────────────────────────────────────────────────────
def export_summary_csv(summary: pd.DataFrame, params: dict):
    out = summary[[
        "Year", "P5_Downside", "Median_P50", "Mean_Expected",
        "P95_Upside", "Std_Dev",
        "P5_Downside_Growth", "Median_P50_Growth",
        "Mean_Expected_Growth", "P95_Upside_Growth"
    ]].copy()

    # Format USD cols (in millions)
    for col in ["P5_Downside", "Median_P50", "Mean_Expected", "P95_Upside", "Std_Dev"]:
        out[col] = (out[col] / 1e6).round(2)
    out.columns = [
        "Year",
        "Bear_P5_M", "Median_P50_M", "Mean_M", "Bull_P95_M", "StdDev_M",
        "Bear_Growth_%", "Median_Growth_%", "Mean_Growth_%", "Bull_Growth_%"
    ]

    path = os.path.join(OUT_DIR, "mc_summary.csv")
    out.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"  Saved -> {path}")
    return out

# ── 8. Print terminal summary ─────────────────────────────────────────────────
def print_summary(summary_csv: pd.DataFrame, params: dict):
    base = params["last_revenue"] / 1e6
    print(f"""
GRUPO TX  |  Monte Carlo Revenue Simulation
============================================
Simulations   : {N_SIM:,}
Horizon       : {N_YEARS} years
Base Revenue  : ${base:.2f}M  ({params['years'][-1]})
Implied Growth: {params['mean_growth']*100:.1f}% mean  |  {params['vol']*100:.1f}% annual volatility
Model         : Geometric Brownian Motion (log-normal returns)

{'Year':<6} {'Bear P5':>10} {'Median':>10} {'Mean':>10} {'Bull P95':>10}  {'Std Dev':>9}
{'-'*60}""")
    for _, row in summary_csv.iterrows():
        print(f"{int(row['Year']):<6} "
              f"${row['Bear_P5_M']:>8.1f}M  "
              f"${row['Median_P50_M']:>8.1f}M  "
              f"${row['Mean_M']:>8.1f}M  "
              f"${row['Bull_P95_M']:>8.1f}M  "
              f"${row['StdDev_M']:>7.1f}M")

    final = summary_csv.iloc[-1]
    print(f"""
Year {int(final['Year'])} Scenarios vs ${base:.1f}M base:
  Bear  (P5)  : ${final['Bear_P5_M']:.1f}M   ({final['Bear_Growth_%']:+.0f}%)
  Median (P50): ${final['Median_P50_M']:.1f}M  ({final['Median_Growth_%']:+.0f}%)
  Mean        : ${final['Mean_M']:.1f}M  ({final['Mean_Growth_%']:+.0f}%)
  Bull  (P95) : ${final['Bull_P95_M']:.1f}M  ({final['Bull_Growth_%']:+.0f}%)
""")

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Loading historical revenue...")
    revenue = load_revenue()
    print(f"  Data: {dict(revenue)}")

    print("\nEstimating model parameters...")
    params = estimate_params(revenue)
    print(f"  Mean log-return : {params['mu']*100:.2f}%")
    print(f"  Volatility      : {params['sigma']*100:.2f}%")
    print(f"  Implied growth  : {params['mean_growth']*100:.2f}%")

    print(f"\nRunning {N_SIM:,} simulations over {N_YEARS} years...")
    paths = simulate(params)

    print("Building summary statistics...")
    summary = build_summary(paths, params)

    print("\nGenerating charts...")
    plot_histogram(paths, params, summary)
    plot_paths(paths, params, summary)

    print("Exporting summary CSV...")
    summary_csv = export_summary_csv(summary, params)

    print_summary(summary_csv, params)
    print("Done.")
