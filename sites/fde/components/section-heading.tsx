import type { ReactNode } from "react";
import { PixelIcon } from "@/components/agentic/pixel-icon";
import { RevealText } from "@/components/agentic/reveal-text";

export function SectionHeading({ label, title, children }: { label: string; title: string; children?: ReactNode }) {
  return <div className="section-heading"><div><div className="template-only"><PixelIcon type="workflow" size={40} /></div><p className="eyebrow">{label}</p><h2 className="legacy-only">{title}</h2><div className="template-only"><RevealText className="ag-heading">{title}</RevealText></div></div>{children && <div className="section-heading-aside">{children}</div>}</div>;
}

export function PageIntro({ label, title, children }: { label: string; title: string; children: ReactNode }) {
  return <header className="page-intro container"><div className="template-only ag-intro-art"><img src={`/agentic/${label.startsWith("CAPABILITIES") ? "compose" : label.startsWith("PROJECTS") ? "researcher" : "deploy"}.png`} alt="" /></div><div className="template-only"><PixelIcon type={label.startsWith("CAPABILITIES") ? "platform" : label.startsWith("PROJECTS") ? "agents" : "integrations"} size={40} /></div><p className="eyebrow">{label}</p><h1 className="legacy-only">{title}</h1><div className="template-only"><RevealText as="h1" className="ag-heading">{title}</RevealText></div><p className="lede">{children}</p></header>;
}
