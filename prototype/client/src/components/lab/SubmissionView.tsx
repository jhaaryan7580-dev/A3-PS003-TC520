import {
  Download,
  ExternalLink,
  CheckCircle2,
  Mail,
  FileCode,
  Video,
} from "lucide-react";
import { type Evidence } from "../../lib/evidence";
import { Panel, Note, SectionHeading } from "./Common";
const assets = [
  [
    "Evaluation report",
    "Standalone HTML with embedded figures; exact results and limitations",
    "Final_Evaluation_Report.html",
  ],
  [
    "AIORI presentation · PDF",
    "Official 11-section structure and AIORI framing",
    "A3-PS003-TC520_Chauraha_Sync.pdf",
  ],
  [
    "Editable presentation · PPTX",
    "The same verified content, editable by the team",
    "A3-PS003-TC520_Chauraha_Sync.pptx",
  ],
  [
    "Mentor walkthrough & pseudocode",
    "Original NumPy aggregation and evaluation workflow",
    "Pseudocode_and_Mentor_Walkthrough.html",
  ],
  [
    "Reproduction guide",
    "Safe isolated runs; frozen outputs remain unchanged",
    "Reproduction_Guide.html",
  ],
  [
    "Every result row · CSV",
    "Primary and diagnostic runs, kept distinct",
    "all_runs.csv",
  ],
];
export default function SubmissionView({
  evidence: e,
}: {
  evidence: Evidence;
}) {
  return (
    <>
      <SectionHeading
        eyebrow="04 / REPRODUCIBILITY & HANDOFF"
        title="Built to be inspected."
      />
      <Note kind="success">
        <CheckCircle2 size={18} />
        <div>
          <strong>Local technical deliverables are complete.</strong>
          <br />
          Repository access, uploads and the required mentor demonstration are
          external actions — not statuses this interface can certify.
        </div>
      </Note>
      <div className="submission-layout">
        <Panel title="The evidence packet" kicker="DOWNLOAD & INSPECT">
          <div className="download-list">
            {assets.map(([title, desc, file]) => (
              <a href={"/downloads/" + file} download key={file}>
                <FileCode size={20} />
                <div>
                  <strong>{title}</strong>
                  <span>{desc}</span>
                </div>
                <Download size={16} />
              </a>
            ))}
          </div>
          <p className="caption">
            The complete submission ZIP also contains frozen raw result JSONs,
            original NumPy code, two saved checkpoints, automatic release checks
            and this interface’s source and compiled assets.
          </p>
        </Panel>
        <Panel title="The team behind the experiment" kicker="CHAURAHA SYNC">
          <div className="team-entry">
            <strong>Aryan Jha</strong>
            <span>Team lead · point of contact</span>
            <a href="mailto:aryanjha.ad26@bmsce.ac.in">
              aryanjha.ad26@bmsce.ac.in
            </a>
          </div>
          <div className="team-entry">
            <strong>Apeksha Benneshiroor</strong>
            <span>Team member</span>
            <a href="mailto:apekshabenneshiroor.ec26@bmsce.ac.in">
              apekshabenneshiroor.ec26@bmsce.ac.in
            </a>
          </div>
          <div className="team-entry">
            <strong>Dr Monika Puttaramaiah</strong>
            <span>Faculty mentor · BMS College of Engineering</span>
            <a href="mailto:monika.mel@bmsce.ac.in">monika.mel@bmsce.ac.in</a>
          </div>
          <div className="external-links">
            <a
              href="https://github.com/jhaaryan7580-dev/A3-PS003-TC520"
              target="_blank"
              rel="noreferrer"
            >
              Private team repository <ExternalLink size={14} />
            </a>
            <a
              href="https://www.youtube.com/watch?v=jJh9rvyaiUA"
              target="_blank"
              rel="noreferrer"
            >
              Team introduction video <Video size={14} />
            </a>
            <a
              href="https://www.linkedin.com/in/aryan-jha-785a29343"
              target="_blank"
              rel="noreferrer"
            >
              Aryan’s LinkedIn <ExternalLink size={14} />
            </a>
          </div>
          <p className="caption">
            Collaborator access is required for the private repository. These
            links are references, not evidence of evaluator access or mentoring
            attendance.
          </p>
        </Panel>
      </div>
      <Panel
        title="What we claim — and what we do not"
        kicker="SCIENTIFIC SCOPE"
      >
        <div className="scope-columns">
          <div>
            <h3>Supported by the frozen artifacts</h3>
            <p>
              A compact 513-parameter model, five virtual operators,
              chronological splits, IID/non-IID comparisons, three seeds,
              common-group disparities and transparent analytical communication
              accounting.
            </p>
            <p>
              Real inference from validation-selected saved weights. No
              best-seed cherry-picking. The browser implementation is separately
              tolerance-checked against NumPy.
            </p>
          </div>
          <div>
            <h3>Not established by this project</h3>
            <p>
              Live city forecasting, Bengaluru generalisation, physical
              intersection mapping, formal privacy protection, measured network
              latency, wire-byte savings or scarce-client data benefits.
            </p>
            <p>
              Three seeds are descriptive. The extended 100-round diagnostic has
              a larger training budget and is not the original matched primary
              comparison.
            </p>
          </div>
        </div>
      </Panel>
      <Panel
        title="Provenance you can reproduce"
        kicker="INTEGRITY, NOT CERTIFICATION"
      >
        <p>Dataset SHA-256</p>
        <code className="hash">{e.audit.sha256}</code>
        <p>
          Every primary and diagnostic run is traceable to its unchanged JSON.
          The result metadata honestly records the original workspace’s missing
          Git commit; no commit ID was invented later.
        </p>
        <a className="text-button" href="/data/source_manifest.json" download>
          Download the source artifact manifest <Download size={14} />
        </a>
        <details className="provenance">
          <summary>Inspect all 21 referenced result files</summary>
          {e.runs.map(r => (
            <div key={r.source}>
              <strong>{r.source}</strong>
              <code>{r.source_sha256}</code>
            </div>
          ))}
        </details>
      </Panel>
      <Note kind="warning">
        AIORI’s public guideline requires a live demo link or direct final
        deliverable files, and a prototype/pseudocode demonstration to the
        mentor. This portable offline-capable interface fulfils the technical
        preparation, not the actual mentoring interaction. The official public
        schedule has not supplied a confirmed Smart Cities session.
      </Note>
    </>
  );
}
