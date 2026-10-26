import Link from "next/link";
import type { CaseStudy } from "@/lib/content";
import { Arrow } from "@/components/icons";

export function CaseCard({ item }: { item: CaseStudy }) {
  return (
    <article className="case-card">
      <div className="case-top"><span className="mono">CASE / {item.id}</span><span>{item.client}</span></div>
      <h3><Link href={`/cases/${item.slug}/`}>{item.title}<Arrow diagonal /></Link></h3>
      <div className="case-copy"><p><span>业务问题</span>{item.problem}</p><p className="case-outcome"><span>带来的变化</span>{item.outcome}</p></div>
      <div className="tags">{item.themes.map((theme) => <span key={theme}>{theme}</span>)}</div>
    </article>
  );
}
