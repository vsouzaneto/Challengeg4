import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // As rotas leem data/*.json via fs em tempo de execução; garante que entrem no bundle de deploy.
  outputFileTracingIncludes: {
    "/api/**": ["./data/**"],
  },
};

export default nextConfig;
