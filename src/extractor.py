import zipfile
from pathlib import Path
from typing import List

def extract_awards(zip_path: Path, data_dir: Path) -> List[Path]:
    """
    Unzips the given year ZIP into data_dir/{year}/,
    deletes the original ZIP, and returns a list of JSON award file paths.
    """
    extract_dir = zip_path.with_suffix("")  # e.g. data/awards/2025
    if not extract_dir.exists():
        extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)
        zip_path.unlink()  # remove ZIP after success
    return list(extract_dir.rglob("*.json"))
