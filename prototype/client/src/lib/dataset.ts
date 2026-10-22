import { unzipSync } from "fflate";

export const DATASET_STEPS = 17856;
export const DATASET_SENSORS = 170;
export const DATASET_CHANNELS = 3;
export const TRAIN_END = 12499;
export const HELD_OUT_START = 15189;
export const LAGS = 12;
const MAX_COMPRESSED_BYTES = 64 * 1024 * 1024;
const MAX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024;

export type Dataset = {
  flow: Float32Array;
  steps: number;
  sensors: number;
  sha256: string;
};

export type ParsedNpy = {
  shape: number[];
  data: Float32Array | Float64Array;
  fortran: boolean;
};

function fail(message: string): never {
  throw new Error(message);
}

function sha256Bytes(bytes: Uint8Array): Promise<ArrayBuffer> {
  // Copy into an ordinary ArrayBuffer to satisfy stricter DOM lib typings and
  // avoid handing subtle() a potentially SharedArrayBuffer-backed view.
  const copy = new Uint8Array(bytes.byteLength);
  copy.set(bytes);
  return globalThis.crypto.subtle.digest("SHA-256", copy.buffer);
}

function hex(bytes: Uint8Array): string {
  let result = "";
  for (const byte of bytes) result += byte.toString(16).padStart(2, "0");
  return result;
}

function readUint16LE(view: DataView, offset: number): number {
  if (offset + 2 > view.byteLength) fail("Malformed NPY header");
  return view.getUint16(offset, true);
}

function readUint32LE(view: DataView, offset: number): number {
  if (offset + 4 > view.byteLength) fail("Malformed NPY header");
  return view.getUint32(offset, true);
}

function parseHeaderDict(header: string): { descr: string; fortran: boolean; shape: number[] } {
  const descrMatch = header.match(/['\"]descr['\"]\s*:\s*['\"]([^'\"]+)['\"]/);
  const fortranMatch = header.match(/['\"]fortran_order['\"]\s*:\s*(True|False)/);
  const shapeMatch = header.match(/['\"]shape['\"]\s*:\s*\(([^)]*)\)/);
  if (!descrMatch || !fortranMatch || !shapeMatch) fail("Malformed NPY header dictionary");
  const shape = shapeMatch[1]
    .split(",")
    .map((part) => part.trim())
    .filter(Boolean)
    .map((part) => Number(part));
  if (shape.length === 0 || shape.some((n) => !Number.isSafeInteger(n) || n < 0)) {
    fail("Invalid NPY shape");
  }
  return { descr: descrMatch[1], fortran: fortranMatch[1] === "True", shape };
}

/** Parse a small/large little-endian NPY array without assuming aligned headers. */
export function parseNpy(array: Uint8Array): ParsedNpy {
  if (array.byteLength < 10) fail("Malformed NPY file");
  const view = new DataView(array.buffer, array.byteOffset, array.byteLength);
  if (view.getUint8(0) !== 0x93 || new TextDecoder().decode(array.subarray(1, 6)) !== "NUMPY") {
    fail("Missing NPY magic");
  }
  const major = view.getUint8(6);
  const minor = view.getUint8(7);
  let headerLength: number;
  let headerStart: number;
  if (major === 1) {
    headerLength = readUint16LE(view, 8);
    headerStart = 10;
  } else if (major === 2 || major === 3) {
    headerLength = readUint32LE(view, 8);
    headerStart = 12;
  } else {
    fail(`Unsupported NPY version ${major}.${minor}`);
  }
  if (headerLength > array.byteLength - headerStart) fail("Truncated NPY header");
  const header = new TextDecoder("latin1").decode(array.subarray(headerStart, headerStart + headerLength));
  const { descr, fortran, shape } = parseHeaderDict(header);
  if (descr !== "<f4" && descr !== "<f8") fail("Only little-endian float32/float64 NPY arrays are supported");
  let count = 1;
  for (const dimension of shape) {
    count *= dimension;
    if (!Number.isSafeInteger(count)) fail("NPY array is too large");
  }
  const bytesPerValue = descr === "<f4" ? 4 : 8;
  const dataStart = headerStart + headerLength;
  const expectedBytes = count * bytesPerValue;
  if (expectedBytes > array.byteLength - dataStart) fail("Truncated NPY data");
  if (dataStart + expectedBytes !== array.byteLength) fail("NPY contains an unexpected trailing payload");
  const result = descr === "<f4" ? new Float32Array(count) : new Float64Array(count);
  const dataView = new DataView(array.buffer, array.byteOffset + dataStart, expectedBytes);
  for (let i = 0; i < count; i++) {
    result[i] = descr === "<f4" ? dataView.getFloat32(i * 4, true) : dataView.getFloat64(i * 8, true);
  }
  return { shape, data: result, fortran };
}

async function asBytes(file: File | ArrayBuffer): Promise<Uint8Array> {
  if (file instanceof ArrayBuffer) return new Uint8Array(file);
  if (typeof File !== "undefined" && file instanceof File) return new Uint8Array(await file.arrayBuffer());
  // Cross-realm/browser test doubles can still implement the File contract.
  if (file && typeof (file as File).arrayBuffer === "function") {
    return new Uint8Array(await (file as File).arrayBuffer());
  }
  fail("loadDataset requires a File or ArrayBuffer");
}

/** Load only data.npy from a bounded NPZ, checking its exact benchmark shape/hash. */
export async function loadDataset(file: File | ArrayBuffer, expectedHash: string): Promise<Dataset> {
  const compressed = await asBytes(file);
  if (compressed.byteLength > MAX_COMPRESSED_BYTES) fail("Compressed dataset exceeds 64 MiB limit");
  const actualHash = hex(new Uint8Array(await sha256Bytes(compressed)));
  if (actualHash !== expectedHash) fail("Dataset checksum mismatch");
  let archive: Record<string, Uint8Array>;
  let totalUncompressed = 0;
  try {
    archive = unzipSync(compressed, {
      filter: (entry) => {
        totalUncompressed += entry.originalSize;
        if (entry.originalSize > MAX_UNCOMPRESSED_BYTES || totalUncompressed > MAX_UNCOMPRESSED_BYTES) {
          fail("NPZ uncompressed payload exceeds 100 MiB limit");
        }
        return entry.name === "data.npy";
      },
    });
  } catch (error) {
    if (error instanceof Error && /limit/.test(error.message)) throw error;
    fail(`Malformed NPZ archive: ${error instanceof Error ? error.message : String(error)}`);
  }
  const npy = archive["data.npy"];
  if (!npy) fail("NPZ must contain data.npy");
  if (npy.byteLength > MAX_UNCOMPRESSED_BYTES) fail("NPY exceeds 100 MiB limit");
  const parsed = parseNpy(npy);
  if (parsed.fortran || parsed.shape.length !== 3 || parsed.shape[0] !== DATASET_STEPS || parsed.shape[1] !== DATASET_SENSORS || parsed.shape[2] !== DATASET_CHANNELS) {
    fail("Dataset must be C-order with exact shape [17856,170,3]");
  }
  const flow = new Float32Array(DATASET_STEPS * DATASET_SENSORS);
  const source = parsed.data;
  for (let t = 0; t < DATASET_STEPS; t++) {
    for (let sensor = 0; sensor < DATASET_SENSORS; sensor++) {
      const value = source[(t * DATASET_SENSORS + sensor) * DATASET_CHANNELS];
      flow[t * DATASET_SENSORS + sensor] = value;
    }
  }
  return { flow, steps: DATASET_STEPS, sensors: DATASET_SENSORS, sha256: actualHash };
}

function checkSensor(ds: Dataset, sensor: number): void {
  if (!Number.isInteger(sensor) || sensor < 0 || sensor >= ds.sensors) fail("Sensor must be an integer in [0,169]");
}

function checkTarget(ds: Dataset, index: number): void {
  if (!Number.isInteger(index) || index < HELD_OUT_START || index >= ds.steps) {
    fail("Target index must be a held-out index in [15189,17856)");
  }
}

function value(ds: Dataset, time: number, sensor: number): number {
  const result = ds.flow[time * ds.sensors + sensor];
  if (!Number.isFinite(result) || result <= 0) fail("Window contains a non-finite or zero flow");
  return result;
}

export function getWindow(ds: Dataset, sensor: number, index: number): { history: number[]; actual: number; persistence: number } {
  checkSensor(ds, sensor);
  checkTarget(ds, index);
  const history: number[] = [];
  for (let time = index - LAGS; time < index; time++) history.push(value(ds, time, sensor));
  const actual = value(ds, index, sensor);
  return { history, actual, persistence: history[history.length - 1] };
}

export function eligibleIndices(ds: Dataset, sensor: number): number[] {
  checkSensor(ds, sensor);
  const indices: number[] = [];
  for (let index = HELD_OUT_START; index < ds.steps; index++) {
    let valid = true;
    for (let time = index - LAGS; time <= index; time++) {
      const current = ds.flow[time * ds.sensors + sensor];
      if (!Number.isFinite(current) || current <= 0) {
        valid = false;
        break;
      }
    }
    if (valid) indices.push(index);
  }
  return indices;
}
