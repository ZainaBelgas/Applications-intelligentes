"""Les modèles à comparer, et la préparation des colonnes."""
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from . import config


def build_preprocessor(X) -> ColumnTransformer:
    """Prépare chaque type de colonne : nombres, catégories (texte court), texte libre."""
    text = config.TEXT_COLUMN if config.TEXT_COLUMN in X.columns else None
    numeric = list(X.select_dtypes(include="number").columns)
    categorical = [c for c in X.columns if c not in numeric and c != text]

    parts = []
    if numeric:
        parts.append(
            ("nombres", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeric)
        )
    if categorical:
        parts.append(
            (
                "categories",
                make_pipeline(
                    SimpleImputer(strategy="most_frequent"),
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
                categorical,
            )
        )
    if text:
        parts.append(("texte", TfidfVectorizer(max_features=500), text))
    return ColumnTransformer(parts, sparse_threshold=0)


def get_models(X) -> dict:
    """Retourne les modèles à comparer, chacun avec sa préparation des données."""
    if config.TASK == "regression":
        models = {
            "Régression linéaire": LinearRegression(),
            "Arbre de décision": DecisionTreeRegressor(max_depth=5, random_state=config.SEED),
            "Forêt aléatoire": RandomForestRegressor(n_estimators=300, random_state=config.SEED),
            "Gradient boosting": GradientBoostingRegressor(random_state=config.SEED),
        }
    else:
        models = {
            "Régression logistique": LogisticRegression(class_weight="balanced", max_iter=1000),
            "Arbre de décision": DecisionTreeClassifier(
                max_depth=5, class_weight="balanced", random_state=config.SEED
            ),
            "Forêt aléatoire": RandomForestClassifier(
                n_estimators=300, class_weight="balanced", random_state=config.SEED
            ),
            "Gradient boosting": GradientBoostingClassifier(random_state=config.SEED),
        }
    return {
        name: Pipeline([("preparation", build_preprocessor(X)), ("modele", model)])
        for name, model in models.items()
    }
