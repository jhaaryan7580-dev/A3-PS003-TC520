import { predict, type Checkpoint } from "./engine";
import { getWindow, type Dataset } from "./dataset";

export type Models = Record<"centralised" | "fedavg_non_iid", Checkpoint>;
export type Predictions = {
  centralised: number;
  fedavg_non_iid: number;
  persistence: number;
};
export type TraceRow = {
  index: number;
  offsetMinutes: number;
  actual: number | null;
  centralised: number | null;
  fedavg_non_iid: number | null;
  persistence: number | null;
  excluded: boolean;
};
export function compareHistory(
  models: Models,
  history: number[],
  index: number
): Predictions {
  return {
    centralised: predict(models.centralised, history, index),
    fedavg_non_iid: predict(models.fedavg_non_iid, history, index),
    persistence: history[11],
  };
}
/** Consecutive target positions, not a selected set of low-error examples.
 * Each forward pass uses its own preceding observed history: one-step playback,
 * not a 60-minute autoregressive roll-out from a single origin.
 */
export function makeTrace(
  ds: Dataset,
  models: Models,
  sensor: number,
  start: number,
  slots = 12
): TraceRow[] {
  if (!Number.isSafeInteger(slots) || slots < 1 || slots > 48)
    throw Error("Trace length must be 1–48 slots.");
  getWindow(ds, sensor, start); // Validate starting index/sensor and current window.
  const rows: TraceRow[] = [];
  for (let index = start; index < Math.min(start + slots, ds.steps); index++) {
    let window;
    try {
      window = getWindow(ds, sensor, index);
    } catch (err) {
      if (!(err instanceof Error) || !/zero|finite/.test(err.message))
        throw err;
      rows.push({
        index,
        offsetMinutes: (index - start) * 5,
        actual: null,
        centralised: null,
        fedavg_non_iid: null,
        persistence: null,
        excluded: true,
      });
      continue;
    }
    // Predictor errors must not be silently relabelled as missing data.
    rows.push({
      index,
      offsetMinutes: (index - start) * 5,
      actual: window.actual,
      ...compareHistory(models, window.history, index),
      excluded: false,
    });
  }
  return rows;
}
export function traceScores(
  rows: TraceRow[],
  method: keyof Predictions
): { n: number; mae: number | null; rmse: number | null } {
  const valid = rows.filter(
    r => !r.excluded && r.actual !== null && r[method] !== null
  );
  if (!valid.length) return { n: 0, mae: null, rmse: null };
  let absolute = 0,
    squared = 0;
  for (const r of valid) {
    const err = r[method]! - r.actual!;
    absolute += Math.abs(err);
    squared += err * err;
  }
  return {
    n: valid.length,
    mae: absolute / valid.length,
    rmse: Math.sqrt(squared / valid.length),
  };
}
