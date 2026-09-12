"""Acces aux CSV, sans dependance a Streamlit."""

from functools import lru_cache
from pathlib import Path
import unicodedata

import pandas as pd

from .errors import DatasetNotFoundError, MultiplePlayersFoundError, PlayerNotFoundError


DATA_DIR = Path(__file__).resolve().parents[1] / "data_csv"
DATASET_FILES = {
    "Liga": "liga_playerper90allstats.csv",
    "Ligue1": "ligue1_playerper90allstats.csv",
    "Big5": "player_2025_big5.csv",
}


def normalize_text(value: str) -> str:
    """Normalise un texte pour les recherches insensibles aux accents/casses."""

    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return " ".join(text.casefold().strip().split())


def _prepare_dataframe(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    result = df.copy()
    name_column = "PlayerName" if "PlayerName" in result.columns else "Player"
    result["_player_name"] = result[name_column].astype(str)
    result["_player_key"] = result["_player_name"].map(normalize_text)
    result["_dataset"] = dataset
    for column in result.columns:
        if column.startswith("_") or column in {"PlayerName", "Player", "Team", "Squad", "Nation", "Pos", "Comp"}:
            continue
        converted = pd.to_numeric(result[column], errors="coerce")
        if converted.notna().all() or result[column].isna().all():
            result[column] = converted
    return result


@lru_cache(maxsize=None)
def load_dataset(dataset: str) -> pd.DataFrame:
    """Charge un dataset et conserve le filtre historique Min > 400."""

    if dataset not in DATASET_FILES:
        raise DatasetNotFoundError(
            f"Dataset inconnu : {dataset}. Valeurs autorisees : {', '.join(DATASET_FILES)}."
        )
    path = DATA_DIR / DATASET_FILES[dataset]
    if not path.exists():
        raise DatasetNotFoundError(f"Fichier de donnees introuvable : {path.name}.")
    df = pd.read_csv(path)
    if dataset in {"Liga", "Ligue1"} and "Min" in df.columns:
        df = df[df["Min"] > 400].copy()
    return _prepare_dataframe(df, dataset)


def public_record(row: pd.Series) -> dict:
    """Convertit une ligne pandas en dictionnaire serialisable par MCP."""

    record = {}
    for key, value in row.items():
        if str(key).startswith("_"):
            continue
        if pd.isna(value):
            record[key] = None
        elif hasattr(value, "item"):
            record[key] = value.item()
        else:
            record[key] = value
    record["dataset"] = row.get("_dataset")
    return record


def normalize_position(position: str) -> str:
    aliases = {
        "gardien": "GK", "goalkeeper": "GK", "defenseur": "DF",
        "defenseur central": "CB", "lateral": "FB", "milieu": "MF",
        "milieux": "MF", "midfielder": "MF", "milieu offensif": "AM",
        "attaquant": "FW", "attaquants": "FW", "forward": "FW",
    }
    return aliases.get(normalize_text(position), position.upper().strip())


def position_matches(value: str, requested: str) -> bool:
    positions = {part.strip().upper() for part in str(value).split(",")}
    return normalize_position(requested) in positions


def search_rows(player_name: str, dataset: str = "Big5") -> pd.DataFrame:
    df = load_dataset(dataset)
    key = normalize_text(player_name)
    exact = df[df["_player_key"] == key]
    return exact if not exact.empty else df[df["_player_key"].str.contains(key, regex=False, na=False)]


def get_one_player(player_name: str, dataset: str = "Big5") -> pd.Series:
    rows = search_rows(player_name, dataset)
    if rows.empty:
        raise PlayerNotFoundError(f"Aucun joueur correspondant a '{player_name}' dans {dataset}.")
    if len(rows) > 1:
        names = rows["_player_name"].drop_duplicates().tolist()
        raise MultiplePlayersFoundError(f"Plusieurs joueurs correspondent a '{player_name}' : {', '.join(names[:10])}.")
    return rows.iloc[0]
