import { useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  Workflow,
  FolderCheck,
  ArrowUpRight,
  Loader2,
  ShieldCheck,
} from "lucide-react";
import { loadEvidence, sha256, type Evidence } from "./lib/evidence";
import { verifyCheckpoint, type Checkpoint } from "./lib/engine";
import ForecastView from "./components/lab/ForecastView";
import EvidenceView from "./components/lab/EvidenceView";
import FederationView from "./components/lab/FederationView";
import SubmissionView from "./components/lab/SubmissionView";
const tabs = [
  {
    id: "forecast",
    label: "Forecast lab",
    caption: "Run saved-model inference",
    icon: Activity,
  },
  {
    id: "evidence",
    label: "Experiment evidence",
    caption: "Accuracy & client disparities",
    icon: BarChart3,
  },
  {
    id: "federation",
    label: "Federation lab",
    caption: "Convergence & payload",
    icon: Workflow,
  },
  {
    id: "submission",
    label: "Submission desk",
    caption: "Inspect the deliverables",
    icon: FolderCheck,
  },
];
export default function App() {
  const [tab, setTab] = useState("forecast"),
    [data, setData] = useState<Evidence | null>(null),
    [models, setModels] = useState<Record<
      "centralised" | "fedavg_non_iid",
      Checkpoint
    > | null>(null),
    [error, setError] = useState("");
  useEffect(() => {
    let live = true;
    async function init() {
      try {
        const { evidence, manifest } = await loadEvidence();
        const pairs = await Promise.all(
          (["centralised", "fedavg_non_iid"] as const).map(async c => {
            const r = await fetch(`/data/${c}_seed0.json`);
            if (!r.ok) throw Error("Saved checkpoint unavailable.");
            const text = await r.text();
            if ((await sha256(text)) !== manifest.checkpoint_files[c])
              throw Error("Checkpoint file differs from packaged reference.");
            const cp = JSON.parse(text) as Checkpoint;
            if (cp.condition !== c || cp.seed !== 0)
              throw Error("Checkpoint identity mismatch.");
            if (!(await verifyCheckpoint(cp)))
              throw Error("Saved parameter integrity check failed.");
            if (cp.dataset_sha256 !== evidence.audit.sha256)
              throw Error("Dataset provenance mismatch.");
            return [c, cp] as const;
          })
        );
        if (live) {
          setData(evidence);
          setModels(
            Object.fromEntries(pairs) as Record<
              "centralised" | "fedavg_non_iid",
              Checkpoint
            >
          );
        }
      } catch (e) {
        if (live) setError((e as Error).message);
      }
    }
    void init();
    return () => {
      live = false;
    };
  }, []);
  return (
    <div className="lab-shell">
      <aside className="sidebar">
        <div className="wordmark">
          <div className="wordmark-symbol">
            <Workflow size={22} />
          </div>
          <div>
            <strong>CHAURAHA</strong>
            <span>SYNC / RESEARCH LAB</span>
          </div>
        </div>
        <div className="project-tag">
          AIORI 3 <span>PS–003</span>
        </div>
        <nav aria-label="Laboratory workspaces">
          {tabs.map(t => (
            <button
              key={t.id}
              className={"nav-item " + (tab === t.id ? "selected" : "")}
              aria-current={tab === t.id ? "page" : undefined}
              onClick={() => setTab(t.id)}
            >
              <t.icon size={20} />
              <div>
                <strong>{t.label}</strong>
                <span>{t.caption}</span>
              </div>
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <span className="eyebrow">TEAM A3–PS003–TC520</span>
          <p>
            Measure the trade-off.
            <br />
            Do not assume a winner.
          </p>
          <a
            href="https://github.com/jhaaryan7580-dev/A3-PS003-TC520"
            target="_blank"
            rel="noreferrer"
          >
            View private repository <ArrowUpRight size={14} />
          </a>
          <img src="/assets/aiori-logo.png" alt="AIORI hackathon logo" />
          <small>Prepared 19 October 2026</small>
        </div>
      </aside>
      <div className="lab-content">
        <header className="topbar">
          <div>
            <span className="small-label">
              SMART CITIES / FEDERATED TRAFFIC FLOW
            </span>
            <span className="topbar-location">
              BMS College of Engineering · Bengaluru team
            </span>
          </div>
          <span className="integrity-tag">
            <ShieldCheck size={14} />
            {models
              ? "Model & evidence integrity checked"
              : "Checking artifacts"}
          </span>
        </header>
        <div className="benchmark-notice">
          <span className="status-dot copper" />
          California PEMS08 benchmark · five virtual operators · not live
          Bengaluru traffic
        </div>
        <main>
          {error ? (
            <div className="load-error">
              <h1>Integrity check stopped the demonstration.</h1>
              <p>{error}</p>
              <button
                className="button button-primary"
                onClick={() => location.reload()}
              >
                Retry
              </button>
            </div>
          ) : !data || !models ? (
            <div className="loading">
              <Loader2 className="spinner" size={28} />
              <strong>Checking model weights and frozen evidence…</strong>
              <span>
                No traffic file is included or requested from a server.
              </span>
            </div>
          ) : (
            <>
              <ForecastView
                models={models}
                evidence={data}
                active={tab === "forecast"}
              />{" "}
              {tab === "evidence" && <EvidenceView evidence={data} />}{" "}
              {tab === "federation" && <FederationView evidence={data} />}{" "}
              {tab === "submission" && <SubmissionView evidence={data} />}
            </>
          )}
        </main>
        <footer className="lab-footer">
          <span>CHAURAHA SYNC / NUMPY CORE + VERIFIED BROWSER INFERENCE</span>
          <span>
            AI-assisted development disclosed in the repository · no formal
            privacy guarantee
          </span>
        </footer>
      </div>
    </div>
  );
}
