import { useEffect, useState } from "react";
import {
  Play,
  Pause,
  GitMerge,
  Database,
  ArrowDownToLine,
  ArrowUpFromLine,
  Terminal,
  Copy,
  Check,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  Legend,
} from "recharts";
import { type Evidence, names, colors, format } from "../../lib/evidence";
import { SectionHeading, Panel, Metric, Note, ChartTooltip } from "./Common";
export default function FederationView({
  evidence: e,
}: {
  evidence: Evidence;
}) {
  const [mode, setMode] = useState<"iid" | "non_iid">("non_iid"),
    [seed, setSeed] = useState(0),
    [budget, setBudget] = useState<"primary" | "diagnostic">("primary"),
    [round, setRound] = useState(1),
    [playing, setPlaying] = useState(false),
    [selected, setSelected] = useState(0),
    [projection, setProjection] = useState(30),
    [copied, setCopied] = useState(false);
  const [copyMessage, setCopyMessage] = useState("");
  const condition = mode === "iid" ? "fedavg_iid" : "fedavg_non_iid";
  const r = e.runs.find(
    x => x.condition === condition && x.seed === seed && x.budget === budget
  )!;
  const history = r.history as any[],
    point = history[Math.min(round, history.length) - 1],
    members = e.groups[mode][String(seed)],
    counts = r.communication.client_train_samples as number[],
    total = counts.reduce((a, b) => a + b, 0);
  const otherCondition = mode === "iid" ? "fedavg_non_iid" : "fedavg_iid";
  const other = e.runs.find(
    x =>
      x.condition === otherCondition && x.seed === seed && x.budget === budget
  )!;
  const central = e.runs.find(
    x =>
      x.condition === "centralised" && x.seed === seed && x.budget === "primary"
  )!;
  const target = 1.05 * central.best_checkpoint.val_mae;
  const selectedHit = history.find(h => h.val_mae <= target)?.round;
  const otherHit = (other.history as any[]).find(
    h => h.val_mae <= target
  )?.round;
  const shownRound = Math.min(round, history.length);
  const raw = e.audit.training_flow_upload_reference_bytes as number,
    perRound = r.communication.bytes_per_round as number;
  useEffect(() => {
    setPlaying(false);
    setRound(1);
  }, [mode, seed, budget]);
  useEffect(() => {
    if (!playing) return;
    const t = setInterval(
      () =>
        setRound(v => {
          if (v >= history.length) {
            setPlaying(false);
            return v;
          }
          return v + 1;
        }),
      650
    );
    return () => clearInterval(t);
  }, [playing, history.length]);
  const plot = history.map((h, i) => ({
    round: h.round,
    val: h.val_mae,
    counterpart: other.history[i].val_mae,
  }));
  const smoke =
    "python src/run_experiments.py --config configs/smoke.json --out results/my_smoke\npython src/check_results.py --dir results/my_smoke --config configs/smoke.json";
  return (
    <>
      <SectionHeading
        eyebrow="03 / EXPLAIN THE FEDERATION"
        title="Five operators. One shared model."
      />
      <div className="mode-strip">
        <span className="status-dot copper" />
        <strong>Verified history replay</strong>
        <span>
          Controls below read saved JSONs. They do not train, transmit weights
          or create new test results.
        </span>
      </div>
      <div className="federation-controls">
        <div className="segmented">
          <button
            className={mode === "iid" ? "active" : ""}
            onClick={() => setMode("iid")}
          >
            IID membership
          </button>
          <button
            className={mode === "non_iid" ? "active" : ""}
            onClick={() => setMode("non_iid")}
          >
            Non-IID membership
          </button>
        </div>
        <select
          aria-label="Replay seed"
          value={seed}
          onChange={x => setSeed(Number(x.target.value))}
        >
          {[0, 1, 2].map(x => (
            <option key={x} value={x}>
              Seed {x}
            </option>
          ))}
        </select>
        <select
          aria-label="Replay budget"
          value={budget}
          onChange={x => setBudget(x.target.value as typeof budget)}
        >
          <option value="primary">Primary · 30 rounds</option>
          <option value="diagnostic">Extended diagnostic · 100 rounds</option>
        </select>
      </div>
      <div className="federation-layout">
        <Panel title="The weight-update loop" kicker="CONCEPTUAL TOPOLOGY">
          <div className="topology">
            <div className="server-node">
              <GitMerge size={28} />
              <strong>FedAvg server</strong>
              <span>Σ nₖ wₖ / Σ nₖ</span>
              <small>Sample-weighted parameters</small>
            </div>
            <div className="exchange-labels">
              <span>
                <ArrowDownToLine size={15} />
                Broadcast 2,052 B/client
              </span>
              <span>
                <ArrowUpFromLine size={15} />
                Return 2,052 B/client
              </span>
            </div>
            <div className="client-nodes">
              {members.map((m, i) => (
                <button
                  key={m.id}
                  className={
                    "client-node " + (i === selected ? "selected" : "")
                  }
                  onClick={() => setSelected(i)}
                >
                  <Database size={18} />
                  <div>
                    <strong>Operator {i + 1}</strong>
                    <span>34 sensor indices</span>
                  </div>
                  <div className="client-weight">
                    {format((100 * counts[i]) / total, 2)}
                    <small>% training weight</small>
                  </div>
                </button>
              ))}
            </div>
          </div>
          <div className="client-detail">
            <strong>
              Operator {selected + 1} · {counts[selected].toLocaleString()}{" "}
              training windows
            </strong>
            <p>
              Valid training sensor-mean flow:{" "}
              {format(members[selected].training_sensor_mean, 2)}. This round’s
              aggregated global-model validation MAE on this client's windows:{" "}
              {format(point.val_mae_per_client[selected])}.
            </p>
            <details>
              <summary>Inspect its 34 sensor indices</summary>
              <code>{members[selected].sensors.join(", ")}</code>
            </details>
          </div>
          <p className="caption">
            Five virtual operators, not mapped physical intersections. The NumPy
            simulator runs client updates sequentially. Local Adam state resets
            each round; optimiser state is not exchanged.
          </p>
          <details className="pseudocode-block">
            <summary>Mentor walkthrough: how one FedAvg round works</summary>
            <p>
              Client k has nₖ eligible training windows. Its weight is αₖ = nₖ /
              Σⱼnⱼ, not automatically 1/5 just because each client has 34
              sensors.
            </p>
            <pre>
              <code>{`for round in fixed_round_budget:
    broadcast(global_parameters) to all five clients
    for client k:
        local_parameters = copy(global_parameters)
        reset local Adam state
        train one epoch on client k's training windows
        return local_parameters
    global_parameters = sum((n_k / total_n) * local_parameters_k)
    score global model on validation windows
    save only when validation MAE improves
score selected checkpoint on the test windows once`}</code>
            </pre>
            <p className="caption">
              Pseudocode for the implemented src/train.py simulator, not code
              executed by the replay control. Shared train-derived scaling is an
              explicit assumption. Optimiser state, test targets and raw traffic
              histories are not the model-weight payload.
            </p>
          </details>
        </Panel>
        <Panel
          title="Validation convergence"
          kicker={`${budget.toUpperCase()} · SEED ${seed}`}
        >
          <div className="convergence-chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={plot}
                margin={{ top: 15, right: 15, left: 0, bottom: 5 }}
              >
                <CartesianGrid
                  strokeDasharray="3 6"
                  vertical={false}
                  stroke="#e6e9ed"
                />
                <XAxis
                  dataKey="round"
                  type="number"
                  domain={[1, history.length]}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  domain={["auto", "auto"]}
                  axisLine={false}
                  tickLine={false}
                  width={45}
                />
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Line
                  dataKey="val"
                  name={names[condition] + " validation MAE"}
                  stroke={colors[condition]}
                  strokeWidth={2.5}
                  dot={false}
                  isAnimationActive={false}
                />
                <Line
                  dataKey="counterpart"
                  name={names[otherCondition] + " · same seed/budget"}
                  stroke={colors[otherCondition]}
                  strokeDasharray="5 4"
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
                <ReferenceLine
                  y={target}
                  stroke="#8c9aa9"
                  strokeDasharray="2 3"
                />
                <ReferenceLine
                  x={shownRound}
                  stroke="#17365e"
                  strokeDasharray="4 3"
                />
                <ReferenceLine
                  x={r.best_checkpoint.round}
                  stroke="#168780"
                  strokeDasharray="3 3"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="replay-controls">
            <button
              className="icon-button"
              aria-label={
                playing ? "Pause saved history" : "Play saved history"
              }
              onClick={() => setPlaying(!playing)}
            >
              {playing ? <Pause size={18} /> : <Play size={18} />}
            </button>
            <input
              aria-label="Saved round"
              type="range"
              min="1"
              max={history.length}
              value={shownRound}
              onChange={x => {
                setRound(Number(x.target.value));
                setPlaying(false);
              }}
            />
            <strong>
              {shownRound} / {history.length}
            </strong>
          </div>
          <div className="round-facts">
            <div>
              <span>Displayed validation MAE</span>
              <strong>{format(point.val_mae)}</strong>
            </div>
            <div>
              <span>Validation-selected round</span>
              <strong>{r.best_checkpoint.round}</strong>
            </div>
            <div>
              <span>Payload through displayed round</span>
              <strong>{point.cumulative_bytes.toLocaleString()} B</strong>
            </div>
          </div>
          <p className="caption">
            Green line marks the validation minimum; the dark line marks the
            replay position. The fixed final test MAE is{" "}
            {format(r.test.overall.mae)} at the selected checkpoint — not a test
            score for every round. Source: {r.source}.
          </p>
          <div className="validation-target-note">
            <strong>Descriptive target: {format(target)} validation MAE</strong>
            <span>
              {names[condition]} first hit: {selectedHit ?? "not reached"};{" "}
              {names[otherCondition]}: {otherHit ?? "not reached"} round(s).
            </span>
          </div>
          <p className="caption">
            Target = 1.05 × this seed's best centralised validation MAE, as in
            the report. It is descriptive, not an operational stopping rule or
            test-error target. Both curves use the same seed and round budget.
          </p>
        </Panel>
      </div>
      <Panel
        title="What does communication actually cost?"
        kicker="PAYLOAD, NOT WIRE BYTES"
      >
        <div className="metric-row">
          <Metric
            label="MODEL WEIGHT PAYLOAD"
            value="2,052 B"
            detail="513 parameters × 4 bytes"
          />
          <Metric
            label="PER ROUND"
            value={perRound.toLocaleString() + " B"}
            detail="5 downloads + 5 uploads"
          />
          <Metric
            label="THIS RUN EXECUTED"
            value={r.communication.total_bytes.toLocaleString() + " B"}
            detail={`${r.communication.rounds} full rounds, not selected-round spend`}
          />
          <Metric
            label="RAW-FLOW REFERENCE"
            value={raw.toLocaleString() + " B"}
            detail="one training-only float32 flow upload"
          />
        </div>
        <div className="projection">
          <label htmlFor="payload-rounds">
            Analytical projection: <strong>{projection} rounds</strong>
          </label>
          <input
            id="payload-rounds"
            type="range"
            min="1"
            max="500"
            value={projection}
            onChange={x => setProjection(Number(x.target.value))}
          />
          <strong>{(projection * perRound).toLocaleString()} B</strong>
          <span>
            {format((100 * projection * perRound) / raw, 2)}% of the raw-flow
            reference
          </span>
        </div>
        <Note>
          At {Math.floor(raw / perRound)} rounds the payload remains below this
          reference; round {Math.floor(raw / perRound) + 1} first exceeds it.
          The slider is arithmetic, not a new run. JSON encoding, network
          headers, retries, shared scaler and metric traffic are excluded. This
          is not an end-to-end bandwidth-saving measurement.
        </Note>
      </Panel>
      <Panel
        title="Want fresh training rather than replay?"
        kicker="ACTUAL NUMPY EXECUTION"
      >
        <div className="smoke-heading">
          <p>
            From the scientific project root, after obtaining the exact NPZ.
            Outputs go to a separate directory; a smoke run is plumbing
            evidence, not a report result.
          </p>
          <button
            className="button button-secondary"
            onClick={async () => {
              try {
                if (!navigator.clipboard?.writeText)
                  throw Error("Clipboard unavailable");
                await navigator.clipboard.writeText(smoke);
                setCopied(true);
                setCopyMessage("Commands copied.");
                setTimeout(() => setCopied(false), 1600);
              } catch {
                setCopied(false);
                setCopyMessage(
                  "Clipboard unavailable or blocked. Select the visible commands below and copy them manually."
                );
              }
            }}
          >
            {copied ? <Check size={15} /> : <Copy size={15} />}Copy commands
          </button>
        </div>
        <pre className="command-box">
          <Terminal size={16} />
          <code>{smoke}</code>
        </pre>
        {copyMessage && (
          <p className="caption" role="status">
            {copyMessage}
          </p>
        )}
        <p className="caption">
          Shared train-derived scaling and complete-case zero filtering are
          explicit modelling assumptions. This educational frontend never
          changes frozen experiments.
        </p>
      </Panel>
    </>
  );
}
