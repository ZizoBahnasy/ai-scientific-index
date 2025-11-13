#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import csv
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

# Input & output locations
DATA_DIR   = Path("data/awards")
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Gather all award JSON files
AWARD_FILES = list(DATA_DIR.rglob("*.json"))
OUT_PATH    = OUTPUT_DIR / "awards.csv"

def sanitize(s: str) -> str:
    """
    Remove newlines and collapse whitespace.
    """
    return " ".join(s.replace("\r", " ").replace("\n", " ").split())

def flatten_award_file(json_path: Path) -> dict:
    """
    Read one award JSON file and return a flat dict of values,
    including a 'year' field from the parent folder name.
    """
    # 0) Year from folder
    try:
        year = int(json_path.parent.name)
    except ValueError:
        year = ""

    data = json.loads(json_path.read_text())
    out = {"year": year}

    # 1) Core award fields
    for k in [
        "awd_id","agcy_id","tran_type","awd_istr_txt","awd_titl_txt",
        "cfda_num","org_code","po_phone","po_email","po_sign_block_name",
        "awd_eff_date","awd_exp_date","tot_intn_awd_amt","awd_amount",
        "awd_min_amd_letter_date","awd_max_amd_letter_date","awd_abstract_narration",
        "awd_arra_amount","dir_abbr","org_dir_long_name","div_abbr","org_div_long_name"
    ]:
        v = data.get(k) or ""
        out[k] = sanitize(str(v)) if isinstance(v, str) else v

    # 2) Program elements
    pes = data.get("pgm_ele") or []
    codes = [(p.get("pgm_ele_code") or "") for p in pes]
    names = [(p.get("pgm_ele_name") or "") for p in pes]
    out["pgm_ele_codes"] = sanitize(";".join(codes))
    out["pgm_ele_names"] = sanitize(";".join(names))

    # 3) Program references
    prs = data.get("pgm_ref") or []
    rcodes = [(p.get("pgm_ref_code") or "") for p in prs]
    txts   = [(p.get("pgm_ref_txt")  or "") for p in prs]
    out["pgm_ref_codes"] = sanitize(";".join(rcodes))
    out["pgm_ref_txts"]  = sanitize(";".join(txts))

    # 4) Agency/fund codes
    for k in ["awd_agcy_code","fund_agcy_code"]:
        v = data.get(k) or ""
        out[k] = sanitize(str(v)) if isinstance(v, str) else v

    # 5) PIs
    pis = data.get("pi") or []
    pnames = [(p.get("pi_full_name") or "") for p in pis]
    proles = [(p.get("pi_role")      or "") for p in pis]
    out["pi_names"] = sanitize(";".join(pnames))
    out["pi_roles"] = sanitize(";".join(proles))

    # 6) Institutions
    for prefix in ("inst", "perf_inst"):
        sub = data.get(prefix) or {}
        for subk, subv in sub.items():
            val = subv or ""
            out[f"{prefix}_{subk}"] = sanitize(str(val))

    # 7) Application funding
    afs = data.get("app_fund") or []
    fcodes = [(a.get("fund_code") or "") for a in afs]
    fnames = [(a.get("fund_name") or "") for a in afs]
    out["app_fund_codes"] = sanitize(";".join(fcodes))
    out["app_fund_names"] = sanitize(";".join(fnames))

    # 8) Obligation FY
    fys = data.get("oblg_fy") or []
    years = [str(f.get("fund_oblg_fiscal_yr") or "") for f in fys]
    amts  = [str(f.get("fund_oblg_amt") or "")           for f in fys]
    out["oblg_fy_years"] = sanitize(";".join(years))
    out["oblg_fy_amts"]  = sanitize(";".join(amts))

    return out

def main():
    if not AWARD_FILES:
        print("No award JSON files found under data/awards/. Run extraction first.")
        return

    # Build header from a sample
    sample = flatten_award_file(AWARD_FILES[0])
    fieldnames = list(sample.keys())

    # Write CSV with all fields quoted
    with OUT_PATH.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames,
            extrasaction="ignore",
            quoting=csv.QUOTE_ALL
        )
        writer.writeheader()

        # Parallel flatten + sequential write
        with ProcessPoolExecutor() as exe:
            for flat in tqdm(
                exe.map(flatten_award_file, AWARD_FILES),
                total=len(AWARD_FILES),
                desc="Exporting awards"
            ):
                writer.writerow(flat)

    print(f"✔ Wrote award‐level file to {OUT_PATH}")

if __name__ == "__main__":
    main()
