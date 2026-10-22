"""Tests rapides : lancer avec la commande `pytest` depuis la racine du projet."""
import pytest

from monprojet import config
from monprojet.data import load_data, split_data
from monprojet.models import get_models


def test_les_donnees_contiennent_la_cible():
    df = load_data()
    assert config.TARGET in df.columns
    assert len(df) > 0


def test_decoupage_sans_melange_des_lignes():
    df = load_data()
    X_train, X_test, y_train, y_test = split_data(df)
    assert len(X_train) + len(X_test) == len(df)
    assert len(X_train) == len(y_train) and len(X_test) == len(y_test)


@pytest.mark.skipif(config.SPLIT != "chronologique", reason="découpage non chronologique")
def test_le_test_est_apres_l_entrainement():
    df = load_data()
    X_train, X_test, _, _ = split_data(df)
    assert df.loc[X_train.index, config.TIME_COLUMN].max() < df.loc[X_test.index, config.TIME_COLUMN].min()


def test_un_modele_s_entraine_et_predit():
    df = load_data()
    X_train, X_test, y_train, _ = split_data(df)
    model = next(iter(get_models(X_train).values()))
    model.fit(X_train, y_train)
    assert len(model.predict(X_test)) == len(X_test)
