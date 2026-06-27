from pathlib import Path
import pandas as pd

DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)

def path(name: str) -> Path:
    return DATA_DIR / name

def init_csv(filename: str, columns):
    p = path(filename)
    if not p.exists():
        pd.DataFrame(columns=columns).to_csv(p, index=False)
    return p

def load_csv(filename: str, columns):
    p = init_csv(filename, columns)
    df = pd.read_csv(p)
    for col in columns:
        if col not in df.columns:
            df[col] = ''
    return df[columns]

def save_csv(filename: str, df: pd.DataFrame):
    df.to_csv(path(filename), index=False)
