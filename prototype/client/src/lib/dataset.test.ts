import { zipSync } from "fflate";
import { describe, expect, it } from "vitest";
import {
  DATASET_CHANNELS,
  DATASET_SENSORS,
  DATASET_STEPS,
  HELD_OUT_START,
  eligibleIndices,
  getWindow,
  loadDataset,
  parseNpy,
  type Dataset,
} from "./dataset";

function npy(values: number[], shape: number[], descr = "<f4", fortran = false): Uint8Array {
  const itemBytes = descr === "<f8" ? 8 : 4;
  const shapeText = shape.length === 1 ? `${shape[0]},` : shape.join(", ");
  let header = `{'descr': '${descr}', 'fortran_order': ${fortran ? "True" : "False"}, 'shape': (${shapeText}), }`;
  const preamble = 10;
  const padding = (16 - ((preamble + header.length + 1) % 16)) % 16;
  header += " ".repeat(padding) + "\n";
  const encoded = new TextEncoder().encode(header);
  const out = new Uint8Array(preamble + encoded.length + values.length * itemBytes);
  out.set([0x93, 0x4e, 0x55, 0x4d, 0x50, 0x59, 1, 0], 0);
  new DataView(out.buffer).setUint16(8, encoded.length, true);
  out.set(encoded, preamble);
  const view = new DataView(out.buffer);
  values.forEach((value, i) => descr === "<f8" ? view.setFloat64(preamble + encoded.length + i * 8, value, true) : view.setFloat32(preamble + encoded.length + i * 4, value, true));
  return out;
}

async function sha256(data: Uint8Array): Promise<string> {
  const copy = new Uint8Array(data.byteLength);
  copy.set(data);
  const digest = await crypto.subtle.digest("SHA-256", copy.buffer);
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function syntheticDataset(): Dataset {
  const flow = new Float32Array(DATASET_STEPS * DATASET_SENSORS);
  for (let time = 0; time < DATASET_STEPS; time++) {
    for (let sensor = 0; sensor < DATASET_SENSORS; sensor++) {
      flow[time * DATASET_SENSORS + sensor] = time + sensor + 1;
    }
  }
  return { flow, steps: DATASET_STEPS, sensors: DATASET_SENSORS, sha256: "synthetic" };
}

describe("NPY/NPZ parser", () => {
  it("decodes unaligned little-endian float32 and float64 payloads", () => {
    const f4 = parseNpy(npy([1.25, 2.5], [2], "<f4"));
    expect(f4.shape).toEqual([2]);
    expect(Array.from(f4.data)).toEqual([1.25, 2.5]);
    const f8 = parseNpy(npy([Math.PI], [1], "<f8"));
    expect(f8.data[0]).toBe(Math.PI);
  });

  it("reports Fortran order for parser callers", () => {
    expect(parseNpy(npy([1, 2, 3, 4], [2, 2], "<f4", true)).fortran).toBe(true);
  });

  it("rejects unsupported dtype, malformed bytes, and bad loader shape", async () => {
    expect(() => parseNpy(npy([1], [1], "|i4"))).toThrow(/little-endian|float/i);
    expect(() => parseNpy(new Uint8Array([1, 2, 3]))).toThrow(/NPY/i);
    const archive = zipSync({ "data.npy": npy([1, 2, 3, 4], [2, 2]) });
    const copy = new Uint8Array(archive.byteLength);
    copy.set(archive);
    await expect(loadDataset(copy.buffer, await sha256(archive))).rejects.toThrow(/shape/i);
  });
});

describe("held-out complete-case windows", () => {
  it("returns oldest-to-newest history, target, and persistence", () => {
    const ds = syntheticDataset();
    const index = HELD_OUT_START;
    expect(getWindow(ds, 0, index)).toEqual({
      history: Array.from({ length: 12 }, (_, i) => index - 11 + i),
      actual: index + 1,
      persistence: index,
    });
  });

  it("rejects bounds, non-integer sensors, and zero/non-finite values", () => {
    const ds = syntheticDataset();
    expect(() => getWindow(ds, 0, HELD_OUT_START - 1)).toThrow(/held-out/i);
    expect(() => getWindow(ds, 170, HELD_OUT_START)).toThrow(/sensor/i);
    expect(() => getWindow(ds, 0.5, HELD_OUT_START)).toThrow(/sensor/i);
    ds.flow[(HELD_OUT_START - 1) * DATASET_SENSORS] = 0;
    expect(() => getWindow(ds, 0, HELD_OUT_START)).toThrow(/zero/i);
    ds.flow[(HELD_OUT_START - 1) * DATASET_SENSORS] = Number.NaN;
    expect(() => getWindow(ds, 0, HELD_OUT_START)).toThrow(/finite|zero/i);
  });

  it("eligibility is sensor-specific but never target-selection driven", () => {
    const ds = syntheticDataset();
    ds.flow[HELD_OUT_START * DATASET_SENSORS] = 0;
    expect(eligibleIndices(ds, 0)).not.toContain(HELD_OUT_START);
    expect(eligibleIndices(ds, 1)).toContain(HELD_OUT_START);
  });
});
