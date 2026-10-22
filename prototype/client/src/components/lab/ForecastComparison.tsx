import { useEffect, useState } from "react";
import { Download, Activity } from "lucide-react";
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
import { type Dataset } from "../../lib/dataset";
import {
  type Models,
  type Predictions,
  type TraceRow,
  makeTrace,
  traceScores,
} from "../../lib/comparison";
import { format, downloadJson } from "../../lib/evidence";
import { Panel, ChartTooltip, Note } from "./Common";
const methods = ["centralised", "fedavg_non_iid", "persistence"] as const;
const labels = {
  centralised: "Centralised · seed 0",
  fedavg_non_iid: "Non-IID FedAvg · seed 0",
  persistence: "Persistence",
};
const colors = {
  centralised: "#17365e",
  fedavg_non_iid: "#c46635",
  persistence: "#8c9aa9",
};
export function PointComparison({
  predictions,
  actual,
}: {
  predictions: Predictions;
  actual: number | null;
}) {
  return (
    <Panel
      title="Compare the exact same target"
      kicker="TWO FIXED CHECKPOINTS + PERSISTENCE"
    >
      <div className="table-scroll">
        <table
          className="result-table"
          aria-label="Same-window forecast comparison"
        >
          <thead>
            <tr>
              <th>Predictor</th>
              <th>Forecast</th>
              <th>Point absolute error</th>
            </tr>
          </thead>
          <tbody>
            {methods.map(m => (
              <tr key={m}>
                <td>
                  <span
                    className="series-dot"
                    style={{ background: colors[m] }}
                  />
                  {labels[m]}
                </td>
                <td className="numeric">{format(predictions[m], 3)}</td>
                <td className="numeric">
                  {actual === null
                    ? "No truth in manual mode"
                    : format(Math.abs(predictions[m] - actual), 3)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="caption">
        Identical 12 lags and global target index. Both checkpoints were fixed
        before export. These are individual forecasts, not three-seed test
        scores or a model-selection rule.
      </p>
    </Panel>
  );
}
export default function ForecastTrace({
  ds,
  models,
  sensor,
  index,
  enabled,
}: {
  ds: Dataset | null;
  models: Models;
  sensor: number;
  index: number;
  enabled: boolean;
}) {
  const [rows, setRows] = useState<TraceRow[] | null>(null),
    [error, setError] = useState("");
  useEffect(() => {
    setRows(null);
    setError("");
  }, [ds, sensor, index]);
  function generate() {
    try {
      if (!ds) throw Error("Select the verified local PEMS08 file first.");
      setRows(makeTrace(ds, models, sensor, index, 12));
      setError("");
    } catch (e) {
      setRows(null);
      setError((e as Error).message);
    }
  }
  return (
    <Panel
      title="A short held-out trajectory"
      kicker="ILLUSTRATIVE ONE-STEP PLAYBACK"
    >
      <p className="trace-description">
        Compare centralised, non-IID FedAvg and persistence on 12 consecutive
        five-minute target positions, starting at your selected index. No
        cherry-picked low-error windows.
      </p>
      <div className="trace-actions">
        <button
          className="button button-secondary"
          onClick={generate}
          disabled={!ds || !enabled}
        >
          <Activity size={15} />
          Compare 12 target slots
        </button>
        {rows && (
          <button
            className="text-button"
            onClick={() =>
              downloadJson("local_heldout_trace_seed0.json", {
                scope:
                  "Local illustrative contiguous one-step trace; not full-test or three-seed results",
                sensor_index: sensor,
                start_index: index,
                dataset_sha256: ds?.sha256,
                rows,
                scores: Object.fromEntries(
                  methods.map(m => [m, traceScores(rows, m)])
                ),
              })
            }
          >
            <Download size={14} />
            Save local trace
          </button>
        )}
      </div>
      {!ds && (
        <p className="caption">
          Load PEMS08 locally to enable recorded truth. Manual examples cannot
          produce an observed trajectory.
        </p>
      )}
      {error && <Note kind="warning">{error}</Note>}
      {rows && (
        <>
          <div className="trace-chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={rows}
                margin={{ top: 15, right: 15, left: 0, bottom: 10 }}
              >
                <CartesianGrid
                  strokeDasharray="3 6"
                  vertical={false}
                  stroke="#e6e9ed"
                />
                <XAxis
                  dataKey="offsetMinutes"
                  tickFormatter={v => `+${v}m`}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  domain={["auto", "auto"]}
                  width={45}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line
                  dataKey="actual"
                  name="Recorded truth"
                  stroke="#168780"
                  strokeWidth={3}
                  dot={{ r: 3 }}
                  connectNulls={false}
                  isAnimationActive={false}
                />
                {methods.map(m => (
                  <Line
                    key={m}
                    dataKey={m}
                    name={labels[m]}
                    stroke={colors[m]}
                    strokeWidth={2}
                    dot={false}
                    connectNulls={false}
                    isAnimationActive={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="table-scroll">
            <table
              className="result-table"
              aria-label="Illustrative trace metrics"
            >
              <thead>
                <tr>
                  <th>Predictor</th>
                  <th>Local trace MAE</th>
                  <th>Local trace RMSE</th>
                  <th>Valid targets</th>
                </tr>
              </thead>
              <tbody>
                {methods.map(m => {
                  const s = traceScores(rows, m);
                  return (
                    <tr key={m}>
                      <td>{labels[m]}</td>
                      <td className="numeric">
                        {s.mae === null ? "—" : format(s.mae)}
                      </td>
                      <td className="numeric">
                        {s.rmse === null ? "—" : format(s.rmse)}
                      </td>
                      <td>
                        {s.n} / {rows.length}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="caption">
            Every target uses its own preceding observed lags. This is not a
            multi-step forecast from one starting history. Zero-containing
            windows remain gaps and are excluded identically for every
            predictor. Indices {rows[0].index}–{rows[rows.length - 1].index};
            time offsets are index-derived, not authenticated timestamps.
          </p>
          <Note>
            These seed-0 slice scores vary with the selected sensor and
            position. They do not replace the frozen full-test three-seed
            evidence, choose checkpoints, or prove one method generally wins.
            Exported raw trace receipts stay local and are not bundled for
            GitHub.
          </Note>
        </>
      )}
    </Panel>
  );
}
