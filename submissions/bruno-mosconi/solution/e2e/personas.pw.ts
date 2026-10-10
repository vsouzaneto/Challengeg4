// Medição para o testador de uso: as três personas em 1280 e 390 px, claro e escuro.
// Mede o tempo e os cliques até a tela responder a pergunta de cada persona, e se a resposta
// aparece sem rolar. Os prints vão para test-results/personas/ (não versionados).

import { writeFileSync } from "node:fs";
import { expect, type Locator, type Page, test } from "@playwright/test";

const OUT = "test-results/personas";
const rows: Record<string, string | number | boolean>[] = [];

// O painel desliza em 280 ms e a primeira abertura leva até 900 ms: mede e fotografa depois
// que a tela assenta (C-18, C-25).
const settle = (page: Page, ms = 400) => page.waitForTimeout(ms);

const inView = (l: Locator) =>
	l.evaluate((el) => {
		const r = el.getBoundingClientRect();
		return r.top >= 0 && r.bottom <= innerHeight;
	});

for (const scheme of ["light", "dark"] as const)
	for (const width of [1280, 390]) {
		const tag = `${width}-${scheme === "light" ? "claro" : "escuro"}`;
		test.describe(tag, () => {
			test.use({
				viewport: { width, height: width > 600 ? 800 : 844 },
				colorScheme: scheme,
				reducedMotion: "no-preference",
			});

			test("vendedora (Anna Snelling): o negócio para atacar primeiro", async ({
				page,
			}) => {
				await page.goto("/");
				const t0 = Date.now();
				await page
					.getByRole("button", { name: /^\S+ Anna Snelling/ })
					.first()
					.click();
				const hero = page.locator(".hero");
				await expect(hero).toBeVisible();
				await expect(hero).toHaveCSS("opacity", "1");
				const ms = Date.now() - t0;
				rows.push({
					persona: "vendedora",
					tela: tag,
					pergunta: "por onde começar (D46: herói de ação)",
					ms,
					cliques: 1,
					semRolar: await inView(hero.locator("h2")),
					resposta: (await hero.locator("h2").textContent()) ?? "",
				});
				await settle(page, 1000);
				await page.screenshot({ path: `${OUT}/vendedora-${tag}.png` });
				// O nº 1 dela tem score 0 (D46): continua em 1º, como cartão.
				const t1 = Date.now();
				await page.locator(".mini").first().click();
				const why = page.locator(".panel.open .why");
				await expect(why).toBeVisible();
				await settle(page);
				rows.push({
					persona: "vendedora",
					tela: tag,
					pergunta: "por que o nº 1 está em primeiro",
					ms: Date.now() - t1,
					cliques: 1,
					semRolar: await inView(why),
					resposta: (await why.textContent()) ?? "",
				});
				await page.screenshot({ path: `${OUT}/vendedora-motivo-${tag}.png` });
				await page.keyboard.press("Escape");
				await settle(page);
				const t2 = Date.now();
				await page
					.getByRole("tab", { name: /^(Atualize ou dê perda|Frios) \d/ })
					.click();
				const intro = page.locator(".list-intro");
				await expect(intro).toBeVisible();
				rows.push({
					persona: "vendedora",
					tela: tag,
					pergunta: "o que fazer com os frios",
					ms: Date.now() - t2,
					cliques: 1,
					semRolar: await inView(intro),
					resposta: (await intro.textContent()) ?? "",
				});
				await page.screenshot({ path: `${OUT}/vendedora-frios-${tag}.png` });
			});

			test("gestor (Summer Sewald): funil, valor frio e lista vazia", async ({
				page,
			}) => {
				await page.goto("/");
				const t0 = Date.now();
				await page
					.getByRole("button", { name: /^\S+ Summer Sewald/ })
					.first()
					.click();
				const lead = page.locator(".lead-h1");
				await expect(lead).toBeVisible();
				rows.push({
					persona: "gestor",
					tela: tag,
					pergunta: "quanto valor está frio",
					ms: Date.now() - t0,
					cliques: 1,
					semRolar: await inView(lead),
					resposta: (await lead.textContent()) ?? "",
				});
				const empty = page.locator(".lead-note");
				rows.push({
					persona: "gestor",
					tela: tag,
					pergunta: "qual vendedor tem a lista vazia",
					ms: 0,
					cliques: 0,
					semRolar: await inView(empty),
					resposta: (await empty.textContent()) ?? "",
				});
				await page.screenshot({
					path: `${OUT}/gestor-${tag}.png`,
					fullPage: true,
				});
			});

			test("Head de RevOps: ver outra equipe pelo seletor (D57)", async ({
				page,
			}) => {
				await page.goto("/");
				await page
					.getByRole("button", { name: /^\S+ Summer Sewald/ })
					.first()
					.click();
				const pick = page.getByLabel("Ver a equipe de");
				await expect(pick).toBeVisible();
				const t0 = Date.now();
				await pick.selectOption("Dustin Brinkmann");
				const lead = page.locator(".lead-h1");
				await expect(lead).toContainText("US$ 282 mil");
				rows.push({
					persona: "RevOps",
					tela: tag,
					pergunta: "ver a equipe da Central pelo seletor",
					ms: Date.now() - t0,
					cliques: 1,
					semRolar: await inView(pick),
					resposta: `${await page.locator(".greet").textContent()} ${await lead.textContent()}`,
				});
				await settle(page);
				await page.screenshot({ path: `${OUT}/revops-equipe-${tag}.png` });
			});

			test("Head de RevOps: como o score funciona", async ({ page }) => {
				await page.goto("/");
				await page
					.getByRole("button", { name: /^\S+ Summer Sewald/ })
					.first()
					.click();
				const t0 = Date.now();
				await page
					.getByRole("navigation", { name: "Áreas" })
					.getByRole("link", { name: "Como funciona" })
					.first()
					.click();
				const table = page.locator(".rule table");
				await expect(table).toBeVisible();
				const steps = page.locator(".rule .steps");
				rows.push({
					persona: "RevOps",
					tela: tag,
					pergunta: "a regra: idade, potencial, score (tabela)",
					ms: Date.now() - t0,
					cliques: 1,
					semRolar: await inView(table),
					resposta:
						(await page.locator(".how-head .lead-sub").textContent()) ?? "",
				});
				rows.push({
					persona: "RevOps",
					tela: tag,
					pergunta: "a regra: o exemplo em três passos",
					ms: 0,
					cliques: 0,
					semRolar: await inView(steps),
					resposta: (await steps.locator("li").last().textContent()) ?? "",
				});
				// Leitura: palavras do texto principal (sem "Ver detalhes"), a 200 palavras por minuto.
				const words = (sel: string) =>
					page.locator(sel).evaluate((el) => {
						const c = el.cloneNode(true) as HTMLElement;
						for (const d of c.querySelectorAll("details")) d.remove();
						return (c.textContent ?? "").split(/\s+/).filter(Boolean).length;
					});
				const rule = await words(".rule");
				const all = await words(".how");
				rows.push({
					persona: "RevOps",
					tela: tag,
					pergunta: "leitura: regra / página inteira (palavras)",
					ms: 0,
					cliques: 0,
					semRolar: false,
					resposta: `${rule} / ${all} palavras; ${Math.round((rule / 200) * 60)} s / ${Math.round((all / 200) * 60)} s a 200 palavras/min`,
				});
				await expect(page.locator(".proof")).toHaveCount(3);
				await page.screenshot({
					path: `${OUT}/revops-${tag}.png`,
					fullPage: true,
				});
			});
		});
	}

test.afterAll(() => {
	writeFileSync(`${OUT}/medicoes.json`, JSON.stringify(rows, null, 2));
	console.table(rows.map(({ resposta, ...r }) => r));
});
