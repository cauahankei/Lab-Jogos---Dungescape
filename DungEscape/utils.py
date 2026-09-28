from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def asset_path(*parts):
    return str(BASE_DIR.joinpath(*parts))