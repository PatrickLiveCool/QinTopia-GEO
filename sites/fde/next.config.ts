import type { NextConfig } from "next";

const config: NextConfig = {
  // Full Next.js runtime by default; retain an explicit COS-compatible export.
  output: process.env.FDE_OUTPUT === "static" ? "export" : undefined,
  trailingSlash: true,
  images: { unoptimized: true },
  ...(process.env.FDE_OUTPUT !== "static" ? {
    async headers() {
      return [{ source: "/:path*", headers: [
        { key: "X-Content-Type-Options", value: "nosniff" },
        { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        { key: "Strict-Transport-Security", value: "max-age=63072000" },
        { key: "X-Robots-Tag", value: "noindex, nofollow" },
      ] }];
    },
  } : {}),
};

export default config;
