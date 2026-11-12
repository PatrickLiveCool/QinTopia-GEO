"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { home } from "@/content/site";
import { IntroAnimation } from "./intro-animation";
import { useMotion } from "./motion-context";

export function AgenticHero() {
  const [ready, setReady] = useState(false);
  const [introSkipped, setIntroSkipped] = useState(false);
  const { enabled } = useMotion();
  const video = useRef<HTMLVideoElement>(null);
  const done = useCallback(() => setReady(true), []);
  useEffect(() => {
    if (!enabled) { video.current?.pause(); setReady(true); setIntroSkipped(true); }
    else video.current?.play().catch(() => {});
  }, [enabled]);
  return <>
    {enabled && !introSkipped && <IntroAnimation onDone={done} />}
    <section className={`ag-hero ${ready ? "is-ready" : ""}`}>
      <video ref={video} autoPlay loop muted playsInline preload="auto" aria-hidden="true" poster="/agentic/arc.png" src="/agentic/hero.mp4" />
      <div className="ag-hero-gradient" aria-hidden="true" />
      {[20, 38, 55].map((height, i) => <div className="ag-hero-blur" key={height} style={{ height: `${height}%`, backdropFilter: `blur(${[12, 6, 2][i]}px)` }} aria-hidden="true" />)}
      <div className="ag-hero-copy"><p className="ag-hero-eyebrow">{home.eyebrow}</p><h1><span>让 AI 接入业务，</span><br /><span>让工作真正向前。</span></h1><p className="ag-hero-description">把分散的信息、已有的系统与 AI 能力连接起来。<br />让重复工作进入流程，让关键判断留给人。</p><div className="ag-hero-links"><Link className="ag-button" href="/cases/">探索项目案例 <span aria-hidden="true">↗</span></Link><Link href="/cooperation/">与我们协作 <span aria-hidden="true">↗</span></Link></div><div className="ag-hero-metrics">{[{value:"04", label:"业务场景"}, {value:"11", label:"项目案例"}, {value:"07", label:"服务能力"}].map((item, i) => <div key={item.label} style={{ transitionDelay: `${120 + i * 80}ms` }}><span>{item.value}</span><small>{item.label}</small></div>)}</div></div>
      <a className="ag-scroll-cue" href="#business-value">向下探索 <span aria-hidden="true">↓</span></a>
    </section>
  </>;
}
