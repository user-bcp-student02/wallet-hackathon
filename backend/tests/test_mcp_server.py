import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from app import mcp_server


def availability(total_records: int = 3) -> dict:
    return {
        "reconciliation_date": "2026-10-15",
        "channels": [
            {
                "channel": "qr",
                "source_counts": {"wallet": 1, "provider": 1, "ledger": 1},
                "total_records": total_records,
                "reconciliation_exists": False,
            }
        ],
    }


def report() -> dict:
    return {
        "run_id": 42,
        "reconciliation_date": "2026-10-15",
        "channel": "qr",
        "summary": {
            "transaction_count": 1,
            "reconciled_count": 1,
            "unreconciled_count": 0,
            "resolved_count": 0,
            "resolved_discrepancy_count": 0,
        },
        "discrepancies": [],
    }


def test_run_reconciliation_returns_existing_report_without_post(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []

    def fake_request(method: str, path: str, payload=None):
        calls.append((method, path))
        if path.startswith("/api/v1/records/availability"):
            return availability()
        if path.startswith("/api/v1/reconciliations?"):
            return [report()]
        raise AssertionError(f"Unexpected API request: {method} {path}")

    monkeypatch.setattr(mcp_server, "_api_request", fake_request)

    result = mcp_server.run_reconciliation("2026-10-15", "qr")

    assert result == {"created": False, "report": report()}
    assert all(method != "POST" for method, _ in calls)


def test_run_reconciliation_does_not_create_empty_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []

    def fake_request(method: str, path: str, payload=None):
        calls.append((method, path))
        if path.startswith("/api/v1/records/availability"):
            return availability(total_records=0)
        raise AssertionError(f"Unexpected API request: {method} {path}")

    monkeypatch.setattr(mcp_server, "_api_request", fake_request)

    with pytest.raises(ValueError, match="no reconciliation was created"):
        mcp_server.run_reconciliation("2026-10-15", "qr")

    assert all(method != "POST" for method, _ in calls)


def test_run_reconciliation_creates_and_reads_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str]] = []

    def fake_request(method: str, path: str, payload=None):
        calls.append((method, path))
        if path.startswith("/api/v1/records/availability"):
            return availability()
        if path.startswith("/api/v1/reconciliations?"):
            return []
        if method == "POST" and path == "/api/v1/reconciliations":
            assert payload == {
                "reconciliation_date": "2026-10-15",
                "channel": "qr",
            }
            return {"id": 42}
        if method == "GET" and path == "/api/v1/reconciliations/42":
            return report()
        raise AssertionError(f"Unexpected API request: {method} {path}")

    monkeypatch.setattr(mcp_server, "_api_request", fake_request)

    result = mcp_server.run_reconciliation("2026-10-15", "qr")

    assert result == {"created": True, "report": report()}
    assert ("POST", "/api/v1/reconciliations") in calls


def test_run_reconciliation_recovers_concurrent_duplicate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    reports = 0

    def fake_request(method: str, path: str, payload=None):
        nonlocal reports
        if path.startswith("/api/v1/records/availability"):
            return availability()
        if path.startswith("/api/v1/reconciliations?"):
            reports += 1
            return [] if reports == 1 else [report()]
        if method == "POST":
            raise mcp_server.ApiError(409, "Run already exists.")
        raise AssertionError(f"Unexpected API request: {method} {path}")

    monkeypatch.setattr(mcp_server, "_api_request", fake_request)

    result = mcp_server.run_reconciliation("2026-10-15", "qr")

    assert result == {"created": False, "report": report()}


def test_mcp_tools_validate_dates_and_require_exact_channel() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        mcp_server.list_available_reconciliation_data("2026-02-30")

    with pytest.raises(ValueError, match="must not be blank"):
        mcp_server.get_reconciliation_report("2026-10-15", "  ")


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.anyio
async def test_mcp_server_publishes_only_read_and_reconciliation_tools() -> None:
    async with create_connected_server_and_client_session(mcp_server.mcp) as client:
        response = await client.list_tools()

    assert {tool.name for tool in response.tools} == {
        "list_available_reconciliation_data",
        "run_reconciliation",
        "get_reconciliation_report",
        "get_daily_reconciliation_summary",
    }


@pytest.mark.anyio
async def test_mcp_server_dispatches_availability_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expected = availability()

    def fake_request(method: str, path: str, payload=None):
        assert method == "GET"
        assert path == "/api/v1/records/availability?reconciliation_date=2026-10-15"
        return expected

    monkeypatch.setattr(mcp_server, "_api_request", fake_request)

    async with create_connected_server_and_client_session(mcp_server.mcp) as client:
        response = await client.call_tool(
            "list_available_reconciliation_data",
            {"reconciliation_date": "2026-10-15"},
        )

    assert not response.isError
    assert response.structuredContent == expected
