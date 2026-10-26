"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { site } from "@/content/site";
import { Arrow } from "@/components/icons";

export function SiteHeader() {
  const pathname = usePathname();
  return (
    <header className="site-header">
      <div className="container header-inner">
        <Link className="brand" href="/" aria-label={`${site.name}首页`}>
          <span>{site.name}</span>
          <span className="brand-caption">AI ENGINEERING & DELIVERY</span>
        </Link>
        <nav aria-label="主导航">
          {site.navigation.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href.replace(/\/$/, ""));
            return <Link key={item.href} href={item.href} aria-current={active ? "page" : undefined}>{item.label}</Link>;
          })}
        </nav>
        <Link className="header-cta" href="/cooperation/">了解合作 <Arrow diagonal /></Link>
      </div>
    </header>
  );
}
