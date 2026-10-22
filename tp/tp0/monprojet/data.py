"""Chargement des données et découpage entraînement / test."""
import pandas as pd
from sklearn.model_selection import train_test_split

from . import config


def load_data() -> pd.DataFrame:
    """Lit le CSV. Si une colonne de date est donnée, trie les lignes dans l'ordre du temps."""
    df = pd.read_csv(config.DATA_PATH)
    if config.TIME_COLUMN:
        df[config.TIME_COLUMN] = pd.to_datetime(df[config.TIME_COLUMN])
        df = df.sort_values(config.TIME_COLUMN).reset_index(drop=True)
    return df


def get_xy(df: pd.DataFrame):
    """Sépare les informations (X) de la colonne à prédire (y)."""
    y = df[config.TARGET]
    if config.FEATURES is not None:
        columns = list(config.FEATURES)
    else:
        columns = [c for c in df.columns if c != config.TARGET]
    if config.TIME_COLUMN in columns:
        columns.remove(config.TIME_COLUMN)  # la date brute n'est pas une information utile
    return df[columns], y


def split_data(df: pd.DataFrame):
    """Retourne X_train, X_test, y_train, y_test."""
    X, y = get_xy(df)
    if config.SPLIT == "chronologique":
        if not config.TIME_COLUMN:
            raise ValueError("SPLIT = 'chronologique' demande une TIME_COLUMN.")
        cut = int(len(df) * (1 - config.TEST_SIZE))  # on coupe dans l'ordre du temps
        return X.iloc[:cut], X.iloc[cut:], y.iloc[:cut], y.iloc[cut:]
    stratify = y if config.TASK == "classification" else None
    return train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.SEED, stratify=stratify
    )
