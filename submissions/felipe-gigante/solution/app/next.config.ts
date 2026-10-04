import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // O SQLite gerado no build (npm run seed) precisa ir junto para as funções serverless da Vercel.
  outputFileTracingIncludes: {
    "/**": ["./data/app.db"],
  },
};

export default nextConfig;
