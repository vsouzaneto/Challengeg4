// Prints e vídeos do protótipo da rodada 3, com o Playwright instalado em solution/.
// Uso: na pasta process-log/prototipos, `python3 -m http.server 8765` e depois
// `node rodada-3/capturar.mjs` (só prints) ou `node rodada-3/capturar.mjs video`.
// Para o repositório não pesar, os prints viram WebP (cwebp -q 82) e os vídeos são recomprimidos em VP9 (ffmpeg).
import { execFileSync } from "node:child_process";
import { readdirSync, unlinkSync } from "node:fs";
import { chromium } from "../../../solution/node_modules/playwright/index.mjs";

const BASE = "http://127.0.0.1:8765/rodada-3/index.html";
const OUT = new URL(".", import.meta.url).pathname;
const errors = [];

async function page(browser, { width, theme, motion = "reduce", video }) {
	const ctx = await browser.newContext({
		viewport: { width, height: width < 600 ? 844 : 860 },
		deviceScaleFactor: 2,
		colorScheme: theme === "escuro" ? "dark" : "light",
		reducedMotion: motion,
		...(video ? { recordVideo: { dir: `${OUT}videos/`, size: { width, height: width < 600 ? 844 : 800 } } } : {}),
	});
	const p = await ctx.newPage();
	p.on("console", (m) => m.type() === "error" && errors.push(m.text()));
	p.on("pageerror", (e) => errors.push(String(e)));
	return { ctx, p };
}

async function prints(browser) {
	for (const theme of ["claro", "escuro"]) {
		for (const width of [1280, 390]) {
			const { ctx, p } = await page(browser, { width, theme });
			// No celular, prints por tela: a página inteira arrasta a barra de abas fixa para o meio.
			const shot = (name, full = width > 600) => p.screenshot({ path: `${OUT}prints/${name}-${width}-${theme}.png`, fullPage: full });
			const below = async (name, sel) => {
				if (width > 600) return;
				await p.locator(sel).first().scrollIntoViewIfNeeded();
				await p.evaluate(() => scrollBy(0, 60));
				await p.waitForTimeout(300);
				await shot(`${name}-rolada`);
				await p.evaluate(() => scrollTo(0, 0));
			};
			await p.goto(`${BASE}?tema=${theme}#semana`);
			await p.waitForTimeout(400);
			await shot("vendedor");
			await below("vendedor", ".thermo-card");
			await p.click(".hero .pill.primary");
			await p.waitForTimeout(400);
			await shot("painel", false);
			await p.click("#close");
			await p.goto(`${BASE}?tema=${theme}#equipe`);
			await p.waitForTimeout(400);
			await shot("gestor");
			await below("gestor", ".member:last-child");
			if (theme === "claro") {
				await p.goto(`${BASE}?tema=${theme}#entrada`);
				await p.waitForTimeout(400);
				await shot("entrada");
				await p.goto(`${BASE}?tema=${theme}#como-funciona`);
				await p.waitForTimeout(400);
				await shot("como-funciona");
				await p.goto(`${BASE}?tema=${theme}#semana`);
				await p.click('[data-tab="prospeccao"]');
				await p.waitForTimeout(300);
				await shot("vazio");
				await p.click('[data-tab="prioridades"]');
				await p.click("#all");
				await p.evaluate(() => scrollTo(0, 0));
				await p.waitForTimeout(300);
				await shot("vendedor-todos");
			}
			await ctx.close();
		}
	}
	// Fonte de quem não usa aparelho Apple
	const { ctx, p } = await page(browser, { width: 1280, theme: "claro" });
	await p.goto(`${BASE}?fonte=onest#semana`);
	await p.waitForTimeout(400);
	await p.screenshot({ path: `${OUT}prints/vendedor-1280-claro-onest.png` });
	await ctx.close();
}

async function video(browser) {
	for (const width of [1280, 390]) {
		const { ctx, p } = await page(browser, { width, theme: "claro", motion: "no-preference", video: true });
		await p.goto(`${BASE}?abertura=1#semana`);
		await p.waitForTimeout(1600);
		// troca de data: volta para 30/09 e avança para 31/12 (os pontos andam para a direita)
		if (width > 600) {
			await p.click('[data-date="2017-09-30"]');
			await p.waitForTimeout(1400);
			await p.click('[data-date="2017-12-31"]');
		} else {
			await p.selectOption("#date-select", "2017-09-30");
			await p.waitForTimeout(1400);
			await p.selectOption("#date-select", "2017-12-31");
		}
		await p.waitForTimeout(1400);
		await p.hover(".hero");
		await p.waitForTimeout(500);
		await p.click(".hero .pill.primary");
		await p.waitForTimeout(1600);
		await p.click("#close");
		await p.waitForTimeout(900);
		if (width > 600) {
			await p.hover(".next .mini:nth-child(2)");
			await p.waitForTimeout(500);
			await p.click(".next .mini:nth-child(2)");
			await p.waitForTimeout(1200);
			await p.click(".next .mini:nth-child(3)");
			await p.waitForTimeout(1200);
			await p.keyboard.press("Escape");
			await p.waitForTimeout(600);
			await p.click('.areas [data-area="equipe"]');
			await p.waitForTimeout(1000);
			await p.click(".member:nth-child(3)");
			await p.waitForTimeout(1200);
		}
		const v = p.video();
		await ctx.close();
		await v.saveAs(`${OUT}videos/movimentos-${width}.webm`);
		await v.delete();
	}
}

function shrink() {
	for (const f of readdirSync(`${OUT}prints`).filter((f) => f.endsWith(".png"))) {
		const png = `${OUT}prints/${f}`;
		execFileSync("cwebp", ["-quiet", "-q", "82", png, "-o", png.replace(/\.png$/, ".webp")]);
		unlinkSync(png);
	}
	for (const f of readdirSync(`${OUT}videos`).filter((f) => f.endsWith(".webm") && !f.startsWith("vp9-"))) {
		const src = `${OUT}videos/${f}`;
		const tmp = `${OUT}videos/vp9-${f}`;
		execFileSync("ffmpeg", ["-v", "error", "-y", "-i", src, "-c:v", "libvpx-vp9", "-crf", "42", "-b:v", "0", "-row-mt", "1", "-an", tmp]);
		execFileSync("mv", [tmp, src]);
	}
}

const browser = await chromium.launch();
if (process.argv[2] === "video") await video(browser);
else if (process.argv[2] !== "comprimir") await prints(browser);
await browser.close();
shrink();
if (errors.length) {
	console.error("Erros no console:\n" + errors.join("\n"));
	process.exit(1);
}
console.log("ok");
