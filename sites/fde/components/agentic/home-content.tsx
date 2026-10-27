import Link from "next/link";
import { home, cooperation } from "@/content/site";
import { featuredCases } from "@/lib/content";
import { CaseCard } from "@/components/case-card";
import { PixelIcon } from "./pixel-icon";
import { RevealText } from "./reveal-text";
import { BentoCard } from "./bento-card";
import { StackingAgentCards } from "./stacking-agent-cards";

function Heading({ icon, label, title, children }: { icon: "platform" | "agents" | "workflow" | "integrations" | "pricing"; label: string; title: string; children?: React.ReactNode }) {
  return <div className="ag-section-heading"><div><PixelIcon type={icon} size={40} /><span className="ag-tag">{label}</span><RevealText className="ag-heading">{title}</RevealText></div>{children && <div className="ag-heading-aside">{children}</div>}</div>;
}

export function AgenticHomeContent() {
  return <>
    <section className="ag-section ag-container" id="business-value"><Heading icon="platform" label="业务价值" title={"不止于一次对话，\n让 AI 进入真实业务。"}><p>为企业与生态伙伴提供<br />场景工程及交付支持。</p></Heading>
      <BentoCard className="ag-arc-card"><img src="/agentic/arc.png" alt="" loading="lazy" /><div className="ag-arc-mask" /><div className="ag-arc-content"><PixelIcon type="platform" size={32} /><h3>把分散的能力，连接成可运行的链路。</h3><p>{home.description}</p><Link className="ag-case-link" href="/capabilities/">了解我们的服务能力 <span aria-hidden="true">↗</span></Link></div></BentoCard>
      <div className="ag-promise-grid">{home.delivery.map((item, i) => <BentoCard key={item.title} delay={i * 80}><PixelIcon type={(["workflow", "integrations", "agents"] as const)[i]} size={32} /><h3>{item.title}</h3><p>{item.text}</p><span className="ag-output">{item.output}</span></BentoCard>)}</div>
    </section>
    <section className="ag-section ag-rule"><div className="ag-container"><Heading icon="agents" label="业务场景" title={"技术的价值，\n体现在工作的变化里。"}><p>从具体问题出发，把 AI 放进真实业务链路。<br />四类业务场景，各有具体解法。</p></Heading><StackingAgentCards /></div></section>
    <section className="ag-section ag-rule"><div className="ag-container"><Heading icon="workflow" label="协作流程" title={"从目标场景，\n到持续使用。"}><Link className="ag-case-link" href="/capabilities/">查看七项服务能力 <span aria-hidden="true">↗</span></Link></Heading><div className="ag-workflow-grid">{cooperation.steps.map((step, i) => <BentoCard key={step.title} className="ag-step-card" delay={i * 80}><img src={`/agentic/${["define", "compose", "test", "deploy"][i]}.png`} alt="" loading="lazy" /><div className="ag-step-copy"><span className="ag-step-number">0{i + 1}</span><h3>{step.title}</h3><p>{step.text}</p></div></BentoCard>)}</div></div></section>
    <section className="ag-section ag-rule"><div className="ag-container"><Heading icon="integrations" label="项目实践" title={"从真实问题，\n走向具体解法。"}><Link className="ag-case-link" href="/cases/">浏览全部 11 个案例 <span aria-hidden="true">↗</span></Link></Heading><div className="case-grid">{featuredCases.map(item => <BentoCard key={item.id}><CaseCard item={item} /></BentoCard>)}</div><p className="ag-project-note">案例按项目场景呈现，客户身份已匿名；不同案例可能来自同一客户。</p></div></section>
    <section className="ag-section ag-rule"><div className="ag-container"><Heading icon="pricing" label="合作方式" title={"你带来业务场景，\n我们一起向前。"}><p>与你的产品、客户与团队协同，<br />明确分工，分阶段实施。</p></Heading><div className="ag-cooperation-grid">{cooperation.models.map((model, i) => <BentoCard key={model.title} className={`ag-cooperation-card ${i === 1 ? "ag-featured" : ""}`} delay={i * 90}><span className="ag-tag">协作模式 / 0{i + 1}</span><h3>{model.title}</h3><p className="ag-model-fit">{model.fit}</p><p>{model.text}</p><Link className="ag-button" href="/cooperation/">了解合作细节 <span aria-hidden="true">↗</span></Link></BentoCard>)}</div></div></section>
  </>;
}
