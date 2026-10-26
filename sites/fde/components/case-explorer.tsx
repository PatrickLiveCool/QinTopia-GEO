"use client";

import { useState } from "react";
import type { CaseStudy } from "@/lib/content";
import { CaseCard } from "@/components/case-card";

export function CaseExplorer({ items, themes }: { items: CaseStudy[]; themes: string[] }) {
  const [selected, setSelected] = useState("全部");
  const [query, setQuery] = useState("");
  const matches = items.filter((item) => (selected === "全部" || item.themes.includes(selected)) && [item.title, item.industry, item.client, item.problem, item.outcome].join(" ").toLocaleLowerCase().includes(query.trim().toLocaleLowerCase()));
  return (
    <div className="case-explorer">
      <div className="case-tools"><div className="filters" role="group" aria-label="按能力主题筛选">{["全部", ...themes].map((theme) => <button key={theme} type="button" aria-pressed={theme === selected} onClick={() => setSelected(theme)}>{theme}</button>)}</div><label className="case-search"><span className="sr-only">搜索案例、行业或业务问题</span><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索案例、行业或业务问题" /></label></div>
      <p className="result-count" role="status" aria-live="polite">找到 {matches.length} 个案例</p>
      {matches.length ? <div className="case-grid">{matches.map((item) => <CaseCard key={item.id} item={item} />)}</div> : <div className="empty-state"><h2>没有找到相关案例</h2><p>试试“订单”“数据”或“协作”，也可以查看全部案例。</p><button className="button button-secondary" onClick={() => { setQuery(""); setSelected("全部"); }}>清除筛选</button></div>}
    </div>
  );
}
