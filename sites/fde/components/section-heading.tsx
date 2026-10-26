import type { ReactNode } from "react";

export function SectionHeading({ label, title, children }: { label: string; title: string; children?: ReactNode }) {
  return <div className="section-heading"><div><p className="eyebrow">{label}</p><h2>{title}</h2></div>{children && <div className="section-heading-aside">{children}</div>}</div>;
}

export function PageIntro({ label, title, children }: { label: string; title: string; children: ReactNode }) {
  return <header className="page-intro container"><p className="eyebrow">{label}</p><h1>{title}</h1><p className="lede">{children}</p></header>;
}
