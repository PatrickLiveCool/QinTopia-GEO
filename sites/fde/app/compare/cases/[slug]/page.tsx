import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/site-link";
import { notFound } from "next/navigation";
import { cases, getCase } from "@/lib/content";
import { InlineText } from "@/components/inline-text";
import { Arrow } from "@/components/icons";
import { CaseCard } from "@/components/case-card";
import { site } from "@/content/site";

export const dynamicParams = false;
export function generateStaticParams() { return cases.map(({ slug }) => ({ slug })); }

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const item = getCase(slug);
  if (!item) return {};
  return { title: item.title, description: `${item.client}：${item.outcome}。`, alternates: { canonical: `/cases/${slug}/` }, openGraph: { title: item.title, description: item.outcome, siteName: site.name, locale: "zh_CN", type: "article", url: `/cases/${slug}/`, images: [{ url: "/social-card.png", width: 1200, height: 630, alt: site.name }] } };
}

export default async function CaseDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const item = getCase(slug);
  if (!item) notFound();
  const related = cases.filter((candidate) => candidate.id !== item.id && candidate.themes.some((theme) => item.themes.includes(theme))).slice(0, 2);
  return <><header className="container case-detail-header"><Link className="text-link" href="/cases/">← 返回项目案例</Link><p className="eyebrow">CASE {item.id} / {item.industry}</p><h1>{item.title}</h1><p className="case-client">{item.client}</p><p className="case-detail-outcome">{item.outcome}</p><div className="tags">{item.themes.map((theme) => <span key={theme}>{theme}</span>)}</div></header><div className="container case-detail-layout"><aside className="case-toc"><p className="eyebrow">本篇内容</p><nav aria-label="案例内容目录">{item.sections.map((section, index) => <a key={section.title} href={`#section-${index + 1}`}><span className="mono">0{index + 1}</span>{section.title}</a>)}</nav></aside><article className="case-body">{item.sections.map((section, index) => <section id={`section-${index + 1}`} key={section.title}><p className="eyebrow">0{index + 1}</p><h2>{section.title}</h2>{section.blocks.map((block, blockIndex) => block.type === "list" ? <ul key={blockIndex}>{block.items.map((text, line) => <li key={line}><InlineText>{text}</InlineText></li>)}</ul> : <p key={blockIndex}><InlineText>{block.items.join("\n")}</InlineText></p>)}</section>)}</article></div>{related.length > 0 && <section className="container section"><div className="section-heading"><h2>相关项目</h2><Link href="/cases/" className="text-link">查看全部案例<Arrow /></Link></div><div className="case-grid">{related.map((candidate) => <CaseCard item={candidate} key={candidate.id} />)}</div></section>}</>;
}
