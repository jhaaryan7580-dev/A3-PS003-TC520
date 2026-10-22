import { useEffect, useMemo, useRef, useState } from "react";
import {
  Upload,
  ArrowRight,
  Download,
  ShieldCheck,
  ChevronRight,
  AlertCircle,
  RotateCcw,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { predict, type Checkpoint } from "../../lib/engine";
import {
  loadDataset,
  getWindow,
  eligibleIndices,
  type Dataset,
} from "../../lib/dataset";
import { downloadJson, format, type Evidence } from "../../lib/evidence";
import { Panel, Metric, Note, SectionHeading, ChartTooltip } from "./Common";
import { compareHistory } from "../../lib/comparison";
import ForecastTrace, { PointComparison } from "./ForecastComparison";
const MANUAL = [160, 166, 173, 170, 168, 172, 175, 178, 180, 176, 179, 181];
type Method = "centralised" | "fedavg_non_iid";
export default function ForecastView({
  models,
  evidence,
  active = true,
}: {
  models: Record<Method, Checkpoint>;
  evidence: Evidence;
  active?: boolean;
}) {
  const [ds, setDs] = useState<Dataset | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const [fileError, setFileError] = useState("");
  const [history, setHistory] = useState(MANUAL.join(", ")),
    [sensor, setSensor] = useState(156),
    [index, setIndex] = useState(15189),
    [method, setMethod] = useState<Method>("fedavg_non_iid");
  const [receipt, setReceipt] = useState<any>(null);
  const file = useRef<HTMLInputElement>(null);
  const cp = models[method];
  const values = useMemo(
    () => history.split(",").map(x => (x.trim() ? Number(x.trim()) : NaN)),
    [history]
  );
  const candidates = useMemo(
    () =>
      ds && Number.isInteger(sensor) && sensor >= 0 && sensor < 170
        ? eligibleIndices(ds, sensor)
        : [],
    [ds, sensor]
  );
  useEffect(() => {
    setReceipt(null);
    if (!ds) return;
    try {
      const w = getWindow(ds, sensor, index);
      setHistory(w.history.join(", "));
      setError("");
    } catch (e) {
      setError((e as Error).message);
      setHistory("");
    }
  }, [ds, sensor, index]);
  useEffect(() => setReceipt(null), [history, method]);
  async function selectFile(f: File) {
    setBusy(true);
    setError("");
    setFileError("");
    setReceipt(null);
    try {
      const data = await loadDataset(f, cp.dataset_sha256);
      setSensor(156);
      setIndex(15189);
      setDs(data);
    } catch (e) {
      setFileError(
        `${(e as Error).message}. ${ds ? "Previous verified dataset remains active." : "Manual-input mode remains available."}`
      );
    } finally {
      setBusy(false);
    }
  }
  function run() {
    try {
      if (busy) throw Error("Wait for dataset verification.");
      const window = ds ? getWindow(ds, sensor, index) : null;
      const h = window ? window.history : values;
      const comparison = compareHistory(models, h, index);
      const p = comparison[method];
      setReceipt({
        mode: ds ? "PEMS08 held-out playback" : "manual-input demonstration",
        condition: method,
        seed: 0,
        sensor_index: ds ? sensor : null,
        global_target_index: index,
        prediction: p,
        observed: window?.actual ?? null,
        persistence: h[11],
        parameter_sha256: cp.parameter_sha256,
        dataset_sha256: ds?.sha256 ?? null,
        history: h,
        comparison,
        note: "One illustrative forward pass. Not a full-test score or live city forecast.",
      });
      setError("");
    } catch (e) {
      setReceipt(null);
      setError((e as Error).message);
    }
  }
  const plot = Array.from({ length: 12 }, (_, i) => ({
    slot: `−${(12 - i) * 5}m`,
    history: Number.isFinite(values[i]) ? values[i] : null,
    prediction: null as number | null,
    observed: null as number | null,
    persistence: null as number | null,
  }));
  plot.push({
    slot: "Target",
    history: null,
    prediction: receipt?.prediction ?? null,
    observed: receipt?.observed ?? null,
    persistence: receipt?.persistence ?? null,
  });
  const group = evidence.groups.non_iid["0"].find(g =>
    g.sensors.includes(sensor)
  );
  if (!active) return null;
  return (
    <>
      <SectionHeading
        eyebrow="01 / EXECUTE THE SAVED MODEL"
        title="Forecast laboratory"
      >
        <button
          className="button button-secondary"
          onClick={() => file.current?.click()}
          disabled={busy}
        >
          <Upload size={16} />
          {busy
            ? "Verifying dataset…"
            : ds
              ? "Replace local dataset"
              : "Load local PEMS08"}
        </button>
      </SectionHeading>
      <input
        ref={file}
        type="file"
        accept=".npz"
        hidden
        onChange={e => {
          const f = e.target.files?.[0];
          if (f) void selectFile(f);
          e.target.value = "";
        }}
      />
      <div className="mode-strip">
        <span className={"status-dot " + (ds ? "green" : "copper")} />
        <strong>
          {ds ? "Verified PEMS08 · held-out playback" : "Manual-input mode"}
        </strong>
        <span>
          {ds
            ? "File processed in this browser; no application upload endpoint."
            : "The example values are manual, not recorded traffic observations."}
        </span>
      </div>
      <div className="forecast-layout">
        <div className="forecast-main">
          <Panel title="History → one-step forecast" kicker="5-MINUTE HORIZON">
            <div className="forecast-chart">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={plot}
                  margin={{ top: 20, right: 22, left: 0, bottom: 10 }}
                >
                  <CartesianGrid
                    strokeDasharray="3 6"
                    vertical={false}
                    stroke="#e6e9ed"
                  />
                  <XAxis
                    dataKey="slot"
                    tick={{ fontSize: 11, fill: "#6a7686" }}
                    interval={1}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    domain={["auto", "auto"]}
                    tick={{ fontSize: 12, fill: "#6a7686" }}
                    axisLine={false}
                    tickLine={false}
                    width={48}
                  />
                  <Tooltip content={<ChartTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 12, paddingTop: 18 }} />
                  <Line
                    dataKey="history"
                    name={ds ? "Recorded history" : "Manual history"}
                    stroke="#17365e"
                    strokeWidth={3}
                    dot={{ r: 3 }}
                    isAnimationActive={false}
                  />
                  <Line
                    dataKey="prediction"
                    name="Saved model"
                    stroke="#c46635"
                    strokeWidth={2}
                    dot={{ r: 7 }}
                    isAnimationActive={false}
                  />
                  <Line
                    dataKey="observed"
                    name="Recorded target"
                    stroke="#168780"
                    dot={{ r: 5 }}
                    isAnimationActive={false}
                  />
                  <Line
                    dataKey="persistence"
                    name="Persistence"
                    stroke="#8c9aa9"
                    dot={{ r: 4 }}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="caption">
              Flow units in the original dataset scale. History positions are
              relative to the target, not authenticated clock timestamps. Target
              truth is displayed after inference and is never an input.
            </p>
          </Panel>
          <div className="metric-row forecast-metrics">
            <Metric
              label="MODEL FORECAST"
              value={receipt ? format(receipt.prediction, 2) : "—"}
              detail="actual saved-weight forward pass"
              accent
            />
            <Metric
              label="RECORDED TARGET"
              value={
                receipt?.observed != null ? format(receipt.observed, 2) : "—"
              }
              detail={
                ds
                  ? "withheld target, displayed for comparison"
                  : "unavailable for manual inputs"
              }
            />
            <Metric
              label="PERSISTENCE"
              value={receipt ? format(receipt.persistence, 2) : "—"}
              detail="previous same-sensor observation"
            />
            <Metric
              label="POINT ABSOLUTE ERROR"
              value={
                receipt?.observed != null
                  ? format(Math.abs(receipt.prediction - receipt.observed), 2)
                  : "—"
              }
              detail="one point, not aggregate MAE"
            />
          </div>
          {receipt && (
            <PointComparison
              predictions={receipt.comparison}
              actual={receipt.observed}
            />
          )}
          <ForecastTrace
            ds={ds}
            models={models}
            sensor={sensor}
            index={index}
            enabled={!busy && !error}
          />
          <Panel
            title="The 12 observations entering the model"
            kicker="OLDEST → NEWEST"
          >
            <div className="lag-grid">
              {Array.from({ length: 12 }, (_, i) => (
                <div key={i}>
                  <span>t − {(12 - i) * 5} min</span>
                  <strong>
                    {Number.isFinite(values[i]) ? format(values[i], 0) : "—"}
                  </strong>
                </div>
              ))}
            </div>
            <label className="field-label" htmlFor="history">
              {ds
                ? "Dataset window — not editable"
                : "Manual example — edit exactly 12 positive comma-separated values"}
            </label>
            <textarea
              id="history"
              value={history}
              readOnly={!!ds}
              onChange={e => {
                setReceipt(null);
                setHistory(e.target.value);
              }}
              rows={2}
            />
          </Panel>
        </div>
        <aside className="forecast-controls">
          <Panel title="Run configuration">
            <label className="field-label" htmlFor="method">
              Saved checkpoint
            </label>
            <select
              id="method"
              value={method}
              onChange={e => {
                setReceipt(null);
                setMethod(e.target.value as Method);
              }}
            >
              <option value="fedavg_non_iid">FedAvg · non-IID · seed 0</option>
              <option value="centralised">Centralised · seed 0</option>
            </select>
            <label className="field-label" htmlFor="sensor">
              Sensor index {group && ds ? `· canonical Q${group.id + 1}` : ""}
            </label>
            <input
              id="sensor"
              type="number"
              min="0"
              max="169"
              value={sensor}
              disabled={!ds}
              onChange={e => {
                setReceipt(null);
                setSensor(Number(e.target.value));
              }}
            />
            {ds && (
              <div className="preset-buttons">
                {[156, 31, 3].map((v, i) => (
                  <button
                    key={v}
                    onClick={() => {
                      setReceipt(null);
                      setSensor(v);
                    }}
                  >
                    Q{[1, 3, 5][i]} · {v}
                  </button>
                ))}
              </div>
            )}
            <label className="field-label" htmlFor="target-index">
              Global target index
            </label>
            <input
              id="target-index"
              type="number"
              min={ds ? 15189 : 12}
              max={ds ? 17855 : undefined}
              value={index}
              onChange={e => {
                setReceipt(null);
                setIndex(Number(e.target.value));
              }}
            />
            {ds && (
              <button
                className="text-button"
                onClick={() => {
                  setReceipt(null);
                  const next = candidates.find(t => t > index);
                  setIndex(next ?? candidates[0] ?? 15189);
                }}
              >
                Next eligible window <ChevronRight size={14} />
              </button>
            )}
            <div className="config-facts">
              <div>
                <span>Architecture</span>
                <strong>14 → 32 → 1</strong>
              </div>
              <div>
                <span>Parameters</span>
                <strong>513 · float32</strong>
              </div>
              <div>
                <span>Checkpoint selection</span>
                <strong>Minimum validation MAE</strong>
              </div>
              <div>
                <span>Payload</span>
                <strong>2,052 B</strong>
              </div>
              <div>
                <span>Feature period</span>
                <strong>index mod 288</strong>
              </div>
            </div>
            <button
              className="button button-primary run-button"
              onClick={run}
              disabled={busy || !!(ds && error)}
            >
              Run forward pass <ArrowRight size={16} />
            </button>
            {receipt && (
              <button
                className="button button-secondary full-width"
                onClick={() =>
                  downloadJson("local_forecast_receipt.json", receipt)
                }
              >
                <Download size={15} />
                Save local receipt
              </button>
            )}
            {!ds && (
              <button
                className="text-button"
                onClick={() => {
                  setHistory(MANUAL.join(", "));
                  setReceipt(null);
                  setError("");
                }}
              >
                <RotateCcw size={13} />
                Reset manual example
              </button>
            )}
            {ds && (
              <button
                className="text-button"
                onClick={() => {
                  setDs(null);
                  setHistory(MANUAL.join(", "));
                  setReceipt(null);
                  setError("");
                  setFileError("");
                }}
              >
                Unload file and return to manual mode
              </button>
            )}
          </Panel>
          {error && (
            <Note kind="warning">
              <AlertCircle size={16} />
              {error}
            </Note>
          )}
          {fileError && (
            <Note kind="warning">
              <AlertCircle size={16} />
              {fileError}
            </Note>
          )}
          <Note kind="success">
            <ShieldCheck size={16} />
            <div>
              <strong>Saved parameters verified</strong>
              <br />
              Checksums and feature settings checked before inference. This is
              integrity checking, not a signed certification.
            </div>
          </Note>
          <div className="scope-card">
            <span className="eyebrow">DEMONSTRATION BOUNDARY</span>
            <p>
              California PEMS08 benchmark. No live cameras, Bengaluru validation
              or privacy guarantee.
            </p>
            <p>
              Only two fixed seed-0 checkpoints are exported. Browser arithmetic
              is tolerance-checked against original NumPy inference; the frozen
              report metrics do not come from this UI.
            </p>
            <a
              href="https://raw.githubusercontent.com/guoshnBJTU/ASTGNN/main/data/PEMS08/PEMS08.npz"
              target="_blank"
              rel="noreferrer"
            >
              Obtain PEMS08 from its upstream source ↗
            </a>
            <p>
              Confirm dataset usage rights. Raw files and local receipts are not
              included in the submission.
            </p>
          </div>
        </aside>
      </div>
    </>
  );
}
