import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { DATA_DIR, loadDataset, readRaw } from "../node/load.ts";
import { day, isoDate, rows } from "./data.ts";

describe("dados", () => {
	it("os CSVs são os originais (SHA-256 igual ao do zip do Kaggle, ver FONTE.md)", () => {
		const sums = readFileSync(`${DATA_DIR}SHA256SUMS`, "utf8")
			.trim()
			.split("\n");
		expect(sums).toHaveLength(5);
		for (const line of sums) {
			const [hash, file] = line.split(/\s+/);
			const actual = createHash("sha256")
				.update(readFileSync(`${DATA_DIR}${file}`))
				.digest("hex");
			expect(actual, file).toBe(hash);
		}
	});

	it("nenhuma linha tem aspas nem número errado de colunas (senão o parser simples não serve)", () => {
		const raw = readRaw();
		for (const text of Object.values(raw))
			expect(() => rows(text)).not.toThrow();
	});

	it("todo produto do funil tem preço depois da normalização GTXPro → GTX Pro", () => {
		const ds = loadDataset();
		expect(ds.deals.every((d) => ds.prices.has(d.product))).toBe(true);
		expect(ds.deals.some((d) => d.product === "GTXPro")).toBe(false);
	});

	it("datas ida e volta", () => {
		expect(isoDate(day("2017-03-01"))).toBe("2017-03-01");
		expect(day("2017-12-31") - day("2017-08-15")).toBe(138);
	});
});
