import { defineConfig } from "@playwright/test";

// Roda contra o build de produção, como o avaliador veria. Com BASE_URL, roda contra o site
// publicado (ex.: BASE_URL=https://… npm run personas), sem subir servidor local.
const external = process.env.BASE_URL;

export default defineConfig({
	testDir: "e2e",
	testMatch: /.*\.pw\.ts/,
	// Sem movimento nos testes: a primeira abertura e as transições não atrapalham as leituras.
	use: {
		baseURL: external ?? "http://localhost:4173",
		locale: "pt-BR",
		reducedMotion: "reduce",
	},
	webServer: external
		? undefined
		: {
				command: "npm run build && npm run preview -- --port 4173 --strictPort",
				url: "http://localhost:4173",
				reuseExistingServer: false,
			},
});
