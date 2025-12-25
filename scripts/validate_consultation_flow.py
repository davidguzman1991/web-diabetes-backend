import json
import os
from pathlib import Path
from urllib import request, error

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
CEDULA = os.getenv("TEST_CEDULA", "0908762115")


def _post(path: str, payload: dict, token: str | None = None):
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(f"{BASE_URL}{path}", data=body, headers=headers, method="POST")
    with request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def _get(path: str, token: str | None = None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(f"{BASE_URL}{path}", headers=headers, method="GET")
    with request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def main():
    if not ADMIN_PASSWORD:
        raise SystemExit("ADMIN_PASSWORD is missing in .env")

    status, token_data = _post(
        "/auth/admin/login", {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
    )
    if status != 200:
        raise SystemExit(f"Login failed: {token_data}")
    token = token_data.get("access_token")
    if not token:
        raise SystemExit("No token returned")

    payload = {
        "cedula": CEDULA,
        "fecha": "2025-12-25",
        "diagnosis": "Diabetes mellitus tipo 2 en control",
        "notes": "Paciente estable, se ajusta tratamiento.",
        "indications": "Continuar controles y adherencia.",
        "medications": [
            {
                "drug_name": "Metformina",
                "dose": "850 mg",
                "route": "VO",
                "frequency": "cada 12 horas",
                "duration": "30 dias",
                "indications": "Tomar con comida",
                "sort_order": 1,
            }
        ],
    }

    status, created = _post("/admin/consultations", payload, token=token)
    print("POST /admin/consultations", status, created)

    status, listed = _get(f"/admin/consultations?cedula={CEDULA}", token=token)
    print("GET /admin/consultations", status, listed)


if __name__ == "__main__":
    try:
        main()
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise SystemExit(f"HTTPError {exc.code}: {body}") from exc
