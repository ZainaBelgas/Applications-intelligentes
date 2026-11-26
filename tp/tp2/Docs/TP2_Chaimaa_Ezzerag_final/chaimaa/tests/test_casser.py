import pytest


VALID = {"temperature_c": 60, "vibration_mm_s": 2, "load_pct": 50, "runtime_hours": 5000}


@pytest.mark.parametrize(("route", "payload", "expected"), [
    ("/v1/predict", {k: v for k, v in VALID.items() if k != "load_pct"}, 422),
    ("/v1/predict", {**VALID, "temperature_c": 500}, 422),
    ("/v1/predict", {**VALID, "temperature_c": "chaud"}, 422),
    ("/v1/predict", {**VALID, "inconnu": 1}, 422),
    ("/v1/predictt", VALID, 404),
])
def test_requete_invalide(client, route, payload, expected):
    response = client.post(route, json=payload, headers={"X-API-Key": "test-key"})
    assert response.status_code == expected
