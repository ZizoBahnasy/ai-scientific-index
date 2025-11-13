#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from tqdm import tqdm

def scrape_missions(output_dir: str = "outputs"):
    out = Path(output_dir)
    div_map_path = out / "division_map.json"
    url_path     = out / "division_urls.txt"

    # Load raw division_map (abbr-only or dict)
    with div_map_path.open() as f:
        raw_div_map = json.load(f)  # { long_name: abbr  OR  long_name: {abbr, mission} }

    # Build inverse map abbr -> long_name
    inv_div = {}
    for longn, val in raw_div_map.items():
        if isinstance(val, dict):
            abbr = val.get("abbr")
        else:
            abbr = val
        if abbr:
            inv_div[abbr] = longn

    # Read URLs
    if not url_path.exists():
        raise FileNotFoundError(f"{url_path} not found: run mappings first.")
    urls = [u.strip() for u in url_path.read_text().splitlines() if u.strip()]

    missions = {}
    for url in tqdm(urls, desc="Scraping missions"):
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
        except Exception:
            continue

        soup = BeautifulSoup(res.text, "html.parser")
        div = soup.find("div",
            class_="clearfix text-formatted field field-org-msn-statement"
        )
        if not div:
            continue

        parts = []
        for el in div.find_all(["p", "li"]):
            text = el.get_text(" ", strip=True)
            if text:
                parts.append(text)
        mission = " ".join(parts)

        # Extract division abbr from URL
        parts = url.rstrip("/").split("/")
        d_abbr, v_abbr = parts[-2], parts[-1]
        longn = inv_div.get(v_abbr)
        if longn:
            missions[longn] = mission

    # Merge missions back into division_map
    new_map = {}
    for longn, val in raw_div_map.items():
        if isinstance(val, dict):
            abbr = val.get("abbr")
        else:
            abbr = val
        entry = {"abbr": abbr}
        if longn in missions:
            entry["mission"] = missions[longn]
        new_map[longn] = entry

    # Overwrite division_map.json
    with div_map_path.open("w") as f:
        json.dump(new_map, f, indent=2)
    print("✔ Updated division_map.json with mission statements")

if __name__ == "__main__":
    scrape_missions()
