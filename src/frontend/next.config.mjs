/** @type {import('next').NextConfig} */
const backendOrigin = process.env.BACKEND_URL ?? "http://127.0.0.1:5000"

const nextConfig = {
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
  async rewrites() {
    return [
      { source: "/health", destination: `${backendOrigin}/health` },
      { source: "/api/:path*", destination: `${backendOrigin}/api/:path*` },
    ]
  },
}

export default nextConfig
