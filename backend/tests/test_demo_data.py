from datetime import date
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base
from app.demo_data import seed_demo_data, seed_previous_demo_days
from app.main import demo_data_enabled
from app.models import ReconciliationRun, SourceRecord


def test_operational_timezone_is_available() -> None:
    assert ZoneInfo("America/Lima").key == "America/Lima"


def test_demo_data_is_enabled_by_default_only_outside_production(
    monkeypatch,
) -> None:
    monkeypatch.delenv("SEED_DEMO_DATA", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    assert demo_data_enabled() is True

    monkeypatch.setenv("APP_ENV", "production")
    assert demo_data_enabled() is False

    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("SEED_DEMO_DATA", "false")
    assert demo_data_enabled() is False


def test_demo_seed_creates_source_data_without_runs_and_is_idempotent() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    business_date = date(2026, 10, 16)

    with Session(engine) as session:
        assert seed_demo_data(session, business_date) is True
        assert seed_demo_data(session, business_date) is False

        assert session.scalar(select(func.count()).select_from(SourceRecord)) == 14
        assert session.scalar(select(func.count()).select_from(ReconciliationRun)) == 0

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_demo_seed_preserves_existing_records_and_adds_synthetic_data() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(
            SourceRecord(
                source="wallet",
                transaction_reference="real-existing-reference",
                transaction_date=date(2026, 10, 16),
                channel="qr",
                amount_minor=1000,
                currency="PEN",
            )
        )
        session.commit()

        assert seed_demo_data(session, date(2026, 10, 16)) is True
        assert session.scalar(select(func.count()).select_from(SourceRecord)) == 15
        assert session.scalar(
            select(func.count())
            .select_from(SourceRecord)
            .where(SourceRecord.transaction_reference == "real-existing-reference")
        ) == 1
        assert session.scalar(select(func.count()).select_from(ReconciliationRun)) == 0

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_previous_five_demo_days_are_seeded_without_creating_runs() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    current_date = date(2026, 10, 16)
    expected_dates = [
        date(2026, 10, 11),
        date(2026, 10, 12),
        date(2026, 10, 13),
        date(2026, 10, 14),
        date(2026, 10, 15),
    ]

    with Session(engine) as session:
        assert seed_previous_demo_days(session, current_date) == expected_dates
        assert seed_previous_demo_days(session, current_date) == []
        assert session.scalar(select(func.count()).select_from(SourceRecord)) == 70
        assert session.scalar(select(func.count()).select_from(ReconciliationRun)) == 0
        seeded_dates = session.scalars(
            select(SourceRecord.transaction_date).distinct().order_by(
                SourceRecord.transaction_date
            )
        ).all()
        assert seeded_dates == expected_dates

    Base.metadata.drop_all(engine)
    engine.dispose()
