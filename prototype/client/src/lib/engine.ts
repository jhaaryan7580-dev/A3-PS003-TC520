/** Numerical forward-pass utilities for the two exported PS-003 checkpoints. */

export const CHECKPOINT_FORMAT = "chauraha-sync-verified-checkpoint-v1";
export const LAGS = 12;
export const PERIOD = 288;

export type Matrix14x32 = number[][];
export type CheckpointParameters = {
  W1: Matrix14x32;
  b1: number[];
  W2: number[];
  b2: number[];
};

export type Checkpoint = {
  condition: string;
  seed: number;
  format: string;
  parameters: CheckpointParameters;
  scaler: { mean: number; std: number };
  parameter_sha256: string;
  dataset_sha256: string;
  selected_checkpoint?: Record<string, unknown>;
  lags?: number;
  cycle_period?: number;
  horizon?: number;
  [key: string]: unknown;
};

const isFiniteNumber = (value: unknown): value is number =>
  typeof value === "number" && Number.isFinite(value);
const isFiniteFloat32 = (value: unknown): value is number =>
  isFiniteNumber(value) && Number.isFinite(Math.fround(value));

function fail(message: string): never {
  throw new Error(message);
}

function validateParameters(cp: Checkpoint): void {
  const parameters = cp?.parameters;
  if (!parameters || typeof parameters !== "object")
    fail("Checkpoint parameters are missing");
  if (!Array.isArray(parameters.W1) || parameters.W1.length !== 14) {
    fail("W1 must have shape [14,32]");
  }
  for (const row of parameters.W1) {
    if (
      !Array.isArray(row) ||
      row.length !== 32 ||
      !row.every(isFiniteFloat32)
    ) {
      fail("W1 must have shape [14,32] and finite values");
    }
  }
  for (const [name, value, length] of [
    ["b1", parameters.b1, 32],
    ["W2", parameters.W2, 32],
    ["b2", parameters.b2, 1],
  ] as const) {
    if (
      !Array.isArray(value) ||
      value.length !== length ||
      !value.every(isFiniteFloat32)
    ) {
      fail(`${name} must have shape [${length}] and finite values`);
    }
  }
}

function validateSettings(cp: Checkpoint): void {
  if (cp.format !== CHECKPOINT_FORMAT) fail("Unsupported checkpoint format");
  if (cp.lags !== LAGS || cp.cycle_period !== PERIOD || cp.horizon !== 1) {
    fail("Unsupported feature/horizon settings");
  }
  const scaler = cp.scaler;
  if (
    !scaler ||
    !isFiniteNumber(scaler.mean) ||
    !isFiniteNumber(scaler.std) ||
    scaler.std <= 0
  ) {
    fail("Invalid training scaler");
  }
}

function float32Payload(cp: Checkpoint): Uint8Array {
  const values: number[] = [];
  for (const row of cp.parameters.W1) values.push(...row);
  values.push(...cp.parameters.b1, ...cp.parameters.W2, ...cp.parameters.b2);
  if (values.length !== 513) fail("Unexpected float32 model payload");
  const bytes = new Uint8Array(values.length * 4);
  const view = new DataView(bytes.buffer);
  values.forEach((value, index) => view.setFloat32(index * 4, value, true));
  return bytes;
}

function bytesToHex(bytes: Uint8Array): string {
  let result = "";
  for (const byte of bytes) result += byte.toString(16).padStart(2, "0");
  return result;
}

async function sha256Hex(bytes: Uint8Array): Promise<string> {
  const copy = new Uint8Array(bytes.byteLength);
  copy.set(bytes);
  const digest = await globalThis.crypto.subtle.digest("SHA-256", copy.buffer);
  return bytesToHex(new Uint8Array(digest));
}

/** Validate a checkpoint and its canonical little-endian Float32 payload checksum. */
export async function verifyCheckpoint(cp: Checkpoint): Promise<boolean> {
  validateSettings(cp);
  validateParameters(cp);
  const actual = await sha256Hex(float32Payload(cp));
  if (actual !== cp.parameter_sha256) fail("Parameter checksum mismatch");
  return true;
}

function validatePredictionInputs(
  cp: Checkpoint,
  history: number[],
  globalIndex: number
): void {
  validateSettings(cp);
  validateParameters(cp);
  if (!Array.isArray(history) || history.length !== LAGS) {
    fail("Exactly 12 lag flows, oldest to newest, are required");
  }
  if (!history.every(value => isFiniteNumber(value) && value > 0)) {
    fail(
      "History must contain finite positive flows; zero is excluded by this protocol"
    );
  }
  if (!Number.isSafeInteger(globalIndex) || globalIndex < LAGS) {
    fail("Global target index must be an integer >=12");
  }
}

/**
 * Run the original 14 -> 32 ReLU -> 1 MLP. Intermediate products and sums are
 * rounded to Float32 to mirror NumPy's float32 feature and parameter arrays.
 */
export function predict(
  cp: Checkpoint,
  history: number[],
  globalIndex: number
): number {
  validatePredictionInputs(cp, history, globalIndex);
  const { mean, std } = cp.scaler;
  const x = new Float32Array(14);
  for (let i = 0; i < LAGS; i++) x[i] = Math.fround((history[i] - mean) / std);
  const phase = (2 * Math.PI * (globalIndex % PERIOD)) / PERIOD;
  x[12] = Math.fround(Math.sin(phase));
  x[13] = Math.fround(Math.cos(phase));

  const hidden = new Float32Array(32);
  for (let j = 0; j < 32; j++) {
    let sum = Math.fround(cp.parameters.b1[j]);
    for (let i = 0; i < 14; i++) {
      sum = Math.fround(sum + Math.fround(x[i] * cp.parameters.W1[i][j]));
    }
    hidden[j] = sum > 0 ? sum : 0;
  }
  let output = Math.fround(cp.parameters.b2[0]);
  for (let j = 0; j < 32; j++) {
    output = Math.fround(output + Math.fround(hidden[j] * cp.parameters.W2[j]));
  }
  const prediction = output * std + mean;
  if (!Number.isFinite(prediction)) fail("Non-finite forecast");
  return prediction;
}
