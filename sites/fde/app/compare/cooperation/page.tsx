import type { Metadata } from "next";
import { cooperation } from "@/content/site";
import { PageIntro, SectionHeading } from "@/components/section-heading";
import { CopyBrief } from "@/components/copy-brief";

export const metadata: Metadata = { title: "合作方式", description: "通过模块委托、联合项目交付或阶段陪跑开展合作，明确平台方、秦托邦与客户团队的职责。", alternates: { canonical: "/cooperation/" } };

export default function CooperationPage() {
  return <><PageIntro label="COOPERATION / 合作方式" title="让各方的专业能力，在项目里形成合力。">面向 AI 平台、企业软件、行业解决方案和系统集成伙伴，从一个具体场景出发，明确工作范围、实施条件与各方职责。</PageIntro><section className="container section-bottom"><div className="cooperation-models">{cooperation.models.map((model, index) => <article key={model.title}><p className="eyebrow">MODEL / 0{index + 1}</p><h2>{model.title}</h2><p className="model-fit">{model.fit}</p><p>{model.text}</p></article>)}</div></section><section className="section section-muted"><div className="container"><SectionHeading label="RESPONSIBILITIES" title="把各方职责放在同一张图上。"><p>以下是典型分工，具体范围根据项目共同约定。</p></SectionHeading><div className="role-grid">{cooperation.roles.map((role) => <article key={role.who}><p className="eyebrow">{role.role}</p><h3>{role.who}</h3><p>{role.details}</p></article>)}</div></div></section><section className="section container"><SectionHeading label="START A PROJECT" title="从第一次交流，到分阶段实施。" /><ol className="cooperation-steps">{cooperation.steps.map((step, index) => <li key={step.title}><span className="mono">0{index + 1}</span><h3>{step.title}</h3><p>{step.text}</p></li>)}</ol></section><section className="container section-bottom"><div className="brief-panel"><div><p className="eyebrow">PROJECT BRIEF</p><h2>先把这个问题讲清楚：<br />你希望哪一项工作发生变化？</h2><p>整理业务目标、现有系统和可提供的协作条件，让第一次沟通直接进入具体场景。</p></div><CopyBrief value={cooperation.brief} /></div></section></>;
}
