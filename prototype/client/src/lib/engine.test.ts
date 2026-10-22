import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { predict, verifyCheckpoint, type Checkpoint } from "./engine";

type Fixture = {
  tolerance_flow_units: number;
  case_count: number;
  cases: Array<{ history: number[]; globalIndex: number }>;
  models: Record<string, { checkpoint: Checkpoint; predictions: number[] }>;
};

const fixture = JSON.parse(readFileSync(new URL("./parity-fixtures.json", import.meta.url), "utf8")) as Fixture;

for (const [name, model] of Object.entries(fixture.models)) {
  describe(`${name} browser/NumPy parity`, () => {
    it(`verifies the supplied checkpoint and predicts all ${fixture.case_count} diagnostic histories`, async () => {
      await expect(verifyCheckpoint(model.checkpoint)).resolves.toBe(true);
      const errors = fixture.cases.map((diagnostic, index) =>
        Math.abs(predict(model.checkpoint, diagnostic.history, diagnostic.globalIndex) - model.predictions[index]),
      );
      const maximumAbsoluteDifference = Math.max(...errors);
      expect(maximumAbsoluteDifference).toBeLessThanOrEqual(fixture.tolerance_flow_units);
      // Keep this measured value visible in test output without presenting it as a traffic metric.
      console.info(`[unit parity] ${name}: max abs difference ${maximumAbsoluteDifference}`);
    });
  });
}

describe("checkpoint validation", () => {
  it("rejects a mutated weight through the canonical Float32 checksum", async () => {
    const cp = structuredClone(fixture.models.centralised.checkpoint);
    cp.parameters.W1[0][0] += 0.0001;
    await expect(verifyCheckpoint(cp)).rejects.toThrow(/checksum/i);
  });

  it.each([
    ["short history", [1, 2, 3], 12],
    ["zero history", Array(11).fill(1).concat(0), 12],
    ["NaN history", Array(11).fill(1).concat(Number.NaN), 12],
    ["fractional index", Array(12).fill(1), 12.5],
    ["too-early index", Array(12).fill(1), 11],
  ])("rejects %s", (_label, history, index) => {
    expect(() => predict(fixture.models.centralised.checkpoint, history as number[], index as number)).toThrow();
  });

  it("rejects an invalid scaler or feature setting before inference", () => {
    const badScaler = structuredClone(fixture.models.centralised.checkpoint);
    badScaler.scaler.std = 0;
    expect(() => predict(badScaler, Array(12).fill(1), 12)).toThrow(/scaler/i);
    const badSettings = structuredClone(fixture.models.centralised.checkpoint);
    badSettings.lags = 11;
    expect(() => predict(badSettings, Array(12).fill(1), 12)).toThrow(/settings|feature/i);
  });
});
