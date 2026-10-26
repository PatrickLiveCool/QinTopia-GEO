import type { Metadata } from "next";
import { cases, caseThemes } from "@/lib/content";
import { CaseExplorer } from "@/components/case-explorer";
import { PageIntro } from "@/components/section-heading";

export const metadata: Metadata = { title: "项目案例", description: "从高校模型服务、供应链订单协同、制造数据治理到酒店多智能体协作，了解秦托邦的 11 个项目案例。", alternates: { canonical: "/cases/" } };

export default function CasesPage() {
  return <><PageIntro label="PROJECTS / 项目案例" title="看业务问题怎样得到解决。">按能力主题或业务问题找到相关实践。每个案例依次说明客户问题、我们的解决方案、客户收益与技术分析。</PageIntro><section className="container section-bottom" aria-label="案例目录"><CaseExplorer items={cases} themes={caseThemes} /></section></>;
}
