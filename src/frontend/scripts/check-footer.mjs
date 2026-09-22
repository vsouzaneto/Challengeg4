import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const footer = readFileSync(join(root, "components/landing/footer-section.tsx"), "utf8");

test("should list G4 institutional pages when the footer columns are rendered", () => {
  assert.match(footer, /"Páginas Institucionais"/);
  assert.match(footer, /name: "Site", href: "https:\/\/g4business.com\/"/);
  assert.match(
    footer,
    /name: "G4 Ai Master", href: "https:\/\/ats\.g4business\.com\/application\/8889da8b-b1b2-46bb-b81f-e825477a3f5b"/,
  );
  assert.match(footer, /name: "Instagram", href: "https:\/\/www\.instagram\.com\/g4\.business\/"/);
  assert.doesNotMatch(footer, /ds3atucsd/);
});

test("should list the G4 podcast on Spotify when the former HDSI column is rendered", () => {
  assert.match(footer, /"Podcast G4"/);
  assert.match(
    footer,
    /name: "Spotify", href: "https:\/\/open\.spotify\.com\/show\/0uNjUO4oP1UDaV0JHRAhXJ"/,
  );
  assert.doesNotMatch(footer, /HDSI|datascience\.ucsd/);
});
