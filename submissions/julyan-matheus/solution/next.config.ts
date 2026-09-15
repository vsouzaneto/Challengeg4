import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // CSVs are read with fs at build time; keep them in the server bundle just in case.
  outputFileTracingIncludes: { "/**": ["./data/**"] },
};

export default nextConfig;
