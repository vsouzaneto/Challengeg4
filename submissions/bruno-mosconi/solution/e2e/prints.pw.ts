// Prints e vídeo dos incrementos 4 e 5 (D41–D48): 1280 e 390 px, claro e escuro.
// Saída em process-log/screenshots/03-app/. Para o repositório não pesar, os PNG viram WebP
// quando o cwebp está instalado; sem ele, ficam em PNG.

import { execFileSync } from "node:child_process";
import { readdirSync, renameSync, rmSync, unlinkSync } from "node:fs";
import { type Page, test } from "@playwright/test";

const DIR = "../process-log/screenshots/03-app";
const enter = async (page: Page, name: string) => {
	await page.goto("/#entrada");
	await page
		.getByRole("button", { name: new RegExp(`^\\S+ ${name}`) })
		.first()
		.click();
};

for (const scheme of ["light", "dark"] as const)
	for (const width of [1280, 390]) {
		const tag = `${width}-${scheme === "light" ? "claro" : "escuro"}`;
		const desk = width > 600;
		test.describe(tag, () => {
			test.use({
				viewport: { width, height: desk ? 860 : 844 },
				deviceScaleFactor: desk ? 1 : 2,
				colorScheme: scheme,
			});
			const shot = (page: Page, name: string, full = desk) =>
				page.screenshot({ path: `${DIR}/${name}-${tag}.png`, fullPage: full });

			test("vendedor, painel e equipe", async ({ page }) => {
				await enter(page, "Zane Levy");
				await shot(page, "02-vendedor");
				if (!desk) {
					await page.locator(".thermo-card").scrollIntoViewIfNeeded();
					await shot(page, "02-vendedor-rolada");
					await page.evaluate(() => scrollTo(0, 0));
				}
				await page.getByRole("button", { name: "Ver o motivo" }).click();
				await page.waitForTimeout(350);
				await shot(page, "03-painel", false);
				await page.keyboard.press("Escape");
				await enter(page, "Summer Sewald");
				await shot(page, "06-gestor");
				if (!desk) {
					await page.locator(".member").last().scrollIntoViewIfNeeded();
					await shot(page, "06-gestor-rolada");
				}
				// D46: o nº 1 com score baixo; o herói vira a prospecção.
				await enter(page, "Anna Snelling");
				await shot(page, "11-heroi-acao", false);
				// Incremento 5: a primeira tela (D48) e a página inteira.
				await page.goto("/#como-funciona");
				await page.locator(".how details").first().waitFor();
				await shot(page, "09-como-funciona-tela", false);
				// A página inteira no celular escuro pesaria 430 kB a mais; a primeira tela basta.
				if (desk || scheme === "light")
					await shot(page, "09-como-funciona", true);
			});

			if (scheme === "light")
				test("entrada, lista completa, frios, vazio, data passada", async ({
					page,
				}) => {
					await page.goto("/#entrada");
					await shot(page, "01-entrada", false);
					await enter(page, "Zane Levy");
					await page.getByRole("button", { name: /Ver todos os/ }).click();
					await page.evaluate(() => scrollTo(0, 0));
					await shot(page, "04-vendedor-todos", true);
					await page
						.getByRole("tab", { name: /^(Atualize ou dê perda|Frios) \d/ })
						.click();
					await shot(page, "05-frios");
					await enter(page, "Cecily Lampkin");
					await shot(page, "07-vazio", false);
					await enter(page, "Zane Levy");
					if (desk)
						await page
							.getByRole("group", { name: "Data dos dados" })
							.getByRole("button", { name: "30/09" })
							.click();
					else
						await page
							.getByRole("combobox", { name: "Data dos dados" })
							.selectOption({ label: "30/09/2017" });
					await shot(page, "08-data-passada");
				});
		});
	}

// Vídeo dos movimentos: primeira abertura, troca de data (os cartões andam e depois o herói
// troca), painel; no celular, a folha fechando ao arrastar.
for (const width of [1280, 390])
	test(`vídeo ${width}`, async ({ browser }) => {
		const desk = width > 600;
		const size = { width, height: desk ? 800 : 844 };
		const ctx = await browser.newContext({
			viewport: size,
			reducedMotion: "no-preference",
			recordVideo: { dir: `${DIR}/video-tmp`, size },
		});
		const page = await ctx.newPage();
		await page.goto("/#entrada");
		await page
			.getByRole("button", { name: /^\S+ Zane Levy/ })
			.first()
			.click();
		await page.waitForTimeout(1500);
		const pick = async (label: string, full: string) =>
			desk
				? page
						.getByRole("group", { name: "Data dos dados" })
						.getByRole("button", { name: label })
						.click()
				: page
						.getByRole("combobox", { name: "Data dos dados" })
						.selectOption({ label: full });
		await pick("30/09", "30/09/2017");
		await page.waitForTimeout(1500);
		await pick("31/12/2017", "31/12/2017");
		await page.waitForTimeout(1500);
		await page.getByRole("button", { name: "Ver o motivo" }).click();
		await page.waitForTimeout(1300);
		if (desk) {
			await page.locator(".mini").nth(1).click();
			await page.waitForTimeout(1000);
			await page.keyboard.press("Escape");
		} else {
			const grip = await page.locator(".panel-grip").boundingBox();
			if (grip) {
				await page.mouse.move(grip.x + 60, grip.y + 20);
				await page.mouse.down();
				await page.mouse.move(grip.x + 60, grip.y + 300, { steps: 12 });
				await page.mouse.up();
			}
		}
		await page.waitForTimeout(900);
		const video = page.video();
		await ctx.close();
		await video?.saveAs(`${DIR}/10-movimentos-${width}.webm`);
		await video?.delete();
	});

test.afterAll(() => {
	rmSync(`${DIR}/video-tmp`, { recursive: true, force: true });
	for (const f of readdirSync(DIR).filter((f) => f.endsWith(".png"))) {
		const png = `${DIR}/${f}`;
		try {
			execFileSync("cwebp", [
				"-quiet",
				"-q",
				"82",
				png,
				"-o",
				png.replace(/\.png$/, ".webp"),
			]);
			unlinkSync(png);
		} catch {
			// sem cwebp, o PNG fica
		}
	}
	for (const f of readdirSync(DIR).filter((f) => f.endsWith(".webm"))) {
		const src = `${DIR}/${f}`;
		try {
			execFileSync("ffmpeg", [
				"-v",
				"error",
				"-y",
				"-i",
				src,
				"-c:v",
				"libvpx-vp9",
				"-crf",
				"42",
				"-b:v",
				"0",
				"-row-mt",
				"1",
				"-an",
				`${src}.vp9.webm`,
			]);
			renameSync(`${src}.vp9.webm`, src);
		} catch {
			// sem ffmpeg, o vídeo fica como o Playwright gravou
		}
	}
});

// Ícone para iPhone e imagem de prévia de link (Open Graph), em public/: refeitos com o app.
test.describe("ícone e prévia de link", () => {
	test.use({ colorScheme: "light", deviceScaleFactor: 1 });
	test("apple-touch-icon e og.jpg", async ({ page }) => {
		await page.setViewportSize({ width: 180, height: 180 });
		await page.goto("/favicon.svg");
		await page.screenshot({ path: "public/apple-touch-icon.png" });
		await page.setViewportSize({ width: 1200, height: 630 });
		await enter(page, "Zane Levy");
		await page.locator(".hero").waitFor();
		await page.waitForTimeout(900);
		await page.screenshot({ path: "public/og.jpg", type: "jpeg", quality: 85 });
	});
});
