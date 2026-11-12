"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

const MotionContext = createContext({ enabled: true, toggle: () => {} });
export const useMotion = () => useContext(MotionContext);

export function MotionProvider({ children }: { children: ReactNode }) {
  const [enabled, setEnabled] = useState(true);
  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => setEnabled(!media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  return <MotionContext.Provider value={{ enabled, toggle: () => setEnabled(value => !value) }}><div className="agentic-shell" data-motion={enabled ? "on" : "off"}>{children}</div></MotionContext.Provider>;
}
