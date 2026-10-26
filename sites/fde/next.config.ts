import type { NextConfig } from "next";

const config: NextConfig = {
  // Full Next.js runtime by default; retain an explicit COS-compatible export.
  output: process.env.FDE_OUTPUT === "static" ? "export" : undefined,
  trailingSlash: true,
  images: { unoptimized: true },
};

export default config;
