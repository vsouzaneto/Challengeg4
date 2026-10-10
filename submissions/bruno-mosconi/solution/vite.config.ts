import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Os CSVs (cerca de 650 kB) vão dentro do bundle de propósito: sem chamada de rede (CA9).
export default defineConfig({
	plugins: [react()],
	build: { chunkSizeWarningLimit: 1000 },
});
