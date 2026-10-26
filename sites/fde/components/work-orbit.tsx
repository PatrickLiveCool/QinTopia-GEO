export function WorkOrbit() {
  return <div className="work-orbit" role="img" aria-label="业务、数据和系统围绕 AI 能力连接，人员保留关键判断。此图为能力概念示意，不是产品界面。">
    <div className="orbit-caption"><span>从分散信息，到协同工作</span><span>01 — 04</span></div>
    <div className="orbit-scene" aria-hidden="true">
      <div className="orbit-plane plane-one" /><div className="orbit-plane plane-two" /><div className="orbit-plane plane-three" />
      <div className="orbit-core"><span>AI</span><small>业务连接</small></div>
      <span className="orbit-node node-one"><i />业务场景</span><span className="orbit-node node-two"><i />数据与知识</span><span className="orbit-node node-three"><i />现有系统</span><span className="orbit-node node-four"><i />人的判断</span>
    </div>
    <div className="orbit-foot"><span><i />连接能力，不替代责任</span><span>能力概念示意</span></div>
  </div>;
}
