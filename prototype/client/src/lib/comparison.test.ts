import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import {
  compareHistory,
  makeTrace,
  traceScores,
  type Models,
  type TraceRow,
} from "./comparison";
import { predict } from "./engine";
import { type Dataset, HELD_OUT_START, TRAIN_END } from "./dataset";
const models: Models = Object.fromEntries(
  ["centralised", "fedavg_non_iid"].map(c => [
    c,
    JSON.parse(
      readFileSync(resolve("client/public/data", `${c}_seed0.json`), "utf8")
    ),
  ])
) as Models;
function synthetic(): Dataset {
  const flow = new Float32Array(17856).fill(180);
  for (let t = HELD_OUT_START - 12; t < 17856; t++) flow[t] = 160 + (t % 17);
  return {
    flow,
    steps: 17856,
    sensors: 1,
    sha256: "synthetic unit fixture, not benchmark evidence",
  };
}
describe("requirement-focused comparative inference", () => {
  it("compares both models on identical lags/index and leaves inputs unchanged", () => {
    const h = Array.from({ length: 12 }, (_, i) => 170 + i);
    const before = [...h];
    const p = compareHistory(models, h, 15189);
    expect(p.centralised).toBe(predict(models.centralised, h, 15189));
    expect(p.fedavg_non_iid).toBe(predict(models.fedavg_non_iid, h, 15189));
    expect(p.persistence).toBe(181);
    expect(h).toEqual(before);
  });
  it("keeps the declared training boundary consistent with the audited split", () =>
    expect(TRAIN_END).toBe(12499));
  it("creates consecutive causal one-step targets, not a rollout using model outputs", () => {
    const ds = synthetic();
    const rows = makeTrace(ds, models, 0, HELD_OUT_START);
    expect(rows).toHaveLength(12);
    for (let i = 0; i < rows.length; i++) {
      expect(rows[i].index).toBe(HELD_OUT_START + i);
      expect(rows[i].offsetMinutes).toBe(i * 5);
      expect(rows[i].actual).toBe(ds.flow[rows[i].index]);
      expect(rows[i].persistence).toBe(ds.flow[rows[i].index - 1]);
    }
    const h = Array.from(
      ds.flow.slice(HELD_OUT_START + 1 - 12, HELD_OUT_START + 1)
    );
    expect(rows[1].centralised).toBe(
      predict(models.centralised, h, HELD_OUT_START + 1)
    );
  });
  it("keeps excluded windows as gaps rather than shifting or connecting past them", () => {
    const ds = synthetic();
    ds.flow[HELD_OUT_START + 3] = 0;
    const rows = makeTrace(ds, models, 0, HELD_OUT_START);
    expect(rows.map(r => r.index)).toEqual(
      Array.from({ length: 12 }, (_, i) => HELD_OUT_START + i)
    );
    expect(rows[3].excluded).toBe(true);
    expect(rows[3].actual).toBeNull();
    expect(rows[3].centralised).toBeNull();
    expect(traceScores(rows, "persistence").n).toBe(3);
  });
  it("clips only at the dataset end and rejects invalid starting indices/sensors/counts", () => {
    const ds = synthetic();
    expect(makeTrace(ds, models, 0, 17854)).toHaveLength(2);
    expect(() => makeTrace(ds, models, 0, HELD_OUT_START - 1)).toThrow(
      /held-out/
    );
    expect(() => makeTrace(ds, models, 1, HELD_OUT_START)).toThrow(/Sensor/);
    expect(() => makeTrace(ds, models, 0, HELD_OUT_START, 0)).toThrow(/length/);
  });
  it("does not hide predictor failures as missing-data gaps", () => {
    const bad = structuredClone(models);
    bad.centralised.scaler.std = 0;
    expect(() => makeTrace(synthetic(), bad, 0, HELD_OUT_START)).toThrow(
      /scaler/
    );
  });
  it("calculates local MAE and RMSE from valid rows only and labels empty scores null", () => {
    const rows: TraceRow[] = [
      {
        index: 15189,
        offsetMinutes: 0,
        actual: 10,
        centralised: 12,
        fedavg_non_iid: 8,
        persistence: 10,
        excluded: false,
      },
      {
        index: 15190,
        offsetMinutes: 5,
        actual: 10,
        centralised: 14,
        fedavg_non_iid: 6,
        persistence: 10,
        excluded: false,
      },
      {
        index: 15191,
        offsetMinutes: 10,
        actual: null,
        centralised: null,
        fedavg_non_iid: null,
        persistence: null,
        excluded: true,
      },
    ];
    expect(traceScores(rows, "centralised")).toEqual({
      n: 2,
      mae: 3,
      rmse: Math.sqrt(10),
    });
    expect(traceScores(rows, "persistence")).toEqual({ n: 2, mae: 0, rmse: 0 });
    expect(traceScores([], "centralised")).toEqual({
      n: 0,
      mae: null,
      rmse: null,
    });
  });
});
