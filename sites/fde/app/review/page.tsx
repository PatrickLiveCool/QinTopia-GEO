import type { Metadata } from "next";
import Link from "next/link";
import { ReviewHomeContent } from "@/components/agentic/review-home-content";
import "./review.css";

export const metadata: Metadata = { title: "业务应用 · 中文调整版", alternates: { canonical: "/review/" } };
export default function ReviewPage() {
  return <><section className="rv-hero"><div className="rv-art" aria-hidden="true"><img src="/agentic/arc.png" alt="" /></div><div className="rv-hero-inner"><p className="rv-kicker">秦托邦智能体工坊</p><h1>减少重复整理，<br />让业务衔接更顺畅。</h1><p className="rv-description">把聊天里的订单、分散的资料与已有业务系统连接起来。<br className="rv-desktop-break" />让 AI 协助整理与处理，让团队专注审核、异常和关键决策。</p><div className="rv-actions"><Link className="rv-primary" href="#review-scenarios">看看能解决哪些问题 <span aria-hidden="true">↓</span></Link><Link href="/cases/">查看项目案例 ↗</Link></div><p className="rv-footnote">从一个具体场景开始 · 样本验证 · 分阶段实施</p></div></section>
  <section className="rv-scenarios ag-container" id="review-scenarios" aria-labelledby="rv-scenarios-title"><div className="rv-scenarios-heading"><h2 id="rv-scenarios-title">你正在为哪件事花时间？</h2><p>先看业务问题，再看技术怎样配合。</p></div><div className="rv-scenario-grid">{[
    {title:"订单反复抄，容易漏",text:"从群聊中识别订单，匹配商品并衔接业务系统，让员工集中处理异常。",href:"/cases/chat-order-workflow/",label:"看群聊收单案例"},
    {title:"资料分散，核对费时间",text:"整理物料与专业资料，统一匹配规则和访问权限，保留专业人员审核。",href:"/cases/material-data-governance/",label:"看物料治理案例"},
    {title:"多人交接，信息对不上",text:"围绕房态、订单与收退款统一业务信息，关键变更保留正式确认。",href:"/cases/hospitality-agent-collaboration/",label:"看经营协作案例"}
  ].map(item=><article key={item.href}><h3>{item.title}</h3><p>{item.text}</p><Link href={item.href}>{item.label} <span aria-hidden="true">↗</span></Link></article>)}</div></section><ReviewHomeContent /></>;
}
