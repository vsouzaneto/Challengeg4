import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import type { ProxyOptions } from "vite";

export function simulateNetworkError(
  _timeout: number,
): ProxyOptions["configure"] {
  return (proxy, _options) => {
    proxy.on("proxyReq", (proxyReq, _req, res) => {
      setTimeout(() => {
        // Destroy the socket connection to the browser
        res.socket?.destroy(new Error("simulated network error"));

        // Also clean up the backend connection
        proxyReq.socket?.destroy();
      }, 2000);
    });
  };
}

const proxyTarget = process.env.BACKEND_URL || "http://localhost:3001";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@chat-template/core/lab-rooms": path.resolve(
        __dirname,
        "../packages/core/src/lab-rooms.ts",
      ),
    },
  },
  server: {
    headers: {
      "Cache-Control": "no-store",
      "Content-Security-Policy":
        "frame-ancestors 'self' http://localhost:3020 http://127.0.0.1:3020",
    },
    cors: {
      origin: ["http://localhost:3020", "http://127.0.0.1:3020"],
    },
    port: process.env.PORT ? Number.parseInt(process.env.PORT) : 3000,
    proxy: {
      "/api/chat": {
        target: proxyTarget,
        changeOrigin: true,
        // Uncomment this to test situations where the stream will time out.
        // configure: simulateNetworkError(2000),
      },
      "/api": {
        target: process.env.BACKEND_URL || "http://localhost:3001",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: false,
  },
});
