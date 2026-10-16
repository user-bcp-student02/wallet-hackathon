from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ReconciliationRun, RecordSource, SourceRecord
from app.reconciliation import build_reconciliation


def seed_demo_data(session: Session, business_date: date) -> bool:
    has_source_records = session.scalar(
        select(func.count()).select_from(SourceRecord)
    )
    has_reconciliation_runs = session.scalar(
        select(func.count()).select_from(ReconciliationRun)
    )
    if has_source_records or has_reconciliation_runs:
        return False

    reference_prefix = f"demo-{business_date:%Y%m%d}"
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
    session.flush()

    session.add_all(
        [
            build_reconciliation(session, business_date, "qr"),
            build_reconciliation(session, business_date, "p2p"),
        ]
    )
    session.commit()
    return True
