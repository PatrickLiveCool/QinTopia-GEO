import Link from "next/link";
import { Arrow } from "@/components/icons";

export function OrderFlow() {
  return (
    <aside className="order-flow" aria-label="群聊收单案例业务流程示意">
      <div className="flow-heading"><span className="mono">SCENARIO / 02</span><span className="flow-label">供应链 · 业务流程示意</span></div>
      <h2>把一条聊天订单，<br />接入业务处理流程。</h2>
      <ol className="flow-stages">
        <li><span className="flow-number">01</span><div><h3>商户在群聊中下单</h3><p>沿用熟悉的业务沟通方式</p></div><span className="flow-type">输入</span></li>
        <li><span className="flow-number">02</span><div><h3>提取信息，匹配商品</h3><p>识别订单字段，连接商品知识库</p></div><span className="flow-type">处理</span></li>
        <li><span className="flow-number">03</span><div><h3>衔接供应链系统</h3><p>承接查询与下单处理</p></div><span className="flow-type">执行</span></li>
      </ol>
      <div className="human-check"><span className="human-dot" aria-hidden="true" /><p>异常与无法直接处理的情况，交由人员处理。</p></div>
      <Link href="/cases/chat-order-workflow/" className="flow-case-link">了解这个项目带来的变化 <Arrow diagonal /></Link>
    </aside>
  );
}
