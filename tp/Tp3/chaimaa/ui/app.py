"""Interface Streamlit de MaintAI."""
import httpx
import pandas as pd
import streamlit as st

from maintai.client import APIError, MaintaiClient
from maintai.config import FEATURES, get_settings

st.set_page_config(page_title="MaintAI", page_icon="??")
st.title("MaintAI ? pr?diction de panne")


@st.cache_data
def charger(path) -> pd.DataFrame:
    return pd.read_csv(path)


with st.sidebar:
    url = st.text_input("URL de l'API", "http://localhost:8000")
    cle = st.text_input("Cl? API", type="password")

onglet_donnees, onglet_prediction = st.tabs(["Donn?es", "Pr?diction"])

# Sprint 1 : exploration des donn?es
with onglet_donnees:
    df = charger(get_settings().data_path)

    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de relev?s", f"{len(df)}")
    col2.metric("Taux de panne", f"{df['failure'].mean() * 100:.1f} %")
    col3.metric("Temp?rature moyenne", f"{df['temperature_c'].mean():.1f} ?C")

    default_index = list(FEATURES).index("vibration_mm_s") if "vibration_mm_s" in FEATURES else 0
    variable = st.selectbox("Variable ? analyser", list(FEATURES), index=default_index)

    tranches = pd.cut(df[variable], bins=10)
    taux_par_tranche = (
        df.assign(tranche=tranches)
        .groupby("tranche", observed=False)["failure"]
        .mean()
        .dropna()
    )

    st.subheader(f"Taux de panne selon {variable}")
    taux_par_tranche.index = taux_par_tranche.index.astype(str)
    st.bar_chart(taux_par_tranche * 100)

    st.subheader("Temp?rature et vibration")
    st.scatter_chart(
        df,
        x="temperature_c",
        y="vibration_mm_s",
        color="failure"
    )

# Sprint 2 : pr?diction via l'API
with onglet_prediction:
    with st.form("releve"):
        releve = {
            "temperature_c": st.slider("Temp?rature (?C)", -40.0, 150.0, 72.0),
            "vibration_mm_s": st.slider("Vibration (mm/s)", 0.0, 50.0, 6.0),
            "load_pct": st.slider("Charge (%)", 0.0, 100.0, 85.0),
            "runtime_hours": st.number_input(
                "Heures de fonctionnement", 0, 100_000, 15000
            ),
        }
        envoye = st.form_submit_button("Pr?dire")

    if envoye:
        try:
            client = MaintaiClient(url, api_key=cle or None)
            resultat = client.predict(releve)

            pct = round(float(resultat["failure_probability"]) * 100)
            st.metric("Probabilit? de panne", f"{pct} %")

            if resultat.get("alert"):
                st.error("ALERTE : risque de panne ?lev?.")
            else:
                st.success("Situation normale : pas d'alerte.")

        except APIError as exc:
            st.warning(f"Erreur API ({exc.status_code}) : {exc.detail}")
        except httpx.HTTPError as exc:
            st.error(f"API injoignable : {exc}")

