import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const catalog = readFileSync(join(root, "lib/spa/applications.ts"), "utf8");

test("should list two Single-SPA applications when the catalog is loaded", () => {
  assert.match(catalog, /name: "@g4\/chatbot"/);
  assert.match(catalog, /name: "@g4\/dashboards"/);
  assert.match(catalog, /activeWhen: "\/sdk\/chatbot"/);
  assert.match(catalog, /activeWhen: "\/sdk\/dashboards"/);
});

test("should point each application at its monorepo origin when defaults are used", () => {
  assert.match(catalog, /defaultOrigin: "http:\/\/localhost:3030"/);
  assert.match(catalog, /defaultOrigin: "http:\/\/localhost:3010"/);
  assert.equal((catalog.match(/defaultOrigin: "http:\/\//g) || []).length, 2);
});
