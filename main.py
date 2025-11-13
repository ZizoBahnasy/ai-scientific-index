#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from src.downloader      import download_year
from src.extractor       import extract_awards
from src.parser          import parse_all
from src.export_awards import main as export_awards
from src.mappings        import build_maps
from src.aggregator      import (
    build_hierarchy,
    make_brief,
    sort_hierarchy,
    sort_hierarchy_by_year
)
from src.taxonomy        import generate_taxonomy
from src.visualize       import run_visualization
from src.mission_scraper import scrape_missions

DATA_DIR    = Path("data/awards")
OUTPUT_DIR  = Path("outputs")

MAX_DL_WORKERS      = 5
MAX_EXTRACT_WORKERS = 3
MAX_PARSE_WORKERS   = None  # uses os.cpu_count()

def download_all(years):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=MAX_DL_WORKERS) as exe:
        futures = {exe.submit(download_year, y, DATA_DIR): y for y in years}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Downloading"):
            year = futures[fut]
            try:
                fut.result()
            except Exception as e:
                print(f"[Error] downloading {year}: {e}")

def extract_all():
    zips = list(DATA_DIR.glob("*.zip"))
    with ThreadPoolExecutor(max_workers=MAX_EXTRACT_WORKERS) as exe:
        futures = {exe.submit(extract_awards, zp, DATA_DIR): zp for zp in zips}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Extracting"):
            zp = futures[fut]
            try:
                fut.result()
            except Exception as e:
                print(f"[Error] extracting {zp.name}: {e}")

def main():
    parser = argparse.ArgumentParser(description="NSF Awards Pipeline")
    parser.add_argument("start",                type=int, help="start year (e.g. 1960)")
    parser.add_argument("end",                  type=int, help="end year   (e.g. 2025)")
    parser.add_argument("--skip-download",      action="store_true", help="skip downloading zips")
    parser.add_argument("--skip-extract",       action="store_true", help="skip extracting JSONs")
    parser.add_argument("--skip-parse",         action="store_true", help="skip parsing JSONs")
    parser.add_argument("--skip-mappings",      action="store_true", help="skip building abbreviation maps")
    parser.add_argument("--skip-aggregate",     action="store_true", help="skip aggregation & writing research.json")
    parser.add_argument("--skip-taxonomy",      action="store_true", help="skip taxonomy.json/tsv")
    parser.add_argument("--skip-visualize",     action="store_true", help="skip plotting charts")
    parser.add_argument("--skip-missionscrape", action="store_true", help="skip scraping division missions")
    parser.add_argument("--skip-export", action="store_true", help="skip export")
    parser.add_argument("--year-sort",          type=int, default=None,
                        help="also write research_{year}.json sorted by that year's funding")
    args = parser.parse_args()

    years = range(args.start, args.end + 1)
    mapping_done = False

    # 1) DOWNLOAD
    if not args.skip_download:
        download_all(years)
    else:
        print("Skipping download.")

    # 2) EXTRACT
    if not args.skip_extract:
        extract_all()
    else:
        print("Skipping extract.")

    # 3) PARSE
    records = []
    if not args.skip_parse:
        records = parse_all(DATA_DIR, max_workers=MAX_PARSE_WORKERS)
    else:
        print("Skipping parse.")

    # 4) MAPPINGS
    if not args.skip_mappings and records:
        build_maps(records, str(OUTPUT_DIR))
        mapping_done = True
    else:
        print("Skipping mappings.")

    if not args.skip_export:
        export_awards()
    else:
        print("Skipping award‐level export.")

    # 5) AGGREGATION → research.json / research_brief.json
    if not args.skip_aggregate and records:
        hierarchy = build_hierarchy(records)

        sorted_full    = sort_hierarchy(hierarchy)
        brief_unsorted = {d: make_brief(sub) for d, sub in hierarchy.items()}
        sorted_brief   = sort_hierarchy(brief_unsorted)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "research.json").write_text(json.dumps(sorted_full, indent=2))
        print("✔ Wrote research.json")
        (OUTPUT_DIR / "research_brief.json").write_text(json.dumps(sorted_brief, indent=2))
        print("✔ Wrote research_brief.json")

        if args.year_sort:
            sr = sort_hierarchy_by_year(hierarchy, args.year_sort)
            p = OUTPUT_DIR / f"research_{args.year_sort}.json"
            p.write_text(json.dumps(sr, indent=2))
            print(f"✔ Wrote {p.name}")
    else:
        print("Skipping aggregation/research outputs.")

    # 6) TAXONOMY
    if not args.skip_taxonomy:
        generate_taxonomy(str(OUTPUT_DIR / "research.json"), str(OUTPUT_DIR))
    else:
        print("Skipping taxonomy.")

    # 7) VISUALIZE
    if not args.skip_visualize:
        run_visualization(str(OUTPUT_DIR / "research.json"))
    else:
        print("Skipping visualization.")

    # 8) MISSION SCRAPE
    if mapping_done and not args.skip_missionscrape:
        scrape_missions(str(OUTPUT_DIR))
    else:
        print("Skipping mission scraping.")

    print("Done.")

if __name__ == "__main__":
    main()
