"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import type { ReactNode } from "react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { PageMotion } from "@/components/page-motion";
import { AgenticNav } from "@/components/agentic/navigation";
import { AgenticFooter } from "@/components/agentic/footer";
import { MotionProvider } from "@/components/agentic/motion-context";

export function SiteShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  if (pathname.startsWith("/compare")) return <div className="comparison-shell"><SiteHeader /><main id="main-content">{children}</main><SiteFooter /><PageMotion /><Link className="version-switch" href={pathname.replace(/^\/compare/, "") || "/"}>旧版对比 · 查看新版 ↗</Link></div>;
  return <MotionProvider><AgenticNav /><main id="main-content">{children}</main><AgenticFooter /><Link className="version-switch" href={`/compare${/^\/(?:capabilities|cases|cooperation)(?:\/|$)/.test(pathname) ? pathname : "/"}`}>模板新版 · 对比旧版 ↗</Link></MotionProvider>;
}
