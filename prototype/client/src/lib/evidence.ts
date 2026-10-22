export type Aggregate = { mean: number; sample_sd: number; values: number[] };
export type Condition =
  | "centralised"
  | "local_iid"
  | "local_non_iid"
  | "fedavg_iid"
  | "fedavg_non_iid";
export type Score = {
  mae: number;
  rmse: number;
  relative_abs_error: number;
  n: number;
};
export type Run = {
  condition: Condition;
  seed: number;
  budget: "primary" | "diagnostic";
  history: any;
  best_checkpoint: any;
  communication: any;
  metadata: any;
  test: {
    overall: Score;
    per_client_non_iid: {
      clients: Score[];
      gap_relative_error: number;
      gap_mae: number;
    };
    per_client_iid: { clients: Score[] };
  };
  source: string;
  source_sha256: string;
};
export type Evidence = {
  summary: {
    primary: Record<
      Condition,
      {
        test: {
          mae: Aggregate;
          rmse: Aggregate;
          relative_abs_error: Aggregate;
        };
        canonical_gap_relative_error: Aggregate;
        canonical_clients: Record<
          string,
          { mae: Aggregate; rmse: Aggregate; relative_abs_error: Aggregate }
        >;
      }
    >;
    diagnostic: any;
    baselines: any;
    communication: any;
  };
  audit: any;
  runs: Run[];
  groups: Record<
    "iid" | "non_iid",
    Record<
      string,
      { id: number; sensors: number[]; training_sensor_mean: number }[]
    >
  >;
  definitions: Record<string, string>;
};
export const names: Record<Condition, string> = {
  centralised: "Centralised",
  local_iid: "Local · IID",
  local_non_iid: "Local · non-IID",
  fedavg_iid: "FedAvg · IID",
  fedavg_non_iid: "FedAvg · non-IID",
};
export const colors: Record<Condition, string> = {
  centralised: "#17365e",
  local_iid: "#8c9aa9",
  local_non_iid: "#7290a2",
  fedavg_iid: "#14857f",
  fedavg_non_iid: "#c46635",
};
export const format = (n: number, d = 3) =>
  n.toLocaleString("en-US", {
    minimumFractionDigits: d,
    maximumFractionDigits: d,
  });
export const sha256 = async (text: string) =>
  Array.from(
    new Uint8Array(
      await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text))
    )
  )
    .map(x => x.toString(16).padStart(2, "0"))
    .join("");
export async function loadEvidence(): Promise<{
  evidence: Evidence;
  manifest: any;
}> {
  const [r, m] = await Promise.all([
    fetch("/data/evidence.json"),
    fetch("/data/source_manifest.json"),
  ]);
  if (!r.ok || !m.ok)
    throw Error("Evidence files unavailable. Run the packaged local launcher.");
  const text = await r.text(),
    manifest = await m.json();
  if ((await sha256(text)) !== manifest.evidence_sha256)
    throw Error("Evidence integrity check failed. Restore the release files.");
  const evidence = JSON.parse(text);
  if (manifest.dataset_sha256 !== evidence.audit.sha256)
    throw Error("Dataset manifest mismatch.");
  return { evidence, manifest };
}
export function downloadJson(name: string, data: unknown) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
