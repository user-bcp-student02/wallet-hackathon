from datetime import date

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from app.database import Base
from app.demo_data import seed_demo_data
from app.main import demo_data_enabled
from app.models import Discrepancy, ReconciliationRun, SourceRecord


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


def test_demo_seed_creates_reconciliations_and_is_idempotent() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    business_date = date(2026, 10, 16)

    with Session(engine) as session:
        assert seed_demo_data(session, business_date) is True
        assert seed_demo_data(session, business_date) is False

        assert session.scalar(select(func.count()).select_from(SourceRecord)) == 14
        assert session.scalar(select(func.count()).select_from(ReconciliationRun)) == 2
        assert session.scalar(select(func.count()).select_from(Discrepancy)) == 3

        runs = session.scalars(
            select(ReconciliationRun).order_by(ReconciliationRun.channel)
        ).all()
        assert [(run.channel, run.transaction_count, run.reconciled_count) for run in runs] == [
            ("p2p", 2, 1),
            ("qr", 3, 1),
        ]

    Base.metadata.drop_all(engine)
    engine.dispose()


def test_demo_seed_does_not_add_records_to_a_nonempty_database() -> None:
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

        assert seed_demo_data(session, date(2026, 10, 16)) is False
        assert session.scalar(select(func.count()).select_from(SourceRecord)) == 1
        assert session.scalar(select(func.count()).select_from(ReconciliationRun)) == 0

    Base.metadata.drop_all(engine)
    engine.dispose()
