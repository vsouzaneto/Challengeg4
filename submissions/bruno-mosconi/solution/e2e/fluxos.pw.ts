// Fluxos das personas no build de produção (CA4, CA5, CA6, CA14) e os ajustes da D44.

import { expect, type Page, test } from "@playwright/test";

/** Na entrada, o botão da pessoa começa pelas iniciais e o nome ("ZL Zane Levy …"); as sugestões repetem alguns nomes. */
const enter = async (page: Page, name: string) => {
	await page.goto("/#entrada");
	await page
		.getByRole("button", { name: new RegExp(`^\\S+ ${name}`) })
		.first()
		.click();
};
const panel = (page: Page) =>
	page.getByRole("dialog", { name: "Detalhe do negócio" });
// No celular, a aba mostra o rótulo curto, e o nome acessível é o texto visível (WCAG 2.5.3).
const SHORT: Record<string, string> = {
	"Prioridades da semana": "Prioridades",
	"Atualize ou dê perda": "Frios",
	Prospecção: "Prospecção",
};
const tab = (page: Page, name: string) =>
	page.getByRole("tab", { name: new RegExp(`^(${name}|${SHORT[name]}) \\d`) });

test("vendedor: o nº 1 é o herói, e o painel mostra a conta com o mesmo número da frase", async ({
	page,
}) => {
	await enter(page, "Zane Levy");
	const hero = page.locator(".hero");
	await expect(hero).toContainText("GTX Plus Pro");
	await expect(hero).toContainText("The New York Inquirer");
	await expect(hero).toContainText("US$ 2.577");
	await expect(hero).toContainText("Esfria em 69 dias");
	await expect(
		hero.getByRole("img", { name: "Score 98 de 100" }),
	).toBeVisible();
	await page.getByRole("button", { name: "Ver o motivo" }).click();
	const p = panel(page);
	await expect(p).toContainText(
		"De cada 100 negócios iniciados, 47 fecharam venda.",
	);
	await expect(p).toContainText("× 47%");
	await expect(p).toContainText("US$ 2.577");
	await expect(p).toContainText("1º na sua semana");
	await page.locator(".mini", { hasText: "Gogozoom" }).click();
	await expect(p).toContainText("2º na sua semana");
	await page.keyboard.press("Escape");
	await expect(page.locator(".panel.open")).toHaveCount(0);
	await expect(page.locator("[role=img] button")).toHaveCount(0);
});

test("saudação: conta só os 5 primeiros (D47)", async ({ page }) => {
	await enter(page, "Zane Levy");
	await expect(page.locator(".greet")).toContainText(
		/Comece por estes 5\. (Destes, .+ nesta semana\.|Nenhum deles esfria nesta semana\.)/,
	);
});

test("herói com score baixo: vira a prospecção, e o nº 1 fica como cartão (D46)", async ({
	page,
}) => {
	await enter(page, "Anna Snelling");
	await expect(page.locator(".greet")).toContainText("Comece pela prospecção.");
	const hero = page.locator(".hero");
	await expect(hero.locator("h2")).toHaveText(
		"55 negócios em prospecção para iniciar contato",
	);
	// O valor a preço de lista é apoio, não o número grande (que nos outros é o potencial).
	await expect(hero.locator(".acct")).toContainText(
		"US$ 77.845 a preço de lista",
	);
	await expect(hero.locator(".hero-pot")).toHaveCount(0);
	await expect(hero).toContainText("score 0");
	const card = page.locator(".mini", { hasText: "MG Special" });
	await expect(card).toContainText("1º");
	// D56: o painel do nº 1 não contradiz o herói nem diz "mais potencial que 0%".
	await card.click();
	const p = panel(page);
	await expect(p).toContainText("Resolva com uma mensagem rápida");
	await expect(p).toContainText("Está entre os de menor potencial dos 298");
	await expect(p).not.toContainText("Peça uma resposta");
	await expect(p).not.toContainText("Mais potencial que 0%");
	await page.keyboard.press("Escape");
	await hero.getByRole("button", { name: "Ver a prospecção" }).click();
	await expect(tab(page, "Prospecção")).toHaveAttribute(
		"aria-selected",
		"true",
	);
});

test("herói de ação visto pelo gestor: fala de Anna, não de 'seu' (D46)", async ({
	page,
}) => {
	await enter(page, "Dustin Brinkmann");
	await page
		.getByRole("button", { name: /Anna Snelling/ })
		.first()
		.click();
	// A prévia segue a regra da semana dela: começa pela prospecção.
	const preview = page.locator(".preview");
	await expect(preview).toContainText("Começaria pela prospecção");
	await expect(preview).toContainText(
		"55 negócios em prospecção para iniciar contato, US$ 77.845 a preço de lista",
	);
	await page.getByRole("button", { name: "Abrir a semana de Anna" }).click();
	const hero = page.locator(".hero");
	await expect(hero).toContainText("O nº 1 de Anna, MG Special, tem score 0");
	await expect(hero).not.toContainText("O seu nº 1");
});

test("equipe da Central: 99,8% frio (não 100%) e a prospecção como trabalho da equipe", async ({
	page,
}) => {
	await enter(page, "Dustin Brinkmann");
	await expect(page.locator(".lead-sub")).toContainText(
		"99,8% do valor em andamento está frio",
	);
	await expect(page.locator(".prospect-note")).toContainText(
		"204 negócios em prospecção esperam o primeiro contato",
	);
	await expect(page.locator(".prospect-note")).toContainText(
		"A equipe precisa transformar prospecção em negócio.",
	);
	await enter(page, "Summer Sewald");
	await expect(page.locator(".prospect-note")).toHaveCount(0);
});

test("quem é você: sugestões no topo, o que cada um vai encontrar e os sem negócios no fim", async ({
	page,
}) => {
	await page.goto("/#semana");
	// Visitante novo: o endereço acompanha a tela.
	await expect(page).toHaveURL(/#entrada$/);
	const groups = page.locator(".people > div");
	await expect(groups.first().locator("h2")).toHaveText("Para conhecer o app");
	await expect(groups.first()).toContainText("Semana cheia");
	await expect(groups.first()).toContainText("31 prioridades");
	await expect(groups.first()).toContainText(
		"Semana que começa pela prospecção",
	);
	await expect(groups.first()).toContainText("US$ 718 mil frios na equipe");
	await expect(groups.last().locator("h2")).toHaveText(
		"Sem negócios em andamento",
	);
	await expect(groups.last()).toContainText("Carl Lin");
	await expect(
		page.getByRole("button", {
			name: /Anna Snelling.*Semana de prospecção: 55 negócios/,
		}),
	).toHaveCount(2);
});

test("as abas ficam no mesmo lugar para todo vendedor", async ({ page }) => {
	const place = async (name: string) => {
		await enter(page, name);
		const g = await page.locator(".greet").boundingBox();
		const t = await page.getByRole("tablist").boundingBox();
		return { below: (t?.y ?? 0) > (g?.y ?? 0) + (g?.height ?? 0) - 1, x: t?.x };
	};
	const zane = await place("Zane Levy");
	const anna = await place("Anna Snelling");
	expect(zane.below && anna.below).toBe(true);
	expect(anna.x).toBe(zane.x);
});

test("como funciona: a regra na primeira tela, as três provas e os termos técnicos só nos detalhes", async ({
	page,
}) => {
	await page.setViewportSize({ width: 1280, height: 800 });
	await enter(page, "Zane Levy");
	await page.getByRole("link", { name: "Como funciona" }).first().click();
	const how = page.locator(".how");
	// A primeira tabela inteira cabe na primeira tela em 1280 (D48).
	const last = page.getByRole("row", { name: /Mais de 138 dias/ });
	const box = await last.boundingBox();
	expect((box?.y ?? 0) + (box?.height ?? 0)).toBeLessThanOrEqual(800);
	await expect(how).toContainText("O nº 1 do Zane em 31/12/2017: GTX Plus Pro");
	await expect(how).toContainText("US$ 2.577");
	await expect(how).toContainText(
		"Score 98: o potencial dele passa o de 98 de cada 100",
	);
	for (const t of [
		"Quanto mais tempo o negócio fica aberto, menor a chance de fechar.",
		"É ilusão: os que nunca fecham ficam fora da conta.",
		"Os 10 primeiros de cada vendedor trouxeram 41%",
		"pelo preço, 33%; no sorteio, 14%",
		"O resultado se repetiu nas três datas.",
		"Um modelo de inteligência artificial mais complexo chegou a 43%",
		"Não mudam: a diferença é do tamanho que o acaso produz.",
		"Olhamos a taxa de ganho",
		"Os dados não separam o efeito do vendedor do efeito da carteira e da região.",
		"O vendedor não muda a chance de fechar, mas muda quanto do funil dele esfria",
		"A base começa cortada em março de 2017.",
		"A chance é histórico, não previsão, e superestima a venda.",
		"O fim de trimestre pesa",
	])
		await expect(how).toContainText(t);
	// Linguagem: fora de "Ver detalhes", nenhum termo técnico.
	const visible = await how.evaluate((el) => {
		const c = el.cloneNode(true) as HTMLElement;
		for (const d of c.querySelectorAll("details")) d.remove();
		return c.textContent ?? "";
	});
	expect(visible).not.toMatch(
		/backtest|coorte|margem de erro|p-valor|IC 95|qui-quadrado|gradient|bootstrap/i,
	);
	const more = how.locator("details").nth(1);
	await expect(more.getByText(/Backtest nas datas/)).toBeHidden();
	await more.locator("summary").click();
	await expect(more.getByText(/Backtest nas datas/)).toBeVisible();
});

test("troca de data com movimento: o herói de 31/12 não aparece em 30/09 nem por um quadro (D34)", async ({
	browser,
}) => {
	const ctx = await browser.newContext({
		baseURL: "http://localhost:4173",
		reducedMotion: "no-preference",
	});
	const page = await ctx.newPage();
	await enter(page, "Zane Levy");
	await expect(page.locator(".hero .acct")).toHaveText("The New York Inquirer");
	await page
		.getByRole("group", { name: "Data dos dados" })
		.getByRole("button", { name: "30/09" })
		.click();
	// Logo depois do clique, sem esperar: nenhuma empresa no herói, e o herói visível é o de 30/09.
	expect(await page.locator(".hero .acct").count()).toBe(0);
	await expect(page.locator(".hero:not(.waiting) h2")).toHaveText(
		"GTX Plus Pro",
	);
	await expect(page.locator(".hero")).toContainText("US$ 2.796");
	await ctx.close();
});

test("a escolha da pessoa fica salva neste aparelho", async ({ page }) => {
	await enter(page, "Zane Levy");
	await page.goto("/");
	await expect(page.locator(".hero")).toContainText("GTX Plus Pro");
	await page.getByRole("link", { name: "Trocar de pessoa" }).click();
	await expect(
		page.getByRole("heading", { name: "Quem é você?" }),
	).toBeVisible();
});

test("sem empresa: cartões e lista dizem 'Sem empresa no CRM'; o ID só aparece no painel", async ({
	page,
}) => {
	await enter(page, "Zane Levy");
	await expect(
		page.locator(".mini", { hasText: "Sem empresa no CRM" }).first(),
	).toBeVisible();
	await page.getByRole("button", { name: /Ver todos os 31/ }).click();
	await tab(page, "Atualize ou dê perda").click();
	await tab(page, "Prioridades da semana").click();
	// IDs reais do Zane: o nº 1 e dois sem empresa (3º e 5º).
	for (const id of ["FZWU2I30", "4R4QF0ZU", "LOHJU3OB"])
		await expect(page.locator(".stack")).not.toContainText(id);
	await page
		.locator(".mini", { hasText: "Sem empresa no CRM" })
		.first()
		.click();
	await expect(panel(page)).toContainText(
		/Sem empresa no CRM\. Negócio [A-Z0-9]{8}\./,
	);
});

test("gestor: a frase da equipe, quem não tem negócio e a semana de cada vendedor", async ({
	page,
}) => {
	await enter(page, "Summer Sewald");
	await expect(page.locator(".lead-h1")).toHaveText(
		"US$ 718 mil frios na equipe. Kary concentra US$ 229 mil.",
	);
	await expect(page.locator(".member", { hasText: "Carl Lin" })).toContainText(
		"Nenhum negócio no CRM",
	);
	await page.locator(".member", { hasText: "James Ascencio" }).click();
	await page.getByRole("button", { name: "Abrir a semana de James" }).click();
	await expect(page.locator(".greet")).toContainText("A semana de James.");
	await page.getByRole("button", { name: "Minha equipe" }).click();
	await expect(page.locator(".lead-note")).toHaveText(
		"Sem prioridade nesta semana: Carl Lin.",
	);
	await page.locator(".member", { hasText: "Carl Lin" }).click();
	await expect(page.locator(".empty")).toContainText(
		"Carl não tem negócio no CRM",
	);
	await expect(page.locator(".empty")).not.toContainText("Você");
});

test("estado vazio: sem negócio quente, leva para os frios", async ({
	page,
}) => {
	await enter(page, "Cecily Lampkin");
	await expect(page.getByText("Nada para avançar esta semana.")).toBeVisible();
	await page.getByRole("button", { name: "Ver os frios" }).click();
	await expect(tab(page, "Atualize ou dê perda")).toHaveAttribute(
		"aria-selected",
		"true",
	);
	await page.locator(".row").first().click();
	await expect(panel(page)).toContainText("Atualize ou dê perda");
});

test("estado vazio: nada em andamento e nenhum negócio no CRM", async ({
	page,
}) => {
	await enter(page, "Garret Kinder");
	await expect(page.getByText("Nada em andamento nesta data.")).toBeVisible();
	await enter(page, "Carl Lin");
	await expect(
		page.getByText("Você não tem negócio no CRM", { exact: false }),
	).toBeVisible();
});

test("data passada: 30/06 bloqueada; em 30/09 sem empresa (nem a falta dela) e sem prospecção", async ({
	page,
}) => {
	await enter(page, "Zane Levy");
	const dates = page.getByRole("group", { name: "Data dos dados" });
	await expect(dates.getByRole("button", { name: "30/06" })).toBeDisabled();
	await dates.getByRole("button", { name: "30/09" }).click();
	await expect(page.locator(".past-note")).toContainText("30/09/2017");
	await expect(page.locator(".stack .acct")).toHaveCount(0);
	await expect(page.getByText("Sem empresa no CRM")).toHaveCount(0);
	await tab(page, "Prospecção").click();
	await expect(
		page.getByText("Prospecção só na data mais recente."),
	).toBeVisible();
});

test("computador: 'Sua carteira no tempo' fica fixa ao rolar", async ({
	page,
}) => {
	await page.setViewportSize({ width: 1280, height: 800 });
	await enter(page, "Zane Levy");
	await page.getByRole("button", { name: /Ver todos os 31/ }).click();
	await page.mouse.wheel(0, 1400);
	await expect.poll(() => page.evaluate(() => scrollY)).toBeGreaterThan(1000);
	const top = await page
		.locator(".thermo-card")
		.evaluate((el) => el.getBoundingClientRect().top);
	expect(top).toBeGreaterThanOrEqual(44);
	expect(top).toBeLessThanOrEqual(80);
});

test("celular: as três abas cabem e a folha fecha ao arrastar para baixo", async ({
	page,
}) => {
	await page.setViewportSize({ width: 390, height: 844 });
	await enter(page, "Zane Levy");
	for (const name of [
		"Prioridades da semana",
		"Atualize ou dê perda",
		"Prospecção",
	]) {
		const box = await tab(page, name).boundingBox();
		expect(box && box.x >= 0 && box.x + box.width <= 390, name).toBe(true);
	}
	await page.getByRole("button", { name: "Ver o motivo" }).click();
	await expect(page.locator(".panel.open")).toHaveCount(1);
	const grip = await page.locator(".panel-grip").boundingBox();
	if (!grip) throw new Error("sem alça");
	await page.mouse.move(grip.x + 40, grip.y + 20);
	await page.mouse.down();
	await page.mouse.move(grip.x + 40, grip.y + 120, { steps: 5 });
	await page.mouse.move(grip.x + 40, grip.y + 260, { steps: 5 });
	await page.mouse.up();
	await expect(page.locator(".panel.open")).toHaveCount(0);
});

for (const width of [1280, 390])
	test(`sem rolagem lateral em ${width} px`, async ({ page }) => {
		await page.setViewportSize({ width, height: 900 });
		for (const seller of ["Zane Levy", "Anna Snelling", "Darcel Schlecht"]) {
			await enter(page, seller);
			for (const name of [
				"Prioridades da semana",
				"Atualize ou dê perda",
				"Prospecção",
			]) {
				await tab(page, name).click();
				const overflow = await page.evaluate(
					() => document.documentElement.scrollWidth - innerWidth,
				);
				expect(overflow, `${seller}, ${name}`).toBeLessThanOrEqual(0);
			}
		}
		await enter(page, "Summer Sewald");
		const overflow = await page.evaluate(
			() => document.documentElement.scrollWidth - innerWidth,
		);
		expect(overflow, "equipe").toBeLessThanOrEqual(0);
		await page.goto("/#como-funciona");
		await page.locator(".how details").first().waitFor();
		const how = await page.evaluate(
			() => document.documentElement.scrollWidth - innerWidth,
		);
		expect(how, "como funciona").toBeLessThanOrEqual(0);
	});

test("sem chamada de rede: toda requisição é do próprio site (CA9)", async ({
	page,
	baseURL,
}) => {
	const outside: string[] = [];
	page.on("request", (r) => {
		const url = r.url();
		if (!url.startsWith(baseURL ?? "") && !url.startsWith("data:"))
			outside.push(url);
	});
	await enter(page, "Zane Levy");
	await page.getByRole("button", { name: "Ver o motivo" }).click();
	await page.keyboard.press("Escape");
	await tab(page, "Prospecção").click();
	await enter(page, "Summer Sewald");
	await page.goto("/#como-funciona");
	await page.locator(".how details").first().waitFor();
	for (const d of await page.locator(".how details summary").all())
		await d.click();
	await page.waitForLoadState("networkidle");
	expect(outside).toEqual([]);
});

test('celular: o selo "o exemplo" não quebra no meio', async ({ page }) => {
	await page.setViewportSize({ width: 390, height: 844 });
	await page.goto("/#como-funciona");
	const tag = page.locator(".mine-tag");
	const h = await tag.evaluate((el) => {
		const r = el.getClientRects();
		return r.length;
	});
	expect(h).toBe(1);
});

test("seletor de equipe: qualquer equipe sem voltar à entrada, e de volta à própria (D57)", async ({
	page,
}) => {
	await enter(page, "Summer Sewald");
	const pick = page.getByLabel("Ver a equipe de");
	await expect(pick).toHaveValue("Summer Sewald");
	await pick.selectOption("Dustin Brinkmann");
	await expect(page.locator(".greet")).toHaveText(
		"A equipe de Dustin Brinkmann.",
	);
	await expect(page.locator(".lead-h1")).toContainText(
		"US$ 282 mil frios na equipe",
	);
	await expect(page.locator(".prospect-note")).toBeVisible();
	// Abrir um vendedor da outra equipe e voltar mantém a equipe escolhida.
	await page.getByRole("button", { name: "Abrir a semana de Anna" }).click();
	await expect(page.locator(".hero")).toContainText("O nº 1 de Anna");
	await page.getByRole("button", { name: "Minha equipe" }).click();
	await expect(pick).toHaveValue("Dustin Brinkmann");
	await expect(pick.locator("option:checked")).toHaveText(
		"Dustin Brinkmann, Central",
	);
	await page.getByRole("button", { name: "Voltar à minha equipe" }).click();
	await expect(pick).toHaveValue("Summer Sewald");
	await expect(
		page.getByRole("button", { name: "Voltar à minha equipe" }),
	).toHaveCount(0);
	await pick.selectOption("Dustin Brinkmann");
	await pick.selectOption("Summer Sewald");
	await expect(page.locator(".greet")).toHaveText("Bom dia, Summer.");
	// Um vendedor também vê outras equipes.
	await enter(page, "Zane Levy");
	await page.getByRole("link", { name: "Minha equipe" }).first().click();
	await expect(page.getByLabel("Ver a equipe de")).toHaveValue("Summer Sewald");
	await page.getByLabel("Ver a equipe de").selectOption("Cara Losch");
	await expect(page.locator(".greet")).toHaveText("A equipe de Cara Losch.");
});

test("como funciona: o gráfico da prova 1 tem tabela (CA16)", async ({
	page,
}) => {
	await page.goto("/#como-funciona");
	const table = page.locator(".pair-table");
	await expect(
		table.getByRole("row", { name: /0 a 29 dias 47 63/ }),
	).toBeVisible();
	await expect(
		table.getByRole("row", { name: /120 a 138 dias 9 76/ }),
	).toBeVisible();
});
