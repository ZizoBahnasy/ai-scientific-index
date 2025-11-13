#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
from pathlib import Path
from typing import Dict, Any

def generate_taxonomy(full_json_path: str, output_dir: str = "outputs") -> None:
    """
    Reads the full hierarchy JSON and writes:
      - taxonomy.json: nested directorate → division → [programs]
      - taxonomy.tsv: flat table with columns directorate, division, program
    """
    hier_path = Path(full_json_path)
    if not hier_path.exists():
        raise FileNotFoundError(f"{full_json_path} not found. Run main.py first.")

    with hier_path.open() as f:
        hierarchy: Dict[str, Any] = json.load(f)

    # Build taxonomy
    taxonomy: Dict[str, Dict[str, list]] = {}
    for directorate, divisions in hierarchy.items():
        taxonomy[directorate] = {}
        for division, programs in divisions.items():
            # skip metric keys
            if division.startswith(("num_awards_", "amt_awarded_")):
                continue
            # collect only program names
            prog_list = [
                p for p in programs.keys()
                if not p.startswith(("num_awards_", "amt_awarded_"))
            ]
            taxonomy[directorate][division] = prog_list

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Write taxonomy.json
    json_out = out_dir / "taxonomy.json"
    with json_out.open("w") as f:
        json.dump(taxonomy, f, indent=2)
    print(f"✔ Wrote taxonomy JSON to {json_out}")

    # Write taxonomy.tsv
    tsv_out = out_dir / "taxonomy.tsv"
    with tsv_out.open("w", newline="") as f:
        writer = csv.writer(f, delimiter="\t")
        writer.writerow(["directorate", "division", "program"])
        for directorate, divisions in taxonomy.items():
            for division, programs in divisions.items():
                for program in programs:
                    writer.writerow([directorate, division, program])
    print(f"✔ Wrote taxonomy TSV to {tsv_out}")
