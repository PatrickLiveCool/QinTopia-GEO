"use client";

import { useState } from "react";
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
  const [active, setActive] = useState(0);
  const item = home.outcomes[active];
  return <div className="scenarios">
    <div className="scenario-selector" role="group" aria-label="选择业务场景">{home.outcomes.map((outcome, index) => <button key={outcome.id} type="button" aria-pressed={active === index} aria-controls="scenario-panel" onClick={() => setActive(index)}><span className="mono">{outcome.id}</span><span>{outcome.label}</span><Arrow /></button>)}</div>
    <div className="scenario-panel" id="scenario-panel" aria-live="polite">
      <div className="scenario-story"><p className="eyebrow">场景 {item.id}</p><h3>{item.title}</h3><div className="scenario-before"><span>原来的工作</span><p>{item.problem}</p></div><div className="scenario-after"><span>接入之后</span><p>{item.change}</p></div><Link className="text-link" href={`/cases/${item.caseSlug}/`}>阅读{item.caseLabel}<Arrow diagonal /></Link></div>
      <div className="scenario-flow"><p className="eyebrow">业务链路示意</p><ol>{flows[active].map((step, index) => <li key={step}><span className="mono">0{index + 1}</span><span>{step}</span>{index === 3 && <span className="human-badge">人工</span>}</li>)}</ol><p className="scenario-note">以接口开放、数据授权与平台适配为前提。</p></div>
    </div>
  </div>;
}
