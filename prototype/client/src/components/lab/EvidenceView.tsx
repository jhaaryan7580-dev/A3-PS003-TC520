import { useState } from "react";
import { Download, ArrowUpRight } from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ErrorBar,
} from "recharts";
import {
  type Evidence,
  type Condition,
  names,
  colors,
  format,
} from "../../lib/evidence";
import { SectionHeading, Panel, Metric, Note, ChartTooltip } from "./Common";
const conditions: Condition[] = [
  "centralised",
  "local_iid",
  "local_non_iid",
  "fedavg_iid",
  "fedavg_non_iid",
];
const plotConditions: Condition[] = [
  "centralised",
  "local_non_iid",
  "fedavg_iid",
  "fedavg_non_iid",
];
export default function EvidenceView({ evidence: e }: { evidence: Evidence }) {
  const [metric, setMetric] = useState<"mae" | "rmse">("mae"),
    [seed, setSeed] = useState<number | null>(null);
  const s = e.summary.primary;
  const penalty =
    100 *
    (s.fedavg_non_iid.canonical_clients["0"].mae.mean /
      s.local_non_iid.canonical_clients["0"].mae.mean -
      1);
  const iidGap = 100 * s.fedavg_iid.canonical_gap_relative_error.mean,
    nonGap = 100 * s.fedavg_non_iid.canonical_gap_relative_error.mean;
  const graph = Array.from({ length: 5 }, (_, i) => {
    const p: any = { group: `Q${i + 1}` };
    for (const c of plotConditions) {
      p[c] = 100 * s[c].canonical_clients[String(i)].relative_abs_error.mean;
      p[c + "_sd"] =
        100 * s[c].canonical_clients[String(i)].relative_abs_error.sample_sd;
    }
    return p;
  });
  return (
    <>
      <SectionHeading
        eyebrow="02 / FROZEN EXPERIMENT EVIDENCE"
        title="Accuracy is not the whole story"
      >
        <a
          className="button button-secondary"
          href="/downloads/all_runs.csv"
          download
        >
          <Download size={15} />
          Download exact run table
        </a>
      </SectionHeading>
      <div className="metric-row">
        <Metric
          label="CENTRALISED TEST MAE"
          value={format(s.centralised.test.mae.mean)}
          detail={`± ${format(s.centralised.test.mae.sample_sd)} sample SD`}
        />
        <Metric
          label="IID FEDAVG VS CENTRALISED"
          value={
            "+" +
            format(
              100 *
                (s.fedavg_iid.test.mae.mean / s.centralised.test.mae.mean - 1),
              2
            ) +
            "%"
          }
          detail="relative increase in mean test MAE"
        />
        <Metric
          label="NON-IID FEDAVG VS CENTRALISED"
          value={
            "+" +
            format(
              100 *
                (s.fedavg_non_iid.test.mae.mean / s.centralised.test.mae.mean -
                  1),
              2
            ) +
            "%"
          }
          detail="relative increase in mean test MAE"
        />
        <Metric
          label="QUIET-GROUP MAE PENALTY"
          value={"+" + format(penalty, 2) + "%"}
          detail="non-IID FedAvg vs matched local Q1"
          accent
        />
      </div>
      <div className="evidence-layout">
        <Panel title="The primary comparison" kicker="30 EPOCHS / 30 ROUNDS">
          <div className="table-controls">
            <div className="segmented">
              {(["mae", "rmse"] as const).map(m => (
                <button
                  className={metric === m ? "active" : ""}
                  key={m}
                  onClick={() => setMetric(m)}
                >
                  {m.toUpperCase()}
                </button>
              ))}
            </div>
            <select
              aria-label="Aggregate or individual seed"
              value={seed ?? "all"}
              onChange={x =>
                setSeed(
                  x.target.value === "all" ? null : Number(x.target.value)
                )
              }
            >
              <option value="all">All seeds · mean ± sample SD</option>
              {[0, 1, 2].map(x => (
                <option key={x} value={x}>
                  Seed {x} · individual result
                </option>
              ))}
            </select>
          </div>
          <table className="result-table">
            <thead>
              <tr>
                <th>Arrangement</th>
                <th>Test {metric.toUpperCase()}</th>
                <th>Model count</th>
              </tr>
            </thead>
            <tbody>
              {conditions.map(c => (
                <tr key={c}>
                  <td>
                    <span
                      className="series-dot"
                      style={{ background: colors[c] }}
                    />
                    {names[c]}
                  </td>
                  <td className="numeric">
                    {format(
                      seed === null
                        ? s[c].test[metric].mean
                        : s[c].test[metric].values[seed]
                    )}
                    {seed === null && (
                      <small> ± {format(s[c].test[metric].sample_sd)}</small>
                    )}
                  </td>
                  <td>{c.startsWith("local") ? "5 × 513" : "1 × 513"}</td>
                </tr>
              ))}
              <tr className="baseline-table-row">
                <td>Persistence · non-learned</td>
                <td className="numeric">
                  {format(e.summary.baselines.persistence[metric])}
                </td>
                <td>Last observation</td>
              </tr>
              <tr className="baseline-table-row">
                <td>Daily cycle · non-learned</td>
                <td className="numeric">
                  {format(e.summary.baselines.daily_cycle_per_sensor[metric])}
                </td>
                <td>Sensor/slot means</td>
              </tr>
            </tbody>
          </table>
          <p className="caption">
            15 primary learned runs. Identical eligible test windows. Three
            seeds describe initialisation/shuffling variation, not independent
            cities or a statistical equivalence test. Both fixed non-learned
            baselines score the same{" "}
            {e.summary.baselines.persistence.n.toLocaleString()} held-out
            windows; they have no seed SD and do not change with the
            learned-seed selector.
          </p>
          <div className="baseline-strip">
            <span>Non-learned references</span>
            <div>
              <strong>
                {format(e.summary.baselines.persistence[metric])}{" "}
                {metric.toUpperCase()}
              </strong>
              <small>Persistence</small>
            </div>
            <div>
              <strong>
                {format(e.summary.baselines.daily_cycle_per_sensor[metric])}{" "}
                {metric.toUpperCase()}
              </strong>
              <small>Per-sensor daily cycle</small>
            </div>
          </div>
          <Note>
            Equal sample passes are not equal optimisation trajectories.
            Local-only has five models and no model exchange, not zero overall
            compute or governance cost.
          </Note>
        </Panel>
        <Panel
          title="Which groups absorb the error?"
          kicker="SAME CANONICAL MASKS"
        >
          <div className="client-chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={graph}
                margin={{ top: 18, right: 12, left: 0, bottom: 4 }}
              >
                <CartesianGrid
                  strokeDasharray="3 6"
                  vertical={false}
                  stroke="#e6e9ed"
                />
                <XAxis dataKey="group" axisLine={false} tickLine={false} />
                <YAxis
                  domain={[0, 10]}
                  tickFormatter={v => v + "%"}
                  axisLine={false}
                  tickLine={false}
                  width={42}
                />
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                {plotConditions.map(c => (
                  <Line
                    key={c}
                    dataKey={c}
                    name={names[c]}
                    stroke={colors[c]}
                    strokeWidth={2.5}
                    dot={{ r: 4 }}
                    isAnimationActive={false}
                  >
                    <ErrorBar
                      dataKey={c + "_sd"}
                      width={5}
                      stroke={colors[c]}
                    />
                  </Line>
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
          <p className="caption">
            Quiet → busy groups were fixed using valid training sensor means.
            Relative error = sum absolute error / sum flow, not MAPE. Curves use
            three-seed means with sample SD.
          </p>
          <div className="gap-comparison">
            <div>
              <span>IID FedAvg gap</span>
              <strong>{format(iidGap)} pp</strong>
            </div>
            <ArrowUpRight size={24} />
            <div>
              <span>Non-IID FedAvg gap</span>
              <strong>{format(nonGap)} pp</strong>
            </div>
          </div>
        </Panel>
      </div>
      <Panel
        title="Quiet-client finding — keep the unfavourable result"
        kicker="H4 REFUTED"
      >
        <div className="finding">
          <div className="finding-number">
            +{format(penalty, 2)}
            <span>%</span>
          </div>
          <div>
            <h3>Non-IID FedAvg did not help the quietest group.</h3>
            <p>
              Q1 mean MAE was{" "}
              {format(s.fedavg_non_iid.canonical_clients["0"].mae.mean)} versus{" "}
              {format(s.local_non_iid.canonical_clients["0"].mae.mean)} for
              matched local-only. The benefit hypothesised in H4 was not
              supported. A scarce-history benefit has not been tested and is not
              used to rescue this finding.
            </p>
          </div>
        </div>
      </Panel>
      <Panel
        title="Dataset and evaluation ledger"
        kicker="TRAIN-ONLY STATISTICS"
      >
        <div className="audit-ledger">
          <div>
            <span>Public tensor</span>
            <strong>17,856 × 170 × 3</strong>
          </div>
          <div>
            <span>Training windows</span>
            <strong>
              {e.audit.windows.train.complete_case.toLocaleString()}
            </strong>
          </div>
          <div>
            <span>Validation windows</span>
            <strong>
              {e.audit.windows.val.complete_case.toLocaleString()}
            </strong>
          </div>
          <div>
            <span>Test windows</span>
            <strong>
              {e.audit.windows.test.complete_case.toLocaleString()}
            </strong>
          </div>
          <div>
            <span>Zero flow markers</span>
            <strong>
              {e.audit.zero_flow_entries.toLocaleString()} ·{" "}
              {format(e.audit.zero_flow_fraction * 100, 3)}%
            </strong>
          </div>
          <div>
            <span>Primary non-IID W1</span>
            <strong>
              {format(e.audit.partitions.non_iid.sensor_mean_w1, 2)} flow units
            </strong>
          </div>
        </div>
        <p className="caption">
          Exact zero as a missing-source marker is a modelling assumption. No
          authenticated calendar timestamps, physical-intersection mapping or
          Bengaluru generalisation claim. Source: results/dataset_audit.json and
          the unchanged primary result JSONs.
        </p>
      </Panel>
    </>
  );
}
