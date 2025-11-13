#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm

def build_maps(records: List[Dict[str, Any]], output_dir: str = "outputs"):
    """
    From parsed records (with dir_abbr, directorate, div_abbr, division,
    program, pgm_code), write:
      - directorate_map.json   (long_name -> abbr)
      - division_map.json      (long_name -> abbr)
      - program_map.json       (program_name -> code)
      - division_urls.txt      (one URL per valid combo)
    Applies:
      * cleans O/D → OD
      * skips abbr==abbr combos
      * uses hard-coded OD divisions
    """
    out = Path(output_dir); out.mkdir(parents=True, exist_ok=True)

    dir_map: Dict[str,str] = {}
    div_map: Dict[str,str] = {}
    prog_map: Dict[str,str] = {}
    combos = set()  # (dir_abbr, div_abbr)

    # 1) Gather maps & raw combos
    for r in tqdm(records, desc="Building abbreviation maps"):
        raw_d = r["dir_abbr"].strip()
        d_abbr = raw_d.replace("/", "")  # clean O/D→OD
        d_long = r["directorate"].strip()
        v_abbr = r["div_abbr"].strip()
        v_long = r["division"].strip()
        p_name = r["program"].strip()
        p_code = r["pgm_code"].strip()

        dir_map[d_long]  = d_abbr
        div_map[v_long]  = v_abbr
        prog_map[p_name] = p_code

        # only keep combos where dir_abbr != div_abbr
        if d_abbr != v_abbr:
            combos.add((d_abbr, v_abbr))

    # 2) Override OD combos
    special_od = [
        ("OD", "EOD"),  # Executive Office of the Director
        ("OD", "OCR"),  # Office of Civil Rights
        ("OD", "OIA"),  # Office of Integrative Activities
        ("OD", "OISE"), # Office of International Science and Engineering
        ("OD", "OLPA"), # Office of Legislative and Public Affairs
        ("OD", "OGC"),  # Office of the General Counsel
        ("OD", "CRSP")  # Office of the Chief of Research Security Strategy and Policy
    ]
    # remove any previously added OD combos
    combos = {(d,v) for (d,v) in combos if d != "OD"}
    # add our canonical OD list
    combos.update(special_od)

    # 3) Write maps
    for fname, mp in [
        ("directorate_map.json", dir_map),
        ("division_map.json",    div_map),
        ("program_map.json",     prog_map),
    ]:
        with (out / fname).open("w") as f:
            json.dump(mp, f, indent=2)
        print(f"✔ Wrote {fname}")

    # 4) Write URLs
    url_file = out / "division_urls.txt"
    with url_file.open("w") as f:
        for d_abbr, v_abbr in sorted(combos):
            f.write(f"https://www.nsf.gov/{d_abbr}/{v_abbr}\n")
    print(f"✔ Wrote division_urls.txt")
