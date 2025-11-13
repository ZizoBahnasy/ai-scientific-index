#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

def find_json_path(json_path_str: str) -> Path:
    """
    Try the given path; if not found, look relative to project root.
    """
    path = Path(json_path_str)
    if path.exists():
        return path
    # assume __file__ is src/visualize.py; go up two levels to project root
    project_root = Path(__file__).parent.parent.resolve()
    candidate = project_root / json_path_str
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"Could not find {json_path_str}")

def load_flattened_data(json_path: Path) -> pd.DataFrame:
    """
    Read the nested research.json and return a flat DataFrame:
      directorate, division, program, year, amount
    """
    data = json.loads(json_path.read_text())
    rows = []

    for d, divs in data.items():
        # divs should be a dict; skip if not
        if not isinstance(divs, dict):
            continue

        for v, progs in divs.items():
            # skip any metric keys at the division level
            if not isinstance(progs, dict):
                continue

            for p, metrics in progs.items():
                # skip any non‐dict entries at the program level
                if not isinstance(metrics, dict):
                    continue

                # metrics is a dict of metric_name → number
                for k, val in metrics.items():
                    # only interested in the amount‐by‐year keys
                    if k.startswith("amt_awarded_"):
                        suffix = k.split("_")[-1]
                        if suffix.isdigit():
                            year = int(suffix)
                            rows.append({
                                "directorate": d,
                                "division":    v,
                                "program":     p,
                                "year":        year,
                                "amount":      val
                            })

    return pd.DataFrame(rows)

def plot_top_divisions(df: pd.DataFrame):
    top = (
        df.groupby("division")["amount"]
          .sum()
          .sort_values(ascending=False)
          .head(10)
    )
    plt.figure()
    top.plot.barh()
    plt.gca().invert_yaxis()
    plt.title("Top-10 NSF Divisions by Total Funding")
    plt.xlabel("Total Funding (USD)")
    plt.tight_layout()
    plt.show()

def plot_directorate_timeseries(df: pd.DataFrame):
    pivot = (
        df.groupby(["year", "directorate"])["amount"]
          .sum()
          .unstack("directorate")
    )
    plt.figure()
    pivot.plot()
    plt.title("NSF Funding by Directorate Over Time")
    plt.ylabel("Funding (USD)")
    plt.xlabel("Year")
    plt.tight_layout()
    plt.show()

def run_visualization(json_path_str: str):
    try:
        path = find_json_path(json_path_str)
    except FileNotFoundError as e:
        print(f"[visualize] {e}")
        return

    df = load_flattened_data(path)
    if df.empty:
        print("[visualize] No data found in research.json.")
        return

    plot_top_divisions(df)
    plot_directorate_timeseries(df)

def main():
    p = argparse.ArgumentParser(
        description="Visualize NSF funding from outputs/research.json"
    )
    p.add_argument(
        "--json",
        default="outputs/research.json",
        help="relative path to research.json (default: outputs/research.json)"
    )
    args = p.parse_args()
    run_visualization(args.json)

if __name__ == "__main__":
    main()
