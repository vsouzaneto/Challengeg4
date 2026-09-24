import { createServer } from "node:http";
import { handleRequest } from "./application.js";
import { config } from "./config.js";
import { pool } from "./database/pool.js";

const server = createServer((request, response) => {
  void handleRequest(request, response);
});

server.listen(config.port, "0.0.0.0", () => {
  console.log(`API running on :${config.port}`);
});

async function shutdown(): Promise<void> {
  server.close();
  await pool.end();
}

process.on("SIGINT", () => {
  void shutdown();
});

process.on("SIGTERM", () => {
  void shutdown();
});
