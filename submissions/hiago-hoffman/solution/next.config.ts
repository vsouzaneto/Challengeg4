import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Fixa a raiz do projeto (evita o Next inferir outro lockfile acima desta pasta).
  turbopack: { root: __dirname },
};

export default nextConfig;
