from datetime import date, datetime, timezone
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecordSource(StrEnum):
    WALLET = "wallet"
    PROVIDER = "provider"
    LEDGER = "ledger"


class DiscrepancyType(StrEnum):
    MISSING_WALLET_RECORD = "MISSING_WALLET_RECORD"
    MISSING_PROVIDER_RESULT = "MISSING_PROVIDER_RESULT"
    MISSING_LEDGER_ENTRY = "MISSING_LEDGER_ENTRY"
    DUPLICATE_WALLET_RECORD = "DUPLICATE_WALLET_RECORD"
    DUPLICATE_PROVIDER_RESULT = "DUPLICATE_PROVIDER_RESULT"
    DUPLICATE_LEDGER_ENTRY = "DUPLICATE_LEDGER_ENTRY"
    CHANNEL_MISMATCH = "CHANNEL_MISMATCH"
    AMOUNT_MISMATCH = "AMOUNT_MISMATCH"
    CURRENCY_MISMATCH = "CURRENCY_MISMATCH"
    PROVIDER_NOT_SUCCESSFUL = "PROVIDER_NOT_SUCCESSFUL"


class InvestigationStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class SourceRecord(Base):
    __tablename__ = "source_records"
    __table_args__ = (
        CheckConstraint("amount_minor > 0", name="ck_source_records_amount_positive"),
        CheckConstraint(
            "source IN ('wallet', 'provider', 'ledger')",
            name="ck_source_records_source",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(16), index=True)
    transaction_reference: Mapped[str] = mapped_column(String(128), index=True)
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    channel: Mapped[str] = mapped_column(String(64), index=True)
    amount_minor: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    loaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"
    __table_args__ = (
        UniqueConstraint("reconciliation_date", "channel", name="uq_run_date_channel"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    reconciliation_date: Mapped[date] = mapped_column(Date, index=True)
    channel: Mapped[str] = mapped_column(String(64), index=True)
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)
    reconciled_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    discrepancies: Mapped[list["Discrepancy"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class Discrepancy(Base):
    __tablename__ = "discrepancies"
    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "transaction_reference",
            "discrepancy_type",
            name="uq_discrepancy_per_run",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("reconciliation_runs.id"), index=True)
    transaction_reference: Mapped[str] = mapped_column(String(128), index=True)
    discrepancy_type: Mapped[str] = mapped_column(String(48))
    status: Mapped[str] = mapped_column(
        String(16), default=InvestigationStatus.OPEN.value
    )
    details: Mapped[str] = mapped_column(String(512))
    investigation_note: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    run: Mapped[ReconciliationRun] = relationship(back_populates="discrepancies")
