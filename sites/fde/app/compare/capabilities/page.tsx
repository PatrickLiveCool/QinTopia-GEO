import type { Metadata } from "next";
import { SiteLink as Link } from "@/components/site-link";
import { capabilities } from "@/content/site";
import { getCase } from "@/lib/content";
import { PageIntro } from "@/components/section-heading";
import { Arrow } from "@/components/icons";

export const metadata: Metadata = { title: "服务能力", description: "业务调研、系统对接、场景搭建、Demo 验证、培训、交付陪跑与复盘：了解秦托邦可以承担的工作、典型产出和协作条件。", alternates: { canonical: "/capabilities/" } };

export default function CapabilitiesPage() {
  return <><PageIntro label="CAPABILITIES / 服务能力" title="把要做的工作、交付的结果讲清楚。">从业务梳理到上线使用，七个服务模块可以按项目组合。我们与伙伴及客户团队共同确认工作范围、接口条件和验收方式。</PageIntro><div className="container capability-layout"><nav className="capability-nav" aria-label="服务能力目录">{capabilities.map((item, index) => <a key={item.id} href={`#${item.id}`}><span className="mono">0{index + 1}</span>{item.title}</a>)}</nav><div>{capabilities.map((item, index) => <section id={item.id} key={item.id} className="capability-section"><p className="eyebrow">SERVICE / 0{index + 1}</p><h2>{item.title}</h2><h3>{item.value}</h3><p className="capability-description">{item.description}</p><div className="capability-columns"><div><h4>我们承担的工作</h4><ul>{item.work.map((text) => <li key={text}>{text}</li>)}</ul></div><div><h4>你将获得的产出</h4><ul>{item.outputs.map((text) => <li key={text}>{text}</li>)}</ul></div></div><p className="conditions"><strong>协作条件</strong>{item.conditions}</p>{item.related.length > 0 && <div className="related-links"><span>相关项目实践</span>{item.related.map((slug) => <Link className="text-link" key={slug} href={`/cases/${slug}/`}>{getCase(slug)?.title}<Arrow diagonal /></Link>)}</div>}</section>)}</div></div><section className="container"><div className="cooperation-cta compact"><div><h2>从明确的工作范围开始合作。</h2><p>共同确认各方职责、客户配合条件与阶段产出。</p></div><Link className="button button-accent" href="/cooperation/">了解合作方式 <Arrow /></Link></div></section></>;
}
