export type DiscrepancyStatus = "OPEN" | "IN_PROGRESS" | "RESOLVED";
export type DiscrepancyType =
  | "MISSING_WALLET_RECORD"
  | "MISSING_PROVIDER_RESULT"
  | "MISSING_LEDGER_ENTRY"
  | "DUPLICATE_WALLET_RECORD"
  | "DUPLICATE_PROVIDER_RESULT"
  | "DUPLICATE_LEDGER_ENTRY"
  | "CHANNEL_MISMATCH"
  | "AMOUNT_MISMATCH"
  | "CURRENCY_MISMATCH"
  | "PROVIDER_NOT_SUCCESSFUL";

export interface Summary {
  transaction_count: number;
  reconciled_count: number;
  unreconciled_count: number;
  resolved_count: number;
  resolved_discrepancy_count: number;
}

export interface Discrepancy {
  id: number;
  transaction_reference: string;
  discrepancy_type: DiscrepancyType;
  status: DiscrepancyStatus;
  details: string;
  investigation_note: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReconciliationReport {
  run_id: number;
  reconciliation_date: string;
  channel: string;
  summary: Summary;
  discrepancies: Discrepancy[];
}

export interface DailySummary {
  reconciliation_date: string;
  channels: string[];
  summary: Summary;
}

export interface ReconciliationCreated {
  id: number;
  reconciliation_date: string;
  channel: string;
  created_at: string;
  summary: Summary;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let message = `La solicitud falló (${response.status}).`;
    try {
      const body: unknown = await response.json();
      if (
        typeof body === "object" &&
        body !== null &&
        "detail" in body &&
        typeof body.detail === "string"
      ) {
        message = body.detail;
      }
    } catch {
      // Keep the HTTP status message when the server response is not JSON.
    }
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  listReports: (date: string, channel: string) => {
    const params = new URLSearchParams({ reconciliation_date: date });
    if (channel) params.set("channel", channel);
    return request<ReconciliationReport[]>(
      `/api/v1/reconciliations?${params.toString()}`,
    );
  },
  dailySummary: (date: string) =>
    request<DailySummary>(
      `/api/v1/reconciliations/daily-summary?reconciliation_date=${encodeURIComponent(date)}`,
    ),
  runReconciliation: (date: string, channel: string) =>
    request<ReconciliationCreated>("/api/v1/reconciliations", {
      method: "POST",
      body: JSON.stringify({ reconciliation_date: date, channel }),
    }),
  updateDiscrepancy: (
    id: number,
    status: DiscrepancyStatus,
    investigationNote?: string,
  ) =>
    request<Discrepancy>(`/api/v1/discrepancies/${id}`, {
      method: "PATCH",
      body: JSON.stringify({
        status,
        ...(investigationNote ? { investigation_note: investigationNote } : {}),
      }),
    }),
  loadRecords: (
    source: "wallet" | "provider" | "ledger",
    records: unknown[],
  ) =>
    request<{ source: string; loaded_count: number }>(
      `/api/v1/records/${source}`,
      {
        method: "POST",
        body: JSON.stringify({ records }),
      },
    ),
};
