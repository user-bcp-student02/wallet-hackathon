import { useCallback, useEffect, useMemo, useState } from "react";

import {
  api,
  ApiError,
  type DailySummary,
  type Discrepancy,
  type DiscrepancyStatus,
  type ReconciliationReport,
  type Summary,
} from "./api";

const today = new Date().toISOString().slice(0, 10);
const emptySummary: Summary = {
  transaction_count: 0,
  reconciled_count: 0,
  unreconciled_count: 0,
  resolved_count: 0,
  resolved_discrepancy_count: 0,
};
const discrepancyLabels: Record<Discrepancy["discrepancy_type"], string> = {
  MISSING_WALLET_RECORD: "Falta en wallet",
  MISSING_PROVIDER_RESULT: "Sin resultado del proveedor",
  MISSING_LEDGER_ENTRY: "Falta asiento de ledger",
  DUPLICATE_WALLET_RECORD: "Wallet duplicado",
  DUPLICATE_PROVIDER_RESULT: "Resultado duplicado",
  DUPLICATE_LEDGER_ENTRY: "Asiento duplicado",
  CHANNEL_MISMATCH: "Canal diferente",
  AMOUNT_MISMATCH: "Monto diferente",
  CURRENCY_MISMATCH: "Moneda diferente",
  PROVIDER_NOT_SUCCESSFUL: "Proveedor no confirmó éxito",
};
const statusLabels: Record<DiscrepancyStatus, string> = {
  OPEN: "Abierto",
  IN_PROGRESS: "En investigación",
  RESOLVED: "Resuelto",
};

function formatCount(value: number) {
  return new Intl.NumberFormat("es-PE").format(value);
}

function dateLabel(value: string) {
  return new Intl.DateTimeFormat("es-PE", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(`${value}T12:00:00`));
}

function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Ocurrió un error inesperado.";
}

function App() {
  const [date, setDate] = useState(today);
  const [channelFilter, setChannelFilter] = useState("");
  const [channel, setChannel] = useState("qr");
  const [reports, setReports] = useState<ReconciliationReport[]>([]);
  const [daily, setDaily] = useState<DailySummary | null>(null);
  const [apiOnline, setApiOnline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busyDiscrepancy, setBusyDiscrepancy] = useState<number | null>(null);
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [source, setSource] = useState<"wallet" | "provider" | "ledger">("wallet");
  const [recordsJson, setRecordsJson] = useState(
    JSON.stringify(
      [
        {
          transaction_reference: "tx-20261015-0001",
          transaction_date: today,
          channel: "qr",
          amount_minor: 2590,
          currency: "PEN",
        },
      ],
      null,
      2,
    ),
  );
  const [loadingRecords, setLoadingRecords] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [reportResult, summaryResult] = await Promise.all([
        api.listReports(date, channelFilter),
        api.dailySummary(date),
      ]);
      setReports(reportResult);
      setDaily(summaryResult);
      setApiOnline(true);
    } catch (requestError) {
      setError(errorMessage(requestError));
      setApiOnline(!(requestError instanceof ApiError && requestError.status >= 500));
    } finally {
      setLoading(false);
    }
  }, [date, channelFilter]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const summary = useMemo(() => {
    if (!channelFilter) return daily?.summary ?? emptySummary;
    return (
      reports.find((report) => report.channel === channelFilter)?.summary ??
      emptySummary
    );
  }, [channelFilter, daily, reports]);

  async function runReconciliation(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setRunning(true);
    setError("");
    setNotice("");
    try {
      await api.runReconciliation(date, channel.trim());
      setNotice(`Conciliación de ${channel.trim()} creada correctamente.`);
      await refresh();
    } catch (requestError) {
      setError(errorMessage(requestError));
      if (requestError instanceof ApiError && requestError.status === 409) {
        await refresh();
      }
    } finally {
      setRunning(false);
    }
  }

  async function updateStatus(
    discrepancy: Discrepancy,
    status: DiscrepancyStatus,
  ) {
    const note = notes[discrepancy.id]?.trim();
    if (status === "RESOLVED" && !note) {
      setError("Agrega una nota de investigación antes de resolver el descalce.");
      return;
    }
    setBusyDiscrepancy(discrepancy.id);
    setError("");
    try {
      await api.updateDiscrepancy(discrepancy.id, status, note);
      setNotice(`Descalce ${discrepancy.transaction_reference}: ${statusLabels[status].toLowerCase()}.`);
      await refresh();
    } catch (requestError) {
      setError(errorMessage(requestError));
    } finally {
      setBusyDiscrepancy(null);
    }
  }

  async function uploadRecords(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingRecords(true);
    setError("");
    setNotice("");
    try {
      const parsed: unknown = JSON.parse(recordsJson);
      if (!Array.isArray(parsed) || parsed.length === 0) {
        throw new Error("El JSON debe ser un arreglo con al menos un registro.");
      }
      const result = await api.loadRecords(source, parsed);
      setNotice(`${formatCount(result.loaded_count)} registros cargados en ${source}.`);
      await refresh();
    } catch (requestError) {
      setError(
        requestError instanceof SyntaxError
          ? "El JSON no es válido."
          : errorMessage(requestError),
      );
    } finally {
      setLoadingRecords(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/" aria-label="Billetera, inicio">
          <span className="brand-mark">b</span>
          <span className="brand-name">billetera<span>.</span></span>
        </a>
        <div className="workspace-label">OPERACIONES</div>
        <nav className="side-nav" aria-label="Navegación principal">
          <a className="nav-link" href="#resumen">
            <span className="nav-icon">◫</span> Resumen
          </a>
          <a className="nav-link active" href="#conciliaciones">
            <span className="nav-icon">⇄</span> Conciliaciones
            <span className="nav-dot" />
          </a>
          <a className="nav-link" href="#descalces">
            <span className="nav-icon">⌁</span> Descalces
          </a>
        </nav>
        <div className="sidebar-bottom">
          <div className="sidebar-help-icon">?</div>
          <div>
            <strong>¿Necesitas ayuda?</strong>
            <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">
              Ver documentación API
            </a>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumbs">
            <span>Operaciones</span><span className="crumb-separator">/</span>
            <strong>Conciliación diaria</strong>
          </div>
          <div className="topbar-right">
            <span className={`api-status ${apiOnline ? "online" : "offline"}`}>
              <i /> API {apiOnline ? "conectada" : "sin conexión"}
            </span>
            <div className="avatar" title="Analista de operaciones">OP</div>
          </div>
        </header>

        <div className="page-container">
          <section className="page-heading">
            <div>
              <div className="eyebrow"><span className="eyebrow-line" /> CONTROL FINANCIERO</div>
              <h1>Conciliación diaria</h1>
              <p className="page-subtitle">
                Compara los movimientos de tu wallet con proveedores y ledger.
              </p>
            </div>
            <button className="button button-secondary refresh-button" onClick={() => void refresh()} disabled={loading}>
              <span className={loading ? "refresh-icon spinning" : "refresh-icon"}>↻</span>
              Actualizar
            </button>
          </section>

          <section className="toolbar-card" aria-label="Filtros de reportes">
            <div className="filter-field date-field">
              <label htmlFor="report-date">Fecha de conciliación</label>
              <div className="input-with-icon">
                <span aria-hidden="true">▦</span>
                <input id="report-date" type="date" value={date} onChange={(event) => setDate(event.target.value)} />
              </div>
            </div>
            <div className="filter-field">
              <label htmlFor="report-channel">Canal de proveedor</label>
              <select id="report-channel" value={channelFilter} onChange={(event) => setChannelFilter(event.target.value)}>
                <option value="">Todos los canales</option>
                {[...new Set([...(daily?.channels ?? []), ...reports.map((item) => item.channel)])]
                  .sort()
                  .map((item) => <option key={item} value={item}>{item.toUpperCase()}</option>)}
              </select>
            </div>
            <div className="toolbar-date">
              <span className="date-caption">MOSTRANDO</span>
              <strong>{dateLabel(date)}</strong>
            </div>
          </section>

          {error && <div className="alert alert-error" role="alert"><span>!</span>{error}</div>}
          {notice && <div className="alert alert-success" role="status"><span>✓</span>{notice}<button onClick={() => setNotice("")} aria-label="Cerrar aviso">×</button></div>}

          <section className="metrics-grid" id="resumen" aria-label="Resumen diario">
            <MetricCard
              label="Transacciones revisadas"
              value={summary.transaction_count}
              caption={channelFilter ? `Canal ${channelFilter.toUpperCase()}` : `${daily?.channels.length ?? 0} canales procesados`}
              icon="↗"
              tone="mint"
            />
            <MetricCard
              label="Conciliadas"
              value={summary.reconciled_count}
              caption={summary.transaction_count ? `${Math.round(summary.reconciled_count / summary.transaction_count * 100)}% del total` : "Sin transacciones"}
              icon="✓"
              tone="green"
            />
            <MetricCard
              label="Por investigar"
              value={summary.unreconciled_count}
              caption={summary.unreconciled_count ? "Requieren atención" : "Todo en orden"}
              icon="!"
              tone="amber"
            />
            <MetricCard
              label="Transacciones resueltas"
              value={summary.resolved_count}
              caption="Todas sus incidencias cerradas"
              icon="↗"
              tone="blue"
            />
            <MetricCard
              label="Incidencias resueltas"
              value={summary.resolved_discrepancy_count}
              caption="Descalces investigados"
              icon="↗"
              tone="blue"
            />
          </section>

          <section className="run-card" id="conciliaciones">
            <div className="run-copy">
              <div className="run-icon">⇄</div>
              <div>
                <h2>Iniciar conciliación</h2>
                <p>Procesa los registros cargados para una fecha y canal.</p>
              </div>
            </div>
            <form className="run-form" onSubmit={runReconciliation}>
              <label className="sr-only" htmlFor="run-channel">Canal de proveedor</label>
              <input
                id="run-channel"
                value={channel}
                onChange={(event) => setChannel(event.target.value)}
                maxLength={64}
                placeholder="Canal, por ejemplo qr"
                required
              />
              <button className="button button-primary" type="submit" disabled={running || !channel.trim()}>
                {running ? <><span className="spinner">◌</span> Procesando</> : <>Ejecutar conciliación <span>→</span></>}
              </button>
            </form>
          </section>

          <details className="import-panel">
            <summary>
              <span className="import-summary-icon">＋</span>
              <span><strong>Cargar registros fuente</strong><small>Importa lotes JSON para probar el flujo completo</small></span>
              <span className="summary-chevron">⌄</span>
            </summary>
            <form className="import-form" onSubmit={uploadRecords}>
              <div className="import-fields">
                <label>
                  Fuente de datos
                  <select value={source} onChange={(event) => setSource(event.target.value as typeof source)}>
                    <option value="wallet">Wallet</option>
                    <option value="provider">Proveedor</option>
                    <option value="ledger">Ledger</option>
                  </select>
                </label>
                <p>El proveedor requiere <code>status</code>: <code>SUCCESS</code>, <code>FAILED</code>, <code>PENDING</code> o <code>TIMEOUT</code>.</p>
              </div>
              <label className="json-label" htmlFor="records-json">Registros JSON</label>
              <textarea id="records-json" spellCheck={false} value={recordsJson} onChange={(event) => setRecordsJson(event.target.value)} rows={8} />
              <div className="import-actions">
                <span>Formato: arreglo de registros normalizados · máximo 1,000 por lote</span>
                <button className="button button-secondary" type="submit" disabled={loadingRecords}>
                  {loadingRecords ? "Cargando…" : "Cargar registros"}
                </button>
              </div>
            </form>
          </details>

          <section className="reports-section" id="descalces">
            <div className="section-heading">
              <div>
                <div className="eyebrow">ACTIVIDAD DEL DÍA</div>
                <h2>Corridas de conciliación</h2>
              </div>
              <span className="report-count">{reports.length} {reports.length === 1 ? "corrida" : "corridas"}</span>
            </div>

            {loading ? (
              <div className="empty-state"><span className="spinner">◌</span><strong>Cargando reportes…</strong></div>
            ) : reports.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">⇄</div>
                <strong>No hay conciliaciones para esta fecha</strong>
                <p>Carga datos fuente y ejecuta una conciliación para comenzar.</p>
              </div>
            ) : (
              <div className="report-list">
                {reports.map((report) => (
                  <ReportCard
                    key={report.run_id}
                    report={report}
                    notes={notes}
                    setNotes={setNotes}
                    busyDiscrepancy={busyDiscrepancy}
                    onUpdateStatus={updateStatus}
                  />
                ))}
              </div>
            )}
          </section>

          <footer className="page-footer">
            <span>Wallet Ops <span className="footer-dot">·</span> Conciliación operativa</span>
            <span>Los montos se procesan en céntimos de PEN</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

function MetricCard({
  label,
  value,
  caption,
  icon,
  tone,
}: {
  label: string;
  value: number;
  caption: string;
  icon: string;
  tone: "mint" | "green" | "amber" | "blue";
}) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <span className={`metric-icon ${tone}`}>{icon}</span>
      </div>
      <strong className="metric-value">{formatCount(value)}</strong>
      <span className="metric-caption">{caption}</span>
    </article>
  );
}

function ReportCard({
  report,
  notes,
  setNotes,
  busyDiscrepancy,
  onUpdateStatus,
}: {
  report: ReconciliationReport;
  notes: Record<number, string>;
  setNotes: React.Dispatch<React.SetStateAction<Record<number, string>>>;
  busyDiscrepancy: number | null;
  onUpdateStatus: (discrepancy: Discrepancy, status: DiscrepancyStatus) => void;
}) {
  const [expanded, setExpanded] = useState(report.discrepancies.length > 0);
  const health = report.summary.unreconciled_count === 0
    ? "good"
    : report.summary.resolved_count > 0 ? "reviewed" : "attention";

  return (
    <article className="report-card">
      <button className="report-header" onClick={() => setExpanded(!expanded)} aria-expanded={expanded}>
        <div className="report-channel-mark">{report.channel.slice(0, 1).toUpperCase()}</div>
        <div className="report-identity">
          <strong>{report.channel.toUpperCase()} <span className={`report-state ${health}`}>
            <i />{health === "good" ? "Conciliado" : health === "reviewed" ? "Revisado" : "Requiere atención"}
          </span></strong>
          <span>Corrida #{report.run_id} <span className="bullet">·</span> {dateLabel(report.reconciliation_date)}</span>
        </div>
        <div className="report-stats">
          <span><strong>{formatCount(report.summary.transaction_count)}</strong> transacciones</span>
          <span><strong>{formatCount(report.discrepancies.length)}</strong> descalces</span>
        </div>
        <span className={`report-chevron ${expanded ? "expanded" : ""}`}>⌄</span>
      </button>
      {expanded && (
        <div className="report-body">
          {report.discrepancies.length === 0 ? (
            <div className="no-discrepancies"><span>✓</span> Todos los movimientos de este canal coinciden.</div>
          ) : (
            <div className="table-scroll">
              <table>
                <thead>
                  <tr><th>REFERENCIA</th><th>TIPO DE DESCALCE</th><th>DETALLE</th><th>ESTADO</th><th>INVESTIGACIÓN</th></tr>
                </thead>
                <tbody>
                  {report.discrepancies.map((item) => (
                    <tr key={item.id}>
                      <td className="reference-cell">{item.transaction_reference}</td>
                      <td><span className="type-pill">{discrepancyLabels[item.discrepancy_type]}</span></td>
                      <td className="detail-cell">{item.details}</td>
                      <td><span className={`status-pill ${item.status.toLowerCase()}`}>{statusLabels[item.status]}</span></td>
                      <td className="action-cell">
                        {item.status === "RESOLVED" ? (
                          <span className="resolved-note" title={item.investigation_note ?? ""}>Nota registrada ✓</span>
                        ) : (
                          <div className="investigation-actions">
                            <input
                              aria-label={`Nota para ${item.transaction_reference}`}
                              placeholder="Nota de investigación"
                              value={notes[item.id] ?? item.investigation_note ?? ""}
                              onChange={(event) => setNotes((current) => ({ ...current, [item.id]: event.target.value }))}
                            />
                            {item.status === "OPEN" && (
                              <button
                                className="text-action"
                                disabled={busyDiscrepancy === item.id}
                                onClick={() => onUpdateStatus(item, "IN_PROGRESS")}
                              >Investigar</button>
                            )}
                            <button
                              className="resolve-action"
                              disabled={busyDiscrepancy === item.id}
                              onClick={() => onUpdateStatus(item, "RESOLVED")}
                            >Resolver</button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </article>
  );
}

export default App;
