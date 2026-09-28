import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Fixa a raiz do projeto (evita o Next inferir outro lockfile acima desta pasta).
  turbopack: { root: __dirname },
  // upload da base do CRM (4 CSVs) via Server Action
  experimental: { serverActions: { bodySizeLimit: "50mb" } },
};

export default nextConfig;
