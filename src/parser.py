#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from typing import List, Dict, Optional
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

def parse_award(json_path: Path) -> Optional[List[Dict]]:
    """
    Read one award JSON and return flat records:
      { year, dir_abbr, directorate, div_abbr, division, program, pgm_code, amount }
    """
    try:
        data = json.loads(json_path.read_text())
    except Exception:
        return None

    # infer year from parent folder name
    try:
        year = int(json_path.parent.name)
    except ValueError:
        return None

    dir_name = data.get("org_dir_long_name")
    div_name = data.get("org_div_long_name")
    amt      = data.get("tot_intn_awd_amt")
    pgm_list = data.get("pgm_ele", [])

    if not dir_name or not div_name or not pgm_list or amt is None:
        return None

    records = []
    for pgm in pgm_list:
        p_name = pgm.get("pgm_ele_name")
        p_code = pgm.get("pgm_ele_code")
        if p_name and p_code:
            records.append({
                "year":         year,
                "dir_abbr":     data.get("dir_abbr", "").strip(),
                "directorate":  dir_name.strip(),
                "div_abbr":     data.get("div_abbr", "").strip(),
                "division":     div_name.strip(),
                "program":      p_name.strip(),
                "pgm_code":     p_code.strip(),
                "amount":       float(amt),
            })
    return records if records else None

def parse_all(data_dir: Path, max_workers: int = None) -> List[Dict]:
    """
    Find all award JSON files under data_dir, parse them in parallel,
    and return a flat list of all records.
    Shows a tqdm progress bar.
    """
    json_files = list(data_dir.rglob("*.json"))
    print(f"Found {len(json_files)} award JSON files to parse.")
    records: List[Dict] = []

    with ProcessPoolExecutor(max_workers=max_workers) as exe:
        for recs in tqdm(
            exe.map(parse_award, json_files),
            total=len(json_files),
            desc="Parsing awards"
        ):
            if recs:
                records.extend(recs)

    print(f"Parsed {len(records)} award‐level records.")
    return records
