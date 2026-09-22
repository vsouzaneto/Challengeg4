import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const home = readFileSync(join(root, "app/page.tsx"), "utf8");
const about = readFileSync(join(root, "app/about-challenge-001/page.tsx"), "utf8");

test("should render the churn about story on the home page when the route is /", () => {
  assert.match(home, /getAboutStory\("001"\)/);
  assert.match(home, /AboutChallenge/);
  assert.match(home, /id="about"|AboutChallenge/);
});

test("should keep the same about story source as about-challenge-001 when both pages load", () => {
  assert.match(about, /getAboutStory\("001"\)/);
  assert.match(home, /getAboutStory\("001"\)/);
});
