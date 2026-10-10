import { describe, expect, it } from "vitest";
import { date, pct, usd, usdShort } from "./format.ts";

describe("formatos da tela (pt-BR, moeda em US$)", () => {
	it("valor inteiro", () => {
		expect(usd(26_768)).toBe("US$ 26.768");
		expect(usd(182_927.6)).toBe("US$ 182.928");
	});

	it("valor curto para a barra de números", () => {
		expect(usdShort(3_892_229)).toBe("US$ 3,89 mi");
		expect(usdShort(465_914)).toBe("US$ 466 mil");
		expect(usdShort(9_870)).toBe("US$ 9.870");
	});

	it("porcentagem e data", () => {
		expect(pct(0.3079)).toBe("30,8%");
		expect(date(17531)).toBe("31/12/2017");
	});
});
