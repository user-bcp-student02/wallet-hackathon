from datetime import date, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import RecordSource, SourceRecord


def seed_demo_data(session: Session, business_date: date) -> bool:
    reference_prefix = f"demo-{business_date:%Y%m%d}"
    existing_demo_records = session.scalar(
        select(func.count())
        .select_from(SourceRecord)
        .where(SourceRecord.transaction_reference.like(f"{reference_prefix}-%"))
    )
    if existing_demo_records:
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
    session.add_all(records)
    session.commit()
    return True


def seed_previous_demo_days(
    session: Session, current_date: date, days: int = 5
) -> list[date]:
    seeded_dates = []
    for offset in range(days, 0, -1):
        business_date = current_date - timedelta(days=offset)
        if seed_demo_data(session, business_date):
            seeded_dates.append(business_date)
    return seeded_dates
