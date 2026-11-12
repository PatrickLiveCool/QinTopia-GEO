"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { site } from "@/content/site";
import { useMotion } from "./motion-context";

export function AgenticNav() {
  const [open, setOpen] = useState(false);
  const pathname = usePathname();
  const { enabled, toggle } = useMotion();
  return <header className="ag-nav-wrap"><nav className="ag-nav" aria-label="主导航">
    <Link className="ag-wordmark" href="/" onClick={() => setOpen(false)} aria-label={`${site.name}首页`}>QINTOPIA<span>智能体工坊</span></Link>
    <div className="ag-nav-links">{site.navigation.map(link => <Link key={link.href} href={link.href} aria-current={(link.href === "/" ? pathname === "/" : pathname.startsWith(link.href)) ? "page" : undefined}>{link.label}</Link>)}</div>
    <div className="ag-nav-actions"><button type="button" className="ag-motion-button" onClick={toggle} aria-label={enabled ? "暂停动效" : "启用动效"} title={enabled ? "暂停动效" : "启用动效"}><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">{enabled ? <><rect x="3" y="2" width="2" height="8" fill="currentColor" /><rect x="7" y="2" width="2" height="8" fill="currentColor" /></> : <path d="M3 2L10 6L3 10Z" fill="currentColor" />}</svg></button><Link className="ag-contact" href="/cooperation/">一起协作 ↗</Link><button className="ag-menu-button" aria-expanded={open} aria-controls="mobile-navigation" onClick={() => setOpen(!open)}>{open ? "关闭" : "菜单"}</button></div>
  </nav>{open && <nav className="ag-mobile-nav" id="mobile-navigation" aria-label="移动导航">{site.navigation.map(link => <Link key={link.href} href={link.href} onClick={() => setOpen(false)}>{link.label}<span aria-hidden="true">↗</span></Link>)}</nav>}</header>;
}
