import type { Metadata } from "next";
import Link from "next/link";
import { home } from "@/content/site";
import { featuredCases } from "@/lib/content";
import { Arrow, Check } from "@/components/icons";
import { OrderFlow } from "@/components/order-flow";
import { CaseCard } from "@/components/case-card";
import { SectionHeading } from "@/components/section-heading";

export const metadata: Metadata = { alternates: { canonical: "/" } };

export default function HomePage() {
  return <>
    <section className="hero"><div className="hero-grid" aria-hidden="true" /><div className="container hero-inner"><div className="hero-copy"><p className="eyebrow light"><span className="status-dot" />{home.eyebrow}</p><h1>{home.title[0]}<br /><span>{home.title[1]}</span></h1><p className="hero-description">{home.description}</p><div className="actions"><Link className="button button-accent" href="/cases/">查看项目案例 <Arrow diagonal /></Link><Link className="button button-ghost" href="/capabilities/">了解服务能力 <Arrow /></Link></div><ul className="hero-values">{home.promises.map((promise) => <li key={promise}><Check />{promise}</li>)}</ul></div><OrderFlow /></div></section>
    <section className="section container"><SectionHeading label="01 / BUSINESS VALUE" title="从这些每天都在发生的问题开始。"><p>将数据、权限、业务规则与人的判断连接起来，让 AI 在实际工作中发挥作用。</p></SectionHeading><div className="outcome-list">{home.outcomes.map((item) => <article className="outcome-row" key={item.id}><span className="outcome-number mono">{item.id}</span><div className="outcome-title"><p className="eyebrow">{item.label}</p><h3>{item.title}</h3></div><div className="outcome-description"><p>{item.problem}</p><p className="outcome-change">{item.change}</p><Link className="text-link" href={`/cases/${item.caseSlug}/`}>{item.caseLabel}<Arrow diagonal /></Link></div></article>)}</div></section>
    <section className="section section-muted"><div className="container"><SectionHeading label="02 / PROJECT EXPERIENCE" title="通过具体项目，理解我们能做什么。"><Link className="text-link" href="/cases/">浏览全部 11 个案例 <Arrow /></Link></SectionHeading><div className="case-grid">{featuredCases.map((item) => <CaseCard item={item} key={item.id} />)}</div></div></section>
    <section className="section container"><SectionHeading label="03 / DELIVERY" title="从业务问题到日常使用，持续参与交付。"><Link className="text-link" href="/capabilities/">查看完整服务能力 <Arrow /></Link></SectionHeading><div className="delivery-grid">{home.delivery.map((step, index) => <article key={step.title}><span className="mono step-number">0{index + 1}</span><h3>{step.title}</h3><p>{step.text}</p><div className="delivery-output">{step.output}</div></article>)}</div></section>
    <section className="container"><div className="cooperation-cta"><div><p className="eyebrow light">WORK TOGETHER</p><h2>你有产品、客户或业务场景，<br />我们一起把交付路径理清楚。</h2><p>面向 AI 平台、企业软件、行业方案与系统集成伙伴，按项目明确工作范围和各方职责。</p></div><Link className="button button-accent" href="/cooperation/">了解合作方式 <Arrow diagonal /></Link></div></section>
  </>;
}
