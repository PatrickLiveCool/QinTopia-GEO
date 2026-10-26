import caseData from "@/content/cases.json";

export type CaseBlock = { type: "paragraph" | "list"; items: string[] };
export type CaseStudy = {
  id: string;
  slug: string;
  title: string;
  client: string;
  industry: string;
  themes: string[];
  problem: string;
  outcome: string;
  sections: { title: string; blocks: CaseBlock[] }[];
};

export const cases = caseData as CaseStudy[];
export const caseThemes = ["模型与数据治理", "业务流程自动化", "行业智能应用", "多智能体协同"];
export const featuredCases = ["01", "02", "03", "11"].map((id) => cases.find((item) => item.id === id)!);

export function getCase(slug: string) {
  return cases.find((item) => item.slug === slug);
}
