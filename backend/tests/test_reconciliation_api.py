from collections.abc import Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_session
from app.main import create_app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("SEED_DEMO_DATA", "false")
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(test_engine)
    test_session = sessionmaker(
        bind=test_engine, autoflush=False, expire_on_commit=False
    )

    def override_session():
        with test_session() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(test_engine)
    test_engine.dispose()


def load(client: TestClient, source: str, records: list[dict]) -> None:
    response = client.post(
        f"/api/v1/records/{source}",
        json={"records": records},
    )
    assert response.status_code == 201, response.text


def record(reference: str, amount: int = 1000, **values: object) -> dict:
    return {
        "transaction_reference": reference,
        "transaction_date": "2026-10-15",
        "channel": "qr",
        "amount_minor": amount,
        "currency": "PEN",
        **values,
    }


def reconcile(client: TestClient, channel: str, transaction_date: str = "2026-10-15") -> dict:
    response = client.post(
        "/api/v1/reconciliations",
        json={"reconciliation_date": transaction_date, "channel": channel},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_reconciles_matching_sources_and_reports_summary(client: TestClient) -> None:
    for source, extra in (
        ("wallet", {}),
        ("provider", {"status": "SUCCESS"}),
        ("ledger", {}),
    ):
        load(client, source, [record("tx-001", **extra)])

    response = client.post(
        "/api/v1/reconciliations",
        json={"reconciliation_date": "2026-10-15", "channel": "qr"},
    )

    assert response.status_code == 201
    assert response.json()["summary"] == {
        "transaction_count": 1,
        "reconciled_count": 1,
        "unreconciled_count": 0,
        "resolved_count": 0,
    }


def test_finds_missing_records_and_tracks_resolution(client: TestClient) -> None:
    load(client, "wallet", [record("tx-missing-provider")])
    load(client, "ledger", [record("tx-missing-provider")])

    response = client.post(
        "/api/v1/reconciliations",
        json={"reconciliation_date": "2026-10-15", "channel": "qr"},
    )
    run_id = response.json()["id"]
    assert response.json()["summary"]["unreconciled_count"] == 1

    report = client.get(
        "/api/v1/reconciliations",
        params={"reconciliation_date": "2026-10-15", "channel": "qr"},
    ).json()[0]
    discrepancy = report["discrepancies"][0]
    assert discrepancy["discrepancy_type"] == "MISSING_PROVIDER_RESULT"

    resolved = client.patch(
        f"/api/v1/discrepancies/{discrepancy['id']}",
        json={
            "status": "RESOLVED",
            "investigation_note": "Provider confirmed the transaction manually.",
        },
    )
    assert resolved.status_code == 200
    assert client.get(f"/api/v1/reconciliations/{run_id}").json()["summary"] == {
        "transaction_count": 1,
        "reconciled_count": 0,
        "unreconciled_count": 0,
        "resolved_count": 1,
    }


def test_detects_amount_mismatch_and_duplicate_provider_result(
    client: TestClient,
) -> None:
    load(client, "wallet", [record("tx-amount")])
    load(
        client,
        "provider",
        [
            record("tx-amount", amount=1200, status="SUCCESS"),
            record("tx-amount", amount=1200, status="SUCCESS"),
        ],
    )
    load(client, "ledger", [record("tx-amount")])

    response = client.post(
        "/api/v1/reconciliations",
        json={"reconciliation_date": "2026-10-15", "channel": "qr"},
    )

    assert response.status_code == 201
    discrepancy_types = {
        item["discrepancy_type"]
        for item in client.get(
            f"/api/v1/reconciliations/{response.json()['id']}"
        ).json()["discrepancies"]
    }
    assert discrepancy_types == {
        "DUPLICATE_PROVIDER_RESULT",
        "AMOUNT_MISMATCH",
    }


def test_reports_all_discrepancy_types_with_reference_and_open_status(
    client: TestClient,
) -> None:
    load(client, "provider", [record("missing-wallet", status="SUCCESS")])
    load(client, "ledger", [record("missing-wallet")])

    load(client, "wallet", [record("missing-provider")])
    load(client, "ledger", [record("missing-provider")])

    load(client, "wallet", [record("missing-ledger")])
    load(client, "provider", [record("missing-ledger", status="SUCCESS")])

    load(client, "wallet", [record("duplicate-wallet"), record("duplicate-wallet")])
    load(client, "provider", [record("duplicate-wallet", status="SUCCESS")])
    load(client, "ledger", [record("duplicate-wallet")])

    load(client, "wallet", [record("duplicate-provider")])
    load(
        client,
        "provider",
        [
            record("duplicate-provider", status="SUCCESS"),
            record("duplicate-provider", status="SUCCESS"),
        ],
    )
    load(client, "ledger", [record("duplicate-provider")])

    load(client, "wallet", [record("duplicate-ledger")])
    load(client, "provider", [record("duplicate-ledger", status="SUCCESS")])
    load(client, "ledger", [record("duplicate-ledger"), record("duplicate-ledger")])

    load(client, "wallet", [record("channel-mismatch", channel="qr")])
    load(client, "provider", [record("channel-mismatch", channel="p2p", status="SUCCESS")])
    load(client, "ledger", [record("channel-mismatch", channel="qr")])

    load(client, "wallet", [record("currency-mismatch")])
    load(client, "provider", [record("currency-mismatch", currency="USD", status="SUCCESS")])
    load(client, "ledger", [record("currency-mismatch")])

    load(client, "wallet", [record("provider-failed")])
    load(client, "provider", [record("provider-failed", status="FAILED")])
    load(client, "ledger", [record("provider-failed")])

    load(client, "wallet", [record("provider-pending")])
    load(client, "provider", [record("provider-pending", status="PENDING")])
    load(client, "ledger", [record("provider-pending")])

    load(client, "wallet", [record("partial-comparison", amount=1000)])
    load(
        client,
        "provider",
        [
            record(
                "partial-comparison",
                amount=1200,
                channel="p2p",
                status="FAILED",
            )
        ],
    )

    run = reconcile(client, "qr")
    report = client.get(f"/api/v1/reconciliations/{run['id']}").json()
    findings = {
        (item["transaction_reference"], item["discrepancy_type"], item["status"])
        for item in report["discrepancies"]
    }
    assert findings == {
        ("missing-wallet", "MISSING_WALLET_RECORD", "OPEN"),
        ("missing-provider", "MISSING_PROVIDER_RESULT", "OPEN"),
        ("missing-ledger", "MISSING_LEDGER_ENTRY", "OPEN"),
        ("duplicate-wallet", "DUPLICATE_WALLET_RECORD", "OPEN"),
        ("duplicate-provider", "DUPLICATE_PROVIDER_RESULT", "OPEN"),
        ("duplicate-ledger", "DUPLICATE_LEDGER_ENTRY", "OPEN"),
        ("channel-mismatch", "CHANNEL_MISMATCH", "OPEN"),
        ("currency-mismatch", "CURRENCY_MISMATCH", "OPEN"),
        ("provider-failed", "PROVIDER_NOT_SUCCESSFUL", "OPEN"),
        ("provider-pending", "PROVIDER_NOT_SUCCESSFUL", "OPEN"),
        ("partial-comparison", "MISSING_LEDGER_ENTRY", "OPEN"),
        ("partial-comparison", "CHANNEL_MISMATCH", "OPEN"),
        ("partial-comparison", "AMOUNT_MISMATCH", "OPEN"),
        ("partial-comparison", "PROVIDER_NOT_SUCCESSFUL", "OPEN"),
    }


def test_filters_reports_and_aggregates_daily_summary_across_channels(
    client: TestClient,
) -> None:
    load(client, "wallet", [record("qr-ok", channel="qr")])
    load(client, "provider", [record("qr-ok", channel="qr", status="SUCCESS")])
    load(client, "ledger", [record("qr-ok", channel="qr")])

    load(client, "wallet", [record("p2p-open", channel="p2p")])
    load(client, "ledger", [record("p2p-open", channel="p2p")])

    load(client, "wallet", [record("other-day", transaction_date="2026-10-14")])
    load(client, "provider", [record("other-day", transaction_date="2026-10-14", status="SUCCESS")])
    load(client, "ledger", [record("other-day", transaction_date="2026-10-14")])

    reconcile(client, "qr")
    p2p_run = reconcile(client, "p2p")
    reconcile(client, "qr", "2026-10-14")

    by_date = client.get(
        "/api/v1/reconciliations",
        params={"reconciliation_date": "2026-10-15"},
    )
    by_channel = client.get(
        "/api/v1/reconciliations",
        params={"reconciliation_date": "2026-10-15", "channel": "p2p"},
    )
    assert len(by_date.json()) == 2
    assert [report["channel"] for report in by_channel.json()] == ["p2p"]

    p2p_discrepancy = by_channel.json()[0]["discrepancies"][0]
    resolved = client.patch(
        f"/api/v1/discrepancies/{p2p_discrepancy['id']}",
        json={
            "status": "RESOLVED",
            "investigation_note": "Provider record verified by operations.",
        },
    )
    assert resolved.status_code == 200

    daily = client.get(
        "/api/v1/reconciliations/daily-summary",
        params={"reconciliation_date": "2026-10-15"},
    )
    assert daily.status_code == 200
    assert daily.json() == {
        "reconciliation_date": "2026-10-15",
        "channels": ["p2p", "qr"],
        "summary": {
            "transaction_count": 2,
            "reconciled_count": 1,
            "unreconciled_count": 0,
            "resolved_count": 1,
        },
    }

    empty_day = client.get(
        "/api/v1/reconciliations/daily-summary",
        params={"reconciliation_date": "2026-10-13"},
    )
    assert empty_day.json()["summary"] == {
        "transaction_count": 0,
        "reconciled_count": 0,
        "unreconciled_count": 0,
        "resolved_count": 0,
    }


def test_rejects_missing_provider_status_and_duplicate_daily_run(
    client: TestClient,
) -> None:
    invalid = client.post(
        "/api/v1/records/provider",
        json={"records": [record("tx-no-status")]},
    )
    assert invalid.status_code == 422

    payload = {"reconciliation_date": date(2026, 10, 15).isoformat(), "channel": "qr"}
    assert client.post("/api/v1/reconciliations", json=payload).status_code == 201
    assert client.post("/api/v1/reconciliations", json=payload).status_code == 409


def test_exposes_openapi_contract_and_interactive_docs(client: TestClient) -> None:
    schema_response = client.get("/openapi.json")
    assert schema_response.status_code == 200
    schema = schema_response.json()
    assert schema["info"]["title"] == "API de conciliación de billetera"
    assert "/api/v1/reconciliations/daily-summary" in schema["paths"]
    assert schema["paths"]["/api/v1/records/{source}"]["post"]["tags"] == [
        "Registros de origen"
    ]
    assert schema["paths"]["/api/v1/reconciliations"]["post"]["summary"] == (
        "Ejecutar una conciliación diaria"
    )
    assert schema["components"]["schemas"]["SourceRecordBatch"]["title"] == (
        "Lote de registros de origen"
    )
    assert schema["components"]["schemas"]["HTTPValidationError"]["title"] == (
        "Respuesta de validación"
    )
    assert schema["components"]["schemas"]["DiscrepancyType"]["title"] == (
        "Tipo de descalce"
    )
    assert schema["components"]["schemas"]["SourceRecordInput"]["properties"][
        "transaction_reference"
    ]["title"] == "Referencia de transacción"
    assert schema["components"]["schemas"]["DiscrepancyResponse"]["properties"][
        "discrepancy_type"
    ]["title"] == "Tipo de descalce"
    assert schema["components"]["schemas"]["HTTPValidationError"]["properties"][
        "detail"
    ]["description"] == "Lista de errores encontrados al validar los datos enviados."
    operations = schema["paths"]
    assert set(
        operations["/api/v1/records/{source}"]["post"]["requestBody"]["content"][
            "application/json"
        ]["examples"]
    ) == {"billetera", "proveedor", "libro_contable"}
    assert "corrida_creada" in operations["/api/v1/reconciliations"]["post"][
        "responses"
    ]["201"]["content"]["application/json"]["examples"]
    assert "reportes_del_dia" in operations["/api/v1/reconciliations"]["get"][
        "responses"
    ]["200"]["content"]["application/json"]["examples"]
    assert "resolver_descalce" in operations[
        "/api/v1/discrepancies/{discrepancy_id}"
    ]["patch"]["requestBody"]["content"]["application/json"]["examples"]
    assert "estado_de_proveedor_obligatorio" in operations[
        "/api/v1/records/{source}"
    ]["post"]["responses"]["422"]["content"]["application/json"]["examples"]
    assert "corrida_duplicada" in operations["/api/v1/reconciliations"]["post"][
        "responses"
    ]["409"]["content"]["application/json"]["examples"]
    assert "corrida_inexistente" in operations[
        "/api/v1/reconciliations/{run_id}"
    ]["get"]["responses"]["404"]["content"]["application/json"]["examples"]
    assert "no_reabrir" in operations[
        "/api/v1/discrepancies/{discrepancy_id}"
    ]["patch"]["responses"]["409"]["content"]["application/json"]["examples"]
    for path in schema["paths"].values():
        for operation in path.values():
            for response in operation.get("responses", {}).values():
                assert response["description"] != "Successful Response"
                assert response["description"] != "Validation Error"
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
