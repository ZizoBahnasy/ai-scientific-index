import requests
from pathlib import Path

def download_year(year: int, data_dir: Path) -> Path:
    """
    Downloads the NSF awards ZIP for a given year if not already present.
    """
    url  = f"https://www.nsf.gov/awardsearch/download?DownloadFileName={year}&All=true&isJson=true"
    dest = data_dir / f"{year}.zip"
    if dest.exists():
        return dest

    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    with open(dest, "wb") as out:
        for chunk in resp.iter_content(chunk_size=1024*1024):
            out.write(chunk)
    return dest
