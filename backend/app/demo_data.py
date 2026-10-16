from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import RecordSource, SourceRecord


def _timeout_records(business_date: date) -> list[SourceRecord]:
    reference = f"demo-{business_date:%Y%m%d}-p2p-003"
    return [
        SourceRecord(
            source=RecordSource.WALLET.value,
            transaction_reference=reference,
            transaction_date=business_date,
            channel="p2p",
            amount_minor=1200,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.PROVIDER.value,
            transaction_reference=reference,
            transaction_date=business_date,
            channel="p2p",
            amount_minor=1200,
            currency="PEN",
            status="TIMEOUT",
        ),
        SourceRecord(
            source=RecordSource.LEDGER.value,
            transaction_reference=reference,
            transaction_date=business_date,
            channel="p2p",
            amount_minor=1200,
            currency="PEN",
        ),
    ]


def seed_demo_data(
    session: Session, business_date: date, *, include_timeout: bool = False
) -> bool:
    reference_prefix = f"demo-{business_date:%Y%m%d}"
    existing_demo_records = session.scalar(
        select(func.count())
        .select_from(SourceRecord)
        .where(SourceRecord.transaction_reference.like(f"{reference_prefix}-%"))
    )
    if existing_demo_records:
        timeout_reference = f"{reference_prefix}-p2p-003"
        existing_timeout_records = session.scalar(
            select(func.count())
            .select_from(SourceRecord)
            .where(SourceRecord.transaction_reference == timeout_reference)
        )
        if include_timeout and not existing_timeout_records:
            session.add_all(_timeout_records(business_date))
            session.commit()
            return True
        return False

    records = [
        SourceRecord(
            source=RecordSource.WALLET.value,
            transaction_reference=f"{reference_prefix}-qr-001",
            transaction_date=business_date,
            channel="qr",
            amount_minor=2500,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.PROVIDER.value,
            transaction_reference=f"{reference_prefix}-qr-001",
            transaction_date=business_date,
            channel="qr",
            amount_minor=2500,
            currency="PEN",
            status="SUCCESS",
        ),
        SourceRecord(
            source=RecordSource.LEDGER.value,
            transaction_reference=f"{reference_prefix}-qr-001",
            transaction_date=business_date,
            channel="qr",
            amount_minor=2500,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.WALLET.value,
            transaction_reference=f"{reference_prefix}-qr-002",
            transaction_date=business_date,
            channel="qr",
            amount_minor=1500,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.PROVIDER.value,
            transaction_reference=f"{reference_prefix}-qr-002",
            transaction_date=business_date,
            channel="qr",
            amount_minor=1600,
            currency="PEN",
            status="SUCCESS",
        ),
        SourceRecord(
            source=RecordSource.LEDGER.value,
            transaction_reference=f"{reference_prefix}-qr-002",
            transaction_date=business_date,
            channel="qr",
            amount_minor=1500,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.WALLET.value,
            transaction_reference=f"{reference_prefix}-qr-003",
            transaction_date=business_date,
            channel="qr",
            amount_minor=700,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.LEDGER.value,
            transaction_reference=f"{reference_prefix}-qr-003",
            transaction_date=business_date,
            channel="qr",
            amount_minor=700,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.WALLET.value,
            transaction_reference=f"{reference_prefix}-p2p-001",
            transaction_date=business_date,
            channel="p2p",
            amount_minor=999,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.PROVIDER.value,
            transaction_reference=f"{reference_prefix}-p2p-001",
            transaction_date=business_date,
            channel="p2p",
            amount_minor=999,
            currency="PEN",
            status="SUCCESS",
        ),
        SourceRecord(
            source=RecordSource.LEDGER.value,
            transaction_reference=f"{reference_prefix}-p2p-001",
            transaction_date=business_date,
            channel="p2p",
            amount_minor=999,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.WALLET.value,
            transaction_reference=f"{reference_prefix}-p2p-002",
            transaction_date=business_date,
            channel="p2p",
            amount_minor=1800,
            currency="PEN",
        ),
        SourceRecord(
            source=RecordSource.PROVIDER.value,
            transaction_reference=f"{reference_prefix}-p2p-002",
            transaction_date=business_date,
            channel="p2p",
            amount_minor=1800,
            currency="PEN",
            status="PENDING",
        ),
        SourceRecord(
            source=RecordSource.LEDGER.value,
            transaction_reference=f"{reference_prefix}-p2p-002",
            transaction_date=business_date,
            channel="p2p",
            amount_minor=1800,
            currency="PEN",
        ),
    ]
    if include_timeout:
        records.extend(_timeout_records(business_date))
    session.add_all(records)
    session.commit()
    return True


def seed_previous_demo_days(
    session: Session, current_date: date, days: int = 14
) -> list[date]:
    seeded_dates = []
    for offset in range(days, 0, -1):
        business_date = current_date - timedelta(days=offset)
        include_timeout = offset in {3, 7, 12}
        if seed_demo_data(session, business_date, include_timeout=include_timeout):
            seeded_dates.append(business_date)
    return seeded_dates
