"""Entraîne les modèles, les compare sur le jeu de test et sauvegarde le meilleur.

Lancer depuis la racine du projet :
    python -m monprojet.train
"""
import json

import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)

from . import config
from .data import load_data, split_data
from .models import get_models

LOWER_IS_BETTER = {"mae", "rmse"}


def compute_metrics(y_true, y_pred) -> dict:
    """Calcule toutes les métriques du type de problème."""
    if config.TASK == "regression":
        return {
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "r2": float(r2_score(y_true, y_pred)),
        }
    average = "binary" if y_true.nunique() == 2 else "macro"
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "recall": float(recall_score(y_true, y_pred, average=average, zero_division=0)),
        "precision": float(precision_score(y_true, y_pred, average=average, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, average=average, zero_division=0)),
    }


def predict(model, X):
    """Prédictions du modèle. En classification, on applique le seuil d'alerte THRESHOLD."""
    if config.TASK == "classification" and hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)
        if proba.shape[1] == 2:
            return (proba[:, 1] >= getattr(config, "THRESHOLD", 0.5)).astype(int)
    return model.predict(X)


def baseline_predictions(df, X_test, y_train):
    """La méthode la plus simple, pour savoir si le modèle apporte quelque chose."""
    if config.TASK == "regression":
        col = getattr(config, "BASELINE_COLUMN", None)
        if col and col in df.columns:
            return df.loc[X_test.index, col].fillna(y_train.mean()), f"copie de « {col} »"
        return np.full(len(X_test), y_train.mean()), "moyenne de l'entraînement"
    majority = y_train.mode().iloc[0]
    return np.full(len(X_test), majority), "classe la plus fréquente"


def main() -> None:
    metric = config.MAIN_METRIC
    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)
    print(f"Données : {len(df)} lignes | entraînement : {len(y_train)} | test : {len(y_test)}")
    print(f"Problème : {config.TASK} | découpage : {config.SPLIT} | métrique principale : {metric}")
    if config.TASK == "classification":
        print(f"Seuil d'alerte : {getattr(config, 'THRESHOLD', 0.5)}")

    results = {}
    base_pred, base_name = baseline_predictions(df, X_test, y_train)
    results[f"Baseline ({base_name})"] = compute_metrics(y_test, base_pred)

    fitted = {}
    for name, model in get_models(X_train).items():
        model.fit(X_train, y_train)
        fitted[name] = model
        results[name] = compute_metrics(y_test, predict(model, X_test))

    names = list(results)
    reverse = metric not in LOWER_IS_BETTER
    names.sort(key=lambda n: results[n][metric], reverse=reverse)
    columns = list(next(iter(results.values())))

    print("\nRésultats sur le jeu de test (du meilleur au moins bon)")
    print("-" * 80)
    width = max(len(n) for n in names) + 2
    print(f"{'Modèle':<{width}}" + "".join(f"{c:>10}" for c in columns))
    for n in names:
        print(f"{n:<{width}}" + "".join(f"{results[n][c]:>10.3f}" for c in columns))

    best = next(n for n in names if n in fitted)
    print(f"\nMeilleur modèle ({metric}) : {best} -> {results[best][metric]:.3f}")

    config.MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(fitted[best], config.MODELS_DIR / "meilleur_modele.joblib")
    with open(config.MODELS_DIR / "resultats.json", "w", encoding="utf-8") as f:
        json.dump({"meilleur": best, "metrique": metric, "resultats": results}, f,
                  ensure_ascii=False, indent=2)
    print(f"Modèle et résultats enregistrés dans : {config.MODELS_DIR}")


if __name__ == "__main__":
    main()
