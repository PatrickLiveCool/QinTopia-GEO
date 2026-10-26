import type { Metadata, Viewport } from "next";
import "@fontsource-variable/noto-sans-sc";

export const viewport: Viewport = { themeColor: "#f5f4f0" };
import { site } from "@/content/site";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { PageMotion } from "@/components/page-motion";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(site.domain),
  title: { default: `${site.name}｜AI 应用工程与生态协同交付`, template: `%s｜${site.name}` },
  description: site.description,
  robots: { index: false, follow: false },
  openGraph: { siteName: site.name, locale: "zh_CN", type: "website", images: [{ url: "/social-card.png", width: 1200, height: 630, alt: "秦托邦智能体工坊：AI 应用工程与生态协同交付" }] },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-CN"><body><a className="skip-link" href="#main-content">跳到正文</a><SiteHeader /><main id="main-content">{children}</main><SiteFooter /><PageMotion /></body></html>;
}
