import hashlib
import os
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(r"e:\My\the20\test_strategy\commodity source\commodity_equilibrium")
MANIFEST_FILE = BASE_DIR / "01_source_registry" / "download_manifest.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/"
}

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def record_manifest(file_id, metal, source_id, file_name, file_url, file_format, file_size, status, local_path, sha256_hash=""):
    record = {
        "file_id": file_id,
        "metal": metal,
        "source_id": source_id,
        "file_name": file_name,
        "file_url": file_url,
        "file_format": file_format,
        "file_size_bytes": file_size,
        "download_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sha256_checksum": sha256_hash,
        "download_status": status,
        "local_path": str(local_path)
    }
    df_new = pd.DataFrame([record])
    if MANIFEST_FILE.exists():
        df_existing = pd.read_csv(MANIFEST_FILE)
        # Avoid duplicate row for same file_id
        df_existing = df_existing[df_existing["file_id"] != file_id]
        df_out = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_out = df_new
    df_out.to_csv(MANIFEST_FILE, index=False, encoding="utf-8")

def download_file(url, target_path, file_id, metal, source_id, custom_headers=None, timeout=30):
    headers = custom_headers or HEADERS
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if already exists and non-empty
    if target_path.exists() and target_path.stat().st_size > 0:
        size = target_path.stat().st_size
        sha = compute_sha256(target_path)
        print(f"[EXISTS] {target_path.name} ({size} bytes, sha: {sha[:8]}...)")
        record_manifest(file_id, metal, source_id, target_path.name, url, target_path.suffix.lstrip("."), size, "SUCCESS_CACHED", target_path, sha)
        return True
        
    try:
        session = requests.Session()
        r = session.get(url, headers=headers, timeout=timeout, stream=True)
        if r.status_code == 200:
            with open(target_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=16384):
                    if chunk:
                        f.write(chunk)
            size = target_path.stat().st_size
            sha = compute_sha256(target_path)
            print(f"[DOWNLOADED] {target_path.name} ({size} bytes, sha: {sha[:8]}...)")
            record_manifest(file_id, metal, source_id, target_path.name, url, target_path.suffix.lstrip("."), size, "SUCCESS", target_path, sha)
            return True
        else:
            print(f"[FAILED] {url} -> Status {r.status_code}")
            record_manifest(file_id, metal, source_id, target_path.name, url, target_path.suffix.lstrip("."), 0, f"FAILED_HTTP_{r.status_code}", target_path)
            return False
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        record_manifest(file_id, metal, source_id, target_path.name, url, target_path.suffix.lstrip("."), 0, f"ERROR_{type(e).__name__}", target_path)
        return False
