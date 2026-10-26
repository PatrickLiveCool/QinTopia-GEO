import type { Metadata } from "next";
import Link from "next/link";
import { home } from "@/content/site";
import { featuredCases } from "@/lib/content";
import { Arrow } from "@/components/icons";
import { BusinessScenarios } from "@/components/business-scenarios";
import { CaseCard } from "@/components/case-card";
import { SectionHeading } from "@/components/section-heading";

export const metadata: Metadata = { alternates: { canonical: "/" } };

export default function HomePage() {
  return <>
    <section className="hero"><div className="hero-art" aria-hidden="true"><img src="/images/iridescent-workflow.png" alt="" fetchPriority="high" width={1536} height={1024} /></div><div className="container hero-inner"><div className="hero-copy"><p className="eyebrow"><span className="status-dot" />{home.eyebrow}</p><h1>{home.title[0]}<br /><span>{home.title[1]}</span></h1><p className="hero-description">把分散的信息、已有的系统与 AI 能力连接起来。<br className="desktop-break" />让重复工作进入流程，让关键判断留给人。</p><div className="actions"><Link className="button button-primary" href="/cases/">探索项目案例 <Arrow diagonal /></Link><Link className="button button-text" href="/cooperation/">与我们协作 <Arrow /></Link></div></div></div><div className="container hero-baseline"><span>为企业与生态伙伴提供场景工程及交付支持</span><a href="#business-value">从实际工作开始 <span aria-hidden="true">↓</span></a></div></section>
    <div className="partner-strip"><div className="container"><p>与不同生态，共同交付</p><ul><li>AI 平台</li><li>企业软件</li><li>行业解决方案</li><li>系统集成伙伴</li></ul></div></div>
    <section className="section container" id="business-value"><SectionHeading label="01 / 业务价值" title="技术的价值，体现在工作的变化里。"><p>不止于一次对话或一个演示。<br />从具体问题出发，把 AI 放进真实业务链路。</p></SectionHeading><BusinessScenarios /></section>
    <section className="section selected-projects"><div className="container"><SectionHeading label="02 / 项目实践" title="从真实问题，走向具体解法。"><Link className="text-link" href="/cases/">浏览全部 11 个案例 <Arrow /></Link></SectionHeading><div className="case-grid">{featuredCases.map((item) => <CaseCard item={item} key={item.id} />)}</div><p className="project-note">案例按项目场景呈现，客户身份已匿名；不同案例可能来自同一客户。</p></div></section>
    <section className="section container"><SectionHeading label="03 / 服务能力" title="从第一步梳理，到日常用起来。"><p>七项服务能力，按项目需要组合。<br />从业务、技术到团队协作，补齐交付中的关键一段。</p></SectionHeading><div className="delivery-grid">{home.delivery.map((step, index) => <article key={step.title}><span className="mono step-number">0{index + 1}</span><h3>{step.title}</h3><p>{step.text}</p><div className="delivery-output">{step.output}</div></article>)}</div><div className="section-end"><Link className="text-link" href="/capabilities/">了解七项服务能力与协作条件 <Arrow /></Link></div></section>
    <section className="container"><div className="cooperation-cta"><div><p className="eyebrow light">04 / 一起向前</p><h2>从你正在面对的<br />一个业务问题开始。</h2><p>你带来产品、客户或业务场景。我们一起明确可行范围、协作分工和下一步。</p></div><Link className="button button-accent" href="/cooperation/">了解合作方式 <Arrow diagonal /></Link></div></section>
  </>;
}
