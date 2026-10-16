from collections import defaultdict
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Discrepancy,
    DiscrepancyType,
    InvestigationStatus,
    ReconciliationRun,
    RecordSource,
    SourceRecord,
)
from app.schemas import ReconciliationSummary


SOURCE_MISSING_TYPES = {
    RecordSource.WALLET: DiscrepancyType.MISSING_WALLET_RECORD,
    RecordSource.PROVIDER: DiscrepancyType.MISSING_PROVIDER_RESULT,
    RecordSource.LEDGER: DiscrepancyType.MISSING_LEDGER_ENTRY,
}
SOURCE_DUPLICATE_TYPES = {
    RecordSource.WALLET: DiscrepancyType.DUPLICATE_WALLET_RECORD,
    RecordSource.PROVIDER: DiscrepancyType.DUPLICATE_PROVIDER_RESULT,
    RecordSource.LEDGER: DiscrepancyType.DUPLICATE_LEDGER_ENTRY,
}
REQUIRED_SOURCES = tuple(RecordSource)


def build_reconciliation(
    session: Session, reconciliation_date: date, channel: str
) -> ReconciliationRun:
    records = session.scalars(
        select(SourceRecord).where(SourceRecord.transaction_date == reconciliation_date)
    ).all()

    by_reference: dict[str, dict[RecordSource, list[SourceRecord]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for record in records:
        by_reference[record.transaction_reference][RecordSource(record.source)].append(
            record
        )

    selected = {
        reference: source_records
        for reference, source_records in by_reference.items()
        if any(record.channel == channel for items in source_records.values() for record in items)
    }
    run = ReconciliationRun(
        reconciliation_date=reconciliation_date,
        channel=channel,
        transaction_count=len(selected),
        reconciled_count=0,
    )

    for reference, source_records in selected.items():
        findings: list[tuple[DiscrepancyType, str]] = []
        for source in REQUIRED_SOURCES:
            source_items = source_records.get(source, [])
            if not source_items:
                findings.append(
                    (
                        SOURCE_MISSING_TYPES[source],
                        f"No {source.value} record was found for this transaction.",
                    )
                )
            elif len(source_items) > 1:
                findings.append(
                    (
                        SOURCE_DUPLICATE_TYPES[source],
                        f"Found {len(source_items)} {source.value} records for this transaction.",
                    )
                )

        wallet = source_records.get(RecordSource.WALLET, [])
        provider = source_records.get(RecordSource.PROVIDER, [])
        ledger = source_records.get(RecordSource.LEDGER, [])
        records_to_compare = [*wallet, *provider, *ledger]
        present_sources = sum(bool(items) for items in (wallet, provider, ledger))
        if present_sources > 1:
            all_records = records_to_compare
            if len({record.channel for record in all_records}) > 1:
                findings.append(
                    (
                        DiscrepancyType.CHANNEL_MISMATCH,
                        "Wallet, provider, and ledger channel values do not match.",
                    )
                )
            if len({record.amount_minor for record in all_records}) > 1:
                findings.append(
                    (
                        DiscrepancyType.AMOUNT_MISMATCH,
                        "Wallet, provider, and ledger amounts do not match.",
                    )
                )
            if len({record.currency for record in all_records}) > 1:
                findings.append(
                    (
                        DiscrepancyType.CURRENCY_MISMATCH,
                        "Wallet, provider, and ledger currencies do not match.",
                    )
                )
        unsuccessful = [record.status for record in provider if record.status != "SUCCESS"]
        if unsuccessful:
            findings.append(
                (
                    DiscrepancyType.PROVIDER_NOT_SUCCESSFUL,
                    "Provider result status is not SUCCESS: "
                    + ", ".join(sorted({status or "missing" for status in unsuccessful}))
                    + ".",
                )
            )

        if not findings:
            run.reconciled_count += 1
        for discrepancy_type, details in findings:
            run.discrepancies.append(
                Discrepancy(
                    transaction_reference=reference,
                    discrepancy_type=discrepancy_type.value,
                    status=InvestigationStatus.OPEN.value,
                    details=details,
                )
            )

    session.add(run)
    session.flush()
    return run


def summarize(run: ReconciliationRun) -> ReconciliationSummary:
    statuses_by_reference: dict[str, list[str]] = defaultdict(list)
    for discrepancy in run.discrepancies:
        statuses_by_reference[discrepancy.transaction_reference].append(discrepancy.status)

    reconciled_count = run.reconciled_count
    resolved_count = sum(
        all(status == InvestigationStatus.RESOLVED.value for status in statuses)
        for statuses in statuses_by_reference.values()
    )
    unreconciled_count = sum(
        any(status != InvestigationStatus.RESOLVED.value for status in statuses)
        for statuses in statuses_by_reference.values()
    )
    return ReconciliationSummary(
        transaction_count=run.transaction_count,
        reconciled_count=reconciled_count,
        unreconciled_count=unreconciled_count,
        resolved_count=resolved_count,
    )
