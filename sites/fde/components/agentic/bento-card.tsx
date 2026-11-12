"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { useMotion } from "./motion-context";

export function BentoCard({ children, className = "", delay = 0 }: { children: ReactNode; className?: string; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(true);
  const { enabled } = useMotion();
  useEffect(() => {
    const el = ref.current;
    if (!el || !enabled) { setVisible(true); return; }
    if (el.getBoundingClientRect().top > innerHeight) setVisible(false);
    const observer = new IntersectionObserver(([entry]) => { if (entry.isIntersecting) { setVisible(true); observer.disconnect(); } }, { threshold: .1 });
    observer.observe(el);
    return () => observer.disconnect();
  }, [enabled]);
  return <div ref={ref} className={`ag-bento ${className}`} style={{ opacity: visible ? 1 : 0, transform: visible ? "translateY(0)" : "translateY(28px)", transitionDelay: `${delay}ms` }} onFocusCapture={() => setVisible(true)} onPointerMove={event => { const rect = event.currentTarget.getBoundingClientRect(); event.currentTarget.style.setProperty("--mouse-x", `${event.clientX - rect.left}px`); event.currentTarget.style.setProperty("--mouse-y", `${event.clientY - rect.top}px`); }}>{children}</div>;
}
