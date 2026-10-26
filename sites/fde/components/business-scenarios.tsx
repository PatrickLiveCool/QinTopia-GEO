import Link from "next/link";
import { home } from "@/content/site";
import { Arrow } from "@/components/icons";

const flows = [
  ["群聊 / 多平台订单", "信息提取 · 商品匹配", "业务系统处理", "人员处理异常"],
  ["多来源物料数据", "清洗 · 去重 · 标准匹配", "统一描述与编码", "专家集中审核"],
  ["模型与应用需求", "申请 · 审批 · 授权", "统一调用与统计", "管理人员控制权限"],
  ["客房 / 床位 / 订单", "统一业务事实", "按职责协同处理", "关键业务正式确认"],
];

export function BusinessScenarios() {
  return <div className="scenarios">{home.outcomes.map((item, scenarioIndex) => (
    <article className="scenario-panel" key={item.id} aria-labelledby={`scenario-${item.id}`}>
      <div className="scenario-story">
        <p className="eyebrow"><span className="mono">{item.id}</span> / {item.label}</p>
        <h3 id={`scenario-${item.id}`}>{item.title}</h3>
        <div className="scenario-before"><span>原来的工作</span><p>{item.problem}</p></div>
        <div className="scenario-after"><span>接入之后</span><p>{item.change}</p></div>
        <Link className="text-link" href={`/cases/${item.caseSlug}/`}>阅读{item.caseLabel}<Arrow diagonal /></Link>
      </div>
      <div className="scenario-visual">
        <div className="scenario-flow">
          <p className="eyebrow">业务链路示意 / {item.id}</p>
          <ol>{flows[scenarioIndex].map((step, index) => <li key={step}><span className="flow-number mono">0{index + 1}</span><span>{step}</span>{index === 3 && <span className="human-badge">人工</span>}</li>)}</ol>
          <p className="scenario-note">以接口开放、数据授权与平台适配为前提。</p>
        </div>
      </div>
    </article>
  ))}</div>;
}
