import os, requests
from config import validate_path

def download_asset(url, filename):
    rel_path = os.path.join("public", filename)
    abs_path = validate_path(rel_path)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
    response = requests.get(url, stream=True, timeout=20, headers=headers)
    response.raise_for_status()
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, 'wb') as f:
        for chunk in response.iter_content(8192): f.write(chunk)
    return f"Success: Downloaded {filename}."